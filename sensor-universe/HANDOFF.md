# Handoff plan: enhancing the ESP32 Sensor Universe with a cheaper model

## Context

**The objective of this codebase.** `sensor-universe/` generates an Excel atlas (currently `esp32_sensor_universe_v55.xlsx`, 70 sheets) from a Python data layer: 405 sensors × 36 fields, 151 outcomes ("things you might want to KNOW"), 99 physical phenomena, 52 fusion edges (derived instruments that only combinations of sensors provide), a greedy set-cover solver, and a live Excel Kit Builder. Its purpose is one person's **individual agency to create physical-AI solutions from sensors and physics** — to know what can be sensed, what it costs, what combinations unlock, what fools each route, and when to build versus buy.

**What v55 has and what it still lacks.** v55 answers *what to buy* (solver), *what combinations know* (fusion closure), and *what my kit can do* (Kit Builder). It still does not answer three things the owner explicitly cares about:
1. **Build or buy?** — no sheet prices a DIY instrument against its commercial equivalent and rules on it.
2. **How do I actually build it?** — the fusion instruments have math and confounds but no bench recipe (wiring, firmware steps, calibration, acceptance test).
3. **Which cheap *groupings* are most generative?** — the solver ranks single sensors; nothing ranks pairs/triples by what they unlock together.

Plus known data debt: 126/151 outcomes lack "what fools it" notes; ~100 records imply a hazard they don't declare; 238 legacy sensors carry a prose `spec` instead of structured range/accuracy; 127 vendor SKUs/library names are flagged VERIFY by the audit.

**Why a cheaper model.** Sessions with the expensive model are scarce. Everything below is scoped so a cheaper model can execute it *mechanically against gates*, with invention and physics judgement explicitly reserved. Tasks are tagged **[H]** (Haiku-class: mechanical, fully specified) or **[S]** (Sonnet-class: templated authoring with a validator gate).

---

## Operating rules for the executing model (non-negotiable)

1. **Never invent a vendor SKU, product number, library name, or URL.** If unconfirmed, describe generically ("an ADS1115 breakout") or set `confidence="estimate"`. Unverifiable → remove, never guess.
2. **Safety invariants:** never site a heated MQ/pellistor gas sensor inside a flammable volume; every combustible-gas / fire / life-safety-adjacent entry carries "NOT a life-safety device — supplement, never replace, a certified alarm"; never call an output logic-safe/3.3V-safe when its supply exceeds 3.6 V; medical-adjacent entries are "awareness aids", never devices.
3. **Physics only.** Every number must be checkable (constant, formula, datasheet-class figure). When a formula is uncertain, write `math="VERIFY: …"` rather than a plausible guess — the owner would rather see a gap than a lie.
4. **Derived values are computed, never authored** (prices tiers, BOM totals, closures, coverage). Author only source fields.
5. **IDs are frozen** (`data/ids.json`). Never renumber. **The build is self-hosting:** the upstream v50 upload no longer exists, so `patch_v50.py` starts from the newest committed `esp32_sensor_universe_vNN.xlsx` whose version ≤ `OUT`, deletes the sheets it owns (`OWNED_SHEETS`), and regenerates them; v50's own sheets are patched in place, idempotently. To make v56: bump `OUT`, run the build (it rebases from v55). Never hand-edit a committed workbook. The Corrections Log's v50 history lives in `data/corrections_v50.json`. **Any new sheet you add must be appended to `OWNED_SHEETS`** or the next rebase will duplicate it.
6. **The gate after every change**, in this order — all must pass before a commit:
   ```
   python3 validate.py                        # data contract → exit 0
   python3 patch_v50.py                       # builds OUT (bump OUT per version: v56, v57…)
   python3 verify_build.py <xlsx>             # Task 0 creates this; 22+ structural checks
   python3 audit_workbook.py <xlsx>           # content release gate → MUST exit 0 (0 CRITICAL)
   ```
