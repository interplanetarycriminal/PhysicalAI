"""Hand-authored enrichment for the core catalog.

Merged with data/enrich.py (agent-authored) by the loader; both are keyed by
stable part ID and the later source wins per-field.

This file exists so the semantic sheets — Inference Atlas, Phenomenon Index,
Constraint Navigator, Modality Map — have real data for the best-known parts
regardless of what else lands.
"""

E = dict  # brevity

ENRICH_CORE = {

# ============================================================ Temperature
"S001": E(modality="Thermal", phenomena=["temperature-contact"],
 inferences=["object-temperature", "water-hot-enough", "compost-active", "soil-ready-to-plant",
             "overheating", "thermal-energy-moved"],
 contact="Contact", privacy="None", environment=["Indoor", "Outdoor", "Submersible"],
 range="-55 to +125°C", accuracy="±0.5°C (-10 to +85°C)", resolution="0.0625°C (12-bit)",
 rate="~1 Hz at 12-bit (750ms conversion)", pins=1, pwr_ua=1000.0, pwr_sleep_ua=1.0,
 logic_3v3=True, calibration="None", lifecycle="Active", maturity="Excellent",
 hazard=[], confidence="High", as_of="2026-07",
 fools="Self-heating during conversion if you poll it continuously — leave gaps. The 4.7k "
       "pull-up is mandatory and long parasitic-power runs are unreliable; use three-wire "
       "mode past a couple of metres. Cheap waterproof probes are frequently counterfeit "
       "DS18B20 clones with much worse accuracy and occasional CRC failures — check the ROM "
       "family code. Reading the probe tip while the cable runs through a hot space measures "
       "a blend of both.",
 requires="4.7kΩ pull-up on the data line",
 substitutes="Cheaper: NTC thermistor + ADC. More accurate: TMP117 (±0.1°C). "
             "Non-contact: MLX90614.",
 esp32_compat="Any variant; the 1-Wire bus is bit-banged or uses the RMT peripheral"),

"S002": E(modality="Thermal", phenomena=["temperature-contact"],
 inferences=["object-temperature", "body-temp-trend", "overheating", "drift-from-baseline"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="-55 to +150°C", accuracy="±0.1°C (-20 to +50°C)", resolution="0.0078°C (16-bit)",
 rate="up to 8 Hz", i2c_addr="0x48-0x4B (two address pins)", pins=2,
 pwr_ua=3.5, pwr_sleep_ua=0.15, logic_3v3=True, calibration="None",
 lifecycle="Active", maturity="Excellent", hazard=[], confidence="High", as_of="2026-07",
 fools="It is accurate enough that its own PCB becomes the error source: copper pours, nearby "
       "regulators and even the I2C pull-ups conduct heat into the die. Thermally isolate it "
       "(slots in the PCB, a thin neck) or you will measure your own board. It reads DIE "
       "temperature, so airflow and mounting dominate any claim about ambient accuracy.",
 substitutes="Cheaper: MCP9808 (±0.25°C). For body-contact use: MAX30205.",
 esp32_compat="Any variant"),

"S003": E(modality="Thermal", phenomena=["temperature-contact"],
 inferences=["object-temperature", "overheating", "device-left-on", "drift-from-baseline"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="-40 to +125°C", accuracy="±0.25°C typ", resolution="0.0625°C",
 i2c_addr="0x18-0x1F (three address pins)", pins=2, pwr_ua=200.0, pwr_sleep_ua=0.1,
 logic_3v3=True, calibration="None", lifecycle="Active", maturity="Excellent",
 hazard=[], confidence="High", as_of="2026-07",
 fools="Same self-heating and board-conduction caveat as any die sensor. The ALERT output is "
       "open-drain and needs a pull-up; people wire it directly and wonder why the interrupt "
       "never fires.",
 substitutes="More accurate: TMP117. Cheaper: NTC + ADC.",
 esp32_compat="Any variant; ALERT works as a deep-sleep wake source"),

"S004": E(modality="Thermal", phenomena=["temperature-contact"],
 inferences=["object-temperature", "overheating", "machine-state", "fire-present"],
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 range="-200 to +1350°C (K-type)", accuracy="±2°C typ", resolution="0.25°C",
 pins=3, pwr_ua=1500.0, logic_3v3=True, calibration="One-point",
 lifecycle="Mature", maturity="Excellent", hazard=["HotSurface"],
 confidence="High", as_of="2026-07",
 fools="The cold-junction sensor is on the BOARD, so if the board is hot or in a draught the "
       "reading is wrong regardless of the probe. Grounded probes short the input on some "
       "rigs — use ungrounded probes unless you have isolation. Thermocouple wire must be the "
       "right alloy the whole way: ordinary copper extension wire creates a second junction "
       "and a silent offset. The MAX31855 cannot detect a shorted thermocouple, only an open one.",
 requires="K-type thermocouple probe (sold separately); ungrounded type preferred",
 substitutes="More accurate below 500°C: MAX31865 + PT100. Multi-type: MCP9600.",
 esp32_compat="Any variant (SPI)"),

"S006": E(modality="Thermal", phenomena=["temperature-contact", "resistance"],
 inferences=["object-temperature", "overheating"],
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 range="-40 to +125°C typical (glass bead to +300°C)", accuracy="±1-3% of the bead's tolerance",
 pins=1, pwr_ua=100.0, logic_3v3=True, calibration="Two-point",
 lifecycle="Active", maturity="Good", hazard=[], confidence="High", as_of="2026-07",
 fools="Self-heating from the divider current is a real error at small bead sizes — keep the "
       "current low or pulse the divider. The B-value is a two-point approximation and drifts "
       "at the ends of the range; use full Steinhart-Hart if you care. The ESP32's own ADC "
       "non-linearity will dominate your error budget long before the thermistor does.",
 requires="Fixed divider resistor; an ADS1115 if you want the accuracy the bead can deliver",
 substitutes="Digital and calibrated: DS18B20. Precision: MAX31865 + PT100.",
 esp32_compat="Use ADC1 — ADC2 is unavailable while Wi-Fi is active"),

"S007": E(modality="Thermal", phenomena=["temperature-remote"],
 inferences=["object-temperature", "overheating", "someone-present", "stove-left-on",
             "frost-tonight", "sky-clear", "bearing-failing"],
 contact="Standoff", privacy="Aggregate", environment=["Indoor", "Outdoor"],
 range="-70 to +380°C object", accuracy="±0.5°C near body temperature", resolution="0.02°C",
 i2c_addr="0x5A (fixed on most modules)", pins=2, pwr_ua=1500.0,
 logic_3v3=True, calibration="One-point", lifecycle="Active", maturity="Excellent",
 hazard=[], confidence="High", as_of="2026-07",
 fools="Emissivity is the whole game: it is calibrated for ~0.95 (most matt surfaces), so "
       "shiny metal reads far too cold — sometimes by a hundred degrees. The ~90° field of "
       "view means at 1m you are averaging a 2m circle, not measuring a spot; people aim it "
       "at a small hot object and get room temperature. Sudden ambient changes need minutes to "
       "settle. Window glass is opaque to its wavelength, so it cannot see through a window.",
 substitutes="Narrower FOV: MLX90614-DCI. A picture instead of a point: MLX90640 / AMG8833.",
 esp32_compat="Any variant; note the address is fixed, so two need a mux"),

# ============================================================ Humidity
"S011": E(modality="Chemical", phenomena=["humidity-relative", "temperature-contact"],
 inferences=["mould-risk", "too-dry", "air-stuffy"],
 contact="Standoff", privacy="None", environment=["Indoor"],
 range="0-100% RH, -40 to +80°C", accuracy="±2-5% RH, ±0.5°C", rate="0.5 Hz maximum",
 pins=1, pwr_ua=1500.0, logic_3v3=True, calibration="None",
 lifecycle="NRND", maturity="Good", hazard=[], confidence="High", as_of="2026-07",
 fools="The single-wire protocol is timing-critical and unreliable under interrupt load — "
       "Wi-Fi activity causes dropped reads, which people misdiagnose as a dead sensor. It "
       "cannot be read faster than every two seconds. Accuracy degrades permanently after "
       "prolonged condensation. Use an AHT20 or SHT41 instead in any new design.",
 substitutes="Strictly better and cheaper: AHT20. Reference-grade: SHT41.",
 esp32_compat="Any variant, but timing sensitivity makes it a poor fit for busy firmware"),

"S012": E(modality="Chemical", phenomena=["humidity-relative", "temperature-contact", "dew-point"],
 inferences=["mould-risk", "too-dry", "air-stuffy", "disease-pressure", "coating-cured"],
 contact="Standoff", privacy="None", environment=["Indoor", "Outdoor"],
 range="0-100% RH, -40 to +125°C", accuracy="±1.8% RH, ±0.2°C", resolution="0.01% RH",
 rate="up to 10 Hz", i2c_addr="0x44 (0x45 on some variants)", pins=2,
 pwr_ua=320.0, pwr_sleep_ua=0.08, logic_3v3=True, calibration="None",
 lifecycle="Active", maturity="Excellent", hazard=[], confidence="High", as_of="2026-07",
 fools="Any self-heating from a nearby regulator biases RH downward, because RH depends on the "
       "sensor's own temperature — mount it away from heat sources and away from the ESP32. "
       "Prolonged exposure above 80% RH causes reversible drift; run the on-chip heater "
       "periodically to recover. Solvent vapours (fresh glue, conformal coating, sealant "
       "off-gassing) poison the polymer semi-permanently, so never pot it in silicone.",
 substitutes="Cheaper: AHT20. Outdoor-rated: SHT31 with a filter cap. Add pressure: BME280.",
 esp32_compat="Any variant"),

"S013": E(modality="Chemical", phenomena=["humidity-relative", "temperature-contact",
                                          "pressure-absolute", "altitude-barometric", "dew-point"],
 inferences=["mould-risk", "air-stuffy", "storm-approaching", "how-high", "door-state"],
 contact="Standoff", privacy="None", environment=["Indoor", "Outdoor"],
 range="0-100% RH, 300-1100 hPa, -40 to +85°C", accuracy="±3% RH, ±1 hPa, ±1°C",
 i2c_addr="0x76 or 0x77 (board-dependent)", pins=2, pwr_ua=3.6, pwr_sleep_ua=0.1,
 logic_3v3=True, calibration="None", lifecycle="Active", maturity="Excellent",
 hazard=[], confidence="High", as_of="2026-07",
 fools="The most counterfeited sensor in the hobby: a large share of cheap boards sold as "
       "BME280 carry a BMP280 with no humidity sensor at all. Read the chip-ID register "
       "(0x60 = BME280, 0x58 = BMP280) before trusting anything. The address differs by board, "
       "which collides with gas sensors that also sit at 0x76. Self-heating from continuous "
       "high-oversampling reads biases both temperature and RH.",
 substitutes="Better humidity: SHT41. Better pressure: BMP390. Newer: BME688 adds gas.",
 esp32_compat="Any variant"),

# ============================================================ Pressure
"S016": E(modality="Mechanical", phenomena=["pressure-absolute", "altitude-barometric"],
 inferences=["how-high", "storm-approaching", "door-state", "returned-to-spot"],
 contact="Standoff", privacy="None", environment=["Indoor", "Outdoor"],
 range="300-1250 hPa", accuracy="±50 Pa absolute, ±3 Pa relative", resolution="0.016 Pa",
 rate="up to 200 Hz", i2c_addr="0x76 or 0x77", pins=2, pwr_ua=3.2, pwr_sleep_ua=0.7,
 logic_3v3=True, calibration="One-point", lifecycle="Active", maturity="Excellent",
 hazard=[], confidence="High", as_of="2026-07",
 fools="Absolute altitude is meaningless without a local sea-level pressure reference that "
       "changes hourly with weather — only RELATIVE altitude over minutes is trustworthy. Wind "
       "gusts across a vent hole produce metres of apparent altitude change; any outdoor or "
       "moving install needs a baffled port. Sunlight on the package causes thermal transients "
       "that look like altitude drift.",
 substitutes="Lower noise for fast relative work: DPS310. Cheapest: BMP280.",
 esp32_compat="Any variant"),

"S020": E(modality="Mechanical", phenomena=["pressure-differential", "flow-gas", "air-velocity"],
 inferences=["filter-clogged", "ventilation-adequate", "air-leak", "machine-state"],
 contact="Through-barrier", privacy="None", environment=["Indoor", "Harsh"],
 range="±500 Pa", accuracy="±3% of reading", resolution="0.01 Pa class",
 i2c_addr="0x25 (0x26 variant)", pins=2, pwr_ua=5000.0, logic_3v3=True,
 calibration="None", lifecycle="Active", maturity="Good", hazard=[],
 confidence="High", as_of="2026-07",
 fools="Its thermal measuring principle means the reading depends on the GAS, not just the "
       "pressure — humid air, and especially any other gas, changes the calibration. Mounting "
       "orientation matters at these tiny pressures because the internal flow channel is "
       "gravity-sensitive. Tube length and diameter form a low-pass filter, so long thin tubes "
       "hide exactly the transients you may be looking for.",
 requires="Silicone tubing to both ports; a defined orifice if you want true flow",
 substitutes="Much cheaper, less stable: XGZP6897D. True air velocity: FS3000.",
 esp32_compat="Any variant"),

# ============================================================ Gas / CO2 / PM
"S023": E(modality="Chemical", phenomena=["voc-index", "gas-concentration", "humidity-relative",
                                          "temperature-contact", "pressure-absolute"],
 inferences=["voc-event", "smell-signature", "cooking-detected", "air-stuffy", "food-fresh"],
 contact="Standoff", privacy="None", environment=["Indoor"],
 range="VOC/gas resistance; IAQ 0-500 via BSEC", accuracy="Relative, not absolute ppm",
 warmup="Minutes for a usable reading; days for a stable BSEC baseline",
 i2c_addr="0x76 or 0x77", pins=2, pwr_ua=900.0, logic_3v3=True,
 calibration="Periodic", lifecycle="Active", maturity="Good",
 hazard=["HotSurface"], confidence="High", as_of="2026-07",
 fools="It does not measure any specific gas. The output is a resistance that moves with "
       "total reducing-gas load AND with humidity AND with temperature, so an unconditioned "
       "reading tracks the weather as much as the air. The BSEC library that makes it useful "
       "is a closed-source binary blob with licence constraints. Its own heater warms the "
       "adjacent temperature and humidity dies, so those readings run high unless compensated. "
       "Silicone vapours poison the sensing layer permanently.",
 substitutes="Simpler index, self-calibrating: SGP40. Real CO2 instead of a proxy: SCD41.",
 esp32_compat="BSEC needs meaningful flash and RAM; comfortable on S3, tight on C3"),

"S026": E(modality="Chemical", phenomena=["gas-concentration"],
 inferences=["gas-leak", "smoke-present"],
 contact="Standoff", privacy="None", environment=["Indoor"],
 range="200-10000 ppm class", accuracy="Qualitative only",
 warmup="24-48 hours of burn-in for a new sensor; minutes from cold each power-up",
 pins=2, pwr_ua=150000.0, logic_3v3=False, calibration="Reference",
 lifecycle="Mature", maturity="Workable", hazard=["HotSurface", "Ignition", "Toxic"],
 confidence="High", as_of="2026-07",
 fools="Broadly cross-sensitive — alcohol, solvents, cooking fumes and humidity all move it, "
       "so it cannot identify a gas, only that something reducing is present. Baseline drifts "
       "over weeks and jumps with humidity. The heater is an ignition source, so it must never "
       "go inside a volume where flammable gas can accumulate. Never a life-safety device: use "
       "a certified alarm and treat this as a logger beside it.",
 requires="5V heater supply; a divider or level shifter for the analog output",
 substitutes="Lower power, faster: MiCS-5524. Selective and quantitative: an electrochemical cell.",
 esp32_compat="Analog out must be divided to 3.3V; use ADC1"),

"S036": E(modality="Chemical", phenomena=["co2-concentration", "humidity-relative",
                                          "temperature-contact"],
 inferences=["air-stuffy", "ventilation-adequate", "someone-present", "how-many-people",
             "hive-state", "growth-rate"],
 contact="Standoff", privacy="Aggregate", environment=["Indoor"],
 range="400-5000 ppm", accuracy="±(40 ppm + 5%)", resolution="1 ppm",
 rate="1 reading / 5 s (periodic mode)", warmup="First valid reading after ~60 s",
 i2c_addr="0x62 (fixed)", pins=2, pwr_ua=500.0, pwr_sleep_ua=0.5,
 logic_3v3=True, calibration="One-point", lifecycle="Active", maturity="Excellent",
 hazard=[], confidence="High", as_of="2026-07",
 fools="Automatic self-calibration assumes the space returns to ~400 ppm at least once a week. "
       "In a continuously occupied room — a bedroom, a greenhouse, an office — that assumption "
       "is false, and the sensor silently re-baselines downward until it under-reads badly. "
       "Disable ASC and calibrate outdoors instead. Ambient pressure must be set for altitude "
       "or readings drift with weather. Breathing on it saturates the reading for minutes. Its "
       "own 205mA measurement pulse self-heats the co-located temperature reading.",
 substitutes="Greenhouse range to 10000 ppm: SCD30. Cheaper: MH-Z19C. Percent-level: STC31.",
 esp32_compat="Any variant; the 205mA pulse needs decent supply decoupling"),

"S040": E(modality="Optical", phenomena=["particulate-mass", "particulate-count"],
 inferences=["particulate-level", "smoke-present", "cooking-detected", "fire-present"],
 contact="Standoff", privacy="None", environment=["Indoor", "Outdoor"],
 range="0-500 µg/m³, six size bins", accuracy="±10% above 100 µg/m³; poor below ~10",
 warmup="~30 s of fan settling before the reading means anything",
 pins=2, pwr_ua=100000.0, logic_3v3=True, calibration="None",
 lifecycle="Active", maturity="Excellent", hazard=["Laser"], confidence="High", as_of="2026-07",
 fools="Over-reads badly above ~75% RH: particles absorb water and swell, so fog, steam and a "
       "damp autumn morning all read like smoke. Log humidity alongside and correct, or your "
       "wildfire alarm fires on dew. It infers MASS from scattered light using an assumed "
       "particle density, so the µg/m³ figure is a convention rather than a measurement. The "
       "fan and laser have a duty-cycle life — running it continuously wears it out in a "
       "year or two, so sample intermittently.",
 substitutes="Calibrated and self-cleaning: SPS30. Combined with RH/T/VOC: Sensirion SEN5x.",
 esp32_compat="Any variant with a spare UART; PMSA003I is the I2C version"),

# ============================================================ Light
"S044": E(modality="Optical", phenomena=["illuminance"],
 inferences=["light-dose-daily", "sky-clear", "device-left-on"],
 contact="Standoff", privacy="None", environment=["Indoor"],
 range="1-65535 lux", accuracy="±20%", resolution="1 lux",
 i2c_addr="0x23 (0x5C with ADDR high)", pins=2, pwr_ua=120.0, pwr_sleep_ua=1.0,
 logic_3v3=True, calibration="None", lifecycle="Active", maturity="Excellent",
 hazard=[], confidence="High", as_of="2026-07",
 fools="Its spectral response only approximates the human eye, so LED and fluorescent sources "
       "read differently from daylight at the same perceived brightness — never compare lux "
       "across light types. It saturates in direct sun. Any window, diffuser or enclosure "
       "lid in front of it changes the calibration, so measure through whatever you intend to "
       "deploy with.",
 substitutes="Wider range and better low light: VEML7700. Extreme range: TSL2591. "
             "Colour-accurate: OPT4048.",
 esp32_compat="Any variant"),

"S049": E(modality="Optical", phenomena=["illuminance", "resistance"],
 inferences=["device-left-on", "object-present", "crossed-boundary"],
 contact="Standoff", privacy="None", environment=["Indoor"],
 range="Relative only", accuracy="Uncalibrated", rate="Slow — tens of ms to settle",
 pins=1, pwr_ua=100.0, logic_3v3=True, calibration="Two-point",
 lifecycle="Mature", maturity="Good", hazard=[], confidence="High", as_of="2026-07",
 fools="Response is slow and asymmetric — it takes far longer to recover from bright light "
       "than to respond to it, which ruins fast beam-break applications. Every cell differs by "
       "tens of percent, so units are not interchangeable without individual calibration. "
       "Strong temperature dependence. Cadmium sulfide is RoHS-restricted, so this is a "
       "prototype and education part rather than a product part.",
 substitutes="Fast beam-break: photo-interrupter or phototransistor. Calibrated: BH1750.",
 esp32_compat="Use ADC1"),

# ============================================================ Distance / presence
"S056": E(modality="Acoustic", phenomena=["distance-point", "ultrasound"],
 inferences=["obstacle-ahead", "tank-level", "object-present", "container-fullness",
             "someone-present", "how-far-travelled"],
 contact="Standoff", privacy="None", environment=["Indoor"],
 range="2-400 cm", accuracy="±3 mm nominal, far worse in practice", rate="up to ~20 Hz",
 pins=2, pwr_ua=15000.0, logic_3v3=False, calibration="One-point",
 lifecycle="Active", maturity="Excellent", hazard=[], confidence="High", as_of="2026-07",
 fools="Soft, angled or textured targets scatter the echo away and simply return nothing — "
       "curtains, foam and a person in a wool coat are close to invisible. The beam is a ~15° "
       "cone, so it reports the NEAREST thing in that cone, not what you aimed at. The speed "
       "of sound changes about 0.6% per °C, so an uncompensated outdoor reading drifts by "
       "centimetres between morning and afternoon. Multiple units interfere unless you fire "
       "them in sequence. The echo pin is 5V and will damage an ESP32 GPIO without a divider.",
 requires="Voltage divider on ECHO (or use the 3.3V-safe US-100)",
 substitutes="3.3V-native with temperature compensation: US-100. Weatherproof: JSN-SR04T. "
             "Precise and narrow-beam: VL53L0X.",
 esp32_compat="Any variant; ECHO must be divided to 3.3V"),

"S058": E(modality="Optical", phenomena=["distance-point"],
 inferences=["obstacle-ahead", "tank-level", "object-present", "consumable-remaining",
             "container-fullness", "crossed-boundary"],
 contact="Standoff", privacy="None", environment=["Indoor"],
 range="30-2000 mm", accuracy="±3% (target- and light-dependent)", resolution="1 mm",
 rate="up to 50 Hz", i2c_addr="0x29 (FIXED — see note)", pins=2, pwr_ua=19000.0,
 pwr_sleep_ua=5.0, logic_3v3=True, calibration="One-point",
 lifecycle="Active", maturity="Excellent", hazard=["Laser"], confidence="High", as_of="2026-07",
 fools="Range depends strongly on target reflectivity — roughly 2m on white, under 1m on dark "
       "grey, and a black matt surface can read as nothing at all. Direct sunlight swamps the "
       "receiver and collapses the usable range outdoors. Any cover glass causes internal "
       "crosstalk unless you use an air gap and run crosstalk calibration. THE ADDRESS IS "
       "FIXED AT 0x29 on every unit: two on one bus is impossible without a multiplexer, or "
       "holding each XSHUT low and assigning addresses one at a time at boot — this is the "
       "single most common reason multi-ToF projects never work.",
 requires="XSHUT pin wired per sensor, or a TCA9548A multiplexer, for more than one",
 substitutes="Longer range: VL53L1X. Very short range: VL6180X. 64-zone depth: VL53L5CX.",
 esp32_compat="Any variant; budget a GPIO per sensor for XSHUT"),

"S065": E(modality="Thermal", phenomena=["temperature-remote", "occupancy-signal"],
 inferences=["someone-present", "intrusion", "crossed-boundary", "entered-or-left"],
 contact="Standoff", privacy="Aggregate", environment=["Indoor"],
 range="~7 m, 120° cone", rate="Event-driven, with an adjustable hold time",
 pins=1, pwr_ua=50.0, logic_3v3=False, calibration="None",
 lifecycle="Active", maturity="Excellent", hazard=[], confidence="High", as_of="2026-07",
 fools="It senses CHANGE in infrared across its lens segments, not presence — so a person "
       "sitting still becomes invisible within seconds. This is the defining limitation and the "
       "reason mmWave replaced it. Sunlight tracking across the lens, warm air from a vent, a "
       "radiator cycling, and pets all trigger it. Cheap modules are electrically noisy and "
       "false-trigger on their own supply, so add a capacitor at the module's VCC. It cannot "
       "see through glass at all.",
 substitutes="True presence including stillness: LD2410. Better optics and specs: Panasonic EKMC. "
             "Directional counting: VL53L1X.",
 esp32_compat="Output is typically 3.3V on 5V-powered modules — verify yours before wiring"),

"S067": E(modality="RF", phenomena=["occupancy-signal", "distance-point", "respiration"],
 inferences=["someone-present", "someone-still-present", "where-in-room", "person-asleep",
             "no-movement-alarm", "occupancy-duration"],
 contact="Through-barrier", privacy="Aggregate", environment=["Indoor"],
 range="0-6 m presence, with configurable distance gates", rate="~10 Hz",
 pins=2, pwr_ua=80000.0, logic_3v3=True, calibration="One-point",
 lifecycle="Active", maturity="Good", hazard=[], confidence="High", as_of="2026-07",
 fools="It detects the micro-motion of breathing, which means it also detects anything else "
       "that moves microscopically: ceiling fans, moving curtains, swaying plants, rain on a "
       "window, and a washing machine two rooms away. Critically, 24GHz passes through "
       "plasterboard, so at default sensitivity it happily detects your neighbour or someone "
       "in the hallway — the distance gates are not optional, they are the entire configuration "
       "task. Metal surfaces cause reflections that create phantom targets. Expect to re-tune "
       "after moving furniture.",
 substitutes="Cheaper motion-only: PIR. Multi-target with coordinates: LD2450. "
             "Vitals and fall detection: MR60BHA2/FDA2.",
 esp32_compat="Any variant with a spare UART; ESPHome has a mature component"),

"S071": E(modality="Thermal", phenomena=["temperature-field", "temperature-remote"],
 inferences=["someone-present", "how-many-people", "where-in-room", "person-fell",
             "stove-left-on", "overheating", "object-temperature"],
 contact="Standoff", privacy="Aggregate", environment=["Indoor"],
 range="0-80°C, 8x8 zones, 60° FOV", accuracy="±2.5°C", rate="10 Hz",
 i2c_addr="0x69 (0x68 selectable)", pins=2, pwr_ua=4500.0, logic_3v3=True,
 calibration="One-point", lifecycle="Active", maturity="Good", hazard=[],
 confidence="High", as_of="2026-07",
 fools="Sixty-four pixels is deliberately too coarse to identify anyone, which is the privacy "
       "advantage — but it also means two people standing close merge into one blob. Anything "
       "warm competes: a radiator, a laptop, a sunlit patch of floor, a cup of tea. Absolute "
       "accuracy is poor; the useful signal is the CONTRAST between a body and its background, "
       "which collapses when the room approaches skin temperature. Note the 0x69 default "
       "collides with IMUs on the same bus.",
 substitutes="Far more pixels: MLX90640 (768). Cheaper presence: PIR or mmWave. "
             "Human-tuned 4x4: Omron D6T.",
 esp32_compat="Any variant; 64 pixels at 10Hz is light on RAM unlike MLX90640"),

# ============================================================ Motion
"S072": E(modality="Mechanical", phenomena=["acceleration", "angular-rate", "tilt", "vibration"],
 inferences=["object-moved", "object-dropped", "am-i-level", "machine-state",
             "step-count", "posture", "which-way-facing"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="±2-16 g, ±250-2000 °/s", accuracy="Uncalibrated; significant offset drift",
 rate="up to 1 kHz", i2c_addr="0x68 (0x69 with AD0 high)", pins=2,
 pwr_ua=3800.0, pwr_sleep_ua=10.0, logic_3v3=True, calibration="One-point",
 lifecycle="EOL", maturity="Excellent", hazard=[], confidence="High", as_of="2026-07",
 fools="The gyroscope drifts substantially with temperature and time — integrate it for "
       "orientation and your heading will wander within a minute unless you fuse it with the "
       "accelerometer. The accelerometer cannot distinguish gravity from linear acceleration, "
       "which is the classic beginner trap. It is officially end-of-life and a large share of "
       "cheap modules are remarked or counterfeit. Its 0x68 default collides with the DS3231 RTC.",
 substitutes="Current equivalent: LSM6DSOX or ICM-42688-P. Orientation solved on-chip: BNO086.",
 esp32_compat="Any variant"),

"S076": E(modality="Mechanical", phenomena=["acceleration", "shock-impact", "vibration", "tilt"],
 inferences=["object-moved", "object-dropped", "machine-running", "machine-state",
             "tamper-detected", "cycle-complete", "unusual-sound"],
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 range="±2-16 g", accuracy="±0.5% typical", resolution="4 mg/LSB (13-bit)",
 rate="up to 3.2 kHz", i2c_addr="0x53 (0x1D with ALT high)", pins=2,
 pwr_ua=140.0, pwr_sleep_ua=0.1, logic_3v3=True, calibration="One-point",
 lifecycle="Mature", maturity="Excellent", hazard=[], confidence="High", as_of="2026-07",
 fools="Its onboard tap and freefall engines are threshold-based and fire on anything with the "
       "right impulse shape — a slammed door, a dropped tool nearby, a lorry passing. Mounting "
       "dominates vibration work: double-sided tape rolls off high frequencies badly, so what "
       "you measure is partly the adhesive. At 3.2 kHz it is fine for machine-state detection "
       "but too slow for real bearing-defect analysis.",
 substitutes="Higher rate for FFT work: KX132 (25 kHz). Seismic noise floor: ADXL355. "
             "Impact to ±200 g: ADXL375.",
 esp32_compat="Any variant; interrupt output works as a deep-sleep wake source"),

# ============================================================ Magnetic
"S085": E(modality="Magnetic", phenomena=["magnetic-field"],
 inferences=["door-state", "object-present", "rotation-speed", "tamper-detected",
             "object-count", "is-raining"],
 contact="Standoff", privacy="None", environment=["Indoor", "Outdoor"],
 range="Contact closes within ~10-25 mm of a magnet", rate="Mechanical, ~100 Hz practical",
 pins=1, pwr_ua=0.0, pwr_sleep_ua=0.0, logic_3v3=True, calibration="None",
 lifecycle="Active", maturity="Excellent", hazard=[], confidence="High", as_of="2026-07",
 fools="Contacts bounce for milliseconds, so an undebounced interrupt counts one event as "
       "several — this silently inflates every tipping-bucket rain total and flow count. The "
       "glass envelope is fragile. Strong nearby magnets or steel can hold it closed or shield "
       "it. It is a mechanical part with a finite operation count, though that count is in the "
       "hundreds of millions.",
 substitutes="Solid state and no bounce: A3144 Hall switch. Field strength rather than "
             "presence: SS49E. Contactless angle: AS5600.",
 esp32_compat="Ideal EXT0/EXT1 deep-sleep wake source — zero standby current"),

# ============================================================ Sound
"S087": E(modality="Acoustic", phenomena=["sound-pressure"],
 inferences=["unusual-sound", "machine-running", "machine-state", "cooking-detected",
             "breathing-rate", "glass-broken", "hive-state"],
 contact="Standoff", privacy="Raw-imagery", environment=["Indoor"],
 range="60 Hz - 15 kHz", accuracy="Uncalibrated (no absolute SPL)", rate="Up to 48 kHz sampling",
 pins=3, pwr_ua=1400.0, logic_3v3=True, calibration="Reference",
 lifecycle="Active", maturity="Good", hazard=[], confidence="High", as_of="2026-07",
 fools="It gives you raw samples, not decibels — deriving true dB(A) needs A-weighting and a "
       "calibrated reference, and without that any 'noise level' you publish is arbitrary. The "
       "I2S clock must keep running or the data stream stalls in ways that look like a dead "
       "sensor. Wind noise and handling noise dominate outdoors without a foam shield. Note the "
       "privacy classification: this captures intelligible speech, which changes what you may "
       "lawfully record and store.",
 substitutes="Flatter response: ICS-43434. Calibrated SPL out of the box: DFRobot dB meter. "
             "Structure-borne only, no speech privacy issue: piezo contact disc.",
 esp32_compat="Needs a real I2S peripheral; comfortable on S3 with ESP-SR wake words"),

"S091": E(modality="Acoustic", phenomena=["sound-structural", "vibration", "shock-impact"],
 inferences=["machine-running", "bearing-failing", "object-dropped", "unusual-sound",
             "crossed-boundary", "cycle-complete"],
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 range="Structure-borne vibration; highly mount-dependent", accuracy="Relative only",
 pins=1, pwr_ua=0.0, logic_3v3=False, calibration="Two-point",
 lifecycle="Active", maturity="Workable", hazard=[], confidence="High", as_of="2026-07",
 fools="A struck disc can generate tens of volts and WILL destroy an ADC pin without clamping "
       "diodes and a bleed resistor. Its output depends enormously on how well it is bonded to "
       "the surface — tape, glue and clamping all give different sensitivities, so readings are "
       "not comparable between installs. It is a high-impedance source, so long unshielded "
       "leads pick up mains hum that swamps the signal. It hears the structure, not the air, "
       "which is a privacy advantage: it cannot resolve speech.",
 requires="Two clamping diodes to 3.3V/GND plus a ~1MΩ bleed resistor before any ADC pin",
 substitutes="Calibrated vibration: KX132 or ADXL345. Airborne sound: INMP441.",
 esp32_compat="Use ADC1 with clamping; a comparator gives a zero-power wake"),

# ============================================================ Force / touch
"S098": E(modality="Mechanical", phenomena=["weight", "force", "strain"],
 inferences=["consumable-remaining", "container-fullness", "someone-present", "hive-state",
             "object-present", "object-count", "posture"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="1 g to hundreds of kg depending on the cell", accuracy="0.05% of full scale, at best",
 rate="10 or 80 Hz (HX711 jumper)", pins=2, pwr_ua=1500.0, pwr_sleep_ua=1.0,
 logic_3v3=True, calibration="Two-point", lifecycle="Active", maturity="Excellent",
 hazard=[], confidence="High", as_of="2026-07",
 fools="Creep is the big one: leave a constant load on a cell and the reading drifts downward "
       "over hours, so a beehive or gas-bottle scale needs periodic re-zeroing or drift "
       "correction. Temperature shifts both zero and span, which outdoors is a larger error "
       "than the thing you are measuring. Mounting is everything — the cell must be loaded "
       "along its intended axis with no side force, and overloading past ~150% deforms it "
       "permanently and silently. The HX711 is noisy near switching supplies.",
 requires="A load cell (sold separately) and rigid, correctly-oriented mounting",
 substitutes="Quieter and I2C-native: NAU7802. Tiny forces: FSR (qualitative only).",
 esp32_compat="Any variant; the HX711 protocol is bit-banged and timing-tolerant"),

"S104": E(modality="Electrical", phenomena=["capacitance"],
 inferences=["object-present", "someone-present", "tank-level", "tamper-detected"],
 contact="Through-barrier", privacy="None", environment=["Indoor"],
 range="12 electrodes, through up to ~5 mm of non-conductive material",
 i2c_addr="0x5A-0x5D", pins=2, pwr_ua=29.0, pwr_sleep_ua=3.0,
 logic_3v3=True, calibration="One-point", lifecycle="Active", maturity="Excellent",
 hazard=[], confidence="High", as_of="2026-07",
 fools="Water is the enemy: a film of condensation or a wet hand reads as a permanent touch "
       "across several pads at once. It auto-baselines, which is usually helpful but means a "
       "slowly-applied touch can be absorbed into the baseline and never register. Electrode "
       "wire length and routing change sensitivity, so pads behave differently depending on "
       "cable dress. A floating (battery, ungrounded) system has a weaker ground reference and "
       "noticeably worse sensitivity.",
 substitutes="Single pad, no I2C: TTP223. Free and built in: ESP32 touch pins. "
             "Position rather than presence: Trill.",
 esp32_compat="Any variant. Note: C3/C6/H2 have NO built-in touch peripheral, so on those "
              "chips an MPR121 is the only capacitive-touch option"),

"S106": E(modality="Electrical", phenomena=["capacitance"],
 inferences=["object-present", "someone-present", "tank-level"],
 contact="Through-barrier", privacy="None", environment=["Indoor"],
 range="Up to 10 channels on supported variants", pins=0, pwr_ua=5.0, pwr_sleep_ua=5.0,
 logic_3v3=True, calibration="One-point", lifecycle="Active", maturity="Good",
 hazard=[], confidence="High", as_of="2026-07",
 fools="Readings drift with temperature and humidity, so a fixed threshold that works in a "
       "cold workshop misfires in a warm room — track a rolling baseline instead. Wi-Fi "
       "activity injects noise into the measurement. Water films cause false touches. And the "
       "critical gotcha: the touch peripheral DOES NOT EXIST on the C3, C6 or H2, so any "
       "project relying on it is silently locked to the classic, S2 or S3.",
 substitutes="Chip-independent: MPR121 or TTP223.",
 esp32_compat="Classic/S2/S3 only. Touch-wake from deep sleep works and costs microamps"),

# ============================================================ Biometric
"S112": E(modality="Biological", phenomena=["ppg-optical"],
 inferences=["heart-rate", "heart-variability", "blood-oxygen", "stress-arousal"],
 contact="Contact", privacy="Identifiable", environment=["Indoor"],
 range="HR 30-240 bpm; SpO2 nominally 70-100%", accuracy="HR good; SpO2 uncalibrated",
 rate="up to 1 kHz PPG", i2c_addr="0x57 (fixed)", pins=2, pwr_ua=600.0,
 pwr_sleep_ua=0.7, logic_3v3=True, calibration="Reference",
 lifecycle="Active", maturity="Good", hazard=[], confidence="High", as_of="2026-07",
 fools="Motion artefact is the dominant error and it is not a small effect — any movement "
       "swamps the pulse waveform entirely, which is why every serious wearable pairs this "
       "with an accelerometer purely to reject corrupted beats. Contact pressure changes the "
       "signal amplitude and the apparent SpO2 ratio. SpO2 from a reflectance sensor at the "
       "wrist is unreliable and must not be presented as a medical figure; even at a fingertip "
       "it needs calibration against a real oximeter to mean anything. Skin tone, tattoos and "
       "cold peripheries all reduce signal quality. The LEDs draw 20-50 mA when on, which the "
       "average current figure hides.",
 requires="Firm, consistent skin contact; an IMU if you want usable data during movement",
 substitutes="Electrical rather than optical, far more robust: AD8232 ECG. "
             "Synchronised both: MAX86150.",
 esp32_compat="Any variant"),

# ============================================================ Water / soil
"S129": E(modality="Electrical", phenomena=["moisture-material", "dielectric-constant"],
 inferences=["plant-thirsty", "moisture-content", "soil-tension"],
 contact="Immersed", privacy="None", environment=["Outdoor"],
 range="Relative, 0-100% of your own calibration", accuracy="Uncalibrated across soil types",
 pins=1, pwr_ua=5000.0, logic_3v3=True, calibration="Two-point",
 lifecycle="Clone-risk", maturity="Good", hazard=[], confidence="High", as_of="2026-07",
 fools="It responds to the soil's dielectric constant, which varies with soil TYPE and "
       "compaction as much as with water — so a reading calibrated in potting compost is "
       "meaningless in clay. The exposed top of the board is not sealed on most clones: water "
       "wicks up, reaches the electronics and kills it within a season unless you seal it "
       "yourself. Board quality varies wildly, including versions with the wrong oscillator "
       "components that barely respond at all. Air gaps around the probe from repeated drying "
       "cause step changes that look like watering events.",
 requires="Sealing the top of the board; per-soil two-point calibration (air and saturated)",
 substitutes="The metric agronomists actually use: Watermark tension sensor. "
             "Research-grade: METER TEROS 12.",
 esp32_compat="Use ADC1; power it from a GPIO so it is not energised between readings"),

"S138": E(modality="Mechanical", phenomena=["flow-liquid"],
 inferences=["flow-rate", "water-used-total", "water-leak", "pump-dry", "thermal-energy-moved"],
 contact="Immersed", privacy="None", environment=["Indoor", "Outdoor"],
 range="1-30 L/min", accuracy="±10% uncalibrated", resolution="~450 pulses/L",
 pins=1, pwr_ua=15000.0, logic_3v3=False, calibration="Two-point",
 lifecycle="Active", maturity="Good", hazard=[], confidence="High", as_of="2026-07",
 fools="The pulses-per-litre figure on the datasheet is a nominal value and varies by ±10% "
       "between units and with flow rate — calibrate against a measured bucket or your totals "
       "will be confidently wrong. It stalls below its minimum flow, so a slow drip or a weeping "
       "joint reads as zero, which is exactly the leak you most want to catch. Grit jams the "
       "turbine and the bearing wears. It is a mechanical restriction in the pipe. The output "
       "may be at supply voltage, so level-shift before an ESP32 GPIO.",
 requires="Level shifting if run above 3.3V; inline plumbing with the correct thread",
 substitutes="No plumbing at all: clamp-on ultrasonic. No moving parts: thermal mass flow.",
 esp32_compat="Use the PCNT peripheral — it counts in hardware with zero CPU load"),

"S147": E(modality="Electrical", phenomena=["current-ac"],
 inferences=["power-now", "which-appliance", "machine-running", "machine-state",
             "device-left-on", "phantom-load", "abnormal-current"],
 contact="Through-barrier", privacy="Aggregate", environment=["Indoor"],
 range="up to 100 A", accuracy="±3% with calibration", rate="Needs kHz sampling for RMS",
 pins=1, pwr_ua=0.0, logic_3v3=True, calibration="Two-point",
 lifecycle="Active", maturity="Good", hazard=["Mains"], confidence="High", as_of="2026-07",
 fools="It measures CURRENT only, so without a voltage reference you get apparent power (VA), "
       "not real power (W) — for anything with a motor or a switching supply those differ "
       "substantially and your energy figures will be wrong. It must clamp around ONE conductor: "
       "clamp around a whole flex containing live and neutral and it reads zero, which is the "
       "most common first-time failure. Never open-circuit a current transformer under load. "
       "Poor accuracy at low currents, so standby loads are close to invisible. The burden "
       "resistor and 1.65V bias network are not optional.",
 requires="Burden resistor and a 1.65V bias network; ADS1115 strongly recommended over the "
          "ESP32's own ADC",
 substitutes="Complete metering with real power and energy: PZEM-004T. DC instead: INA226.",
 esp32_compat="Use ADC1 at a high sample rate, or an ADS1115; ADC2 dies when Wi-Fi is on"),
}
