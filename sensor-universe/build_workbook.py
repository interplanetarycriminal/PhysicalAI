#!/usr/bin/env python3
"""Build the ESP32 Sensor Universe workbook (v5) from the data/ modules.

Usage: python3 build_workbook.py [output.xlsx]
"""
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))

from meta import VENDORS, THEMES, CATEGORY_GUIDE, SYNERGY_GROUPS, SYNERGY_CELLS  # noqa: E402
from seeds import SEEDS  # noqa: E402

DATA_PARTS = [
    "part1_temp_humidity_pressure", "part2_air_gas", "part3_light_distance",
    "part4_presence_motion_magnetic", "part5_sound_force_touch",
    "part6_bio_weather_soil", "part7_water_power_position",
    "part8_gps_thermal_camera_rf", "part9_classics_and_gaps",
    "part10_industrial_exotic",
]

# ---------------------------------------------------------------- palette
NAVY = "1F2A44"
INK = "2D2D2D"
WHITE = "FFFFFF"
ACCENT = "E8A33D"
LIGHT = "F5F2EB"

CAT_COLORS = [
    "FDEBD0", "D6EAF8", "D5F5E3", "FADBD8", "E8DAEF", "FCF3CF", "D1F2EB",
    "F6DDCC", "D4E6F1", "D0ECE7", "F9E79F", "EBDEF0", "D5DBDB", "FAE5D3",
    "D6DBDF", "E8F8F5", "FDF2E9", "EAF2F8", "E9F7EF", "FDEDEC", "F4ECF7",
    "FEF9E7", "E8F6F3", "F8F9F9", "FEF5E7", "EBF5FB", "EAFAF1", "F9EBEA",
    "F5EEF8", "FCFBE3", "E0F2F1", "FBEEE6",
]

TIER_FILLS = {"$": "D5F5E3", "$$": "FCF3CF", "$$$": "FAD7A0", "$$$$": "F5B7B1"}
DIFF_LABEL = {1: "1 · plug & play", 2: "2 · easy", 3: "3 · some skill",
              4: "4 · advanced", 5: "5 · expert"}

thin = Side(style="thin", color="C9C4B8")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def price_tier(usd):
    if usd is None:
        return "$"
    if usd < 5:
        return "$"
    if usd < 15:
        return "$$"
    if usd < 50:
        return "$$$"
    return "$$$$"


def load_sensors():
    sensors = []
    for mod_name in DATA_PARTS:
        mod = __import__(mod_name)
        sensors.extend(mod.SENSORS)
    # validate + order by category guide order
    cat_order = {c: i for i, c in enumerate(CATEGORY_GUIDE)}
    problems = []
    for s in sensors:
        if s["cat"] not in cat_order:
            problems.append(f"unknown category: {s['cat']} ({s['n']})")
        for t in [x.strip() for x in s["tags"].split(",")]:
            if t not in THEMES:
                problems.append(f"unknown theme tag '{t}' on {s['n']}")
        for vcode in [x.strip() for x in s["buy"].split(",")]:
            if vcode and vcode != "—" and vcode not in VENDORS:
                problems.append(f"unknown vendor '{vcode}' on {s['n']}")
    if problems:
        raise SystemExit("DATA ERRORS:\n" + "\n".join(problems))
    sensors.sort(key=lambda s: (cat_order[s["cat"]], s["sub"], s["n"]))
    for i, s in enumerate(sensors, 1):
        s["id"] = f"S{i:03d}"
    return sensors


def expand_vendors(codes):
    out = []
    for c in [x.strip() for x in codes.split(",")]:
        if c in VENDORS:
            out.append(VENDORS[c][0])
        elif c:
            out.append(c)
    return " · ".join(out)


# ---------------------------------------------------------------- style utils

def header_row(ws, row, headers, fill=NAVY, font_color=WHITE, size=10):
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=row, column=col, value=h)
        c.font = Font(bold=True, color=font_color, size=size)
        c.fill = PatternFill("solid", fgColor=fill)
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        c.border = BORDER