7. **Excel constraints (openpyxl 3.1.5):** no pivot tables, no sparklines, no `XLOOKUP/FILTER/UNIQUE`; `_xlfn.` prefix for `TEXTJOIN/IFS/SWITCH`; never a native Table + `ws.auto_filter` on one sheet; never merge cells inside a filter/table range or among formula rows; `column_dimensions.group()` before `set_widths`; formula-bearing sheets need ASCII names; formulas are raw `"="` strings and `wb.calculation.fullCalcOnLoad` is already set.
8. **Style:** follow `patch_v50.py`'s `add_*` pattern (`_banner` → `S.section` → hand-rolled header row → data rows; yellow `FFF3C4` = editable, blue `EAF0F6` = computed; tab colours per topic; `freeze_panes` row 4). Helpers live in `sheet_lib.py` (`S.cell`, `S.section`, `S.price_bars`, `S.flag_text`, `S.DataBarRule`, `S.FormulaRule`).
9. **Commit per task** with a descriptive message; push to `claude/tender-euler-1e2bss`. One version bump per phase, not per task.
10. **When a task is ambiguous, do the bounded interpretation and log the ambiguity** in the commit message. Do not widen scope.

### Codebase map (read these first, in this order)
| File | Role |
|---|---|
| `data/schema.py` | The contract: 36 fields, 11 enums (`MODALITY, CONTACT, PRIVACY, POWER_CLASS, ENVIRONMENT, CALIBRATION, LIFECYCLE, HAZARD, CONFIDENCE, MATURITY, INTERFACE`) |
| `data/vocab.py` | Controlled vocabularies: `CATEGORY`(31) `THEME`(16) `PHENOMENON`(99) `INFERENCE`(151: key→(question, domain), 13 domains) `CONSTRAINT`(16) `FUSION`(9 patterns) |
| `data/loader.py` | `load_all()` → (records, seeds). Loads `part1…part13`, other catalogs, applies `enrich_core → enrich → enrich_manual` overlays, migrates categories, assigns IDs, derives `_tier/_power_class` |
| `data/fusion.py` | `EMERGENT`(26) + `FUSION_EDGES`(52) + `matrix_capabilities()`, `covers()`, `topo_edges()`. Edge schema in the module docstring |
| `data/outcome_solver.py` | `index, greedy_cover, trace_kit, solve, closure, minimise, greedy_budget, build` |
| `solve.py` | CLI (`--want/--domain/--by/--budget/--fusion/--max-usd/…/--export`) + `export()` → `exports/` (8 files) |
| `patch_v50.py` | The build: loads v50, corrects 274 catalog cells, appends 167 sensors contiguously, adds 14 sheets, fixes Idea Forge, saves OUT |
| `validate.py` / `audit_workbook.py` | Data gate / content gate (`EXEMPT_SHEETS` for sheets that legitimately discuss hazards) |
| `data/inference_notes.py` | 25/151 outcomes with `{fools, unlocks, market}` |
| `data/seeds.py`, `data/seeds_extra.py` | 88 invention seeds with `sensor_ids` |
| `data/derived_instruments.py` | 14 first-principles instruments (8-tuples; `parts` field is prose) |
| `exports/` | `solver_run.json`, `SOLVER.md`, `coverage_matrix.csv`, `fusion_edges.csv`, … regenerated every build |

---

## Phase 0 — Make the gate portable  [H]  (do first, tiny)

