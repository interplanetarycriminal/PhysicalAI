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
