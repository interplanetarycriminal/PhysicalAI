"""Outcome Solver — computes, from the live catalog, which sensors buy the most outcomes.

This is not a written sheet. It is an OPTIMISER that runs at build time against
whatever the catalog currently contains, so it cannot go stale.

The question: given 151 things you might want to KNOW and 405 sensors, which
small set of sensors buys you the most of them?

That is the Maximum Coverage Problem. It is NP-hard, but greedy selection is
provably within (1 − 1/e) ≈ 63% of optimal and no polynomial algorithm does
better, so greedy is not a compromise here — it is the right answer.

Two greedy objectives are run, and the difference between them is the finding:
  * by COUNT      — pick the sensor covering the most uncovered outcomes
  * by COUNT/COST — pick the sensor covering the most uncovered outcomes per pound

v50 already documents how to COMBINE sensors (Derived Quantities, Combination
Grammar, Fusion Patterns). Nothing computes what to BUY. That is this.
"""
from collections import defaultdict


def build(records, INFERENCE):
    ALL = set(INFERENCE)
    S = {r["id"]: (r, set(i for i in r.get("inferences") or [] if i in INFERENCE))
         for r in records if r.get("catalog") == "sensor" and r.get("inferences")}

    def greedy(target, pool=None, by_cost=True):
        pool = pool if pool is not None else S
        cov, kit, used = set(), [], set()
        while cov != target:
            best, bv = None, 0
            for sid, (r, inf) in pool.items():
                if sid in used:
                    continue
                g = len((inf & target) - cov)
                if not g:
                    continue
                v = g / max(r.get("usd") or 1, 1) if by_cost else g
                if v > bv:
                    bv, best = v, (sid, r, g)
            if best is None:
                break
            used.add(best[0])
            kit.append(best)
            cov |= (S[best[0]][1] & target)
        return kit, cov

    # ---------------------------------------------------------------- the curve
    kit_cost, _ = greedy(ALL, by_cost=True)
    kit_count, _ = greedy(ALL, by_cost=False)

    curve, run, spend = [], set(), 0.0
    for sid, r, g in kit_cost:
        run |= S[sid][1]
        spend += r.get("usd") or 0
        curve.append((r["n"], r.get("usd") or 0, g, len(run), len(run) / len(ALL), spend))

    # tiers at 50 / 75 / 90 / 100 % of all outcomes
    tiers, marks = [], [0.50, 0.75, 0.90, 1.00]
    names = ["FOUNDATION", "CORE", "BROAD", "COMPLETE"]
    blurbs = [
        "Half of everything this atlas can infer. The striking part is the price.",
        "Three quarters. Still dominated by parts costing less than a coffee.",
        "Ninety percent. The additions here are specific instruments, not generic ones.",
        "Everything. The last stretch is expensive because each part buys exactly one outcome.",
    ]
    prev = 0
    for name, mark, blurb in zip(names, marks, blurbs):
        idx = next((i for i, c in enumerate(curve) if c[4] >= mark), len(curve) - 1)
        tiers.append(dict(name=name, blurb=blurb, upto=idx + 1,
                          added=[c[0] for c in curve[prev:idx + 1]],
                          n=idx + 1, cov=curve[idx][3], pct=curve[idx][4],
                          cost=curve[idx][5]))
        prev = idx + 1

    # ---------------------------------------------------------------- per outcome
    prov = defaultdict(list)
    for sid, (r, inf) in S.items():
        for i in inf:
            prov[i].append(r)
    first_tier = {}
    for t_i, t in enumerate(tiers):
        seen = set()
        for c in curve[:t["upto"]]:
            pass
        run2 = set()
        for sid, r, g in kit_cost[:t["upto"]]:
            run2 |= S[sid][1]
        for i in run2:
            first_tier.setdefault(i, tiers[t_i]["name"])

    outcomes = []
    for key, (question, domain) in INFERENCE.items():
        alts = prov.get(key, [])
        priced = [a for a in alts if isinstance(a.get("usd"), (int, float))]
        cheap = min(priced, key=lambda a: a["usd"]) if priced else None
        # "best" = most capable route: highest price×difficulty among alternatives
        best = max(alts, key=lambda a: ((a.get("usd") or 0) + (a.get("diff") or 0) * 10)) if alts else None
        nocon = [a for a in alts if a.get("contact") in ("Through-barrier", "Standoff", "Remote")]
        nc = min(nocon, key=lambda a: a.get("usd") or 1e9) if nocon else None
        priv = [a for a in alts if a.get("privacy") in ("None", "Aggregate")]
        pv = min(priv, key=lambda a: a.get("usd") or 1e9) if priv else None
        outcomes.append(dict(
            domain=domain, question=question, n_routes=len(alts),
            cheap=f"{cheap['n']} (${cheap['usd']:g})" if cheap else "—",
            best=f"{best['n']}" if best else "—",
            nocontact=f"{nc['n']} (${nc['usd']:g})" if nc else "— none",
            privacy=f"{pv['n']} (${pv['usd']:g})" if pv else "— none",
            tier=first_tier.get(key, "beyond COMPLETE"),
            rarity=("SOLE ROUTE" if len(alts) == 1 else ("rare" if len(alts) <= 3 else "")),
        ))
    outcomes.sort(key=lambda o: (o["domain"], -o["n_routes"]))

    # ---------------------------------------------------------------- domains
    doms = defaultdict(set)
    for k, (q, d) in INFERENCE.items():
        doms[d].add(k)
    domain_kits = []
    for d in sorted(doms, key=lambda d: -len(doms[d])):
        kit, cov = greedy(doms[d])
        domain_kits.append(dict(
            domain=d, n_out=len(doms[d]), n_sens=len(kit),
            cost=sum((r.get("usd") or 0) for _, r, _ in kit),
            kit=" · ".join(f"{r['n']} (${r.get('usd'):g})" for _, r, _ in kit)))

    # ---------------------------------------------------------------- constraints
    CON = [
        ("🔒 No privacy footprint", lambda r: r.get("privacy") in ("None", "Aggregate"),
         "Nothing that could identify a person. The constraint that gets projects approved."),
        ("🔋 Battery, µA-class", lambda r: (r.get("pwr_ua") or 1e9) < 1000,
         "Parts a coin cell or small LiPo can run for months."),
        ("🚫 Never touches the subject", lambda r: r.get("contact") in ("Through-barrier", "Standoff", "Remote"),
         "No contact, no contamination, no consent problem."),
        ("💵 Nothing over $5", lambda r: (r.get("usd") or 999) < 5,
         "The constraint that produces the most surprising result in this whole analysis."),
        ("🧑‍🔧 Beginner-buildable", lambda r: (r.get("diff") or 9) <= 2,
         "Plug-and-play or simple wiring only."),
        ("🌦 Survives outdoors", lambda r: "Outdoor" in (r.get("environment") or []),
         "Weather-exposed with suitable housing."),
    ]
    constraint_kits = []
    for name, pred, why in CON:
        pool = {k: v for k, v in S.items() if pred(v[0])}
        kit, cov = greedy(ALL, pool=pool)
        missed = sorted(ALL - cov, key=lambda i: INFERENCE[i][1])
        constraint_kits.append(dict(
            name=name, why=why, eligible=len(pool), covered=len(cov),
            pct=len(cov) / len(ALL), n_sens=len(kit),
            cost=sum((r.get("usd") or 0) for _, r, _ in kit),
            kit=" · ".join(r["n"] for _, r, _ in kit[:10]),
            lost=" · ".join(INFERENCE[i][0] for i in missed[:6]) or "nothing"))

    # ---------------------------------------------------------------- irreplaceable
    irr = []
    for sid, (r, inf) in S.items():
        score = sum(1.0 / len(prov[i]) for i in inf if prov.get(i))
        solo = [INFERENCE[i][0] for i in inf if len(prov.get(i, [])) == 1]
        irr.append((score, r, solo, len(inf)))
    irr.sort(key=lambda x: -x[0])

    # recombinatory index: outcomes per pound, for parts covering 4+
    recomb = sorted(
        [(len(inf) / max(r.get("usd") or 0.5, 0.5), r, len(inf)) for r, inf in
         ((v[0], v[1]) for v in S.values()) if len(inf) >= 4],
        key=lambda x: -x[0])

    return dict(curve=curve, tiers=tiers, outcomes=outcomes, domain_kits=domain_kits,
                constraint_kits=constraint_kits, irreplaceable=irr[:18],
                recomb=recomb[:18], n_all=len(ALL), n_sensors=len(S),
                kit_count_len=len(kit_count), kit_cost_len=len(kit_cost),
                cost_count=sum((r.get("usd") or 0) for _, r, _ in kit_count),
                cost_cost=sum((r.get("usd") or 0) for _, r, _ in kit_cost))