**Task 0.1** Create `sensor-universe/verify_build.py` from the session's scratch checker (`/tmp/claude-0/…/scratchpad/verify_v55.py` if present; otherwise re-implement its checks: zip integrity; sheet count = 56 v50 + N added; no v50 sheet lost; catalog contiguous rows 4–408 and `auto_filter.ref == "$A$3:$V$408"`; Idea Forge has no `$241`/`RANDBETWEEN(1,238)`; Coverage Matrix grid equals `fusion.covers(r) ∩ matrix columns` for all 405 rows and rows align with Kit Builder; every Kit Builder formula range is `8:412`, `5:5`, `6:6`, single-row, or >412; outcome block refs the right column per key; chained edge refs point only to earlier rows; independent closure fixpoint reproduces `sol["fusion"]["tier_closures"]`; `coverage_matrix.csv` equals the grid). Take the xlsx path as argv. Exit 1 on any failure.
**Done when:** `python3 verify_build.py esp32_sensor_universe_v55.xlsx` prints all-pass and exits 0. Commit.

---

## Phase 1 — Build or Buy  [S]  → v56   *(the owner's core question)*

**Why:** "reinvent what needs reinventing, don't reinvent the wheel, affordably" is a *decision*, and nothing in the atlas makes it.

**Task 1.1** Create `data/build_or_buy.py` with `VERDICTS: list[dict]`, one per fusion edge (52) **and** per BUILD/MARGINAL derived instrument (11), schema:
```python
dict(key=<edge key or "di:<slug>">, instrument=<name>,
     commercial_class="<generic description, e.g. 'ultrasonic heat meter, MID-approved'>",
     commercial_price_low=<int USD>, commercial_price_high=<int USD>,
     commercial_confidence="verified"|"high"|"estimate",     # from schema CONFIDENCE
     diy_bom_ids=["S001", ...],          # catalog IDs only; price is COMPUTED from records
     diy_extra_usd=<int>,                # non-catalog parts (wire, wick, enclosure)
     capability_gap="<what the commercial unit does that DIY cannot, or 'none'>",
     verdict="BUY"|"BUILD"|"HYBRID"|"NOTHING-TO-BUY",
     rule="<one sentence: why, citing the price ratio or the gap>")
```
Seed material: v50's *Derived Quantities* col D ("What it beats buying"), *Derived Instruments* col G, and each edge's `example` field. **No brand names in `commercial_class`** unless already present in the catalog text. Prices are tiers with confidence, never quotes.
**Task 1.2** `validate.py`: `validate_build_or_buy()` — every key resolves to an edge or derived instrument; every `diy_bom_ids` entry exists; verdict enum; exactly one verdict per instrument; `commercial_price_low ≤ high`.
**Task 1.3** `patch_v50.py`: `add_build_or_buy(wb, records, sol)` → sheet **"Build or Buy"**: computed DIY cost (`sum(usd for ids) + extra`), commercial range, ratio, gap, verdict badge (BUY blue / BUILD green / HYBRID amber), rule. Summary tiles: count per verdict, total DIY cost of all BUILD verdicts vs their commercial low-bound sum. Sort: BUILD first by ratio desc. Add the sheet to the Kit Builder's fusion block as a 7th column "Verdict" (static text, looked up by edge key).
**Task 1.4** `solve.py --export`: add `exports/build_or_buy.csv`; SOLVER.md section "Build or buy".
**Done when:** gate passes; the sheet shows 63 rows; the headline tile reads e.g. "BUILD ×N saves $X against commercial low-bounds". Commit as v56.

---

## Phase 2 — Build Sheets: from knowing to building  [S]  → v57

**Why:** agency means the bench, not the spreadsheet. Each fusion instrument already has math + confound; it lacks the recipe.

