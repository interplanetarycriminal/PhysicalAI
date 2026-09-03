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
import re
import time
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


# ---------------------------------------------------------------- wiring model
# A SET is not the sum of its parts. Two I2C sensors do not cost four GPIO
# lines, they cost two, because the bus is shared. Everything below models that,
# because "outcomes per pin" rewards exactly the wrong sets if the pin count is
# the naive sum.

# Shared buses: (lines the FIRST device on the bus costs, lines each EXTRA one
# costs). SPI is three shared lines plus one chip-select per device.
SHARED_BUS = {"I2C": (2, 0), "SPI": (3, 1), "1-Wire": (1, 0), "I2S": (3, 0)}

# Charged per device, no shared setup — there is no UART fabric to share.
PER_DEVICE_BUS = {"UART": 2}

# An ESP32 has three hardware UARTs and the console normally eats one.
MAX_UART_DEVICES = 2

# A plausible GPIO budget for one board, and for one part inside a set.
GPIO_BUDGET = 26
MAX_PART_PINS = 12

# `esp32_compat` is prose, so it is mined for FLAGS and never for arithmetic.
# (key, exclusive, note, keywords). `exclusive` means the ESP32 has exactly one
# of the resource, so two members both wanting it makes the set unbuildable.
ESP32_COMPAT_FLAGS = [
    ("camera", True,
     "parallel camera interface, of which an ESP32 has one",
     ("camera interface", "parallel camera", "dvp", "esp32-cam", "camera bus")),
    ("adc2-wifi", False,
     "ADC1 only — ADC2 is dead while Wi-Fi is running",
     ("adc2",)),
    ("psram", False,
     "PSRAM wanted — an S3 or WROVER variant, not a plain ESP32",
     ("psram",)),
    ("touch-pin", False,
     "a capacitive touch channel is consumed",
     ("touch pin", "touch-pin", "touch pad", "touch channel")),
    ("level-shift", False,
     "a level translator is needed — not a 3.3V-native signal",
     ("level shift", "level-shift", "level translator", "not 5v tolerant",
      "5v-tolerant")),
    ("dac", False,
     "a true DAC pin is needed, and the original ESP32 has two",
     ("dac",)),
]

# Phrasing that means the catalog itself says the part does not work here.
ESP32_UNUSABLE = ("not compatible", "won't work", "will not work", "incompatible")

# Free-text i2c_addr mining. The repo's older regex found only "0x[0-9A-Fa-f]{2}",
# which reads '0x18-0x1F via A0/A1/A2' as the two endpoints and silently loses
# the six addresses between them. Ranges are expanded here instead.
I2C_ADDR_RE = re.compile(r"0x([0-9A-Fa-f]{2})")
I2C_RANGE_RE = re.compile(r"0x([0-9A-Fa-f]{2})\s*[-–—]\s*0x([0-9A-Fa-f]{2})")

# Any of these in the address text means the address can be MOVED. The list is
# deliberately generous: calling a rigid part flexible only costs a caveat,
# while calling a flexible part rigid throws away a buildable set.
I2C_FLEX_WORDS = (" or ", "/", "jumper", "selectable", "strap", "addr", "add0",
                  "solder", "reprogram", "eeprom", "resistor", "mux", "default",
                  "pulled", "tied", "variant", "settable", "configurable")


def i2c_addresses(text):
    """Every 7-bit address a part can answer on, and whether it can be moved.

    The addresses matter because two parts stuck on the same one cannot share a
    bus, and that is a hardware fact no coverage score knows about. Ranges are
    expanded rather than read as endpoints, so '0x18-0x1F via A0/A1/A2' yields
    eight addresses and not two.

    text — the record's free-text `i2c_addr` field, or None

    Returns (sorted list of ints, flexible bool).
    """
    t = text or ""
    addrs = set()
    for lo, hi in I2C_RANGE_RE.findall(t):
        a, b = int(lo, 16), int(hi, 16)
        if a <= b and b - a <= 32:
            addrs |= set(range(a, b + 1))
    addrs |= {int(a, 16) for a in I2C_ADDR_RE.findall(t)}
    low = t.lower()
    return sorted(addrs), (len(addrs) > 1 or any(w in low for w in I2C_FLEX_WORDS))


