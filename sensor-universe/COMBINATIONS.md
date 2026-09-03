# Combination Ranker — twenty pairs and triples worth building

**405 sensors · 81,810 pairs scored exhaustively · 190,603 triples scored from a stated neighbourhood · 335 part families.** The solver next door asks which sensors to buy. This asks a different question: which two or three of them, put together, know something that none of them knows alone.

The twenty entries below are **curated, not the top twenty by score**. They were chosen from the top ~60 deduped pairs and the top ~30 deduped triples, every candidate's `fools` text was read, and nine were thrown out because the reasoning did not survive the reading. Those nine are named at the end, with what went wrong. A ranked list you have not argued with is a list of numbers.

---

## What the score measures, and what it does not

The total is a weighted sum of six components. Each is computed from the records, none is authored, and every one carries the evidence that produced it — `python3 combine.py --explain S008,S015` prints the whole derivation for any row in the table.

| Component | Weight | What it counts | What it cannot see |
|---|--:|---|---|
| synergy | 0.30 | outcomes the combination reaches that no member reaches alone, via `fusion.FUSION_EDGES` | whether the edge's physics applies to *these* parts in *this* place |
| compensation | 0.28 | (fooled part, interferent, correcting part) channels, extracted by regex from `fools` prose | whether the corrector is measuring the same air, surface or subject |
| shared_measurand | 0.18 | one quantity read through two different transduction mechanisms | mechanisms it cannot name — 121 of 405 parts have none identified |
| failure_independence | 0.12 | Jaccard distance between the members' extracted interferent sets | interferents the lexicon has no pattern for |
| time_separation | 0.08 | decades between time constants, signed by claim type, scaled by how the τ was obtained | anything about a part whose prose states no response time |
| novelty | 0.04 | whether the catalog's own prose already pairs these parts | almost nothing — see below |

**Totals are calibrated within a k.** The normalisation caps were fitted on the 81,810-pair run, so a triple saturates more components than a pair and their totals are not on one scale. Every row carries `percentile_within_k` beside its total for exactly this reason. A triple at the 99.99th percentile is the best of the triples *searched*; it is not a claim that it is 99.99% likely to work.

**`novelty` carries almost no information.** Virtually every combination comes out `unexplored`, because the catalog's `pair` prose names a handful of partners per part and nothing else. It is kept at weight 0.04 as a tiebreaker and should be read as "this catalog's prose does not mention it", never as "nobody has done this".

**Cost is deliberately not a component.** Ranking by outcomes-per-pound rediscovers what the outcome solver already proved — that the cheap generic transducers win — and fills the table with 50p pairs. Cost is reported, not scored.

### The seven known failure modes, and how far the fixes go

These were found by attacking the round-one output. Each has a fix; none of the fixes is complete, and the residue is stated.

**1 · Incidental capabilities.** 59 parts carry `temperature-contact` because they have a die-temperature register. The closure could not tell that register from a thermometer, so all 1,711 of those pairs fired the same three ×2 edges and owned the top of the table. A phenomenon is now **incidental** when its stem appears nowhere in the part's own `n`, `meas`, `cat` or `sub` — 223 of 956 phenomenon listings (23%). Incidental phenomena earn no shared-measurand credit and drop a compensation channel to 5% of its weight. *Residue:* the test is stem-matching over prose, and the boundary between "the mechanism" and "the output" is a judgement the catalog does not make. Two parts remain flagged as wholly incidental (`S235`, `S366`) and both were read and left alone deliberately.

**2 · Per-part modality was the wrong instrument.** Round one gave full differential credit whenever two parts had different `modality` labels. `modality` is a per-part field and the question is per-channel: an HDC3022 (`Electrical`) and a DS18B20 (`Electrical`) scored as redundant when they are not, and an MLX90632 (`Optical`) scored as differential against a contact probe on a channel its own silicon bandgap produces. There are now **37 transduction mechanisms**, matched from `how`/`sub`/`meas` prose and restricted by `MECHANISM_SERVES` to the phenomena each can physically transduce. Full credit requires two known, *different* mechanisms; same mechanism or unknown on either side drops to redundancy weight. 16 of the 37 names are shared with `data/physics.py`'s `TRANSDUCTION` table, which is a parallel and more authoritative layer — this one exists because it can be computed today. *Residue:* 121 of 405 parts have no readable mechanism, including the SHT31, whose prose never says "capacitive polymer". Those channels score as redundancy forever.

**3 · Regex over prose matches negations and topics.** `fools` text is written in English, and "a fake BME280 arrives with no humidity sensor at all" matched the humidity interferent. There are now negation guards (`ABSENCE_PREFIXES`, anchored to a governing prefix rather than "any negation nearby", because true confounders are routinely phrased negatively) and `require_nearby` effect-word guards. They reject **127 matches across 405 sensors**. *Measured residue, post-fix:* 40 surviving channels were sampled at random from the population of 821 and read. **Six were wrong — 15%.** The guards catch negation; they do not catch topicality. The BMP280's humidity match survives on a *second* occurrence — "before you trust a humidity number from a $2 board" — which is about a counterfeit chip-ID, not about humidity fooling a barometer.

