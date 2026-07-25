"""Loads every catalog, applies stable IDs, migration, enrichment and derived fields.

Load order matters:
    1. raw records from the part files (legacy v5 shape) and the new catalogs
    2. legacy category/theme names migrated to the schema-v2 vocabulary
    3. stable IDs attached from ids.json (assigned once, never renumbered)
    4. enrichment overlay merged in by ID  (the ~17 schema-v2 fields)
    5. derived fields computed  (tier, power class — never authored)
"""
import json
import re
from pathlib import Path

import schema
import vocab

HERE = Path(__file__).parent

SENSOR_PARTS = [
    "part1_temp_humidity_pressure", "part2_air_gas", "part3_light_distance",
    "part4_presence_motion_magnetic", "part5_sound_force_touch",
    "part6_bio_weather_soil", "part7_water_power_position",
    "part8_gps_thermal_camera_rf", "part9_classics_and_gaps",
    "part10_industrial_exotic",
    # schema-v2 expansion files (added in phase B); absent files are skipped
    "part11_gaps_positioning_industrial", "part12_gaps_sensing_families",
    "part13_gaps_frontier_and_new",
]
OTHER_CATALOGS = [("actuators", "actuator"), ("glue", "glue"), ("boards", "board")]

# ---------------------------------------------------------------- migration maps

CAT_MIGRATION = {
    "Humidity + Temp": "Humidity & Moisture",
    "CO2 (true)": "CO2",
    "Particulate (PM)": "Particulate",
    "Color & Spectral": "Colour & Spectral",
    "Motion & IMU": "Motion & Vibration",
    "Vibration & Shock": "Motion & Vibration",
    "Power & Energy": "Power & Electrical",
    "GPS & Positioning": "GNSS & Positioning",
    "RFID & NFC": "Identity & Tags",
    "Industrial Sensing": "Industrial & Automotive",
    "E-Textile & Materials": "Materials & Textiles",
    "Weather & Outdoor": "Weather & Outdoor",
}

# v5's "Radiation & EM" mixed ionising radiation with RF electronics — two
# unrelated physics domains and two unrelated hazard classes. Split by part.
CAT_MIGRATION_BY_NAME = {
    "Geiger counter kit": "Radiation & Nuclear",
    "RD200 radon sensor": "Radiation & Nuclear",
    "EMF / RF field probes": "RF & Electromagnetic",
    "SI4432/CC1101 sub-GHz sniffer": "RF & Electromagnetic",
    # "Specialty & Exotic" was a junk drawer: 7 of 12 had an obvious real home.
    "FS3000 air velocity": "Weather & Outdoor",
    "LDC1612 inductive sensing": "Industrial & Automotive",
    "Scale-hacking: NAU7802": "Force & Weight",
    "Thermal flow: SDP + thermistor DIY": "Frontier Sensing",
    "Time-of-flight gesture radar 60GHz": "Presence & Occupancy",
    "Weight-in-motion: piezo cable": "Motion & Vibration",
    "Muon detector (CosmicWatch)": "Radiation & Nuclear",
    "Scintillating gamma spectrometer": "Radiation & Nuclear",
    "Soil/water nitrate ion-selective": "Water & Liquid",
    "Doppler ultrasonic flow (clamp-on)": "Water & Liquid",
    "Transit-time ultrasonic flow (clamp-on)": "Water & Liquid",
}

# Four v5 themes (Motion, Sound, Light, Touch) were near-synonyms of a category,
# so they duplicated the shelf instead of cross-cutting it. Dropped; entries that
# would be left tagless fall back to a category-derived theme.
THEME_DROP = {"Motion", "Sound", "Light", "Touch"}
CAT_FALLBACK_THEME = {
    "Temperature": "Home", "Humidity & Moisture": "Home", "Pressure & Altitude": "Wild",
    "Gas & VOC": "Air", "CO2": "Air", "Particulate": "Air",
    "Light & UV": "Home", "Colour & Spectral": "Play",
    "Distance & Ranging": "Robots", "Presence & Occupancy": "Home",
    "Motion & Vibration": "MachineHealth", "Magnetic & Compass": "MachineHealth",
    "Sound & Audio": "Play", "Force & Weight": "Home",
    "Touch & Capacitive": "Play", "Flex & Stretch": "Health",
    "Biometric & Health": "Health", "Weather & Outdoor": "Wild",
    "Soil & Agriculture": "Grow", "Water & Liquid": "Water",
    "Power & Electrical": "Energy", "Position & Rotation": "Robots",
    "GNSS & Positioning": "Wild", "Thermal Imaging": "Invisible",
    "Cameras & Vision": "Play", "Radiation & Nuclear": "Invisible",
    "RF & Electromagnetic": "Invisible", "Identity & Tags": "Access",
    "Industrial & Automotive": "Industry", "Materials & Textiles": "Play",
    "Frontier Sensing": "Invisible",
}

# Legacy free-text interfaces -> the INTERFACE enum. v5 had 101 distinct strings
# for what is really 16 buses, which made "every I2C part" unanswerable.
IFACE_PATTERNS = [
    (r"\bI2S\b", "I2S"), (r"\bI2C\b|\bI²C\b", "I2C"), (r"\bSPI\b", "SPI"),
    (r"\bRS-?485\b|Modbus", "RS-485"), (r"\bCAN\b|TWAI", "CAN"),
    (r"4-?20\s?mA", "4-20mA"), (r"\bUART\b|serial", "UART"),
    (r"1-?Wire", "1-Wire"), (r"\bUSB\b", "USB"),
    (r"\bDVP\b|MIPI|camera", "Camera"),
    (r"quadrature|\bPCNT\b|pulse|trigger/echo|tach", "Pulse"),
    (r"\bPWM\b", "PWM"),
    (r"radio itself|CSI|RSSI|backscatter", "Radio"),
    (r"built-?in|native", "Builtin"),
    (r"analog|\bADC\b|divider|bridge|0-1V|10mV", "Analog"),
    (r"digital|NPN|PNP|open.collector|dry contact|HIGH/LOW|comparator|switch", "Digital"),
]