def title_block(ws, title, subtitle, ncols):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    t = ws.cell(row=1, column=1, value=title)
    t.font = Font(bold=True, size=18, color=WHITE)
    t.fill = PatternFill("solid", fgColor=NAVY)
    t.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    ws.row_dimensions[1].height = 34
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
    s = ws.cell(row=2, column=1, value=subtitle)
    s.font = Font(size=10, italic=True, color="6B6B6B")
    s.alignment = Alignment(vertical="center", horizontal="left", indent=1, wrap_text=True)
    ws.row_dimensions[2].height = 26
    for col in range(1, ncols + 1):
        ws.cell(row=1, column=col).fill = PatternFill("solid", fgColor=NAVY)


def body_cell(c, wrap=True, size=10, bold=False, fill=None, align="left", valign="top"):
    c.font = Font(size=size, bold=bold)
    c.alignment = Alignment(wrap_text=wrap, vertical=valign, horizontal=align)
    c.border = BORDER
    if fill:
        c.fill = PatternFill("solid", fgColor=fill)


# ---------------------------------------------------------------- sheets

def sheet_catalog(wb, sensors, cat_color):
    ws = wb.create_sheet("Sensor Catalog")
    ws.sheet_properties.tabColor = ACCENT
    headers = ["ID", "Sensor", "Category", "Subcategory", "What It Measures",
               "How It Works (Plain English)", "Interface", "Voltage", "≈Price USD",
               "Tier", "Difficulty", "Power Draw", "Key Specs & Gotchas",
               "Where To Buy", "Boards / Modules", "Library / Driver",
               "Common Uses", "Invention Sparks", "Pairs Well With", "Themes"]
    title_block(ws, "🌐 SENSOR CATALOG — every sensor, what it does, what it could become",
                f"{len(sensors)} sensors × 20 fields. Filter by Category/Theme/Tier/Difficulty. "
                "Prices are typical breakout street prices (vary by vendor & region).", len(headers))
    header_row(ws, 3, headers)
    ws.freeze_panes = "C4"
    r = 4
    for s in sensors:
        fill = cat_color[s["cat"]]
        vals = [s["id"], s["n"], s["cat"], s["sub"], s["meas"], s["how"], s["iface"],
                s["v"], s["usd"] if s["usd"] else "free", price_tier(s["usd"]),
                DIFF_LABEL[s["diff"]], s["pwr"], s["spec"], expand_vendors(s["buy"]),
                s["brd"], s["lib"], s["use"], s["spark"], s["pair"], s["tags"]]
        for col, v in enumerate(vals, 1):
            c = ws.cell(row=r, column=col, value=v)
            body_cell(c, size=9)
        ws.cell(row=r, column=1).font = Font(size=9, bold=True, color="8A8378")
        ws.cell(row=r, column=2).font = Font(size=10, bold=True)
        for col in (1, 2, 3):
            ws.cell(row=r, column=col).fill = PatternFill("solid", fgColor=fill)
        tier_c = ws.cell(row=r, column=10)
        tier_c.fill = PatternFill("solid", fgColor=TIER_FILLS[price_tier(s["usd"])])
        tier_c.alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=r, column=9).alignment = Alignment(horizontal="center", vertical="top")
        ws.row_dimensions[r].height = 86
        r += 1
    widths = [6, 20, 15, 14, 26, 44, 12, 10, 8, 6, 11, 12, 28, 24, 20, 20, 38, 46, 26, 18]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.auto_filter.ref = f"A3:T{r-1}"
    return ws


