# Authoring guide — Sensor Universe schema v2

Read `data/schema.py` and `data/vocab.py` first. They are the contract. Any field
name or vocabulary term not defined there does not exist and will fail validation.

## The record shape

```python
dict(
  catalog="sensor",                      # sensor | actuator | glue | board
  n="SCD41 true CO2",                    # human name — the part, not a project
  pn="SCD41",                            # ONE product. See "no merged products" below.
  cat="CO2",                             # exact key from vocab.CATEGORY
  sub="Photoacoustic",                   # free text, short
  modality="Chemical",                   # exact key from schema.MODALITY
  phenomena=["co2-concentration", "humidity-relative", "temperature-contact"],
  inferences=["air-stuffy", "ventilation-adequate", "someone-present"],

  meas="Real CO2 400-5000ppm plus RH and temperature",
  how="Fires IR pulses into a sealed chamber; CO2 absorbs them and the gas "
      "literally pops acoustically, which a tiny microphone hears. That is real "
      "CO2, not the 'eCO2' a VOC sensor infers.",

  range="400-5000 ppm", accuracy="±(40ppm + 5%)", resolution="1 ppm",
  rate="1 reading / 5 s", warmup="First reading valid after ~60 s",

  iface=["I2C"], v="2.4-5.5V", logic_3v3=True, i2c_addr="0x62", pins=2,
  esp32_compat="Any variant",

  contact="Standoff", privacy="Aggregate",
  environment=["Indoor"], ip="",

  pwr="0.5mA average at 1 reading/5min; ~205mA peak during a measurement",
  pwr_ua=500.0, pwr_sleep_ua=0.5,

  usd=25.0, buy=["AF","SF","DK","MO"],
  brd="Adafruit 5190, SparkFun Qwiic SCD41",
  lib="Sensirion scd4x, Adafruit_SCD4X",
  link="https://sensirion.com/products/catalog/SCD41",
  lifecycle="Active", maturity="Excellent",
  confidence="High", as_of="2026-07",

  fools="Needs its ambient-pressure or altitude register set — uncompensated "
        "readings drift with weather and read badly high above ~500m. Its "
        "automatic self-calibration assumes the room reaches ~400ppm at least "
        "once a week; in a continuously occupied space that assumption is false "
        "and it will slowly under-read. Breathing directly on it pins the reading.",
  hazard=[], calibration="One-point",
  consumable="None — sealed optical path, no wear-out",
  requires="", substitutes="MH-Z19C is cheaper and physically bigger; SCD30 "
                           "reaches 10000ppm for greenhouses; STC31 for percent-level CO2",

  diff=1,
  use="Ventilation control, classroom and office air, sleep-room stuffiness, "
      "greenhouse enrichment, fermentation monitoring.",
  spark="Meeting-room honesty light: an ePaper sign showing live CO2 and 'this "
        "room needs 10 minutes of airing'. Behaviour changes when the number is public.",
  pair="ePaper display, SGP41 for VOCs, a PM sensor for the full IAQ trifecta",
  tags=["Air","Health","Home"],
)
```

## Rules that will fail validation if broken

1. **No merged products.** `pn` names ONE product. v5 priced a $60 pyranometer
   and a $225 one under a single `usd`, and merged a wideband LSU with a
   narrowband HEGO under one interface. If two parts differ in price, interface
   or technology, write two records. If you genuinely must merge a close family
   (e.g. SHT40/41/45), set `confidence="Estimate"`.
2. **`hazard` is required wherever the text implies one.** Mains, >48V, heated
   elements, lasers, UV-C, flammable gas, toxic gas, amps of current. The
   validator greps your prose for these and fails you if the field is empty.
3. **`logic_3v3` must be set** for any part with a supply above 3.6V and a
   Digital/Pulse/Analog/PWM output. Getting this wrong destroys hardware — v5
   told readers the XKC-Y25 had a "logic-safe out" when its output follows VCC.
