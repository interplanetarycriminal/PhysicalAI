#!/usr/bin/env python3
"""Patch v50 in place: apply the correctness fixes, add what it genuinely lacks.

v50 is a far better DOCUMENT than anything I built — 56 sheets, 90 physics cheat
codes, a Failure Museum, an Anti-Catalog. But its Sensor Catalog is the unfixed
v5 catalog: 238 sensors carrying every error the review found, including two
safety hazards and one instruction that destroys an ESP32.

So this does not replace v50. It:
  1. patches the Sensor Catalog cells that are WRONG, preserving everything else
     including v50's own 'Second Life' and 'Edge-AI Hook' columns;
  2. adds the four sheets v50 has no equivalent of;
  3. writes a Corrections Log so every change is auditable.

It deliberately does NOT add my Physics Cheatsheet, Inference Atlas or
Phenomenon Index — v50's Physics Cheat Codes, Transduction Map and Measurement
Index already cover that ground, and cover it better.
"""
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
from openpyxl import load_workbook  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))
sys.path.insert(0, str(HERE))

import schema      # noqa: E402
from v50_columns import V50_COLS  # noqa: E402
from physics_codes_ii import CODES_II, CORRECTIONS as PHYS_FIX  # noqa: E402
from derived_instruments import INSTRUMENTS, METHOD  # noqa: E402
from anti_catalog_ii import WALLS  # noqa: E402
import outcome_solver  # noqa: E402
import fusion  # noqa: E402
import vocab  # noqa: E402
import sheet_lib as S  # noqa: E402
from loader import load_all  # noqa: E402

OUT = HERE / "esp32_sensor_universe_v55.xlsx"

# The sheets this script OWNS. On a self-hosted build they are deleted from the
# source workbook and regenerated, so the pipeline can rebase from any prior
# version. Every other sheet is v50's and is patched in place, idempotently.
OWNED_SHEETS = [
    "Corrections Log", "Glue & Signal Chain", "Boards & Compute", "I2C & Wiring Reality",
    "Physics Cheat Codes II", "Derived Instruments", "The Anti-Catalog II",
    "Outcome Solver", "Outcome → Kit", "Solver Run", "Solver Data",
    "Fusion Solver", "Kit Builder", "Coverage Matrix",
]


def _resolve_src():
    """The upstream v50 upload no longer exists, so the build is self-hosting:
    it starts from the newest committed workbook whose version is <= OUT's.
    Building OUT from itself is a rebuild in place (saved atomically)."""
    import re
    upload = Path("/root/.claude/uploads/f55cc0f7-8744-54de-a2e0-8ff2f0fa91bf/"
                  "86aced1a-esp32_sensor_universe_v50.xlsx")
    if upload.exists():
        return upload
    want = int(re.search(r"_v(\d+)\.xlsx$", OUT.name).group(1))
    cands = []
    for p in HERE.glob("esp32_sensor_universe_v*.xlsx"):
        m = re.search(r"_v(\d+)\.xlsx$", p.name)
        if m and 50 < int(m.group(1)) <= want:
            cands.append((int(m.group(1)), p))
    if not cands:
        sys.exit("no source workbook: need the v50 upload or a committed v51+ build")
    return max(cands)[1]


SRC = _resolve_src()

CAT_BACK = {  # schema-v2 category -> the v50 taxonomy name, so the sheet stays coherent
    "Humidity & Moisture": "Humidity + Temp", "CO2": "CO2 (true)",
    "Particulate": "Particulate (PM)", "Colour & Spectral": "Color & Spectral",
    "Motion & Vibration": "Motion & IMU", "Power & Electrical": "Power & Energy",
    "GNSS & Positioning": "GPS & Positioning", "Identity & Tags": "RFID & NFC",
    "Industrial & Automotive": "Industrial Sensing",
    "Materials & Textiles": "E-Textile & Materials",
    "Radiation & Nuclear": "Radiation & EM", "RF & Electromagnetic": "Radiation & EM",
}

# v50 names that I renamed because the name itself was factually wrong.
RENAMED = {
    "AS7331+photodiode flame/UV-C": "IR flame detector (flicker)",
    "MEMS hydrogen sensor": "MQ-8 hydrogen sensor",
    "Doppler ultrasonic flow (clamp-on)": "Transit-time ultrasonic flow (clamp-on)",
    "Soil tensiometer (real suction)": "Watermark granular-matrix soil water sensor",
    "SEN0395 / mmWave 60GHz sleep radar": "DFRobot Gravity mmWave presence radar",
    "O2 sensor (automotive narrowband)": "Narrowband O2 sensor (HEGO)",
    "MH-Z19 style CH4 / propane NDIR": "NDIR methane / hydrocarbon module",
    "Dissolved oxygen kit": "Dissolved oxygen kit (Atlas EZO-DO)",
}

# v50 column header -> which field of my corrected record supplies it.
# Columns absent here are left exactly as v50 has them (taxonomy, difficulty,
# themes, and v50's own two columns).
COLMAP = {
    "Sensor": "n",
    "What It Measures": "meas",
    "How It Works (Plain English)": "how",
    "Voltage": "v",
    "≈Price USD": "usd",
    "Power Draw": "pwr",
    "Key Specs & Gotchas": "spec",
    "Boards / Modules": "brd",
    "Library / Driver": "lib",
    "Common Uses": "use",
    "Invention Sparks": "spark",
    "Pairs Well With": "pair",
}


def _differs(old, new):
    """Idempotence: 95 and 95.0 are the same price; a rebase must find no change."""
    try:
        return abs(float(old) - float(new)) > 1e-9
    except (TypeError, ValueError):
        return str(old) != str(new)


def main():
    records, _ = load_all(persist_ids=False)
    mine = {r["n"]: r for r in records if r.get("catalog") == "sensor"}

    wb = load_workbook(SRC)
    dropped = [n for n in OWNED_SHEETS if n in wb.sheetnames]
    for n in dropped:
        del wb[n]
    print(f"Source: {SRC.name}" + (f" — regenerating {len(dropped)} owned sheets" if dropped else ""))
    ws = wb["Sensor Catalog"]
    hdr = {ws.cell(row=3, column=c).value: c for c in range(1, ws.max_column + 1)}

    changes = []   # (sensor, column, old, new)
    unmatched = []

    for r in range(4, ws.max_row + 1):
        v50_name = ws.cell(row=r, column=hdr["Sensor"]).value
        if not v50_name:
            continue
        rec = mine.get(RENAMED.get(v50_name, v50_name))
        if rec is None:
            unmatched.append(v50_name)
            continue
        for col_name, field in COLMAP.items():
            if col_name not in hdr:
                continue
            new = rec.get(field)
            if new in (None, "", []):
                continue
            cell = ws.cell(row=r, column=hdr[col_name])
            old = cell.value
            if _differs(old, new):
                changes.append((v50_name, col_name, str(old or "")[:400], str(new)[:400]))
                cell.value = new

    print(f"Sensor Catalog: {len(changes)} cells corrected across "
          f"{len({c[0] for c in changes})} sensors")
    if unmatched:
        print(f"  ! {len(unmatched)} v50 rows had no counterpart: {unmatched[:5]}")

    added = append_new_sensors(wb, ws, hdr, records)
    print(f"Sensor Catalog: {added} new sensors appended -> "
          f"{len([r for r in records if r.get('catalog') == 'sensor'])} rows total")
    add_corrections_log(wb, changes, added)
    add_catalog(wb, records, "glue", "Glue & Signal Chain",
                "🔧 GLUE & SIGNAL CHAIN — the parts that make the others work",
                "v50 has no equivalent sheet. These decide whether an analog sensor gives you "
                "data or noise. The ADS1115 alone upgrades about a third of the catalog.")
    add_catalog(wb, records, "board", "Boards & Compute",
                "🧠 BOARDS & COMPUTE — which ESP32, and why",
                "The variants differ more than people expect. C3/C6/H2 have NO capacitive touch "
                "peripheral and NO DAC — a fact that invalidates several recommendations elsewhere.")
    add_wiring(wb, records)
    n = fix_physics_codes(wb)
    add_physics_ii(wb)
    print(f"Physics Cheat Codes: {n} numerical errors corrected; 12 codes added as II")
    add_derived(wb)
    add_anti_ii(wb)
    print(f"Derived Instruments: {len(INSTRUMENTS)} worked from first principles "
          f"({sum(1 for i in INSTRUMENTS if i[0]=='DEAD')} killed by arithmetic); "
          f"Anti-Catalog II: {len(WALLS)} walls")
    sol = outcome_solver.build(records, vocab.INFERENCE)
    add_solver(wb, sol)
    add_outcome_index(wb, sol)
    add_solver_run(wb, sol)
    add_solver_data(wb, sol, vocab.INFERENCE)
    print(f"Outcome Solver: {sol['n_all']} outcomes over {sol['n_sensors']} sensors; "
          f"full coverage in {sol['kit_cost_len']} parts for ${sol['cost_cost']:.0f}")
    print(f"Solver Run: both objectives traced in full "
          f"({sol['kit_cost_len']} + {sol['kit_count_len']} steps, every step's outcomes named)")

    layout = make_layout(records)
    add_fusion_solver(wb, sol)
    add_kit_builder(wb, records, sol, layout)
    add_coverage_matrix(wb, records, layout)
    fus = sol["fusion"]
    print(f"Fusion Solver: {fus['n_edges']} edges, {fus['n_emergent']} emergent outcomes; "
          f"FOUNDATION closes to {fus['tier_closures'][0]['total']} capabilities, "
          f"COMPLETE to {fus['tier_closures'][-1]['total']}")
    forge_fixed = fix_idea_forge(wb)
    print(f"Idea Forge: {forge_fixed} formulas rewired for the 405-row catalog "
          f"(was blind to the 167 merged sensors)")

    # The same run, written out in formats that do not need Excel. This is what
    # makes the analysis servable anywhere else.
    import solve as solve_cli
    names = solve_cli.export(records, vocab.INFERENCE, sol)
    print(f"Solver Data: {sol['edges']} edges published; "
          f"exports/ regenerated ({', '.join(names)})")

    # openpyxl drops cached formula results on round-trip; v50 has 10 formula
    # cells on Idea Forge. Forcing a full recalculation on open means Excel
    # repopulates them immediately and the user never sees a blank.
    wb.calculation.fullCalcOnLoad = True
    tmp = OUT.with_suffix(".tmp.xlsx")     # atomic: a failed build never corrupts SRC/OUT
    wb.save(tmp)
    tmp.replace(OUT)
    print(f"\nWrote {OUT}")
    print(f"  {len(wb.sheetnames)} sheets (v50 had 56)")
    return changes