def sheet_start(wb, sensors):
    ws = wb.create_sheet("START HERE", 0)
    ws.sheet_properties.tabColor = NAVY
    ncols = 6
    title_block(ws, "🧭 ESP32 SENSOR UNIVERSE — v5",
                "The most comprehensive maker-sensor atlas we could build: what exists, what it costs, "
                "where to buy it, and — most importantly — what it could become.", ncols)
    widths = [22, 30, 46, 30, 26, 22]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    r = 4
    n_cats = len({s['cat'] for s in sensors})
    facts = [
        ("WHAT THIS IS", f"{len(sensors)} sensors across {n_cats} categories, each with plain-English physics, "
         "real prices, vendors, libraries, common uses and invention sparks — plus the original 73 ESP32 "
         "platform capabilities (v4) preserved and cleaned on their own sheet."),
        ("LINEAGE", "v4 mapped what the ESP32 chip can do. v5 maps what the WORLD around it can sense. "
         "Capabilities × Sensors is where inventions live."),
    ]
    for label, text in facts:
        c = ws.cell(row=r, column=1, value=label)
        body_cell(c, bold=True, fill=LIGHT)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=ncols)
        c2 = ws.cell(row=r, column=2, value=text)
        body_cell(c2)
        ws.row_dimensions[r].height = 42
        r += 1

    r += 1
    ws.cell(row=r, column=1, value="THE SHEETS").font = Font(bold=True, size=13, color=NAVY)
    r += 1
    sheet_guide = [
        ("Sensor Catalog", "The master table. Start by filtering one Category or one Theme — never read it top to bottom."),
        ("Categories", "The 30+ sensor families: what each does and when to reach for it."),
        ("Themes", "16 invention territories (Body & Health, Invisible Worlds…) — each is a question, not a parts list."),
        ("Synergy Matrix", "Which sensing worlds combine explosively. Cross two high-star groups and steal the example."),
        ("Invention Seeds", "40 fully-specified project concepts with sensors, BOM cost, difficulty and who'd care."),
        ("Buying Guide", "Vendor directory with regions and honest notes, plus how to shop without getting burned."),
        ("ESP32 Capabilities", "The platform map (v4): buses, radios, power modes — what the chip itself brings."),
        ("Dashboard", "Counts, price tiers, difficulty spread, theme coverage, and three curated starter kits."),
    ]
    header_row(ws, r, ["Sheet", "How to use it", "", "", "", ""], fill="4A5878")
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=ncols)
    r += 1
    for name, how in sheet_guide:
        c = ws.cell(row=r, column=1, value=name)
        body_cell(c, bold=True, fill=LIGHT)
        c.hyperlink = f"#'{name}'!A1"
        c.font = Font(bold=True, color="1F4E79", underline="single")
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=ncols)
        c2 = ws.cell(row=r, column=2, value=how)
        body_cell(c2)
        ws.row_dimensions[r].height = 24
        r += 1

    r += 1
    ws.cell(row=r, column=1, value="HOW TO BE CREATIVE WITH THIS").font = Font(bold=True, size=13, color=NAVY)
    r += 1
    moves = [
        ("1 · Start from a theme question", "Each Theme sheet row is a question ('What is my body saying that I can't hear?'). Pick the one that itches."),
        ("2 · Cross two distant categories", "Novelty lives at intersections: Sound × Soil = beehive acoustics. Use the Synergy Matrix as a dartboard."),
        ("3 · Mine the Sparks column", "Every sensor carries one worked invention spark. Read ten sparks from a random category and your brain will make an eleventh."),
        ("4 · Add TIME to any sensor", "A sensor is a number; a LOGGED sensor is a story. Trends, baselines and anomalies turn $2 parts into new instruments (weight→depletion, vibration→bearing health)."),
        ("5 · Think in fleets", "One node is a gadget; ten are a map. ESP-NOW + $2 sensors makes spatial sensing (room-by-room, street-by-street) cheap."),
        ("6 · Fuse cheap pairs instead of buying exotic", "PIR + mmWave = true presence. Sky-IR + RH = frost oracle. Two $5 sensors often beat one $50 sensor."),
        ("7 · Make the invisible visible", "The most magnetic projects expose a hidden layer: CO2, radon, cosmic rays, ultrasound, RF. Pick an invisible thing and give it a face."),
    ]
    for label, text in moves:
        c = ws.cell(row=r, column=1, value=label)
        body_cell(c, bold=True, fill="FDF6EC")
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=ncols)
        body_cell(ws.cell(row=r, column=2, value=text))
        ws.row_dimensions[r].height = 32
        r += 1

    r += 1
    ws.cell(row=r, column=1, value="FIELD LEGEND").font = Font(bold=True, size=13, color=NAVY)
    r += 1
    legend = [
        ("≈Price USD / Tier", "Typical hobby-breakout street price. $ <5 · $$ 5-15 · $$$ 15-50 · $$$$ 50+. AliExpress halves most prices; Adafruit/SparkFun buy you docs and support."),
        ("Difficulty", "1 plug & play (Qwiic/STEMMA) · 2 easy library · 3 wiring/calibration thought · 4 analog frontends or protocols · 5 research-grade adventure."),
        ("Interface", "I2C = shareable 2-wire bus (most beginner-friendly) · SPI = fast 4-wire · Analog = needs ADC (use ADS1115!) · UART = serial · 1-Wire = many sensors, one pin."),
        ("Invention Sparks", "Deliberately specific ideas — steal them whole, or use them as proof of the pattern 'this sensor + that twist = new thing'."),
        ("Themes", "Tags linking into the 16 invention territories on the Themes sheet."),
    ]
    for label, text in legend:
        c = ws.cell(row=r, column=1, value=label)
        body_cell(c, bold=True, fill=LIGHT)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=ncols)
        body_cell(ws.cell(row=r, column=2, value=text))
        ws.row_dimensions[r].height = 36
        r += 1
    return ws