**Task 2.1** Create `data/build_sheets.py`: `RECIPES: dict[edge_key → dict]` for all 52 edges:
```python
dict(bom=["S016", "S007"],                       # catalog IDs; computed cost
     wiring="<bus + pins, pull-ups, level shifting; cite I²C addresses from records>",
     firmware=["step 1 …", "step 2 …"],           # 4–8 numbered algorithm steps that
                                                   # implement the edge's `math` field verbatim
     calibration="<the one procedure that makes it honest>",
     acceptance="<'you know it works when …' — a concrete number/behaviour>",
     log_fields=["t", "T_dew", "T_surface", …],   # what to record, so the temporal edges work
     time_to_first_result="<minutes/hours/days>")
```
Rules: `bom` must satisfy the edge's `requires` under `fusion.covers()` (validator computes this — Task 2.2); wiring must not contradict the parts' `requires` field or `I2C & Wiring Reality` sheet (VL53 family fixed 0x29, 0x68 crowded, pull-ups add up, ADC2 dies with Wi-Fi); firmware steps reference the math symbols by name.
**Task 2.2** `validate.py`: `validate_build_sheets()` — every edge has a recipe; every BOM id exists; `closure(bom_records)` fires that edge (the recipe is *provably sufficient*); no I²C address collision inside a BOM unless `wiring` mentions a multiplexer/XSHUT; `acceptance` non-empty and contains a digit.
**Task 2.3** `patch_v50.py`: `add_build_sheets(wb, …)` → sheet **"Build Sheets"**, one block per instrument (name · verdict from Phase 1 · BOM with IDs and computed cost · wiring · firmware steps · calibration · acceptance · log fields). Static, `_banner`/`S.section` style, freeze `A4`.
**Task 2.4** Exports: `exports/build_sheets.json`; SOLVER.md appendix.
**Done when:** validator proves all 52 BOMs sufficient; gate passes. Commit as v57.

---

## Phase 3 — Recombination: which cheap groupings are most generative  [H]  → v58

**Why:** the owner asked for "sensor groupings that have the most potential recombinatory outcomes"; v55 ranks singles only. This is pure computation.

**Task 3.1** `data/outcome_solver.py`: add `best_groups(S, edges, max_usd=5, k=2)`: for every pair (and triple for parts ≤$3, or cap at 20k combinations) of sensors under the cap, compute `declared = |∪ inferences|`, `closure` → fired edges and emergent count, `score = declared + emergent`, `per_dollar = score / max(cost, 0.5)`. Return top 30 by score and top 30 by per-dollar, with the emergent keys each unlocks. Include in `build()` as `sol["groups"]`. Performance target: < 60 s (405² /2 ≈ 82k pairs × 52-edge fixpoint is fine in pure Python; triples must be capped).
**Task 3.2** `patch_v50.py`: `add_solver` section "7 · THE MOST GENERATIVE PAIRS AND TRIPLES" — two tables (by reach, by reach per dollar), each row: parts · cost · declared · +emergent · what emerges.
**Task 3.3** `solve.py --groups [--k 3] [--max-usd N]` CLI; `exports/groups.csv`; SOLVER.md section.
**Done when:** the sheet names concrete cheap pairs with their emergent unlocks; independent recount in `verify_build.py` for the top row. Commit as v58.

**Status — Tasks 3.1 and 3.3 are DONE. Task 3.2 is deliberately NOT done, so there is no version bump and the workbook is untouched (still v55).**
`data/outcome_solver.py` gained `best_groups()` and the wiring model it needs (`pin_cost`, `group_flags`, `i2c_addresses`, `compat_flags`), wired into `build()` as `sol["groups"]`. `solve.py` gained `--groups [--k N] [--max-usd N]` as a terminal mode, writes `exports/best_groups.csv` from both `--groups` and `--export`, and adds a "The most generative SETS" section to `exports/SOLVER.md`. `verify_build.py` gained `# 8 · best_groups sanity` — nine checks that re-derive the pin model, the rigid-I2C rule and the closure recount independently rather than re-calling the solver. Deviations from the task as written, all deliberate:
- **Sets of 2–6 parts, not pairs and triples.** Pairs are still exhaustive (81,810 closures, ~4 s); k=3..6 is a beam search (beam 30, extension pool 120) seeded from the best pairs, so larger sets are the best sets FOUND, not proven optima. Exhaustive search dies immediately past k=2.
- **Three objectives, not two** — outcomes per part, per dollar and per PIN. The pin objective needed a real model of ESP32 wiring (I2C/SPI/1-Wire/I2S buses paid once for the set, not once per device), which is what turns the ranking into a shopping list.
- **`exports/best_groups.csv`, not `exports/groups.csv`** — the filename matches the function.
- **Constraints the written task did not ask for**: `iface` (set pin cost), `i2c_addr` (two rigid parts on one address reject the set; a flexible one becomes a "move this jumper" note) and `esp32_compat` (keyword flags with negation handling, exclusive resources reject).
- **`--max-usd` is read as a PER-PART cap**, matching the existing `build_predicate` semantics, not a set total.
Task 3.2 (the `patch_v50.py` section "7 · THE MOST GENERATIVE PAIRS AND TRIPLES") stays open: it is the only piece that touches the workbook, and it is what would earn the v58 bump.

