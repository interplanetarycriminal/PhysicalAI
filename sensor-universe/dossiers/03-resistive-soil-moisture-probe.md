# 03 — Two-nail resistive soil moisture probe

**Incumbent:** Two galvanised nails, or a fork-shaped tinned-copper PCB, pushed into soil with a DC
voltage across them and one resistor forming a divider. The output is an ADC count. The design is a
direct descendant of the Bouyoucos gypsum block (1940) with the gypsum — the entire point of the
original — removed.
**Claims to detect:** How wet the soil is, and therefore whether the plant needs watering.
**Actually measures:** The bulk DC electrical conductivity of the path between the two electrodes,
which is dominated by the concentration of dissolved ions in the pore water, not by the amount of
water. Because it runs on DC, it is also a two-electrode electrolysis cell that consumes itself
while it measures.

## The gap
Water is a poor conductor; salt water is a good one. A resistive probe therefore reads *salinity ×
wetness*, and cannot separate the two factors, so a fertigation event makes dry soil look wet and
rainwater on a leached bed makes wet soil look dry. Worse, plants do not respond to how much water
is present — they respond to how hard they must pull to get it, which is **matric potential** (soil
water tension, in kPa), and to how hard the atmosphere is pulling water out of their leaves, which
is **vapour pressure deficit**. Two soils at 25 % volumetric water content can differ a hundredfold
in tension; a sandy soil at 12 % is comfortable and a clay at 25 % is at wilting point. The probe
measures a third quantity that correlates with neither, and then destroys its own electrodes doing
it.

**Dataset honesty note:** the atlas carries **no record for the two-nail resistive probe itself**.
The closest first-party statement about it is in `data/inference_notes.py`, and the
corrosion/electrolysis mechanism is documented in the gypsum-block and Watermark records, which
share the electrode physics.

## What fools it
| Fools it | Why, physically | Atlas source |
| --- | --- | --- |
| Fertiliser, manure, saline irrigation water | Conductivity scales with ion concentration; water content is only one factor in the product | `plant-thirsty` (data/inference_notes.py) `fools`: "Cheap resistive soil probes corrode away within weeks and measure salinity as much as water; use capacitive ones." |
| Its own excitation voltage | DC across two electrodes in an electrolyte is electroplating; the electrodes polarise and then dissolve | `S357` `fools`: "Never read it with DC. A steady voltage polarises the electrodes and electrolyses the block; you will watch the reading drift upward over days and the block physically degrade within weeks." |
| The soil type it happens to be in | Any moisture number is soil-specific and non-transferable | `plant-thirsty` `fools`: "Even capacitive readings are meaningless across different soils without per-soil calibration, because they respond to dielectric constant, which varies with soil type and compaction." |
| The whole framing of the measurement | Content is not the scheduling variable | `plant-thirsty` `fools`: "The metric agriculture actually schedules on is soil water TENSION, not water content — how hard roots must pull, rather than how much water is present." |
| Temperature, on any resistive probe | Ionic mobility rises with temperature, so resistance falls with no change in water | `S357` `fools`: "Resistance falls roughly 3% per degree, so a block at 10C and one at 25C at identical tension read differently - bury a temperature sensor with it." |
| Air gaps you cannot see | Shrink-swell pulls soil off the probe and you measure the dielectric or resistance of air | `S129` `fools`: "Air gaps are invisible and fatal — after the soil dries and shrinks away from the blade… you are measuring the dielectric of air; the reading looks convincingly dry and only recovers after a watering settles the soil back against the board." |
| Replacement risk: even the tension sensor is salinity-sensitive | The gypsum buffer that tolerates salt is the part that dissolves | `S186` `fools`: "It is a resistance sensor with a gypsum buffer, so anything that changes soil salinity changes the reading — a fertigation event, a manure application or saline irrigation water will make dry soil look wet — and the very buffer that gives it salinity tolerance is the part that slowly dissolves away." |