def parse_iface(text):
    found = []
    for pat, name in IFACE_PATTERNS:
        if re.search(pat, text, re.I) and name not in found:
            found.append(name)
    return found or ["Analog"]


_UNIT = {"na": 0.001, "ua": 1.0, "µa": 1.0, "ma": 1000.0, "a": 1_000_000.0}


def parse_power_ua(text):
    """Best-effort µA from v5's free-text power strings. Returns None if unparseable."""
    if not text:
        return None
    t = text.strip().lower()
    if t.startswith("0") or "passive" in t or "generates" in t or t == "—":
        return 0.0
    m = re.search(r"([\d.]+)\s*(na|µa|ua|ma|a)\b", t)
    if m:
        try:
            return float(m.group(1)) * _UNIT[m.group(2)]
        except (ValueError, KeyError):
            return None
    m = re.search(r"([\d.]+)\s*(m?w)\b", t)  # power in W/mW at ~3.3V
    if m:
        watts = float(m.group(1)) * (0.001 if m.group(2) == "mw" else 1.0)
        return watts / 3.3 * 1_000_000
    return None


# ---------------------------------------------------------------- ids

IDS_PATH = HERE / "ids.json"


def natural_key(rec):
    return f"{rec.get('catalog','sensor')}|{rec['n']}"


def load_ids():
    if IDS_PATH.exists():
        return json.loads(IDS_PATH.read_text())
    return {}


def assign_ids(records, persist=True):
    """Stable IDs, assigned once and frozen. v5 generated them from sort order at
    build time, so adding one sensor renumbered everything downstream."""
    ids = load_ids()
    prefix = {"sensor": "S", "actuator": "A", "glue": "G", "board": "B"}
    used = {v for v in ids.values()}
    counters = {}
    for p in prefix.values():
        nums = [int(v[1:]) for v in used if v.startswith(p) and v[1:].isdigit()]
        counters[p] = max(nums) if nums else 0
    new = False
    for r in records:
        k = natural_key(r)
        if k not in ids:
            p = prefix[r.get("catalog", "sensor")]
            counters[p] += 1
            ids[k] = f"{p}{counters[p]:03d}"
            new = True
        r["id"] = ids[k]
    if new and persist:
        IDS_PATH.write_text(json.dumps(ids, indent=1, sort_keys=True, ensure_ascii=False))
    return records


# ---------------------------------------------------------------- load

def _import(name):
    try:
        return __import__(name)
    except ModuleNotFoundError:
        return None


def load_all(persist_ids=True):
    records = []
    for mod_name in SENSOR_PARTS:
        mod = _import(mod_name)
        if mod is None:
            continue
        for r in mod.SENSORS:
            r = dict(r)
            r.setdefault("catalog", "sensor")
            records.append(r)
    for mod_name, kind in OTHER_CATALOGS:
        mod = _import(mod_name)
        if mod is None:
            continue
        for r in getattr(mod, "PARTS", []):
            r = dict(r)
            r["catalog"] = kind
            records.append(r)

    for r in records:
        # category migration
        cat = r.get("cat", "")
        cat = CAT_MIGRATION_BY_NAME.get(r["n"], CAT_MIGRATION.get(cat, cat))
        r["cat"] = cat
        # theme migration
        if isinstance(r.get("tags"), str):
            tags = [t.strip() for t in r["tags"].split(",") if t.strip()]
        else:
            tags = list(r.get("tags") or [])
        tags = [t for t in tags if t not in THEME_DROP and t in vocab.THEME]
        if not tags:
            fb = CAT_FALLBACK_THEME.get(cat)
            tags = [fb] if fb else ["Play"]
        r["tags"] = tags
        # interface enum
        if isinstance(r.get("iface"), str):
            r["iface"] = parse_iface(r["iface"])
        # vendor list
        if isinstance(r.get("buy"), str):
            r["buy"] = [v.strip() for v in r["buy"].split(",") if v.strip() and v.strip() != "—"]
        # phenomena/inferences may arrive as csv strings
        for f in ("phenomena", "inferences", "hazard", "environment"):
            if isinstance(r.get(f), str):
                r[f] = [v.strip() for v in r[f].split(",") if v.strip()]

    assign_ids(records, persist=persist_ids)

    # enrichment overlay, keyed by stable id
    enrich = _import("enrich")
    if enrich is not None:
        overlay = getattr(enrich, "ENRICH", {})
        for r in records:
            extra = overlay.get(r["id"])
            if extra:
                for k, v in extra.items():
                    r[k] = v

    # derived — computed, never authored
    for r in records:
        if r.get("pwr_ua") is None:
            r["pwr_ua"] = parse_power_ua(r.get("pwr", ""))
        r["_tier"] = schema.price_tier(r.get("usd"))
        r["_power_class"] = schema.power_class(r.get("pwr_ua"), r.get("pwr", ""))
        r.setdefault("modality", None)
        r.setdefault("phenomena", [])
        r.setdefault("inferences", [])
        r.setdefault("confidence", "High")

    seeds_mod = _import("seeds")
    seeds = getattr(seeds_mod, "SEEDS", []) if seeds_mod else []
    return records, seeds