---

## Phase 4 — Executable physics: `physlib`  [H]  → no version bump (repo only)

**Why:** an atlas whose formulas run is one the owner can trust and reuse in firmware.

**Task 4.1** Create `sensor-universe/physlib/physlib.py` implementing every formula named in `FUSION_EDGES[*].math` and `derived_instruments.py` as pure functions with docstrings citing the edge key: `dew_point_magnus(T, RH)`, `ach_from_co2_decay(c1, c2, dt_h, c_out=420)`, `hydronic_power_w(flow_lpm, dT)`, `wet_bulb_stull(T, RH)` *(mark: Stull 2011 approximation)*, `air_density(P, T, RH)`, `sound_speed(T)`, `tdoa_bearing(dt, d, c=343)`, `leak_position(L, dt, v)`, `helmholtz_f(A, V, L, c=343)`, `dphp_theta(q_per_m, r, dT_max, C_dry)`, `pv_performance_ratio(P, G, P_rated)`, `heat_index_rothfusz(T, RH)` *(guard: T≥27°C, RH≥40%)*, `wind_chill_ec2001(T, v)`, `ua_w_per_k(P, dT)`, `thermal_tau(...)`, `nernst_slope_mv(T)`, `muon_pressure_correct(rate, P, P0, beta=0.002)`.
**Task 4.2** `physlib/test_physlib.py` (pytest or plain asserts): known-answer tests — e.g. Magnus dew point of 20°C/50% RH ≈ 9.3°C; 4186×ΔT sanity; `sound_speed(20) ≈ 343.4`; Rothfusz refuses out-of-domain inputs; ACH of a decay from 1400→800 ppm in 1 h with 420 ppm outside ≈ 0.95 h⁻¹.
**Task 4.3** `physlib/physlib.h` — a C header port of the same functions (no allocation, `float` only) for ESP32 use, plus a tiny host test compiled with `gcc` comparing against the Python results to 1e-3.
**Done when:** `python3 physlib/test_physlib.py` passes and `gcc -o /tmp/t physlib/test_physlib.c && /tmp/t` passes. Commit.

---

## Phase 5 — Data debt, mechanical  [H] then [S]  → v59