def esp32_unusable(record):
    """True when the record's own prose says it will not work on an ESP32."""
    low = (record.get("esp32_compat") or "").lower()
    return any(w in low for w in ESP32_UNUSABLE)


# The compat prose says "no DAC or touch needed" at least as often as it says a
# part wants one, and a bare substring search reads those two the same way. A
# negator this close in front of a keyword cancels the hit.
NEGATORS = ("no ", "not ", "nothing", "without", "never", "n't", "free of")
NEG_WINDOW = 48


def compat_flags(record):
    """Which ESP32_COMPAT_FLAGS keys this one record trips, by keyword.

    Every hit is checked against the words immediately before it, because the
    catalog states a part's INDIFFERENCE to a resource as often as its need for
    one, and a flag raised on "no DAC or touch involved" is worse than no flag.
    """
    low = (record.get("esp32_compat") or "").lower()
    hit = set()
    for key, _x, _n, words in ESP32_COMPAT_FLAGS:
        for w in words:
            i = low.find(w)
            while i >= 0:
                if not any(g in low[max(0, i - NEG_WINDOW):i] for g in NEGATORS):
                    hit.add(key)
                    break
                i = low.find(w, i + 1)
            if key in hit:
                break
    if "Camera" in (record.get("iface") or []):
        hit.add("camera")
    return hit


_WIRING = {}


def part_wiring(record):
    """Per-part wiring facts, memoised by catalog id.

    The set ranker asks these questions of the same few hundred parts a hundred
    thousand times over, and re-running two regexes and six substring scans each
    time is most of the runtime. Records do not change within a run, so the
    answer is cached against `id`.

    Returns dict(buses, uart, plain, addr, movable, flags).
    """
    w = _WIRING.get(record["id"])
    if w is not None:
        return w
    ifaces = list(record.get("iface") or [])
    plain = [i for i in ifaces if i not in SHARED_BUS and i not in PER_DEVICE_BUS]
    addrs, flexible = i2c_addresses(record.get("i2c_addr"))
    w = dict(
        buses=frozenset(i for i in ifaces if i in SHARED_BUS),
        uart=("UART" in ifaces),
        # the authored fallback, used whenever the part's interface is one this
        # model does not represent (Analog, Digital, Pulse, PWM, CAN, USB...)
        plain=((int(record.get("pins") or 0), plain[0] if plain else "direct")
               if (plain or not ifaces) else None),
        addr=(addrs[0] if "I2C" in ifaces and len(addrs) == 1 else None),
        movable=(flexible or any(i != "I2C" for i in ifaces)),
        flexible=flexible,
        flags=compat_flags(record))
    _WIRING[record["id"]] = w
    return w


def pin_cost(recs, plan=False):
    """GPIO lines one ESP32 actually spends on a SET, not the sum of `pins`.

    Summing the authored per-part `pins` charges the I2C bus once per device,
    which makes an all-I2C set look three times more expensive than it is. Here
    a shared bus is paid once for the set and then per device, and a part
    listing several interfaces takes whichever is cheapest GIVEN what the rest
    of the set has already opened — which is why the choice cannot be made part
    by part. Only the buses some member actually offers are considered, so all
    open/shut combinations are enumerated exactly and the cheapest consistent
    one wins; ties break on bus name then part id, so the answer is
    deterministic.

    recs — catalog records for the whole set
    plan — return the full assignment instead of just the integer

    Returns an int, or dict(pins, buses, assign, uart) when `plan` is set.
    """
    ws = [part_wiring(r) for r in recs]
    present = sorted({b for w in ws for b in w["buses"]})
    best = None
    for mask in range(1 << len(present)):
        opened = [present[i] for i in range(len(present)) if mask >> i & 1]
        total, assign, ok = sum(SHARED_BUS[b][0] for b in opened), [], True
        for r, w in zip(recs, ws):
            opts = [(SHARED_BUS[b][1], b) for b in opened if b in w["buses"]]
            if w["uart"]:
                opts.append((PER_DEVICE_BUS["UART"], "UART"))
            if w["plain"] is not None:
                opts.append(w["plain"])
            if not opts:
                ok = False        # its only bus is shut in this combination
                break
            c, b = min(opts)
            assign.append((r["id"], b))
            total += c
        if not ok:
            continue
        cand = (total, tuple(opened), tuple(sorted(assign)))
        if best is None or cand < best:
            best = cand
    if best is None:                                  # nothing modelled at all
        best = (sum(int(r.get("pins") or 0) for r in recs), (), ())
    if not plan:
        return best[0]
    assign = dict(best[2])
    return dict(pins=best[0], buses=list(best[1]), assign=assign,
                uart=sum(1 for b in assign.values() if b == "UART"))