**4 · A sample rate is not a time constant.** 146 of 405 parts have a τ derived from `1/f_max`, which is a **lower bound** on response, not a measurement. The time component is now multiplied by the weakest member's confidence — `high` 1.0, `medium` 0.7, `low` 0.35 — and every lower-bound τ says so in its basis string and in the CSV's `tau_lower_bound` column. *Residue:* attenuating is not the same as knowing. A pair of `low`-confidence parts still scores 0.35 of a number that may be meaningless.

**5 · Near-duplicate parts fill the table.** Nine digital contact thermometers make the same claim nine times. Parts are now grouped into **335 families** — same `cat`+`sub`+phenomena set, or one naming the other in `substitutes` prose — and combinations sharing a family signature *and* the same synergy keys collapse, best row kept, the rest listed as `equivalent_swaps`. 24,338 of 81,810 pairs collapse. *Deviation, measured:* linking on `substitutes` prose alone puts 377 of 405 sensors in one family, because the prose crosses categories on purpose ("No-contact: MLX90614" on a contact probe) and union-find is transitive. Restricting those links to the same `cat`+`sub` gives the 335 above. *Residue:* a 16×12 thermal array and a 32×32 thermal array are different families and both appear.

**6 · Corrections that cannot be co-located.** Round one credited an $85 bench e-nose loop with correcting an STC31 five channels over. A channel is now flagged `co_location: doubtful` when the two parts share no `environment` value, when the corrector is difficulty 5, when its name reads as a bench rig, or when the contact classes cannot coexist — and is attenuated to 35%. *Residue:* it catches the `Indoor` vs `Outdoor` case and the bench rig. It does not catch the case that matters most, which is two indoor parts 30 cm apart in different air.

**7 · Totals were being read across k.** `percentile_within_k` is now on every row, in the CSV header note, in the JSON `meta` and in the CLI output.

---

## Read this before the table

Two things recur in almost every entry and are stated once here rather than twenty times.

**The temperature-contact halo is discounted, not gone.** Thirteen fusion edges are satisfied by one capability at multiplicity ≥2 — `psychrometric-wetbulb`, `soil-heat-pulse`, `compost-core`, `bearing-thermal` — and any two parts that both carry a die-temperature register fire them. They are discounted to 0.25 (or 0.05 when the multiplicity can only be reached by counting an incidental register), and every entry below marks them `discounted`. At 0.25 × 3.0 per key they can still contribute a third of the synergy cap. If a row's gains are *all* discounted, the row is the halo and nothing else.

**Every compensation claim is a claim about placement.** "Part B corrects part A" means B is reading the same air, the same surface or the same subject as A. The model cannot know your enclosure. Where the catalog gives a reason to doubt, it says so; where it does not, silence is not evidence.

---

## The twenty

### Pairs

#### 1 · MLX90632 miniature IR temp + SHT31 weatherproof probe — `S008` + `S015`, $26

**Jointly infers:** `condensation-risk` (EMERGENT — will water condense on that surface soon?), `black-ice-risk` (EMERGENT — is the road surface about to ice over?), `sky-clear`. Neither part measures any of them.

**Mechanism.** The SHT31 gives air temperature and RH, from which dew point follows by Magnus; the MLX90632 gives the temperature of a *surface* without touching it. The inference is the difference between them: `T_surface − T_dew < 1.5 °C` is condensation, and `T_road ≤ 1 °C AND T_road ≤ T_dew + 0.5 °C` is frost deposition. Each part also corrects the other — the SHT31's contact temperature is the ambient reference the MLX90632's own package self-heating corrupts, and the MLX90632's remote read is the check on the SHT31 being sun-baked.

**What would kill it.** The SHT31's own text: *"Outdoors and unshielded in sun it reads 5-15°C high, and since RH is referenced to that temperature the humidity number"* is wrong too. And the edge's stated confound: emissivity — a shiny surface lies to an IR thermometer by 20×. Put matt tape at the cold spot and aim at that.

**τ.** 3.2 decades apart, `separated`, confidence `low`: the SHT31 is a measured 30 s (63% step response through the sintered cap) but the MLX90632's 0.02 s is a lower bound from its 50 Hz rate, not a response. The direction is right — a slow air reference disciplining a fast surface read — the magnitude is not trustworthy.

**ESP32.** ✓ single-board, 2 pins, both I²C, no address clash. All 14 host boards.

#### 2 · SHT31 weatherproof probe + Grid-EYE AMG8833 thermal array — `S015` + `S071`, $47

**Jointly infers:** `condensation-risk`, `black-ice-risk`, `sky-clear`.

**Mechanism.** The same claim as entry 1 with a 64-pixel field instead of a spot, which is the difference between "that surface is cold" and "the cold corner is behind the wardrobe". The array corrects the SHT31 for `sunlight-ir`; the SHT31 corrects the array for its own `self-heating`, which the array's text says shifts *every pixel* by a degree or more over the first minutes.

**What would kill it.** The AMG8833's own text: *"The whole frame drifts with the sensor's own die temperature - self-heating over the first few minutes shifts every pixel by a degree or more - so work with per-pixel"* differences, not absolutes. And both members are fooled by sunlight and ambient IR, so their agreement is not independent confirmation.

