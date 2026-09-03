# 09 — Sprinkler-timer rain sensor (cork disc stack)

**Incumbent:** A stack of compressed cork or hygroscopic-fibre discs held in a vented plastic cup on
a bracket at the eaves. Rain wets the discs, they swell along the stack axis, and past a set
expansion they push open a normally-closed microswitch wired in series with the irrigation
controller's common. A knurled cap sets how many millimetres of swell it takes. The Mini-Clik-class
device dates to the early 1980s and is still the default rain shutoff sold with clockwork and
solid-state sprinkler timers alike.
**Claims to detect:** That it has rained enough, so the sprinklers should skip today.
**Actually measures:** The linear expansion of a stack of cork discs — a lagged, saturating integral
of recent wetting minus recent drying at one point under one eave, with the drying half of the
integral set by the ventilation of the cup rather than by anything happening in the soil.

## The gap
Irrigation is a mass balance: water in (rain plus irrigation) minus water out (evapotranspiration
plus drainage) equals what the root zone holds. The cork sensor measures none of those four terms.
It is a wetness *event* detector with a mechanical time constant, which means it saturates — once
the discs are fully swollen, 2 mm and 40 mm of rain are indistinguishable — and it clears on a
drying schedule set by wind and sun on the cup, not by soil. So it can suppress irrigation for two
days after a 1 mm shower that never reached the roots, and permit irrigation the morning after 30 mm
because the cup happened to sit in a sunny, windy spot. It also says nothing at all about the demand
side: a still, humid 18 °C week and a windy, dry 32 °C week pull wildly different amounts of water
out of the same soil, and the cork disc cannot tell them apart because it never gets wet in either.

## What fools it
The dataset carries no cork rain sensor. These quotes come from the atlas parts that share its
physics — a surface-wetness plate (`S231`), a leaf-wetness board (`S127`) and a tipping bucket
(`S123`) — and each failure listed is one the cork stack has too.

| Fools it | Why, physically | Atlas source |
| --- | --- | --- |
| Dew, fog, a spider web, a fallen leaf | Anything that puts water or a dielectric on the sensing surface is indistinguishable from rain | `S231` `fools`: "Dew, fog, a spider web holding moisture, a slug crossing the plate, a fallen leaf and a hand waved 10cm above it all register as wet." |
| Its own drying rate, not the rainfall | The reset is an evaporation problem at the sensor, uncoupled from the soil | `S231` `fools`: "Drying time rather than rainfall sets when it clears, so a sheltered plate reports 'raining' for an hour after the rain stopped, and a windy plate clears while it is still raining." |
| Any rain past its threshold | It saturates, so "enough" and "far too much" are the same output | `S231` `fools`: "It saturates: once the surface is covered, heavy rain and drizzle read identically, so it can tell you when a shower started but never how much fell." |
| Where and how you mounted it | Siting moves the answer more than weather does, and there is no reference to check against | `S127` `fools`: "Mount the same board at 30 degrees instead of 45 and the wet-hours count changes… the number only means something relative to a threshold you established yourself over a season." |
| Silent blockage | A blocked vent or a clogged funnel reads exactly like dry weather, indefinitely | `S123` `fools`: "Leaves, pine needles, pollen mats and spider webs block the funnel silently: the record simply reads zero, which is indistinguishable from dry weather, and nobody notices for months." |
| Drizzle and mist | Below the mechanical threshold, real precipitation is invisible; above it, nothing is measured | `S123` `fools`: "And anything under one tip is invisible: drizzle, dew and mist that never accumulate 0.28 mm are simply never recorded." |
| Residue and ageing | Hygroscopic contamination shifts the baseline permanently and slowly, so it looks like a trend | `S127` `fools`: "Dust, pollen and dried spray residue are hygroscopic, so a dirty board reads wet at 80% RH with no liquid water present — and because this develops over weeks it looks exactly like a genuine seasonal trend." |

## Where the dataset is thin — say this out loud
This is the weakest of the ten areas. The atlas contains **exactly one** rain gauge (`S123` tipping
bucket, $12), **one** DIY capacitive wetness plate (`S231`, $3, explicitly a home-etched PCB), and
**one** leaf-wetness part (`S127`, $15). There is **no commercial optical or piezo rain sensor
record at all** — the Hydreon RG-15 class appears only inside `S123`'s `substitutes` string, not as
a part you can cite an `id`, `pn` and `usd` for. If you want a no-moving-parts rain instrument, this
dataset cannot sell you one. The strong move is therefore not to buy a better rain sensor. It is to
stop sensing rain as the primary signal and compute the water balance instead, which the dataset
*does* support properly, through the `et0-station` edge and a real matric-potential probe.