# ------------------------------------------------------------------ new sheets

def _banner(ws, title, subtitle, ncols):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    c = ws.cell(row=1, column=1, value=title)
    c.font = S.Font(name=S.FONT, size=16, bold=True, color="FFFFFF")
    c.fill = S.PatternFill("solid", fgColor=S.NAVY)
    c.alignment = S.Alignment(vertical="center", indent=1)
    ws.row_dimensions[1].height = 30
    for i in range(1, ncols + 1):
        ws.cell(row=1, column=i).fill = S.PatternFill("solid", fgColor=S.NAVY)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
    s = ws.cell(row=2, column=1, value=subtitle)
    s.font = S.sfont(9.5, italic=True, color=S.MUTED)
    s.alignment = S.Alignment(vertical="center", indent=1, wrap_text=True)
    ws.row_dimensions[2].height = 28
    return 3


def append_new_sensors(wb, ws, hdr, records):
    """Merge the sensors v50 lacks into its own Sensor Catalog, in its own format.

    A separate expansion sheet would leave the catalog in two tiers. Merging keeps
    one catalog — which is only honest if the new rows carry v50's own two
    signature columns too, hence data/v50_columns.py.
    """
    existing = {ws.cell(row=r, column=hdr["Sensor"]).value
                for r in range(4, ws.max_row + 1) if ws.cell(row=r, column=hdr["Sensor"]).value}
    new = [r for r in records if r.get("catalog") == "sensor" and r["n"] not in existing]
    new.sort(key=lambda r: (r["cat"], r["n"]))

    # copy the styling of an existing data row so the new rows are indistinguishable
    template = {c: ws.cell(row=5, column=c) for c in range(1, ws.max_column + 1)}
    # v50 pads every sheet with styled empty rows to row 1000; appending at
    # max_row+1 stranded the new sensors at rows 1001+ with a 759-row hole,
    # outside the sheet's own AutoFilter. Append after the last POPULATED row.
    row = 1 + max(r for r in range(4, ws.max_row + 1)
                  if ws.cell(row=r, column=hdr["Sensor"]).value)
    for rec in new:
        sl, hook = V50_COLS.get(rec["id"], ("", ""))
        vals = {
            "ID": rec["id"],
            "Sensor": rec["n"],
            "Category": CAT_BACK.get(rec["cat"], rec["cat"]),
            "Subcategory": rec.get("sub", ""),
            "What It Measures": rec.get("meas", ""),
            "How It Works (Plain English)": rec.get("how", ""),
            "Interface": "/".join(rec.get("iface") or []),
            "Voltage": rec.get("v", ""),
            "≈Price USD": rec.get("usd"),
            "Tier": schema.price_tier(rec.get("usd")),
            "Difficulty": f"{rec.get('diff')} · "
                          f"{schema.DIFFICULTY_RUBRIC.get(rec.get('diff'), '').split(' — ')[0]}",
            "Power Draw": rec.get("pwr", ""),
            "Key Specs & Gotchas": " · ".join(
                x for x in (rec.get("range"), rec.get("accuracy"), rec.get("rate"),
                            rec.get("requires")) if x),
            "Where To Buy": ", ".join(rec.get("buy") or []),
            "Boards / Modules": rec.get("brd", ""),
            "Library / Driver": rec.get("lib", ""),
            "Common Uses": rec.get("use", ""),
            "Invention Sparks": rec.get("spark", ""),
            "Pairs Well With": rec.get("pair", ""),
            "Themes": ", ".join(rec.get("tags") or []),
            "Second Life (off-label modes)": sl,
            "Edge-AI Hook": hook,
        }
        for col_name, col in hdr.items():
            if col_name is None:
                continue
            cell = ws.cell(row=row, column=col, value=vals.get(col_name, ""))
            t = template.get(col)
            if t is not None:
                cell.font = t.font.copy()
                cell.fill = t.fill.copy()
                cell.border = t.border.copy()
                cell.alignment = t.alignment.copy()
        ws.row_dimensions[row].height = ws.row_dimensions[5].height
        row += 1
    # the filter range was still $A$3:$V$241 — the appended sensors were
    # invisible to every filter operation. Extend it over the whole catalog.
    from openpyxl.utils import get_column_letter
    ws.auto_filter.ref = f"$A$3:${get_column_letter(ws.max_column)}${row - 1}"
    return len(new)


def fix_physics_codes(wb):
    """Correct the two numerical errors in the original ninety, in place."""
    if "Physics Cheat Codes" not in wb.sheetnames:
        return 0
    ws = wb["Physics Cheat Codes"]
    fixed = 0
    for _code, wrong, right, _why in PHYS_FIX:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and wrong in cell.value:
                    cell.value = cell.value.replace(wrong, right)
                    fixed += 1
    return fixed