def sheet_categories(wb, sensors, cat_color):
    ws = wb.create_sheet("Categories")
    ws.sheet_properties.tabColor = "7A9E7E"
    headers = ["Category", "Sensors", "What this family does", "Reach for it when…",
               "Cheapest entry", "Deepest cut"]
    title_block(ws, "🗂 CATEGORY GUIDE — the sensor families",
                "Every family in the catalog: counts, purpose, entry points. Click a category, then filter the Catalog.",
                len(headers))
    header_row(ws, 3, headers)
    ws.freeze_panes = "A4"
    by_cat = {}
    for s in sensors:
        by_cat.setdefault(s["cat"], []).append(s)
    r = 4
    for cat, (emoji, what, when) in CATEGORY_GUIDE.items():
        items = by_cat.get(cat, [])
        if not items:
            continue
        priced = [s for s in items if s["usd"]]
        cheap = min(priced, key=lambda s: s["usd"]) if priced else items[0]
        deep = max(items, key=lambda s: (s["diff"], s["usd"] or 0))
        vals = [f"{emoji} {cat}", len(items), what, when,
                f"{cheap['n']} (${cheap['usd']:g})" if priced else f"{cheap['n']} (free)",
                f"{deep['n']} (lvl {deep['diff']})"]
        for col, v in enumerate(vals, 1):
            body_cell(ws.cell(row=r, column=col, value=v), size=10)
        ws.cell(row=r, column=1).font = Font(bold=True, size=10)
        ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=cat_color[cat])
        ws.cell(row=r, column=2).alignment = Alignment(horizontal="center", vertical="top")
        ws.row_dimensions[r].height = 42
        r += 1
    for i, w in enumerate([26, 8, 50, 50, 30, 28], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.auto_filter.ref = f"A3:F{r-1}"
    return ws


def sheet_themes(wb, sensors):
    ws = wb.create_sheet("Themes")
    ws.sheet_properties.tabColor = "B86FA2"
    headers = ["Theme", "Territory", "The question it asks", "Sensors tagged",
               "Star sensors", "Example inventions"]
    title_block(ws, "🎨 INVENTION THEMES — 16 territories to explore",
                "Themes are creative lenses, not categories. Pick a question that itches, "
                "then filter the Catalog's Themes column by the tag.", len(headers))
    header_row(ws, 3, headers)
    ws.freeze_panes = "A4"
    counts = {t: 0 for t in THEMES}
    for s in sensors:
        for t in [x.strip() for x in s["tags"].split(",")]:
            counts[t] += 1
    r = 4
    for tag, (name, desc, question, stars, examples) in THEMES.items():
        vals = [tag, f"{name} — {desc}", question, counts[tag], stars, examples]
        for col, v in enumerate(vals, 1):
            body_cell(ws.cell(row=r, column=col, value=v), size=10)
        ws.cell(row=r, column=1).font = Font(bold=True, size=11, color=NAVY)
        ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=LIGHT)
        ws.cell(row=r, column=3).font = Font(italic=True, size=10, color="6B4E8E")
        ws.cell(row=r, column=4).alignment = Alignment(horizontal="center", vertical="top")
        ws.row_dimensions[r].height = 46
        r += 1
    for i, w in enumerate([15, 44, 36, 9, 38, 52], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.auto_filter.ref = f"A3:F{r-1}"
    return ws


def sheet_synergy(wb):
    ws = wb.create_sheet("Synergy Matrix")
    ws.sheet_properties.tabColor = "C75B39"
    groups = list(SYNERGY_GROUPS)
    n = len(groups)
    title_block(ws, "🔀 SYNERGY MATRIX — where sensing worlds collide",
                "★ ratings: how fertile the crossing is. The richest inventions cross 3+ groups. "
                "Below the grid: the example combo behind every 4-5★ cell.", n + 1)

    def lookup(a, b):
        return SYNERGY_CELLS.get((a, b)) or SYNERGY_CELLS.get((b, a))

    r0 = 4
    ws.cell(row=r0, column=1, value="crosses ↓ →").font = Font(bold=True, size=9, color="888888")
    for j, g in enumerate(groups):
        c = ws.cell(row=r0, column=2 + j, value=g)
        c.font = Font(bold=True, size=9, color=WHITE)
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[r0].height = 30
    star_fill = {5: "F9C74F", 4: "F8E16C", 3: "EFEFEF", 2: "FAFAFA", 1: "FFFFFF"}
    for i, ga in enumerate(groups):
        row = r0 + 1 + i
        c = ws.cell(row=row, column=1, value=ga)
        c.font = Font(bold=True, size=9, color=WHITE)
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(vertical="center")
        c.border = BORDER
        for j, gb in enumerate(groups):
            cell = ws.cell(row=row, column=2 + j)
            cell.border = BORDER
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if i == j:
                cell.value = "—"
                cell.fill = PatternFill("solid", fgColor="DDD9CE")
                continue
            info = lookup(ga, gb)
            rating = info[0] if info else 2
            cell.value = "★" * rating
            cell.font = Font(size=9, color="9A6A00" if rating >= 4 else "777777",
                             bold=rating >= 4)
            cell.fill = PatternFill("solid", fgColor=star_fill[rating])
        ws.row_dimensions[row].height = 22
    ws.column_dimensions["A"].width = 16
    for j in range(n):
        ws.column_dimensions[get_column_letter(2 + j)].width = 11
    ws.freeze_panes = "B5"

    r = r0 + n + 2
    ws.cell(row=r, column=1, value="THE COMBOS BEHIND THE STARS (4★ and 5★ crossings)").font = \
        Font(bold=True, size=12, color=NAVY)
    r += 1
    header_row(ws, r, ["Crossing", "★", "Example combo / why it works"] + [""] * (n - 2), fill="4A5878")
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=n + 1)
    r += 1
    seen = set()
    rows = []
    for (a, b), (rating, example) in SYNERGY_CELLS.items():
        key = tuple(sorted((a, b)))
        if key in seen or rating < 4 or example.startswith("Same as") or example.startswith("Duplicate"):
            continue
        seen.add(key)
        rows.append((rating, f"{a} × {b}", example))
    rows.sort(key=lambda x: (-x[0], x[1]))
    for rating, crossing, example in rows:
        body_cell(ws.cell(row=r, column=1, value=crossing), bold=True, fill=LIGHT, size=9)
        c = ws.cell(row=r, column=2, value="★" * rating)
        body_cell(c, size=9, align="center")
        c.font = Font(size=9, color="9A6A00", bold=True)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=n + 1)
        body_cell(ws.cell(row=r, column=3, value=example), size=9)
        ws.row_dimensions[r].height = 20
        r += 1
    return ws