## What the underlying phenomenon actually is
Reference evapotranspiration, ET₀ — the atmospheric demand for water, in millimetres per day — plus
measured rainfall in, plus the root zone's actual matric potential as the truth check. ET₀ closes an
energy balance, so it needs four transduction paths and not one. **Radiant → Thermal · Absorption**
("Anything that absorbs radiation warms up… absorb the radiation and measure the heat") gives the
radiation term through a pyranometer, which dominates ET₀ in summer. **Mechanical → Thermal ·
Convective cooling** ("Moving fluid carries heat away from a warm body faster than still fluid") is
the aerodynamic term, delivered here by a cup anemometer rather than a hot wire. A capacitive RH
element plus a bandgap thermometer give the vapour-pressure deficit, and a barometer gives the
psychrometric constant. The truth check is different physics again: the Watermark's gypsum-buffered
granular matrix equilibrates with soil suction and reports it as resistance —
`Thermal → Electrical · Thermoresistive`'s electrical cousin, and the only quantity in the whole
stack that a root actually experiences.

## Proposed ESP32 stack
| Role | Part | `pn` | id | ~USD | Captures |
| --- | --- | --- | --- | --- | --- |
| ET₀ radiation term | Pyranometer (solar irradiance) | `DFRobot SEN0562 (Gravity)` | `S128` | $60 | 0–1800 W/m², silicon-cell class ±5 % clear-sky. The term that dominates summer ET₀ |
| ET₀ aerodynamic term | Anemometer cup sensor | `WH-SP-WS01 / Davis 6410` | `S121` | $12 | Wind speed at 2 m; passive reed pulses into PCNT |
| ET₀ vapour-pressure deficit | SHT31 weatherproof probe | `SHT31 / SHT35` | `S015` | $12 | ±2 % RH, ±0.2–0.3 °C behind a sintered cap — needs a radiation shield, not just weatherproofing |
| ET₀ psychrometric constant | BMP390 precision barometer | `BMP390 / BMP388` | `S016` | $10 | Station pressure at 3.2 µA; also gives you storm context for free |
| Water in — actual depth, not an event | Tipping bucket rain gauge | `WH-SP-RG / Davis` | `S123` | $12 | 0.2794 mm per tip, cumulative, on an interrupt. Still the incumbent's honest cousin |
| The truth check — what the roots feel | Watermark granular-matrix soil water sensor | `Watermark 200SS + adapter` | `S186` | $45 | 0–239 kPa matric potential; irrigation decisions live between 10 and 80 kPa |
| Mandatory Watermark correction | DS18B20 digital temp probe | `DS18B20` | `S001` | $2.50 | Soil temperature at the same depth. `S186` `requires` calls this "equally non-negotiable" |
| Did the valve actually deliver? | YF-S201 flow sensor | `YF-S201 / FS300A` | `S138` | $5 | ~450 pulses/L, so "open for 12 minutes" becomes "delivered 41 L" |
| Analog front end | ADS1115 / ADS1015 16-bit ADC | `ADS1115 (16-bit) / ADS1015 (12-bit)` | `G015` | $3 | The Watermark's H-bridge divider and the pyranometer's analog output both need better than the ESP32 SAR ADC |
| Close the loop | Solenoid valve (water) | `1/2" 12V normally-closed solenoid valve` | `A009` | $8 | The actuator. `A010` motorised ball valve ($20) if you are on a gravity-fed tank — see costs |

**Board:** ESP32-C6 (`B006`, `ESP32-C6-WROOM-1 / C6-DevKitC-1`, $6) · **Sensor total:** ~$161.50 ·
**Build:** ~$175.50 with the valve and board. **Cut-down:** swap `S128` for `S044` BH1750 ($2.50) and
divide lux by ~120 per `S128` `substitutes` — sensor total falls to ~$104, at ±20 % clear-sky and
"useless under cloud or artificial light."

## The fusion
**Edge:** `et0-station` (data/fusion.py)
**Math:** `FAO-56 Penman-Monteith ET₀ (or Hargreaves ET₀ = 0.0023·Ra·√ΔT·(T+17.8) when only temperature is available)`
**Confound:** The radiation term dominates in summer: a dusty or shaded pyranometer silently halves
ET₀ and you under-water in exactly the week it matters.