def group_flags(recs, plan=None):
    """Can this SET actually be built on one ESP32, and what has to be said?

    Coverage says what a set could know; this says whether you can wire it. Two
    rules reject outright — two parts welded to the same I2C address with no
    second bus between them, and two parts each wanting the one exclusive
    resource — because those sets do not exist in hardware. Everything softer
    becomes a caveat, because a false rejection silently deletes a good answer
    while a false caveat only costs a sentence.

    recs — catalog records for the whole set
    plan — a `pin_cost(..., plan=True)` result, if the caller already has one

    Returns (ok bool, notes list of str).
    """
    ok, notes = True, []

    # --- I2C address collisions
    by_addr = defaultdict(list)
    for r in recs:
        w = part_wiring(r)
        if w["addr"] is not None:
            by_addr[w["addr"]].append((r, w))
    for addr, members in sorted(by_addr.items()):
        if len(members) < 2:
            continue
        stuck = [m for m in members if not m[1]["movable"]]
        who = " and ".join(m[0]["n"] for m in members)
        if len(stuck) >= 2:
            ok = False
            notes.append(f"unbuildable — {who} are both fixed at 0x{addr:02x} "
                         f"with no second bus between them")
        else:
            m = [m for m in members if m[1]["movable"]][0]
            how = ("move its address jumper" if m[1]["flexible"]
                   else "put it on its other bus")
            notes.append(f"0x{addr:02x} clash between {who} — {how} for {m[0]['n']}")

    # --- exclusive ESP32 resources
    seen = defaultdict(list)
    for r in recs:
        for k in part_wiring(r)["flags"]:
            seen[k].append(r)
    for key, exclusive, note, _words in ESP32_COMPAT_FLAGS:
        hits = seen.get(key)
        if not hits:
            continue
        who = ", ".join(h["n"] for h in hits)
        if exclusive and len(hits) > 1:
            ok = False
            notes.append(f"unbuildable — two parts want the same single "
                         f"resource ({note}): {who}")
        else:
            notes.append(f"{note} — {who}")

    # --- pin budget
    plan = pin_cost(recs, plan=True) if plan is None else plan
    if plan["uart"] > MAX_UART_DEVICES:
        notes.append(f"{plan['uart']} UART devices — an ESP32 has three hardware "
                     f"UARTs and the console usually takes one")
    if plan["pins"] > GPIO_BUDGET:
        ok = False
        notes.append(f"unbuildable — {plan['pins']} GPIO lines, past the "
                     f"{GPIO_BUDGET}-line budget for one board")
    return ok, notes


def _bus_phrase(plan):
    """'all of it sits on I2C' / 'it spans I2C + UART' — for the prose line."""
    buses = sorted(set(plan["assign"].values()))
    if not buses:
        return "it wires straight to GPIO"
    if len(buses) == 1:
        return f"all of it sits on {buses[0]}"
    return "it spans " + " + ".join(buses)


def _reason(g, plan, by_key):
    """Generate the group's prose FROM its numbers, never from a template bank.

    Every clause has to be recoverable from the group dict, so the sentence
    cannot drift away from the computation the way authored prose does. It
    names the fusion edges the set fires that no member fires alone, the
    emergent keys those edges provide, the solo-versus-together reach, and what
    the thing costs in dollars and pins.
    """
    who = " + ".join(g["names"])
    named = [by_key[k]["name"] for k in g["new_edge_keys"] if k in by_key]
    bits = []
    if named:
        bits.append("fires " + ", ".join(named[:3])
                    + (f" and {len(named) - 3} more" if len(named) > 3 else ""))
    if g["new_emergent_keys"]:
        bits.append("unlocking " + ", ".join(g["new_emergent_keys"][:4]))
    n_new = len(g["new_routes"])
    if n_new:
        bits.append(f"plus {n_new} new route{'s' if n_new != 1 else ''} to "
                    f"outcomes it declares nowhere")
    head = (", ".join(bits) if bits else
            "adds cover without firing anything its members do not fire alone")
    s = (f"{who}: the set {head} — {g['score']} outcomes together against "
         f"{g['solo_best_score']} for its best single member, a lift of "
         f"{g['lift']}. It costs {g['pins']} ESP32 pins and ${g['usd']:g}; "
         f"{_bus_phrase(plan)}.")
    if g["notes"]:
        s += f" Caveat: {g['notes'][0]}."
    return s


