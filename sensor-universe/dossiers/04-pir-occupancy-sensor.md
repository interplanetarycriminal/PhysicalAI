# 04 — PIR occupancy sensor

**Incumbent:** A lithium tantalate or PZT pyroelectric element, split into two (or four) opposed
segments, behind a moulded polyethylene Fresnel lens that carves the field of view into a fan of
alternating beams. As a warm body crosses from one beam into the next, heat shifts from one element
to the other and the difference signal swings; a comparator turns that swing into a digital pulse.
Domestic from the 1970s and effectively unchanged since.
**Claims to detect:** Whether a room is occupied.
**Actually measures:** The **time derivative** of the far-infrared flux landing on a segmented
pyroelectric crystal. It is a change detector with a high-pass filter built into its physics — no
motion across a lens boundary, no signal, regardless of how many people are in the room.

## The gap
Pyroelectricity is not a heat sensor; it is a *heat-change* sensor. `data/physics.py` says it in one
line: "Some crystals produce charge when their temperature CHANGES — not when it is high. That is
exactly why a PIR sees you walk past and goes blind when you sit still." Everything the PIR gets
wrong follows from that single fact. Stillness is indistinguishable from absence, so a person
reading in a chair is an empty room within the hold time. In the other direction, *any* moving
far-IR gradient is a person: a sunlit patch crawling across the floor, warm air off a radiator, a
cat. And because the pyroelectric element's signal is proportional to the temperature *contrast*
between body and background, the sensor's sensitivity collapses on a hot day — exactly when the room
is occupied and the cooling matters. The device is not a bad occupancy sensor; it is an excellent
motion sensor being asked the wrong question.

## What fools it
| Fools it | Why, physically | Atlas source |
| --- | --- | --- |
| A person sitting still | Pyroelectric charge is proportional to dT/dt at the element; no crossing, no signal | `S065` `fools`: "It senses change in mid-IR, not presence, so a person sitting still disappears within the hold time - the single most complained-about behaviour in home automation, and it cannot be fixed in software." |
| Sunlight, radiators, HVAC plumes, headlights, cats | All of these move far-IR gradients across the lens boundaries, which is the entire signal | `S065` `fools`: "it fires on sunlight moving across the lens or a sunlit patch crossing the floor, warm air from a heating or A/C vent, a radiator or incandescent lamp switching on, headlights and a warm bonnet through a window, cats, and the thermal draught of a door opening onto a cold hallway." |
| Its own Wi-Fi radio | Unshielded high-impedance FET front end rectifies the 2.4 GHz transmit burst | `S065` `fools`: "RF is the underrated one: an unshielded HC-SR501 sitting beside an ESP32 antenna triggers on the Wi-Fi transmit burst, which is why a grounded metal can or 15cm of separation is standard practice." |
| A hot room | Body-to-background IR contrast is what it measures, and it goes to zero near skin temperature | `S065` `fools`: "Sensitivity collapses as ambient approaches skin temperature - above about 30C the body-to-background contrast vanishes and it is nearly useless in a hot conservatory." |
| Replacement risk: radar sees too much | 24 GHz passes through plasterboard, doors and glass, and micro-motion is everywhere | `S067` `fools`: "It sees through plasterboard, doors and glass, so someone in the hallway, a neighbour in the next flat, or a person in the garden outside a window all show as 'present' - and it sees through ceilings too, so a ground-floor unit may be tracking someone upstairs." |
| Replacement risk: the thermal array at range | 64 pixels averages a distant person with the wall behind them | `S071` `fools`: "a person at 4m occupies roughly one pixel, and that pixel averages them with the wall behind - a distant human reads as a 24C blob against a 21C wall, a 3C signal against a +/-2.5C accuracy spec." |
| Replacement risk: ToF in sunlight | Ambient IR raises the noise floor until zones return error codes instead of ranges | `S060` `fools`: "a sunlit window or a halogen downlight in the field raises the noise floor and zones start returning status codes instead of distances. Statuses 5, 10 and 255 must be filtered out or a moving sunbeam becomes a detected fall." |
| Replacement risk: radar track IDs are not people | Coordinates jitter and IDs are reassigned on re-acquisition | `S068` `fools`: "Track IDs are not identities - two people crossing paths swap IDs, and anyone who stands still long enough is dropped and re-acquired as a new ID, which silently breaks any dwell-time or queue-length logic built on ID continuity." |