## What the underlying phenomenon actually is
Two phenomena, and the plant sits between them. On the soil side it is **matric potential**: the
energy required to pull water out of the capillary and adsorbed films holding it, measured in kPa
and spanning roughly −10 kPa (field capacity) to −1500 kPa (permanent wilting). On the atmosphere
side it is **vapour pressure deficit** and, integrated over a day, **reference evapotranspiration**
— the water the sky pulled out of the crop, which is what actually has to be replaced. The
transduction paths in `data/physics.py`: **Chemical → Electrical · Electrochemical** is what the
incumbent is accidentally doing and must stop; **Thermal → Electrical · Thermoresistive** gives the
soil temperature that every resistive tension reading needs; **Mechanical → Electrical ·
Capacitive** ("Capacitance is proximity sensing for matter itself" in `MOVES`) gives water content
at 70 MHz, where the dielectric constant of water (~80) swamps that of soil solids (~4); and true
TDR moves that same measurement to gigahertz, where salinity stops mattering. **Mechanical → Thermal
· Convective cooling** is the route the atlas lists for sap flow and dual-probe heat-pulse water
content — measuring water by how it carries heat, not how it carries charge.

## Proposed ESP32 stack
| Role | Part | `pn` | id | ~USD | Captures |
| --- | --- | --- | --- | --- | --- |
| Soil water tension — the scheduling variable | Watermark granular-matrix soil water sensor | `Watermark 200SS + adapter` | `S186` | $45 | 0–239 kPa: how hard roots must pull. AC-excited, so it does not eat itself |
| Soil temperature at the same depth | DS18B20 soil temp spear | `DS18B20 in steel spear` | `S132` | $5 | Non-optional: the Watermark kPa equations are temperature-corrected at ~1-3 %/°C |
| Water content trend, cheaply | Capacitive soil moisture v2 | `Capacitive Soil v1.2/2.0` | `S129` | $2 | The wetting/drying *shape* between irrigations, and a cross-check that the tension sensor still has soil contact |
| Air temperature + RH (VPD) | SHT31 weatherproof probe | `SHT31 / SHT35` | `S015` | $12 | Vapour pressure deficit — the atmospheric half of the plant's water balance |
| ADC for the two analog channels | ADS1115 / ADS1015 16-bit ADC | `ADS1115 (16-bit) / ADS1015 (12-bit)` | `G015` | $3 | The ESP32's own ADC is not good enough for a 1–200 kΩ resistance ratio |
| ET₀ tier: wind | Anemometer cup sensor | `WH-SP-WS01 / Davis 6410` | `S121` | $12 | The aerodynamic term of Penman-Monteith |
| ET₀ tier: solar | Pyranometer (solar irradiance) | `DFRobot SEN0562 (Gravity)` | `S128` | $60 | The radiation term, which dominates ET₀ in summer |
| Reference tier, if you need truth | METER TEROS 21 soil water potential | `METER Group TEROS 21` | `S356` | $290 | Matric potential with no dissolving consumable and no salinity sensitivity |
| Reference tier, water content | True TDR soil water content probe | `Acclima TDR-315H` | `S358` | $395 | Genuine sub-nanosecond TDR: "the laboratory method, shrunk into the probe" |
| Plant-side truth | Point dendrometer (stem diameter) | `DIY point dendrometer: Invar frame + linear potentiometer` | `S361` | $70 | Daily stem shrinkage — water stress visible before wilting and often before the soil sensors notice |

**Board:** ESP32-C3-MINI-1 / C3-DevKitM-1 (`B005`, $3) — two GPIO for the Watermark's
alternating-polarity excitation, one for 1-Wire, I²C for the ADC and the RH probe. · **Sensor total
(core four):** ~$64 · **Build (core + `G015` + board):** ~$70 · **Build with the ET₀ tier:** ~$142 ·
**Reference tier:** add $290–$755.

## The fusion
**Edge:** `et0-station` — Evapotranspiration (irrigation truth) (data/fusion.py)
**Math:** `FAO-56 Penman-Monteith ET₀ (or Hargreaves ET₀ = 0.0023·Ra·√ΔT·(T+17.8) when only
temperature is available)`
**Confound:** The radiation term dominates in summer: a dusty or shaded pyranometer silently halves
ET₀ and you under-water in exactly the week it matters.

