#!/usr/bin/env python3
"""Ingest authored catalog fragments into data modules, with validation.

    python3 ingest.py records  <src.py> data/part11_x.py SENSORS
    python3 ingest.py overlay  <src.py> data/enrich.py   ENRICH

Authoring agents return a bare Python literal (a list of dicts, or a dict keyed
by part id). This script exec()s it in a sandbox, checks it against schema v2
BEFORE it can reach the build, normalises it, and writes a tidy module.

Anything that fails is reported per-record and skipped rather than silently
poisoning the catalog — v5's lesson was that unvalidated data is worse than
missing data.
"""
import ast
import pprint
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))

import schema  # noqa: E402
import vocab   # noqa: E402


def load_literal(path):
    """Parse a bare Python literal, tolerating stray fences or prose around it."""
    text = Path(path).read_text()
    # strip markdown fences if an agent added them despite instructions
    if "```" in text:
        parts = [p for p in text.split("```") if p.strip()]
        parts = [p[len("python"):] if p.lstrip().startswith("python") else p for p in parts]
        text = max(parts, key=len)
    text = text.strip()
    start = min((i for i in (text.find("["), text.find("{")) if i != -1), default=-1)
    if start == -1:
        raise SystemExit(f"{path}: no list or dict literal found")
    end = max(text.rfind("]"), text.rfind("}"))
    text = text[start:end + 1]
    # dict(...) calls are not literals, so eval in a namespace that provides dict
    return eval(compile(ast.parse(text, mode="eval"), "<ingest>", "eval"), {"dict": dict}, {})


def check(rec, label):
    """Returns (ok, [problems]). Only fields the schema knows, only legal values."""
    problems = []
    for k in list(rec):
        if k not in schema.FIELDS:
            problems.append(f"unknown field {k!r}")
            rec.pop(k)
    for field, val in list(rec.items()):
        if val in (None, "", []):
            continue
        kind = schema.FIELDS[field][1]
        if kind.startswith("enum:"):
            allowed = getattr(schema, kind.split(":")[1])
            if val not in allowed:
                problems.append(f"{field}={val!r} illegal")
                rec.pop(field)
        elif kind.startswith("enumlist:"):
            allowed = getattr(schema, kind.split(":")[1])
            bad = [v for v in val if v not in allowed]
            if bad:
                problems.append(f"{field} drops {bad}")
                rec[field] = [v for v in val if v in allowed]
        elif kind.startswith("vocab:"):
            allowed = getattr(vocab, kind.split(":")[1])
            if val not in allowed:
                problems.append(f"{field}={val!r} not in vocabulary")
        elif kind.startswith("vocablist:"):
            allowed = getattr(vocab, kind.split(":")[1])
            bad = [v for v in val if v not in allowed]
            if bad:
                problems.append(f"{field} drops {bad}")
                rec[field] = [v for v in val if v in allowed]
        elif kind == "float" and isinstance(val, str):
            try:
                rec[field] = float(val.replace(",", ""))
            except ValueError:
                problems.append(f"{field}={val!r} not numeric")
                rec.pop(field)
        elif kind == "csv" and isinstance(val, str):
            rec[field] = [v.strip() for v in val.split(",") if v.strip()]
    return problems


def ingest_records(src, dest, varname):
    data = load_literal(src)
    if not isinstance(data, list):
        raise SystemExit(f"{src}: expected a list of dicts, got {type(data).__name__}")
    kept, dropped = [], 0
    for rec in data:
        if not isinstance(rec, dict) or not rec.get("n"):
            dropped += 1
            continue
        problems = check(rec, rec.get("n", "?"))
        # `id` is assigned by the loader from ids.json, never authored
        missing = [f for f in schema.REQUIRED_CORE if f != "id" and not rec.get(f)]
        if missing:
            print(f"  ✗ {rec.get('n','?')[:44]:44} missing {missing}")
            dropped += 1
            continue
        if problems:
            print(f"  ~ {rec['n'][:44]:44} {'; '.join(problems)[:90]}")
        kept.append(rec)
    write_module(dest, varname, kept, src)
    print(f"✓ {dest}: {len(kept)} records ({dropped} dropped)")
    return kept


def ingest_overlay(src, dest, varname, merge=True):
    data = load_literal(src)
    if not isinstance(data, dict):
        raise SystemExit(f"{src}: expected a dict keyed by id")
    existing = {}
    if merge and Path(dest).exists():
        ns = {}
        exec(compile(Path(dest).read_text(), dest, "exec"), {"dict": dict}, ns)
        existing = ns.get(varname, {})
    added = 0
    for pid, rec in data.items():
        if not isinstance(rec, dict):
            continue
        problems = check(rec, pid)
        if problems:
            print(f"  ~ {pid} {'; '.join(problems)[:90]}")
        existing.setdefault(pid, {}).update(rec)
        added += 1
    write_module(dest, varname, existing, src)
    print(f"✓ {dest}: {added} ids merged, {len(existing)} total")
    return existing


def write_module(dest, varname, obj, src):
    header = (
        f'"""Generated by ingest.py from {Path(src).name}.\n\n'
        f'Validated against schema v2 at ingest time: unknown fields and illegal\n'
        f'enum/vocabulary values are stripped rather than allowed into the build.\n'
        f'"""\n'
    )
    body = pprint.pformat(obj, width=100, sort_dicts=False)
    Path(dest).write_text(f"{header}\n{varname} = {body}\n")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        raise SystemExit(__doc__)
    mode, src, dest, var = sys.argv[1:5]
    if mode == "records":
        ingest_records(src, dest, var)
    elif mode == "overlay":
        ingest_overlay(src, dest, var)
    else:
        raise SystemExit(f"unknown mode {mode!r}")
