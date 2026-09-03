# 10 — Resistive under-sink leak puck

**Incumbent:** A coin-sized plastic puck with two exposed metal electrodes on its underside, about
20 mm apart, a coin cell and a piezo buzzer. A resistor pulls one electrode toward the rail; when
water bridges the gap the divider crosses a comparator threshold and the buzzer sounds. The design
is as old as the doorbell and unchanged in principle since the first "water alarm" patents of the
1970s; the modern version adds a Wi-Fi radio and nothing else.
**Claims to detect:** A water leak under the sink.
**Actually measures:** The DC conductivity of whatever sits across a 20 mm gap on the cabinet floor
at one point, compared with one threshold — a threshold set with tap water, against a medium whose
conductivity spans four orders of magnitude.

## The gap
Water leaves a plumbing system continuously and arrives on the floor discontinuously, at whichever
low point the floor slopes to, after however long it takes to soak through a cabinet base. The puck
samples the arrival process, at one point, with a detector that also requires the water to be
dissolved-solids-rich enough to conduct. So there are four independent ways for a real leak to be
invisible: it evaporates as fast as it drips; it runs inside a wall, a floor void or the back of a
cabinet; the floor slopes away from the puck; or the water is clean enough not to trip the
threshold. And there is a fifth failure in the other direction — condensation, mopping water and
conductive dust all bridge the gap perfectly well — which is why every one of these ends its life
either silent or crying wolf. A leak is a *flow* fault, and the puck has no flow channel at all.

## What fools it
| Fools it | Why, physically | Atlas source |
| --- | --- | --- |
| A leak in a wall, a ceiling, or behind the cabinet | It only measures where the electrodes are, and the floor is the last place water reaches | `S141` `fools`: "It only sees water where the rope physically lies. Most expensive water damage starts inside a wall, above a ceiling or behind an appliance and reaches the floor hours or days later, by which time the flooring is gone — a rope is a last line, not an early warning." |
| Clean water | Conductivity, not water, is what closes the circuit; condensate and RO water are a few µS/cm | `S141` `fools`: "It also needs the water to conduct: air-conditioner condensate, distilled water and clean rainwater are a few microsiemens per centimetre and may not trip a threshold that was set with tap water." |
| Its own bias current | Continuous DC electrolyses the electrodes, so the device slowly destroys the measurement it makes | `S141` `fools`: "Continuous DC bias electrolyses the conductors, so cheap modules that simply pull the line up through a resistor corrode the rope where it stays damp and drift toward a permanent alarm within months; pulsed excitation makes it last years." |
| Condensation and household dust | The dry-state resistance falls over years until an ordinary humid night crosses the threshold | `S141` `fools`: "Humidity and dust are enough on their own — a rope behind a dryer or in a damp basement accumulates conductive dust until the dry-state resistance falls and an ordinary humid night triggers it." |
| Anyone who cleans under the sink | It gets kicked aside, and nothing about a dry reading tells you it moved | `S141` `fools`: "Someone will move it: the rope gets kicked aside when the washing machine is serviced and nobody notices, so a supervised design with a terminating resistor at the far end is the only way to know it is still connected and still where you put it." |
| A slow drip, in the other direction too | Even the obvious replacement — an inline turbine — cannot see the leak sizes that matter | `S138` `fools`: "It is a turbine, so below about 1 L/min the impeller does not turn and a dripping tap, a slow toilet fill or a pinhole leak — the exact things you bought it for — are completely invisible. This is why 'zero flow at 3 am' is a far better leak signal than 'a small flow'." |
| Latching | Once wet it stays alarmed until it dries, sometimes days later | `S141` `fools`: "And a wet event latches until it dries, sometimes days later, so 'leak cleared' is not a signal you can trust." |

## What the underlying phenomenon actually is
Water leaving the system, not water arriving on the floor. That has four independent signatures, and
the value comes from requiring more than one of them.

**Flow that should not be happening.** A leak anywhere downstream of the meter shows as non-zero
consumption when the house is empty — `Mechanical → Electrical · Hall effect` on a turbine, or an
optical pickup on the utility meter's disc.

**A pipe that stays cold.** A leak keeps mains-temperature water moving through a pipe that should be
static, so the pipe surface sits several degrees below the cabinet air and stays there.
`Thermal → Electrical · Thermoresistive` on a clamped probe, or `Thermal → Radiant · Blackbody
emission` for the no-contact version — the atlas maps that effect to area `e` explicitly as "pipe
surface".

