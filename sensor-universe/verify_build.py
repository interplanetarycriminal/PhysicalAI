"""Structural release gate for any built workbook.

    python3 verify_build.py esp32_sensor_universe_vNN.xlsx

Runs after patch_v50.py and before audit_workbook.py. Exit 1 on any failure.
See HANDOFF.md, operating rule 6. Every check here caught a real defect once.
"""
import csv
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))
sys.path.insert(0, str(HERE))

import openpyxl  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402
from openpyxl.worksheet.formula import ArrayFormula  # noqa: E402

import fusion  # noqa: E402
import loader  # noqa: E402
import outcome_solver as osv  # noqa: E402
import patch_v50  # noqa: E402
import vocab  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else str(patch_v50.OUT)
V50 = patch_v50.SRC
FIRST, LAST = 8, 412          # sensor rows on Kit Builder / Coverage Matrix
fails = []


def check(name, ok, detail=""):
    print(f"  {'✓' if ok else '✗ FAIL'} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        fails.append(name)


# 1 · integrity + inventory
check("zip integrity", zipfile.ZipFile(OUT).testzip() is None)
wb = openpyxl.load_workbook(OUT)
wb50 = openpyxl.load_workbook(V50)
new_names = set(wb.sheetnames) - set(wb50.sheetnames)
check("no v50 sheet lost", not (set(wb50.sheetnames) - set(wb.sheetnames)))
v55_sheets = {"Corrections Log", "Glue & Signal Chain", "Boards & Compute",
              "I2C & Wiring Reality", "Physics Cheat Codes II", "Derived Instruments",
              "The Anti-Catalog II", "Outcome Solver", "Outcome → Kit", "Solver Run",
              "Solver Data", "Fusion Solver", "Kit Builder", "Coverage Matrix"}
check("all v55 sheets present", v55_sheets <= new_names,
      str(v55_sheets - new_names) if not v55_sheets <= new_names else f"{len(new_names)} added")

# 2 · Sensor Catalog contiguity + filter
ws = wb["Sensor Catalog"]
pop = [r for r in range(4, ws.max_row + 1) if ws.cell(r, 2).value]
check("catalog contiguous from row 4", pop == list(range(4, 4 + len(pop))),
      f"{len(pop)} rows, last {pop[-1]}")
check("auto_filter spans the catalog",
      str(ws.auto_filter.ref) == f"$A$3:${get_column_letter(ws.max_column)}${pop[-1]}",
      str(ws.auto_filter.ref))

# 3 · Idea Forge wired to the whole catalog
forge = wb["Idea Forge"]
texts = []
for row in forge.iter_rows():
    for c in row:
        t = c.value.text if isinstance(c.value, ArrayFormula) else c.value
        if isinstance(t, str) and t.startswith("="):
            texts.append(t)
n_cat = len(pop)
check("Idea Forge: no stale ranges",
      not any("$241" in t or "RANDBETWEEN(1,238)" in t for t in texts))
check("Idea Forge: drivers span the catalog",
      sum(1 for t in texts if f"RANDBETWEEN(1,{n_cat})" in t) == 4)
check("Idea Forge: 41 formulas", len(texts) == 41, str(len(texts)))

# 4 · Coverage Matrix truth + alignment
records, _ = loader.load_all(persist_ids=False)
sol = osv.build(records, vocab.INFERENCE)
caps = fusion.matrix_capabilities()
cap_keys = {k for k, _kd in caps}
col_of = {k: 5 + i for i, (k, _kd) in enumerate(caps)}
cm, kb = wb["Coverage Matrix"], wb["Kit Builder"]
sensors = sorted((r for r in records if r.get("catalog") == "sensor"),
                 key=lambda r: int(r["id"][1:]))
mismatch = []
for i, r in enumerate(sensors):
    row = FIRST + i
    if cm.cell(row, 1).value != r["id"] or kb.cell(row, 1).value != r["id"]:
        mismatch.append((row, r["id"], "misaligned"))
        continue
    grid = {k for k in cap_keys if cm.cell(row, col_of[k]).value == 1}
    if grid != (fusion.covers(r) & cap_keys):
        mismatch.append((row, r["id"], "grid≠covers"))
check("matrix rows aligned + truthful", not mismatch and len(sensors) == LAST - FIRST + 1,
      str(mismatch[:2]) if mismatch else f"{len(sensors)} rows")

# 5 · formula-reference audit
rng = re.compile(r"\$?([A-Z]{1,2})\$?(\d+):\$?([A-Z]{1,2})\$?(\d+)")
inf_last = get_column_letter(4 + len(vocab.INFERENCE))
bad_refs, n_formulas = [], 0
for sheet in (cm, kb):
    for row in sheet.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("="):
                n_formulas += 1
                for m in rng.finditer(c.value):
                    r1, r2 = int(m.group(2)), int(m.group(4))
                    if (r1, r2) not in ((FIRST, LAST), (5, 5), (6, 6)) and r1 != r2 \
                            and r1 <= LAST:
                        bad_refs.append((sheet.title, c.coordinate, m.group(0)))
check("formula ranges sane", not bad_refs, str(bad_refs[:3]))
print(f"      ({n_formulas} live formulas)")
overrun = [c.coordinate for (c,) in kb.iter_rows(min_row=FIRST, max_row=LAST, min_col=5, max_col=5)
           if isinstance(c.value, str) and f"${inf_last}" not in c.value]
check("buys-next stops at inference columns", not overrun, str(overrun[:3]))

out_bad, found = [], 0
for row in kb.iter_rows(min_row=LAST + 1, max_row=kb.max_row, min_col=3, max_col=4):
    key_c, count_c = row
    if (key_c.value in vocab.INFERENCE and isinstance(count_c.value, str)
            and re.fullmatch(r"='Coverage Matrix'!\$[A-Z]+\$5", count_c.value)):
        found += 1
        if f"${get_column_letter(col_of[key_c.value])}$5" not in count_c.value:
            out_bad.append(key_c.value)
check("outcome block refs correct columns",
      found == len(vocab.INFERENCE) and not out_bad, f"{found}/{len(vocab.INFERENCE)} {out_bad[:2]}")

edge_bad = []
for (c,) in kb.iter_rows(min_row=LAST + 1, max_row=kb.max_row, min_col=4, max_col=4):
    v = c.value
    if isinstance(v, str) and v.startswith("=IF(AND") and '"UNLOCKED"' in v:
        edge_bad += [(c.coordinate, m.group(0)) for m in re.finditer(r"\$D\$(\d+)=", v)
                     if int(m.group(1)) >= c.row]
check("chained edges reference earlier rows only", not edge_bad, str(edge_bad[:3]))


# 6 · independent closure re-implementation
def closure2(recs):
    counts = Counter(c for r in recs for c in fusion.covers(r))
    fired, granted, changed = set(), set(), True
    while changed:
        changed = False
        for e in fusion.FUSION_EDGES:
            if e["key"] not in fired and all(
                    counts.get(c, 0) >= m or (m == 1 and c in granted) for c, m in e["requires"]):
                fired.add(e["key"]); granted.add(e["provides"]); changed = True
    return fired, granted


tiers_ok = True
for t, tc in zip(sol["tiers"], sol["fusion"]["tier_closures"]):
    ids = {s["id"] for s in sol["trace_cost"][:t["upto"]]}
    fired, granted = closure2([r for r in sensors if r["id"] in ids])
    em = len({g for g in granted if g in fusion.EMERGENT})
    if (len(fired), em) != (tc["fired"], tc["emergent"]):
        tiers_ok = False
check("closure independently reproduced per tier", tiers_ok)
preload = {s["id"] for s in sol["trace_cost"][:sol["tiers"][0]["upto"]]}
check("FOUNDATION preload written",
      all((kb.cell(FIRST + i, 4).value == 1) == (r["id"] in preload) for i, r in enumerate(sensors)),
      f"{len(preload)} preloaded")

# 7 · exports agree with the build
with open(HERE / "exports" / "coverage_matrix.csv") as f:
    rows = list(csv.reader(f))
hdr = rows[0][3:]
csv_ok = len(rows) == len(sensors) + 1 and all(
    rows[1 + i][0] == r["id"] and
    [int(x) for x in rows[1 + i][3:]] == [1 if k in fusion.covers(r) else 0 for k in hdr]
    for i, r in enumerate(sensors))
check("coverage_matrix.csv equals the grid", csv_ok)
with open(HERE / "exports" / "fusion_edges.csv") as f:
    check("fusion_edges.csv rows", sum(1 for _ in f) == len(fusion.FUSION_EDGES) + 1)
j = json.load(open(HERE / "exports" / "solver_run.json"))
check("solver_run.json fusion object", j.get("fusion", {}).get("n_edges") == len(fusion.FUSION_EDGES))

print()
if fails:
    print(f"❌ {len(fails)} FAILURES: {fails}")
    sys.exit(1)
print(f"✅ all checks pass for {OUT}")
