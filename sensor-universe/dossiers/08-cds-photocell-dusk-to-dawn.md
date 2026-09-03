# 08 — CdS photocell dusk-to-dawn control

**Incumbent:** A cadmium-sulphide photoconductive cell potted into a translucent head on top of a
streetlight, garden light or nightlight. Photoconductivity in selenium was reported by Willoughby
Smith in 1873; the CdS cell became the cheap commodity form in the mid-twentieth century, and the
domestic dusk-to-dawn head has not changed since. The cell's resistance falls with light, a fixed
resistor makes it a divider, a comparator (or a bimetal heater in the oldest heads) switches the
lamp, and one feedback resistor sets the hysteresis so it does not chatter at the threshold.
**Claims to detect:** Dusk. "Turns on at sunset, off at sunrise."
**Actually measures:** The photoconductivity of a thin CdS film — integrated, uncalibrated, over
most of one hemisphere, weighted by a spectral response that peaks near 540 nm and is nearly blind
to infrared — compared against one resistor, with hysteresis set by a second resistor.

## The gap
Dusk is not a light level; it is a geometric event. The sun's elevation at a given place and instant
is computable to better than a minute from date, latitude and longitude, and has been for centuries.
The photocell instead measures irradiance at one point, which is the sum of the sun, the sky, the
moon, every artificial source in the hemisphere, and the lamp the cell is itself mounted under. It
therefore cannot separate "the sun has set" from "a cumulus passed" or "a car turned in". Worse, the
question the device is actually asked is not "is it dark?" but "does anyone need light here?" — a
question with two terms, illuminance *on the useful surface* and *presence*, of which the photocell
measures neither. A dusk-to-dawn head is a correct answer to a question nobody has.

## What fools it
| Fools it | Why, physically | Atlas source |
| --- | --- | --- |
| A passing cloud, and its own lamp's reflection | CdS has light-history memory and a decay of hundreds of ms to seconds, so a step change smears and the cell hunts around the threshold | `S049` `fools`: "It has memory: a cell stored in darkness reads several tens of percent different from an identical cell that has been in light, and takes minutes to settle. Decay back to dark resistance takes hundreds of milliseconds to seconds, so it smears fast events and cannot see chopped or modulated light." |
| A headlight, or any mains-lit neighbour | 100/120 Hz ripple rides on the divider output and pushes it across the comparator threshold | `S049` `fools`: "Mains-lit rooms put a 100/120Hz ripple on the output; average over a whole mains cycle or your threshold chatters." |
| Sodium, LED and incandescent light of the same apparent brightness | Its response peaks around 540 nm and is nearly blind to IR, so the spectrum of what is lighting it changes the answer | `S049` `fools`: "Its spectral response peaks around 540nm and it is nearly blind to infrared, so it badly under-reads incandescent, halogen and IR sources and over-reads green LEDs - it is not a lux meter and never was." |
| A dirty lens, a spider web, condensation | Surface leakage across the two electrodes is in parallel with the film, and it drifts one way only | `S049` `fools`: "Outdoors the bare cell fogs and the surface leakage across the two electrodes drifts the reading toward 'bright'." |
| Ageing | The film loses sensitivity, so the switch-on point walks later every year with no error indication | `S049` `consumable`: "None as such, but CdS cells lose sensitivity after years of strong UV; outdoors a bare cell also grows a leakage path across the electrodes from condensation" |
| Two "identical" units in the same street | ±50 % part-to-part spread within one batch, so no two heads agree on when dusk was | `S049` `fools`: "Part-to-part spread is enormous (+/-50% in one batch), so every cell needs its own calibration and cells are not interchangeable." |
| The hemisphere itself | Any wide-field photometer is dominated by the single brightest thing in its cone, not by the scene | `S045` `fools`: "Its field of view is wide (about +/-55 degrees), so one bright lamp anywhere in the hemisphere dominates a reading you believed was about the room." |
| Empty streets | It has no presence channel at all, so it burns all night for nobody | `S203` `fools`: "It senses CHANGE in far-infrared across its zones, so a person sitting perfectly still vanishes within seconds — that is physics, not a defect, and it is why every PIR-driven light eventually strands someone in the dark." (the failure the presence channel must itself avoid) |

