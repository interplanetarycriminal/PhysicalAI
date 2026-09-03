#!/usr/bin/env python3
"""Rank sensor COMBINATIONS — what two or three parts know that neither knows alone.

solve.py answers "what should I buy to cover these outcomes". This answers a
different question: of the 81,810 pairs the catalog can make, which ones are
actually interesting, and WHY — with the evidence attached, so a ranking can be
argued with instead of believed.

    python3 combine.py                          top 30 pairs, as markdown
    python3 combine.py --k 3 --top 20           top triples (candidate-generated)
    python3 combine.py --max-usd 15             nothing over £15 for the pair
    python3 combine.py --esp32-only             only what hangs off one board
    python3 combine.py --unexplored-only        only what the catalog has not paired
    python3 combine.py --modality Acoustic      at least one acoustic member
    python3 combine.py --require condensation-risk    must yield that key
    python3 combine.py --explain S036,S192      the whole evidence dump for one pair
    python3 combine.py --export                 write exports/ for use elsewhere

Every number printed here comes from data/combinatorics.py, which states its own
limits: the ESP32 fit is a heuristic over `iface`/`pins`/`i2c_addr` (the schema
has no bus or ADC-channel fields), and triples are found by candidate generation,
not exhaustive search. Pairs ARE exhaustive.
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))
sys.path.insert(0, str(HERE))

import combinatorics as cmb   # noqa: E402
import fusion                 # noqa: E402
import vocab                  # noqa: E402
from loader import load_all   # noqa: E402

EXPORTS = HERE / "exports"
EXPORT_ROWS = 1000            # rows written to the CSVs unless --top overrides


# --------------------------------------------------------------------- filters

def build_predicate(a):
    tests = []
    if a.modality:
        want = {m.strip().lower() for m in a.modality.split(",")}
        tests.append(lambda recs: any((r.get("modality") or "").lower() in want for r in recs))
    if a.max_usd is not None:
        tests.append(lambda recs: sum(r.get("usd") or 0 for r in recs) <= a.max_usd)
    if not tests:
        return None
    return lambda *recs: all(t(recs) for t in tests)


def build_postfilter(a):
    tests = []
    if a.unexplored_only:
        tests.append(lambda s: s["novelty"] == "unexplored")
    if a.esp32_only:
        tests.append(lambda s: s.get("esp32_verdict") in
                     ("single-board", "single-board-with-caveats"))
    if a.require:
        key = a.require.strip()
        tests.append(lambda s: key in s["joint_reach"])
    if not tests:
        return None
    return lambda s: all(t(s) for t in tests)


def constraint_label(a):
    bits = []
    if a.max_usd is not None:
        bits.append(f"combination under ${a.max_usd:g}")
    if a.modality:
        bits.append(f"at least one {a.modality} member")
    if a.esp32_only:
        bits.append("fits one ESP32 board")
    if a.unexplored_only:
        bits.append("not already paired in the catalog's prose")
    if a.require:
        bits.append(f"must yield `{a.require}`")
    return " + ".join(bits) or "none"


# ---------------------------------------------------------------------- report

def _cell(vals, n=4):
    vals = list(vals)
    if not vals:
        return "—"
    out = ", ".join(f"`{v}`" for v in vals[:n])
    return out + (f" +{len(vals) - n}" if len(vals) > n else "")


def report(rows, k, title, constraints, top, n_considered, elapsed, triples_meta=None):
    L = [f"# {title}", ""]
    L.append(f"- **Search space** — {n_considered:,} "
             + ("combinations, EXHAUSTIVE — every C(405,2) pair" if k == 2
                else "candidates, NOT exhaustive — see the note below"))
    L.append(f"- **Constraints** — {constraints}")
    L.append(f"- **Surviving the filters** — {len(rows):,}")
    L.append(f"- **Scored in** — {elapsed:.1f}s")
    L.append("- **Weights** — " + ", ".join(f"{k2} {v:g}" for k2, v in cmb.WEIGHTS.items()))
    if k == 3 and triples_meta:
        L.append(f"- **! Triples are a heuristic** — {triples_meta['n_candidates']:,} candidates "
                 f"from the top {triples_meta['params']['top_pairs']} pairs extended by every "
                 f"sensor, plus every triple from the {triples_meta['params']['cheap_pool']} "
                 f"parts at or under ${triples_meta['params']['extra_pool_max_usd']:g}. "
                 f"C(405,3) = 11,042,570 was not searched.")
    L.append("- **! Scores are comparable within a k, not across it** — the normalisation "
             "caps are pair-calibrated, so triples saturate more components.")
    if not rows:
        L += ["", "✗ Nothing survived those constraints."]
        return "\n".join(L)

    L += ["", f"## Top {min(top, len(rows))}", "",
          "| # | Score | $ | Parts | Gained (emergent · routes) | Compensation | Shared | τ | New? | ESP32 |",
          "|--:|--:|--:|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows[:top], 1):
        syn = r["synergy"]
        mo = set(syn["multiplicity_only_keys"])
        gained = _cell([k2 for k2 in syn["emergent_keys"] if k2 not in mo], 3)
        routes = _cell([k2 for k2 in syn["new_route_keys"] if k2 not in mo], 2)
        comp = r["compensation"]
        cstr = ("—" if not comp["channels"] else
                "; ".join(f"{c['corrector_id']}→{c['fooled_id']} `{c['interferent']}`"
                          for c in comp["channels"][:2])
                + (f" +{len(comp['channels']) - 2}" if len(comp["channels"]) > 2 else ""))
        d = r["time"]["decades"]
        tau = "unknown" if d is None else f"{d:.1f}dec {r['time']['mode']}"
        mark = {"single-board": "✓", "single-board-with-caveats": "!",
                "needs-glue": "!", "not-single-board": "✗"}.get(r.get("esp32_verdict"), "?")
        L.append(f"| {i} | {r['total']:.3f} | {r['usd']:g} | "
                 + " + ".join(f"{n} `{i2}`" for n, i2 in zip(r["names"], r["ids"]))
                 + f" | {gained} · {routes} | {cstr} | {_cell(r['shared_measurand']['keys'], 3)} "
                 f"| {tau} | {'✓' if r['novelty'] == 'unexplored' else '·'} | "
                 f"{mark} {r.get('esp32_verdict', '')} |")
    return "\n".join(L)


def why(rows, prep, boards, by_id, top):
    """The prose beneath the table: what each row actually claims, and what
    would break it. Regenerated with full evidence — the ranking pass throws
    the snippets away to stay inside memory."""
    L = ["", "## Why — the evidence behind each row", ""]
    for i, r in enumerate(rows[:top], 1):
        s = cmb.score_combo([by_id[x] for x in r["ids"]], prep, boards)
        L.append(f"**{i}. {' + '.join(s['names'])}** — {s['total']:.3f}, ${s['usd']:g}, "
                 f"{s['novelty']}, ESP32 {s['esp32_verdict']}")
        L.append("")
        L.append(f"{s['reasoning']}")
        L.append("")
        for c in s["compensation"]["channels"]:
            L.append(f"- ✓ **{c['corrector']}** measures `{'`, `'.join(c['phenomena'])}`, "
                     f"which corrects **{c['fooled']}** for *{c['interferent_label'].lower()}* — "
                     f"its own `fools` says: “{c['evidence']}”")
        for t in s["time"]["taus"]:
            L.append(f"- τ({t['id']}) = "
                     + (f"{t['tau']:g}s ({t['confidence']}) — {t['basis']}"
                        if t["tau"] is not None else f"unknown — {t['basis']}"))
        if s["synergy"]["multiplicity_only_keys"]:
            L.append("- ! discounted as multiplicity-only (two copies of one part would do "
                     "the same): " + ", ".join(f"`{k}`" for k in
                                               s["synergy"]["multiplicity_only_keys"]))
        for c in s["esp32"]["blockers"]:
            L.append(f"- ✗ {c}")
        for c in s["esp32"]["caveats"] + s["esp32"]["unknowns"]:
            L.append(f"- ! {c}")
        L.append(f"- **Confound** — {s['confound']}")
        L.append("")
    return "\n".join(L)


def explain(ids, prep, boards, by_id):
    missing = [i for i in ids if i not in by_id]
    if missing:
        print(f"✗ unknown sensor id(s): {', '.join(missing)}")
        sys.exit(1)
    recs = [by_id[i] for i in ids]
    s = cmb.score_combo(recs, prep, boards)
    L = [f"# {' + '.join(s['names'])}", "",
         f"`{'` + `'.join(s['ids'])}` · **{s['total']:.4f}** · ${s['usd']:g} · "
         f"{s['novelty']} · max difficulty {s['max_diff']} · privacy {s['privacy']} · "
         f"{s['pwr_ua']:g}µA · hazards {', '.join(s['hazard']) or 'none'}", "",
         s["reasoning"], "",
         "## Score, component by component", "",
         "| Component | Weight | Raw | Normalised | Contribution |",
         "|---|--:|--:|--:|--:|"]
    raws = dict(synergy=s["synergy"]["raw"], compensation=s["compensation"]["raw"],
                shared_measurand=s["shared_measurand"]["raw"],
                failure_independence=s["failure_independence"]["score"],
                time_separation=s["time"]["score"],
                novelty=1.0 if s["novelty"] == "unexplored" else 0.0)
    for k, w in cmb.WEIGHTS.items():
        v = s["components"][k]
        L.append(f"| {k} | {w:g} | {raws[k]:g} | {v:.3f} | {w * v:.4f} |")
    L.append(f"| **total** | | | | **{s['total']:.4f}** |")

    L += ["", "## Synergy — what the pair reaches that no member does", ""]
    if not s["synergy"]["keys"]:
        L.append("Nothing. No fusion edge fires for this combination that does not already "
                 "fire for one of its members alone.")
    for k in s["synergy"]["keys"]:
        kind = "EMERGENT" if k in fusion.EMERGENT else "new route"
        q = (fusion.EMERGENT.get(k) or vocab.INFERENCE.get(k) or ("", ""))[0]
        flag = ""
        if k in s["synergy"]["multiplicity_only_keys"]:
            flag = "  ! multiplicity-only — two copies of one part would do the same"
        elif k in s["synergy"]["multiplicity_assisted_keys"]:
            flag = "  ! partly multiplicity-driven"
        L.append(f"- **{k}** ({kind}) — {q}{flag}")
    if s["synergy"]["edges_fired_jointly"]:
        L += ["", "Fusion edges that need more than one member:", ""]
        for e in fusion.FUSION_EDGES:
            if e["key"] in s["synergy"]["edges_fired_jointly"]:
                L.append(f"- `{e['key']}` **{e['name']}** — requires "
                         + " + ".join(f"{c}×{m}" for c, m in e["requires"])
                         + f" → `{e['provides']}`")
                L.append(f"  - math: {e['math']}")
                L.append(f"  - confound: {e['confound']}")

    L += ["", "## Compensation channels", ""]
    if not s["compensation"]["channels"]:
        L.append("None. No member's extracted interferents are measured by another member.")
    for c in s["compensation"]["channels"]:
        L.append(f"- **{c['corrector']}** (`{c['corrector_id']}`) measures "
                 f"`{'`, `'.join(c['phenomena'])}` → corrects **{c['fooled']}** "
                 f"(`{c['fooled_id']}`) for **{c['interferent_label']}**")
        L.append(f"  - evidence from `{c['fooled_id']}`'s own `fools`: “{c['evidence']}”")
    if s["compensation"]["self_compensated"]:
        L.append(f"- ({s['compensation']['self_compensated']} further channel(s) discarded: "
                 f"the fooled part already measures that interferent itself)")

    L += ["", "## Shared measurand", ""]
    if not s["shared_measurand"]["shared"]:
        L.append("No phenomenon in common.")
    for x in s["shared_measurand"]["shared"]:
        L.append(f"- `{x['phenomenon']}` — {x['a']} ({x['modality_a']}) vs {x['b']} "
                 f"({x['modality_b']}) → **{x['kind']}**, weight {x['weight']:g}")

    L += ["", "## Failure independence", ""]
    for p in s["failure_independence"]["pairs"]:
        L.append(f"- {p['a']} vs {p['b']} — Jaccard distance "
                 f"{p['jaccard_distance'] if p['jaccard_distance'] is not None else 'unknown'}, "
                 f"modality differs: {p['modality_differ']}, contact differs: "
                 f"{p['contact_differ']}")
        if p["shared_interferents"]:
            L.append("  - both fooled by: "
                     + ", ".join(f"`{k}`" for k in p["shared_interferents"]))
    L += ["", "Every interferent extracted, with the prose it came from:", ""]
    for rec in recs:
        L.append(f"- **{rec['n']}** (`{rec['id']}`)")
        found = cmb.extract_interferents(rec)
        if not found:
            L.append("  - none matched")
        for k, snip in sorted(found.items()):
            L.append(f"  - `{k}` — {cmb.INTERFERENTS[k]['label']}"
                     + (f" · measured by `{'`, `'.join(cmb.INTERFERENTS[k]['measured_by'])}`"
                        if cmb.INTERFERENTS[k]["measured_by"] else " · nothing measures this")
                     + f"\n    “{snip}”")

    L += ["", "## Time constants", "",
          f"mode `{s['time']['mode']}` — {s['time']['note']}", ""]
    for t in s["time"]["taus"]:
        L.append(f"- `{t['id']}` τ = "
                 + (f"{t['tau']:g} s (confidence {t['confidence']})" if t["tau"] is not None
                    else "UNKNOWN")
                 + f" — {t['basis']}")
    L.append(f"- separation: "
             + (f"{s['time']['decades']:.2f} decades → component {s['time']['score']:.3f}"
                if s["time"]["decades"] is not None
                else "unknown, scored 0.0 (never a bonus for missing data)"))

    f = s["esp32"]
    L += ["", "## ESP32 single-board fit", "",
          f"**{f['verdict']}** · pin budget {f['pin_budget']} · buses {f['buses']}", ""]
    for d in f["detail"]:
        L.append(f"- `{d['id']}` {d['name']} → {d['iface']} "
                 f"(options {', '.join(d['iface_options'])}, `pins` = {d['pins_field']})")
    for b in f["blockers"]:
        L.append(f"- ✗ {b}")
    for c in f["caveats"]:
        L.append(f"- ! {c}")
    for u in f["unknowns"]:
        L.append(f"- ? {u}")
    for n in f["notes"]:
        L.append(f"- · {n}")
    L.append("- boards that fit: "
             + (", ".join(f"{b['name']} (`{b['id']}`, {b['pins']} pins)"
                          for b in f["boards_that_fit"]) or "none"))

    L += ["", "## Novelty", "", f"**{s['novelty']}**"]
    for e in s["novelty_evidence"]:
        L.append(f"- {e}")
    L += ["", "## Confound", "", s["confound"]]
    return "\n".join(L)


# ---------------------------------------------------------------------- export

def _row(rank, r):
    syn, comp = r["synergy"], r["compensation"]
    return [rank, "|".join(r["ids"]), "|".join(r["names"]), r["usd"], round(r["total"], 5),
            round(syn["raw"], 3), "|".join(syn["emergent_keys"]),
            "|".join(syn["new_route_keys"]), "|".join(r["shared_measurand"]["keys"]),
            "|".join(f"{c['corrector_id']}>{c['fooled_id']}:{c['interferent']}"
                     for c in comp["channels"]),
            r["failure_independence"]["score"],
            "" if r["time"]["decades"] is None else round(r["time"]["decades"], 3),
            r["time"]["mode"], r["novelty"], r.get("esp32_verdict", ""),
            "|".join(r.get("boards_that_fit") or []),
            r.get("reasoning", ""), r.get("confound", "")]


HEADER = ["rank", "ids", "parts", "usd", "total", "synergy", "emergent_keys",
          "new_route_keys", "shared_phenomena", "compensation_channels",
          "failure_independence", "tau_decades", "time_mode", "novelty",
          "esp32_verdict", "boards_that_fit", "reasoning", "confound"]


def export(pairs, triples, meta, prep, boards, by_id, n_rows):
    EXPORTS.mkdir(exist_ok=True)

    def write(name, rows):
        with open(EXPORTS / name, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(HEADER)
            for i, r in enumerate(rows[:n_rows], 1):
                full = cmb.score_combo([by_id[x] for x in r["ids"]], prep, boards)
                r = dict(r, reasoning=full["reasoning"], confound=full["confound"])
                w.writerow(_row(i, r))

    write("combinations_pairs.csv", pairs)
    write("combinations_triples.csv", triples["rows"])

    payload = dict(
        meta=dict(
            source="ESP32 Sensor Universe — combination ranker",
            sensors=meta["n_sensors"], boards=meta["n_boards"],
            pairs_scored=meta["n_pairs"], pairs_exhaustive=True,
            pairs_possible=meta["n_pairs_possible"],
            triples_scored=triples["n_scored"],
            triples_candidates=triples["n_candidates"],
            triples_possible=meta["n_triples_possible"],
            triples_exhaustive=False,
            triple_strategy=cmb.TRIPLE_STRATEGY,
            triple_params=triples["params"],
            csv_rows_written=n_rows,
            seconds=dict(pairs=round(meta["t_pairs"], 2), triples=round(meta["t_triples"], 2)),
            weights=cmb.WEIGHTS, normalisation_caps=cmb.NORM,
            multiplicity_discount=cmb.SYNERGY_MULTIPLICITY_ONLY,
            multiplicity_only_edges=sorted(cmb.MULTIPLICITY_ONLY_EDGES),
            interferents=len(cmb.INTERFERENTS),
            caveats=[
                "Pairs are exhaustive; TRIPLES ARE NOT — see triple_strategy.",
                "Normalisation caps are pair-calibrated, so a triple's total is not "
                "comparable with a pair's. Rank within a k.",
                "The ESP32 verdict is a heuristic over `iface`, `pins` and `i2c_addr`. "
                "The schema has no bus-instance or ADC-channel field, so it can say "
                "'these two collide at 0x76' and cannot say 'this will boot'.",
                "Interferents are regex-extracted from free prose. Every one carries the "
                "matched snippet; read it before trusting the key.",
                "A tau of `unknown` is carried through, never treated as favourable.",
            ]),
        interferent_lexicon={k: dict(label=v["label"], measured_by=v["measured_by"],
                                     patterns=v["patterns"])
                             for k, v in cmb.INTERFERENTS.items()},
        pairs=[_dictrow(r) for r in pairs[:n_rows]],
        triples=[_dictrow(r) for r in triples["rows"][:n_rows]],
    )
    (EXPORTS / "combinations_run.json").write_text(
        json.dumps(payload, indent=1, ensure_ascii=False))
    return ["combinations_pairs.csv", "combinations_triples.csv", "combinations_run.json"]


def _dictrow(r):
    return dict(ids=r["ids"], parts=r["names"], usd=r["usd"], total=r["total"],
                components=r["components"], synergy=r["synergy"],
                compensation=r["compensation"],
                shared_measurand=r["shared_measurand"],
                failure_independence=r["failure_independence"], time=r["time"],
                novelty=r["novelty"], esp32_verdict=r.get("esp32_verdict"),
                boards_that_fit=r.get("boards_that_fit"), max_diff=r["max_diff"],
                hazard=r["hazard"], privacy=r["privacy"], pwr_ua=r["pwr_ua"],
                per_dollar=r["per_dollar"])


# ------------------------------------------------------------------------ main

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--k", type=int, choices=[2, 3], default=2,
                   help="combination size (2 = exhaustive, 3 = candidate-generated)")
    p.add_argument("--top", type=int, help="how many rows to print (default 30)")
    p.add_argument("--max-usd", type=float, help="cap the COMBINATION's total price")
    p.add_argument("--esp32-only", action="store_true",
                   help="only combinations that hang off one ESP32 board")
    p.add_argument("--unexplored-only", action="store_true",
                   help="only combinations the catalog's own prose does not already pair")
    p.add_argument("--modality", help="require at least one member of this modality")
    p.add_argument("--require", help="combination must yield this inference/emergent key")
    p.add_argument("--explain", help="ID1,ID2[,ID3] — the full evidence dump for one "
                                     "combination, and the audit path for any ranked row")
    p.add_argument("--no-why", action="store_true", help="table only, skip the evidence prose")
    p.add_argument("--export", action="store_true", help="write exports/ and exit")
    p.add_argument("--json", action="store_true", help="emit this run as JSON")
    a = p.parse_args()

    records, _ = load_all(persist_ids=False)
    sensors = [r for r in records if r.get("catalog") == "sensor"]
    boards = [r for r in records if r.get("catalog") == "board"]
    by_id = {r["id"]: r for r in sensors}
    prep = cmb.prepare(sensors)

    if a.explain:
        print(explain([x.strip() for x in a.explain.split(",") if x.strip()],
                      prep, boards, by_id))
        return

    pred, post = build_predicate(a), build_postfilter(a)
    n_pairs_possible = len(sensors) * (len(sensors) - 1) // 2
    n_triples_possible = n_pairs_possible * (len(sensors) - 2) // 3

    t0 = time.time()
    pairs = cmb.rank_pairs(sensors, prep, boards, predicate=pred, postfilter=post)
    t_pairs = time.time() - t0

    triples, t_triples = None, 0.0
    if a.k == 3 or a.export:
        base = (pairs if not (pred or post)
                else cmb.rank_pairs(sensors, prep, boards, keep=1000))
        t1 = time.time()
        triples = cmb.rank_triples(sensors, base, prep, boards,
                                   predicate=pred, postfilter=post)
        t_triples = time.time() - t1

    meta = dict(n_sensors=len(sensors), n_boards=len(boards), n_pairs=len(pairs),
                n_pairs_possible=n_pairs_possible, n_triples_possible=n_triples_possible,
                t_pairs=t_pairs, t_triples=t_triples)

    if a.export:
        n_rows = a.top or EXPORT_ROWS
        names = export(pairs, triples, meta, prep, boards, by_id, n_rows)
        print(f"exports/ written — {len(names)} files ({n_rows} rows each)")
        for n in names:
            print(f"  {n:<28} {(EXPORTS / n).stat().st_size:>10,} bytes")
        return

    rows = pairs if a.k == 2 else triples["rows"]
    top = a.top or 30
    if a.json:
        print(json.dumps(dict(meta=meta, weights=cmb.WEIGHTS, norm=cmb.NORM,
                              rows=[_dictrow(r) for r in rows[:top]]),
                         indent=1, ensure_ascii=False))
        return

    considered = n_pairs_possible if a.k == 2 else triples["n_candidates"]
    print(report(rows, a.k,
                 f"Combination ranker — {'pairs' if a.k == 2 else 'triples'}",
                 constraint_label(a), top, considered,
                 t_pairs if a.k == 2 else t_triples,
                 triples if a.k == 3 else None))
    if not a.no_why and rows:
        print(why(rows, prep, boards, by_id, min(top, 12)))


if __name__ == "__main__":
    main()