def best_groups(S, edges=None, records=None, min_k=2, max_k=6, max_usd=None,
                beam=30, top=30, cand_cap=120):
    """Rank sensor SETS, not sensors, by what the set knows that no member does.

    Every other ranking in this module scores parts one at a time, which the
    fusion layer itself calls a lower bound. A set is worth more than its
    members when an edge fires across it, and the whole question is which cheap
    sets do that. Exhaustive search dies immediately — 405 choose 6 is about
    7e12 — so pairs are enumerated in FULL and k=3..max_k is a beam search
    seeded from the best pairs. That is a stated DEVIATION from an exact
    answer: a set outside the beam at k=3 can never be found at k=6, so these
    are the best sets FOUND, not proven optima. Breadth is traded for time on
    purpose, and the parameters that set the trade are arguments.

    The beam keeps `beam` survivors under EACH objective rather than one merged
    ranking, so a two-dollar pair and a fifty-dollar six-part set both live to
    the next level instead of the wide sets crowding the cheap ones out. Sets
    are extended only by parts some edge's `requires` actually mentions (plus
    the widest-reaching parts, to keep plain coverage reachable), capped at
    `cand_cap`. Every candidate list is sorted before use and every tie breaks
    on (score desc, usd asc, ids), so a run is reproducible and
    `verify_build.py` can re-derive the top row independently.

    Sets are also checked against the hardware, which is what makes this a
    shopping list rather than an arithmetic exercise: shared buses are paid
    once (`pin_cost`), and I2C address collisions or exclusive ESP32 resources
    reject a set outright (`group_flags`).

    S        — the bipartite index from `index()`: sensor id -> (record, outcomes)
    edges    — fusion edges; defaults to fusion.FUSION_EDGES
    records  — the full catalog, optional; used only to confirm ids resolve
    min_k    — smallest set size to report
    max_k    — largest set size to search
    max_usd  — PER-PART price cap, matching solve.py's --max-usd, not a set total
    beam     — survivors kept per objective at each level
    top      — rows per ranking
    cand_cap — hard cap on the extension candidate pool

    Returns dict(groups, by_score, by_part, by_dollar, by_pin, params).
    """
    t0 = time.time()
    edges = fusion.FUSION_EDGES if edges is None else edges
    by_key = {e["key"]: e for e in edges}
    catalog_ids = {r["id"] for r in records} if records else None

    # ---- the candidate pool: affordable, wireable, and actually in the catalog
    pool = {}
    for sid, (r, inf) in S.items():
        if catalog_ids is not None and sid not in catalog_ids:
            continue
        usd = r.get("usd") if isinstance(r.get("usd"), (int, float)) else 1e9
        if max_usd is not None and usd > max_usd:
            continue
        if int(r.get("pins") or 0) > MAX_PART_PINS or esp32_unusable(r):
            continue
        pool[sid] = (r, inf)

    # ---- what each part reaches on its own, so `lift` means something
    solo = {}
    for sid, (r, inf) in pool.items():
        cl = closure([r], edges)
        solo[sid] = dict(declared=len(inf), score=len(inf) + len(cl["emergent"]),
                         fired=set(cl["fired_keys"]),
                         emergent_keys=set(cl["emergent"]))

    # ---- who can even create emergence: parts an edge's `requires` mentions
    atoms = {c for e in edges for c, _m in e["requires"]}
    order = sorted(pool, key=lambda s: (-solo[s]["score"],
                                        pool[s][0].get("usd") or 0, s))
    ext = [s for s in order if fusion.covers(pool[s][0]) & atoms][:cand_cap]
    for s in order:                       # keep the widest reach in regardless
        if len(ext) >= cand_cap:
            break
        if s not in ext:
            ext.append(s)
    ext = sorted(set(ext), key=lambda s: (-solo[s]["score"],
                                          pool[s][0].get("usd") or 0, s))

    seen, stats = {}, dict(evaluated=0, rejected=0)

    def evaluate(ids):
        """Score one set, or None when the hardware says it cannot be built."""
        fs = frozenset(ids)
        if fs in seen:
            return seen[fs]
        seen[fs] = None
        recs = [pool[s][0] for s in ids]
        plan = pin_cost(recs, plan=True)
        ok, notes = group_flags(recs, plan=plan)
        if not ok:
            stats["rejected"] += 1
            return None
        stats["evaluated"] += 1
        cl = closure(recs, edges)
        declared = set()
        for s in ids:
            declared |= pool[s][1]
        solo_fired = set().union(*(solo[s]["fired"] for s in ids))
        solo_em = set().union(*(solo[s]["emergent_keys"] for s in ids))
        best_solo = max(solo[s]["score"] for s in ids)
        usd = round(sum((pool[s][0].get("usd") or 0) for s in ids), 2)
        score = len(declared) + len(cl["emergent"])
        g = dict(
            ids=sorted(ids), names=[pool[s][0]["n"] for s in sorted(ids)],
            n_parts=len(ids), usd=usd, pins=plan["pins"], buses=plan["buses"],
            declared=len(declared), emergent=len(cl["emergent"]),
            emergent_keys=list(cl["emergent"]),
            new_emergent_keys=sorted(set(cl["emergent"]) - solo_em),
            new_routes=list(cl["new_routes"]),
            fired_keys=list(cl["fired_keys"]),
            new_edge_keys=sorted(set(cl["fired_keys"]) - solo_fired),
            score=score,
            solo_best=max(solo[s]["declared"] for s in ids),
            solo_best_score=best_solo, lift=score - best_solo,
            per_part=round(score / len(ids), 3),
            per_dollar=round(score / max(usd, 0.5), 3),
            per_pin=round(score / max(plan["pins"], 1), 3),
            notes=notes)
        g["reasoning"] = _reason(g, plan, by_key)
        seen[fs] = g
        return g

    OBJ = (("by_score", "score"), ("by_part", "per_part"),
           ("by_dollar", "per_dollar"), ("by_pin", "per_pin"))

    def rank(gs, field, n):
        return sorted(gs, key=lambda g: (-g[field], g["usd"], g["ids"]))[:n]

    def survivors(gs):
        """Union of the top `beam` under each objective — see the docstring."""
        keep = {}
        for _name, field in OBJ:
            for g in rank(gs, field, beam):
                keep[tuple(g["ids"])] = g
        return [keep[k] for k in sorted(keep)]

    # ---- k = 2, exhaustive: 405 parts is 81,810 pairs, which is affordable
    ids = sorted(pool)
    level = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            g = evaluate((a, b))
            if g is not None:
                level.append(g)
    found = {tuple(g["ids"]): g for g in level} if min_k <= 2 else {}

    # ---- k = 3..max_k, beam search over the extension pool
    for k in range(3, max_k + 1):
        nxt = {}
        for g in survivors(level):
            have = set(g["ids"])
            for s in ext:
                if s in have:
                    continue
                ng = evaluate(tuple(sorted(have | {s})))
                if ng is not None:
                    nxt[tuple(ng["ids"])] = ng
        if not nxt:
            break
        level = list(nxt.values())
        if k >= min_k:
            found.update(nxt)

    all_found = list(found.values())
    out = dict(params=dict(min_k=min_k, max_k=max_k, max_usd=max_usd, beam=beam,
                           top=top, cand_cap=cand_cap, pool=len(pool),
                           extension_pool=len(ext), searched=len(seen),
                           evaluated=stats["evaluated"],
                           rejected=stats["rejected"], n_edges=len(edges)))
    union = {}
    for name, field in OBJ:
        out[name] = rank(all_found, field, top)
        for g in out[name]:
            union[tuple(g["ids"])] = g
    out["groups"] = sorted(union.values(),
                           key=lambda g: (-g["score"], g["usd"], g["ids"]))
    out["params"]["seconds"] = round(time.time() - t0, 2)
    return out


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

    # ---------------------------------------------------------------- groups
    # Everything above ranks parts. This ranks SETS, which is the only place the
    # fusion edges can actually pay out, and it prices each set in pins as well
    # as dollars because a set that will not fit on the board is not an answer.
    groups = None
    if fusion is not None:
        groups = best_groups(S, records=records)

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
                fusion=fus, groups=groups, budget_frontier=budget_frontier,
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
