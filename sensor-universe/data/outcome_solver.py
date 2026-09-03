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
from collections import Counter, defaultdict

try:
    import fusion
except ImportError:          # fusion layer optional — solver still runs without it
    fusion = None


def capability_counts(recs):
    """How many distinct parts in `recs` cover each capability key."""
    counts = Counter()
    for r in recs:
        for c in fusion.covers(r):
            counts[c] += 1
    return counts


def closure(recs, edges=None):
    """Monotone fixpoint over the fusion edges: which derived instruments does
    this set of sensors unlock? A fired edge grants its `provides` key, so
    chained edges (instrument feeding instrument) resolve in <= len(edges)+1
    passes. Returns fired edge keys, the emergent outcomes gained, and the new
    ROUTES (existing inference outcomes reached with none of their direct
    sensors present)."""
    edges = fusion.FUSION_EDGES if edges is None else edges
    counts = capability_counts(recs)
    declared = {i for r in recs for i in r.get("inferences") or []}
    fired, fired_keys, granted = [], set(), set()
    changed = True
    while changed:
        changed = False
        for e in edges:
            if e["key"] in fired_keys:
                continue
            if all(counts.get(c, 0) >= m or (m == 1 and c in granted)
                   for c, m in e["requires"]):
                fired.append(e)
                fired_keys.add(e["key"])
                granted.add(e["provides"])
                changed = True
    return dict(
        fired=fired,
        fired_keys=sorted(fired_keys),
        emergent=sorted({e["provides"] for e in fired
                         if e["provides"] in fusion.EMERGENT}),
        new_routes=sorted({e["provides"] for e in fired
                           if e["provides"] not in fusion.EMERGENT
                           and e["provides"] not in declared}),
        counts=dict(counts))


def minimise(S, kit, target, by_cost=True):
    """Local search on a greedy kit: reverse-delete redundant members (most
    expensive first), then try replacing each member with any single cheaper
    non-member that preserves coverage. Greedy is within (1-1/e) of optimal;
    this closes some of the remaining gap and, when it finds nothing, certifies
    the kit locally minimal under prune and 1-swap. Returns (kit, notes)."""
    notes = []
    kit = list(kit)

    def coverage(members):
        cov = set()
        for sid, _r, _g in members:
            cov |= S[sid][1] & target
        return cov

    full = coverage(kit)

    # reverse-delete: a later pick can make an earlier one redundant
    changed = True
    while changed:
        changed = False
        for cand in sorted(kit, key=lambda k: -(k[1].get("usd") or 0)):
            rest = [k for k in kit if k[0] != cand[0]]
            if coverage(rest) == full:
                kit = rest
                notes.append(f"pruned {cand[1]['n']} (${cand[1].get('usd') or 0:g}) — "
                             "made redundant by later picks")
                changed = True
                break

    # 1-swap: replace any member with a strictly cheaper non-member
    if by_cost:
        member_ids = {sid for sid, _r, _g in kit}
        changed = True
        while changed:
            changed = False
            for i, (sid, r, g) in enumerate(list(kit)):
                rest_cov = coverage([k for k in kit if k[0] != sid])
                needed = full - rest_cov
                price = r.get("usd") or 0
                best = None
                for tid, (tr, tinf) in S.items():
                    if tid in member_ids:
                        continue
                    tprice = tr.get("usd") or 0
                    if tprice >= price:
                        continue
                    if needed <= (tinf & target):
                        if best is None or tprice < (best[1].get("usd") or 0):
                            best = (tid, tr)
                if best is not None:
                    tid, tr = best
                    kit[i] = (tid, tr, g)
                    member_ids.discard(sid)
                    member_ids.add(tid)
                    notes.append(f"swapped {r['n']} (${price:g}) -> {tr['n']} "
                                 f"(${tr.get('usd') or 0:g}), saved "
                                 f"${price - (tr.get('usd') or 0):g}")
                    changed = True
                    break
    return kit, notes


def greedy_budget(S, target, budget, pool=None):
    """Budgeted maximum coverage: cost-benefit greedy under a spend cap,
    compared against the best single affordable sensor — that comparison is
    what carries the 1/2*(1-1/e) guarantee. Returns (kit, covered, spend)."""
    pool = pool if pool is not None else S
    cov, kit, used, spend = set(), [], set(), 0.0
    while True:
        best, bv = None, 0.0
        for sid, (r, inf) in pool.items():
            if sid in used:
                continue
            price = r.get("usd") or 0
            if spend + price > budget:
                continue
            g = len((inf & target) - cov)
            if not g:
                continue
            v = g / max(price, 0.5)
            if v > bv:
                bv, best = v, (sid, r, g)
        if best is None:
            break
        used.add(best[0])
        kit.append(best)
        spend += best[1].get("usd") or 0
        cov |= S[best[0]][1] & target

    # guarantee step: the single best affordable sensor may beat the greedy set
    single, sg = None, 0
    for sid, (r, inf) in pool.items():
        price = r.get("usd") or 0
        if price > budget:
            continue
        g = len(inf & target)
        if g > sg:
            sg, single = g, (sid, r, g)
    if single is not None and sg > len(cov):
        kit = [single]
        cov = S[single[0]][1] & target
        spend = single[1].get("usd") or 0
    return kit, cov, spend


