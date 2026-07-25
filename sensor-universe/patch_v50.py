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
import sheet_lib as S  # noqa: E402
from loader import load_all  # noqa: E402

SRC = "/root/.claude/uploads/f55cc0f7-8744-54de-a2e0-8ff2f0fa91bf/86aced1a-esp32_sensor_universe_v50.xlsx"
OUT = HERE / "esp32_sensor_universe_v52.xlsx"

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


def main():
    records, _ = load_all(persist_ids=False)
    mine = {r["n"]: r for r in records if r.get("catalog") == "sensor"}

    wb = load_workbook(SRC)
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
            if str(old) != str(new):
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

    # openpyxl drops cached formula results on round-trip; v50 has 10 formula
    # cells on Idea Forge. Forcing a full recalculation on open means Excel
    # repopulates them immediately and the user never sees a blank.
    wb.calculation.fullCalcOnLoad = True
    wb.save(OUT)
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
    row = ws.max_row + 1
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


def add_corrections_log(wb, changes, added=0):
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