**Second edge — `soil-water-budget` — new edge, not in fusion.py.** Maths mine:
`D(t) = D(t−1) + Kc·ET₀(t) − P_eff(t) − I(t)`, clamped at 0, where `D` is root-zone depletion in mm,
`P_eff` is tipping-bucket rainfall less runoff, and `I` is delivered irrigation from `∫ flow dt`.
Irrigate when `D > MAD·TAW` **and** the Watermark confirms `ψ_soil > 40 kPa`; run for
`t = D / (precip_rate · efficiency)` and verify against the flow meter, alarming if delivered
volume misses the target by more than 20 % (a stuck valve, a burst line, or an air-filled meter).

**Why it beats the incumbent:** The cork sensor can only ever veto. This computes how much water the
garden lost and how much to put back, then confirms with an independent measurement that the soil
agrees and a third that the valve actually opened. The `et0-station` `why` field is blunt about it:
"How much to water is not how dry the soil FEELS — it is how much water the atmosphere pulled out.
Four measurements close the energy balance agriculture actually runs on; this is the equation behind
every commercial irrigation controller worth owning." The rain gauge stays in the stack, but demoted
from decision-maker to one term in a budget.

## What this costs you
- **Price.** ~$175 against ~$30 for a cork sensor, or ~$120 for a whole clockwork controller with
  one bundled in. `S128` alone is a third of the build.
- **Two long warm-ups before any of it means anything.** `S186` `warmup`: "A new sensor must be
  wetted and dried through 2-3 cycles before it settles, and needs about a week in the ground for
  soil-to-sensor contact to establish…" `S015` `warmup`: the cap "slows the 63% step response to
  ~20-30s."
- **Consumables and service, everywhere.** `S186` `consumable`: the gypsum wafer "dissolves slowly —
  expect 3-7 years in ordinary soil, markedly less in saline soil." `S121` `consumable`: "Cheap cups
  get sticky within 2-3 outdoor years — the failure is a rising start-up threshold, not a dead
  sensor." `S123` `consumable`: the funnel "needs clearing of leaves, pollen and insects every few
  months." `S128` `consumable`: "Expect a few percent per year of soiling drift and plan a
  recalibration every ~2 years…"
- **Calibration burden.** `S186` is `One-point` but only after AC excitation is built correctly —
  `requires`: "You MUST alternate the polarity… DC excitation polarises the electrodes and
  electrolyses the block, destroying the sensor within weeks." `S128` is the dataset's only
  `Periodic`-calibration part in this stack. `S138` is `One-point` and needs a bucket and a stopwatch.
- **Siting is now an engineering job.** `S121` `fools`: "Siting dominates everything else: any
  obstacle within about ten times its own height upwind ruins the reading…" `S015` outdoors and
  unshielded "reads 5-15 °C high, and since RH is referenced to that temperature the humidity number
  is garbage too." `S128` needs level mounting and a clear horizon.
- **The valve has a hard precondition.** `A009` `fools`: "Servo-assisted valves need minimum inlet
  pressure — on a gravity-fed tank they simply do not open, which catches out most rainwater
  projects." On a rain barrel you must spend $20 on `A010` instead.
- **Power.** Mains or a real solar panel. `S015` 800 µA, `S128` <5 mA, `S138` 15 mA while flowing,
  and the solenoid coil ~500 mA at 12 V continuously while open. The cork sensor draws nothing.
- **The `S128` record has a known defect.** Its own `note` says it "merges a ~$60 silicon-cell
  Gravity unit with a ~$225 Apogee SP-110, which are different instruments with different accuracy
  classes and different interfaces." Budget for the $60 part and expect silicon-cell spectral error.

## Verdict
Strong on the physics, moderate on the build. Replacing an event detector with a mass balance is the
right move and the dataset supports it properly — `et0-station` is the equation commercial
controllers already run, and the Watermark closes the loop with the one quantity roots actually
experience. Confidence is high on ET₀ and on the soil-tension check, and lower on the rain term,
because the atlas offers a single tipping bucket that "always under-reads, never over" and no
alternative. This would have to be true to pay off: that you irrigate enough to care. On a 20 m²
lawn watered twice a week the cork sensor's errors cost a few pounds a year and this stack never
repays $175. On an orchard, a vineyard row, or anywhere water is metered or scarce, it repays in a
season — and the flow-verification channel alone will find a leak the incumbent cannot see.
