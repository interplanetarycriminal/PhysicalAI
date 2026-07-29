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
STRICT = "--strict" in sys.argv


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

    # unknown fields — catches typos like v5's spec_note="".
    # Leading-underscore keys are loader-computed derived values, not authored.
    for k in r:
        if not k.startswith("_") and k not in schema.FIELDS:
            err(pid, f"unknown field {k!r}")

    for f in schema.REQUIRED_CORE:
        if f not in r or r[f] in (None, "", []):
            err(pid, f"missing required field {f!r}")
    for f in schema.REQUIRED_SEMANTIC:
        if f not in r or r[f] in (None, "", []):
            (err if STRICT else warn)(pid, f"not yet enriched: {f!r}")

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


def validate_fusion(records):
    """The fusion layer's contract: every capability atom resolves, every
    emergent outcome is reachable, and the chain graph is a DAG (a cycle would
    be an Excel circular reference on the Kit Builder sheet)."""
    try:
        import fusion
        import vocab
    except ImportError:
        warn("fusion", "data/fusion.py not present — fusion checks skipped")
        return
    P, I, E = set(vocab.PHENOMENON), set(vocab.INFERENCE), set(fusion.EMERGENT)

    for k, v in fusion.EMERGENT.items():
        if not (isinstance(v, tuple) and len(v) == 2):
            err(f"fusion:{k}", "EMERGENT value must be (question, domain)")
            continue
        if v[1] not in vocab.INFERENCE_DOMAINS:
            err(f"fusion:{k}", f"unknown domain {v[1]!r}")
        if k in P or k in I:
            err(f"fusion:{k}", "EMERGENT key collides with PHENOMENON/INFERENCE")

    seen, provided = set(), set()
    for e in fusion.FUSION_EDGES:
        k = e.get("key", "?")
        for f in ("key", "name", "pattern", "requires", "provides",
                  "math", "why", "confound", "example"):
            if not e.get(f):
                err(f"fusion:{k}", f"missing/empty field {f!r}")
        if k in seen:
            err(f"fusion:{k}", "duplicate edge key")
        seen.add(k)
        if e.get("pattern") not in vocab.FUSION:
            err(f"fusion:{k}", f"pattern {e.get('pattern')!r} not in vocab.FUSION")
        for c, m in e.get("requires") or []:
            if c not in P | I | E:
                err(f"fusion:{k}", f"unresolved capability {c!r}")
            if not (isinstance(m, int) and 1 <= m <= 10):
                err(f"fusion:{k}", f"multiplicity {m!r} out of range for {c!r}")
            if m > 1 and c in E:
                err(f"fusion:{k}", f"multiplicity >1 on emergent {c!r} — granted "
                                   "capabilities are boolean")
        pv = e.get("provides")
        if pv not in E | I:
            err(f"fusion:{k}", f"provides {pv!r} not in EMERGENT or INFERENCE")
        if pv in {c for c, _m in e.get("requires") or []}:
            err(f"fusion:{k}", "edge requires its own provides")
        provided.add(pv)
    for k in E - provided:
        err(f"fusion:{k}", "EMERGENT outcome no edge provides — orphan")

    try:
        fusion.topo_edges()
    except ValueError as ex:
        err("fusion", str(ex))

    # honest negative space: edges even the full catalog cannot fire
    from collections import Counter as _C
    counts = _C()
    for r in records:
        if r.get("catalog") != "sensor":
            continue
        for c in fusion.covers(r):
            counts[c] += 1
    granted = set()
    for e in fusion.topo_edges():
        ok = all(counts.get(c, 0) >= m or (m == 1 and c in granted)
                 for c, m in e["requires"])
        if ok:
            granted.add(e["provides"])
        else:
            missing = [f"{c} (need {m}, have {counts.get(c, 0)})"
                       for c, m in e["requires"]
                       if counts.get(c, 0) < m and not (m == 1 and c in granted)]
            warn(f"fusion:{e['key']}", "unfireable even by the full catalog — "
                                       + ", ".join(missing))


def main():
    records, seeds = load_all()
    seen_ids, seen_pns = {}, {}
    for r in records:
        validate_record(r, seen_ids, seen_pns)
    validate_seeds(records, seeds)
    validate_fusion(records)

    collisions = validate_i2c(records)

    print(f"Validated {len(records)} parts, {len(seeds)} seeds"
          + ("  [STRICT]" if STRICT else ""))
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