**Structure-borne hiss.** A pressurised leak jets into the pipe wall and the pipe is a waveguide.
`Mechanical → Electrical · Piezoelectric` picks it up at two points and cross-correlation locates it.

**Air that is wetter than it should be.** Evaporating water raises the cabinet's absolute humidity
before any puddle forms — and the same measurement, run against the coldest surface, is what lets you
*distinguish* a leak from ordinary summer condensation instead of alarming on both.

**Pressure decay** is the fifth, and here the dataset lets you down — see the costs section.

## Proposed ESP32 stack
| Role | Part | `pn` | id | ~USD | Captures |
| --- | --- | --- | --- | --- | --- |
| Water leaving the system | YF-S201 flow sensor | `YF-S201 / FS300A` | `S138` | $5 | ~450 pulses/L on the incoming main. Its blind spot below 1 L/min is exactly why the signal used is *zero flow*, not *small flow* |
| The gate: is anyone home | LD2410 mmWave presence | `HLK-LD2410B/C` | `S067` | $5 | Holds presence on a motionless person, which a PIR cannot — the difference between "empty house" and "everyone asleep" |
| Pipe surface, cold and hot legs | DS18B20 digital temp probe | `DS18B20` | `S001` | $2.50 ×2 = $5 | Two probes on one 1-Wire bus, bedded in paste under insulation. A cold leg that never warms back up is a running leak |
| Cabinet air: dew point | SHT41 humidity + temp | `SHT41 / SHT40 / SHT45` | `S012` | $6 | ±1.8 % RH, ±0.2 °C. Absolute humidity rising with the doors shut is evaporating water |
| The coldest surface in the cabinet | MLX90614 IR thermometer | `MLX90614` | `S007` | $8 | Aim it once at the cold main. With the SHT41 this runs `condensation-watch`, so predicted sweating is not reported as a leak |
| Structure-borne leak hiss, ×2 | Piezo contact mic / disc | `27mm piezo disc` | `S091` | $0.50 ×2 = $1 | Two pickups bracketing the run, epoxied not taped. Feeds the correlator |
| Front end for the piezos | Charge amplifier for piezo sensors | `LMP7721 / TL072-based charge amp` | `G021` | $6 | `S091` `requires` clamp diodes and a high-impedance buffer; without a charge amp the reading changes when you change the cable |
| Ultrasonic leak signature (optional) | Acoustic emission (ultrasonic contact) | `Piezo + 40kHz front-end` | `S232` | $10 | A pressurised leak radiates at 40 kHz. `diff: 5` — envelope-detect, never sample the carrier |
| Last-resort confirm on the floor | Water leak rope sensor | `Leak rope / WLD modules` | `S141` | $10 | The incumbent's job, done with metres of coverage instead of a 20 mm gap, pulse-excited so it does not corrode itself |
| Actually stop it | Motorised ball valve | `1/2"-1" 12V motorised ball valve (CR-02/CR-05)` | `A010` | $20 | Full bore, holds position with power off, reports its state. `A010` `spark`: "detection without shutoff just tells you about the flood you are already having" |

**Board:** ESP32-S3 (`B003`, `ESP32-S3-WROOM-1 / S3-DevKitC-1`, $8) — chosen for the DSP
instructions and PSRAM the cross-correlation needs · **Sensor total:** ~$56 · **Build:** ~$84 with
the valve and board, against about $15 for a Wi-Fi puck.

## The fusion
**Edge:** `leak-by-context` (data/fusion.py)
**Math:** `Alarm when flow > 0 sustained > 10 min AND nobody-present > 30 min`
**Confound:** Washing machines and irrigation run legitimately when out: whitelist their schedules or
their flow signatures first.

**Supporting edges, both already in fusion.py.** `pipe-leak-correlator` locates it —
`Leak position from cross-correlation lag: x = (L − v·Δt)/2, v ≈ 1200–1400 m/s in water-filled metal pipe`
— with the confound that plastic pipe drops v to ~300–500 m/s, so you calibrate with a deliberate tap
at a known point first. `condensation-watch` suppresses the commonest false alarm —
`Risk when T_surface − T_dew < 1.5°C (T_dew via Magnus: γ = ln(RH/100) + 17.62·T/(243.12+T))` — so a
cold main sweating in August is predicted rather than alarmed.

