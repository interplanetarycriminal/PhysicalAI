# 02 — Bimetal / single-thermistor room thermostat

**Incumbent:** Two bonded metals with different expansion coefficients; the strip curls with
temperature and, past a set curvature, closes a contact. Warren S. Johnson patented the electric
room thermostat in Milwaukee in 1883 (the company became Johnson Controls); Honeywell's
mercury-switch-on-a-coiled-bimetal round thermostat made the mechanism domestic from 1953. The
modern version swaps the strip for a single 10 kΩ NTC bead and a microcontroller, but the sensing
geometry has not changed in 140 years.
**Claims to detect:** Whether the room is comfortable.
**Actually measures:** The temperature of one cubic centimetre of air, roughly 1.4 m up an interior
wall, inside a plastic case, next to its own electronics — and in the bimetal case, the temperature
of a metal strip in thermal contact with that wall.

## The gap
Human thermal comfort is a heat-balance problem with six inputs: air temperature, **mean radiant
temperature**, air speed, humidity, clothing insulation and metabolic rate. The thermostat measures
one of them, at one point, in the least representative place in the room. Radiant exchange is not a
correction to air temperature — it is roughly half of a seated person's sensible heat loss, and a
body facing a single-glazed window at 8 °C loses heat to it regardless of the air being at 21 °C.
Meanwhile the same 21 °C at 0.4 m/s of draught feels about 2 °C cooler than at 0.05 m/s, and at 70 %
RH versus 30 % the evaporative half of the balance changes entirely. The incumbent then runs the
boiler until its own one point reaches setpoint, which is why one room bakes, another is cold, and
everyone argues.

## What fools it
| Fools it | Why, physically | Atlas source |
| --- | --- | --- |
| Its own electronics | Self-heating raises the sensing element above room air; in an NTC divider it is a permanent positive offset | `S006` `fools`: "Self-heating is the built-in error: 3.3V across a 10k/10k divider puts ~0.27mW into the bead, and with a dissipation constant of 1-3 mW/°C that is 0.1-0.3°C in stirred air and up to 1°C in a still, sealed probe." |
| Two "identical" sensors disagreeing | The B-value is nominal, so a fleet of cheap beads cannot be compared to each other without calibration | `S006` `fools`: "two 'identical' beads matched at 25°C disagree by 1-2°C at 80°C — which is why a two-point calibration at ice and boiling matters." |
| Sun on the wall, or the sensor's own mounting | It reports the temperature of its own body, not of the room it is nominally in | `S001` `fools`: "It reports the temperature of its own probe tip, so a stainless probe strapped to a pipe mostly reads room air unless it is bedded in paste and insulated. Outdoors in sun it reads solar gain, not air temperature, without a radiation shield." |
| A cold window that the thermostat cannot see | Radiant loss to a cold surface is invisible to any air-temperature sensor | `data/physics.py` TRANSDUCTION, **Blackbody emission**: "Everything above absolute zero radiates, and both how MUCH and what COLOUR depend only on temperature… This is why you can read temperature from across a room without touching anything." |
| The one-point assumption itself | A room is a temperature *field*, not a scalar | `microclimate-grid` `why` (data/fusion.py): "A single thermostat reads one point of a field that varies 5°C across a room." |
| Replacement risk: the thermal camera behind a lid | Glass and plastic are opaque at 8-14 µm, so an enclosure window destroys the MRT channel | `S161` `fools`: "Glass and most plastics are opaque to this band, so it cannot see through a window — it reads the window." |
| Replacement risk: the air-speed channel at room draught levels | Below its own convective floor, a hot-wire sensor is reading its own plume | `S177` `fools`: "Below about 0.5 m/s, natural convection off its own heater dominates and the reading is mush — which matters, because a stagnant room is precisely where you want a trustworthy small number." |

## What the underlying phenomenon actually is
The quantity to measure is **operative temperature** — the area-weighted blend of air temperature
and mean radiant temperature that a body actually exchanges heat with — and, one step further, the
PMV heat balance that adds air speed, humidity, clo and met. Three transduction paths in
`data/physics.py` cover it. **Thermal → Radiant · Blackbody emission** gives mean radiant
temperature without touching anything: a thermopile array reads the surface temperature of every
wall, window and radiator in its cone, and MRT is the view-factor-weighted average of those
surfaces. **Thermal → Electrical · Seebeck effect** is what those thermopile arrays physically are —
stacked junctions, as the atlas puts it, "thermopiles inside every IR thermometer." **Mechanical →
Thermal · Convective cooling** gives air speed from a heated element. Humidity is a capacitive RH
element on the same die as the air thermometer. And the incumbent's own mechanism is in the grid
too, as **Thermal → Mechanical · Thermal expansion**: "Bond two together and the strip bends — the
original thermostat."

## Proposed ESP32 stack
| Role | Part | `pn` | id | ~USD | Captures |
| --- | --- | --- | --- | --- | --- |
| Mean radiant temperature | MLX90640 thermal camera | `MLX90640 (32x24)` | `S161` | $45 | 768 surface temperatures across the room — walls, glazing, radiator, floor. This is the MRT channel and the whole point of the rebuild |
| Air temperature + humidity | SHT41 humidity + temp | `SHT41 / SHT40 / SHT45` | `S012` | $6 | Dry bulb and RH, ±0.2 °C / ±1.8 % RH, on a cable stub away from the board |
| Air speed | FS3000 air velocity | `FS3000-1005/1015` | `S177` | $26 | Draught, honestly, above ~0.5 m/s; below that it reports its own convection and you must say so |
| Occupancy + ventilation | SCD41 true CO2 | `SCD41 / SCD40` | `S036` | $25 | Whether anyone is in the room to be comfortable, and (via `ach-co2-decay`) the room's real air-change rate |
| Spot surface probe | MLX90614 IR thermometer | `MLX90614` | `S007` | $8 | Aim it at the coldest corner once, permanently — the `condensation-watch` and `mould-forecast` input |
| Room field, 3 points | DS18B20 digital temp probe | `DS18B20` | `S001` | $2.50 ×3 = $7.50 | Stratification and draught path on one wire — the `microclimate-grid` input |
| Cheaper MRT swap for `S161` | Grid-EYE AMG8833 thermal array | `AMG8833` | `S071` | $35 | 64 pixels instead of 768; adequate for wall/window MRT, useless for people at 4 m |

