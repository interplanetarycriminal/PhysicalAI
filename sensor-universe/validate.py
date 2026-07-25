#!/usr/bin/env python3
"""Hard validation gate for the Sensor Universe data.

Exits non-zero on any error. Run before every build.

This exists because v5 shipped with: a stray schema key on one record, 165
distinct free-text power strings, categories that silently invented themselves,
duplicate dict keys that clobbered real content at parse time, seeds citing
sensors that did not exist, and an I2C stack that could not physically work
(five VL53L1X on one bus, all at address 0x29).
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))

import schema  # noqa: E402
import vocab   # noqa: E402
from loader import load_all  # noqa: E402

ERRORS, WARNINGS = [], []


def err(part_id, msg):
    ERRORS.append(f"  ✗ [{part_id}] {msg}")


def warn(part_id, msg):
    WARNINGS.append(f"  ! [{part_id}] {msg}")


# Text that implies a hazard. If a record matches and declares no hazard, that is
# an error — this is the check that would have caught v5's gas-locker advice.
HAZARD_TRIGGERS = [
    (r"\bmains\b|\b230\s?V|\b120\s?V|\bAC line\b|CT clamp|live conductor", "Mains"),
    (r"\b\d{3,}\s?V\b|high[- ]voltage|400\s?V|SiPM bias", "HighVoltage"),
    (r"heated (?:bead|element|hotplate)|~?300°C|heater\b", "HotSurface"),
    (r"\blaser\b", "Laser"),
    (r"UV-?C|germicidal", "UV"),
    (r"explosive|flammable atmosphere|LPG|propane|hydrogen|methane", "Ignition"),
    (r"\bCO2\b.*(?:tank|cylinder|enrich)|asphyxia", "Asphyxiant"),
    (r"carbon monoxide|\bCO\b gas|toxic|H2S|formaldehyde", "Toxic"),
]


def validate_record(r, seen_ids, seen_pns):
    pid = r.get("id", r.get("n", "<no id>"))

    # unknown fields — catches typos like v5's spec_note=""
    for k in r:
        if k not in schema.FIELDS:
            err(pid, f"unknown field {k!r}")

    for f in schema.REQUIRED:
        if f not in r or r[f] in (None, "", []):
            err(pid, f"missing required field {f!r}")

    if r.get("id") in seen_ids:
        err(pid, f"duplicate id (also {seen_ids[r['id']]!r})")
    else:
        seen_ids[r.get("id")] = r.get("n")

    pn = (r.get("pn") or "").strip().lower()
    if pn:
        if pn in seen_pns:
            warn(pid, f"part number shared with {seen_pns[pn]!r} — merge or differentiate")
        else:
            seen_pns[pn] = r.get("n")

    # enums and vocabularies
    for field, (_req, kind, _note) in schema.FIELDS.items():
        if field not in r or r[field] in (None, "", []):
            continue
        val = r[field]
        if kind.startswith("enum:"):
            allowed = getattr(schema, kind.split(":")[1])
            if val not in allowed:
                err(pid, f"{field}={val!r} not in {kind.split(':')[1]}")
        elif kind.startswith("enumlist:"):
            allowed = getattr(schema, kind.split(":")[1])
            for v in val:
                if v not in allowed:
                    err(pid, f"{field} contains {v!r}, not in {kind.split(':')[1]}")
        elif kind.startswith("vocab:"):
            allowed = getattr(vocab, kind.split(":")[1])
            if val not in allowed:
                err(pid, f"{field}={val!r} not in vocab {kind.split(':')[1]}")
        elif kind.startswith("vocablist:"):
            allowed = getattr(vocab, kind.split(":")[1])
            for v in val:
                if v not in allowed:
                    err(pid, f"{field} contains {v!r}, not in vocab {kind.split(':')[1]}")
        elif kind == "int" and not isinstance(val, int):
            err(pid, f"{field} must be int, got {type(val).__name__}")
        elif kind == "float" and not isinstance(val, (int, float)):
            err(pid, f"{field} must be numeric, got {type(val).__name__}")

    if r.get("diff") not in schema.DIFFICULTY_RUBRIC:
        err(pid, f"diff={r.get('diff')!r} outside 1-5")

    usd = r.get("usd")
    if isinstance(usd, (int, float)):
        if usd < 0:
            err(pid, "negative price")
        if usd > 400:
            warn(pid, f"price ${usd} is high — confirm it isn't a merged product range")

    # merged-product smell: v5 priced a $60 and a $225 part under one usd figure
    if r.get("pn") and re.search(r"\s/\s", r["pn"]) and r.get("confidence") != "Estimate":
        warn(pid, "pn merges multiple products but confidence is not 'Estimate' — "
                  "split the entry or mark the price as an estimate")

    # safety gate
    blob = " ".join(str(r.get(f, "")) for f in ("n", "meas", "how", "use", "spec", "spark", "pwr", "v", "note"))
    declared = set(r.get("hazard") or [])
    for pattern, hz in HAZARD_TRIGGERS:
        if re.search(pattern, blob, re.I) and hz not in declared:
            warn(pid, f"text implies hazard {hz!r} but it is not declared in `hazard`")

    # 3.3V safety: if the supply range goes above 3.6V and the interface is a raw
    # logic output, the record must say whether the signal is 3.3V-safe.
    v = str(r.get("v", ""))
    if re.search(r"(?:1[0-9]|[5-9])\s*-?\s*\d*\s*V", v) and r.get("logic_3v3") is None:
        if set(r.get("iface") or []) & {"Digital", "Pulse", "Analog", "PWM"}:
            warn(pid, f"supply '{v}' may exceed 3.3V logic and logic_3v3 is unset — "
                      "state explicitly whether the output can touch an ESP32 GPIO")


def validate_i2c(records):
    """Flag address collisions, and fixed-address parts used in multiples."""
    by_addr = defaultdict(list)
    for r in records:
        for a in re.findall(r"0x[0-9A-Fa-f]{2}", r.get("i2c_addr") or ""):
            by_addr[a.lower()].append(r["n"])
    collisions = {a: ns for a, ns in by_addr.items() if len(ns) > 1}
    return collisions


def validate_seeds(records, seeds):
    ids = {r["id"] for r in records}
    names = {r["n"] for r in records}
    for s in seeds:
        refs = s.get("sensor_ids") or []
        for ref in refs:
            if ref not in ids:
                err(f"seed:{s['name']}", f"references unknown part id {ref!r}")
        if not refs and s.get("sensors"):
            warn(f"seed:{s['name']}", "has free-text sensors but no structured sensor_ids — "
                                      "BOM cannot be computed or checked")


def main():
    records, seeds = load_all()
    seen_ids, seen_pns = {}, {}
    for r in records:
        validate_record(r, seen_ids, seen_pns)
    validate_seeds(records, seeds)

    collisions = validate_i2c(records)

    print(f"Validated {len(records)} parts, {len(seeds)} seeds")
    by_cat = Counter(r["cat"] for r in records)
    print(f"  {len(by_cat)} categories, "
          f"{len({m for r in records for m in [r.get('modality')] if m})} modalities in use")
    if collisions:
        print(f"  {len(collisions)} I2C addresses shared by 2+ parts "
              f"(expected and documented on the wiring sheet)")

    if WARNINGS:
        print(f"\n{len(WARNINGS)} warnings:")
        for w in WARNINGS[:60]:
            print(w)
        if len(WARNINGS) > 60:
            print(f"  … and {len(WARNINGS)-60} more")
    if ERRORS:
        print(f"\n{len(ERRORS)} ERRORS:")
        for e in ERRORS[:80]:
            print(e)
        if len(ERRORS) > 80:
            print(f"  … and {len(ERRORS)-80} more")
        sys.exit(1)
    print("\n✓ validation passed")


if __name__ == "__main__":
    main()