def add_physics_ii(wb):
    """Twelve codes the original ninety do not cover, in the same five columns."""
    ws = wb.create_sheet("Physics Cheat Codes II")
    S.sheet_defaults(ws, tab_color="4E6E5D")
    ncols = 5
    row = _banner(
        ws, "🧪 PHYSICS CHEAT CODES II — twelve the first ninety do not cover",
        "The original ninety are excellent, which is not the same as complete. Auditing them for "
        "COVERAGE rather than quality turns up two of the most powerful moves in instrumentation "
        "(synchronous detection and matched filtering), a whole physical domain (nuclear "
        "attenuation), a whole chemistry (biological selectivity), and the one thinking tool that "
        "predicts answers before you solve anything (dimensional analysis).", ncols)

    # corrections banner first — errors before additions
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    S.cell(ws, row, 1, "FIRST: two numerical errors in the original ninety, now corrected in place",
           size=11, bold=True, color="FFFFFF", fill="A8412F")
    ws.row_dimensions[row].height = 22
    row += 1
    for code, wrong, right, why in PHYS_FIX:
        S.cell(ws, row, 1, code, size=9, bold=True, fill="FBE9E4")
        S.cell(ws, row, 2, wrong, size=9, fill="FBE9E4")
        S.cell(ws, row, 3, right, size=9, bold=True, fill="E7F0E9")
        ws.merge_cells(start_row=row, start_column=4, end_row=row, end_column=ncols)
        S.cell(ws, row, 4, why, size=9)
        ws.row_dimensions[row].height = max(40, 12 + len(why) // 3.2)
        row += 1
    row += 1

    for col, name in enumerate(["Cheat Code", "The physics (one line)", "Catalog exploits",
                                "Build it this weekend", "How to spot the next one"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = S.BORDER
    ws.row_dimensions[row].height = 20
    row += 1
    for i, (code, phys, exploits, weekend, spot) in enumerate(CODES_II):
        n = 91 + i
        S.cell(ws, row, 1, f"{n}. {code}", size=10, bold=True, color=S.NAVY, fill="FBEFD8")
        S.cell(ws, row, 2, phys, size=9)
        S.cell(ws, row, 3, exploits, size=9, color=S.MUTED)
        S.cell(ws, row, 4, weekend, size=9, fill="EAF0F6")
        S.cell(ws, row, 5, spot, size=9, fill="E4EFE6")
        ws.row_dimensions[row].height = max(78, 12 + len(phys) // 3.0)
        row += 1
    S.set_widths(ws, [30, 62, 44, 52, 50])
    ws.freeze_panes = "A4"
    return ws


def add_derived(wb):
    """Instruments derived here rather than catalogued from elsewhere."""
    ws = wb.create_sheet("Derived Instruments")
    S.sheet_defaults(ws, tab_color="C8853A")
    ncols = 7
    row = _banner(
        ws, "🔬 DERIVED INSTRUMENTS — sensing methods worked out here, with the arithmetic",
        "Everything else in this atlas is synthesis. This is not. Each entry is an instrument "
        "DERIVED by applying the transduction grid and the cheat codes to a measurement problem, "
        "then tested with numbers before anything was bought. Three come out DEAD, killed by their "
        "own arithmetic — kept deliberately, because a notebook of only successes is a marketing "
        "document, and a calculation that kills an idea in ten minutes saves a season.", ncols)

    for label, text in METHOD:
        S.cell(ws, row, 1, label, size=9, bold=True, fill="F5F2EB")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9)
        ws.row_dimensions[row].height = max(26, 12 + len(text) // 4.2)
        row += 1
    row += 1

    for col, name in enumerate(["Verdict", "The instrument", "What it measures that nothing cheap does",
                                "The physics", "The arithmetic — does it actually work?",
                                "Parts & cost", "What kills it · why it doesn't exist"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = S.BORDER
    ws.row_dimensions[row].height = 22
    row += 1
    vfill = {"BUILD": "E7F0E9", "MARGINAL": "FBEFD8", "DEAD": "F8DED7"}
    vcolor = {"BUILD": "2F6B45", "MARGINAL": "9A6A00", "DEAD": "A8412F"}
    for verdict, name, meas, phys, arith, parts, kills, why in INSTRUMENTS:
        c = S.cell(ws, row, 1, verdict, size=10, bold=True, halign="center",
                   fill=vfill[verdict], color=vcolor[verdict])
        S.cell(ws, row, 2, name, size=10, bold=True, color=S.NAVY)
        S.cell(ws, row, 3, meas, size=9)
        S.cell(ws, row, 4, phys, size=9)
        S.cell(ws, row, 5, arith, size=9, fill="EAF0F6")
        S.cell(ws, row, 6, parts, size=9)
        S.cell(ws, row, 7, f"KILLS IT: {kills}\n\nWHY IT DOESN'T EXIST: {why}", size=9,
               fill="FBE9E4" if verdict == "DEAD" else None)
        ws.row_dimensions[row].height = max(110, 12 + len(arith) // 2.4)
        row += 1
    S.set_widths(ws, [11, 26, 40, 56, 60, 30, 62])
    ws.freeze_panes = "C4"
    return ws


def add_anti_ii(wb):
    """More walls. Knowing what is impossible is worth more than knowing what is possible."""
    ws = wb.create_sheet("The Anti-Catalog II")
    S.sheet_defaults(ws, tab_color="8A4A3A")
    ncols = 4
    row = _banner(
        ws, "🧱 THE ANTI-CATALOG II — twelve more walls, and what each one teaches",
        "The original Anti-Catalog is the best sheet in this atlas and one of the smallest, which "
        "is backwards. Every wall here is a genuine physical limit rather than an engineering "
        "inconvenience — stated with the number that makes it a wall, what it teaches, and the "
        "nearest honest thing you CAN measure instead.", ncols)
    for col, name in enumerate(["The wall", "The physics of the wall",
                                "What the wall teaches", "The nearest honest route"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = S.BORDER
    row += 1
    for wall, phys, teaches, route in WALLS:
        S.cell(ws, row, 1, wall, size=10, bold=True, color=S.NAVY, fill="F8DED7")
        S.cell(ws, row, 2, phys, size=9)
        S.cell(ws, row, 3, teaches, size=9, fill="FBEFD8")
        S.cell(ws, row, 4, route, size=9, fill="E7F0E9")
        ws.row_dimensions[row].height = max(76, 12 + len(phys) // 2.6)
        row += 1
    S.set_widths(ws, [34, 66, 56, 58])
    ws.freeze_panes = "B4"
    return ws


def add_solver(wb, sol):
    """The optimiser: which sensors buy the most outcomes."""
    ws = wb.create_sheet("Outcome Solver")
    S.sheet_defaults(ws, tab_color="1F6F5C")
    ncols = 7
    row = _banner(
        ws, "🎯 OUTCOME SOLVER — which sensors buy the most of everything",
        f"{sol['n_all']} things you might want to KNOW, {sol['n_sensors']} sensors that might tell "
        "you. Which small set buys the most? That is the Maximum Coverage Problem — NP-hard, but "
        "greedy is provably within 63% of optimal and nothing polynomial does better, so greedy is "
        "the right answer rather than a compromise. Everything below is COMPUTED from the live "
        "catalog at build time, so it cannot go stale.", ncols)

    for label, text in outcome_solver.FINDINGS:
        S.cell(ws, row, 1, label, size=9.5, bold=True, fill="FBEFD8")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9.5)
        ws.row_dimensions[row].height = max(30, 12 + len(text) // 4.4)
        row += 1
    row += 1

    # ---- tiers
    row = S.section(ws, row, "1 · THE FOUR KITS", ncols,
                    "Cost-optimal greedy. Each tier is the previous one plus the parts that buy "
                    "the next block of outcomes most cheaply.")
    for col, name in enumerate(["Tier", "Sensors", "Outcomes", "% of all", "Total cost",
                                "What it is", "What this tier adds"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF"); c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, horizontal="center", vertical="center")
        c.border = S.BORDER
    row += 1
    for t in sol["tiers"]:
        S.cell(ws, row, 1, t["name"], size=11, bold=True, color=S.NAVY, fill="E4EFE6", halign="center")
        S.cell(ws, row, 2, t["n"], size=11, bold=True, halign="center")
        S.cell(ws, row, 3, t["cov"], size=10, halign="center")
        S.cell(ws, row, 4, f"{t['pct']*100:.0f}%", size=11, bold=True, halign="center", fill="EAF0F6")
        S.cell(ws, row, 5, f"${t['cost']:.0f}", size=11, bold=True, halign="center")
        S.cell(ws, row, 6, t["blurb"], size=9)
        S.cell(ws, row, 7, " · ".join(t["added"]), size=8.5)
        ws.row_dimensions[row].height = max(46, 12 + len(" · ".join(t["added"])) // 5.5)
        row += 1
    row += 1

    # ---- curve
    row = S.section(ws, row, "2 · THE CURVE — every step, and where it stops being worth it", ncols,
                    "Read down until the bar stops growing. That is your kit.")
    for col, name in enumerate(["#", "Sensor", "$", "Buys", "Running total", "% of all outcomes", "Cumulative $"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF"); c.fill = S.PatternFill("solid", fgColor="4A5878")
        c.alignment = S.Alignment(wrap_text=True, horizontal="center"); c.border = S.BORDER
    row += 1
    for i, (name, usd, gain, cum, pct, spend) in enumerate(sol["curve"], 1):
        S.cell(ws, row, 1, i, size=9, halign="center")
        S.cell(ws, row, 2, name, size=9, bold=(i <= 12))
        S.cell(ws, row, 3, f"${usd:g}", size=9, halign="center")
        S.cell(ws, row, 4, f"+{gain}", size=9, halign="center", bold=True)
        S.cell(ws, row, 5, cum, size=9, halign="center")
        b = S.cell(ws, row, 6, "█" * max(1, round(pct * 34)) + f"  {pct*100:.0f}%", size=9)
        b.font = S.sfont(9, color=S.ACCENT)
        S.cell(ws, row, 7, f"${spend:.0f}", size=9, halign="center")
        ws.row_dimensions[row].height = 14
        row += 1
    row += 1

    # ---- domains
    row = S.section(ws, row, "3 · IF YOU ONLY WANT ONE DOMAIN", ncols,
                    "The minimum cost-optimal kit that covers EVERY outcome in that domain.")
    for col, name in enumerate(["Domain", "Outcomes", "Sensors", "Cost", "The kit", "", ""], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF"); c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, horizontal="center"); c.border = S.BORDER
    row += 1
    for d in sol["domain_kits"]:
        S.cell(ws, row, 1, d["domain"], size=10, bold=True, fill="F5F2EB")
        S.cell(ws, row, 2, d["n_out"], size=10, halign="center")
        S.cell(ws, row, 3, d["n_sens"], size=10, halign="center", bold=True)
        S.cell(ws, row, 4, f"${d['cost']:.0f}", size=10, halign="center", bold=True, fill="EAF0F6")
        ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=ncols)
        S.cell(ws, row, 5, d["kit"], size=8.5)
        ws.row_dimensions[row].height = max(30, 12 + len(d["kit"]) // 6.5)
        row += 1
    row += 1

    # ---- constraints
    row = S.section(ws, row, "4 · WHAT A CONSTRAINT COSTS YOU, IN OUTCOMES", ncols,
                    "The only place in this atlas that prices a design decision in capability "
                    "rather than money. Decide BEFORE you commit.")
    for col, name in enumerate(["Constraint", "Eligible parts", "Reachable", "%", "Kit / cost",
                                "What you lose entirely", ""], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF"); c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, horizontal="center"); c.border = S.BORDER
    row += 1
    for c_ in sol["constraint_kits"]:
        S.cell(ws, row, 1, c_["name"], size=10, bold=True, fill="F5F2EB")
        S.cell(ws, row, 2, c_["eligible"], size=9, halign="center")
        S.cell(ws, row, 3, f"{c_['covered']}/{sol['n_all']}", size=9, halign="center")
        pc = S.cell(ws, row, 4, f"{c_['pct']*100:.0f}%", size=11, bold=True, halign="center")
        pc.fill = S.PatternFill("solid", fgColor="E7F0E9" if c_["pct"] > 0.85 else "FBEFD8")
        S.cell(ws, row, 5, f"{c_['n_sens']} parts, ${c_['cost']:.0f}", size=9, halign="center")
        ws.merge_cells(start_row=row, start_column=6, end_row=row, end_column=ncols)
        S.cell(ws, row, 6, f"{c_['why']}\n\nUNREACHABLE: {c_['lost']}", size=9, fill="FBE9E4")
        ws.row_dimensions[row].height = 54
        row += 1
    row += 1

    # ---- irreplaceable + recombinatory
    row = S.section(ws, row, "5 · THE TWO OPPOSITE RANKINGS", ncols,
                    "Hubs cover many outcomes and are replaceable. Keys cover few and are the ONLY "
                    "route. A good kit needs both, and they anti-correlate.")
    S.cell(ws, row, 1, "🔑 IRREPLACEABLE — buy these for INTENT", size=10, bold=True, fill="F8DED7")
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
    S.cell(ws, row, 4, "🧲 RECOMBINATORY — buy these for BREADTH", size=10, bold=True, fill="E4EFE6")
    ws.merge_cells(start_row=row, start_column=4, end_row=row, end_column=ncols)
    row += 1
    for i in range(max(len(sol["irreplaceable"]), len(sol["recomb"]))):
        if i < len(sol["irreplaceable"]):
            sc, r, solo, n = sol["irreplaceable"][i]
            S.cell(ws, row, 1, r["n"][:38], size=8.5, bold=True)
            S.cell(ws, row, 2, f"${r.get('usd')}", size=8.5, halign="center")
            S.cell(ws, row, 3, ("SOLE: " + solo[0][:40]) if solo else f"{n} outcomes", size=8.5,
                   color=S.BAD if solo else S.MUTED)
        if i < len(sol["recomb"]):
            per, r, n = sol["recomb"][i]
            S.cell(ws, row, 4, r["n"][:38], size=8.5, bold=True)
            S.cell(ws, row, 5, f"${r.get('usd')}", size=8.5, halign="center")
            S.cell(ws, row, 6, f"{n} outcomes", size=8.5, halign="center")
            S.cell(ws, row, 7, f"{per:.1f} outcomes per $", size=8.5, color=S.MUTED)
        ws.row_dimensions[row].height = 14
        row += 1
    row += 1

    # ---- budget frontier
    row = S.section(ws, row, "6 · WHAT A FIXED BUDGET BUYS", ncols,
                    "Hand the optimiser a hard spend cap instead of a coverage target. "
                    "The first £10 buys almost half of everything — the arithmetic of the "
                    "inversion, priced.")
    for col, name in enumerate(["Budget", "Parts", "Outcomes", "% of all", "Spent",
                                "The kit", ""], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, horizontal="center"); c.border = S.BORDER
    row += 1
    for b in sol["budget_frontier"]:
        S.cell(ws, row, 1, f"${b['budget']}", size=10, bold=True, halign="center",
               fill="E4EFE6")
        S.cell(ws, row, 2, b["n_sens"], size=10, halign="center")
        S.cell(ws, row, 3, b["covered"], size=10, halign="center")
        S.cell(ws, row, 4, f"{b['pct']*100:.0f}%", size=11, bold=True, halign="center",
               fill="EAF0F6")
        S.cell(ws, row, 5, f"${b['spend']:.1f}", size=10, halign="center")
        ws.merge_cells(start_row=row, start_column=6, end_row=row, end_column=ncols)
        S.cell(ws, row, 6, b["kit"], size=8)
        ws.row_dimensions[row].height = max(24, 12 + len(b["kit"]) // 8)
        row += 1
    S.set_widths(ws, [30, 15, 13, 13, 22, 46, 30])
    ws.freeze_panes = "A4"
    return ws


def add_outcome_index(wb, sol):
    """Pick ANY outcome, read the kit."""
    ws = wb.create_sheet("Outcome → Kit")
    S.sheet_defaults(ws, tab_color="2F6B45")
    ncols = 8
    row = _banner(
        ws, "🗺 OUTCOME → KIT — pick any outcome, read what buys it",
        f"All {sol['n_all']} outcomes, each with its cheapest route, its most capable route, its "
        "no-contact route and its privacy-safe route — plus how many alternatives exist and which "
        "tier first reaches it. Rows marked SOLE ROUTE have exactly one sensor in the entire "
        "catalog that provides them.", ncols)
    for col, name in enumerate(["Domain", "You want to know…", "Routes", "Rarity",
                                "💵 Cheapest route", "🎯 Most capable route",
                                "🚫 No-contact route", "🔒 Privacy-safe route"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF"); c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, horizontal="center", vertical="center")
        c.border = S.BORDER
    ws.row_dimensions[row].height = 24
    row += 1
    for o in sol["outcomes"]:
        S.cell(ws, row, 1, o["domain"], size=8.5, fill="EDE7F3")
        S.cell(ws, row, 2, o["question"], size=9.5, bold=True, color=S.NAVY)
        S.cell(ws, row, 3, o["n_routes"], size=9, halign="center")
        rc = S.cell(ws, row, 4, o["rarity"] or "—", size=8.5, halign="center", bold=bool(o["rarity"]))
        if o["rarity"] == "SOLE ROUTE":
            rc.fill = S.PatternFill("solid", fgColor="F8DED7"); rc.font = S.sfont(8.5, bold=True, color=S.BAD)
        elif o["rarity"]:
            rc.fill = S.PatternFill("solid", fgColor="FBEFD8")
        S.cell(ws, row, 5, o["cheap"], size=8.5, fill="E7F0E9")
        S.cell(ws, row, 6, o["best"], size=8.5)
        S.cell(ws, row, 7, o["nocontact"], size=8.5)
        S.cell(ws, row, 8, o["privacy"], size=8.5, fill="EAF0F6")
        ws.row_dimensions[row].height = 26
        row += 1
    S.set_widths(ws, [17, 36, 8, 12, 34, 30, 32, 32])
    ws.freeze_panes = "C4"
    return ws


def add_solver_run(wb, sol):
    """The run itself, not a summary of it.

    'Outcome Solver' reports what the optimiser concluded. This sheet is the
    working: every step of both objectives, with the outcomes that step actually
    bought named in full, so the result can be checked by hand and lifted out of
    this workbook into anything else without re-running the build.
    """
    ws = wb.create_sheet("Solver Run")
    S.sheet_defaults(ws, tab_color="14524A")
    ncols = 9
    row = _banner(
        ws, "🧮 SOLVER RUN — the working, step by step",
        f"One complete execution against the live catalog: {sol['n_sensors']} sensors, "
        f"{sol['n_all']} outcomes, {sol['edges']} sensor→outcome edges. Both objectives are run to "
        "100% coverage and printed in full, including the outcomes each step BOUGHT — which is the "
        "difference between a summary of a run and the run itself. Every number in the Outcome "
        "Solver sheet can be re-derived from this one by hand.", ncols)

    # ---- provenance: what went in, what the algorithm guarantees
    row = S.section(ws, row, "0 · WHAT WAS RUN", ncols,
                    "Stated plainly so the result is reproducible rather than merely presented.")
    for k, v in [
        ("Problem", "Maximum Coverage: choose the smallest set of sensors whose combined "
                    "inference sets cover every outcome."),
        ("Complexity", "NP-hard. Exhaustive search over 405 sensors is 2^405 subsets, which is "
                       "not a computation anyone will ever finish."),
        ("Algorithm", "Greedy — repeatedly take the sensor with the best marginal value, until "
                      "coverage is complete."),
        ("Guarantee", "Greedy is within (1 − 1/e) ≈ 63% of optimal, and it is proven that no "
                      "polynomial-time algorithm beats that bound unless P = NP. So greedy is "
                      "not a shortcut here — it is the best available answer."),
        ("Objective A", f"Marginal outcomes per DOLLAR → {sol['kit_cost_len']} sensors, "
                        f"${sol['cost_cost']:.0f}, 100% coverage."),
        ("Objective B", f"Marginal outcomes per PART → {sol['kit_count_len']} sensors, "
                        f"${sol['cost_count']:.0f}, 100% coverage."),
        ("Inputs", f"{sol['n_sensors']} sensors that declare at least one inference; "
                   f"{sol['n_all']} outcomes in the controlled vocabulary; "
                   f"{sol['edges']} declared sensor→outcome edges. The full edge list is on the "
                   "Solver Data sheet."),
        ("Re-run it", "python3 solve.py — same optimiser, any subset of outcomes, any "
                      "constraint. `--export` writes JSON/CSV/Markdown for use outside Excel."),
        ("Post-processing", "Reverse-delete + 1-swap local search on the terminal kits "
                            "(tiers stay raw greedy prefixes, since each tier is defined as "
                            "the previous plus additions): "
                            + ("; ".join(sol["minimise_notes_cost"])
                               if sol["minimise_notes_cost"]
                               else "certified locally minimal under prune and 1-swap")
                            + f". Minimised COMPLETE kit: {sol['kit_cost_min_len']} parts, "
                              f"${sol['cost_cost_min']:.0f} (greedy said "
                              f"{sol['kit_cost_len']} / ${sol['cost_cost']:.0f})."),
        ("Fusion layer", f"{sol['fusion']['n_edges']} authored hyperedges close each kit over "
                         "combination outcomes — see the Fusion Solver sheet. The count "
                         "objective's kit: "
                         + ("; ".join(sol["minimise_notes_count"])
                            if sol["minimise_notes_count"]
                            else "certified locally minimal under prune and 1-swap") + "."),
    ]:
        S.cell(ws, row, 1, k, size=9, bold=True, fill="E4EFE6")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, v, size=9)
        ws.row_dimensions[row].height = max(18, 12 + len(v) // 8.0)
        row += 1
    row += 1

    hdr = ["#", "Sensor ID", "Sensor", "$", "Buys", "Total", "% covered",
           "Cumulative $", "The outcomes this step bought"]

    def block(row, title, note, trace, fill):
        row = S.section(ws, row, title, ncols, note)
        for col, name in enumerate(hdr, 1):
            c = ws.cell(row=row, column=col, value=name)
            c.font = S.sfont(9, bold=True, color="FFFFFF")
            c.fill = S.PatternFill("solid", fgColor=fill)
            c.alignment = S.Alignment(wrap_text=True, horizontal="center", vertical="center")
            c.border = S.BORDER
        row += 1
        for s in trace:
            bought = " · ".join(s["bought"])
            S.cell(ws, row, 1, s["rank"], size=8.5, halign="center")
            S.cell(ws, row, 2, s["id"], size=8.5, halign="center", color=S.MUTED)
            S.cell(ws, row, 3, s["name"], size=9, bold=True)
            S.cell(ws, row, 4, f"${s['usd']:g}", size=8.5, halign="center")
            g = S.cell(ws, row, 5, f"+{s['gain']}", size=9, bold=True, halign="center")
            g.fill = S.PatternFill("solid", fgColor="E7F0E9" if s["gain"] > 1 else "F5F2EB")
            S.cell(ws, row, 6, s["cum"], size=8.5, halign="center")
            p = S.cell(ws, row, 7, f"{s['pct']*100:.0f}%", size=8.5, halign="center")
            p.font = S.sfont(8.5, color=S.ACCENT)
            S.cell(ws, row, 8, f"${s['cum_cost']:.0f}", size=8.5, halign="center")
            S.cell(ws, row, 9, bought, size=8.5)
            ws.row_dimensions[row].height = max(14, 11 + len(bought) // 11.0)
            row += 1
        return row + 1

    row = block(row, "1 · OBJECTIVE A — cheapest route to everything",
                f"Marginal outcomes per dollar. {sol['kit_cost_len']} sensors, "
                f"${sol['cost_cost']:.0f}. Notice the order: the dumbest parts in the catalog go "
                "first, because unselective is what recombinatory MEANS.",
                sol["trace_cost"], "1F6F5C")

    row = block(row, "2 · OBJECTIVE B — fewest parts to everything",
                f"Marginal outcomes per part, ignoring price. {sol['kit_count_len']} sensors — "
                f"{sol['kit_cost_len'] - sol['kit_count_len']} fewer than objective A — but "
                f"${sol['cost_count']:.0f} against ${sol['cost_cost']:.0f}. The two objectives "
                "disagree about the FIRST pick, and that disagreement is the whole insight: "
                "capable modules minimise part count, dumb transducers minimise spend.",
                sol["trace_count"], "4A5878")

    # ---- what the two runs agree and disagree about
    a = {s["name"] for s in sol["trace_cost"]}
    b = {s["name"] for s in sol["trace_count"]}
    row = S.section(ws, row, "3 · WHERE THE TWO RUNS AGREE", ncols,
                    "Parts chosen by BOTH objectives are load-bearing under either philosophy — "
                    "they are not an artefact of how you weighted the problem.")
    for label, names, fill in [
        (f"✅ BOTH ({len(a & b)})", sorted(a & b), "E7F0E9"),
        (f"💵 CHEAPEST-ONLY ({len(a - b)})", sorted(a - b), "FBEFD8"),
        (f"📦 FEWEST-PARTS-ONLY ({len(b - a)})", sorted(b - a), "EAF0F6"),
    ]:
        S.cell(ws, row, 1, label, size=9, bold=True, fill=fill)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=ncols)
        S.cell(ws, row, 3, " · ".join(names), size=8.5)
        ws.row_dimensions[row].height = max(20, 12 + len(" · ".join(names)) // 12.0)
        row += 1

    S.set_widths(ws, [5, 10, 30, 9, 8, 8, 11, 13, 78])
    ws.freeze_panes = "A4"
    return ws


def add_solver_data(wb, sol, INFERENCE):
    """The graph the solver consumed. Publishing it is what makes the run checkable."""
    ws = wb.create_sheet("Solver Data")
    S.sheet_defaults(ws, tab_color="3A4A6B")
    ncols = 8
    row = _banner(
        ws, "🔗 SOLVER DATA — the graph every number was computed from",
        f"{sol['edges']} declared edges between {sol['n_sensors']} sensors and {sol['n_all']} "
        "outcomes. This is the optimiser's entire input: no other data enters the calculation. "
        "Filter it, sort it, or lift it out — the same rows are in exports/coverage_edges.csv.",
        ncols)

    row = S.section(ws, row, "1 · EVERY SENSOR, AND EVERYTHING IT CAN TELL YOU", ncols,
                    "Sorted by reach. The top of this list is the recombinatory end of the "
                    "catalog and the bottom is the specific end.")
    for col, name in enumerate(["ID", "Sensor", "$", "Category", "Reach",
                                "Per $", "Contact", "Outcomes it supports"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, horizontal="center", vertical="center")
        c.border = S.BORDER
    row += 1
    first = row
    for g in sol["graph"]:
        usd = g["usd"] if isinstance(g["usd"], (int, float)) else None
        S.cell(ws, row, 1, g["id"], size=8.5, halign="center", color=S.MUTED)
        S.cell(ws, row, 2, g["name"], size=9, bold=True)
        S.cell(ws, row, 3, usd, size=8.5, halign="center")
        S.cell(ws, row, 4, g["cat"], size=8, color=S.MUTED)
        n = S.cell(ws, row, 5, g["n"], size=9, bold=True, halign="center")
        if g["n"] >= 8:
            n.fill = S.PatternFill("solid", fgColor="E7F0E9")
        S.cell(ws, row, 6, round(g["n"] / max(usd or 0.5, 0.5), 1) if usd is not None else "",
               size=8.5, halign="center")
        S.cell(ws, row, 7, g["contact"] or "", size=8, halign="center")
        S.cell(ws, row, 8, " · ".join(g["questions"]), size=8.5)
        ws.row_dimensions[row].height = max(14, 11 + len(" · ".join(g["questions"])) // 14.0)
        row += 1
    S.price_bars(ws, 3, first, row - 1)
    row += 1

    row = S.section(ws, row, "2 · EVERY OUTCOME, AND EVERY ROUTE TO IT", ncols,
                    "The same graph read the other way. Route count is the honest measure of how "
                    "constrained an outcome is: one route means one point of failure and one "
                    "price you cannot negotiate.")
    for col, name in enumerate(["Key", "Domain", "You want to know…", "Routes", "Rarity",
                                "", "", "Every sensor that can tell you"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor="4A5878")
        c.alignment = S.Alignment(wrap_text=True, horizontal="center", vertical="center")
        c.border = S.BORDER
    row += 1
    for o in sorted(sol["outcomes"], key=lambda o: (o["domain"], o["n_routes"])):
        S.cell(ws, row, 1, o["key"], size=8, color=S.MUTED)
        S.cell(ws, row, 2, o["domain"], size=8, fill="EDE7F3")
        S.cell(ws, row, 3, o["question"], size=9, bold=True, color=S.NAVY)
        S.cell(ws, row, 4, o["n_routes"], size=9, bold=True, halign="center")
        rc = S.cell(ws, row, 5, o["rarity"] or "", size=8, halign="center")
        if o["rarity"] == "SOLE ROUTE":
            rc.fill = S.PatternFill("solid", fgColor="F8DED7")
            rc.font = S.sfont(8, bold=True, color=S.BAD)
        ws.merge_cells(start_row=row, start_column=6, end_row=row, end_column=ncols)
        S.cell(ws, row, 6, " · ".join(
            f"{r['name']}" + (f" (${r['usd']:g})" if isinstance(r["usd"], (int, float)) else "")
            for r in o["routes"]), size=8.5)
        ws.row_dimensions[row].height = max(14, 11 + len(o["routes"]) * 2.4)
        row += 1

    S.set_widths(ws, [10, 17, 34, 8, 12, 10, 10, 84])
    ws.freeze_panes = "C4"
    return ws


def fix_idea_forge(wb):
    """The forge's 41 formulas were sized for the 238-row catalog and can never
    deal the 167 merged sensors. Rewire every range for rows 4-408."""
    from openpyxl.worksheet.formula import ArrayFormula
    ws, fixed = wb["Idea Forge"], 0
    for row in ws.iter_rows():
        for c in row:
            v = c.value
            t = v.text if isinstance(v, ArrayFormula) else v
            if isinstance(t, str) and t.startswith("="):
                new = (t.replace("$241", "$408")
                        .replace("RANDBETWEEN(1,238)", "RANDBETWEEN(1,405)"))
                if new != t:
                    c.value = new   # plain string; these are ordinary formulas
                    fixed += 1
    return fixed


# --------------------------------------------------------------- fusion sheets

def make_layout(records):
    """Shared geometry for Kit Builder and Coverage Matrix. Sensor i sits on
    row 8+i on BOTH sheets — that row alignment is what makes every cross-sheet
    formula a plain relative reference."""
    from openpyxl.utils import get_column_letter
    caps = fusion.matrix_capabilities()
    sensors = sorted((r for r in records if r.get("catalog") == "sensor"),
                     key=lambda r: int(r["id"][1:]))
    first_cap_col = 5                                   # column E
    col_of = {k: first_cap_col + i for i, (k, _kd) in enumerate(caps)}
    return dict(
        caps=caps, sensors=sensors, col_of=col_of,
        first_row=8, last_row=7 + len(sensors),
        first_cap_col=first_cap_col,
        last_cap_col=first_cap_col + len(caps) - 1,
        last_inf_col=first_cap_col + sum(1 for _k, kd in caps if kd == "inference") - 1,
        L=get_column_letter)


def add_coverage_matrix(wb, records, lay):
    """The 0/1 grid every Kit Builder formula reads. Row 5 counts how many
    OWNED sensors cover each capability; row 6 flags the uncovered ones."""
    ws = wb.create_sheet("Coverage Matrix")
    S.sheet_defaults(ws, tab_color="3A4A6B")
    L, col_of = lay["L"], lay["col_of"]
    fr, lr = lay["first_row"], lay["last_row"]

    ws.merge_cells("A1:H1")
    c = ws.cell(row=1, column=1, value="🔢 COVERAGE MATRIX — the solver's input as a live grid")
    c.font = S.Font(name=S.FONT, size=16, bold=True, color="FFFFFF")
    for i in range(1, 9):
        ws.cell(row=1, column=i).fill = S.PatternFill("solid", fgColor=S.NAVY)
    c.alignment = S.Alignment(vertical="center", indent=1)
    ws.row_dimensions[1].height = 30
    ws.merge_cells("A2:H2")
    s = ws.cell(row=2, column=1, value=(
        "One row per sensor, one column per capability; 1 = this sensor covers it. Row 5 counts "
        "how many sensors you own (Kit Builder column D) cover each capability; row 6 flags the "
        "still-uncovered outcomes. Every formula on the Kit Builder reads THIS sheet — nothing "
        "else enters the computation. The same grid, dense, is exports/coverage_matrix.csv."))
    s.font = S.sfont(9.5, italic=True, color=S.MUTED)
    s.alignment = S.Alignment(vertical="center", indent=1, wrap_text=True)
    ws.row_dimensions[2].height = 30

    ws.cell(row=3, column=4, value="kind →").font = S.sfont(8, color=S.MUTED)
    for k, kd in lay["caps"]:
        cc = ws.cell(row=3, column=col_of[k], value="INF" if kd == "inference" else "PHN")
        cc.font = S.sfont(7, bold=True,
                          color=S.NAVY if kd == "inference" else S.ACCENT)
        cc.alignment = S.Alignment(horizontal="center")

    for col, name in (1, "ID"), (2, "Sensor"), (3, "$"), (4, "Reach"):
        hc = ws.cell(row=4, column=col, value=name)
        hc.font = S.sfont(9, bold=True, color="FFFFFF")
        hc.fill = S.PatternFill("solid", fgColor=S.NAVY)
    for k, _kd in lay["caps"]:
        hc = ws.cell(row=4, column=col_of[k], value=k)
        hc.font = S.sfont(7.5, bold=True)
        hc.alignment = S.Alignment(textRotation=90, horizontal="center", vertical="bottom")
    ws.row_dimensions[4].height = 118

    ws.cell(row=5, column=2, value="OWNED sensors covering ↓").font = S.sfont(8.5, bold=True)
    ws.cell(row=6, column=2, value="1 = still uncovered ↓").font = S.sfont(8.5, bold=True, color=S.BAD)
    for k, _kd in lay["caps"]:
        col = col_of[k]
        cl = L(col)
        c5 = ws.cell(row=5, column=col,
                     value=f"=SUMPRODUCT({cl}${fr}:{cl}${lr},'Kit Builder'!$D${fr}:$D${lr})")
        c5.fill = S.PatternFill("solid", fgColor="EAF0F6")
        c5.font = S.sfont(8, bold=True)
        c6 = ws.cell(row=6, column=col, value=f"=IF({cl}5=0,1,0)")
        c6.font = S.sfont(8, color=S.MUTED)

    covers = {r["id"]: fusion.covers(r) for r in lay["sensors"]}
    for i, r in enumerate(lay["sensors"]):
        row = fr + i
        ws.cell(row=row, column=1, value=r["id"]).font = S.sfont(8, color=S.MUTED)
        ws.cell(row=row, column=2, value=r["n"]).font = S.sfont(8.5)
        usd = r.get("usd")
        ws.cell(row=row, column=3,
                value=usd if isinstance(usd, (int, float)) else 0).font = S.sfont(8)
        ws.cell(row=row, column=4, value=len(covers[r["id"]])).font = S.sfont(8)
        for k in covers[r["id"]]:
            col = col_of.get(k)
            if col:
                ws.cell(row=row, column=col, value=1)   # sparse: blanks are 0

    ws.conditional_formatting.add(
        f"E{fr}:{L(lay['last_cap_col'])}{lr}",
        S.CellIsRule(operator="equal", formula=["1"],
                     fill=S.PatternFill("solid", fgColor="CFE3D4")))
    widths = [8, 30, 6, 6] + [2.8] * len(lay["caps"])
    S.set_widths(ws, widths)
    ws.freeze_panes = "E8"
    return ws


def add_kit_builder(wb, records, sol, lay):
    """The solver, running IN the sheet. Mark what you own; everything updates."""
    ws = wb.create_sheet("Kit Builder")
    S.sheet_defaults(ws, tab_color="18645A")
    L, col_of = lay["L"], lay["col_of"]
    fr, lr = lay["first_row"], lay["last_row"]
    inf_first, inf_last = L(lay["first_cap_col"]), L(lay["last_inf_col"])
    ncols = 7

    row = _banner(
        ws, "🎛 KIT BUILDER — mark what you own, watch what you know",
        "Type 1 in a yellow cell to own that sensor. Everything recomputes live, in Excel, with "
        "no Python: which of the 151 outcomes your kit covers, what it costs, which single "
        "purchase buys the most NEW outcomes next, and which fusion instruments (Fusion Solver "
        "sheet) your kit unlocks. The FOUNDATION kit is pre-marked so the machinery is alive when "
        "you open it — clear column D to start from nothing. Computed cells are blue; edit only "
        "the yellow.", ncols)

    tiles = [
        ("Outcomes covered", f"=COUNTIF('Coverage Matrix'!${inf_first}$5:${inf_last}$5,\">0\")",
         f"of {sol['n_all']} — single-sensor coverage only"),
        ("Kit cost", f"=SUMPRODUCT($C${fr}:$C${lr},$D${fr}:$D${lr})", "sum of owned parts"),
        ("Sensors owned", f"=SUM($D${fr}:$D${lr})", ""),
    ]
    trow = row + 1
    for i, (label, formula, note) in enumerate(tiles):
        col = 1 + i * 2
        lc = ws.cell(row=trow, column=col, value=label)
        lc.font = S.sfont(9, bold=True)
        fc = ws.cell(row=trow, column=col + 1, value=formula)
        fc.font = S.sfont(14, bold=True, color=S.NAVY)
        fc.fill = S.PatternFill("solid", fgColor="EAF0F6")
        fc.alignment = S.Alignment(horizontal="center", vertical="center")
        nc = ws.cell(row=trow + 1, column=col + 1, value=note)
        nc.font = S.sfont(7.5, italic=True, color=S.MUTED)
    ws.row_dimensions[trow].height = 26
    row = trow + 2  # placeholder; fusion tiles added after blocks are placed

    # ---- sensor block (rows 8..412, aligned with the matrix)
    row = fr - 1
    for col, name in enumerate(["ID", "Sensor", "$", "Own? 0/1", "Buys next",
                                "Category", "Reach"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, horizontal="center", vertical="center")
        c.border = S.BORDER
    preload = {sid for sid, _r, _g in
               [(s["id"], None, None) for s in sol["trace_cost"][:sol["tiers"][0]["upto"]]]}
    covers = {r["id"]: fusion.covers(r) for r in lay["sensors"]}
    for i, r in enumerate(lay["sensors"]):
        rw = fr + i
        ws.cell(row=rw, column=1, value=r["id"]).font = S.sfont(8, color=S.MUTED)
        ws.cell(row=rw, column=2, value=r["n"]).font = S.sfont(8.5, bold=r["id"] in preload)
        usd = r.get("usd")
        ws.cell(row=rw, column=3,
                value=usd if isinstance(usd, (int, float)) else 0).font = S.sfont(8)
        oc = ws.cell(row=rw, column=4, value=1 if r["id"] in preload else 0)
        oc.fill = S.PatternFill("solid", fgColor="FFF3C4")
        oc.font = S.sfont(9, bold=True)
        oc.alignment = S.Alignment(horizontal="center")
        oc.border = S.BORDER
        bc = ws.cell(row=rw, column=5, value=(
            f"=IF($D{rw}=1,0,SUMPRODUCT('Coverage Matrix'!${inf_first}{rw}:${inf_last}{rw},"
            f"'Coverage Matrix'!${inf_first}$6:${inf_last}$6))"))
        bc.font = S.sfont(8.5, bold=True, color=S.NAVY)
        bc.alignment = S.Alignment(horizontal="center")
        ws.cell(row=rw, column=6, value=r.get("cat", "")).font = S.sfont(7.5, color=S.MUTED)
        ws.cell(row=rw, column=7, value=len(covers[r["id"]])).font = S.sfont(8)
        ws.row_dimensions[rw].height = 12.5
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type="list", formula1='"0,1"', allow_blank=True,
                        errorTitle="0 or 1 only", error="Own = 1, not owned = 0")
    ws.add_data_validation(dv)
    dv.add(f"D{fr}:D{lr}")
    ws.conditional_formatting.add(
        f"E{fr}:E{lr}",
        S.DataBarRule(start_type="num", start_value=0, end_type="num",
                      end_value=12, color="C8853A", showValue=True))

    # ---- outcome status block
    row = lr + 2
    row = S.section(ws, row, "EVERY OUTCOME — covered by your kit?", ncols,
                    "Routes = how many owned sensors can answer it. Red rows are what "
                    "your kit cannot yet know.")
    for col, name in enumerate(["Domain", "You want to know…", "Key",
                                "Owned routes", "Status", "", ""], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor="4A5878")
        c.border = S.BORDER
    row += 1
    out_first = row
    for k in vocab.INFERENCE:
        q, d = vocab.INFERENCE[k]
        cl = L(col_of[k])
        ws.cell(row=row, column=1, value=d).font = S.sfont(8, color=S.MUTED)
        ws.cell(row=row, column=2, value=q).font = S.sfont(8.5, bold=True)
        ws.cell(row=row, column=3, value=k).font = S.sfont(7.5, color=S.MUTED)
        rc = ws.cell(row=row, column=4, value=f"='Coverage Matrix'!${cl}$5")
        rc.font = S.sfont(8.5, bold=True)
        rc.alignment = S.Alignment(horizontal="center")
        sc = ws.cell(row=row, column=5, value=f'=IF($D{row}>0,"covered","—")')
        sc.font = S.sfont(8.5)
        sc.alignment = S.Alignment(horizontal="center")
        ws.row_dimensions[row].height = 12.5
        row += 1
    out_last = row - 1
    ws.conditional_formatting.add(
        f"A{out_first}:E{out_last}",
        S.FormulaRule(formula=[f"$D{out_first}=0"],
                      font=S.sfont(8.5, color=S.BAD),
                      fill=S.PatternFill("solid", fgColor="FBE9E4")))

    # ---- fusion edge block (topological order: chains reference earlier rows)
    row = out_last + 2
    row = S.section(ws, row, "FUSION INSTRUMENTS — what your kit unlocks beyond any sensor", ncols,
                    "Each row is a derived instrument from the Fusion Solver sheet. It lights "
                    "UNLOCKED when your kit holds every capability it needs. ×N means N "
                    "measurement points — N copies of one covering part also works.")
    for col, name in enumerate(["Instrument", "Pattern", "Needs", "Status",
                                "What you gain", "The math", ""], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor="1F6F5C")
        c.border = S.BORDER
    row += 1
    edge_first = row
    edge_row = {}
    E_ = set(fusion.EMERGENT)
    provided_by = {}
    for e in fusion.FUSION_EDGES:
        provided_by.setdefault(e["provides"], []).append(e["key"])
    for e in fusion.topo_edges():
        conds = []
        needs = []
        for cap, m in e["requires"]:
            if cap in col_of:
                cl = L(col_of[cap])
                base = f"'Coverage Matrix'!${cl}$5>={m}"
            else:
                base = None   # emergent-only capability: no matrix column
            chain = [f'$D${edge_row[k]}="UNLOCKED"' for k in provided_by.get(cap, [])
                     if k in edge_row]
            if base and chain:
                conds.append("OR(" + base + "," + ",".join(chain) + ")")
            elif base:
                conds.append(base)
            elif chain:
                conds.append("OR(" + ",".join(chain) + ")" if len(chain) > 1 else chain[0])
            needs.append(f"{'×' + str(m) + ' ' if m > 1 else ''}{cap}")
        q = (fusion.EMERGENT.get(e["provides"]) or vocab.INFERENCE.get(e["provides"]))[0]
        ws.cell(row=row, column=1, value=e["name"]).font = S.sfont(8.5, bold=True)
        ws.cell(row=row, column=2, value=e["pattern"]).font = S.sfont(7.5, color=S.MUTED)
        ws.cell(row=row, column=3, value=" + ".join(needs)).font = S.sfont(7.5)
        stc = ws.cell(row=row, column=4,
                      value=f'=IF(AND({",".join(conds)}),"UNLOCKED","—")')
        stc.font = S.sfont(8.5, bold=True)
        stc.alignment = S.Alignment(horizontal="center")
        gc = ws.cell(row=row, column=5, value=("NEW: " if e["provides"] in E_ else "route: ") + q)
        gc.font = S.sfont(7.5, color=S.NAVY if e["provides"] in E_ else S.MUTED)
        ws.cell(row=row, column=6, value=e["math"]).font = S.sfont(7, color=S.MUTED)
        ws.row_dimensions[row].height = 12.5
        edge_row[e["key"]] = row
        row += 1
    edge_last = row - 1
    ws.conditional_formatting.add(
        f"A{edge_first}:F{edge_last}",
        S.FormulaRule(formula=[f'$D{edge_first}="UNLOCKED"'],
                      fill=S.PatternFill("solid", fgColor="D9EBDD")))

    # ---- emergent tile row (needed the edge rows to exist first)
    et = ws.cell(row=trow, column=7,
                 value=f'=COUNTIF($D${edge_first}:$D${edge_last},"UNLOCKED")')
    et.font = S.sfont(14, bold=True, color="1F6F5C")
    et.fill = S.PatternFill("solid", fgColor="E4EFE6")
    et.alignment = S.Alignment(horizontal="center", vertical="center")
    lc = ws.cell(row=trow - 1, column=7, value="Fusion unlocked")
    lc.font = S.sfont(9, bold=True)
    lc.alignment = S.Alignment(horizontal="center")
    nc = ws.cell(row=trow + 1, column=7, value=f"of {len(fusion.FUSION_EDGES)} instruments")
    nc.font = S.sfont(7.5, italic=True, color=S.MUTED)
    nc.alignment = S.Alignment(horizontal="center")

    S.set_widths(ws, [8, 34, 7, 9, 10, 20, 42])
    ws.freeze_panes = f"F{fr}"
    return ws


def add_fusion_solver(wb, sol):
    """The static record of the fusion computation: edges, closures, marginals."""
    fus = sol["fusion"]
    ws = wb.create_sheet("Fusion Solver")
    S.sheet_defaults(ws, tab_color="0F5B4E")
    ncols = 8
    row = _banner(
        ws, "🧬 FUSION SOLVER — what combinations know that no sensor claims",
        f"{fus['n_edges']} derived instruments, authored from this atlas's own Derived "
        f"Quantities, Derived Instruments and Combination Grammar — now as computable data. "
        f"{fus['n_emergent']} outcomes exist in NO sensor's row because only combinations "
        "provide them. Everything below is computed against the live catalog; the Kit Builder "
        "sheet runs the same computation on YOUR kit, live.", ncols)

    for label, text in fusion.FUSION_FINDINGS:
        S.cell(ws, row, 1, label, size=9.5, bold=True, fill="FBEFD8")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9.5)
        ws.row_dimensions[row].height = max(30, 12 + len(text) // 4.4)
        row += 1
    row += 1

    # ---- tier closures
    row = S.section(ws, row, "1 · THE MULTIPLIER — each kit, closed under fusion", ncols,
                    "Declared = what the sensors claim alone (the old lower bound). "
                    "Emergent = outcomes the same parts unlock through the instruments below. "
                    "No new hardware appears anywhere in this table.")
    for col, name in enumerate(["Kit", "Parts", "Cost", "Declared", "Edges fired",
                                "Emergent", "TOTAL", "What emerges"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, horizontal="center", vertical="center")
        c.border = S.BORDER
    row += 1
    for t in fus["tier_closures"]:
        S.cell(ws, row, 1, t["name"], size=10, bold=True, color=S.NAVY,
               fill="E4EFE6", halign="center")
        S.cell(ws, row, 2, t["n"], size=10, halign="center")
        S.cell(ws, row, 3, f"${t['cost']:.0f}", size=10, halign="center")
        S.cell(ws, row, 4, t["declared"], size=10, halign="center")
        S.cell(ws, row, 5, t["fired"], size=10, halign="center")
        S.cell(ws, row, 6, f"+{t['emergent']}", size=10, bold=True, halign="center",
               fill="D9EBDD")
        S.cell(ws, row, 7, t["total"], size=11, bold=True, halign="center", fill="EAF0F6")
        S.cell(ws, row, 8, " · ".join(t["emergent_keys"]), size=7.5)
        ws.row_dimensions[row].height = max(24, 11 + len(" · ".join(t["emergent_keys"])) // 8)
        row += 1
    row += 1

    # ---- the edge table
    row = S.section(ws, row, "2 · THE INSTRUMENTS — every edge, in full", ncols,
                    "requires → provides, with the actual math. ×N = N measurement points. "
                    "Two instruments consume the OUTPUT of others (chains, marked ⛓).")
    for col, name in enumerate(["Instrument", "Pattern", "Requires", "Provides",
                                "The math", "Why it works", "What kills it",
                                "Worked build"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor="1F6F5C")
        c.alignment = S.Alignment(wrap_text=True, horizontal="center", vertical="center")
        c.border = S.BORDER
    row += 1
    E_ = set(fusion.EMERGENT)
    all_provided = {e["provides"] for e in fusion.FUSION_EDGES}
    for e in fusion.topo_edges():
        chained = any(c in all_provided for c, _m in e["requires"])
        needs = " + ".join(f"{'×' + str(m) + ' ' if m > 1 else ''}{c}"
                           for c, m in e["requires"])
        q = (fusion.EMERGENT.get(e["provides"]) or vocab.INFERENCE.get(e["provides"]))[0]
        S.cell(ws, row, 1, ("⛓ " if chained else "") + e["name"], size=8.5, bold=True)
        S.cell(ws, row, 2, e["pattern"], size=8, color=S.MUTED, halign="center")
        S.cell(ws, row, 3, needs, size=8)
        pv = S.cell(ws, row, 4, ("NEW · " if e["provides"] in E_ else "route · ") + q, size=8,
                    fill="D9EBDD" if e["provides"] in E_ else None)
        S.cell(ws, row, 5, e["math"], size=8, color=S.NAVY)
        S.cell(ws, row, 6, e["why"], size=8)
        S.cell(ws, row, 7, e["confound"], size=8, fill="FBE9E4")
        S.cell(ws, row, 8, e["example"], size=8)
        ws.row_dimensions[row].height = max(40, 12 + max(len(e["why"]), len(e["confound"])) // 5.5)
        row += 1
    row += 1

    # ---- marginal ranking
    row = S.section(ws, row, "3 · BEST NEXT PURCHASE FOR EMERGENCE", ncols,
                    "Starting from the $18 FOUNDATION kit: which single added part fires the "
                    "most new instruments? This is a different question from 'buys the most "
                    "outcomes' — and it has different answers.")
    for col, name in enumerate(["Add this", "$", "New instruments", "Emergent",
                                "Which ones", "", "", ""], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor="4A5878")
        c.border = S.BORDER
    row += 1
    seen_names = set()
    shown = 0
    for m in fus["marginal"]:
        base = m["name"].split(" (")[0][:20]   # collapse near-duplicates (PIR variants)
        if base in seen_names:
            continue
        seen_names.add(base)
        S.cell(ws, row, 1, m["name"], size=8.5, bold=True)
        S.cell(ws, row, 2, f"${m['usd']}", size=8.5, halign="center")
        S.cell(ws, row, 3, f"+{m['edges_gained']}", size=9, bold=True, halign="center",
               fill="D9EBDD")
        S.cell(ws, row, 4, f"+{m['emergent_gained']}", size=8.5, halign="center")
        ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=ncols)
        S.cell(ws, row, 5, " · ".join(m["gained_keys"]), size=8)
        ws.row_dimensions[row].height = 14
        row += 1
        shown += 1
        if shown >= 20:
            break

    S.set_widths(ws, [30, 12, 26, 26, 34, 42, 42, 36])
    ws.freeze_panes = "A4"
    return ws


def add_corrections_log(wb, changes, added=0):
    # Self-hosted builds start from an already-corrected catalog, so the diff
    # pass finds little or nothing. The v50 history (recovered from the v55
    # sheet) is the base; anything genuinely new is appended after it.
    import json
    hist_path = HERE / "data" / "corrections_v50.json"
    if hist_path.exists():
        hist = [tuple(c) for c in json.loads(hist_path.read_text())]
        seen = {(h[0], h[1]) for h in hist}
        changes = hist + [c for c in changes if (c[0], c[1]) not in seen]
        added = added or 167
    ws = wb.create_sheet("Corrections Log")
    S.sheet_defaults(ws, tab_color="A8412F")
    ncols = 5
    row = _banner(
        ws, "🩹 CORRECTIONS LOG — every cell this pass changed, and why",
        "v50's Sensor Catalog was inherited unchanged from v5. A hostile review found errors that "
        "a reference document cannot carry, including two genuine safety hazards and one "
        "instruction that destroys hardware. Each row below is one corrected cell. "
        f"A further {added} sensors were merged into the Catalog, carrying v50's own Second Life "
        "and Edge-AI Hook columns so it stays one catalog rather than two tiers.", ncols)

    headline = [
        ("🔴 SAFETY", "MQ gas sensors sited inside LPG lockers and hydrogen-accumulating battery rooms",
         "An MQ element is an unenclosed bead heated to ~300°C. In an atmosphere that can "
         "accumulate flammable gas it is a candidate IGNITION SOURCE. v50 recommended exactly this "
         "and framed it as explosion prevention. Rewritten to monitor the ventilated space OUTSIDE "
         "such volumes, with a pointer to certified intrinsically-safe detectors."),
        ("🔴 SAFETY", "Inconsistent life-safety framing across the MQ family",
         "MQ-7 carried 'NOT a life-safety device'. MQ-2, MQ-4, MQ-6 and MQ-8 made equivalent "
         "life-safety claims with no disclaimer at all. Now uniform."),
        ("🔴 HARDWARE", "XKC-Y25 documented as 'logic-safe out'",
         "Its output follows VCC. Wired per that claim at 12-24V it destroys an ESP32 GPIO. "
         "Corrected with an explicit warning."),
        ("🟠 FACTUAL", "GL5528 photoresistor resistance stated backwards",
         "'~10kΩ dark to ~1kΩ bright' is wrong by about two orders of magnitude — a GL5528 is "
         "~0.5-2MΩ in darkness. Anyone sizing a divider from that figure gets it badly wrong."),
        ("🟠 FACTUAL", "VL53L0X described as 'immune to target color'",
         "Reflectivity is the DOMINANT range variable: ST quotes ~2m on white against ~0.8m on "
         "dark grey. The false claim propagated into the L1X and L5CX entries too."),
        ("🟠 FACTUAL", "MPRLS labelled gauge pressure",
         "The MPRLS0025PA is ABSOLUTE — it reads ~14.7 PSI on the bench. Every listed use (tank "
         "depth, tensiometer, blood-pressure cuff) requires subtracting atmospheric, which was "
         "never mentioned."),
        ("🟠 PROVENANCE", "A fabricated Adafruit product number",
         "'Adafruit 5417' was cited as an ADXL355 breakout with an 'Adafruit_ADXL355' library. "
         "Adafruit 5417 is a MicroPython Pyboard Lite; neither the breakout nor the library "
         "exists. Replaced with real sources."),
        ("🟠 FACTUAL", "Eight sensors whose NAME was wrong",
         "Watermark called a tensiometer (it is a granular-matrix resistance sensor) · TUF-2000M "
         "called Doppler (it is transit-time) · MQ-8 called MEMS (heated SnO2) · SEN0395 called "
         "60GHz (it is 24GHz) · an AS7331 'flame sensor' that was actually a KY-026 IR "
         "phototransistor, blind to flame UV · narrowband HEGO merged with wideband LSU, implying "
         "an LSU can be read on a bare ADC, which it cannot."),
        ("🟡 OVERSTATEMENT", "Missing caveats that change real builds",
         "NDIR CO2 needs ambient-pressure compensation · optical PM sensors over-read above ~75% "
         "RH · AS3935 fires milliseconds after validation, not microseconds, and false-triggers on "
         "switching supplies · GPS PPS is nanoseconds at the pin and microseconds through an ESP32 "
         "interrupt · the ESP32's internal hall sensor was REMOVED in ESP-IDF v5 · HuskyLens face "
         "recognition is trained on human faces, so the cat-door build needs a custom model."),
    ]
    S.cell(ws, row, 1, "SEVERITY", size=9, bold=True, color="FFFFFF", fill=S.NAVY, halign="center")
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=2)
    S.cell(ws, row, 2, "WHAT WAS WRONG", size=9, bold=True, color="FFFFFF", fill=S.NAVY)
    ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=ncols)
    S.cell(ws, row, 3, "WHY IT MATTERS", size=9, bold=True, color="FFFFFF", fill=S.NAVY)
    row += 1
    for sev, what, why in headline:
        fill = "F8DED7" if "🔴" in sev else ("FBEFD8" if "🟠" in sev else "F5F2EB")
        S.cell(ws, row, 1, sev, size=9, bold=True, halign="center", fill=fill)
        S.cell(ws, row, 2, what, size=9, bold=True)
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=ncols)
        S.cell(ws, row, 3, why, size=9)
        ws.row_dimensions[row].height = max(30, 12 + len(why) // 4.4)
        row += 1

    row += 1
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = S.cell(ws, row, 1, f"CELL-BY-CELL: {len(changes)} cells changed across "
                           f"{len({x[0] for x in changes})} sensors", size=12, bold=True,
               color=S.NAVY, fill=S.ACCENT_SOFT)
    ws.row_dimensions[row].height = 22
    row += 1
    for col, name in enumerate(["Sensor", "Column", "Was", "Now", ""], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor="4A5878")
        c.border = S.BORDER
    row += 1
    for sensor, colname, old, new in changes:
        S.cell(ws, row, 1, sensor, size=8.5, bold=True)
        S.cell(ws, row, 2, colname, size=8.5, color=S.MUTED)
        S.cell(ws, row, 3, old, size=8.5, fill="FBE9E4")
        ws.merge_cells(start_row=row, start_column=4, end_row=row, end_column=ncols)
        S.cell(ws, row, 4, new, size=8.5, fill="E7F0E9")
        ws.row_dimensions[row].height = max(24, 11 + max(len(old), len(new)) // 9.0)
        row += 1
    S.set_widths(ws, [26, 20, 52, 52, 30])
    ws.freeze_panes = "A4"
    return ws


_UNUSED_EXP_COLS = [
    ("ID", 7), ("Sensor", 24), ("Category", 19), ("What It Measures", 30),
    ("How It Works (Plain English)", 46), ("What Fools It", 46), ("Modality", 12),
    ("Interface", 14), ("Range", 20), ("Accuracy", 18), ("Contact", 14), ("Privacy", 13),
    ("Hazard", 13), ("Power Draw", 14), ("≈$", 8), ("Diff", 6), ("Requires", 30),
    ("Substitutes", 32), ("Where To Buy", 20), ("Invention Sparks", 40),
]


def _unused_add_expansion(wb, records):
    """The 175 parts v50's catalog does not contain, in a richer column set."""
    v50_names = set()
    ws0 = wb["Sensor Catalog"]
    for r in range(4, ws0.max_row + 1):
        n = ws0.cell(row=r, column=2).value
        if n:
            v50_names.add(n)
    new = [r for r in records if r.get("catalog") == "sensor" and r["n"] not in v50_names]

    ws = wb.create_sheet("Catalog Expansion")
    S.sheet_defaults(ws, tab_color="C8853A")
    ncols = len(EXP_COLS)
    row = _banner(
        ws, f"➕ CATALOG EXPANSION — {len(new)} sensors the Catalog does not yet contain",
        "Fills the gaps a coverage audit found: ultra-wideband, 4-20mA current loop, CAN/TWAI, "
        "UHF RAIN RFID, Sensirion SEN5x/SEN66, percent-level CO2, the modern IMU landscape, "
        "AS7265x and AS7343 spectral, newer ST time-of-flight, optical flow, battery fuel gauges, "
        "energy-metering AFEs, ion-selective electrodes and research soil probes. "
        "Carries four columns the main Catalog has no place for: what fools it, contact class, "
        "privacy profile and declared hazards.", ncols)
    for col, (name, _w) in enumerate(EXP_COLS, 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = S.BORDER
    row += 1
    for rec in sorted(new, key=lambda r: (r["cat"], r["n"])):
        vals = [
            rec["id"], rec["n"], rec["cat"], rec.get("meas", ""), rec.get("how", ""),
            rec.get("fools", ""), rec.get("modality", ""),
            "/".join(rec.get("iface") or []), rec.get("range", ""), rec.get("accuracy", ""),
            rec.get("contact", ""), S.PRIVACY_BADGE.get(rec.get("privacy"), ""),
            " ".join(S.HAZARD_BADGE.get(h, h) for h in (rec.get("hazard") or [])),
            rec.get("pwr", ""), rec.get("usd"), rec.get("diff"),
            rec.get("requires", ""), rec.get("substitutes", ""),
            ", ".join(rec.get("buy") or []), rec.get("spark", ""),
        ]
        for col, v in enumerate(vals, 1):
            S.cell(ws, row, col, v, size=8.5,
                   halign="center" if col in (1, 15, 16) else "left")
        ws.cell(row=row, column=2).font = S.sfont(9, bold=True)
        ws.cell(row=row, column=6).fill = S.PatternFill("solid", fgColor="FBE9E4")
        pv = rec.get("privacy")
        if pv in S.PRIVACY_FILL:
            ws.cell(row=row, column=12).fill = S.PatternFill("solid", fgColor=S.PRIVACY_FILL[pv])
        if rec.get("hazard"):
            ws.cell(row=row, column=13).font = S.sfont(8, bold=True, color=S.BAD)
        ws.row_dimensions[row].height = 56
        row += 1
    S.set_widths(ws, [w for _n, w in EXP_COLS])
    ws.freeze_panes = "C4"
    return ws


def add_catalog(wb, records, kind, sheet_name, title, subtitle):
    items = [r for r in records if r.get("catalog") == kind]
    if not items:
        return None
    cols = [("ID", 7), ("Part", 26), ("What It Brings", 34), ("How It Works", 46),
            ("What Fools It", 46), ("Interface", 14), ("Voltage", 16), ("≈$", 8),
            ("Diff", 6), ("Requires", 30), ("Substitutes", 32), ("Where To Buy", 20),
            ("Why It Matters", 40)]
    ws = wb.create_sheet(sheet_name)
    S.sheet_defaults(ws, tab_color="4A5878" if kind == "glue" else "2F5D50")
    row = _banner(ws, title, subtitle, len(cols))
    for col, (name, _w) in enumerate(cols, 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = S.BORDER
    row += 1
    for rec in sorted(items, key=lambda r: r["n"]):
        vals = [rec["id"], rec["n"], rec.get("meas", ""), rec.get("how", ""), rec.get("fools", ""),
                "/".join(rec.get("iface") or []), rec.get("v", ""), rec.get("usd"),
                rec.get("diff"), rec.get("requires", ""), rec.get("substitutes", ""),
                ", ".join(rec.get("buy") or []), rec.get("spark", "")]
        for col, v in enumerate(vals, 1):
            S.cell(ws, row, col, v, size=8.5, halign="center" if col in (1, 8, 9) else "left")
        ws.cell(row=row, column=2).font = S.sfont(9, bold=True)
        ws.cell(row=row, column=5).fill = S.PatternFill("solid", fgColor="FBE9E4")
        ws.row_dimensions[row].height = 62
        row += 1
    S.set_widths(ws, [w for _n, w in cols])
    ws.freeze_panes = "C4"
    return ws


def add_wiring(wb, records):
    import re
    from collections import defaultdict
    ws = wb.create_sheet("I2C & Wiring Reality")
    S.sheet_defaults(ws, tab_color="6E7F5E")
    ncols = 6
    row = _banner(
        ws, "🔌 I²C ADDRESS MAP & WIRING REALITY",
        "The sheet that stops projects dying. Two parts at the same fixed address cannot share a "
        "bus. v50 recommends multi-sensor stacks in several places without noting that some of "
        "them are not physically buildable as written.", ncols)
    by_addr = defaultdict(list)
    for r in records:
        for a in re.findall(r"0x[0-9A-Fa-f]{2}", str(r.get("i2c_addr") or "")):
            by_addr[a.upper().replace("0X", "0x")].append(r)
    for col, name in enumerate(["Address", "#", "Conflict?", "Parts sharing it",
                                "Can it be changed?", "The fix"], 1):
        c = ws.cell(row=row, column=col, value=name)
        c.font = S.sfont(9, bold=True, color="FFFFFF")
        c.fill = S.PatternFill("solid", fgColor=S.NAVY)
        c.alignment = S.Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = S.BORDER
    row += 1
    for addr in sorted(by_addr):
        parts = by_addr[addr]
        conflict = len(parts) > 1
        changeable = [p for p in parts if "jumper" in str(p.get("i2c_addr", "")).lower()
                      or "/" in str(p.get("i2c_addr", "")) or "-" in str(p.get("i2c_addr", ""))]
        vals = [addr, len(parts), "⚠ YES" if conflict else "—",
                " · ".join(p["n"] for p in parts),
                f"{len(changeable)} of {len(parts)} have a selectable address" if conflict else "n/a",
                ("Use a TCA9548A multiplexer, or set jumpers so each part gets a distinct address. "
                 "Fixed-address parts must go behind the mux." if conflict else "")]
        for col, v in enumerate(vals, 1):
            S.cell(ws, row, col, v, size=8.5, halign="center" if col in (1, 2, 3) else "left")
        ws.cell(row=row, column=1).font = S.sfont(9, bold=True, name=S.MONO)
        if conflict:
            ws.cell(row=row, column=3).font = S.sfont(9, bold=True, color=S.BAD)
            ws.cell(row=row, column=3).fill = S.PatternFill("solid", fgColor="FBE3DE")
        ws.row_dimensions[row].height = 30
        row += 1
    row += 1
    for title, text in [
        ("The ToF trap", "The entire ST VL53/VL6180 family ships at a FIXED 0x29. Two on one bus "
         "is impossible without driving each XSHUT low and assigning addresses one at a time at "
         "boot. Any project using several ToF sensors must budget for this — it is the single "
         "most common reason a multi-ToF build never works."),
        ("0x68 is crowded", "MPU-6050, MPU-9250, ICM-20948 and the DS3231 RTC all default here. "
         "Most IMUs have an AD0 pin that moves them to 0x69; the RTC usually does not move."),
        ("0x29 is crowded too", "TCS34725 colour and the whole VL53 family share it, so "
         "colorimetry plus ranging on one bus needs a multiplexer."),
        ("Pull-ups add up", "Every breakout carries its own 4.7k pull-ups. Six boards in parallel "
         "gives ~780Ω, which is too strong and the bus stops working reliably. Remove them on all "
         "but one or two boards."),
        ("ADC2 dies with Wi-Fi", "On the classic ESP32, ADC2 cannot be used while Wi-Fi is "
         "active. Put every analog sensor on ADC1, or accept that readings stop when the radio "
         "comes up."),
        ("Check logic levels first", "Plenty of sealed industrial and automotive parts output at "
         "their supply rail. An open-collector sensor pulled up to 24V destroys a GPIO — the "
         "XKC-Y25 correction in this workbook exists for exactly that reason."),
    ]:
        S.cell(ws, row, 1, title, size=9, bold=True, fill="F5F2EB")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9)
        ws.row_dimensions[row].height = max(28, 12 + len(text) // 3.6)
        row += 1
    S.set_widths(ws, [12, 8, 11, 58, 32, 52])
    return ws


if __name__ == "__main__":
    main()