**τ.** 2.5 decades, `separated`, confidence `low` — the array's 0.1 s is 1/10 Hz, a frame rate, not a thermal response. Its real settling is minutes, which the model does not know.

**ESP32.** ✓ single-board, both I²C. All 14 host boards. This is the cheap, no-level-shifter version of entry 3.

#### 3 · SHT31 weatherproof probe + FLIR Lepton 3.1R radiometric thermal module — `S015` + `S329`, $192

**Jointly infers:** `condensation-risk`, `black-ice-risk`, `sky-clear` — at 160×120 radiometric pixels.

**Mechanism.** Same physics as entries 1 and 2; what the money buys is that the Lepton reports absolute temperature per pixel, so the dew-point margin can be computed for a whole wall at once instead of one spot. The SHT31 corrects the Lepton for `temperature-drift`, which is the flat-field shutter problem below.

**What would kill it.** The Lepton's own text: *"The flat-field shutter fires automatically as the module's own temperature drifts, freezing the image for about half a second; disable it to avoid the interruption and th"*en the radiometry walks away. You choose between a gap in the data and a drift in the numbers.

**τ.** 0.8 decades, `separated`, confidence **`high`** — both taus are measured: the SHT31's 20-30 s step response and the Lepton's "specified after several minutes of thermal settling". This is one of the few rows where the timing claim is worth as much as the physics claim.

**ESP32.** ! single-board-with-caveats — the Lepton runs 2.8 V I/O with 1.2 V and 2.5 V core rails and needs a carrier board. Privacy is `Raw-imagery`. All 14 host boards electrically.

#### 4 · BME688 gas + climate AI + STC31 percent-level CO2 — `S023` + `S279`, $43

**Jointly infers:** `window-open-state` (EMERGENT), `radon-risk-rising` (EMERGENT — is radon likely rising, before the slow meter can say?).

**Mechanism.** The STC31 measures CO2 by thermal conductivity at percent levels, and thermal conductivity is a function of *everything* in the gas: pressure, humidity, temperature and any other gas present. The BME688 supplies four of those five compensation inputs from one part — pressure, RH, temperature and a MOX gas channel. Five compensation channels, all at full weight. On top of that, CO2 decay rate plus an indoor temperature slew gives window state, and falling pressure plus a measured air-change rate gives the radon proxy.

**What would kill it.** The STC31's own text: *"an uncompensated STC31 in a fermenter headspace at 100% RH is simply wrong; you MUST read an RH sensor and write the value into the sensor's compens"*ation register. And: *"Hydrogen, helium and methane conduct heat far better than air and will drive the reading violently negative"* — a biogas or a hydrogen leak reads as negative CO2, and the BME688's MOX channel is a warning, not a correction.

**τ.** 5.2 decades, `separated`, confidence `low`. The BME688's 48 h is a *measured* burn-in for a unit stored unpowered; the STC31's 1 s is a lower bound from its 1 Hz rate. The real story is the 48 h: this pair does not tell you anything true on its first day.

**ESP32.** ✓ single-board, both I²C. All 14 host boards. Hazards: `Asphyxiant`, `Ignition`.

#### 5 · BME280 climate combo + STC31 percent-level CO2 — `S013` + `S279`, $34

**Jointly infers:** `window-open-state`, `radon-risk-rising`.

**Mechanism.** The same compensation argument as entry 4 at two-thirds the price and without the gas channel — pressure, humidity and temperature into the STC31's compensation register. What you give up is the cross-gas warning; what you gain is a part whose RH response is a measured ~1 s rather than a 48 h burn-in.

**What would kill it.** Identical to entry 4: hydrogen, helium and methane. Without the BME688's MOX channel you have no indication at all that it has happened. Also note that both members are fooled by humidity, so their agreement is not independent.

**τ.** 0.0 decades — `separated` mode but no separation, and confidence `low` because the STC31's τ is a lower bound. The timing component contributes essentially nothing here and the row stands on its compensation channels.

**ESP32.** ✓ single-board. All 14 host boards.

#### 6 · KY-037/038 sound modules + Eastron SDM120-Modbus DIN energy meter — `S209` + `S257`, $39

**Jointly infers:** `recording-authenticity` (EMERGENT — was this recording really made when it claims?), `energy-waste-unoccupied` (EMERGENT), `cost-per-use` (EMERGENT).

**Mechanism.** This is the ENF (Electrical Network Frequency) trick and it is the most interesting thing in the table. Mains frequency wanders by a few tens of millihertz on a schedule nobody controls; that wander is recorded as hum in any mains-powered audio, and it is also measurable directly at the meter. Correlate the hum drift extracted from the audio against your own logged grid-frequency history and a genuine timestamp correlates r > 0.9 over minutes. The meter is simultaneously the *corrector* for the microphone: the sound module's own text says mains hum on a long lead is indistinguishable from a clap, and the meter tells you when the hum is there.

**What would kill it.** The edge's own confound, stated plainly: *"Battery-powered outdoor recordings carry no hum; heavy audio compression notches 50 Hz out. Absence of match ≠ forgery — it is absence of evidence."* And the KY-037's own text: it has *"no frequency discrimination whatsoever, so a door slam, a dropped saucepan, wind on the capsule and mains hum picked up on a long lead are indistinguishable"*.

