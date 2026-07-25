#!/usr/bin/env python3
"""Build the ESP32 Sensor Universe workbook (v6, "The Invention Atlas").

    python3 validate.py && python3 build_workbook.py [out.xlsx]

Sheet groups:
    Orient    START HERE · Dashboard · Provenance
    Catalogs  Sensors · Actuators · Glue · Boards
    Read      Sensor Cards
    Query     Phenomenon Index · Inference Atlas · Constraint Navigator
    Group     Categories · Themes · Modality Map
    Create    Fusion Grammar · Synergy Matrix · Invention Seeds
    Build     I2C & Wiring · Power Budget · Project Archetypes
    Legacy    ESP32 Capabilities
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))
sys.path.insert(0, str(HERE))

import schema      # noqa: E402
import vocab       # noqa: E402
import sheet_lib as S  # noqa: E402
from loader import load_all  # noqa: E402

try:
    import archetypes  # noqa: E402
    ARCHETYPES = archetypes.ARCHETYPES
except ModuleNotFoundError:
    ARCHETYPES = []
try:
    import inference_notes  # noqa: E402
    INF_NOTES = inference_notes.NOTES
except ModuleNotFoundError:
    INF_NOTES = {}

# Sheet order and the short labels used in the nav bar.
SHEETS = [
    ("START HERE", "START"), ("Dashboard", "Dash"), ("Sensor Catalog", "Sensors"),
    ("Sensor Cards", "Cards"), ("Actuators", "Actuators"), ("Glue & Signal Chain", "Glue"),
    ("Boards & Compute", "Boards"), ("Phenomenon Index", "Measure…"),
    ("Inference Atlas", "Know…"), ("Constraint Navigator", "Constraints"),
    ("Categories", "Categories"), ("Themes", "Themes"), ("Modality Map", "Modality"),
    ("Fusion Grammar", "Fusion"), ("Synergy Matrix", "Synergy"),
    ("Invention Seeds", "Seeds"), ("I2C & Wiring", "Wiring"),
    ("Power Budget", "Power"), ("Project Archetypes", "Archetypes"),
    ("Buying Guide", "Buying"), ("ESP32 Capabilities", "ESP32"), ("Provenance", "Provenance"),
]
NAV_COLS = len(SHEETS)


def new_sheet(wb, name, title, subtitle, ncols, tab=None):
    ws = wb.create_sheet(name)
    S.sheet_defaults(ws, tab_color=tab or S.NAVY)
    S.nav_bar(ws, SHEETS, name, max(ncols, NAV_COLS))
    row = S.banner(ws, title, subtitle, ncols, row=2)
    return ws, row


def joinlist(v, sep=" · "):
    if isinstance(v, (list, tuple)):
        return sep.join(str(x) for x in v)
    return str(v) if v is not None else ""


def hazard_badges(r):
    return " ".join(S.HAZARD_BADGE.get(h, h) for h in (r.get("hazard") or []))


# ============================================================ catalogs

CATALOG_COLS = [
    ("ID", 7), ("Part", 24), ("Category", 19), ("What it measures", 30),
    ("Modality", 12), ("Interface", 15), ("Range", 20), ("Accuracy", 17),
    ("Contact", 14), ("Privacy", 15), ("Power", 13), ("$", 8), ("Tier", 7),
    ("Diff", 7), ("Hazard", 14), ("Lifecycle", 11), ("Buy from", 22), ("Themes", 18),
]


def sheet_catalog(wb, records, kind, name, title, subtitle, tab):
    items = [r for r in records if r.get("catalog") == kind]
    headers = S.unique_headers([h for h, _ in CATALOG_COLS])
    ws, row = new_sheet(wb, name, title, subtitle, len(headers), tab)
    hdr = row
    S.table_header(ws, hdr, headers)
    r0 = hdr + 1
    for i, rec in enumerate(items):
        rr = r0 + i
        mfill = schema.MODALITY_COLOR.get(rec.get("modality"), "EFEFEF")
        vals = [
            rec["id"], rec["n"], rec["cat"], rec.get("meas", ""),
            rec.get("modality") or "", joinlist(rec.get("iface"), "/"),
            rec.get("range") or "", rec.get("accuracy") or "",
            rec.get("contact") or "", S.PRIVACY_BADGE.get(rec.get("privacy"), ""),
            rec.get("pwr") or "", rec.get("usd"), rec["_tier"], rec.get("diff"),
            hazard_badges(rec), rec.get("lifecycle") or "",
            joinlist(rec.get("buy"), ", "), joinlist(rec.get("tags"), ", "),
        ]
        for c, v in enumerate(vals, 1):
            S.cell(ws, rr, c, v, size=9,
                   halign="center" if c in (1, 12, 13, 14) else "left")
        ws.cell(row=rr, column=1).font = S.sfont(9, bold=True, color=S.MUTED)
        S.link_to(ws.cell(row=rr, column=1), "Sensor Cards", f"A{rr}", tooltip=rec["n"])
        ws.cell(row=rr, column=2).font = S.sfont(10, bold=True)
        ws.cell(row=rr, column=5).fill = S.PatternFill("solid", fgColor=mfill)
        pv = rec.get("privacy")
        if pv in S.PRIVACY_FILL:
            ws.cell(row=rr, column=10).fill = S.PatternFill("solid", fgColor=S.PRIVACY_FILL[pv])
        if rec.get("hazard"):
            ws.cell(row=rr, column=15).font = S.sfont(8, bold=True, color=S.BAD)
        ws.row_dimensions[rr].height = 28
    last = r0 + len(items) - 1
    if items:
        S.make_table(ws, hdr, last, len(headers), f"tbl{kind.capitalize()}")
        S.price_bars(ws, 12, r0, last)
        S.difficulty_icons(ws, 14, r0, last)
    S.set_widths(ws, [w for _, w in CATALOG_COLS])
    ws.freeze_panes = ws.cell(row=r0, column=3)
    S.print_ready(ws, len(headers), repeat_rows=f"1:{hdr}")
    return ws


# ============================================================ cards

def sheet_cards(wb, records):
    """One part per block, laid out to be READ. v5 buried 500-char prose in a
    20-column grid at 86pt row height, which nobody can read."""
    sensors = [r for r in records if r.get("catalog") == "sensor"]
    ncols = 8
    ws, row = new_sheet(
        wb, "Sensor Cards", "🔍 SENSOR CARDS — the full detail, laid out to be read",
        "Every sensor in depth: how it works, what fools it, what it unlocks. "
        "Jump here from any catalog ID. Use Excel's outline (+/−) at the left to collapse rows.",
        ncols, tab=S.ACCENT)
    S.set_widths(ws, [10, 20, 26, 26, 26, 24, 24, 24])

    for rec in sensors:
        mfill = schema.MODALITY_COLOR.get(rec.get("modality"), "EFEFEF")
        # header strip
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 1, rec["id"], size=10, bold=True, halign="center",
               fill=mfill, color=S.NAVY)
        t = S.cell(ws, row, 2, f"{rec['n']}   ·   {rec.get('pn','')}", size=12, bold=True,
                   fill=mfill, color=S.NAVY)
        t.alignment = S.Alignment(vertical="center", indent=1)
        ws.row_dimensions[row].height = 22
        row += 1

        meta = [
            ("Category", f"{rec['cat']} › {rec.get('sub','')}"),
            ("Measures", rec.get("meas", "")),
            ("Modality", rec.get("modality") or "—"),
            ("Interface", joinlist(rec.get("iface"), " / ")),
            ("Supply", rec.get("v", "")),
            ("Price", f"${rec.get('usd')}  ({rec['_tier']})"),
            ("Difficulty", f"{rec.get('diff')} — {schema.DIFFICULTY_RUBRIC.get(rec.get('diff'),'')}"),
        ]
        for i in range(0, len(meta), 2):
            pair = meta[i:i + 2]
            S.cell(ws, row, 1, pair[0][0], size=8, bold=True, color=S.MUTED, halign="right")
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
            S.cell(ws, row, 2, pair[0][1], size=9)
            if len(pair) > 1:
                S.cell(ws, row, 5, pair[1][0], size=8, bold=True, color=S.MUTED, halign="right")
                ws.merge_cells(start_row=row, start_column=6, end_row=row, end_column=ncols)
                S.cell(ws, row, 6, pair[1][1], size=9)
            ws.row_dimensions[row].height = 15
            row += 1

        blocks = [
            ("HOW IT WORKS", rec.get("how", ""), None),
            ("WHAT FOOLS IT", rec.get("fools", ""), "FBE9E4"),
            ("COMMON USES", rec.get("use", ""), None),
            ("INVENTION SPARK", rec.get("spark", ""), "FDF3E3"),
            ("REQUIRES (hard dependencies)", rec.get("requires", ""), None),
            ("SUBSTITUTES", rec.get("substitutes", ""), None),
            ("PAIRS WELL WITH", rec.get("pair", ""), None),
        ]
        for label, text, fill in blocks:
            if not text:
                continue
            S.cell(ws, row, 1, label.split()[0][:9], size=8, bold=True,
                   color=S.MUTED, halign="right")
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
            c = S.cell(ws, row, 2, text, size=9, fill=fill)
            c.alignment = S.Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[row].height = max(15, min(70, 12 + len(text) // 12))
            row += 1

        # detail strip
        det = []
        for lbl, key in (("Range", "range"), ("Accuracy", "accuracy"), ("Resolution", "resolution"),
                         ("Rate", "rate"), ("Warm-up", "warmup"), ("I2C addr", "i2c_addr"),
                         ("Calibration", "calibration"), ("Consumable", "consumable"),
                         ("Environment", "environment"), ("Lifecycle", "lifecycle"),
                         ("Maturity", "maturity"), ("ESP32", "esp32_compat")):
            v = rec.get(key)
            if v:
                det.append(f"{lbl}: {joinlist(v, ', ')}")
        if det:
            S.cell(ws, row, 1, "specs", size=8, bold=True, color=S.MUTED, halign="right")
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
            S.cell(ws, row, 2, "   ".join(det), size=8, color=S.MUTED)
            ws.row_dimensions[row].height = max(14, min(40, 12 + len("".join(det)) // 14))
            row += 1

        if rec.get("hazard"):
            S.cell(ws, row, 1, "⚠", size=10, bold=True, color=S.BAD, halign="right")
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
            S.cell(ws, row, 2, "HAZARD: " + ", ".join(
                f"{h} — {schema.HAZARD[h]}" for h in rec["hazard"] if h in schema.HAZARD),
                size=9, bold=True, color=S.BAD, fill="F8DED7")
            ws.row_dimensions[row].height = 22
            row += 1

        # sourcing + provenance
        S.cell(ws, row, 1, "buy", size=8, bold=True, color=S.MUTED, halign="right")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        src = f"{joinlist(rec.get('buy'), ' · ')}   |   boards: {rec.get('brd','')}   |   lib: {rec.get('lib','')}"
        if rec.get("link"):
            src += f"   |   {rec['link']}"
        src += f"   [{rec.get('confidence','High')}"
        src += f", {rec['as_of']}]" if rec.get("as_of") else "]"
        S.cell(ws, row, 2, src, size=8, color=S.MUTED)
        ws.row_dimensions[row].height = 16
        row += 1

        # inference chips — the "what this unlocks" payoff
        infs = [i for i in (rec.get("inferences") or []) if i in vocab.INFERENCE]
        if infs:
            S.cell(ws, row, 1, "unlocks", size=8, bold=True, color=S.NAVY, halign="right")
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
            S.cell(ws, row, 2, "  •  ".join(vocab.INFERENCE[i][0] for i in infs),
                   size=9, italic=True, color=S.NAVY, fill="EAF0F6")
            ws.row_dimensions[row].height = max(15, min(45, 12 + len(infs) * 6))
            row += 1

        row += 1  # gap between cards
    ws.freeze_panes = "A4"
    return ws


# ============================================================ query sheets

def sheet_phenomenon(wb, records):
    ncols = 7
    ws, row = new_sheet(
        wb, "Phenomenon Index", "🔬 PHENOMENON INDEX — “I want to measure X”",
        "Reverse lookup. Pick the physical quantity, see every part that can sense it, "
        "sorted cheapest first, with the trade-off made explicit.", ncols, tab="6E8B74")
    headers = S.unique_headers(["Phenomenon", "What it is", "#", "Cheapest route",
                                "No-contact route", "Lowest-power route", "All parts"])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1
    by_phen = defaultdict(list)
    for r in records:
        for p in r.get("phenomena") or []:
            by_phen[p].append(r)
    for phen, desc in vocab.PHENOMENON.items():
        parts = by_phen.get(phen, [])
        if not parts:
            continue
        priced = [p for p in parts if isinstance(p.get("usd"), (int, float))]
        cheap = min(priced, key=lambda p: p["usd"]) if priced else None
        nocontact = [p for p in parts if p.get("contact") in ("Through-barrier", "Standoff", "Remote")]
        nc = min(nocontact, key=lambda p: p.get("usd") or 1e9) if nocontact else None
        powered = [p for p in parts if isinstance(p.get("pwr_ua"), (int, float))]
        lp = min(powered, key=lambda p: p["pwr_ua"]) if powered else None
        vals = [
            phen, desc, len(parts),
            f"{cheap['n']} (${cheap['usd']:g})" if cheap else "—",
            f"{nc['n']} — {nc['contact']}" if nc else "—",
            f"{lp['n']} ({lp['pwr']})" if lp else "—",
            " · ".join(p["n"] for p in sorted(parts, key=lambda p: p.get("usd") or 0)[:14]),
        ]
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9, halign="center" if c == 3 else "left")
        ws.cell(row=row, column=1).font = S.sfont(9, bold=True, name=S.MONO)
        ws.row_dimensions[row].height = 30
        row += 1
    S.make_table(ws, hdr, row - 1, ncols, "tblPhenomena")
    S.set_widths(ws, [24, 34, 6, 26, 28, 24, 60])
    ws.freeze_panes = ws.cell(row=hdr + 1, column=2)
    return ws


ROUTE_DEFS = [
    ("💵 Cheapest", lambda p: isinstance(p.get("usd"), (int, float)), lambda p: p.get("usd", 1e9)),
    ("🎯 Most capable", lambda p: True, lambda p: -((p.get("usd") or 0) + (p.get("diff") or 0) * 8)),
    ("🚫 No contact", lambda p: p.get("contact") in ("Through-barrier", "Standoff", "Remote"),
     lambda p: p.get("usd") or 1e9),
    ("🔒 Privacy-safe", lambda p: p.get("privacy") in ("None", "Aggregate"), lambda p: p.get("usd") or 1e9),
    ("🔋 Lowest power", lambda p: isinstance(p.get("pwr_ua"), (int, float)), lambda p: p.get("pwr_ua", 1e12)),
    ("🧑‍🔧 Easiest", lambda p: isinstance(p.get("diff"), int), lambda p: (p.get("diff", 9), p.get("usd") or 0)),
]


def sheet_inference(wb, records):
    """The heart of v6: one thing you want to KNOW -> many sensor routes to it."""
    ncols = 9
    ws, row = new_sheet(
        wb, "Inference Atlas", "🧠 INFERENCE ATLAS — “I want to know Y”",
        "A sensor never measures what you want to know; it measures a proxy. This sheet starts "
        "from the KNOWING and works back to the parts. Each row offers several routes to the "
        "same answer — they differ in cost, privacy, power and what fools them. Choosing the "
        "route is the design act.", ncols, tab="8A6FA8")
    headers = S.unique_headers(["Domain", "You want to know…", "#",
                                *[n for n, _, _ in ROUTE_DEFS],
                                ][:3] + [n for n, _, _ in ROUTE_DEFS])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1

    by_inf = defaultdict(list)
    for r in records:
        for i in r.get("inferences") or []:
            by_inf[i].append(r)

    for key, (question, domain) in vocab.INFERENCE.items():
        parts = by_inf.get(key, [])
        if not parts:
            continue
        vals = [domain, question, len(parts)]
        for _label, filt, sortk in ROUTE_DEFS:
            cands = [p for p in parts if filt(p)]
            best = sorted(cands, key=sortk)[0] if cands else None
            if best is None:
                vals.append("—")
            else:
                extra = f"${best['usd']:g}" if isinstance(best.get("usd"), (int, float)) else ""
                vals.append(f"{best['n']}\n{extra}")
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9, halign="center" if c == 3 else "left")
        ws.cell(row=row, column=2).font = S.sfont(10, bold=True, color=S.NAVY)
        ws.cell(row=row, column=1).fill = S.PatternFill("solid", fgColor="EDE7F3")
        ws.row_dimensions[row].height = 32
        row += 1
    S.make_table(ws, hdr, row - 1, ncols, "tblInference")
    S.set_widths(ws, [17, 34, 6, 22, 22, 22, 22, 22, 22])
    ws.freeze_panes = ws.cell(row=hdr + 1, column=3)

    # authored commentary, where present
    if INF_NOTES:
        row += 1
        row = S.section(ws, row, "WHAT FOOLS EACH APPROACH, AND WHAT IT UNLOCKS", ncols,
                        "Route-level caveats: the failure modes that belong to the METHOD "
                        "rather than to any one part.")
        S.table_header(ws, row, S.unique_headers(
            ["You want to know…", "What fools this whole approach", "What it unlocks",
             "Who pays for it", "", "", "", "", ""]))
        row += 1
        for key, note in INF_NOTES.items():
            if key not in vocab.INFERENCE:
                continue
            S.cell(ws, row, 1, vocab.INFERENCE[key][0], size=9, bold=True)
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
            S.cell(ws, row, 2, note.get("fools", ""), size=9, fill="FBE9E4")
            ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=7)
            S.cell(ws, row, 5, note.get("unlocks", ""), size=9)
            ws.merge_cells(start_row=row, start_column=8, end_row=row, end_column=9)
            S.cell(ws, row, 8, note.get("market", ""), size=9, color=S.MUTED)
            ws.row_dimensions[row].height = 34
            row += 1
    return ws


def sheet_constraints(wb, records):
    ncols = 6
    ws, row = new_sheet(
        wb, "Constraint Navigator", "⛓ CONSTRAINT NAVIGATOR — start from what you CAN'T do",
        "Constraints generate inventions far more reliably than open brainstorming. "
        "Pick the thing blocking you; these are the parts that survive it.", ncols, tab="9A6B5A")
    headers = S.unique_headers(["Constraint", "How it's satisfied", "#",
                                "Best picks", "Cheapest", "Watch out for"])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1

    def pick(pred):
        return [r for r in records if r.get("catalog") == "sensor" and pred(r)]

    rules = {
        "no-touch": lambda r: r.get("contact") in ("Through-barrier", "Standoff", "Remote"),
        "through-wall": lambda r: r.get("contact") == "Through-barrier",
        "no-power": lambda r: r.get("_power_class") in ("Zero", "Nanoamp", "Microamp"),
        "no-privacy": lambda r: r.get("privacy") in ("None", "Aggregate"),
        "invisible": lambda r: r.get("contact") in ("Through-barrier", "Remote")
                               or (r.get("pins") or 9) <= 2,
        "underwater": lambda r: "Submersible" in (r.get("environment") or []),
        "outdoors": lambda r: "Outdoor" in (r.get("environment") or []),
        "cheap": lambda r: isinstance(r.get("usd"), (int, float)) and r["usd"] < 5,
        "beginner": lambda r: (r.get("diff") or 9) <= 2 and r.get("maturity") in ("Excellent", "Good"),
        "fast": lambda r: "kHz" in str(r.get("rate", "")) or "MHz" in str(r.get("rate", "")),
        "tiny": lambda r: (r.get("pins") or 9) <= 2 and (r.get("pwr_ua") or 1e9) < 5000,
        "harsh": lambda r: "Harsh" in (r.get("environment") or []),
        "no-calibration": lambda r: r.get("calibration") in ("None", "One-point")
                                    and not r.get("consumable"),
        "safe-for-life": lambda r: bool(r.get("hazard")),
        "long-range": lambda r: r.get("contact") == "Remote",
        "no-line-of-sight": lambda r: r.get("modality") in ("RF", "Magnetic", "Acoustic", "Mechanical"),
    }
    caveat = {
        "safe-for-life": "These parts carry declared hazards. Hobby sensors SUPPLEMENT a "
                         "certified alarm — they never replace one.",
        "no-privacy": "Radar and thermal beat cameras here, but a fine-enough thermal array "
                      "or a tracking radar can still be re-identifying in a small space.",
        "cheap": "Cheap parts are a quality lottery — buy two or three of everything, and "
                 "expect clone substitutions.",
        "no-power": "The µA figure is the sensor alone; the ESP32's radio dominates the "
                    "budget unless you deep-sleep between readings.",
    }
    for key, (statement, satisfied) in vocab.CONSTRAINT.items():
        parts = pick(rules.get(key, lambda r: False))
        parts.sort(key=lambda p: (p.get("diff") or 9, p.get("usd") or 1e9))
        priced = [p for p in parts if isinstance(p.get("usd"), (int, float))]
        cheap = min(priced, key=lambda p: p["usd"]) if priced else None
        vals = [statement, satisfied, len(parts),
                " · ".join(p["n"] for p in parts[:10]) or "—",
                f"{cheap['n']} (${cheap['usd']:g})" if cheap else "—",
                caveat.get(key, "")]
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9, halign="center" if c == 3 else "left")
        ws.cell(row=row, column=1).font = S.sfont(10, bold=True, color=S.NAVY)
        ws.row_dimensions[row].height = 46
        row += 1
    S.make_table(ws, hdr, row - 1, ncols, "tblConstraints")
    S.set_widths(ws, [34, 30, 6, 62, 24, 40])
    ws.freeze_panes = ws.cell(row=hdr + 1, column=2)
    return ws


# ============================================================ grouping sheets

def sheet_categories(wb, records):
    ncols = 7
    ws, row = new_sheet(wb, "Categories", "🗂 CATEGORY GUIDE — the families",
                        "What each family does and when to reach for it. "
                        "Categories are a primary shelf; cross-cutting lives in Phenomena and Themes.",
                        ncols, tab="6E8B74")
    headers = S.unique_headers(["Category", "#", "What this family does", "Reach for it when…",
                                "Cheapest entry", "Deepest cut", "Dominant modality"])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1
    by_cat = defaultdict(list)
    for r in records:
        by_cat[r["cat"]].append(r)
    for cat, (emoji, what, when) in vocab.CATEGORY.items():
        items = by_cat.get(cat, [])
        if not items:
            continue
        priced = [s for s in items if isinstance(s.get("usd"), (int, float))]
        cheap = min(priced, key=lambda s: s["usd"]) if priced else None
        deep = max(items, key=lambda s: ((s.get("diff") or 0), s.get("usd") or 0))
        mods = Counter(s.get("modality") for s in items if s.get("modality"))
        dom = mods.most_common(1)[0][0] if mods else "—"
        vals = [f"{emoji} {cat}", len(items), what, when,
                f"{cheap['n']} (${cheap['usd']:g})" if cheap else "—",
                f"{deep['n']} (lvl {deep.get('diff')})", dom]
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9, halign="center" if c == 2 else "left")
        ws.cell(row=row, column=1).font = S.sfont(10, bold=True)
        ws.cell(row=row, column=7).fill = S.PatternFill(
            "solid", fgColor=schema.MODALITY_COLOR.get(dom, "EFEFEF"))
        ws.row_dimensions[row].height = 34
        row += 1
    S.make_table(ws, hdr, row - 1, ncols, "tblCategories")
    S.set_widths(ws, [26, 6, 46, 46, 26, 26, 15])
    return ws


def sheet_themes(wb, records):
    ncols = 6
    ws, row = new_sheet(wb, "Themes", "🎨 INVENTION THEMES — territories, framed as questions",
                        "Themes cut ACROSS categories on purpose. Pick the question that itches, "
                        "then filter the catalog's Themes column.", ncols, tab="B07AA0")
    headers = S.unique_headers(["Theme", "Territory", "The question it asks", "#",
                                "Star parts", "Example inventions"])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1
    counts = Counter(t for r in records for t in (r.get("tags") or []))
    for tag, (nm, desc, q, stars, examples) in vocab.THEME.items():
        vals = [tag, f"{nm} — {desc}", q, counts.get(tag, 0), stars, examples]
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9, halign="center" if c == 4 else "left")
        ws.cell(row=row, column=1).font = S.sfont(11, bold=True, color=S.NAVY)
        ws.cell(row=row, column=1).fill = S.PatternFill("solid", fgColor="F3EAF0")
        ws.cell(row=row, column=3).font = S.sfont(10, italic=True, color="6B4E8E")
        ws.row_dimensions[row].height = 42
        row += 1
    S.make_table(ws, hdr, row - 1, ncols, "tblThemes")
    S.set_widths(ws, [15, 42, 38, 6, 40, 52])
    return ws


def sheet_modality(wb, records):
    ncols = 6
    ws, row = new_sheet(wb, "Modality Map", "🌐 MODALITY MAP — by physical principle",
                        "The cross-cut nobody publishes: which slice of physics each part uses. "
                        "Two sensors sharing a modality usually share failure modes — which is "
                        "exactly why cross-modality pairs make robust systems.", ncols, tab="5E7A8A")
    headers = S.unique_headers(["Modality", "What it exploits", "#", "Categories it appears in",
                                "Typical failure mode shared by this family", "Example parts"])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1
    shared_failure = {
        "Thermal": "Anything else warm in the field of view; slow response; self-heating.",
        "Optical": "Ambient light, sunlight, dust on the lens, target colour and reflectivity.",
        "Acoustic": "Background noise, echoes, soft/angled targets, wind, temperature-dependent speed.",
        "Mechanical": "Temperature drift, creep, mounting resonance, and gravity mixed into the signal.",
        "Electrical": "Ground loops, mains hum, contact resistance, and cable capacitance.",
        "Chemical": "Cross-sensitivity to the wrong gas, humidity, drift, and finite cell life.",
        "Magnetic": "Nearby motors, speakers, steel structure and DC currents warping the field.",
        "RF": "Multipath, interference, absorption by water and bodies, regulatory limits.",
        "Nuclear": "Counting statistics — short samples are noisy; background varies with altitude.",
        "Biological": "Motion artefacts, electrode contact quality, and huge person-to-person variation.",
    }
    by_mod = defaultdict(list)
    for r in records:
        if r.get("modality"):
            by_mod[r["modality"]].append(r)
    for mod, desc in schema.MODALITY.items():
        items = by_mod.get(mod, [])
        cats = sorted({r["cat"] for r in items})
        vals = [mod, desc, len(items), " · ".join(cats[:9]),
                shared_failure.get(mod, ""),
                " · ".join(r["n"] for r in sorted(items, key=lambda r: r.get("usd") or 0)[:8])]
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9, halign="center" if c == 3 else "left")
        ws.cell(row=row, column=1).font = S.sfont(11, bold=True)
        ws.cell(row=row, column=1).fill = S.PatternFill(
            "solid", fgColor=schema.MODALITY_COLOR.get(mod, "EFEFEF"))
        ws.row_dimensions[row].height = 40
        row += 1
    S.make_table(ws, hdr, row - 1, ncols, "tblModality")
    S.set_widths(ws, [14, 40, 6, 44, 50, 48])
    return ws


# ============================================================ creative sheets

def sheet_fusion(wb):
    ncols = 5
    ws, row = new_sheet(
        wb, "Fusion Grammar", "🔀 FUSION GRAMMAR — eight ways to combine sensors",
        "Named, generative patterns. These replace 'here is a big matrix, good luck': each one "
        "is a move you can apply to any pair of parts in the catalog.", ncols, tab="C25E42")
    headers = S.unique_headers(["Pattern", "What it does", "Why it works", "Worked example", "Try it on"])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1
    try_it = {
        "complementary": "Any fast-but-twitchy sensor + any slow-but-certain one.",
        "cross-validation": "Any alarm you don't trust yet. Two modalities, both must agree.",
        "compensation": "Every gas, PM and ultrasonic sensor you own. Add RH/temperature.",
        "context-gating": "Any automation that has ever fired at the wrong moment.",
        "differential": "Any boundary: window, filter, wall, heat exchanger, inlet vs outlet.",
        "triangulation": "Any 'where' or 'which direction' question. Buy the sensor twice.",
        "temporal": "Literally every sensor here. Log it, baseline it, alarm on the deviation.",
        "fleet": "Any measurement where the spatial pattern is the interesting part.",
    }
    for key, (name, does, why, example) in vocab.FUSION.items():
        vals = [name, does, why, example, try_it.get(key, "")]
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9)
        ws.cell(row=row, column=1).font = S.sfont(11, bold=True, color=S.NAVY)
        ws.cell(row=row, column=1).fill = S.PatternFill("solid", fgColor=S.ACCENT_SOFT)
        ws.row_dimensions[row].height = 62
        row += 1
    S.make_table(ws, hdr, row - 1, ncols, "tblFusion")
    S.set_widths(ws, [18, 42, 44, 66, 40])
    return ws


def sheet_synergy(wb):
    import meta
    groups = list(meta.SYNERGY_GROUPS)
    n = len(groups)
    ncols = max(n + 1, NAV_COLS)
    ws, row = new_sheet(
        wb, "Synergy Matrix", "🕸 SYNERGY MATRIX — where sensing worlds collide",
        "★ = how fertile the crossing is. The richest inventions cross three or more. "
        "Every cell's concrete combo is listed below the grid.", ncols, tab="C75B39")
    r0 = row
    S.cell(ws, r0, 1, "crosses ↓ →", size=8, bold=True, color="FFFFFF", fill=S.NAVY,
           halign="center")
    for j, g in enumerate(groups):
        c = S.cell(ws, r0, 2 + j, g, size=8, bold=True, color="FFFFFF", fill=S.NAVY,
                   halign="center", valign="center")
        c.alignment = S.Alignment(wrap_text=True, horizontal="center", vertical="center")
    ws.row_dimensions[r0].height = 34
    star_fill = {5: "F6C453", 4: "FAE3A0", 3: "EFEFEF", 2: "F8F8F8", 1: "FFFFFF"}
    for i, ga in enumerate(groups):
        rr = r0 + 1 + i
        S.cell(ws, rr, 1, ga, size=8, bold=True, color="FFFFFF", fill=S.NAVY, valign="center")
        for j, gb in enumerate(groups):
            c = ws.cell(row=rr, column=2 + j)
            c.border = S.BORDER
            c.alignment = S.Alignment(horizontal="center", vertical="center")
            if i == j:
                c.value = "—"
                c.fill = S.PatternFill("solid", fgColor="DDD9CE")
                continue
            info = meta.SYNERGY_CELLS.get(tuple(sorted((ga, gb))))
            rating = info[0] if info else 2
            c.value = "★" * rating
            c.font = S.sfont(8, bold=rating >= 4, color="9A6A00" if rating >= 4 else S.MUTED)
            c.fill = S.PatternFill("solid", fgColor=star_fill[rating])
        ws.row_dimensions[rr].height = 20
    S.set_widths(ws, [16] + [10] * n)
    ws.freeze_panes = ws.cell(row=r0 + 1, column=2)

    row = r0 + n + 2
    row = S.section(ws, row, "THE COMBO BEHIND EVERY CELL", ncols)
    S.table_header(ws, row, S.unique_headers(["Crossing", "★", "The combination, concretely"]
                                             + [""] * (ncols - 3)))
    row += 1
    for k in sorted(meta.SYNERGY_CELLS, key=lambda k: (-meta.SYNERGY_CELLS[k][0], k)):
        rating, ex = meta.SYNERGY_CELLS[k]
        S.cell(ws, row, 1, f"{k[0]} × {k[1]}", size=9, bold=True, fill="F5F2EB")
        c = S.cell(ws, row, 2, "★" * rating, size=9, halign="center")
        c.font = S.sfont(9, bold=True, color="9A6A00")
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=ncols)
        S.cell(ws, row, 3, ex, size=9)
        ws.row_dimensions[row].height = 24
        row += 1
    return ws


def sheet_seeds(wb, seeds, records):
    by_id = {r["id"]: r for r in records}
    ncols = 10
    ws, row = new_sheet(
        wb, "Invention Seeds", "💡 INVENTION SEEDS — buildable concepts",
        "Each is real enough to start this weekend. Where a seed lists structured part IDs its "
        "BOM is COMPUTED from the catalog, so it cannot drift from the real prices.",
        ncols, tab=S.ACCENT)
    headers = S.unique_headers(["#", "Invention", "The pitch", "Parts", "Other parts",
                                "≈BOM", "Computed", "Difficulty", "Themes", "Why it works"])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1
    for i, s in enumerate(seeds, 1):
        ids = s.get("sensor_ids") or []
        computed = sum(by_id[x].get("usd") or 0 for x in ids if x in by_id)
        parts_txt = " · ".join(by_id[x]["n"] for x in ids if x in by_id) or s.get("sensors", "")
        vals = [i, s["name"], s["pitch"], parts_txt, s.get("parts", ""),
                f"${s.get('bom','?')}",
                f"${computed:.0f}" if ids else "—",
                s.get("diff"), s.get("themes", ""), s.get("why", "")]
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9,
                   halign="center" if c in (1, 6, 7, 8) else "left")
        ws.cell(row=row, column=2).font = S.sfont(10, bold=True)
        ws.cell(row=row, column=2).fill = S.PatternFill("solid", fgColor="FDF6EC")
        ws.row_dimensions[row].height = 54
        row += 1
    S.make_table(ws, hdr, row - 1, ncols, "tblSeeds")
    S.difficulty_icons(ws, 8, hdr + 1, row - 1)
    S.set_widths(ws, [4, 24, 52, 34, 24, 9, 10, 9, 20, 44])
    ws.freeze_panes = ws.cell(row=hdr + 1, column=3)
    return ws


# ============================================================ build-reality sheets

def sheet_wiring(wb, records):
    ncols = 6
    ws, row = new_sheet(
        wb, "I2C & Wiring", "🔌 I²C ADDRESS MAP & WIRING REALITY",
        "The sheet that stops projects dying. Two parts at the same address cannot share a bus "
        "without a multiplexer or an address jumper — and some families have no jumper at all.",
        ncols, tab="4A5878")
    import re
    by_addr = defaultdict(list)
    for r in records:
        for a in re.findall(r"0x[0-9A-Fa-f]{2}", str(r.get("i2c_addr") or "")):
            by_addr[a.upper().replace("0X", "0x")].append(r)

    row = S.section(ws, row, "ADDRESS MAP — collisions highlighted", ncols,
                    "Anything with two or more parts is a potential conflict. The fix is a "
                    "TCA9548A multiplexer, an address jumper, or XSHUT sequencing.")
    headers = S.unique_headers(["Address", "# parts", "Conflict?", "Parts sharing it",
                                "Can the address be changed?", "Fix"])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1
    for addr in sorted(by_addr):
        parts = by_addr[addr]
        conflict = len(parts) > 1
        changeable = [p for p in parts if "jumper" in str(p.get("i2c_addr", "")).lower()
                      or "/" in str(p.get("i2c_addr", ""))]
        vals = [addr, len(parts), "⚠ YES" if conflict else "—",
                " · ".join(p["n"] for p in parts),
                f"{len(changeable)} of {len(parts)} have a selectable address" if conflict else "n/a",
                ("Use a TCA9548A I²C multiplexer, or set jumpers so each part gets a distinct "
                 "address. Parts with a FIXED address must go behind the mux."
                 if conflict else "")]
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9, halign="center" if c in (1, 2, 3) else "left")
        ws.cell(row=row, column=1).font = S.sfont(10, bold=True, name=S.MONO)
        if conflict:
            ws.cell(row=row, column=3).font = S.sfont(9, bold=True, color=S.BAD)
            ws.cell(row=row, column=3).fill = S.PatternFill("solid", fgColor="FBE3DE")
        ws.row_dimensions[row].height = 30
        row += 1
    if by_addr:
        S.make_table(ws, hdr, row - 1, ncols, "tblI2C")
    S.set_widths(ws, [12, 9, 11, 62, 34, 52])

    row += 1
    row = S.section(ws, row, "BUS AND PIN REALITY", ncols)
    facts = [
        ("The ToF trap", "The entire ST VL53 family ships at a FIXED 0x29. Two on one bus is "
         "impossible without either a multiplexer, or driving each sensor's XSHUT pin low and "
         "assigning addresses one at a time at boot. Any project using several ToF sensors must "
         "budget for this — it is the single most common reason a multi-ToF build never works."),
        ("BME280 / BMP280 clones", "Address is 0x76 or 0x77 depending on the board, and many "
         "boards sold as BME280 carry a BMP280 with no humidity sensor. Scan the bus first, then "
         "read the chip ID register before trusting the label."),
        ("0x68 is crowded", "MPU-6050, MPU-9250, ICM-20948 and the DS3231 RTC all default here. "
         "Most IMUs have an AD0 pin that moves them to 0x69; the RTC usually does not move."),
        ("Pull-ups add up", "Every breakout carries its own 4.7k pull-ups. Six boards in parallel "
         "gives ~780Ω, which is too strong — the bus stops working reliably. Remove pull-ups on "
         "all but one or two boards on a long chain."),
        ("Bus length", "I²C is designed for a few tens of centimetres. Past ~1m, drop to 100kHz, "
         "use twisted pair with ground, or switch to a differential extender (P82B715)."),
        ("Pin budget", "An ESP32 classic has ~34 GPIO but far fewer usable: strapping pins, "
         "flash pins, and input-only pins (34-39, no pull-ups) all bite. A DVP camera consumes "
         "~16 pins on its own, which is why camera projects need an S3."),
        ("ADC2 vs Wi-Fi", "On the classic ESP32, ADC2 cannot be used while Wi-Fi is active. Put "
         "every analog sensor on ADC1, or accept that readings stop when the radio comes up."),
        ("The ESP32 ADC is poor", "Non-linear, noisy, and not to be trusted for anything "
         "precise. Any analog sensor you care about deserves an ADS1115 (16-bit, I²C, ~$3). "
         "This single part upgrades a third of this catalog."),
        ("5V outputs", "Plenty of sealed industrial and automotive parts output at their supply "
         "rail. Check the `logic_3v3` column before wiring anything with a supply above 3.6V "
         "directly to a GPIO."),
    ]
    for title, text in facts:
        S.cell(ws, row, 1, title, size=9, bold=True, fill="F5F2EB")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9)
        ws.row_dimensions[row].height = max(26, 12 + len(text) // 3.4)
        row += 1
    return ws


def sheet_power(wb, records):
    """Live-formula battery calculator. Real formulas, not a static table."""
    ncols = 8
    ws, row = new_sheet(
        wb, "Power Budget", "🔋 POWER & BATTERY CALCULATOR",
        "Change the yellow cells and everything recalculates. This is why power is stored as a "
        "number (µA) rather than as prose — v5 had 165 different free-text power strings and "
        "could not do this at all.", ncols, tab="6E7F5E")
    row = S.section(ws, row, "1 · YOUR NODE", ncols, "Edit the yellow cells.")
    inputs = [
        ("Battery capacity", 2000, "mAh", "18650 ≈ 2500-3400 · AA alkaline ≈ 2500 · LiPo 503035 ≈ 500 · CR2032 ≈ 220"),
        ("Readings per hour", 6, "per hour", "How often the node wakes and measures"),
        ("Awake time per reading", 3.0, "seconds", "Boot + sensor warm-up + measure + transmit"),
        ("Awake current", 90.0, "mA", "ESP32 with Wi-Fi active ≈ 80-160 · ESP-NOW burst ≈ 90 · BLE ≈ 30"),
        ("Deep-sleep current", 20.0, "µA", "ESP32 classic ≈ 10-20 · C3 ≈ 5 · plus your sensors' standby"),
        ("Sensor standby current", 5.0, "µA", "Sum of the sleep draw of everything left powered"),
        ("Battery derating", 0.80, "fraction", "Real capacity after cold, ageing and converter loss"),
    ]
    first_input = row
    for label, val, unit, note in inputs:
        S.cell(ws, row, 1, label, size=9, bold=True)
        c = S.cell(ws, row, 2, val, size=10, bold=True, fill="FFF3C4", halign="center")
        c.border = S.BORDER
        S.cell(ws, row, 3, unit, size=9, color=S.MUTED)
        ws.merge_cells(start_row=row, start_column=4, end_row=row, end_column=ncols)
        S.cell(ws, row, 4, note, size=9, color=S.MUTED)
        ws.row_dimensions[row].height = 17
        row += 1
    cap, per_hr, awake_s, awake_ma, sleep_ua, sens_ua, derate = (
        f"B{first_input + i}" for i in range(7))

    row += 1
    row = S.section(ws, row, "2 · RESULT", ncols)
    results = [
        ("Awake charge per reading", f"={awake_ma}*({awake_s}/3600)", "mAh",
         "current × time, converted to hours"),
        ("Awake charge per day", f"=B{row}*{per_hr}*24", "mAh/day", ""),
        ("Sleep charge per day", f"=(({sleep_ua}+{sens_ua})/1000)*24", "mAh/day",
         "standby current runs the whole 24 hours"),
        ("Total per day", f"=B{row + 1}+B{row + 2}", "mAh/day", ""),
        ("Estimated battery life", f"=IF(B{row + 3}<=0,\"—\",({cap}*{derate})/B{row + 3})", "days",
         "capacity × derating ÷ daily draw"),
        ("…in months", f"=IF(B{row + 3}<=0,\"—\",B{row + 4}/30.4)", "months", ""),
        ("Duty cycle", f"=({awake_s}*{per_hr})/3600", "fraction of time awake",
         "Below ~0.1% is where multi-year nodes live"),
    ]
    for label, formula, unit, note in results:
        S.cell(ws, row, 1, label, size=9, bold=True)
        c = S.cell(ws, row, 2, formula, size=10, bold=True, halign="center", fill="EAF0F6")
        c.number_format = "0.00"
        S.cell(ws, row, 3, unit, size=9, color=S.MUTED)
        ws.merge_cells(start_row=row, start_column=4, end_row=row, end_column=ncols)
        S.cell(ws, row, 4, note, size=9, color=S.MUTED)
        ws.row_dimensions[row].height = 17
        row += 1

    row += 1
    row = S.section(ws, row, "3 · WHAT DOMINATES YOUR BUDGET", ncols,
                    "For most battery nodes the sensor is irrelevant and the radio is everything.")
    for title, text in [
        ("The radio is the budget", "An ESP32 transmitting over Wi-Fi draws ~100-160mA. Three "
         "seconds of that is more charge than a µA-class sensor uses in a week. Optimise the "
         "radio first: ESP-NOW instead of Wi-Fi association saves seconds of connection time."),
        ("Connection time, not transmit time", "Associating with an AP and getting DHCP can take "
         "2-5 seconds. ESP-NOW sends in milliseconds with no handshake. For a sensor node that "
         "reports a number, this one change often triples battery life."),
        ("Wake on interrupt, not on a timer", "Many sensors here have an interrupt output — "
         "threshold alerts, motion wake, tap detection. Letting the SENSOR decide when the ESP32 "
         "should wake turns a duty-cycled node into an event-driven one."),
        ("Sleep current is a real number", "A 20µA deep-sleep node uses ~0.5mAh/day doing "
         "nothing. Leaving one 5mA sensor powered during sleep adds 120mAh/day — 240× more. "
         "Switch sensor power with a MOSFET or a GPIO where current allows."),
        ("Cold kills capacity", "An 18650 at -10°C may deliver half its rated capacity, and LiPo "
         "charging below 0°C damages the cell permanently. Outdoor winter nodes need derating "
         "and a charge-inhibit below freezing."),
    ]:
        S.cell(ws, row, 1, title, size=9, bold=True, fill="F5F2EB")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9)
        ws.row_dimensions[row].height = max(26, 12 + len(text) // 3.2)
        row += 1
    S.set_widths(ws, [26, 12, 14, 22, 22, 22, 22, 22])

    row += 1
    row = S.section(ws, row, "4 · THE µA-CLASS PARTS IN THIS CATALOG", ncols,
                    "Sorted by active draw — the parts that make multi-year nodes possible.")
    S.table_header(ws, row, S.unique_headers(
        ["Part", "Active µA", "Sleep µA", "Class", "Category", "$", "", ""]))
    row += 1
    lowp = [r for r in records if isinstance(r.get("pwr_ua"), (int, float)) and r["pwr_ua"] < 2000]
    for r in sorted(lowp, key=lambda r: r["pwr_ua"])[:40]:
        for c, v in enumerate([r["n"], round(r["pwr_ua"], 2), r.get("pwr_sleep_ua"),
                               r["_power_class"], r["cat"], r.get("usd")], 1):
            S.cell(ws, row, c, v, size=9, halign="center" if c in (2, 3, 6) else "left")
        ws.row_dimensions[row].height = 15
        row += 1
    return ws


def sheet_archetypes(wb):
    ncols = 7
    ws, row = new_sheet(
        wb, "Project Archetypes", "🏗 PROJECT ARCHETYPES — the shapes projects actually take",
        "Ten recurring architectures. Most builds are one of these with different sensors "
        "bolted on; knowing which one you're building tells you the failure modes in advance.",
        ncols, tab="7A6A5A")
    headers = S.unique_headers(["Archetype", "What it is", "Typical parts", "Power strategy",
                                "Comms", "Where it usually fails", "Good first build"])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1
    for a in ARCHETYPES:
        vals = [a["name"], a["what"], a["parts"], a["power"], a["comms"], a["fails"], a["first"]]
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9)
        ws.cell(row=row, column=1).font = S.sfont(10, bold=True, color=S.NAVY)
        ws.cell(row=row, column=1).fill = S.PatternFill("solid", fgColor="F0EBE3")
        ws.cell(row=row, column=6).fill = S.PatternFill("solid", fgColor="FBE9E4")
        ws.row_dimensions[row].height = 62
        row += 1
    if ARCHETYPES:
        S.make_table(ws, hdr, row - 1, ncols, "tblArchetypes")
    S.set_widths(ws, [22, 40, 40, 30, 24, 42, 30])
    return ws


# ============================================================ orient sheets

def sheet_start(wb, records, seeds):
    ncols = 8
    ws, row = new_sheet(
        wb, "START HERE", "🧭 ESP32 SENSOR UNIVERSE — v6 · The Invention Atlas",
        "The most comprehensive maker-sensor reference we could build: what exists, what it "
        "costs, where to buy it, what fools it — and, above all, what it could become.",
        ncols, tab=S.NAVY)
    S.set_widths(ws, [22, 30, 34, 26, 22, 20, 20, 20])
    n_sensors = sum(1 for r in records if r["catalog"] == "sensor")
    n_act = sum(1 for r in records if r["catalog"] == "actuator")
    n_glue = sum(1 for r in records if r["catalog"] == "glue")
    n_board = sum(1 for r in records if r["catalog"] == "board")

    row = S.section(ws, row, "THE IDEA", ncols)
    for label, text in [
        ("The problem with catalogs",
         "A sensor never measures what you actually want to know. It measures a physical PROXY. "
         "A load cell measures grams — the invention infers that a beehive is about to swarm. A "
         "barometer measures hPa — the invention infers that a door opened on the third floor. A "
         "CT clamp measures amps — the invention infers that Grandma made tea this morning, and "
         "is therefore fine."),
        ("So this document has two directions",
         "→ Forward: pick a part, see everything it could tell you (Sensor Cards). "
         "← Backward: pick something you want to KNOW, see every route to it (Inference Atlas). "
         "The backward direction is where inventions come from, and it is what most parts "
         "catalogs never give you."),
        ("Two facts make it generative",
         "ONE INFERENCE HAS MANY ROUTES — 'is someone in the room?' can be answered by PIR, "
         "mmWave, thermal array, ToF, CO2 rise, Wi-Fi CSI, floor vibration, or a 50c reed switch, "
         "and they differ in cost, privacy, power and what fools them. "
         "ONE SENSOR SERVES MANY INFERENCES — a single accelerometer yields tilt, impact, "
         "vibration spectra, step count, sleep movement, machine load, seismic events and knock "
         "signatures. Choosing the route is the design act; seeing all of them is the creative one."),
    ]:
        S.cell(ws, row, 1, label, size=9, bold=True, fill="F5F2EB")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9.5)
        ws.row_dimensions[row].height = max(30, 12 + len(text) // 4.6)
        row += 1

    row += 1
    row = S.section(ws, row, "WHAT'S IN IT", ncols)
    stats = [
        (f"{n_sensors}", "sensors"), (f"{n_act}", "actuators & outputs"),
        (f"{n_glue}", "glue & signal-chain parts"), (f"{n_board}", "boards"),
        (f"{len(vocab.CATEGORY)}", "categories"), (f"{len(vocab.PHENOMENON)}", "physical phenomena"),
        (f"{len(vocab.INFERENCE)}", "things you can infer"), (f"{len(seeds)}", "invention seeds"),
    ]
    for i, (num, label) in enumerate(stats):
        c = 1 + (i % 4) * 2
        if i % 4 == 0 and i:
            row += 1
        n = S.cell(ws, row, c, num, size=18, bold=True, color=S.ACCENT, halign="right")
        S.cell(ws, row, c + 1, label, size=9, color=S.MUTED, valign="center")
        ws.row_dimensions[row].height = 26
    row += 2

    row = S.section(ws, row, "THE SHEETS", ncols)
    guide = [
        ("Sensor Catalog", "The master table. Filter one category or theme — never read it top to bottom."),
        ("Sensor Cards", "The same parts laid out to actually READ. Click any catalog ID to jump here."),
        ("Actuators", "The other half of invention. Sense → decide → ACT. You cannot build with inputs alone."),
        ("Glue & Signal Chain", "The parts that make analog sensors work. Start with the ADS1115."),
        ("Boards & Compute", "Which ESP32, and why. C3/C6/H2 have no touch and no DAC — people get this wrong constantly."),
        ("Phenomenon Index", "“I want to MEASURE X” → every part that can, cheapest first."),
        ("Inference Atlas", "“I want to KNOW Y” → several routes, differing in cost, privacy and power. The heart of this document."),
        ("Constraint Navigator", "“I can't touch it / no power / no privacy / $5 max” → what survives."),
        ("Fusion Grammar", "Eight named ways to combine sensors. Apply any of them to any pair."),
        ("Synergy Matrix", "Which sensing worlds cross well, with the concrete combo behind every cell."),
        ("Invention Seeds", "Fully-specified projects with BOMs computed from the catalog."),
        ("I2C & Wiring", "Address collisions and pin budgets — the sheet that stops projects dying."),
        ("Power Budget", "Live formulas: parts + duty cycle → battery life."),
        ("Project Archetypes", "The ten shapes projects take, and where each one usually fails."),
        ("Provenance", "Which numbers to trust, and how they were checked."),
    ]
    for name, how in guide:
        c = S.cell(ws, row, 1, name, size=9, bold=True, fill="F5F2EB")
        S.link_to(c, name)
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, how, size=9)
        ws.row_dimensions[row].height = 19
        row += 1

    row += 1
    row = S.section(ws, row, "SEVEN MOVES THAT PRODUCE IDEAS", ncols,
                    "If you are stuck, run these in order. They work.")
    for label, text in [
        ("1 · Start from a question, not a part",
         "Open the Inference Atlas and read the questions until one itches. Working backward from "
         "'what do I want to know' beats browsing parts every time."),
        ("2 · Cross two distant categories",
         "Novelty lives at intersections. Sound × Soil = beehive acoustics. Light × Water = "
         "colorimetry. Use the Synergy Matrix as a dartboard and the Fusion Grammar as the move."),
        ("3 · Add TIME to any sensor",
         "A sensor is a number; a LOGGED sensor is a story. Weight-over-time is a depletion "
         "curve. Vibration-over-time is a bearing dying. This is the cheapest superpower here."),
        ("4 · Multiply by a fleet",
         "One node is a gadget; ten are a map. ESP-NOW makes duplication nearly free, and spatial "
         "structure is invisible from a single point."),
        ("5 · Take a constraint seriously",
         "'It must not see faces.' 'It must run three years on a coin cell.' 'I can't drill the "
         "tank.' Constraints eliminate the obvious answer and force the interesting one."),
        ("6 · Fuse two cheap parts instead of buying one expensive one",
         "PIR + mmWave = true presence. Sky-IR + humidity = a frost oracle. Two $5 sensors "
         "routinely beat one $50 sensor, because their failure modes don't overlap."),
        ("7 · Make something invisible visible",
         "The projects people remember expose a hidden layer: CO2, radon, ultrasound, RF, cosmic "
         "rays, magnetic fields. Pick an invisible thing and give it a face."),
    ]:
        S.cell(ws, row, 1, label, size=9, bold=True, fill="FDF6EC")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9)
        ws.row_dimensions[row].height = max(24, 12 + len(text) // 4.6)
        row += 1

    row += 1
    row = S.section(ws, row, "HOW TO READ A ROW", ncols)
    for label, text in [
        ("Difficulty", " · ".join(f"{k} = {v.split(' — ')[0]}" for k, v in schema.DIFFICULTY_RUBRIC.items())),
        ("Price tier", " · ".join(f"{k} {v}" for k, v in schema.PRICE_TIER_LABEL.items() if k != "?")),
        ("Contact", " · ".join(f"{k}: {v}" for k, v in schema.CONTACT.items())),
        ("Privacy", " · ".join(f"{k}: {v}" for k, v in schema.PRIVACY.items())),
        ("Hazard", "A badge here means real risk — mains, high voltage, heat, laser, UV-C, "
                   "ignition source, toxic or asphyxiant gas. Read the card before you build."),
        ("What fools it", "The most useful column in the document, and the one almost nobody "
                          "publishes. Read it before you trust a reading."),
        ("Confidence", " · ".join(f"{k}: {v}" for k, v in schema.CONFIDENCE.items())),
    ]:
        S.cell(ws, row, 1, label, size=9, bold=True, fill="F5F2EB")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9)
        ws.row_dimensions[row].height = max(22, 12 + len(text) // 4.6)
        row += 1
    return ws


def sheet_dashboard(wb, records, seeds):
    ncols = 8
    ws, row = new_sheet(wb, "Dashboard", "📊 DASHBOARD — the universe at a glance",
                        "Coverage, cost and difficulty across the catalog, plus three kits if "
                        "you'd rather just start buying.", ncols, tab="444444")
    S.set_widths(ws, [26, 8, 30, 6, 26, 8, 30, 10])
    sensors = [r for r in records if r["catalog"] == "sensor"]

    def bars(start_row, col, heading, data, note=None):
        ws.cell(row=start_row, column=col, value=heading).font = S.sfont(11, bold=True, color=S.NAVY)
        r = start_row + 1
        if note:
            S.cell(ws, r, col, note, size=8, italic=True, color=S.MUTED, border=False)
            r += 1
        mx = max(data.values()) if data else 1
        for k, v in sorted(data.items(), key=lambda kv: -kv[1]):
            S.cell(ws, r, col, str(k), size=9, wrap=False)
            S.cell(ws, r, col + 1, v, size=9, halign="center", wrap=False)
            b = S.cell(ws, r, col + 2, "█" * max(1, round(v / mx * 26)), size=9, wrap=False)
            b.font = S.sfont(9, color=S.ACCENT)
            ws.row_dimensions[r].height = 14
            r += 1
        return r

    r1 = bars(row, 1, f"BY CATEGORY  ({len(sensors)} sensors)",
              Counter(r["cat"] for r in sensors))
    r2 = bars(row, 5, "BY THEME", Counter(t for r in records for t in (r.get("tags") or [])))
    row = max(r1, r2) + 1
    r1 = bars(row, 1, "BY MODALITY", Counter(r["modality"] for r in records if r.get("modality")))
    r2 = bars(row, 5, "BY PRICE TIER",
              Counter(f"{r['_tier']}  {schema.PRICE_TIER_LABEL.get(r['_tier'],'')}" for r in records))
    row = max(r1, r2) + 1
    r1 = bars(row, 1, "BY DIFFICULTY",
              Counter(f"{r['diff']} · {schema.DIFFICULTY_RUBRIC[r['diff']].split(' — ')[0]}"
                      for r in records if r.get("diff") in schema.DIFFICULTY_RUBRIC))
    r2 = bars(row, 5, "BY CONTACT CLASS", Counter(r["contact"] for r in records if r.get("contact")))
    row = max(r1, r2) + 1
    r1 = bars(row, 1, "BY PRIVACY PROFILE", Counter(r["privacy"] for r in records if r.get("privacy")))
    r2 = bars(row, 5, "BY POWER CLASS", Counter(r["_power_class"] for r in records if r.get("_power_class")))
    row = max(r1, r2) + 2

    row = S.section(ws, row, "CURATED KITS", ncols, "If you want to stop reading and start buying.")
    kits = [
        ("🎒 $60 Explorer",
         "ESP32 devkit · BME280 · BH1750 · HC-SR04 · PIR · MPU6050 · DS18B20 · capacitive soil · "
         "MPR121 · INA219 · rotary encoder · piezo discs · ADS1115",
         "Touches ten categories and every bus. Every classic tutorial works. The complete "
         "sensing alphabet, and the ADS1115 fixes the ESP32's worst weakness on day one."),
        ("🧰 $170 Inventor",
         "Explorer + SCD41 · LD2410 mmWave · VL53L1X · SHT41 · HX711 + load cell · INMP441 · "
         "AS7341 · SGP41 · AS5600 · TCS34725 · flow sensor · leak rope · TCA9548A mux",
         "True presence, true CO2, spectral colour, weight, audio. This is the tier where the "
         "Inference Atlas opens up, because you can finally take several routes to one answer."),
        ("🔬 $450 Frontier Lab",
         "Inventor + MLX90640 thermal · SPS30 · LD2450 XY radar · BNO086 · AS3935 lightning · "
         "pH/EC kit · Geiger kit · CC1101 · BME688 ×2 · GNSS · UWB pair · Person Sensor",
         "Thermal imaging, radar tracking, isotopes, smell-prints, centimetre ranging, sub-GHz "
         "forensics. Nobody at the meetup has this bag."),
    ]
    for name, contents, why in kits:
        S.cell(ws, row, 1, name, size=10, bold=True, fill="FDF6EC", wrap=False)
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, contents, size=9)
        ws.row_dimensions[row].height = 30
        row += 1
        S.cell(ws, row, 1, "why", size=8, italic=True, color=S.MUTED, halign="right")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        c = S.cell(ws, row, 2, why, size=9, italic=True, color="555555")
        ws.row_dimensions[row].height = 26
        row += 1
    return ws


def sheet_provenance(wb, records):
    ncols = 6
    ws, row = new_sheet(
        wb, "Provenance", "📋 PROVENANCE — which numbers to trust",
        "A reference document that hides its uncertainty is worse than one that admits it. "
        "This is what we know, how we know it, and where we don't.", ncols, tab="666666")
    S.set_widths(ws, [26, 34, 34, 30, 24, 24])
    row = S.section(ws, row, "CONFIDENCE ACROSS THE CATALOG", ncols)
    counts = Counter(r.get("confidence", "High") for r in records)
    for k, desc in schema.CONFIDENCE.items():
        S.cell(ws, row, 1, k, size=10, bold=True, fill="F5F2EB")
        S.cell(ws, row, 2, counts.get(k, 0), size=10, halign="center")
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=ncols)
        S.cell(ws, row, 3, desc, size=9)
        ws.row_dimensions[row].height = 18
        row += 1

    row += 1
    row = S.section(ws, row, "POLICY", ncols)
    for label, text in [
        ("Prices are tiers, not quotes",
         "Every price is a typical hobby-breakout street price and drifts constantly. AliExpress "
         "roughly halves most of them; Adafruit and SparkFun charge more and give you "
         "documentation, libraries and support that are frequently worth the difference. Use the "
         "tier ($ / $$ / $$$ / $$$$), not the number."),
        ("Specs come from datasheets and experience, not our lab",
         "Nothing here was measured on a bench by us. Accuracy figures are manufacturer claims, "
         "which are best-case, at 25°C, after calibration. Your result will be worse."),
        ("SKUs and libraries are named only when known",
         "v5 of this document confidently cited an Adafruit product number for a breakout that "
         "does not exist, and a library to match. Both were fabrications. Everything flagged in "
         "review was re-checked; where a SKU could not be confirmed it is now described "
         "generically instead. An honest gap beats a confident invention."),
        ("What fools it is the most valuable and least verifiable column",
         "These failure modes come from datasheets, application notes and hard-won community "
         "experience. They are directionally right and specific on purpose. Treat them as "
         "'things to test for', not as guarantees."),
        ("Safety content is a starting point, never a substitute",
         "Where a part carries a hazard badge, the badge is a prompt to go and read the "
         "manufacturer's documentation. For anything life-safety — combustible gas, carbon "
         "monoxide, fire, medical — a certified device is the answer and a hobby sensor is at "
         "best a supplement to it. This document previously got this wrong; it now says so "
         "loudly and in every relevant entry."),
    ]:
        S.cell(ws, row, 1, label, size=9, bold=True, fill="F5F2EB")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9)
        ws.row_dimensions[row].height = max(28, 12 + len(text) // 4.2)
        row += 1

    row += 1
    row = S.section(ws, row, "VERSION HISTORY", ncols)
    for ver, what in [
        ("v4", "ESP32 capability map — 73 platform capabilities. Preserved on the ESP32 sheet, "
               "with its text corruption repaired."),
        ("v5", "First sensor catalog: 238 sensors × 20 fields, themes, synergy matrix, 41 seeds."),
        ("v5.1", "Correctness pass after a hostile expert review. 36 fixes: dangerous advice about "
                 "siting heated gas sensors inside LPG lockers and hydrogen-accumulating battery "
                 "rooms removed; a documented 'logic-safe' output that would destroy an ESP32 "
                 "corrected; ~18 factual errors fixed; a fabricated SKU replaced; the synergy "
                 "matrix's silent key collisions repaired."),
        ("v6", "The Invention Atlas. Schema v2 with 36 fields including what-fools-it, hazard, "
               "privacy and calibration. Four catalogs. Phenomena and inferences as controlled "
               "vocabularies, which makes the Inference Atlas, Phenomenon Index and Constraint "
               "Navigator possible. Stable IDs. A hard validator."),
    ]:
        S.cell(ws, row, 1, ver, size=10, bold=True, color=S.NAVY, fill="F5F2EB")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, what, size=9)
        ws.row_dimensions[row].height = max(22, 12 + len(what) // 4.2)
        row += 1
    return ws


def sheet_buying(wb):
    import meta
    ncols = 6
    ws, row = new_sheet(wb, "Buying Guide", "🛒 BUYING GUIDE — where the parts live",
                        "Vendor codes used throughout, plus the shopping wisdom that saves money "
                        "and weeks.", ncols, tab="5B8DB8")
    headers = S.unique_headers(["Code", "Vendor", "Site", "Region", "Why shop here", "Price level"])
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1
    for code, (name, site, region, why, lvl) in meta.VENDORS.items():
        for c, v in enumerate([code, name, site, region, why, lvl], 1):
            S.cell(ws, row, c, v, size=9, halign="center" if c in (1, 6) else "left")
        ws.cell(row=row, column=1).font = S.sfont(9, bold=True, color=S.NAVY)
        ws.cell(row=row, column=2).font = S.sfont(9, bold=True)
        ws.row_dimensions[row].height = 20
        row += 1
    S.make_table(ws, hdr, row - 1, ncols, "tblVendors")
    S.set_widths(ws, [8, 22, 26, 15, 66, 11])
    row += 1
    row = S.section(ws, row, "SHOPPING WISDOM", ncols)
    for label, text in [
        ("The two-supply-chain strategy",
         "Prototype with Adafruit/SparkFun — the documentation and libraries are the product, and "
         "they work first time. Scale with AliExpress at a fifth of the price, a three-week wait "
         "and roughly a 10% dud rate. Order cheap parts in twos and threes."),
        ("Clone awareness",
         "Boards sold as BME280 frequently carry a BMP280 with no humidity sensor. Boards sold as "
         "HMC5883L are almost always QMC5883L, which needs a different library. MPU-9250s are "
         "widely remarked. Scan the bus and read the chip ID before trusting a label."),
        ("Connector ecosystems beat jumper wires",
         "Qwiic (SparkFun) and STEMMA QT (Adafruit) are the same 4-pin JST-SH I²C plug and are "
         "cross-compatible. Grove (Seeed) and Gravity (DFRobot) are their own. Pick one and "
         "prototyping becomes LEGO instead of a bird's nest."),
        ("The ADS1115 rule",
         "The ESP32's own ADC is its weakest organ — non-linear, noisy, and unusable on ADC2 "
         "while Wi-Fi is on. Any analog sensor you care about deserves a $3 ADS1115. Buy three."),
        ("Probes and cells are consumables",
         "pH probes last roughly a year, electrochemical gas cells one to two, DO membranes need "
         "servicing, PM laser diodes have a duty-cycle life. Budget for replacement like printer "
         "ink, and prefer optical or sealed alternatives for anything you want to forget about."),
        ("Calibration is the real purchase",
         "pH buffer sachets, a conductivity standard, a known mass, an ice bath, a reference "
         "thermometer. Fifteen dollars of references turns hobby numbers into data you can act on."),
        ("Buy the dev board first for exotic parts",
         "For UWB, radar, spectral and thermal parts, the vendor board with working example "
         "firmware costs maybe $10 more and saves a weekend of bring-up. Buy the bare module "
         "only once you know the part works."),
    ]:
        S.cell(ws, row, 1, label, size=9, bold=True, fill="F5F2EB")
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=ncols)
        S.cell(ws, row, 2, text, size=9)
        ws.row_dimensions[row].height = max(26, 12 + len(text) // 3.6)
        row += 1
    return ws


def sheet_esp32(wb):
    path = HERE / "data" / "esp32_capabilities.json"
    if not path.exists():
        return None
    rows = json.loads(path.read_text())
    headers = S.unique_headers(["Domain", "Capability", "Status", "Tier", "Required hardware",
                                "Common uses", "Novel combos & invention sparks",
                                "How it actually works"])
    ncols = len(headers)
    ws, row = new_sheet(
        wb, "ESP32 Capabilities", "⚡ ESP32 PLATFORM CAPABILITIES (v4 map, preserved)",
        "What the chip itself brings: buses, radios, power modes, security. Cross these with the "
        "sensor catalog — capability × sensor is the invention grid.", ncols, tab="888888")
    S.table_header(ws, row, headers)
    hdr, row = row, row + 1
    for r in rows:
        vals = [r["Domain"], r["Capability"], r["Status"], r["Tier"], r["Required Hardware"],
                r["Common Uses"], r["Novel Combos & Invention Sparks"],
                r["How It Actually Works (Plain English)"]]
        for c, v in enumerate(vals, 1):
            S.cell(ws, row, c, v, size=9, halign="center" if c in (3, 4) else "left")
        ws.cell(row=row, column=2).font = S.sfont(9, bold=True)
        ws.cell(row=row, column=3).fill = S.PatternFill(
            "solid", fgColor="E3F0E7" if r["Status"] == "Covered" else "FBE3DE")
        ws.row_dimensions[row].height = 62
        row += 1
    S.make_table(ws, hdr, row - 1, ncols, "tblESP32")
    S.set_widths(ws, [16, 22, 10, 10, 24, 42, 52, 52])
    ws.freeze_panes = ws.cell(row=hdr + 1, column=3)
    return ws


# ============================================================ main

def main(out_path):
    records, seeds = load_all()
    wb = Workbook()
    wb.remove(wb.active)

    sheet_start(wb, records, seeds)
    sheet_dashboard(wb, records, seeds)
    sheet_catalog(wb, records, "sensor", "Sensor Catalog",
                  "🌐 SENSOR CATALOG — everything that measures the world",
                  "Scannable by design. Click an ID for the full card. Filter by category, "
                  "modality, contact class, privacy, hazard, price or difficulty.", S.ACCENT)
    sheet_cards(wb, records)
    sheet_catalog(wb, records, "actuator", "Actuators",
                  "⚙ ACTUATORS & OUTPUTS — everything that changes the world",
                  "You cannot invent with inputs alone. Sense → decide → ACT.", "8C3B2E")
    sheet_catalog(wb, records, "glue", "Glue & Signal Chain",
                  "🔧 GLUE & SIGNAL CHAIN — the parts that make the others work",
                  "ADCs, amplifiers, multiplexers, isolators, power. Unglamorous and decisive.",
                  "4A5878")
    sheet_catalog(wb, records, "board", "Boards & Compute",
                  "🧠 BOARDS & COMPUTE — which ESP32, and why",
                  "The variants differ more than people expect: C3/C6/H2 have no touch peripheral "
                  "and no DAC, and only S2/S3/P4 realistically drive cameras.", "2F5D50")
    sheet_phenomenon(wb, records)
    sheet_inference(wb, records)
    sheet_constraints(wb, records)
    sheet_categories(wb, records)
    sheet_themes(wb, records)
    sheet_modality(wb, records)
    sheet_fusion(wb)
    sheet_synergy(wb)
    sheet_seeds(wb, seeds, records)
    sheet_wiring(wb, records)
    sheet_power(wb, records)
    sheet_archetypes(wb)
    sheet_buying(wb)
    sheet_esp32(wb)
    sheet_provenance(wb, records)

    # tab order to match the nav bar
    order = [n for n, _ in SHEETS if n in wb.sheetnames]
    wb._sheets = [wb[n] for n in order] + [ws for ws in wb._sheets if ws.title not in order]

    wb.save(out_path)
    n = Counter(r["catalog"] for r in records)
    print(f"Wrote {out_path}")
    print(f"  {len(wb.sheetnames)} sheets · {n['sensor']} sensors · {n['actuator']} actuators · "
          f"{n['glue']} glue · {n['board']} boards · {len(seeds)} seeds")
    print(f"  {len(vocab.PHENOMENON)} phenomena · {len(vocab.INFERENCE)} inferences · "
          f"{len(vocab.CATEGORY)} categories")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(HERE / "esp32_sensor_universe_v6.xlsx"))