## What the underlying phenomenon actually is
The phenomenon is **a human body persistently occupying a volume**, and it leaves four independent
physical traces, none of which requires the person to move. It is a ~100 W heat source at 37 °C core
with ~1.8 m² of skin (`ANCHORS`, `data/physics.py`) radiating in the 8–14 µm band — that is
**Thermal → Radiant · Blackbody emission**, read absolutely by a thermopile array rather than
differentially by a pyroelectric one. It displaces air with a chest that moves 12–20 times a minute
— that is a phase modulation on a 24 GHz reflection, **RF** micro-motion. It occupies space — that
is an optical **time-of-flight** range, since light travels 30 cm per nanosecond and a chair with a
person in it is nearer than a chair without. And it exhales roughly 40 000 ppm CO₂ against 420 ppm
outdoors, so "One person raises a closed room's CO₂ measurably within minutes". Four traces, four
uncorrelated failure modes — which is exactly the condition under which coincidence gating works.

## Proposed ESP32 stack
| Role | Part | `pn` | id | ~USD | Captures |
| --- | --- | --- | --- | --- | --- |
| Micro-motion presence | LD2410 mmWave presence | `HLK-LD2410B/C` | `S067` | $5 | Breathing-scale motion: knows a still, sleeping person is there. The channel PIR structurally cannot have |
| Position and count | LD2450 multi-target tracking radar | `HLK-LD2450` | `S068` | $12 | X/Y and speed for up to 3 targets — zone logic instead of a single room-wide boolean |
| Absolute thermal | Grid-EYE AMG8833 thermal array | `AMG8833` | `S071` | $35 | 64 absolute temperatures: a still body is still warm. Deliberately too coarse to identify anyone (`privacy`: Aggregate) |
| Depth zones | VL53L5CX 8x8 ToF array | `VL53L5CX / VL53L7CX` | `S060` | $20 | 64 range zones — seat-occupied versus seat-empty, and a physics that shares no failure mode with radar |
| Slow ground truth | SCD41 true CO2 | `SCD41 / SCD40` | `S036` | $25 | Minutes-latency but essentially unfoolable: CO₂ does not rise for a sunbeam. Also gives ACH via `ach-co2-decay` |
| Free fifth channel | Wi-Fi CSI sensing (the router IS the sensor) | `ESP32 CSI firmware` | `S228` | $0 | Presence and breathing from the radio already in the board — no extra hardware, and no extra bill |
| Keep the incumbent | HC-SR501 PIR motion | `HC-SR501` | `S065` | $1.50 | 50 µA idle. As the *wake* channel it is excellent; it just must not be the *decide* channel |
| Reference tier | Omron D6T-32L 1024-pixel thermopile array | `D6T-32L-01A` | `S343` | $200 | 32×32 absolute temperatures if 64 pixels is not enough |

**Board:** ESP32-S3-WROOM-1 / S3-DevKitC-1 (`B003`, $8) — two hardware UARTs for the two radars (the
LD2410 runs at 256 000 baud, beyond comfortable software serial), I²C for the array and the ToF, and
enough flash for the VL53L5CX's ~84 KB firmware blob. · **Sensor total:** ~$97 (~$98.50 with the PIR
kept as the wake channel) · **Build:** ~$105 · **Minimum honest two-physics build:** `S067` + `S071`
+ `B005` = ~$43.

## The fusion
**Edge:** `presence-two-physics` — Two-physics presence verifier (data/fusion.py)
**Math:** `Verified = both channels TRUE within a 5 s window; disagreement = log + keep watching`
**Confound:** The computation counts part TYPES — it cannot check the physics differ. YOU must: two
PIRs share failure causes and verify nothing; pick PIR + radar or thermal + ultrasound. Both
channels must respond in seconds — CO2-based presence is minutes too slow for the coincidence
window.