**Why it beats the incumbent:** The puck reports an event that has already ruined the floor. This
reports the leak while the water is still inside the pipe, from four physics that fail for unrelated
reasons: flow, thermal, acoustic and hygrometric. `leak-by-context`'s own `why` puts the principle
exactly: "Water flowing is normal; water flowing in an EMPTY house is a burst pipe… most false alarms
are true readings in the wrong context." And the correlator turns "there is a leak somewhere" into a
metre-accurate position, which is the difference between one hole in the wall and five.

## What this costs you
- **Price and difficulty.** ~$84 against ~$15, and the difficulty is uneven: `S138` and `S001` are
  `diff: 1`, but `G021` and `S232` are both `diff: 5`. The acoustic channel is a real analog project.
- **The dataset cannot give you pressure decay.** The obvious fifth signature — isolate a section,
  watch the pressure fall — has no affordable part here. `S021` MPRLS ($15) is the only ported
  pressure sensor, and its `range` is "0-25 PSI absolute (0-172 kPa)", *below* typical household
  supply pressure of 40–80 PSI: it would sit pinned at full scale. The only in-range part is `S254`
  Gems 3100 4-20 mA transmitter at **$150**, which additionally needs a 24 V loop supply, a 150 Ω
  shunt and a clamp — `S254` `fools`: "if the shunt resistor ever goes open… the loop's full 24V
  compliance voltage appears across your ADC input and kills it." **State this as a gap: there is no
  cheap potable-water line-pressure sensor in this dataset.**
- **Privacy, and it is not small.** `S091` `privacy` is `Raw-imagery`, and its `fools` explains why:
  "It is a genuine contact microphone: stuck to a wall it picks up conversation in the next room, a
  privacy consequence nobody anticipates from a drum trigger." `S067` is `privacy: Aggregate` and
  "sees through plasterboard, doors and glass" — your leak detector knows when your neighbour is home.
- **Power.** `S067` is 80 mA continuous and `S138` 15 mA while flowing. This is a mains device; the
  puck runs three years on a coin cell.
- **The acoustic channel is the fragile one.** `S091` `fools`: "What it really measures is the bond:
  blu-tack, tape, cyanoacrylate and epoxy differ by more than 20 dB… and any bond that ages shifts
  your baseline." `S232` `consumable`: "Couplant is the consumable and it dominates repeatability.
  Silicone grease or ultrasound gel dries out in days to weeks and the reading falls as it does,
  which looks exactly like a machine getting healthier."
- **The flow meter has costs of its own.** `S138` `consumable`: plastic impeller and one bearing,
  "2-5 years on clean municipal water, far less on hard water." It restricts flow, and it "is not
  certified potable in most jurisdictions." An optical pickup on the existing utility meter is free
  and wets nothing — `S138` `substitutes` names it — but the dataset has no record for that pickup.
- **The shutoff is slow.** `A010` `fools`: "Travel takes seconds, so this is not an emergency shutoff
  for a burst pipe — it is a controlled shutoff… Valves that sit unused for months can seize;
  exercise them monthly in software."
- **Calibration and drift.** `S001` is `lifecycle: Clone-risk` and counterfeits miss ±0.5 °C by
  2–4 °C. `S007` `consumable`: "a fingerprint, kitchen grease film or dust changes the apparent
  emissivity and there is no way to compensate for it in software." `S012` is silicone-poisoned by
  RTV, cable insulation and some tapes — do not seal this cabinet with the wrong sealant.

## Verdict
Strong. This is the clearest of the three reinventions, because the incumbent is not a bad
implementation of the right measurement — it is the wrong measurement, and the right one
(`leak-by-context`) costs $10 in parts and is already an edge in the dataset. Confidence is high on
the flow-plus-presence channel, moderate on the thermal and hygrometric channels, and low on the
acoustic correlator, which is a `diff: 5` build whose repeatability depends on epoxy and couplant.
This would have to be true to pay off: that you can get a meter or a turbine onto the incoming main
at all. In a flat where the stopcock is behind a communal panel, the whole architecture collapses and
you are back to a $10 leak rope on the floor — which is still a better buy than the puck, because it
covers metres instead of 20 millimetres.