## What the underlying phenomenon actually is
There are three quantities, and only two of them need a sensor. **Solar elevation** is *computed*,
not sensed: sin h = sin φ·sin δ + cos φ·cos δ·cos H, from a clock and a fixed latitude/longitude.
That alone replaces the entire photocell for the "is the sun down?" term, with no drift, no fogging
and no spectral error. What remains is **task illuminance** — the photopic light actually falling on
the pavement, road or bench people use, which is what decides whether the lamp is needed at all —
and **presence**, which decides whether it is needed *now*. Task illuminance is
`Radiant → Electrical · Photoelectric / photovoltaic` ("A photon with enough energy knocks an
electron free… current proportional to light"), done properly with a filtered photodiode and an
on-die ADC instead of a bare film. A spectral channel on the same path lets you *identify* the
source: daylight, the lamp's own return, and a passing headlight have different band ratios, so the
controller can subtract its own contribution instead of oscillating against it. Presence is
`Thermal → Electrical · Pyroelectric` ("Some crystals produce charge when their temperature
CHANGES… exactly why a PIR sees you walk past and goes blind when you sit still") cross-checked
against 24 GHz micro-motion radar, which has no entry in `physics.py`'s 22-effect grid — it is an RF
Doppler measurement and the grid does not cover it.

## Proposed ESP32 stack
| Role | Part | `pn` | id | ~USD | Captures |
| --- | --- | --- | --- | --- | --- |
| Task illuminance, moonlight to noon sun | VEML7700 high-accuracy lux | `VEML7700` | `S045` | $5 | 0.0036–120 000 lux, photopic, calibrated. Aim it *down* at the surface you are lighting, not up at the sky |
| Which light is this? | AS7341 11-channel spectral | `AS7341` | `S052` | $14 | 11 bands, 350–1000 nm plus a flicker channel — separates daylight from the lamp's own reflection, from a sodium neighbour, from a headlight |
| Presence, channel 1 | LD2410 mmWave presence | `HLK-LD2410B/C` | `S067` | $5 | Holds on a motionless person; 0.75 m distance gates let you exclude the road and keep the pavement |
| Presence, channel 2 (different physics) | Panasonic EKMC PIR (quality) | `EKMC1603111` | `S203` | $12 | 12 m, 102°×92°, 64 characterised zones — the independent channel that makes cross-validation meaningful |
| The clock that makes sunset computable | DS3231 precision RTC | `DS3231 / DS3231SN` | `G027` | $3 | ±2 ppm across power loss; its alarm output wakes the ESP32 at a computed time rather than every N seconds |
| Latitude, longitude and UTC, once | NEO-6M GPS | `u-blox NEO-6M (GY-GPS6MV2)` | `S157` | $8 | Commissioning only — power it for one fix, write lat/lon to NVS, never power it again. `lifecycle`: `EOL`, so treat it as optional |
| Dim, do not switch | High-power LED driver (constant current) | `MEAN WELL LDD-H / AL8860 / Recom` | `A019` | $10 | PWM-dimmable constant current, so "nobody here" means 20 % output rather than off |

**Board:** ESP32-C6 (`B006`, `ESP32-C6-WROOM-1 / C6-DevKitC-1`, $6) · **Sensor total:** ~$47 with
the GPS, ~$39 without · **Build:** ~$63 with the LED driver, against about $2 for a photocell head
(`S049` is $0.20 for the cell alone).

## The fusion
**Edge:** `presence-two-physics` (data/fusion.py)
**Math:** `Verified = both channels TRUE within a 5 s window; disagreement = log + keep watching`
**Confound:** The computation counts part TYPES — it cannot check the physics differ. YOU must: two
PIRs share failure causes and verify nothing; pick PIR + radar or thermal + ultrasound. Both channels
must respond in seconds — CO2-based presence is minutes too slow for the coincidence window.

**Second edge — `solar-geometry-gate` — new edge, not in fusion.py.** Maths mine:
`Need = (h_sun(φ, λ, t_UTC) < −6°) AND (E_task < E_min)` where
`sin h = sin φ·sin δ + cos φ·cos δ·cos H`, and
`Output = P_min + (P_max − P_min)·presence_verified`, with `E_task` the VEML7700 reading corrected
by subtracting the lamp's own spectral signature measured by the AS7341 at commissioning.

**Why it beats the incumbent:** The photocell's job is split into three terms that fail
independently. The sun term cannot be fooled by weather, dirt or ageing because nothing senses it.
The illuminance term is calibrated and photopic, so a sodium neighbour and an LED neighbour of equal
perceived brightness give the same number. And the presence term converts an all-night burn into a
duty cycle: the atlas's own field result for two-physics presence is "39 false triggers in 40 events
alone, zero when cross-validated." A dusk-to-dawn head cannot dim, cannot know the street is empty,
and cannot tell you it has gone blind.

## What this costs you
- **Price and complexity.** ~$63 against ~$2. A CdS head has two components and no firmware; this
  has six devices, two buses, a UART at 256 000 baud and a solar-position routine.
- **Power.** `S067` `pwr`: 80 mA, continuously. That is the whole design: this is a mains streetlight
  controller, not a battery garden light. `S045` is 45 µA and `S203` 170 µA, so if you drop the radar
  the node is coin-cell-viable — but then you have one presence channel and the fusion collapses.
  For a true battery build the atlas's low-power lux part is `S194` MAX44009 at 0.65 µA, $3.
- **Warm-up.** `S067` `warmup`: "A few seconds electrically, but allow ~30s of an empty, quiet room
  for the static-clutter baseline to settle - and repeat it after moving any furniture"
  `S203` `warmup`: "~30 s stabilisation after power-up before the output can be trusted".
- **Enclosure is the calibration.** `S045` `fools`: "Mounting it behind acrylic or a diffuser changes
  the calibration by 20-50%, so measure your own window rather than trusting the datasheet." The
  AS7341 is worse: its interference filters "blue-shift with the angle of incoming light."
- **Environment mismatch, stated plainly.** `S067` and `S203` are both `environment: Indoor` in the
  dataset. For a streetlight head they need a genuinely weatherproof, non-metallic, IR-transparent
  housing — and `S203` `fools` notes glass is opaque at 8–14 µm, so the PIR window must be HDPE, not
  the polycarbonate you would use for the lux sensor.
- **Privacy.** `S067` and `S203` are both `privacy: Aggregate`. The old head knew nothing about
  anyone; this one knows when the street outside your window is occupied, and `S067` "sees through
  plasterboard, doors and glass."
- **New drift mechanisms.** `G027` `fools`: "Backup batteries do die, and a node that silently
  reverts to 1 January 2000 corrupts a dataset quietly" — and here it would compute sunset for the
  wrong day. `S157` is `EOL` with `Clone-risk`-grade counterfeits.
- **A gap.** There is no outdoor-rated presence sensor in this dataset. Every presence part in area
  `d` is `Indoor`. The housing is your problem and the dataset gives you nothing to copy.

## Verdict
Strong on the sun term, strong on the presence term, moderate overall. Computing sunset removes the
incumbent's entire failure surface at zero marginal cost — that part is close to free and cannot
regress. The presence term is where the real energy saving lives and where the confidence drops: it
depends on getting `S067`'s distance gates set so the road is excluded, and on a weatherproof
housing the dataset does not describe. This would have to be true to pay off: that the light is
genuinely unoccupied for most of the night. On a busy pavement the duty cycle approaches 100 % and
you have spent $63 to buy a calibrated version of a $2 part.
