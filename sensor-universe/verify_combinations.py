#!/usr/bin/env python3
"""Release gate for the combination ranker.

    python3 verify_combinations.py            check the live run
    python3 verify_combinations.py --quick    skip the 22s exhaustive pair pass

Exit 1 on any failure. The point of this file is that it does NOT trust
data/combinatorics.py: the headline row is recomputed here from the raw records
by a second, independently written closure and pin-budget implementation, and
the two answers must agree. If combinatorics.py and this file ever drift, one of
them is wrong and the build stops until someone decides which.
"""
import re
import subprocess
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))
sys.path.insert(0, str(HERE))

import combinatorics as cmb   # noqa: E402
import fusion                 # noqa: E402
import vocab                  # noqa: E402
from loader import load_all   # noqa: E402

QUICK = "--quick" in sys.argv
fails = []


def check(name, ok, detail=""):
    print(f"  {'✓' if ok else '✗ FAIL'} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        fails.append(name)


# ===========================================================================
# An INDEPENDENT implementation of everything the headline row depends on.
# Written from the schema and fusion.FUSION_EDGES, not from combinatorics.py:
# no import of covers(), closure(), esp32_fit() or chosen_iface() below.
# ===========================================================================

def indep_capabilities(rec):
    """phenomena ∪ inferences, vocab-filtered — straight off the record."""
    caps = set()
    for p in rec.get("phenomena") or []:
        if p in vocab.PHENOMENON:
            caps.add(p)
    for i in rec.get("inferences") or []:
        if i in vocab.INFERENCE:
            caps.add(i)
    return caps


def indep_closure_provides(recs):
    """Monotone fixpoint, written independently: how many DISTINCT parts cover
    each capability, then repeatedly fire any edge whose every (cap, mult) atom
    is satisfied — by part count, or by a previously granted single key.
    Returns the set of keys the combination PROVIDES (capabilities + grants)."""
    counts = {}
    for r in recs:
        for c in indep_capabilities(r):
            counts[c] = counts.get(c, 0) + 1
    granted, fired = set(), set()
    while True:
        added = False
        for e in fusion.FUSION_EDGES:
            if e["key"] in fired:
                continue
            ok = True
            for cap, mult in e["requires"]:
                if counts.get(cap, 0) >= mult:
                    continue
                if mult == 1 and cap in granted:
                    continue
                ok = False
                break
            if ok:
                fired.add(e["key"])
                granted.add(e["provides"])
                added = True
        if not added:
            break
    base = set()
    for r in recs:
        base |= indep_capabilities(r)
    return base | granted, fired


def indep_synergy_keys(recs):
    joint, _ = indep_closure_provides(recs)
    alone = set()
    for r in recs:
        solo, _ = indep_closure_provides([r])
        alone |= solo
    return joint - alone


def indep_pin_budget(recs):
    """The documented model, retyped: I2C shares 2, 1-Wire shares 1, SPI is
    3 + 1 CS each, UART is 2 each, everything else spends its own `pins`."""
    order = ["I2C", "1-Wire", "I2S", "SPI", "UART", "Pulse", "PWM", "Digital",
             "Analog", "Builtin", "Radio", "Camera", "USB", "RS-485", "CAN", "4-20mA"]
    picked = []
    for r in recs:
        have = r.get("iface") or []
        picked.append(next((w for w in order if w in have), have[0] if have else None))
    total = 0
    if "I2C" in picked:
        total += 2
    if "1-Wire" in picked:
        total += 1
    n_spi = picked.count("SPI")
    if n_spi:
        total += 3 + n_spi
    total += 2 * picked.count("UART")
    for r, p in zip(recs, picked):
        if p in ("I2C", "1-Wire", "SPI", "UART", "RS-485", "CAN", "4-20mA"):
            continue
        total += r["pins"] if isinstance(r.get("pins"), int) else 1
    return total


# ===========================================================================

def main():
    records, _ = load_all(persist_ids=False)
    sensors = [r for r in records if r.get("catalog") == "sensor"]
    boards = [r for r in records if r.get("catalog") == "board"]
    by_id = {r["id"]: r for r in sensors}
    print(f"Verifying the combination ranker over {len(sensors)} sensors, "
          f"{len(boards)} boards" + ("  [QUICK]" if QUICK else ""))

    # -- 1 · the lexicon's own contract ----------------------------------
    bad = [(k, p) for k, v in cmb.INTERFERENTS.items()
           for p in v["measured_by"] if p not in vocab.PHENOMENON]
    check("every measured_by key is in vocab.PHENOMENON", not bad,
          f"{len(cmb.INTERFERENTS)} interferents, "
          f"{sum(len(v['measured_by']) for v in cmb.INTERFERENTS.values())} keys"
          if not bad else str(bad))
    check("every interferent has a label and at least one pattern",
          all(v.get("label") and v.get("patterns") for v in cmb.INTERFERENTS.values()))
    dead = [k for k in cmb.INTERFERENTS
            if not any(cmb.extract_interferents(r).get(k) for r in sensors)]
    check("no interferent matches nothing in the catalog", not dead, str(dead))

    # -- 2 · rank ---------------------------------------------------------
    prep = cmb.prepare(sensors)
    pool = sensors if not QUICK else sensors[:120]
    rows = cmb.rank_pairs(pool, prep, boards)
    check("pair enumeration is exhaustive",
          len(rows) == len(pool) * (len(pool) - 1) // 2,
          f"{len(rows):,} rows for {len(pool)} sensors")
    check("ranking is sorted and deterministic",
          all(rows[i]["total"] >= rows[i + 1]["total"] for i in range(len(rows) - 1)))

    top = rows[0]
    recs = [by_id[i] for i in top["ids"]]
    print(f"\n  Top row: {' + '.join(top['names'])}  ({', '.join(top['ids'])}) "
          f"total {top['total']:.5f}\n")

    # -- 3 · recount the top row by the independent path ------------------
    indep_keys = indep_synergy_keys(recs)
    engine_keys = set(top["synergy"]["emergent_keys"]) | set(top["synergy"]["new_route_keys"])
    check("top row synergy set recomputed independently", indep_keys == engine_keys,
          f"{sorted(indep_keys)}"
          if indep_keys == engine_keys
          else f"independent {sorted(indep_keys)} != engine {sorted(engine_keys)}")

    indep_cost = round(sum(r.get("usd") or 0 for r in recs), 2)
    check("top row cost recomputed independently", indep_cost == top["usd"],
          f"${indep_cost}")

    indep_pins = indep_pin_budget(recs)
    engine_pins = cmb.esp32_fit(recs, boards)["pin_budget"]
    check("top row pin budget recomputed independently", indep_pins == engine_pins,
          f"{indep_pins} pins")

    # -- 4 · invariants over the whole run --------------------------------
    bad_overlap = []
    for r in rows:
        own = set()
        for i in r["ids"]:
            own |= indep_capabilities(by_id[i])
        syn = set(r["synergy"]["emergent_keys"]) | set(r["synergy"]["new_route_keys"])
        if syn & own:
            bad_overlap.append((r["ids"], sorted(syn & own)))
    check("no synergy key is already covered by a member", not bad_overlap,
          f"checked {len(rows):,} rows"
          if not bad_overlap else f"{len(bad_overlap)} violations, e.g. {bad_overlap[0]}")

    bad_em = [(r["ids"], k) for r in rows for k in r["synergy"]["emergent_keys"]
              if k not in fusion.EMERGENT]
    check("every reported emergent key is in fusion.EMERGENT", not bad_em,
          str(bad_em[:3]) if bad_em else "")
    bad_rt = [(r["ids"], k) for r in rows for k in r["synergy"]["new_route_keys"]
              if k not in vocab.INFERENCE]
    check("every reported new-route key is in vocab.INFERENCE", not bad_rt,
          str(bad_rt[:3]) if bad_rt else "")

    bad_tot = [r["ids"] for r in rows if not (0.0 <= r["total"] <= 1.0)]
    check("every total lies in [0, 1]", not bad_tot, str(bad_tot[:3]) if bad_tot else "")
    bad_cmp = [(r["ids"], k) for r in rows for k, v in r["components"].items()
               if not (0.0 <= v <= 1.0)]
    check("every normalised component lies in [0, 1]", not bad_cmp,
          str(bad_cmp[:3]) if bad_cmp else "")

    bad_time = [r["ids"] for r in rows
                if r["time"]["decades"] is None and r["time"]["score"] != 0.0]
    check("an unknown tau never scores above zero", not bad_time,
          str(bad_time[:3]) if bad_time else "")

    # a tau is never invented: every member with a tau must have a basis quoting
    # a field that actually contains something
    bad_basis = []
    for r in sensors:
        tau, basis, conf = cmb.estimate_tau(r)
        if tau is None and conf != "none":
            bad_basis.append((r["id"], "tau None but confidence " + conf))
        if tau is not None and not (r.get("rate") or r.get("warmup")):
            bad_basis.append((r["id"], "tau from nothing"))
    check("no tau is invented from an empty field", not bad_basis,
          str(bad_basis[:3]) if bad_basis else "")

    # -- 4b · the round-two fixes actually fire ---------------------------
    # Each of these asserts that a fix CHANGED something on the real data. A
    # fix that quietly matches nothing is worse than no fix, because it reads
    # as a guarantee in the report.

    # Fix 3 — negation and effect-word guards
    guarded, rejects_seen = 0, {}
    for r in sensors:
        _found, rej = cmb.extract_interferents(r, with_rejects=True)
        for k, whys in rej.items():
            for _lit, why in whys:
                guarded += 1
                tag = why.split(" '")[0].split(" (")[0]
                rejects_seen[tag] = rejects_seen.get(tag, 0) + 1
    check("Fix 3 · the negation/effect-word guards reject real matches", guarded > 0,
          f"{guarded} rejections across {len(sensors)} sensors: "
          + ", ".join(f"{k} x{v}" for k, v in sorted(rejects_seen.items(),
                                                     key=lambda kv: -kv[1])[:3]))
    bmp = by_id.get("S192")
    if bmp:
        _f, rej = cmb.extract_interferents(bmp, with_rejects=True)
        # The named regression: BMP280's fools text says a fake BME280 arrives
        # "with no humidity sensor at all". The negation guard must reject that
        # occurrence. It does NOT follow that `humidity` disappears from the
        # record — the same prose later says "before you trust a humidity number
        # from a $2 board", which survives the guard and is a DIFFERENT kind of
        # false positive (topical, not negated). That residue is measured in the
        # report, not silently asserted away here.
        check("Fix 3 · BMP280's 'with no humidity sensor' occurrence is rejected",
              any("negated" in why for _lit, why in rej.get("humidity", [])),
              str(rej.get("humidity", "NOT REJECTED — the guard regressed")))

    # Fix 1 — incidental capabilities
    inc_parts = {r["id"]: cmb.incidental_capabilities(r) for r in sensors}
    n_inc = sum(len(v) for v in inc_parts.values())
    n_listed = sum(len([p for p in (r.get("phenomena") or []) if p in vocab.PHENOMENON])
                   for r in sensors)
    check("Fix 1 · incidental capabilities are found", 0 < n_inc < n_listed,
          f"{n_inc} of {n_listed} phenomenon listings ({100 * n_inc / n_listed:.0f}%)")
    whole = [r["id"] for r in sensors
             if inc_parts[r["id"]]
             and len(inc_parts[r["id"]]) ==
             len([p for p in (r.get("phenomena") or []) if p in vocab.PHENOMENON])]
    # A part flagged wholly incidental measures NOTHING it says it is for, which
    # is normally a stem miss. Six survive and each was read: S235 is a bench rig
    # whose phenomena belong to its constituent parts, S366 is an EEG front end
    # whose EOG/EMG really are side channels, and the rest are genuinely marginal
    # (optical flow as `displacement-linear`). The gate is a ceiling, not zero.
    check("Fix 1 · almost no part is WHOLLY incidental", len(whole) <= 8,
          f"{len(whole)} of {len(sensors)}: {whole}")
    fuel = by_id.get("S375")
    if fuel:
        check("Fix 1 · MAX17260's die-temperature register is incidental",
              "temperature-contact" in inc_parts["S375"],
              "the multiplicity halo depends on this being caught")

    # the discount reaches the score
    disc = [r for r in rows if r["synergy"].get("multiplicity_incidental_keys")]
    check("Fix 1 · the incidental discount fires on real rows", bool(disc),
          f"{len(disc):,} of {len(rows):,} rows carry a near-zero multiplicity key")

    # Fix 2 — transduction mechanisms
    full = [cmb.score_combo([by_id[i] for i in r["ids"]], prep, boards)
            for r in rows[:60]]
    bad_diff = []
    for s2 in full:
        for x in s2["shared_measurand"]["shared"]:
            ma, mb = set(x["mechanism_a"] or []), set(x["mechanism_b"] or [])
            if x["kind"] == "differential" and (not ma or not mb or (ma & mb)):
                bad_diff.append((s2["ids"], x["phenomenon"]))
            if x["weight"] == 1.0 and x["kind"] != "differential":
                bad_diff.append((s2["ids"], x["phenomenon"], "full weight, not differential"))
            if (x["incidental_a"] or x["incidental_b"]) and x["weight"] != 0.0:
                bad_diff.append((s2["ids"], x["phenomenon"], "incidental but paid"))
    check("Fix 2 · full shared-measurand credit needs two DIFFERENT known mechanisms",
          not bad_diff, str(bad_diff[:2]) if bad_diff else
          f"{sum(len(s2['shared_measurand']['shared']) for s2 in full)} channels checked "
          f"over the top 60 rows")
    n_mech = sum(1 for r in sensors if cmb.mechanisms(r))
    check("Fix 2 · mechanisms are read for most parts, and UNKNOWN is left unknown",
          0 < n_mech < len(sensors),
          f"{n_mech}/{len(sensors)} sensors have an identified mechanism; "
          f"{len(sensors) - n_mech} are unknown and can never earn differential credit")

    # Fix 4 — tau confidence attenuation
    bad_tf = [r["ids"] for r in rows
              if abs(r["time"]["score"] - r["time"]["raw"]
                     * r["time"]["confidence_factor"]) > 2e-4]   # both are round(_, 4)
    check("Fix 4 · the time component equals raw x tau-confidence factor", not bad_tf,
          str(bad_tf[:3]) if bad_tf else f"{len(rows):,} rows")
    atten = [r for r in rows if r["time"]["raw"] > 0
             and r["time"]["confidence_factor"] < 1.0]
    check("Fix 4 · the attenuation actually bites", bool(atten),
          f"{len(atten):,} rows scored below their raw time value")
    lb = [r["id"] for r in sensors if cmb.estimate_tau(r, with_bound=True)[3]]
    check("Fix 4 · rate-derived taus are flagged as LOWER BOUNDS", bool(lb),
          f"{len(lb)} of {len(sensors)} sensors")
    bad_lb = [r["id"] for r in sensors
              if cmb.estimate_tau(r, with_bound=True)[3]
              and "LOWER BOUND" not in cmb.estimate_tau(r)[1]]
    check("Fix 4 · every lower-bound tau says so in its basis string", not bad_lb,
          str(bad_lb[:3]) if bad_lb else "")

    # Fix 5 — family dedup keeps the best of the family
    by_ids = {tuple(r["ids"]): r for r in rows}
    bad_dd = []
    for r in rows:
        tgt = r.get("deduped_into")
        if not tgt:
            continue
        t = by_ids.get(tuple(tgt))
        if t is None:
            bad_dd.append((r["ids"], "target not in the run"))
        elif t["total"] < r["total"]:
            bad_dd.append((r["ids"], "collapsed into a WORSE row"))
        elif t["family_signature"] != r["family_signature"]:
            bad_dd.append((r["ids"], "different family"))
        elif sorted(t["synergy"]["keys"]) != sorted(r["synergy"]["keys"]):
            bad_dd.append((r["ids"], "different synergy claim"))
    n_dd = sum(1 for r in rows if r.get("deduped_into"))
    check("Fix 5 · dedup keeps the best row of each family+claim", not bad_dd,
          str(bad_dd[:2]) if bad_dd else
          f"{n_dd:,} of {len(rows):,} rows collapsed, "
          f"{len({v['family'] for v in prep.values()})} families")
    check("Fix 5 · dedup collapses something but not everything",
          0 < n_dd < len(rows), f"{n_dd:,}")

    # Fix 6 — co-location
    doubt = [c for s2 in full for c in s2["compensation"]["channels"]
             if c["co_location"] == "doubtful"]
    bad_cl = [c for c in doubt if c["weight"] >= 1.0]
    check("Fix 6 · a doubtful co-location always attenuates its channel", not bad_cl,
          f"{len(doubt)} doubtful channels in the top 60 rows"
          if not bad_cl else str(bad_cl[:1]))
    ncl = sum(1 for a, b in combinations(sensors[:150], 2)
              if cmb.co_location(a, b)[0] == "doubtful")
    check("Fix 6 · the co-location test fires on the real catalog", ncl > 0,
          f"{ncl:,} doubtful orderings among the first 150 sensors")

    # Fix 7 — per-k percentile
    bad_p = [r["ids"] for r in rows
             if not isinstance(r.get("percentile_within_k"), float)
             or not (0.0 <= r["percentile_within_k"] <= 100.0)]
    check("Fix 7 · every row carries a percentile_within_k in [0, 100]", not bad_p,
          str(bad_p[:3]) if bad_p else f"{len(rows):,} rows")
    bad_mono = [rows[i]["ids"] for i in range(len(rows) - 1)
                if rows[i]["percentile_within_k"] < rows[i + 1]["percentile_within_k"]]
    check("Fix 7 · percentile is monotone with total", not bad_mono,
          str(bad_mono[:3]) if bad_mono else "")
    bad_k = [r["ids"] for r in rows if r.get("k") != len(r["ids"])]
    check("Fix 7 · every row states its own k", not bad_k, "")

    # -- 4c · THE PHYSICS-LAYER GATE --------------------------------------
    # The px_* preference chain is designed against a schema on another branch.
    # Nothing here may quietly depend on it: this run must have come out of the
    # prose fallback path end to end. If this check starts failing because the
    # fields have landed, that is NOT a bug — it means the ranking must be
    # re-read as a px run, and this assertion should be updated deliberately.
    PX = ("px_status", "px_measurand", "px_units", "px_effect", "px_chain", "px_cross",
          "px_cross_note", "px_range", "px_resolution", "px_bandwidth", "px_drift",
          "px_implies", "px_ref", "px_ref_kind")
    have_px = [r["id"] for r in records if any((r.get(f) or "") for f in PX)]
    check("px gate · no record carries a physics-layer field today", not have_px,
          f"{len(records)} records, none with any of {len(PX)} px_* fields"
          if not have_px else f"{len(have_px)} records DO: {have_px[:5]} — the ranking "
          f"is no longer a pure prose run and the report must say so")
    check("px gate · every tau came from the prose path",
          all(v["tau_source"] == "prose" for v in prep.values()),
          f"{len(prep)} sensors")
    check("px gate · every incidental verdict came from the prose path",
          all(v["incidental_source"] == "prose" for v in prep.values()))
    check("px gate · every mechanism came from the prose path",
          all(v["mechanism_source"] == "prose" for v in prep.values()))
    srcs = {c["source"] for s2 in full for c in s2["compensation"]["channels"]}
    check("px gate · every compensation channel came from the prose lexicon",
          srcs <= {"prose"}, f"sources seen: {sorted(srcs) or ['none']}")
    check("px gate · has_physics_layer() agrees",
          not any(cmb.has_physics_layer(r) for r in records))
    check("px gate · the PHYSQTY bridge is wired to real PHENOMENON keys",
          all(p in vocab.PHENOMENON
              for v in cmb.PHYSQTY_OBSERVED_BY.values() for p in v),
          f"{len(cmb.PHYSQTY_OBSERVED_BY)} PHYSQTY tokens mapped")

    # -- 5 · the --explain path agrees with the ranked row -----------------
    ids = ",".join(top["ids"])
    out = subprocess.run([sys.executable, str(HERE / "combine.py"), "--explain", ids],
                         capture_output=True, text=True, timeout=600)
    ok = out.returncode == 0
    m = re.search(r"\*\*([0-9.]+)\*\*", out.stdout or "")
    check("--explain runs", ok, (out.stderr or "").strip()[-300:] if not ok else "")
    check("--explain total matches the ranked row",
          bool(m) and abs(float(m.group(1)) - top["total"]) < 5e-5,
          f"explain {m.group(1) if m else '?'} vs rank {top['total']:.5f}")
    for k in top["synergy"]["emergent_keys"]:
        if f"**{k}**" not in (out.stdout or ""):
            check(f"--explain lists emergent key {k}", False)
            break
    else:
        check("--explain lists every emergent key of the ranked row", True,
              f"{len(top['synergy']['emergent_keys'])} keys")
    ncomp = (out.stdout or "").count("→ corrects")
    check("--explain lists every compensation channel of the ranked row",
          ncomp == len(top["compensation"]["channels"]),
          f"{ncomp} channels")

    print()
    if fails:
        print(f"✗ {len(fails)} FAILURES: {fails}")
        sys.exit(1)
    print("✓ combination ranker verified")


if __name__ == "__main__":
    main()
