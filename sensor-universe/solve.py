#!/usr/bin/env python3
"""Run the Outcome Solver standalone — no Excel, no workbook, no build step.

The workbook shows you ONE run: all 151 outcomes, cost-optimal. That run is the
interesting one, but it is not the only question you will ever ask. This is the
same optimiser exposed as a tool, so you can point it at any subset of outcomes
under any constraint and get the kit that buys them.

    python3 solve.py                            the canonical run, as markdown
    python3 solve.py --list                      every outcome key, by domain
    python3 solve.py --domain Energy,Water       solve two domains
    python3 solve.py --want water-leak,intrusion solve named outcomes
    python3 solve.py --max-usd 5                 cheapest parts only
    python3 solve.py --privacy-safe --no-contact stack constraints
    python3 solve.py --by count                  fewest PARTS instead of cheapest
    python3 solve.py --groups                    rank sensor SETS, not sensors
    python3 solve.py --export                    write exports/ for use elsewhere

--export is the answer to "how do I serve this context elsewhere": it writes the
whole run, and the graph it was computed from, as JSON, CSV and Markdown that
nothing needs Excel to read.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))
sys.path.insert(0, str(HERE))

import outcome_solver as osv   # noqa: E402
import vocab                   # noqa: E402
from loader import load_all    # noqa: E402

EXPORTS = HERE / "exports"


# --------------------------------------------------------------------- filters

def build_predicate(a):
    tests = []
    if a.max_usd is not None:
        tests.append(lambda r: (r.get("usd") if isinstance(r.get("usd"), (int, float)) else 1e9) <= a.max_usd)
    if a.privacy_safe:
        tests.append(lambda r: r.get("privacy") in ("None", "Aggregate"))
    if a.no_contact:
        tests.append(lambda r: r.get("contact") in ("Through-barrier", "Standoff", "Remote"))
    if a.battery:
        tests.append(lambda r: (r.get("pwr_ua") or 1e9) < 1000)
    if a.beginner:
        tests.append(lambda r: (r.get("diff") or 9) <= 2)
    if a.outdoor:
        tests.append(lambda r: "Outdoor" in (r.get("environment") or []))
    if not tests:
        return None
    return lambda r: all(t(r) for t in tests)


def constraint_label(a):
    bits = []
    if a.max_usd is not None:
        bits.append(f"nothing over ${a.max_usd:g}")
    if a.privacy_safe:
        bits.append("no privacy footprint")
    if a.no_contact:
        bits.append("never touches the subject")
    if a.battery:
        bits.append("battery, µA-class")
    if a.beginner:
        bits.append("beginner-buildable")
    if a.outdoor:
        bits.append("survives outdoors")
    return " + ".join(bits) or "none"


# ---------------------------------------------------------------------- report

def report(res, INFERENCE, title, constraints, by):
    L = [f"# {title}", ""]
    L.append(f"- **Outcomes targeted** — {len(res['target'])}")
    L.append(f"- **Objective** — {'outcomes per pound' if by == 'cost' else 'outcomes per part'}")
    L.append(f"- **Constraints** — {constraints}")
    L.append(f"- **Result** — {res['n_sensors']} sensors, ${res['cost']:.2f}, "
             f"covering {len(res['covered'])}/{len(res['target'])} ({res['pct']*100:.0f}%)")
    if res["unknown"]:
        L.append(f"- **Unknown keys ignored** — {', '.join(res['unknown'])}")
    L += ["", "## The run, step by step", "",
          "| # | Sensor | $ | Buys | Total | % | Cum $ | What this step bought |",
          "|--:|---|--:|--:|--:|--:|--:|---|"]
    for s in res["trace"]:
        L.append(f"| {s['rank']} | {s['name']} | {s['usd']:g} | +{s['gain']} | {s['cum']} | "
                 f"{s['pct']*100:.0f}% | {s['cum_cost']:.2f} | " +
                 "; ".join(s["bought"]) + " |")
    if res["missed"]:
        L += ["", f"## Unreachable under these constraints ({len(res['missed'])})", ""]
        for k in res["missed"]:
            L.append(f"- {INFERENCE[k][0]}  `{k}`")
    return "\n".join(L)


# ---------------------------------------------------------------------- groups

# The four rankings best_groups() returns, and the CSV's `objective` label for
# each. Kept here because export() and --groups must write the same file.
GROUP_RANKINGS = (("by_score", "score", "Score"),
                  ("by_part", "per_part", "Outcomes per part"),
                  ("by_dollar", "per_dollar", "Outcomes per dollar"),
                  ("by_pin", "per_pin", "Outcomes per pin"))

GROUP_COLS = ["rank", "objective", "sensor_ids", "sensors", "n_parts", "usd", "pins",
              "declared", "emergent", "score", "lift", "per_part", "per_dollar",
              "per_pin", "emergent_keys", "new_routes", "fired_edges", "notes",
              "reasoning"]


def write_groups(groups, path):
    """Write every ranking to one CSV, in rank order. Returns the row count."""
    rows = 0
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(GROUP_COLS)
        for name, obj, _label in GROUP_RANKINGS:
            for i, g in enumerate(groups[name], 1):
                w.writerow([i, obj, "|".join(g["ids"]), "|".join(g["names"]),
                            g["n_parts"], g["usd"], g["pins"], g["declared"],
                            g["emergent"], g["score"], g["lift"], g["per_part"],
                            g["per_dollar"], g["per_pin"],
                            "|".join(g["emergent_keys"]), "|".join(g["new_routes"]),
                            "|".join(g["fired_keys"]), "|".join(g["notes"]),
                            g["reasoning"]])
                rows += 1
    return rows


def groups_report(groups, title):
    """The three set rankings as markdown: per part, per dollar, per pin."""
    p = groups["params"]
    cap = f"${p['max_usd']:g} per part" if p["max_usd"] is not None else "none"
    L = [f"# {title}", "",
         f"- **Pool** — {p['pool']} sensors, price cap {cap}",
         f"- **Set size** — {p['min_k']} to {p['max_k']} parts",
         f"- **Searched** — {p['searched']:,} sets, {p['rejected']} rejected as "
         f"unbuildable on one ESP32",
         f"- **Method** — pairs exhaustive; k≥3 is a beam search (beam {p['beam']}, "
         f"extension pool {p['extension_pool']}), so these are the best sets FOUND, "
         f"not proven optima",
         f"- **Elapsed** — {p['seconds']}s", ""]
    for name, obj, label in GROUP_RANKINGS[1:]:
        L += ["", f"## Best sets by {label.lower()}", "",
              f"| # | Set | Parts | $ | Pins | Declared | +Emergent | Score | Lift | "
              f"{label} | What only the set reaches |",
              "|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|---|"]
        for i, g in enumerate(groups[name][:15], 1):
            L.append(f"| {i} | {' + '.join(g['names'])} | {g['n_parts']} | "
                     f"${g['usd']:g} | {g['pins']} | {g['declared']} | "
                     f"+{g['emergent']} | **{g['score']}** | +{g['lift']} | "
                     f"{g[obj]:g} | {', '.join(g['new_emergent_keys']) or '—'} |")
    L += ["", "", "## Why these sets, in words", ""]
    for g in groups["groups"][:8]:
        L.append(f"- {g['reasoning']}")
    return "\n".join(L)


# ---------------------------------------------------------------------- export

def export(records, INFERENCE, sol):
    EXPORTS.mkdir(exist_ok=True)

    # 1 · the whole run, machine-readable
    payload = dict(
        meta=dict(
            source="ESP32 Sensor Universe — Outcome Solver",
            sensors=sol["n_sensors"], outcomes=sol["n_all"], edges=sol["edges"],
            algorithm="greedy maximum coverage",
            guarantee="within (1 - 1/e) ~= 63% of optimal; no polynomial algorithm does better",
            objectives=dict(
                by_cost=dict(sensors=sol["kit_cost_len"], usd=round(sol["cost_cost"], 2)),
                by_count=dict(sensors=sol["kit_count_len"], usd=round(sol["cost_count"], 2))),
        ),
        findings=[dict(title=t, text=x) for t, x in osv.FINDINGS],
        tiers=sol["tiers"],
        trace_by_cost=sol["trace_cost"],
        trace_by_count=sol["trace_count"],
        outcomes=sol["outcomes"],
        domain_kits=sol["domain_kits"],
        constraint_kits=sol["constraint_kits"],
        irreplaceable=sol["irreplaceable_full"],
        recombinatory=sol["recomb_full"],
        graph=sol["graph"],
        budget_frontier=sol["budget_frontier"],
        minimisation=dict(cost_notes=sol["minimise_notes_cost"],
                          count_notes=sol["minimise_notes_count"],
                          minimised_kit=dict(sensors=sol["kit_cost_min_len"],
                                             usd=round(sol["cost_cost_min"], 2))),
        groups=sol.get("groups"),
        fusion=(dict(
            n_edges=sol["fusion"]["n_edges"], n_emergent=sol["fusion"]["n_emergent"],
            tier_closures=sol["fusion"]["tier_closures"],
            marginal=sol["fusion"]["marginal"][:50],
            gaps=sol["fusion"]["gaps"],
        ) if sol.get("fusion") else None),
    )
    (EXPORTS / "solver_run.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False))

    # 2 · the edge list — the solver's actual input, 2401 rows
    with open(EXPORTS / "coverage_edges.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sensor_id", "sensor", "usd", "category", "contact", "privacy",
                    "outcome_key", "outcome_question", "domain"])
        for g in sol["graph"]:
            for k in g["keys"]:
                q, d = INFERENCE[k]
                w.writerow([g["id"], g["name"], g["usd"], g["cat"], g["contact"],
                            g["privacy"], k, q, d])

    # 3 · one row per sensor
    with open(EXPORTS / "sensors_by_reach.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sensor_id", "sensor", "usd", "category", "n_outcomes",
                    "outcomes_per_dollar", "outcome_keys"])
        for g in sol["graph"]:
            usd = g["usd"] if isinstance(g["usd"], (int, float)) else None
            per = round(g["n"] / max(usd or 0.5, 0.5), 2) if usd is not None else ""
            w.writerow([g["id"], g["name"], usd, g["cat"], g["n"], per, "|".join(g["keys"])])

    # 4 · one row per outcome, with EVERY route
    with open(EXPORTS / "outcomes_all_routes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["outcome_key", "domain", "question", "n_routes", "rarity", "first_tier",
                    "cheapest", "most_capable", "no_contact", "privacy_safe", "all_routes"])
        for o in sol["outcomes"]:
            w.writerow([o["key"], o["domain"], o["question"], o["n_routes"], o["rarity"],
                        o["tier"], o["cheap"], o["best"], o["nocontact"], o["privacy"],
                        " | ".join(f"{r['name']} (${r['usd']})" for r in o["routes"])])

    # 5 · the two curves
    with open(EXPORTS / "solver_curve.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["objective", "rank", "sensor_id", "sensor", "usd", "gain",
                    "cumulative_outcomes", "pct", "cumulative_usd", "usd_per_outcome_gained",
                    "outcomes_bought"])
        for obj, tr in (("by_cost", sol["trace_cost"]), ("by_count", sol["trace_count"])):
            for s in tr:
                w.writerow([obj, s["rank"], s["id"], s["name"], s["usd"], s["gain"], s["cum"],
                            round(s["pct"], 4), round(s["cum_cost"], 2),
                            round(s["per_outcome"], 3) if s["per_outcome"] is not None else "",
                            "|".join(s["bought_keys"])])

    # 6 · the fusion layer: edges and the dense capability matrix
    import fusion as fus
    with open(EXPORTS / "fusion_edges.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["key", "name", "pattern", "requires", "provides", "provides_kind",
                    "question", "domain", "math", "why", "confound", "example"])
        for e in fus.FUSION_EDGES:
            kind = "emergent" if e["provides"] in fus.EMERGENT else "route"
            q, d = (fus.EMERGENT.get(e["provides"])
                    or __import__("vocab").INFERENCE.get(e["provides"]))
            w.writerow([e["key"], e["name"], e["pattern"],
                        "|".join(f"{c}×{m}" for c, m in e["requires"]),
                        e["provides"], kind, q, d,
                        e["math"], e["why"], e["confound"], e["example"]])

    caps = fus.matrix_capabilities()
    with open(EXPORTS / "coverage_matrix.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sensor_id", "sensor", "usd"] + [k for k, _kd in caps])
        for r in sorted((x for x in records if x.get("catalog") == "sensor"),
                        key=lambda x: int(x["id"][1:])):
            cov = fus.covers(r)
            w.writerow([r["id"], r["n"], r.get("usd")]
                       + [1 if k in cov else 0 for k, _kd in caps])

    # 7 · the servable narrative
    (EXPORTS / "SOLVER.md").write_text(markdown(sol, INFERENCE))

    # 8 · the ranked sensor SETS — the only export that prices a kit in pins
    if sol.get("groups"):
        write_groups(sol["groups"], EXPORTS / "best_groups.csv")

    return sorted(p.name for p in EXPORTS.iterdir())


def markdown(sol, INFERENCE):
    L = ["# Outcome Solver — the canonical run", "",
         f"**{sol['n_sensors']} sensors · {sol['n_all']} outcomes · {sol['edges']} sensor→outcome "
         f"edges.** This is the Maximum Coverage Problem. Solving it exactly is NP-hard, but "
         f"greedy selection is provably within (1 − 1/e) ≈ 63% of optimal, and it is proven that "
         f"no polynomial-time algorithm beats that bound unless P = NP. Greedy is therefore the "
         f"best available answer, not a shortcut.", "",
         f"- Optimising **outcomes per pound**: {sol['kit_cost_len']} sensors, "
         f"${sol['cost_cost']:.0f}, 100% coverage.",
         f"- Optimising **outcomes per part**: {sol['kit_count_len']} sensors, "
         f"${sol['cost_count']:.0f}, 100% coverage.",
         "", "---", ""]
    for t, x in osv.FINDINGS:
        L += [f"## {t}", "", x, ""]

    L += ["---", "", "## The four kits", "",
          "| Tier | Sensors | Outcomes | % | Cost | What it adds |", "|---|--:|--:|--:|--:|---|"]
    for t in sol["tiers"]:
        L.append(f"| **{t['name']}** | {t['n']} | {t['cov']} | {t['pct']*100:.0f}% | "
                 f"${t['cost']:.0f} | {' · '.join(t['added'])} |")

    L += ["", "## The run, step by step (cost-optimal)", "",
          "| # | Sensor | $ | Buys | Total | % | Cum $ | Outcomes this step bought |",
          "|--:|---|--:|--:|--:|--:|--:|---|"]
    for s in sol["trace_cost"]:
        L.append(f"| {s['rank']} | {s['name']} | {s['usd']:g} | +{s['gain']} | {s['cum']} | "
                 f"{s['pct']*100:.0f}% | {s['cum_cost']:.0f} | {'; '.join(s['bought'])} |")

    L += ["", "## The same problem, fewest PARTS instead of fewest pounds", "",
          f"{sol['kit_count_len']} sensors instead of {sol['kit_cost_len']}, but "
          f"${sol['cost_count']:.0f} instead of ${sol['cost_cost']:.0f}. Optimising for part count "
          f"reaches for capable multi-purpose modules; optimising for cost reaches for dumb cheap "
          f"transducers. Both reach 100%.", "",
          "| # | Sensor | $ | Buys | Total | % | Cum $ |", "|--:|---|--:|--:|--:|--:|--:|"]
    for s in sol["trace_count"]:
        L.append(f"| {s['rank']} | {s['name']} | {s['usd']:g} | +{s['gain']} | {s['cum']} | "
                 f"{s['pct']*100:.0f}% | {s['cum_cost']:.0f} |")

    if sol.get("fusion"):
        import fusion as fus
        f = sol["fusion"]
        L += ["", "## The multiplier — every kit, closed under fusion", "",
              f"The solver's coverage numbers count what each sensor supports alone — a stated "
              f"lower bound. {f['n_edges']} authored fusion edges (from the atlas's Derived "
              f"Quantities, Derived Instruments and Combination Grammar) compute the gap: "
              f"{f['n_emergent']} outcomes exist in no sensor's row, because only combinations "
              f"provide them.", "",
              "| Kit | Parts | Cost | Declared | Edges fired | Emergent | TOTAL |",
              "|---|--:|--:|--:|--:|--:|--:|"]
        for t in f["tier_closures"]:
            L.append(f"| **{t['name']}** | {t['n']} | ${t['cost']:.0f} | {t['declared']} | "
                     f"{t['fired']} | +{t['emergent']} | **{t['total']}** |")
        L += ["", "### Best next purchase for emergence (from FOUNDATION)", "",
              "| Add this | $ | New instruments | Which |", "|---|--:|--:|---|"]
        for m in f["marginal"][:12]:
            L.append(f"| {m['name']} | {m['usd']} | +{m['edges_gained']} | "
                     f"{' · '.join(m['gained_keys'])} |")
        L += ["", "### The instruments", "",
              "| Instrument | Pattern | Requires | Provides | Math |", "|---|---|---|---|---|"]
        for e in fus.topo_edges():
            kind = "NEW" if e["provides"] in fus.EMERGENT else "route"
            needs = " + ".join(f"{'×' + str(m) + ' ' if m > 1 else ''}{c}"
                               for c, m in e["requires"])
            L.append(f"| {e['name']} | {e['pattern']} | {needs} | {kind}: {e['provides']} | "
                     f"{e['math']} |")

    if sol.get("groups"):
        gr = sol["groups"]
        L += ["", "## The most generative SETS", "",
              f"Every ranking above scores parts one at a time. This one scores SETS, "
              f"which is where the fusion edges actually pay out. {gr['params']['searched']:,} "
              f"sets of {gr['params']['min_k']}–{gr['params']['max_k']} parts were searched "
              f"(pairs exhaustively, larger sets by beam search) and priced in ESP32 pins as "
              f"well as dollars, because a shared I2C bus is paid once and a set that will not "
              f"fit on the board is not an answer.", "",
              "| Set | Parts | $ | Pins | Declared | +Emergent | Score | Lift | "
              "What only the set reaches |",
              "|---|--:|--:|--:|--:|--:|--:|--:|---|"]
        for g in gr["groups"][:15]:
            L.append(f"| {' + '.join(g['names'])} | {g['n_parts']} | ${g['usd']:g} | "
                     f"{g['pins']} | {g['declared']} | +{g['emergent']} | "
                     f"**{g['score']}** | +{g['lift']} | "
                     f"{', '.join(g['new_emergent_keys']) or '—'} |")

    L += ["", "## What a fixed budget buys", "",
          "| Budget | Parts | Outcomes | % | Spent |", "|--:|--:|--:|--:|--:|"]
    for b in sol["budget_frontier"]:
        L.append(f"| ${b['budget']} | {b['n_sens']} | {b['covered']} | "
                 f"{b['pct']*100:.0f}% | ${b['spend']:.1f} |")

    L += ["", "## Single-domain kits", "",
          "| Domain | Outcomes | Sensors | Cost | Kit |", "|---|--:|--:|--:|---|"]
    for d in sol["domain_kits"]:
        L.append(f"| {d['domain']} | {d['n_out']} | {d['n_sens']} | ${d['cost']:.0f} | {d['kit']} |")

    L += ["", "## What a constraint costs you, in outcomes", "",
          "| Constraint | Eligible | Reachable | % | Kit cost | Lost entirely |",
          "|---|--:|--:|--:|--:|---|"]
    for c in sol["constraint_kits"]:
        L.append(f"| {c['name']} | {c['eligible']} | {c['covered']}/{sol['n_all']} | "
                 f"{c['pct']*100:.0f}% | {c['n_sens']} parts, ${c['cost']:.0f} | {c['lost']} |")

    L += ["", "## Every outcome, and what buys it", "",
          "| Domain | You want to know… | Routes | Rarity | Cheapest | No-contact | Privacy-safe |",
          "|---|---|--:|---|---|---|---|"]
    for o in sol["outcomes"]:
        L.append(f"| {o['domain']} | {o['question']} | {o['n_routes']} | {o['rarity'] or ''} | "
                 f"{o['cheap']} | {o['nocontact']} | {o['privacy']} |")

    L += ["", "## The two opposite rankings", "",
          "Hubs cover many outcomes and are replaceable. Keys cover few and are the only route. "
          "A good kit needs both, and they anti-correlate.", "",
          "| Irreplaceable (buy for intent) | $ | | Recombinatory (buy for breadth) | $ | per $ |",
          "|---|--:|---|---|--:|--:|"]
    for i in range(max(len(sol["irreplaceable_full"]), len(sol["recomb_full"]))):
        a = sol["irreplaceable_full"][i] if i < len(sol["irreplaceable_full"]) else None
        b = sol["recomb_full"][i] if i < len(sol["recomb_full"]) else None
        note = ""
        if a:
            note = ("SOLE: " + a["sole"][0]) if a["sole"] else "{} outcomes".format(a["n"])
        L.append(f"| {a['name'] if a else ''} | {a['usd'] if a else ''} | {note} | "
                 f"{b['name'] if b else ''} | {b['usd'] if b else ''} | "
                 f"{b['per_dollar'] if b else ''} |")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------ main

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--list", action="store_true", help="print every outcome key by domain")
    p.add_argument("--want", help="comma-separated outcome keys")
    p.add_argument("--domain", help="comma-separated domains")
    p.add_argument("--by", choices=["cost", "count"], default="cost")
    p.add_argument("--max-usd", type=float)
    p.add_argument("--privacy-safe", action="store_true")
    p.add_argument("--no-contact", action="store_true")
    p.add_argument("--battery", action="store_true")
    p.add_argument("--beginner", action="store_true")
    p.add_argument("--outdoor", action="store_true")
    p.add_argument("--budget", type=float,
                   help="hard spend cap: maximise outcomes under $N instead of covering all")
    p.add_argument("--fusion", action="store_true",
                   help="also report which fusion instruments the resulting kit unlocks")
    p.add_argument("--groups", action="store_true",
                   help="rank sensor SETS (2-6 parts) by outcomes per part, "
                        "per dollar and per pin")
    p.add_argument("--k", type=int, default=6, help="largest set size to search")
    p.add_argument("--export", action="store_true", help="write exports/ and exit")
    p.add_argument("--json", action="store_true", help="emit this run as JSON")
    a = p.parse_args()

    records, _ = load_all(persist_ids=False)
    INF = vocab.INFERENCE

    if a.list:
        from collections import defaultdict
        by = defaultdict(list)
        for k, (q, d) in INF.items():
            by[d].append((k, q))
        for d in sorted(by):
            print(f"\n\033[1m{d}\033[0m  ({len(by[d])})")
            for k, q in sorted(by[d]):
                print(f"  {k:<28} {q}")
        return

    if a.export:
        sol = osv.build(records, INF)
        names = export(records, INF, sol)
        print(f"exports/ written — {len(names)} files")
        for n in names:
            print(f"  {n:<26} {(EXPORTS / n).stat().st_size:>9,} bytes")
        return

    if a.groups:
        S = osv.index(records, INF)
        groups = osv.best_groups(S, records=records, max_k=a.k, max_usd=a.max_usd)
        title = f"Sensor SETS — the most generative groupings (up to {a.k} parts)"
        print(groups_report(groups, title))
        EXPORTS.mkdir(exist_ok=True)
        rows = write_groups(groups, EXPORTS / "best_groups.csv")
        print(f"\n_{rows} rows written to exports/best_groups.csv_")
        return

    keys = None
    title = "Outcome Solver — all outcomes"
    if a.want:
        keys = [k.strip() for k in a.want.split(",") if k.strip()]
        title = f"Outcome Solver — {len(keys)} chosen outcomes"
    elif a.domain:
        doms = {d.strip().lower() for d in a.domain.split(",")}
        keys = [k for k, (q, d) in INF.items() if d.lower() in doms]
        title = f"Outcome Solver — {a.domain}"
        if not keys:
            print(f"No outcomes in domain(s) {a.domain}. Domains: "
                  f"{sorted({d for _q, d in INF.values()})}")
            return

    if a.budget is not None:
        S = osv.index(records, INF)
        target = set(keys) if keys else set(INF)
        pred = build_predicate(a)
        pool = {k: v for k, v in S.items() if pred(v[0])} if pred else S
        kit, cov, spend = osv.greedy_budget(S, target, a.budget, pool=pool)
        tr = osv.trace_kit(S, kit, INF, target)
        res = dict(target=sorted(target), unknown=[], trace=tr,
                   covered=sorted(cov), missed=sorted(target - cov),
                   n_sensors=len(kit), cost=spend,
                   pct=len(cov) / max(len(target), 1))
        title += f" — under ${a.budget:g}"
    else:
        res = osv.solve(records, INF, keys=keys, by_cost=(a.by == "cost"),
                        predicate=build_predicate(a))

    if a.json:
        print(json.dumps(res, indent=1, ensure_ascii=False))
    else:
        print(report(res, INF, title, constraint_label(a), a.by))

    if a.fusion:
        import fusion as fus
        by_id = {r["id"]: r for r in records}
        kit_recs = [by_id[s["id"]] for s in res["trace"]]
        cl = osv.closure(kit_recs)
        print(f"\n## Fusion closure of this kit\n")
        print(f"- Instruments unlocked: {len(cl['fired'])} of {len(fus.FUSION_EDGES)}")
        print(f"- Emergent outcomes gained: {len(cl['emergent'])} — "
              + (", ".join(cl["emergent"]) or "none"))
        if cl["new_routes"]:
            print(f"- New routes to declared outcomes: {', '.join(cl['new_routes'])}")
        near = []
        fired = set(cl["fired_keys"])
        granted = {e["provides"] for e in cl["fired"]}
        for e in fus.FUSION_EDGES:
            if e["key"] in fired:
                continue
            missing = [(c, m) for c, m in e["requires"]
                       if cl["counts"].get(c, 0) < m and not (m == 1 and c in granted)]
            if len(missing) == 1:
                c, m = missing[0]
                near.append(f"{e['name']} — needs {('×' + str(m) + ' ') if m > 1 else ''}{c} "
                            f"(have {cl['counts'].get(c, 0)})")
        if near:
            print("- One capability away: " + "; ".join(near[:8]))


if __name__ == "__main__":
    main()