**Board:** ESP32-S3-WROOM-1 / S3-DevKitC-1 (`B003`, $8) — the MLX90640 needs 1 MHz I²C plus RAM for
a 768-word frame *and* its calibration parameter set, which is the one place a C3 will hurt. ·
**Sensor total:** ~$117.50 · **Build:** ~$125.50.

## The fusion
**Edge:** `feels-like` — Feels-like temperature station (data/fusion.py)
**Math:** `T<10°C: wind chill (Environment Canada 2001 formula); T>27°C and RH>40%: heat index
(Rothfusz regression, invalid below that); between: dry bulb`
**Confound:** The anemometer must see YOUR microclimate: a sheltered patio and the rooftop differ by
the whole wind-chill term.

**Second edge — `new edge — not in fusion.py`:** `operative-temperature`, pattern `compensation`,
requires `[('temperature-remote', 1), ('temperature-contact', 1), ('humidity-relative', 1),
('wind-speed', 1)]`, provides an indoor-comfort analogue of `feels-like-temperature`.
**Math (new, mine):** `T_mrt = (Σ_i F_i·T_i⁴)^(1/4) over the thermopile array's pixels, F_i = pixel
solid angle / 2π; T_op = A·T_air + (1−A)·T_mrt with A = 0.5 for v < 0.2 m/s, 0.6 for 0.2–0.6 m/s,
0.7 for 0.6–1.0 m/s (ASHRAE 55 Table); control on T_op, not T_air`
**Confound (new, mine):** The array's view factors are only correct if you know where it is pointing
and what fraction of its cone is window versus wall — a badly aimed sensor produces a confidently
wrong MRT. Emissivity is the second killer, and the atlas is blunt about it in `condensation-watch`:
"a shiny surface lies to the IR thermometer by 20×."
**Why it beats the incumbent:** `feels-like` alone already fixes two of the six comfort inputs the
bimetal ignores, using parts costing $32. The new operative-temperature edge fixes the biggest one:
a room at 19 °C air with warm walls and a room at 22 °C air with a cold window can have the same
operative temperature, and only the second one currently gets heated. Controlling on T_op means the
boiler stops chasing an air number that nobody's body cares about — and the same array tells you
*which surface* is the problem, which is an insulation decision rather than a heating decision.

## What this costs you
- **Price.** ~$126 against $25 for a decent programmable thermostat, or $3 for a bimetal one. And $8
  of the parts (`S001` ×3) exist purely to prove the room is a field.
- **Placement becomes an engineering problem.** The MLX90640 must have a clear line of sight —
  `S161` `requires`: "1MHz I2C, and enough RAM for the frame plus the calibration parameter set",
  and `S071` `requires` "A completely unobstructed line of sight. Ordinary glass, acrylic and
  polycarbonate are opaque in the 8-14um band…" No pretty enclosure window. No dust on the lens.
- **Warm-up and self-heating everywhere.** `S161` `fools`: "The chip's own temperature enters the
  calculation, so it needs minutes to stabilise after power-up and drifts if mounted next to
  anything warm." `S012` `fools`: "an ESP32 on the same board raises the temperature channel 1-3°C,
  and because RH is computed against that temperature, 1°C of error is roughly 6 points of RH."
  `S177` `warmup`: "~5s for the micro-heater to reach equilibrium after power-up; the first second
  of data is nonsense".
- **The air-speed channel is honest only above ~0.5 m/s.** Indoor comfort draughts live at 0.05–0.3
  m/s. `S177` is the dataset's only solid-state air-velocity part and it explicitly cannot resolve
  that band; the alternative it names is a cup anemometer (`S121`, $12) with a 0.5–1.4 m/s stall
  threshold, which is worse indoors. **This is a genuine gap: the dataset carries no room-scale
  low-velocity anemometer.** Report the draught term as "below threshold" rather than as zero.
- **Power.** `S161` at 20 mA and `S177` at 10 mA plus the SCD41's 205 mA measurement peak put this
  firmly on mains. The bimetal thermostat needs no power at all.
- **Drift and calibration.** `S001` is `Clone-risk` and its counterfeits miss spec by 2-4 °C; `S006`
  needs a `Two-point` calibration; `S036` needs its altitude register set and its automatic
  self-calibration disabled in a continuously occupied room, or it "slowly under-reads by hundreds
  of ppm while looking perfectly healthy."

## Verdict
Strong, and the strongest of the four on physics: mean radiant temperature is a first-order comfort
term that the incumbent structurally cannot see, and $45 buys it outright. Confidence high on the
MRT channel and the humidity channel, low on the draught channel — the dataset has no part that
measures room-scale air speed honestly, so the PMV calculation will run on an assumed still-air
value most of the time. This would have to be true to pay off: that your building actually has
radiant asymmetry worth chasing. In a well-insulated modern flat with warm walls, T_op ≈ T_air and
the whole rebuild collapses back into a $6 SHT41.