**Supporting edge:** `soil-moisture-tc` — Temperature-corrected soil moisture.
**Math:** `Correct raw counts by the probe's measured temperature coefficient (typ. 0.1–0.3%/°C),
learned from a 24 h constant-moisture log`
**Confound:** Fast rain during the calibration day corrupts the learned coefficient — pick a dry 24
h, or learn it under a cover.

**Third edge — `new edge — not in fusion.py`:** `tension-gated-irrigation`, pattern
`context-gating`, requires `[('water-tension', 1), ('evapotranspiration', 1)]`.
**Math (new, mine):** `Irrigate when Ψ_soil ≤ Ψ_trigger (crop-specific, typ. −40 kPa vegetables /
−80 kPa vines) AND ΣET₀ − Σrain since last event ≥ 60 % of the root zone's readily available water;
dose = (ΣET₀ − Σrain) / irrigation efficiency, capped at field capacity`
**Confound (new, mine):** The Watermark is blind above about −10 kPa, which is exactly the
field-capacity region, so the *dose* cap has to come from the ET₀ budget rather than from the
tension sensor — and a sensor that has lost soil contact reads permanently dry and will irrigate
forever. Require the capacitive channel to move after every irrigation, or declare the tension probe
faulty.
**Why it beats the incumbent:** The two-nail probe answers "is the resistance below my threshold",
where the threshold was set by eye on one soil, on one day, before the electrodes started
dissolving. The fusion answers two separate questions with two independent physics: the soil says
whether the plant can still get water, and the sky says how much it will lose tomorrow.
`et0-station`'s `why` field puts it plainly: "How much to water is not how dry the soil FEELS — it
is how much water the atmosphere pulled out." Requiring both to agree means a hot windy day triggers
pre-emptive irrigation while a cool humid week does not, and a fertiliser application no longer
reads as rain.

## What this costs you
- **Price.** $70 against about $2 for two nails, and $142 for the version that closes the energy
  balance. The reference tier is $290–$755 and is genuinely better; you should know that before
  pretending the $70 build is equivalent.
- **Consumables, still.** You have not escaped the dissolving electrode, only slowed it. `S186`
  `consumable`: "The gypsum wafer inside dissolves slowly — expect 3-7 years in ordinary soil,
  markedly less in saline soil or with frequent aggressive wet/dry cycling." `S129` `consumable`:
  "One season to a few years buried; the failure is water wicking up the PCB into the header, which
  drifts the reading for weeks before the pins corrode through."
- **AC excitation is mandatory, not optional.** `S186` `requires`: "You MUST alternate the polarity
  — two GPIO driving the sensor through a series resistor, or a proper H-bridge — in bursts of a few
  milliseconds. DC excitation polarises the electrodes and electrolyses the block, destroying the
  sensor within weeks." Get this wrong and you have rebuilt the incumbent at 22× the price.
- **Installation is most of the accuracy.** `S186` `fools`: "installing it as a slurry-packed plug
  in a correctly sized hole is most of the skill and most of the failures." A badly installed $45
  sensor is worse than a well-installed $2 one, because you will trust it.
- **Latency.** `S186` "equilibrates over hours, so it will never confirm that a valve opened." Any
  closed-loop control has to be dosed open-loop from the ET₀ budget and merely *verified* by tension
  days later.
- **Blind spots at both ends.** `S186` below ~10 kPa "has almost no resolution, which is exactly the
  range where over-watering happens"; `S357` is blind above −30 kPa; `S356` saturates above −9 kPa.
  Nothing in the dataset under $200 measures the wet end well.
- **Calibration burden.** `S186` is `One-point`, `S129` is `Two-point` *in the actual soil*, `S128`
  is `Periodic`. The pyranometer needs cleaning or it silently halves ET₀.

## Verdict
Strong — the strongest reinvention of the four in terms of measuring a *different and correct*
quantity rather than the same quantity better. Tension plus ET₀ is what commercial irrigation
actually runs on, and $70 buys a defensible version of it. Confidence high that it beats the
incumbent (which is close to a null instrument), moderate that the numbers are transferable between
sites: the Watermark's salinity sensitivity, hours-long equilibration and wet-end blindness are
real, and in a cracking clay or a coarse sand it can lose contact and read dry forever. This would
have to be true to pay off: that you install to a slurry, bury a temperature probe at the same
depth, and never once put DC across an electrode.