def sheet_seeds(wb):
    ws = wb.create_sheet("Invention Seeds")
    ws.sheet_properties.tabColor = "E8A33D"
    headers = ["#", "Invention", "The pitch", "Sensors (from Catalog)", "Other parts",
               "≈BOM", "Difficulty", "Themes", "Who cares (market)", "Why now / why it works"]
    title_block(ws, "💡 INVENTION SEEDS — 40 buildable concepts",
                "Each seed is real enough to start this weekend. Steal whole, or fork: "
                "swap one sensor, one context, or one user and it becomes yours.", len(headers))
    header_row(ws, 3, headers)
    ws.freeze_panes = "C4"
    r = 4
    for i, s in enumerate(SEEDS, 1):
        vals = [i, s["name"], s["pitch"], s["sensors"], s["parts"], f"${s['bom']}",
                DIFF_LABEL[s["diff"]], s["themes"], s["market"], s["why"]]
        for col, v in enumerate(vals, 1):
            body_cell(ws.cell(row=r, column=col, value=v), size=9)
        ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=r, column=2).font = Font(bold=True, size=10)
        ws.cell(row=r, column=2).fill = PatternFill("solid", fgColor="FDF6EC")
        ws.cell(row=r, column=6).alignment = Alignment(horizontal="center", vertical="top")
        ws.row_dimensions[r].height = 64
        r += 1
    for i, w in enumerate([4, 22, 52, 34, 26, 8, 12, 20, 30, 42], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.auto_filter.ref = f"A3:J{r-1}"
    return ws


def sheet_buying(wb):
    ws = wb.create_sheet("Buying Guide")
    ws.sheet_properties.tabColor = "5B8DB8"
    headers = ["Code", "Vendor", "Site", "Region", "Why you'd shop here", "Price level"]
    title_block(ws, "🛒 BUYING GUIDE — where the sensors live",
                "Vendor codes used throughout the Catalog, plus the shopping wisdom that saves money and weeks.",
                len(headers))
    header_row(ws, 3, headers)
    r = 4
    for code, (name, site, region, why, lvl) in VENDORS.items():
        vals = [code, name, site, region, why, lvl]
        for col, v in enumerate(vals, 1):
            body_cell(ws.cell(row=r, column=col, value=v), size=10)
        ws.cell(row=r, column=1).font = Font(bold=True, size=10, color=NAVY)
        ws.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=r, column=2).font = Font(bold=True, size=10)
        ws.row_dimensions[r].height = 22
        r += 1
    for i, w in enumerate([8, 20, 26, 14, 64, 10], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    r += 1
    ws.cell(row=r, column=1, value="SHOPPING WISDOM").font = Font(bold=True, size=13, color=NAVY)
    r += 1
    tips = [
        ("The two-supply-chain strategy", "Prototype with Adafruit/SparkFun (docs, libraries, it WORKS), then scale with AliExpress (5-10x cheaper, 3-week wait, 10% duds). Order AliExpress parts in 2s and 3s."),
        ("Clone awareness", "Cheap 'BME280' boards often carry BMP280 (no humidity); 'HMC5883L' are usually QMC5883L (different lib); MPU-9250s may be remarked. Cross-check the chip marking against the listing."),
        ("Connector ecosystems beat jumper wires", "Qwiic (SparkFun) and STEMMA QT (Adafruit) are the same I2C plug; Grove (Seeed) and Gravity (DFRobot) are their own. Standardise and prototyping becomes LEGO."),
        ("The ADS1115 rule", "The ESP32's ADC is its weakest organ. Any analog sensor you care about deserves a $3 ADS1115 (16-bit, I2C). Buy three."),
        ("Probes & consumables age", "pH probes (~1yr), electrochemical gas cells (1-2yr), DO membranes — budget replacement like printer ink. Sealed/optical alternatives often win long-term."),
        ("Calibration is the real purchase", "pH buffer sachets, a salinity standard, a known weight, an ice bath: $15 of references turn hobby numbers into trustworthy data."),
        ("Buy the dev board version first", "For exotic parts (UWB, radar, spectral), the $10-premium dev board with proven firmware saves a weekend of bring-up pain."),
    ]
    for label, text in tips:
        body_cell(ws.cell(row=r, column=1, value=label), bold=True, fill=LIGHT)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
        body_cell(ws.cell(row=r, column=2, value=text))
        ws.row_dimensions[r].height = 40
        r += 1
    return ws


def sheet_esp32(wb):
    ws = wb.create_sheet("ESP32 Capabilities")
    ws.sheet_properties.tabColor = "888888"
    rows = json.loads((HERE / "data" / "esp32_capabilities.json").read_text())
    headers = ["Domain", "Capability", "Status", "Tier", "Priority", "Required Hardware",
               "Common Uses", "Novel Combos & Invention Sparks", "How It Actually Works"]
    title_block(ws, "⚡ ESP32 PLATFORM CAPABILITIES (v4 map, preserved & cleaned)",
                "What the chip itself brings: buses, radios, power modes, security. "
                "Cross these with the Sensor Catalog — capability × sensor is the invention grid.", len(headers))
    header_row(ws, 3, headers)
    ws.freeze_panes = "C4"
    r = 4
    domains = []
    for row in rows:
        if row["Domain"] not in domains:
            domains.append(row["Domain"])
    dom_fill = {d: CAT_COLORS[i % len(CAT_COLORS)] for i, d in enumerate(domains)}
    for row in rows:
        vals = [row["Domain"], row["Capability"], row["Status"], row["Tier"], row["Priority"],
                row["Required Hardware"], row["Common Uses"],
                row["Novel Combos & Invention Sparks"],
                row["How It Actually Works (Plain English)"]]
        for col, v in enumerate(vals, 1):
            body_cell(ws.cell(row=r, column=col, value=v), size=9)
        ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=dom_fill[row["Domain"]])
        ws.cell(row=r, column=2).font = Font(bold=True, size=9)
        status = ws.cell(row=r, column=3)
        status.fill = PatternFill("solid", fgColor="D5F5E3" if row["Status"] == "Covered" else "FADBD8")
        status.alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=r, column=4).alignment = Alignment(horizontal="center", vertical="top")
        ws.cell(row=r, column=5).alignment = Alignment(horizontal="center", vertical="top")
        ws.row_dimensions[r].height = 80
        r += 1
    for i, w in enumerate([16, 22, 9, 9, 8, 24, 42, 52, 52], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.auto_filter.ref = f"A3:I{r-1}"
    return ws


def sheet_dashboard(wb, sensors):
    ws = wb.create_sheet("Dashboard")
    ws.sheet_properties.tabColor = "444444"
    ncols = 8
    title_block(ws, "📊 DASHBOARD — the universe at a glance",
                "Counts, costs and coverage — plus three curated kits if you want to just start buying.", ncols)
    for i, w in enumerate([26, 9, 34, 4, 26, 9, 34, 10], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    by_cat, by_tier, by_diff, by_theme, by_iface = {}, {}, {}, {}, {}
    for s in sensors:
        by_cat[s["cat"]] = by_cat.get(s["cat"], 0) + 1
        by_tier[price_tier(s["usd"])] = by_tier.get(price_tier(s["usd"]), 0) + 1
        by_diff[s["diff"]] = by_diff.get(s["diff"], 0) + 1
        for t in [x.strip() for x in s["tags"].split(",")]:
            by_theme[t] = by_theme.get(t, 0) + 1
        fam = s["iface"].split("/")[0].split("(")[0].strip()
        fam = {"Trigger": "Pulse/GPIO", "Pulse": "Pulse/GPIO", "Digital": "Digital GPIO",
               "Dry contact": "Digital GPIO", "2-wire serial": "Other serial",
               "1-wire proprietary": "1-Wire"}.get(fam, fam)
        by_iface[fam] = by_iface.get(fam, 0) + 1

    def bar_block(start_row, col, heading, data, max_label=None, scale=1.0):
        ws.cell(row=start_row, column=col, value=heading).font = Font(bold=True, size=12, color=NAVY)
        r = start_row + 1
        mx = max(data.values()) if data else 1
        for k, v in sorted(data.items(), key=lambda kv: -kv[1]):
            body_cell(ws.cell(row=r, column=col, value=str(k)), size=9, wrap=False)
            c = ws.cell(row=r, column=col + 1, value=v)
            body_cell(c, size=9, align="center", wrap=False)
            bar = ws.cell(row=r, column=col + 2, value="█" * max(1, round(v / mx * 28 * scale)))
            bar.font = Font(size=9, color=ACCENT)
            bar.border = BORDER
            ws.row_dimensions[r].height = 16
            r += 1
        return r

    r1 = bar_block(4, 1, f"SENSORS BY CATEGORY ({len(sensors)} total)", by_cat)
    r2 = bar_block(4, 5, "SENSORS BY THEME TAG", by_theme)
    nxt = max(r1, r2) + 1
    tier_named = {f"{t}  ({ {'$':'under $5','$$':'$5-15','$$$':'$15-50','$$$$':'$50+'}[t] })": v
                  for t, v in by_tier.items()}
    r3 = bar_block(nxt, 1, "PRICE TIERS", tier_named)
    diff_named = {DIFF_LABEL[d]: v for d, v in by_diff.items()}
    r4 = bar_block(nxt, 5, "DIFFICULTY SPREAD", diff_named)
    nxt2 = max(r3, r4) + 1
    r5 = bar_block(nxt2, 1, "INTERFACE FAMILIES", by_iface)

    r = nxt2
    ws.cell(row=r, column=5, value="CURATED KITS").font = Font(bold=True, size=12, color=NAVY)
    r += 1
    kits = [
        ("🎒 $60 Explorer", "ESP32 devkit · BME280 · BH1750 · HC-SR04 · HC-SR501 PIR · MPU6050 · DS18B20 · capacitive soil · MPR121 · INA219 · KY-040 · piezo discs",
         "Touches 10 categories. Every classic tutorial works. The complete sensing alphabet."),
        ("🧰 $170 Inventor", "Explorer + SCD41 · LD2410 mmWave · VL53L1X · SHT41 · HX711+cells · INMP441 · AS7341 · SGP40 · AS5600 · ADS1115 ×2 · TCS34725 · flow + leak rope",
         "True presence, true CO2, spectral color, weight, audio — the modern-build tier where inventions start."),
        ("🔬 $450 Frontier Lab", "Inventor + MLX90640 thermal · SPS30 · LD2450 XY radar · BNO086 · AS3935 lightning · pH/EC kit · Geiger kit · CC1101 · BME688 ×2 · GPS M10 · Person Sensor",
         "Thermal imaging, radar tracking, isotopes, smell-prints, sub-GHz forensics — nobody at the meetup has this bag."),
    ]
    for name, contents, why in kits:
        body_cell(ws.cell(row=r, column=5, value=name), bold=True, fill="FDF6EC", wrap=False)
        ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=8)
        body_cell(ws.cell(row=r, column=6, value=contents), size=9)
        ws.row_dimensions[r].height = 46
        r += 1
        ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=8)
        body_cell(ws.cell(row=r, column=5, value="why:"), size=9, wrap=False)
        ws.cell(row=r, column=5).font = Font(italic=True, size=9, color="888888")
        c = ws.cell(row=r, column=6, value=why)
        body_cell(c, size=9)
        c.font = Font(italic=True, size=9, color="555555")
        ws.row_dimensions[r].height = 26
        r += 1

    r = max(r5, r) + 1
    ws.cell(row=r, column=1, value="BEST FIRST 15 (cheap, easy, broad)").font = Font(bold=True, size=12, color=NAVY)
    r += 1
    picks = [s for s in sensors if s["usd"] and s["usd"] <= 6 and s["diff"] <= 2]
    picks.sort(key=lambda s: (s["diff"], s["usd"]))
    chosen, cats = [], set()
    for s in picks:
        if s["cat"] not in cats:
            chosen.append(s)
            cats.add(s["cat"])
        if len(chosen) == 15:
            break
    for s in chosen:
        body_cell(ws.cell(row=r, column=1, value=f"{s['n']}"), size=9, wrap=False, bold=True)
        body_cell(ws.cell(row=r, column=2, value=f"${s['usd']:g}"), size=9, align="center", wrap=False)
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=3)
        body_cell(ws.cell(row=r, column=3, value=s["cat"]), size=9, wrap=False)
        ws.row_dimensions[r].height = 16
        r += 1
    return ws


# ---------------------------------------------------------------- main

def main(out_path):
    sensors = load_sensors()
    cats = []
    for s in sensors:
        if s["cat"] not in cats:
            cats.append(s["cat"])
    cat_color = {c: CAT_COLORS[i % len(CAT_COLORS)] for i, c in enumerate(cats)}

    wb = Workbook()
    wb.remove(wb.active)
    sheet_start(wb, sensors)
    sheet_catalog(wb, sensors, cat_color)
    sheet_categories(wb, sensors, cat_color)
    sheet_themes(wb, sensors)
    sheet_synergy(wb)
    sheet_seeds(wb)
    sheet_buying(wb)
    sheet_esp32(wb)
    sheet_dashboard(wb, sensors)
    wb.save(out_path)
    print(f"Wrote {out_path}: {len(sensors)} sensors, {len(cats)} categories, "
          f"{len(SEEDS)} seeds, {len(THEMES)} themes, {len(VENDORS)} vendors")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else str(HERE / "esp32_sensor_universe_v5.xlsx")
    main(out)