**τ.** 3.0 decades, `separated`, confidence `medium` — the mic's sub-1 ms is a measured digital response, the meter's ~1 s is a stated update period. The shape is right: a slow grid reference disciplining a fast audio channel.

**ESP32.** ! single-board-with-caveats — the SDM120 is self-powered from the measured mains and speaks RS-485, which needs a transceiver and level shifting. Hazard: `Mains`. All 14 host boards.

#### 7 · MAX9814 AGC mic amp + INA226/INA228 precision power — `S089` + `S145`, $13

**Jointly infers:** `recording-authenticity`, `energy-waste-unoccupied`, `cost-per-use`.

**Mechanism.** The same ENF claim as entry 6 for a third of the price, using a precision shunt monitor as the voltage reference instead of a DIN meter. The INA226 corrects the MAX9814 for `mains-hum`, and the mic amp's own text tells you why it needs correcting.

**What would kill it.** The MAX9814's own text: *"Long unshielded leads make it a 50/60 Hz mains-hum antenna. And the ESP32 ADC is nonlinear enough that an FFT of raw analogRead()"* is not the spectrum you think it is. For an ENF claim that nonlinearity is not a nuisance, it is the measurement. Pair this with an external ADC or accept that the correlation you compute is partly the ESP32's.

**τ.** 1.1 decades, `separated`, confidence `low` — both taus are `1/f_max` lower bounds (40 kHz and 3 kHz). The separation number here should be ignored; the physics stands without it.

**ESP32.** ✓ single-board. Privacy `Raw-imagery` — a live microphone is what it is. All 14 host boards.

#### 8 · BME688 gas + climate AI + MH-Z19C budget NDIR CO2 — `S023` + `S038`, $33

**Jointly infers:** `window-open-state`, `radon-risk-rising`.

**Mechanism.** NDIR CO2 is pressure-dependent and the MH-Z19C exposes no pressure register, so weather fronts and altitude bias it permanently. The BME688 supplies the pressure. The second channel is subtler and more valuable: the MH-Z19C self-heats by ~5 °C, so a temperature sensor mounted next to it reads the *module*, not the room — the BME688's temperature channel is what lets you know how much of the reading is the module's own heat.

**What would kill it.** The MH-Z19C's own text: *"Readings track ambient pressure (roughly 1.6% per 10 hPa) and most firmware exposes no pressure register, so weather and altitude bias them perman"*ently, and *"The module self-heats by around 5 degC, so a temperature sensor mounted next to it reads the sensor, not the r"*oom. Both members are fooled by self-heating, so agreement between them is not independent confirmation.

**τ.** 3.5 decades, `separated`, confidence **`high`** — both measured: 48 h BME688 recovery and "~1 min to a plausible value, ~3 min to specified accuracy" for the MH-Z19C.

**ESP32.** ✓ single-board. All 14 host boards. Hazard: `Ignition`.

#### 9 · BME688 gas + climate AI + NDIR methane / hydrocarbon module — `S023` + `S035`, $60

**Jointly infers:** nothing emergent — this row earns its place entirely on **shared measurand through genuinely different physics**, which is what Fix 2 was built to find.

**Mechanism.** Both parts report `gas-concentration`. The BME688 does it chemiresistively (a heated metal-oxide film whose resistance changes when something adsorbs) and the NDIR module does it optically (absorption in the 3.3 µm band). Those two mechanisms fail in completely different ways, so their *disagreement* is the measurement: a MOX response with no NDIR absorption is a VOC that is not a hydrocarbon; NDIR absorption with no MOX response is a hydrocarbon the MOX film does not adsorb. Four compensation channels run from the BME688 into the NDIR module — pressure, humidity, temperature and a VOC cross-check.

**What would kill it.** The NDIR module's own text: *"the methane absorption band near 3.3 um is shared with other hydrocarbons: propane, butane and ethanol vapour all absorb there, so a bottled-gas leak reads as methane and vice versa"*, and *"Water condensing on the optical window produces a large sustained false reading"*. Both members are also fooled by ethanol and by humidity — the shared blind spot is exactly the one you would most want covered.

**τ.** 2.8 decades, `separated`, confidence **`high`** — 48 h and "3-5 min from cold for the IR source and thermopile".

**ESP32.** ! single-board-with-caveats — the NDIR module is 5 V and needs level shifting. All 14 host boards. Hazard: `Ignition`.

#### 10 · US-100 ultrasonic w/ temp comp + FLIR Lepton 3.1R — `S197` + `S329`, $184

**Jointly infers:** `sky-clear`, `stove-left-on`.

**Mechanism.** A radiometric thermal camera reports apparent temperature, and apparent temperature depends on distance through atmospheric attenuation and on how much of a pixel the target fills. The US-100 supplies the distance. In the other direction the Lepton reads the air the ultrasonic pulse actually crosses, which the US-100's own on-board thermometer does not: its sensor sits on the PCB inside your housing.

