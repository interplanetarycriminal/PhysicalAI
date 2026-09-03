#!/usr/bin/env python3
"""Generate data/enrich_iface.py from the authored iface_data_*.json files.

    python3 tools/gen_enrich_iface.py [input_dir]

Each input file is `{"S042": {"esp32_driver": "...", "v_min": 3.0}, ...}` — any
subset of the eleven ESP32 interface fields, keyed by stable part ID. A key that
is absent is simply not written, and the loader derives it or nulls it. An
explicit JSON `null` is written as `None` and means "checked, could not verify".

Everything is validated before anything is written: an unknown field, an enum
value outside its enum, a non-numeric float, a non-integer int or an ID that is
not in the catalog is a hard error and nothing is generated. Two files that
disagree about the same field are a warning, resolved deterministically in
favour of the alphabetically last file.

Output is sorted by ID and by field, one field per line, so a regeneration
produces a readable diff instead of a reshuffle. A missing input directory or
zero input files is a clean no-op that still writes a valid empty module.
"""
import json
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "data"))

import iface_derive  # noqa: E402
import loader  # noqa: E402
import schema  # noqa: E402

DEFAULT_IN = ("/tmp/claude-0/-home-claude-PhysicalAI/"
              "e7bf3cf5-c37a-5ac4-8862-2f369627a164/scratchpad")
OUT = ROOT / "data" / "enrich_iface.py"
FIELDS = iface_derive.IFACE_FIELDS
MAX_LINE = 96

HEADER = '''"""Authored ESP32 interface fields, keyed by stable part ID.

GENERATED FILE — do not hand-edit. `tools/gen_enrich_iface.py` builds it from
the authored `iface_data_*.json` files and rewrites it wholesale; anything typed
in here by hand is lost on the next run. Edit the JSON, then regenerate.

This is the fourth and last overlay the loader merges, so a value here beats
`enrich_core`, `enrich`, `enrich_manual` and every derivation in
`data/iface_derive.py`. Author only what you have checked against a datasheet or
a real driver; leave the rest out and let the derivation (or an explicit None)
stand. An explicit None here means "checked, could not verify".
"""

'''

errors = []


def err(msg):
    errors.append(msg)


def id_key(pid):
    """S9 before S10. Non-conforming ids sort last, by string."""
    return (0, pid[0], int(pid[1:])) if pid[1:].isdigit() else (1, pid, 0)


def check_value(pid, field, val, src):
    """One authored value against the schema. None is always allowed."""
    if val is None:
        return
    _req, kind, _note = schema.FIELDS[field]
    if kind.startswith("enum:"):
        allowed = getattr(schema, kind.split(":")[1])
        if val not in allowed:
            err(f"{src}: {pid}.{field}={val!r} not in {kind.split(':')[1]}")
    elif kind == "float":
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            err(f"{src}: {pid}.{field}={val!r} must be a number")
    elif kind == "int":
        if isinstance(val, bool) or not isinstance(val, int):
            err(f"{src}: {pid}.{field}={val!r} must be an int")
    elif kind == "str":
        if not isinstance(val, str):
            err(f"{src}: {pid}.{field}={val!r} must be a string")


def literal(val):
    """A stable Python literal. Strings use double quotes, like the rest of the repo."""
    if isinstance(val, str):
        return json.dumps(val, ensure_ascii=False)
    return repr(val)


def emit_pair(field, val):
    """`"field": value,` lines, wrapping only long strings and only at spaces."""
    lit = literal(val)
    head = f'    "{field}": '
    if len(head) + len(lit) + 1 <= MAX_LINE or not isinstance(val, str):
        return [f"{head}{lit},"]
    width = MAX_LINE - len(head) - 4
    chunks = textwrap.wrap(val, width=max(width, 20), break_long_words=False,
                           break_on_hyphens=False)
    lines = [f"{head}{json.dumps(chunks[0] + ' ', ensure_ascii=False)}"]
    for c in chunks[1:-1]:
        lines.append(" " * len(head) + json.dumps(c + " ", ensure_ascii=False))
    lines.append(" " * len(head) + json.dumps(chunks[-1], ensure_ascii=False) + ",")
    return lines


def render(merged):
    if not merged:
        return HEADER + "ENRICH_IFACE: dict[str, dict] = {}\n"
    out = [HEADER, "ENRICH_IFACE: dict[str, dict] = {\n"]
    for pid in sorted(merged, key=id_key):
        out.append(f'"{pid}": {{\n')
        for field in FIELDS:
            if field in merged[pid]:
                out.append("\n".join(emit_pair(field, merged[pid][field])) + "\n")
        out.append("},\n")
    out.append("}\n")
    return "".join(out)


def main():
    in_dir = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IN)
    files = sorted(in_dir.glob("iface_data_*.json")) if in_dir.is_dir() else []
    if not in_dir.is_dir():
        print(f"input dir {in_dir} does not exist — writing an empty overlay")

    records, _ = loader.load_all(persist_ids=False)
    known = {r["id"] for r in records}

    merged, origin = {}, {}
    for path in files:
        src = path.name
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as ex:
            err(f"{src}: unreadable — {ex}")
            continue
        if not isinstance(data, dict):
            err(f"{src}: top level must be an object keyed by part ID")
            continue
        for pid, fields in sorted(data.items()):
            if pid not in known:
                err(f"{src}: unknown part id {pid!r}")
                continue
            if not isinstance(fields, dict):
                err(f"{src}: {pid} must map to an object")
                continue
            for field, val in sorted(fields.items()):
                if field not in FIELDS:
                    err(f"{src}: {pid} has unknown field {field!r}")
                    continue
                check_value(pid, field, val, src)
                prev = merged.setdefault(pid, {})
                if field in prev and prev[field] != val:
                    print(f"  ! {pid}.{field}: {origin[(pid, field)]} says "
                          f"{prev[field]!r}, {src} says {val!r} — taking {src}")
                prev[field] = val
                origin[(pid, field)] = src

    if errors:
        print(f"\n{len(errors)} ERRORS — nothing written:")
        for e in errors[:40]:
            print(f"  ✗ {e}")
        if len(errors) > 40:
            print(f"  … and {len(errors) - 40} more")
        sys.exit(1)

    OUT.write_text(render(merged), encoding="utf-8")
    n_vals = sum(len(v) for v in merged.values())
    print(f"wrote {OUT.relative_to(ROOT)}: {len(merged)} parts, {n_vals} values, "
          f"from {len(files)} file(s) in {in_dir}")


if __name__ == "__main__":
    main()