def index(records, INFERENCE):
    """The bipartite graph: sensor id -> (record, set of outcomes it supports)."""
    return {r["id"]: (r, set(i for i in r.get("inferences") or [] if i in INFERENCE))
            for r in records if r.get("catalog") == "sensor" and r.get("inferences")}


def greedy_cover(S, target, pool=None, by_cost=True):
    """Greedy maximum coverage. Returns (kit, covered).

    kit is a list of (sensor_id, record, marginal_gain) in selection order.
    `pool` restricts what may be SELECTED; coverage is always scored against S,
    which is the same set unless a constraint is filtering the pool.
    """
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


def trace_kit(S, kit, INFERENCE, target):
    """Replay a kit step by step, recording exactly which outcomes each step BOUGHT.

    The curve says how many. This says which — which is the difference between a
    summary of a run and the run itself, and it is what makes the result
    auditable by hand and portable to anything that is not Excel.
    """
    out, cov, spend = [], set(), 0.0
    for rank, (sid, r, _g) in enumerate(kit, 1):
        gained = sorted((S[sid][1] & target) - cov)
        cov |= (S[sid][1] & target)
        spend += r.get("usd") or 0
        out.append(dict(
            rank=rank, id=sid, name=r["n"], usd=r.get("usd") or 0,
            cat=r.get("cat", ""), gain=len(gained), cum=len(cov),
            pct=len(cov) / max(len(target), 1), cum_cost=spend,
            bought=[INFERENCE[k][0] for k in gained], bought_keys=gained,
            # what this step cost per outcome it actually bought
            per_outcome=((r.get("usd") or 0) / len(gained)) if gained else None))
    return out


def solve(records, INFERENCE, keys=None, by_cost=True, predicate=None):
    """Run the solver against ANY subset of outcomes. The public entry point.

    keys      — outcome keys you want; None means all of them
    by_cost   — optimise outcomes per pound (True) or per part (False)
    predicate — optional filter over sensor records, e.g. a privacy or budget rule

    Returns dict(target, trace, covered, missed, n_sensors, cost).
    """
    S = index(records, INFERENCE)
    target = set(keys) if keys else set(INFERENCE)
    unknown = sorted(target - set(INFERENCE))
    target &= set(INFERENCE)
    pool = {k: v for k, v in S.items() if predicate(v[0])} if predicate else S
    kit, cov = greedy_cover(S, target, pool=pool, by_cost=by_cost)
    tr = trace_kit(S, kit, INFERENCE, target)
    return dict(target=sorted(target), unknown=unknown, trace=tr,
                covered=sorted(cov), missed=sorted(target - cov),
                n_sensors=len(kit), cost=sum(s["usd"] for s in tr),
                pct=len(cov) / max(len(target), 1))