**What would kill it.** The US-100's own text: the temperature sensor *"is on the PCB inside whatever housing you built, so it measures the housing, not the air column — a sun-warmed enclosure over-compensates and drifts the same way an uncompensated sensor would"*. And both members are fooled by multipath and ghost returns, so agreement is not independent.

**τ.** 3.5 decades, `separated`, confidence **`high`** — 60 ms measured echo decay against several minutes of Lepton settling. A genuinely well-shaped fast/slow pair.

**ESP32.** ! single-board-with-caveats — Lepton rails again. Privacy `Raw-imagery`. All 14 host boards.

#### 11 · SHT31 weatherproof probe + Non-contact liquid level XKC-Y26 — `S015` + `S139`, $20

**Jointly infers:** `plant-thirsty` (new route).

**Mechanism.** The XKC-Y26 detects a dielectric change through a tank wall — which means it detects *anything* that changes the dielectric, including condensation running down the inside of the wall. The SHT31 tells you whether the air is at a dew point where that can happen, which is the difference between "the tank is full" and "the wall is wet". In the other direction the level sensor is the only part in this pair that can tell you the SHT31 has been immersed, which its own text says finishes it.

**What would kill it.** The XKC-Y26's own text: *"it detects a dielectric change, not water specifically, so condensation running down the inside of the wall, a wet patch outside, foam, a sludge layer or yo"*ur hand all read as liquid. And the SHT31's: *"Weatherproof is not waterproof: the cap must pass vapour, so driving rain, a hose-down or immersion still finishes it."* Both are fooled by humidity.

**τ.** 1.8 decades, `separated`, confidence **`high`** — 30 s SHT31 cap response against a deliberately filtered 500 ms level response.

**ESP32.** ! single-board-with-caveats — the XKC-Y26 wants 5-24 V and needs level shifting. All 14 host boards.

#### 12 · MPRLS ported pressure + SCD41 true CO2 — `S021` + `S036`, $40

**Jointly infers:** `air-density` (EMERGENT — what is the actual air density right now?), `radon-risk-rising`.

**Mechanism.** The SCD41's photoacoustic cell is pressure-dependent and needs its ambient-pressure register fed; the MPRLS is a ported absolute barometer, so it can be plumbed to the *same* volume the CO2 cell samples rather than to room air. That porting is why this pair beats a bare barometer for enclosed or ducted work. Pressure plus temperature plus humidity gives air density directly; falling pressure plus the CO2-derived air-change rate gives the radon proxy.

**What would kill it.** The SCD41's own text: *"uncompensated readings drift with weather fronts and read badly high above ~500m. Its automatic self-calibration assumes the room reaches"* outdoor baseline regularly — in a room that never does, ASC will slowly calibrate the truth away. And the air-density edge's confound: self-heating biases the temperature by up to 1 °C on combo boards.

**τ.** 3.0 decades, `separated`, confidence `medium` — a 5 ms conversion against a 5 s update period, both stated.

**ESP32.** ✓ single-board, both I²C, no clash. All 14 host boards. 2.5 mA total.

#### 13 · BMP390 precision barometer + SCD30 NDIR CO2 — `S016` + `S037`, $50

**Jointly infers:** `air-density`, `radon-risk-rising`.

**Mechanism.** The same shape as entry 12 with a precision barometer instead of a ported one — better absolute accuracy, no plumbing. The SCD30's NDIR reading moves 1.4% per 10 hPa and its pressure register has to be fed from somewhere.

**Worth noting for what it does *not* claim:** both parts list `temperature-contact`, and the model scores that shared measurand at **zero** — it is incidental for both, a die register on a barometer and a die register on a CO2 module, neither of which is a thermometer. This is Fix 1 doing its job on a row you might otherwise have believed.

**What would kill it.** The SCD30's own text: *"The reading moves roughly 1.4% per 10 hPa of pressure, so weather fronts and altitude are visible in the data unless the pressure register is fed."* Both members are fooled by barometric pressure — the barometer measures the confounder rather than being immune to it, so a systematic pressure error corrupts both channels the same way.

**τ.** 1.1 decades, `separated`, confidence **`high`** — 1-2 min for the BMP390 die to reach equilibrium, >10 s to the SCD30's first reading.

**ESP32.** ✓ single-board. All 14 host boards.

#### 14 · SCD41 true CO2 + BMP280 budget barometer — `S036` + `S192`, $26.50

**Jointly infers:** `air-density`, `radon-risk-rising`. Also fires four **discounted** temperature-halo keys (`wet-bulb-heat-stress`, `soil-water-volumetric`, `thermal-time-constant`, `bearing-failing`), which should be read as noise.

**Mechanism.** The cheapest honest route to air density and the radon proxy: a $1.50 barometer feeding the SCD41's ambient-pressure register.

**! This row contains a scoring error and is included so you can see one.** The model credits a second channel — "SCD41 corrects BMP280 for humidity" — on this snippet from the BMP280's `fools`: *"read the chip-ID register (0x58 = BMP280, 0x60 = BME280) before you trust a humidity number from a $2 board"*. That sentence is about counterfeit modules sold as BME280s, not about humidity fooling a barometer. It is one of the 15% of surviving channels measured as false positives in Fix 3, and it is exactly the kind the negation guard cannot catch, because nothing in it is negated. **The pressure channel is real; the humidity channel is not.** Score the row at one channel, not two.