**Task 5.1 [H] Hazard declarations.** `validate.py` warns "text implies hazard X but not declared" for ~100 records. For each, add the implied hazard to `hazard` in the record's *enrichment overlay* (`data/enrich_manual.py` — never edit `part*.py` for this). Only add hazards the text *states* (mains, high voltage, laser, hot surface, UV-C…); never remove one. **Done when:** that warning class is zero and the audit still exits 0.
**Task 5.2 [H] Legacy `spec` → structured.** For the 238 sensors with a `spec` string and empty `range`/`accuracy`/`resolution`/`rate`, parse the numbers out into the structured fields (in `enrich_manual.py`), leaving `spec` intact. Only move values that are unambiguous in the text; otherwise leave empty. **Done when:** ≥ 80% of legacy records have `range` populated; validator clean.
**Task 5.3 [S] Inference notes to 151.** Extend `data/inference_notes.py` from 25 to 151 keys with `{fools, unlocks, market}`. Template: `fools` must name at least two distinct routes from `exports/outcomes_all_routes.csv` and say *why each fails* (a physical mechanism, not "can be inaccurate"); `unlocks` names the action the answer enables; `market` lists 3–5 sectors. Cite a phenomenon key in `fools` where possible. **Gate:** a new `validate_notes()` — every key ∈ INFERENCE, every route named exists in the catalog by name substring, no note under 200 chars, no note contains "may vary"/"depends" without a stated dependency. Then **stop and request an expensive-model refute pass** on a 20-note random sample before merging into a version.
**Task 5.4 [S] Seeds → closure.** For each of the 88 seeds, compute `closure(seed sensor_ids)` and write a computed column set into the *Invention Seeds* sheet block (`add_*` in `patch_v50.py`, a new section appended to the existing sheet or a new sheet "Seeds, Closed"): declared outcomes, emergent unlocked, fusion instruments fired, computed BOM vs authored `bom`. Flag seeds whose authored BOM differs from computed by >30%. No authoring.
**Done when:** gate passes; v59 built. Commit.

---

## Phase 6 — Verification of vendor claims  [H, needs web access]  → v60

**Task 6.1** Run `python3 audit_workbook.py <xlsx>` and extract the two VERIFY classes (61 SKUs, 66 library names). For each: fetch the vendor's own domain / GitHub org (Adafruit, SparkFun, Sensirion, Bosch, ST, TI…). Outcome per item: **verified** (leave; set record `confidence="verified"` in `enrich_manual.py`), or **unverifiable** (replace with the generic description in the record's `brd`/`lib` field, note in commit). Never substitute a guessed number.
**Task 6.2** Add a `verified_as_of` note to `Corrections Log` headline block listing counts.
**Done when:** every VERIFY item is either confirmed or generalised; audit exit 0. Commit as v60.

---

## Phase 7 (optional — owner's call) — HTML explorer  [S]

Previously deferred by the owner ("later — get the xlsx right first"). Only if requested: a **static** `explorer/index.html` that loads `exports/solver_run.json`, `coverage_matrix.csv`, `fusion_edges.csv`, `build_or_buy.csv` and reproduces Kit Builder (own-flags in localStorage → live coverage + fusion closure + best-next-buy), Outcome → Kit, and Build or Buy — no backend, no build step, one file. Reuse the closure algorithm from `outcome_solver.closure` ported to JS (≤ 40 lines).

---

## Reserved for the expensive model (do NOT attempt with the cheaper model)
- New fusion edges, new physics, or edits to existing `math`/`why`/`confound` text.
- Schema changes (e.g. a `latency` class so time-critical edges can exclude slow inferrers — the known weakness of count-based closure).
- Any judgement call about safety framing beyond the fixed disclaimer string.
- The refute pass on Task 5.3's notes.

## Verification (end-to-end, after every phase)
1. `python3 validate.py` → exit 0.
2. `python3 patch_v50.py` → builds the version's OUT; sheet count = previous + new sheets.
3. `python3 verify_build.py <OUT>` → all pass.
4. `python3 audit_workbook.py <OUT>` → **exit 0**.
5. `python3 solve.py --export` regenerates `exports/` without error; `python3 solve.py --budget 25 --fusion` runs.
6. Phase 4 only: `python3 physlib/test_physlib.py` and the C host test pass.
7. Open the xlsx: no repair prompt; new sheet renders; formulas populate on load.
8. Commit + push; deliver the xlsx and `exports/SOLVER.md` in chat.

## Order and cost estimate (relative)
Phase 0 (tiny) → 1 (medium, highest value) → 3 (small, high value) → 2 (large) → 4 (medium) → 5 (large, mostly mechanical) → 6 (medium, web) → 7 (only if asked). Phases 3 and 4 can run in parallel with 1–2 since they touch different files.