def build(records, INFERENCE):
    ALL = set(INFERENCE)
    S = index(records, INFERENCE)

    def greedy(target, pool=None, by_cost=True):
        return greedy_cover(S, target, pool=pool, by_cost=by_cost)

    # ---------------------------------------------------------------- the curve
    kit_cost, _ = greedy(ALL, by_cost=True)
    kit_count, _ = greedy(ALL, by_cost=False)

    # local search on the terminal kits (tiers stay raw greedy prefixes — the
    # tier prose depends on each being the previous plus additions)
    kit_cost_min, min_notes_cost = minimise(S, kit_cost, ALL, by_cost=True)
    kit_count_min, min_notes_count = minimise(S, kit_count, ALL, by_cost=False)

    trace_cost = trace_kit(S, kit_cost, INFERENCE, ALL)
    trace_count = trace_kit(S, kit_count, INFERENCE, ALL)

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
            key=key, domain=domain, question=question, n_routes=len(alts),
            routes=[dict(id=a["id"], name=a["n"], usd=a.get("usd"),
                         contact=a.get("contact"), privacy=a.get("privacy"))
                    for a in sorted(alts, key=lambda a: (a.get("usd") if isinstance(a.get("usd"), (int, float)) else 1e9))],
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

    # ---------------------------------------------------------------- raw graph
    # The bipartite graph the solver actually consumes. Publishing it is what
    # makes every number above reproducible somewhere other than this workbook.
    graph = []
    for sid, (r, inf) in sorted(S.items(), key=lambda kv: -len(kv[1][1])):
        graph.append(dict(
            id=sid, name=r["n"], usd=r.get("usd"), cat=r.get("cat", ""),
            contact=r.get("contact"), privacy=r.get("privacy"),
            diff=r.get("diff"), n=len(inf),
            keys=sorted(inf), questions=[INFERENCE[k][0] for k in sorted(inf)]))
    edges = sum(len(g["keys"]) for g in graph)

    # ---------------------------------------------------------------- fusion
    fus = None
    if fusion is not None:
        tier_closures = []
        for t in tiers:
            recs_t = [S[sid][0] for sid, _r, _g in kit_cost[:t["upto"]]]
            cl = closure(recs_t)
            tier_closures.append(dict(
                name=t["name"], n=t["n"], cost=t["cost"], declared=t["cov"],
                fired=len(cl["fired"]), emergent=len(cl["emergent"]),
                new_routes=len(cl["new_routes"]),
                emergent_keys=cl["emergent"], new_route_keys=cl["new_routes"],
                fired_keys=cl["fired_keys"],
                total=t["cov"] + len(cl["emergent"]),
                multiplier=(t["cov"] + len(cl["emergent"])) / t["cov"]))

        # which single added sensor unlocks the most emergence over FOUNDATION?
        found_ids = {sid for sid, _r, _g in kit_cost[:tiers[0]["upto"]]}
        found_recs = [S[sid][0] for sid in found_ids]
        base = closure(found_recs)
        base_fired = set(base["fired_keys"])
        marginal = []
        for sid, (r, _inf) in S.items():
            if sid in found_ids:
                continue
            cl = closure(found_recs + [r])
            gained = [k for k in cl["fired_keys"] if k not in base_fired]
            if gained:
                em_gain = len(set(cl["emergent"]) - set(base["emergent"]))
                marginal.append(dict(id=sid, name=r["n"], usd=r.get("usd"),
                                     edges_gained=len(gained), emergent_gained=em_gain,
                                     gained_keys=gained))
        marginal.sort(key=lambda m: (-m["edges_gained"],
                                     m["usd"] if isinstance(m["usd"], (int, float)) else 1e9))

        full = closure([v[0] for v in S.values()])
        by_key = {e["key"]: e for e in fusion.FUSION_EDGES}
        gaps = []
        for e in fusion.FUSION_EDGES:
            if e["key"] not in set(full["fired_keys"]):
                missing = [(c, m, full["counts"].get(c, 0)) for c, m in e["requires"]
                           if full["counts"].get(c, 0) < m]
                gaps.append(dict(key=e["key"], name=e["name"], missing=missing))

        fus = dict(n_edges=len(fusion.FUSION_EDGES), n_emergent=len(fusion.EMERGENT),
                   tier_closures=tier_closures, marginal=marginal, gaps=gaps,
                   foundation_closure=dict(fired=len(base["fired"]),
                                           emergent=base["emergent"],
                                           new_routes=base["new_routes"]),
                   full_fired=len(full["fired_keys"]))

    # budget frontier: the best reachable at hard spend caps
    budget_frontier = []
    for b in (10, 25, 50, 100, 250):
        kb, cb, sb = greedy_budget(S, ALL, b)
        budget_frontier.append(dict(budget=b, n_sens=len(kb), covered=len(cb),
                                    pct=len(cb) / len(ALL), spend=sb,
                                    kit=" · ".join(r["n"] for _s, r, _g in kb)))

    return dict(curve=curve, tiers=tiers, outcomes=outcomes, domain_kits=domain_kits,
                constraint_kits=constraint_kits, irreplaceable=irr[:18],
                recomb=recomb[:18], n_all=len(ALL), n_sensors=len(S),
                kit_count_len=len(kit_count), kit_cost_len=len(kit_cost),
                cost_count=sum((r.get("usd") or 0) for _, r, _ in kit_count),
                cost_cost=sum((r.get("usd") or 0) for _, r, _ in kit_cost),
                trace_cost=trace_cost, trace_count=trace_count,
                fusion=fus, budget_frontier=budget_frontier,
                minimise_notes_cost=min_notes_cost,
                minimise_notes_count=min_notes_count,
                kit_cost_min_len=len(kit_cost_min),
                cost_cost_min=sum((r.get("usd") or 0) for _, r, _ in kit_cost_min),
                graph=graph, edges=edges,
                irreplaceable_full=[dict(id=r["id"], name=r["n"], usd=r.get("usd"),
                                         score=round(sc, 3), n=n, sole=solo)
                                    for sc, r, solo, n in irr],
                recomb_full=[dict(id=r["id"], name=r["n"], usd=r.get("usd"),
                                  n=n, per_dollar=round(per, 2))
                             for per, r, n in recomb])


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