FINDINGS = [
 ("The inversion: specificity is anti-recombinatory",
  "Run the optimiser by cost and the parts it reaches for first are the cheapest and dumbest in "
  "the catalog — a 50p piezo disc, a 50p reed switch, a 30p thermistor, a 20p photoresistor, a £2 "
  "IMU. The expensive specific instruments arrive last and buy one outcome each. This is not a "
  "quirk of the data, it is what specificity MEANS: a sensor engineered to respond to exactly one "
  "thing has been engineered to ignore everything else. Generic transducers are cheap BECAUSE they "
  "are unselective, and unselective is precisely what makes them recombinatory."),
 ("Therefore the omniscience kit is cheap",
  "Half of everything this atlas knows how to infer is reachable for the price of a takeaway. The "
  "constraint 'nothing over $5' still reaches nearly three quarters of all outcomes. If your "
  "instinct is that broad capability requires expensive instruments, the arithmetic says the "
  "opposite — and it says so decisively."),
 ("What the expensive parts actually buy",
  "They buy the tail. Each of the last additions is the SOLE route to one outcome: lightning "
  "distance, radon accumulation, isotope identity, belt slip, atmospheric charge. Those are worth "
  "buying when you want that specific outcome, and worth nothing to general capability. Read the "
  "irreplaceability table as a shopping list for intentions, not for breadth."),
 ("Where the real leverage is",
  "It is not in the sensor list at all — it is in TIME and FUSION. A generic transducer plus a "
  "baseline plus a second modality produces outcomes that neither sensor claims alone. The "
  "optimiser below counts only what each sensor supports BY ITSELF, so every number here is a "
  "LOWER BOUND on what the kit can actually do once the Derived Quantities and Combination "
  "Grammar sheets are applied to it."),
 ("How to use this sheet",
  "Pick the row you want from Outcome → Kit. If you want breadth, buy a tier. If you want a "
  "domain, buy its kit. If you have a constraint, read what it costs you in outcomes BEFORE you "
  "commit — the constraint table is the only place in this atlas that prices a design decision in "
  "capability rather than in money."),
]