**What would kill it.** As entry 12, plus the counterfeit problem itself — check the chip ID before you trust the part.

**τ.** 2.9 decades, `separated`, confidence `low` — the BMP280's 6 ms is 1/157 Hz, a rate.

**ESP32.** ✓ single-board. All 14 host boards.

### Triples

Triple totals are **not comparable with pair totals** — the caps are pair-calibrated. Compare within the triples.

#### 15 · BME280 climate combo + MH-Z19C budget NDIR CO2 + Thermistor airflow (nasal) kit — `S013` + `S038` + `S218`, $27

**Jointly infers:** `window-open-state`, `radon-risk-rising`.

**Mechanism.** Entry 8 plus a fast bead NTC, and the third part earns its $1 by answering the question the pair leaves open. The MH-Z19C self-heats ~5 °C, so a thermometer next to it reads the module; the BME280 is a slow, port-limited climate reference and the bead NTC is a 100 ms probe you can put *on* the module. Two thermometers with genuinely different mechanisms — silicon bandgap versus thermoresistive — reading the same `temperature-contact`, which is scored as a full **differential** pair: their disagreement is the self-heating term.

**What would kill it.** The MH-Z19C's own text again: *"The module self-heats by around 5 degC, so a temperature sensor mounted next to it reads the sensor, not the r"*oom. Three members are fooled by self-heating and by part-to-part tolerance. Privacy is `Identifiable` because a nasal airflow kit measures a person's breathing.

**τ.** 2.8 decades, `separated`, confidence **`high`** — all three taus measured: ~1 s BME280 RH, ~1 min MH-Z19C, ~100 ms bead NTC.

**ESP32.** ✓ single-board, 13 of 14 host boards (not the ESP32-CAM, which has 4 free pins).

#### 16 · SCD41 true CO2 + SenseAir S8 CO2 + BMP280 budget barometer — `S036` + `S039` + `S192`, $51.50

**Jointly infers:** `air-density`, `radon-risk-rising`.

**Mechanism.** Two CO2 cells that fail differently, plus the pressure both need. The SCD41 is photoacoustic; the S8 is classic NDIR. Same measurand, genuinely different physics, scored **differential** — and it is the useful kind of redundancy, because the two have different ageing behaviour and different self-calibration assumptions, so a slow divergence between them is a calibration alarm neither can raise alone.

**What would kill it.** The S8's own text: *"There is no ambient-pressure register in the standard firmware, so altitude biases it: at 1000 m expect roughly 10% low unless you scale in software."* Both cells run automatic baseline calibration on the assumption that the room reaches outdoor CO2 regularly; in a room that never does, both drift the same way, and their agreement means nothing.

**τ.** 2.9 decades, `separated`, confidence `low` — the two CO2 cells are 4 s and 5 s stated update periods, the barometer's is a rate-derived lower bound.

**ESP32.** ✓ single-board. All 14 host boards.

#### 17 · SHT41 humidity + temp + SHT31 weatherproof probe + FLIR Lepton 3.1R — `S012` + `S015` + `S329`, $198

**Jointly infers:** `condensation-risk`, `black-ice-risk`, `sky-clear`.

**Mechanism.** Entry 3 with a second hygrometer, and the point is placement rather than precision: the SHT41 is a bare fast part for indoor air (~4 s), the SHT31 is a potted weatherproof probe for the outdoor or in-duct side (~30 s). Condensation is an *indoor-surface* phenomenon driven by an *outdoor* temperature, so having both sides instrumented is what turns the Lepton's surface map into a forecast.

**! Honest note on the shared measurand.** The model scores all three shared channels (`humidity-relative`, `dew-point`, `temperature-contact`) as `unverified`, not differential — because the SHT31's prose never names its transduction mechanism, so Fix 2 refuses to claim two different physics. In truth both are capacitive polymer sensors and this *is* redundancy, not a differential pair. The model's caution happens to land on the right answer here by refusing to guess.

**What would kill it.** The SHT31's sun error (entry 1) and the Lepton's flat-field shutter (entry 3). All three members are fooled by humidity.

**τ.** 1.7 decades, `separated`, confidence **`high`** — 4 s, 30 s, several minutes, all measured.

**ESP32.** ! single-board-with-caveats, two of them: the SHT41 and SHT31 **collide at 0x44/0x45** and the SHT41 must be strapped to its alternate address; and the Lepton needs its carrier board. All 14 host boards.

#### 18 · MAX31855 thermocouple amp + ACS712 Hall current + INA700 power monitor — `S004` + `S146` + `S378`, $22

**Jointly infers:** `building-heat-loss` (EMERGENT — how many watts does this building leak per degree?), `cost-per-use`, `power-quality`.

**Mechanism.** Two current measurements through completely different physics — the ACS712 is a Hall-effect device that never touches the conductor, the INA700 is a shunt with an ADC on the die — scored as a full **differential** pair on `current-dc`. That disagreement is the measurement: a Hall device drifts with temperature and a shunt does not, so the difference between them *is* the ACS712's thermal error, and the thermocouple amp tells you the temperature that caused it. In the other direction the current sensors tell you when the SSR is switching, which is when the thermocouple's long leads pick up hum.

