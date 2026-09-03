#!/usr/bin/env python3
"""Physics-layer coverage report and quality gate.

Prints how much of the physics layer exists — totals by status, filled counts by
modality, and every filled sensor with its citation — then checks that anything
claiming `px_status="filled"` actually is: all eight substance fields present
(measurand, units, effect, range, resolution, bandwidth, drift, implies) plus a
citation (`px_ref` and `px_ref_kind`). Exits 1 if any filled record is
incomplete, so the data workers' output is checked mechanically rather than by
reading it.

A standalone script rather than a `solve.py --export` section: this is a gate,
and a gate needs its own exit code and its own run, independent of whether the
exporter happens to be running.

Usage:
    python3 px_report.py            # report + gate
    python3 px_report.py --quiet    # gate only: failures and the verdict
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))

import physics_layer  # noqa: E402
import schema  # noqa: E402
from loader import load_all  # noqa: E402

QUIET = "--quiet" in sys.argv


def say(*a):
    if not QUIET:
        print(*a)


def main():
    records, _seeds = load_all()
    sensors = [r for r in records if r.get("catalog", "sensor") == "sensor"]
    cov = physics_layer.coverage(records)

    say("PHYSICS LAYER COVERAGE")
    say("=" * 66)
    say(f"{cov['total']} sensors in the catalog")
    say("")
    for st in schema.PX_STATUS:
        n = cov["by_status"].get(st, 0)
        pct = (100.0 * n / cov["total"]) if cov["total"] else 0.0
        say(f"  {st:<10} {n:>4}   {pct:5.1f}%")

    say("")
    say("BY MODALITY (filled / total)")
    say("-" * 66)
    for mod in sorted(cov["by_modality"], key=lambda m: (-cov["filled_by_modality"][m], m)):
        say(f"  {mod:<14} {cov['filled_by_modality'][mod]:>4} / {cov['by_modality'][mod]:<4}")

    filled = [r for r in sensors if r.get("px_status") == "filled"]
    partial = [r for r in sensors if r.get("px_status") == "partial"]

    say("")
    say(f"FILLED RECORDS ({len(filled)})")
    say("-" * 66)
    if not filled:
        say("  (none yet — the physics data lands in data/physics_layer.py)")
    for r in sorted(filled, key=lambda r: r["id"]):
        say(f"  {r['id']}  {r['n']}")
        say(f"        {r.get('px_measurand') or '—'}")
        say(f"        ref: {r.get('px_ref') or 'MISSING'}"
            f"  [{r.get('px_ref_kind') or 'MISSING'}]")

    if partial:
        say("")
        say(f"PARTIAL RECORDS ({len(partial)})")
        say("-" * 66)
        for r in sorted(partial, key=lambda r: r["id"]):
            gaps = physics_layer.missing_fields(r)
            say(f"  {r['id']}  {r['n']:<38} still needs: {', '.join(gaps) or '—'}")

    # ------------------------------------------------------------------ gate
    failures = []
    for r in sorted(filled, key=lambda r: r["id"]):
        gaps = physics_layer.missing_fields(r)
        if gaps:
            failures.append(f"  ✗ [{r['id']}] {r['n']}: claims 'filled' but is missing "
                            f"{', '.join(gaps)}")
        kind = r.get("px_ref_kind")
        if kind and kind not in schema.PX_REF_KIND:
            failures.append(f"  ✗ [{r['id']}] {r['n']}: px_ref_kind={kind!r} not in PX_REF_KIND")

    print("")
    if failures:
        print(f"{len(failures)} incomplete 'filled' records:")
        for f in failures:
            print(f)
        print("\n✗ physics-layer gate FAILED")
        return 1
    print(f"✓ physics-layer gate passed "
          f"({len(filled)} filled, {len(partial)} partial, "
          f"{cov['by_status'].get('unfilled', 0)} unfilled)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
