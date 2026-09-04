# 01 — Ionisation smoke alarm

**Incumbent:** A sealed chamber holding roughly 0.3 µCi of americium-241. The alpha source ionises
the air between two plates, a small steady current flows, and smoke particles entering the chamber
capture ions and collapse that current. Commercialised from the late 1960s (Duane Pearsall and
Stanley Peterson's battery-powered unit, 1969-70) and mass-market from the mid-1970s.
**Claims to detect:** Fire, early enough to wake you.
**Actually measures:** The ion-recombination rate in ~1 cm³ of air — i.e. the aerosol surface area
per unit volume of *whatever* enters the chamber, weighted towards particles smaller than about 1
µm. It has no idea what the particles are made of, and no idea whether anything is burning.

## The gap
Ionisation is a particle-counting method with no chemistry in it. Combustion is a chemical process
that emits particles *and* carbon monoxide *and* CO₂ *and* heat, in a ratio that says what is
burning and how completely. The incumbent samples one of those four channels, in one small volume,
and answers a yes/no question with a single threshold. That is why it is famously fast on flaming
fires (lots of sub-micron soot) and famously slow on smouldering ones (bigger, cooler, greasier
particles), and why it fires on toast: burnt toast and a house fire look identical to an ion
current. One channel cannot separate a cause from a coincidence.

**Dataset honesty note:** the atlas carries **no ionisation-chamber part and no photoelectric
smoke-chamber part**. The nearest catalogued physics is laser scattering (`S040`, `S041`, `S294`)
and heated metal-oxide "smoke" sensing (`S026`). Everything below is built from what actually exists
in the dataset; nothing here is a substitute for a certified alarm.

## What fools it
| Fools it | Why, physically | Atlas source |
| --- | --- | --- |
| Steam and humid air read as smoke | Water condenses onto and swells hygroscopic particles, so the optical/ionic cross-section grows with no combustion at all | `S040` `fools`: "It over-reads badly above ~75% RH because particles absorb water and swell: fog, shower steam and a humid summer night all read like wildfire smoke, which is why every serious network applies a humidity correction." |
| Ultrafine cooking and candle aerosol is invisible to the replacement optics | Mie scattering falls off steeply below the wavelength; a laser counter simply cannot see 0.1 µm particles | `S040` `fools`: "It is blind below 0.3 um, and that is most of what a candle, a gas hob or a laser printer emits by number — 'clean air' during a real ultrafine event is a routine false negative." |
| A dust-filled chamber under-reads for a year without complaining | Lint accumulation reduces the sampled volume and the optical path; there is no self-test for it | `S040` `fools`: "The fan pulls in lint and hair; a unit running continuously for a year typically reads 20-30% low with no warning." |
| Hydrogen from a charging battery reads as CO on the cheap CO channel | Both are reducing gases oxidised by the same hot metal-oxide surface | `S028` `fools`: "It sees hydrogen roughly as strongly as carbon monoxide, plus alcohol and methane, so a garage with petrol vapour or a charging lead-acid battery reads as a CO event." |
| A real electrochemical CO cell keeps reporting plausible numbers after it has died | The cell degrades chemically; the current it produces stays in range and nothing flags it | `S033` `fools`: "the cell continues to output a plausible-looking number long after it has lost its sensitivity — there is no self-diagnostic, only a calendar." |
| Sunlight or a hot kettle reads as flame on the cheap flame channel | It is a near-IR level detector, and window glass is transparent in the near-IR | `S180` `fools`: "Direct or reflected sunlight saturates it instantly; so does any incandescent or halogen lamp, a quartz heater, a hot soldering iron, a kettle that just boiled, and your TV remote." |

## What the underlying phenomenon actually is
The phenomenon is **incomplete combustion**, and it has a signature, not a level. Combustion
converts hydrocarbons to CO₂ and H₂O when oxygen is plentiful, and to CO plus condensed carbon when
it is not — so the *ratio* of particle mass to CO to CO₂ is a statement about how a fire is burning,
and a rise in all three at once is a statement that something is burning at all. Four transduction
routes in `data/physics.py` carry those channels: **Photoelectric / photovoltaic** (laser scattering
off particles onto a photodiode), **Electrochemical** (CO oxidised at an electrode, the reaction's
electrons *are* the signal), **Radiant → Thermal · Absorption** followed by **Photoacoustic** (NDIR
and photoacoustic CO₂ — the SCD41 is explicitly the catalog's photoacoustic example), and **Thermal
→ Radiant · Blackbody emission** (the IR thermometer reading a hot surface across the room).
**Chemiresistive (MOX)** supplies a cheap fifth channel that is fast and non-specific — useful as a
corroborator, never as a decider. The ionisation route itself is in the grid as **Ionisation /
avalanche** ("One energetic particle rips electrons from atoms; a strong field multiplies that into
a measurable pulse"), which is why the physics is present in this atlas even though the part is not.

## Proposed ESP32 stack
| Role | Part | `pn` | id | ~USD | Captures |
| --- | --- | --- | --- | --- | --- |
| Particles | PMS5003 particulate | `PMS5003 / PMSA003I` | `S040` | $15 | PM1.0/2.5/10 mass + counts in six size bins — the smoke channel, with the size distribution the ion chamber throws away |
| CO, quantitative | Electrochemical gas cells | `SPEC/EC-Sense/Alphasense (CO, NO2, O3, SO2, H2S)` | `S033` | $80 | Real ppm CO — the channel that separates a smouldering fire from burnt toast |
| CO₂ | SCD41 true CO2 | `SCD41 / SCD40` | `S036` | $25 | Photoacoustic CO₂ — combustion product and, via `ach-co2-decay`, the room's ventilation rate |
| VOC | SGP40 VOC index | `SGP40 / SGP41` | `S024` | $12 | Pyrolysis products before visible smoke; explicitly *not* a smoke alarm on its own |
| Air T + RH | SHT41 humidity + temp | `SHT41 / SHT40 / SHT45` | `S012` | $6 | The humidity correction without which the PM channel is a weather station |
| Surface heat | MLX90614 IR thermometer | `MLX90614` | `S007` | $8 | Hot-surface rise (hob, flue, appliance) — a fourth physics, no contact |
| Optional: flame | IR flame detector (flicker) | `KY-026 / 5-channel IR flame array` | `S180` | $2 | Open-flame hint only — advisory channel, never a trigger |
| Budget swap for `S033` | MiCS-5524 CO/VOC | `MiCS-5524` | `S030` | $14 | CO at 1/6 the price and a fraction of the selectivity |

**Board:** ESP32-WROOM-32E / DevKitC v4 (`B001`, $6) — chosen because it has three UARTs and this
build needs two (PMS5003 and the SPEC DGS CO module) alongside I²C. · **Sensor total:** ~$146 (+$2
with the flame channel) · **Build:** ~$152 · **Budget build with `S030` in place of `S033`:** ~$86.

**Missing from the dataset:** `S033` `requires` an LMP91000-class potentiostat front end. There is
no such glue record — the 33 `G0xx` parts cover ADCs, level shifters and isolators but no
potentiostat. Either buy the UART SPEC DGS module (which contains its own front end) or accept that
the analog-cell route needs a part this atlas does not price.

## The fusion
**Edge:** `fire-coincidence` — Fire coincidence detector (data/fusion.py)
**Math:** `Alarm = smoke AND (CO rising ≥ 5 ppm over baseline within 10 min); either alone =
advisory`
**Confound:** Smouldering PVC and some foams are CO-rich but smoke-poor early on: keep the
single-channel advisory alerts, gate only the loud alarm.
**Why it beats the incumbent:** The ion chamber asks "are there particles?" and has to set its
threshold low enough to catch a real fire, which guarantees it also catches showers and toast. The
coincidence gate asks "are there particles *and* is CO climbing?" — and the things that produce only
particles (dust, steam, cooking) or only CO (a blocked flue, an idling car) fail it. Because the two
channels fail for uncorrelated physical reasons, the false-alarm rate is roughly the *product* of
two small numbers rather than the sum. And the single-channel advisories survive: you still get told
about the blocked flue, which the incumbent cannot detect at all.

## What this costs you
- **Price.** $152 against about $8 for the thing it replaces. That is a nineteen-fold price increase
  for a device that is explicitly not certified.
- **Consumables.** `S033`: "The cell IS the consumable: 1-2 years of life from the day the shorting
  clip comes off, used or not. Budget ~$25-60 per cell per replacement". `S040`: fan bearing and
  laser diode, "realistically 1-2 years running 24/7." The Am-241 chamber has a ten-year service
  life and no moving parts.
- **Warm-up.** Nothing here is instantly ready. `S024`: "~60s for a valid raw signal; ~1h before the
  index means anything; ~24h for a settled baseline." `S033`: "up to 24-48 h for a cell that has
  just had its shipping shorting clip removed". `S040`: 30 s of fan every time it wakes.
- **Power.** The PM fan is 100 mA whenever it runs and cannot be a battery device; the incumbent
  lives nine years on one 9 V cell. This is a mains build with a duty-cycled fan, or nothing.
- **Calibration.** `S033` and `S024` are `Reference` and `Periodic` respectively; the CO cell needs
  its per-cell sensitivity constants typed into your firmware or the current means nothing.
- **Certification.** None of this is UL 217 / EN 14604. It is a supplement, and the
  `fire-coincidence` `why` field says so directly: "NOT a life-safety device — supplement, never
  replace, a certified alarm."

## Verdict
Strong on diagnosis, weak on replacement. As an *early-warning and forensics* layer — smouldering
detection, blocked-flue detection, a CO trend you can read, a false-alarm rate low enough that
nobody removes the battery — this is a large and real improvement, and the coincidence gate is the
reason. As a life-safety device it is worse than a $8 alarm, because it has consumables, a fan, and
no certification. Build it *next to* the certified alarm, not instead of it. Confidence: high on the
physics, moderate on the CO channel, which is the expensive, ageing, silently-dying part of the
whole stack.