**What would kill it.** The ACS712's own text: *"Its zero point drifts with temperature and its noise floor is large relative to small currents — a ±30A part cannot usefully see"* small loads. And the MAX31855's: an open thermocouple *"silently reads 0°C and a PID loop responds by heating forever. Long unshielded leads pick up mains hum and SSR switching; twist the pair and add a 10nF across the inputs."*

**τ.** **Unknown** — the INA700's prose states no response time at all, so the time component scores zero and nothing is claimed about the timing. That is the honest outcome, not a penalty: the model will not invent a number.

**ESP32.** ! single-board-with-caveats — the ACS712 is 5 V and needs a divider or a 3.3 V variant. Hazards: `HotSurface`, `Mains`. 13 of 14 host boards.

#### 19 · FS3000 air velocity + Thermistor airflow (nasal) kit + INA700 power monitor — `S177` + `S218` + `S378`, $33

**Jointly infers:** `building-heat-loss`, `cost-per-use`.

**Mechanism.** Two airflow measurements through different physics — the FS3000 is a heated element read by convective cooling, the nasal kit is a bare bead thermistor read by the temperature difference the flow creates — scored **differential** on `flow-gas`. The FS3000's stated blind spot is below 0.5 m/s, where convection off its own heater dominates and the reading is mush; the bead NTC is unaffected by that particular failure because it has no heater of its own. The bead also supplies the temperature reference the FS3000's self-heating corrupts.

**What would kill it.** The FS3000's own text: *"Below about 0.5 m/s, natural convection off its own heater dominates and the reading is mush — which matters, because a stagnant room is precisely"* the case you care about. And the nasal kit's: *"It senses temperature difference, not airflow, so it detects breath PHASE and rate but tells you nothing about volume."* Neither part measures volume; the pair measures presence and direction of flow, not how much.

**τ.** **Unknown** — the INA700 again. The two flow parts are 5 s and 100 ms, both measured, but the model refuses to score a triple's separation when a member is unknown.

**ESP32.** ! single-board-with-caveats — the INA700 is an I²C part with **no `i2c_addr` recorded in the catalog**, so its address against the FS3000 is unknown rather than clear. Check before you build. Privacy `Identifiable`.

#### 20 · SCD30 NDIR CO2 + BMP280 budget barometer + SEN66 six-in-one air module — `S037` + `S192` + `S278`, $111.50

**Jointly infers:** `air-density`, `radon-risk-rising`.

**Mechanism.** A full indoor-air node where the barometer is the part that makes the other two honest: it feeds the SCD30's pressure register and the SEN66's CO2 cell, which inherits the SCD4x's pressure dependence. The SEN66 also brings PM, VOC, NOx and RH, so the CO2 channels get their humidity compensation from the same enclosure.

**What would kill it.** The SEN66's own text: *"It inherits every weakness of its parts. The CO2 cell carries the SCD4x's altitude and pressure dependence — leave the ambient-pressure register at sea-level default in Den"*ver and it is simply wrong. The BMP280 counterfeit problem from entry 14 applies here too, and the same false-positive humidity channel is scored twice in this row (once from the SCD30, once from the SEN66) — **subtract both.** 109 mA of draw, mostly the SEN66's fan and laser.

**τ.** `separated`, confidence `low` — barometer rate-derived.

**ESP32.** ✓ single-board. All 14 host boards. Hazards: `Asphyxiant`, `Laser`.

---

## The nine that were thrown out

Twenty-nine candidates were read; nine did not survive. Every one of them scored well.