4. **Vocabulary terms must exist.** Check `vocab.PHENOMENON`, `vocab.INFERENCE`,
   `vocab.CATEGORY`, `vocab.THEME`. Do not invent terms; if something genuinely
   has no term, pick the closest and note it in `note`.
5. **`diff` follows `schema.DIFFICULTY_RUBRIC`.** 1 = Qwiic cable and a library
   example. 5 = you are writing drivers and validating your own results. A $45
   NPU camera is not a 1 and a 400V Geiger kit is not a 2.

## The ESP32 interface fields

Eleven optional fields carry the wiring answer in a form you can filter on. The
prose stays where it is — `iface`, `v`, `lib`, `esp32_compat` — these are its
computable twin.

| field | kind | what it says |
|---|---|---|
| `iface_primary` | `enum:INTERFACE` | The bus you actually wire when the part offers a choice |
| `v_min` / `v_max` | `float` | Supply range in volts — the computable form of `v` |
| `logic_v` | `str` | Logic level of the signal lines as wired: `"3.3V"`, `"5V TTL"`, `"0-3.3V analog"` |
| `level_shift` | `enum:LEVEL_SHIFT` | What must sit between those lines and an ESP32 GPIO |
| `addr_mode` | `enum:ADDR_MODE` | How the device is selected on its bus — this is what decides how many you can stack |
| `cs_pins` | `int` | Dedicated select lines beyond the shared bus (0 on I2C, 1 on SPI) |
| `i_peak_ua` | `float` | Peak/burst draw in µA — what the 3.3V rail must survive |
| `rate_hz` | `float` | Maximum sample/update rate in Hz — the computable form of `rate` |
| `esp32_driver` | `str` | A specific known-good driver: library name, source and framework |
| `driver_status` | `enum:DRIVER_STATUS` | Confidence in the ESP32 driver situation |

**The rule.** Author a value only when you have verified it against a datasheet
or a real driver, and put it in the authored JSON that `tools/gen_enrich_iface.py`
turns into `data/enrich_iface.py`. Anything unverified stays an explicit `None`,
which the loader guarantees is present on every record — a null here means
"nobody has checked", and that is data. Everything else comes from
`data/iface_derive.py`, which re-reads `v`, `rate`, `pwr`, `iface`, `i2c_addr`,
`logic_3v3` and `hazard` and refuses anything ambiguous. **Derived values are
never authored by hand**, and an authored value always beats a derived one.
`esp32_driver` and `driver_status` have no derivation at all: they are authored
or they are `None`.

## What good prose looks like

- **`how`** — 2-4 sentences of real physics in plain English. Explain the
  mechanism, not the marketing. A smart 14-year-old should follow it; an engineer
  should not wince. Say what it actually measures versus what people think it does.
- **`fools`** — *the most valuable field in the document.* Concrete failure modes:
  what produces false positives, what it is cross-sensitive to, where it goes
  blind, how it drifts. Be specific and quantitative where you can ("optical PM
  sensors over-read above ~75% RH because particles absorb water and swell").
  Never write "may be inaccurate in some conditions".
- **`spark`** — one *specific* invention, not a category. "A bedside sleep lab"
  is weak. "Two ROI zones in a doorway give entry/exit direction, so you get
  anonymous footfall counts for under $15" is strong. Do not write pedagogy
  ("great first sensor for kids") — that is not an invention.
- **`substitutes`** — name the cheaper option, the more accurate option, and the
  no-contact option where they exist. This is what makes the catalog navigable.
- **`use`** — real applications, comma-separated, concrete nouns.

## Tone

Confident, specific, honest about limits. Never marketing ("exceptional
sensitivity", "MCERTS-adjacent"). Where a part is commonly misunderstood, say so
plainly — the reader is trying to build something and would rather know now.

## Accuracy

You are writing a reference document. If you are not confident in a price or
spec, set `confidence="Estimate"` and give a range. **Do not invent product SKUs
or library names** — v5 shipped "Adafruit 5417" for an ADXL355 breakout that does
not exist. If you don't know the SKU, describe the board generically
("generic CJMCU breakout", "Analog Devices EVAL board"). An honest gap beats a
confident fabrication.
