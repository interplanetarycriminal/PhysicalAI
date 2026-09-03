# `sensor-universe/firmware` — the atlas, running

The first firmware for this repository. It takes three **fusion edges** out of
`sensor-universe/data/fusion.py` and turns each into an ESP32 program that
measures the parts the atlas names, computes the quantity the atlas's `math`
field defines, and prints both the number **and** whether the reading can be
trusted.

Every formula lives once, in `physlib/physlib.h` — header-only, pure C++, no
`Arduino.h`, no `Wire.h`. The three examples include it, and so does the
host-side test, so the arithmetic that runs on a desktop is the identical
arithmetic that runs on the board. This is HANDOFF.md **Phase 4 Task 4.3**,
implemented.

Nothing here has been run on hardware. Read
[Untested on hardware](#untested-on-hardware) before you believe any of it.

---

## The three edges

### 1. `condensation-watch` — "Condensation forecaster"

*provides* `condensation-risk` (EMERGENT — no catalog sensor claims it).
Highest-scoring edge in the atlas on the ranking used to pick these three.

**math** (verbatim from `fusion.py`):

> Risk when T_surface − T_dew < 1.5°C (T_dew via Magnus: γ = ln(RH/100) +
> 17.62·T/(243.12+T))

**confound** (verbatim from `fusion.py`):

> Emissivity: a shiny surface lies to the IR thermometer by 20× (Anti-Catalog
> II). Put a strip of matt tape at the cold spot and aim at that.

Parts: SHT41 (air temperature + RH) and MLX90614 (surface temperature, without
touching the surface). Source: `src/condensation_watch.cpp`.

The emissivity confound is not decidable from a single IR reading — a shiny
target simply returns the wrong number with no signature — so it is carried as
a standing warning on every result. What *is* checkable is checked: an indoor
spot more than 15 K below or 5 K above air temperature is flagged as a probable
reflection. That threshold is this firmware's heuristic, not an atlas number,
and it says so in the code.

### 2. `ach-co2-decay` — "CO2-decay ventilation meter"

*provides* `air-changes-hour` (EMERGENT). Joint-highest score.

**math** (verbatim):

> ACH = ln((C₁−C_out)/(C₂−C_out)) / Δt[h], C_out ≈ 420 ppm, after the room
> empties

**confound** (verbatim):

> Anyone re-entering mid-decay corrupts the fit (gate on presence); wind-driven
> infiltration makes ACH weather-dependent, so log the fits against wind and
> you get the infiltration curve as a bonus.

Parts: one SCD41. Source: `src/ach_co2_decay.cpp`.

Two slices of this confound are machine-detected: **CO2 rose or stayed flat**
across the window (somebody re-entered, or the room never emptied), and a **fit
window shorter than 15 minutes** (too few points against the SCD41's
±(40 ppm + 5 % of reading)). Wind-driven infiltration needs an anemometer, so
it stays in the standing text.

### 3. `air-density-live` — "Live air-density computer"

*provides* `air-density` (EMERGENT).

**math** (verbatim):

> ρ = (P_dry·M_d + P_vap·M_v)/(R·T); P_vap from RH × saturation pressure
> (Magnus)

**confound** (verbatim):

> Sensor self-heating biases T by up to 1°C on combo boards (BME280's known
> flaw) — read fast, sleep long, or mount the thermometer separately.

Parts: one BME280. Source: `src/air_density_live.cpp`.

Self-heating **is** machine-detectable given a thermally separate thermometer:
`physlib::air_density_live()` takes an optional reference temperature and flags
the reading when the combo board sits more than 1 K above it. The example uses
its own cold-start reading as that reference and is explicit about the
limitation (a genuine ambient rise trips it too). Pass an SHT41 on a flying
lead — the `condensation-watch` edge already has one — for the strict version.

The example also performs the bring-up check the BME280's catalog record
demands: it reads the chip ID and **refuses to compute ρ** if the die answers
`0x58` (a BMP280, which has no humidity element) instead of `0x60`.

---

## Bill of materials

Prices are the atlas's own `usd` field — typical breakout street price in USD,
not a live quote. Catalog ids refer to `sensor-universe/data/`.

| Edge | Part | Catalog id | `pn` | USD | I2C address | Breakouts | Library (pinned) |
|---|---|---|---|---|---|---|---|
| condensation-watch | SHT41 humidity + temp | `S012` | SHT41 / SHT40 / SHT45 | **6** | `0x44` (fixed; `-BD1B` variant is `0x45`) | Adafruit 5776 STEMMA QT | `adafruit/Adafruit SHT4x Library @ 1.0.5` |
| condensation-watch | MLX90614 IR thermometer | `S007` | MLX90614 | **8** | `0x5A` (default; reprogrammable in EEPROM) | GY-906 module, Adafruit 1747 | `adafruit/Adafruit MLX90614 Library @ 2.1.6` |
| ach-co2-decay | SCD41 true CO2 | `S036` | SCD41 / SCD40 | **25** | `0x62` (fixed) | Adafruit 5190, SparkFun Qwiic SCD41 | `sensirion/Sensirion I2C SCD4x @ 1.1.0` |
| air-density-live | BME280 climate combo | `S013` | BME280 | **6** | `0x76` with SDO→GND (`0x77` on Adafruit boards) | GY-BME280, Adafruit 2652 | `adafruit/Adafruit BME280 Library @ 2.3.0` |
| | | | | **45 total** | four distinct addresses, no conflict | | |

`Adafruit BusIO`, `Adafruit Unified Sensor` and `Sensirion Core` arrive as
declared transitive dependencies and are deliberately not listed in
`platformio.ini`. Adafruit's SHT4x library also declares `Adafruit SH110X` and
`Adafruit SSD1306` — display libraries used only by its own examples. They are
downloaded and never compiled into this firmware.

All three BOMs share one bus, which is the point: the SCD41's record requires
the ambient-pressure register to be set at boot, and the BME280 in edge 3 is
exactly the part that supplies that number.

---

## Wiring

**3V3 only, on every part.** See [Power](#power-and-pull-ups) below —
the MLX90614 breakout is *not* 5V-logic-safe.

### ESP32-S3 devkit (DevKitC-1 class) — `esp32-s3-devkitc-1`

| signal | S3 pin | SHT41 | MLX90614 (GY-906) | SCD41 | BME280 |
|---|---|---|---|---|---|
| SDA | **GPIO8** | SDA | SDA | SDA | SDA / SDI |
| SCL | **GPIO9** | SCL | SCL | SCL | SCL / SCK |
| 3V3 | 3V3 | VIN / VDD | VIN (**not 5V**) | VDD (+100 µF) | VIN / VCC |
| GND | GND | GND | GND | GND | GND |
| address | — | fixed `0x44` | fixed `0x5A` | fixed `0x62` | **SDO → GND ⇒ `0x76`** |

### Classic ESP32 devkit (WROOM-32) — `esp32dev`

| signal | ESP32 pin | SHT41 | MLX90614 (GY-906) | SCD41 | BME280 |
|---|---|---|---|---|---|
| SDA | **GPIO21** | SDA | SDA | SDA | SDA / SDI |
| SCL | **GPIO22** | SCL | SCL | SCL | SCL / SCK |
| 3V3 | 3V3 | VIN / VDD | VIN (**not 5V**) | VDD (+100 µF) | VIN / VCC |
| GND | GND | GND | GND | GND | GND |
| address | — | fixed `0x44` | fixed `0x5A` | fixed `0x62` | **SDO → GND ⇒ `0x76`** |

Nothing else differs between the two boards. This kit uses no ADC, no 1-Wire,
no pulse counting and no analog, so the classic ESP32's "ADC2 dies with Wi-Fi"
trap and its input-only pins 34–39 never come up. That is the practical payoff
of the pure-I²C constraint.

These GPIOs are the *variant defaults* from `arduino-esp32`
(`variants/esp32/pins_arduino.h`: SDA 21 / SCL 22;
`variants/esp32s3/pins_arduino.h`: SDA 8 / SCL 9), but S3 board vendors vary, so
each example **defines its pins explicitly** with `#if CONFIG_IDF_TARGET_ESP32S3`
and calls `Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000)` rather than trusting
the no-argument form. If your S3 board documents different I²C pins, change the
two `#define`s at the top of the example.

Ground: one common GND, star from the devkit's GND pin. Keep the whole bus
under ~30 cm of dupont wire.

### Power and pull-ups

- **SHT41** — 3V3. `1.1–3.6 V`; 3.6 V is the absolute maximum. Never wire the
  bare part to a 5 V rail.
- **MLX90614** — **3V3, and this one matters.** The catalog record marks it
  `logic_3v3: False`. On a 5V-fed GY-906 the module's own bus pull-ups sit at
  5 V, which puts 5 V on SDA/SCL and therefore on the ESP32's GPIOs. Power the
  module from 3.3 V.
- **BME280** — 3V3. `1.7–3.6 V`; bare modules without a regulator die on 5 V.
- **SCD41** — 3V3, **and budget the current.** It draws ~205 mA peaks during a
  measurement. Give it a 3.3 V regulator rated for 250 mA and **100 µF of bulk
  capacitance at its VDD pin**, or a measurement coinciding with a Wi-Fi
  transmit will brown out the ESP32. A regulated Qwiic/STEMMA breakout
  (Adafruit 5190, SparkFun Qwiic SCD41) accepts 3–5 V and may instead be fed
  from the board's 5V/VUSB pin, keeping the peak off the LDO. Pick one
  deliberately.
- **Pull-ups.** Every breakout carries its own 4.7 kΩ pull-ups. Four boards in
  parallel gives ~1.2 kΩ (six gives ~780 Ω) — too strong, and the bus stops
  working reliably. **Keep the pull-ups on exactly one or two breakouts and
  remove or cut the jumpers on the rest**, targeting an effective 2.2 kΩ–4.7 kΩ
  to 3V3 on each of SDA and SCL. For a single-edge build (edge 1 = two boards,
  edge 3 = one board) the stock pull-ups are fine as they are.
- **Bus speed: 100 kHz**, set explicitly in every example. The MLX90614 speaks
  **SMBus, not plain I²C**; some drivers need clock-stretch tolerance and it
  behaves badly sharing a bus with parts that stretch SCL. If `0x44`, `0x62` or
  `0x76` vanish from a bus scan the moment `0x5A` joins, the MLX90614 is the
  culprit — move it to a second `Wire1` instance on its own pins. Both boards
  have two I²C peripherals.

### Placement the firmware cannot fix

- **SHT41 self-heating.** An ESP32 on the same board raises the temperature
  channel 1–3 °C, and RH is computed against that temperature, so 1 °C of error
  is roughly 6 points of RH — i.e. a wrong dew point. Mount it on a flying lead
  away from the ESP32 and the regulator.
- **MLX90614 field of view.** The standard part sees roughly 90°, so at 1 m it
  averages a ~2 m circle. Treat distance-to-spot as about 1:1, aim close, and
  apply the edge's own confound: matt tape on the target.
- **SCD41.** Set the ambient-pressure register at boot (`AMBIENT_PRESSURE_PA` in
  the example, or the BME280's reading). Its automatic self-calibration assumes
  the room reaches ~400 ppm weekly, which is false in a continuously occupied
  room.

---

## Building

PlatformIO Core, Arduino framework. The platform is pinned to an exact
release — `espressif32 @ 6.13.0` — rather than floating, and every library is
pinned to an exact version.

```sh
cd sensor-universe/firmware

pio run                            # all six embedded environments
pio run -e condensation-s3         # one of them
pio run -e condensation-s3 -t upload
pio device monitor -b 115200
```

| environment | edge | board | source compiled |
|---|---|---|---|
| `condensation-s3` | condensation-watch | `esp32-s3-devkitc-1` | `src/condensation_watch.cpp` |
| `condensation-esp32` | condensation-watch | `esp32dev` | `src/condensation_watch.cpp` |
| `ach-s3` | ach-co2-decay | `esp32-s3-devkitc-1` | `src/ach_co2_decay.cpp` |
| `ach-esp32` | ach-co2-decay | `esp32dev` | `src/ach_co2_decay.cpp` |
| `airdensity-s3` | air-density-live | `esp32-s3-devkitc-1` | `src/air_density_live.cpp` |
| `airdensity-esp32` | air-density-live | `esp32dev` | `src/air_density_live.cpp` |
| `native` | — | host | `test/test_physlib/test_physlib.cpp` |

Each environment's `build_src_filter` compiles exactly one example plus the
shared header, so the three programs never see each other's `setup()`.

### Host-side tests

```sh
pio test -e native
```

27 Unity test cases over `physlib.h`, run on the desktop with no board
attached. The expected values come from outside this repository — published
psychrometric tables, the ICAO standard atmosphere, and arithmetic done by
hand — so a wrong formula fails instead of agreeing with itself:

- Magnus dew point at 20 °C/50 % → 9.3 °C, 25 °C/60 % → 16.7 °C,
  30 °C/80 % → 26.2 °C, and T_dew ≡ T at 100 % RH.
- ACH of a 1400 → 800 ppm decay over 1 h with C_out = 420 ppm →
  ln(980/380) = 0.947380 h⁻¹, plus a second hand-computed case at a different
  C_out and window.
- Air density of dry air at 15 °C / 101325 Pa → 1.225 kg/m³, the ICAO
  standard sea-level value, within 0.002 kg/m³ (the tolerance is explained in
  the test: ICAO defines its figure with slightly different values of `M_d` and
  `R` than the CIPM constants used here).
- Humid air must be *lighter* than dry air at the same P and T — the classic
  sign error.
- Every invalid-input path: RH of 0 or 101 %, temperature at absolute zero,
  Δt ≤ 0, C₁ ≤ C_out, a CO2 rise instead of a decay, a vapour pressure larger
  than the total pressure.
- Both machine-detectable confounds, in the fired and not-fired directions.

The suite was checked against deliberate mutations: changing the Magnus
coefficient from 17.62 to 17.50, inverting the CO2 ratio, or perturbing the
molar mass of dry air each fail three test cases.

### Note on `verify_build.py`

`sensor-universe/verify_build.py` is a structural release gate for a built
`.xlsx` workbook — it opens a spreadsheet with `openpyxl` and checks sheets,
rows and formula lineage. It does not apply to firmware and was not run here.

---

## Untested on hardware

**No part of this firmware has been executed on a physical ESP32, and no sensor
has been read.** What has actually been verified is only this: all six embedded
environments compile and link cleanly (`pio run`, no warnings from the project
sources), and the 27 host-side tests pass (`pio test -e native`). Compilation
proves the library calls exist with the signatures used; it proves nothing
about the bus, the parts, or the numbers coming off them.

Check these on a real board, roughly in this order.

**Bus and addressing**

1. Run an `i2cdetect`-style scan first. Expect `0x44` (SHT41), `0x5A`
   (MLX90614), `0x62` (SCD41), `0x76` (BME280). A BME280 breakout that answers
   at `0x77` needs `ADDR_BME280` changed in `src/air_density_live.cpp`.
2. Scan again **after** adding the MLX90614 to a populated bus. If any other
   address disappears, the SMBus part is disturbing the bus — move it to
   `Wire1`. This is the single most likely hardware surprise in the kit.
3. Confirm the ESP32-S3 board really uses GPIO8/GPIO9 for I²C. Vendors differ.
4. Confirm the pull-up total: with four breakouts in parallel the bus may need
   jumpers cut on two of them.

**Per-edge sanity**

5. `condensation-watch`: breathe on the SHT41 — RH should rise and the dew
   point with it. Aim the MLX90614 at a mug of ice water; the margin should
   collapse and the risk flag assert. Then aim at bare metal and watch the
   emissivity heuristic fire: that is the confound detector doing its job, not
   a fault.
6. `ach-co2-decay`: confirm the SCD41 answers `getSerialNumber()` and that
   `setAmbientPressure()` returns 0. The first useful ACH figure needs a real
   20-minute decay in an empty room — nothing shorter is a measurement.
   Deliberately walk back in mid-window and confirm the "CO2 rose" confound
   fires.
7. `air-density-live`: check the printed chip ID is `0x60`. If it is `0x58` the
   board carries a BMP280 die and the firmware will refuse — that refusal is
   correct behaviour, not a bug. Compare ρ against a hand calculation from the
   printed P, T and RH.

**Power**

8. Watch the 3V3 rail on a scope while the SCD41 measures. If it dips, the
   100 µF is missing or too far from the part. Confirm the ESP32 does not reset
   when Wi-Fi and an SCD41 measurement coincide.
9. Verify with a meter that nothing on the bus is being fed 5 V before the
   MLX90614 goes in.

**Timing and drift**

10. Let each example run for an hour and confirm the loop period holds and no
    watchdog fires — none of the examples has been timed on silicon.
11. Leave `air-density-live` running from cold and see whether the self-heating
    flag trips: the cold-start reference is a stand-in for a properly separate
    thermometer, and this is where its limits show.