| Rank | Combination | Why it was discarded |
|---|---|---|
| pair #1 | BMP280 + SEN66 (`S192`+`S278`), $71.50 | **The top-scoring pair in the run.** One of its two compensation channels is the counterfeit chip-ID false positive described in entry 14, and the other direction is real but ordinary. Strip the false channel and it is a worse version of entry 20. The highest score in the table rests partly on a sentence about buying fake parts. |
| pair #19 | TPMS receivers + STC31 (`S223`+`S279`), $38 | A TPMS receiver is a **radio that relays somebody else's pressure measurement** from inside a wheel. Its `pressure-absolute` is not ambient barometric pressure and cannot feed a CO2 cell's compensation register. The mechanism layer was tightened to stop receivers earning differential credit for measurements they only relay; the compensation layer was not, and this is the hole. |
| pair #41 | KY-037 + ADS1115 (`S209`+`S213`), $4 | The ADS1115 is credited with correcting the microphone for `mains-hum` because it lists `voltage`. It is an **analog-to-digital converter** — the thing that digitises the microphone, not an independent reference for what is wrong with it. Any generic ADC or fuel gauge that lists `voltage` becomes a universal corrector for everything fooled by supply noise. |
| pair #15 | MAX31855 + BL0940 (`S004`+`S381`), $16.50 | Scored a full **differential** shared measurand on `temperature-contact` — Seebeck effect against silicon bandgap, which is true — between a thermocouple tip that may be in a kiln and a die register inside a mains metering IC on the other side of an isolation barrier. Different mechanisms, different *places*. Fix 2 checks the physics and cannot check the geometry. |
| pair #16 | MAX31865 + INA700 (`S005`+`S378`), $19 | Identical failure to the row above. |
| pair #46 | MPU-6050 + BL0940 (`S072`+`S381`), $3.50 | The BL0940's die temperature is offered as the correction for the MPU-6050's `self-heating` and `temperature-drift`. The IMU's own text says its die register *"reads the die, typically 2-5C above ambient from self-heating, so it is a compensation input, not a room thermometer"* — and so is the BL0940's. Two compensation inputs do not make a reference. |
| triple #1 | MAX31855 + INA700 + LEM LA 55-P (`S004`+`S378`+`S382`), $54 | **The top-scoring triple in the run**, and it fails the same way as pair #15: the differential temperature claim is between parts that cannot occupy the same place. The current half of the claim (Hall against shunt) is genuine, which is why entry 18 keeps that half with a thermocouple whose job is to explain the Hall drift. |
| triples #2, #5 | …+ LEM IT 60-S ULTRASTAB (`S383`), $919 | Same failure, plus a $900 laboratory fluxgate transducer that no co-location test in this model would ever question — it has no bench keyword in its name and a difficulty below 5. Fix 6 does not catch it. |
| triple #28 | SCD41 + TPMS + STC31 (`S036`+`S223`+`S279`), $63 | The TPMS problem again. Worth reading anyway as the one place in this table where **Fix 6 visibly fires**: the TPMS→SCD41 channel is flagged `co_location: doubtful` for `no shared environment (['Indoor'] vs ['Harsh', 'Outdoor'])` and attenuated to 0.35. It caught the indoor/outdoor mismatch and still missed that the pressure is inside a tyre. |

Three failure patterns account for all nine: **a relay is not a measurement** (TPMS), **a die register is not a reference** (BL0940, INA700, ADS1115), and **different physics in different places is not a differential pair** (the thermocouple rows). None of the seven fixes addresses any of them directly, which is the honest state of the model.

---

## What changes when the physics layer lands

A parallel branch adds fourteen optional `px_*` fields to the schema — among them `px_measurand` (what the part is actually for), `px_effect` (the transduction effect, from a controlled vocabulary), `px_cross` (cross-sensitivities as `PHYSQTY` tokens) and `px_bandwidth` (a real −3 dB bandwidth or response time). **No record carries any of them today**, and `verify_combinations.py` asserts that: every number in this document came out of the prose fallback path, and the gate fails if that ever stops being true.

The engine is already wired for them as a preference chain — authored field first, prose second, never mixed within one channel, with a `source` field of `px` or `prose` on every compensation channel and counts of each in the run's `meta`. What would change:

| Component | Today | With `px_*` |
|---|---|---|
| compensation | 39 regex interferents over `fools` prose, **15% measured false-positive rate** | `px_cross` tokens matched against `px_measurand` through a 52-token controlled vocabulary — no regex, no prose |
| incidental capability | stem match over `n`/`meas`/`cat`/`sub`, 23% of listings flagged | `px_measurand` is the authored answer to exactly this question |
| transduction mechanism | 37 regex cues, **121 of 405 parts unknown** | `px_effect` from a controlled vocabulary, presumably for all of them |
| τ | 146 of 405 are `1/f_max` lower bounds at `low` confidence | `px_bandwidth` → τ = 1/(2πf₃dB) at `high` confidence |

**Would the Fix-3 false-positive rate largely go away? Yes — that specific rate would go to essentially zero, and it is the wrong thing to celebrate.** All six false positives in the sample of forty are failures of *reading English*: a negation the guard did not govern, a sentence about counterfeit chip IDs, "a loud bang" read as mechanical shock. A controlled vocabulary of cross-sensitivities does not have those failure modes, because it is not prose. What it inherits instead is whatever the person filling in `px_cross` decided, and the errors move from "the regex was fooled" to "the field is incomplete" — which is harder to measure, because a missing `px_cross` token produces no channel and therefore no evidence of its own absence. The 15% here is at least visible.

The three failure patterns that killed the nine rejects would be **partly** helped and not solved: `px_measurand` would say plainly that a TPMS receiver measures a radio packet, which kills that reject cleanly. Nothing in the field list says where a part is physically mounted, so "different physics in different places" survives untouched — that needs a deployment model this atlas does not have.

---

## Reproducing any of this

```
python3 combine.py --k 2 --top 25              # deduped pairs, exhaustive
python3 combine.py --k 2 --top 25 --no-diverse # every row, near-duplicates included
python3 combine.py --k 3 --top 10              # triples (candidate-generated, not exhaustive)
python3 combine.py --explain S008,S015         # the full derivation of one row
python3 combine.py --export                    # exports/combinations_{pairs,triples}.csv, _run.json
python3 verify_combinations.py                 # the release gate — recounts the top row independently
```

`--explain` is the audit path: every interferent with the sentence it was extracted from, every mechanism with the cue that matched it, every τ with the field and literal it came from, every incidental verdict with its reason, and the pin budget. If a row in this document disagrees with `--explain`, the document is wrong.