**Payoff edge:** `unoccupied-burn` — Empty-room energy auditor.
**Math:** `Waste = ∫ P dt while unoccupied, per room per week; rank rooms by wasted kWh`
**Confound:** Fridges and servers SHOULD run unoccupied: subtract each room's always-on baseline
first or the kitchen wins every audit unfairly.

**Fleet edge:** `desk-utilisation` — Space-utilisation truth map.
**Math:** `Per-zone occupied-hours histograms; utilisation = occupied / available hours per zone per
week`
**Confound:** Sensor placement bias: a PIR facing a walkway counts traffic as occupancy. Aim each
zone's sensor at the seat, not the aisle.

**Why it beats the incumbent:** The `presence-two-physics` `why` field carries the number that
matters: "The field result in this atlas: 39 false triggers in 40 events alone, zero when
cross-validated." PIR false-triggers on moving heat; radar false-triggers on fans, curtains and the
neighbour through the wall; a thermal array false-triggers on a laptop and a sunlit floor. Those
three failure causes are physically unrelated, so requiring two of them to agree within 5 s removes
almost all of them — while the *false-negative* problem, the still person, is fixed outright by the
radar and the thermal array, neither of which needs motion. Note the confound honestly: SCD41 is
minutes too slow for the 5 s coincidence window, so it is a slow arbiter that decides disputes over
tens of minutes, not a coincidence channel.

## What this costs you
- **Price and power.** ~$105 against $1.50, and the power budget is the real cost: `S067` draws 80
  mA, `S068` 100 mA, `S060` ~70 mA while ranging, and the SCD41 peaks at ~205 mA. The HC-SR501 idles
  at **50 µA**. This is a mains-powered node; the incumbent runs for years on a coin cell.
- **Duty-cycling does not rescue it.** `S060` `fools`: "The firmware reload at each power-up makes
  deep-sleep duty cycling expensive, which is why battery builds of this rarely work out."
- **Commissioning becomes real work.** `S067` `fools`: "Zone and gate gating is therefore not an
  optimisation, it is what makes the sensor usable at all, and nearly every 'my mmWave never turns
  off' complaint is factory-default sensitivities plus an unset maximum distance gate." `S067`
  `warmup`: "allow ~30s of an empty, quiet room for the static-clutter baseline to settle - and
  repeat it after moving any furniture". `S068` `requires`: "A rigid mount at a known height and
  orientation - the coordinates are in the module's own frame, so any tilt rotates every zone
  boundary you defined."
- **Enclosure constraints.** `S071` `requires`: "A completely unobstructed line of sight. Ordinary
  glass, acrylic and polycarbonate are opaque in the 8-14um band". `S067` `requires`: "A
  non-metallic path to the room: metal, foil-backed plasterboard and wire mesh block it completely."
  You cannot satisfy both with one pretty box without care.
- **Privacy moves, but not to zero.** Every part here is `privacy`: Aggregate except the ToF
  (`None`), so nothing is identifiable and no imagery leaves the room — better than a camera. But
  the radar sees through the wall into a neighbour's flat, which is a privacy question about *them*,
  not you, and gating is the only answer.
- **The free channel is not production-ready.** `S228` `fools`: "The technique is genuinely exciting
  and genuinely not production-ready; treat demonstrations, including your own, with suspicion."
  `calibration`: Reference. Treat CSI as a research channel, not as one of your two votes.
- **Interpolation is a lie.** Both `S071` and `S060` warn that upsampling 8×8 to a smooth image
  "adds no information and mainly disguises how coarse the data really is." Do not ship the pretty
  heat map.

## Verdict
Strong, and the cleanest win of the four: the incumbent's core defect — invisibility of a motionless
person — is not a tuning problem but a consequence of pyroelectric physics, and $5 of radar removes
it outright. Confidence high; this is the dataset's deepest area and the coincidence result is
stated as a measured field number rather than an argument. The $43 two-physics build (LD2410 +
AMG8833) captures most of the gain and is the one I would actually build; the $105 version buys
zone-level utilisation data, which is worth it in an office and pointless in a hallway. What would
have to be true: that you commission the radar's range gates properly and mount it where it cannot
see through a wall — an uncommissioned LD2410 is worse than the PIR it replaced, because it is
confidently wrong instead of obviously blind.

