"""Enrichment for the 35 records the batch agents didn't reach.

Two of the ten enrichment agents truncated mid-output, leaving contiguous gaps
around power/position/GNSS/thermal/camera and the industrial/textile/frontier
tail. These are high-traffic parts, so they are written directly rather than
left un-enriched — without the semantic fields they would be invisible to the
Inference Atlas, Phenomenon Index and Constraint Navigator.

Merged over data/enrich.py by the loader.
"""

ENRICH_MANUAL = {

# ---------------------------------------------------------------- power
"S145": dict(modality="Electrical", phenomena=["current-dc", "voltage", "energy-accumulated"],
 inferences=["power-now", "battery-charge", "solar-performance", "energy-budget-node",
             "abnormal-current", "machine-running", "device-left-on", "energy-cost"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="INA226 ±36V bus; INA228 ±85V bus", accuracy="INA226 0.1%; INA228 0.05%",
 resolution="INA226 16-bit; INA228 20-bit", rate="Up to ~3kHz conversion",
 i2c_addr="0x40-0x4F (A0/A1 pin-strapped)", pins=2, logic_3v3=True,
 pwr_ua=330.0, pwr_sleep_ua=2.0, hazard=[], calibration="One-point",
 consumable="None", lifecycle="Active", maturity="Good",
 esp32_compat="Any variant. The alert pin can wake the ESP32 on an over-current event.",
 requires="A shunt resistor matched to your current range, and the calibration register programmed "
          "to match it — an unprogrammed calibration register returns plausible but wrong numbers",
 substitutes="INA219 is cheaper and coarser; INA3221 gives three channels; ACS712 when you need "
             "galvanic isolation; INA700 has the shunt on-die",
 link="https://www.ti.com/product/INA228", confidence="High", as_of="2026-07",
 fools="It measures the voltage across a shunt, so shunt self-heating shows up directly as a "
       "reading that drifts as the load warms — high-current shunts need Kelvin connections and a "
       "temperature-stable resistor. INA228's coulomb counter accumulates silently and must be "
       "read before it wraps. High-side sensing needs the bus voltage within the part's common-mode "
       "range; exceed it and the readings are not merely wrong but meaningless. PWM'd loads alias "
       "badly unless you average across whole PWM cycles."),

"S146": dict(modality="Magnetic", phenomena=["current-dc", "current-ac", "magnetic-field"],
 inferences=["machine-running", "machine-state", "abnormal-current", "power-now",
             "device-left-on", "machine-duty-cycle", "bearing-failing", "cycle-complete"],
 contact="Through-barrier", privacy="None", environment=["Indoor", "Harsh"],
 range="±5A / ±20A / ±30A variants", accuracy="±1.5% at 25°C, worse over temperature",
 resolution="66-185 mV/A depending on variant", rate="80kHz bandwidth",
 pins=1, logic_3v3=False,
 pwr_ua=10000.0, hazard=["Mains"], calibration="One-point", consumable="None",
 lifecycle="Mature", maturity="Good",
 esp32_compat="Output is centred at Vcc/2, so a 5V-powered ACS712 idles at 2.5V and will damage a "
 "3.3V ADC input. Use a divider, or the 3.3V variant, and prefer an ADS1115 over the internal ADC.",
 requires="A voltage divider or level shift if run at 5V; RMS maths in software for AC",
 substitutes="INA226 for far better DC resolution when isolation is not needed; SCT-013 clamp for "
             "non-invasive mains; LEM closed-loop Hall for accuracy",
 link="https://www.allegromicro.com/en/products/sense/current-sensor-ics/integrated-current-sensors/acs712",
 confidence="Verified", as_of="2026-09",
 fools="Its zero point drifts with temperature and its noise floor is large relative to small "
       "currents — a ±30A part cannot usefully see 200mA, and people routinely buy the wrong range "
       "and conclude the sensor is broken. The offset must be re-zeroed at the operating "
       "temperature. It responds to any nearby magnetic field, so a motor or transformer next to it "
       "shifts the reading. For AC you must sample fast enough to compute true RMS; averaging the "
       "raw output gives zero regardless of load."),

"S148": dict(modality="Electrical", phenomena=["current-ac", "voltage", "energy-accumulated"],
 inferences=["power-now", "which-appliance", "phantom-load", "energy-cost", "power-quality",
             "device-left-on", "machine-running", "machine-duty-cycle"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="80-260VAC, 100A with the clamp version", accuracy="±0.5% class",
 resolution="0.1W, 1Wh", rate="~1Hz update", pins=2, logic_3v3=True,
 pwr_ua=30000.0, hazard=["Mains"], calibration="None", consumable="None",
 lifecycle="Active", maturity="Good",
 esp32_compat="The UART side is isolated from mains, which is what makes this the safest way for a "
 "maker to measure mains. Use a hardware UART, not SoftwareSerial.",
 requires="Mains wiring competence and an enclosure; the CT version needs the clamp around ONE "
          "conductor only",
 substitutes="A flashable smart plug for a single appliance with no wiring at all; SCT-013 plus "
             "EmonLib if you want the raw waveform; ATM90E32 for polyphase",
 link="https://en.peacefair.cn/product/772.html", confidence="High", as_of="2026-09",
 fools="Energy accumulates in the module's own non-volatile memory, not in your code, so a reset "
       "does not zero it and a replacement module starts from a different total. Clamping around "
       "both conductors of a cable reads zero because the fields cancel — the single most common "
       "wiring mistake. It reports real power, so it cannot distinguish a 100W resistive load from "
       "a 100W load with terrible power factor unless you also read the PF field. The 1Hz update "
       "is far too slow for appliance-signature disaggregation."),

"S149": dict(modality="Electrical", phenomena=["voltage"],
 inferences=["power-quality", "power-now", "device-left-on"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="Up to ~250VAC", accuracy="±1% after calibration", rate="Waveform-faithful to several kHz",
 pins=1, logic_3v3=False, pwr_ua=10000.0, hazard=["Mains"], calibration="Two-point",
 consumable="None", lifecycle="Active", maturity="Workable",
 esp32_compat="Analog output biased around mid-rail; use ADS1115 rather than the ESP32's ADC, and "
 "never ADC2 with Wi-Fi running.",
 requires="Calibration against a known mains voltage, and a fused, enclosed mains connection",
 substitutes="PZEM-004T if you want the maths done and isolation included; AMC1311 for isolated "
             "precision voltage sensing",
 link="", confidence="High", as_of="2026-07",
 fools="The onboard trim pot sets gain and arrives at an arbitrary position, so an uncalibrated "
       "module reports confident nonsense. Its transformer core saturates at the extremes, "
       "flattening waveform peaks and hiding exactly the sags and swells you bought it to see. "
       "Sampling must be synchronised to whole mains cycles or the computed RMS wanders. It "
       "provides functional isolation only — treat the low side as live for safety purposes."),

"S150": dict(modality="Electrical", phenomena=["current-dc", "voltage"],
 inferences=["power-now", "battery-charge", "abnormal-current", "machine-running"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="MAX471 ±3A; ADS1115 ±0.256V to ±6.144V programmable",
 accuracy="MAX471 ±2%; ADS1115 gain error <0.1%", resolution="ADS1115 16-bit",
 rate="ADS1115 8-860 SPS", i2c_addr="ADS1115 0x48-0x4B", pins=2, logic_3v3=True,
 pwr_ua=1000.0, pwr_sleep_ua=1.5, hazard=[], calibration="One-point", consumable="None",
 lifecycle="Active", maturity="Excellent",
 esp32_compat="The ADS1115 is the single most valuable upgrade for any analog sensing on an ESP32 — "
 "the internal ADC is non-linear, noisy, and unusable on ADC2 while Wi-Fi is active.",
 requires="A shunt sized so the expected current produces a voltage within the chosen PGA range",
 substitutes="INA226 integrates shunt amplifier, ADC and power maths in one part",
 link="https://www.ti.com/product/ADS1115", confidence="High", as_of="2026-07",
 fools="The ADS1115's 860 SPS maximum is a hard ceiling that catches people trying to sample audio "
       "or mains waveforms with it. Its differential mode is what makes it powerful and is widely "
       "unused. Setting a PGA range narrower than the actual signal silently clips. MAX471's "
       "high-side sensing puts the bus voltage on its pins, so exceeding its rating destroys it "
       "rather than saturating gracefully."),

# ---------------------------------------------------------------- position
"S151": dict(modality="Mechanical", phenomena=["angle-relative"],
 inferences=["object-moved", "rotation-speed"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="Continuous rotation, typically 20 detents/rev", resolution="4 counts per detent in quadrature",
 rate="Human speed; PCNT handles any realistic rate", pins=3, logic_3v3=True,
 pwr_ua=100.0, hazard=[], calibration="None",
 consumable="Mechanical contacts wear; ~50,000-100,000 rotations", lifecycle="Active",
 maturity="Excellent",
 esp32_compat="Read it with the PCNT hardware peripheral (ESP32Encoder does this) — software "
 "polling misses steps whenever Wi-Fi interrupts, which is the usual cause of a 'jumpy' knob.",
 requires="Debouncing — RC filters on both channels or a hardware-filtered PCNT configuration",
 substitutes="AS5600 for a contactless magnetic knob with no wear; a capacitive touch slider for "
             "sealed panels",
 link="", confidence="High", as_of="2026-07",
 fools="Cheap EC11 encoders bounce badly, producing phantom counts and direction reversals — this "
       "is a hardware problem that software alone rarely fixes cleanly. The detent position often "
       "sits mid-transition, so a single click can register zero or two counts depending on how "
       "you sample. Modules with the resistors already fitted behave far better than bare "
       "encoders. Contacts degrade with use, and the failure is gradual and confusing rather than "
       "sudden."),

"S152": dict(modality="Magnetic", phenomena=["angle-absolute", "magnetic-field"],
 inferences=["rotation-speed", "object-moved", "am-i-level", "which-way-facing"],
 contact="Standoff", privacy="None", environment=["Indoor", "Harsh"],
 range="0-360° absolute", accuracy="±1° typical after linearisation", resolution="12-bit (0.088°)",
 rate="Up to ~1kHz sampling", i2c_addr="0x36 (fixed — a real constraint for multi-axis builds)",
 pins=2, logic_3v3=True, pwr_ua=6500.0, pwr_sleep_ua=1.5, hazard=[], calibration="One-point",
 consumable="None — fully contactless, nothing to wear", lifecycle="Active", maturity="Good",
 esp32_compat="Any variant. Fixed I2C address means multiple AS5600s need a TCA9548A multiplexer.",
 requires="A DIAMETRICALLY magnetised magnet (not axially) centred over the chip at 0.5-3mm — the "
          "wrong magnetisation is the most common reason it appears not to work",
 substitutes="AS5048A for 14-bit and SPI daisy-chaining; optical encoder for higher speed; KY-040 "
             "if relative steps are enough",
 link="https://ams.com/as5600", confidence="High", as_of="2026-07",
 fools="Magnet alignment dominates everything: off-centre by half a millimetre and linearity "
       "collapses, too far and the field is too weak, too close and it saturates. Any nearby "
       "ferrous metal or motor magnet distorts the field and biases the angle. The fixed 0x36 "
       "address is a hard limit — a two-axis gimbal needs a multiplexer. It reports absolute angle "
       "within one turn only; multi-turn counting is your software's job and is lost on reset."),

"S153": dict(modality="Optical", phenomena=["angle-relative"],
 inferences=["rotation-speed", "how-far-travelled", "machine-running", "machine-duty-cycle"],
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 range="Continuous; 600 pulses/rev typical (2400 counts in quadrature)",
 accuracy="Non-cumulative within a revolution", resolution="0.15° at 600PPR x4",
 rate="Tens of kHz", pins=2, logic_3v3=False, pwr_ua=40000.0, hazard=["Mechanical"],
 calibration="None", consumable="Bearings; the optical disc is sensitive to oil and dust",
 lifecycle="Active", maturity="Good",
 esp32_compat="NPN open-collector output at 5-24V — must be level-shifted or pulled up to 3.3V "
 "before touching a GPIO. Use PCNT for counting.",
 requires="Pull-up to 3.3V (not to the encoder's supply), and a rigid shaft coupling",
 substitutes="AS5600 for contactless absolute angle; a magnetic ring encoder for harsh environments",
 link="", confidence="High", as_of="2026-07",
 fools="The open-collector output swings to whatever you pull it up to — pulling up to the 24V "
       "supply destroys the ESP32 input, and this is exactly the mistake the catalog's logic_3v3 "
       "column exists to prevent. It counts relative motion only, so absolute position is lost at "
       "every power cycle and must be re-homed. Oil mist and dust on the optical disc cause "
       "intermittent missed counts that look like mechanical slip. Flexible couplings introduce "
       "backlash that shows up as hysteresis."),

"S154": dict(modality="Electrical", phenomena=["displacement-linear", "resistance"],
 inferences=["object-moved", "how-far-travelled", "container-fullness"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="60-500mm travel depending on part", accuracy="±1-2% of full scale",
 resolution="ADC-limited", rate="Instant", pins=1, logic_3v3=True,
 pwr_ua=100.0, hazard=[], calibration="Two-point",
 consumable="Wiper track wears; membrane SoftPots are rated in the low millions of actuations",
 lifecycle="Active", maturity="Good",
 esp32_compat="Read through an ADS1115 rather than the internal ADC for a stable reading. Membrane "
 "SoftPots need a fixed pull-down or they float wildly when untouched.",
 requires="A pull-down resistor for membrane types so an untouched strip reads a defined value",
 substitutes="Draw-wire encoder for long travel; VL53L0X for contactless linear position; magnetic "
             "linear encoder for harsh environments",
 link="https://www.spectrasymbol.com/linear-position-sensors/soft-membrane-linear-pots-softpot",
 confidence="High", as_of="2026-09",
 fools="A membrane SoftPot reads garbage when nothing is touching it — you must detect 'touched' "
       "separately, usually with a second sensing line, or you will act on meaningless values. "
       "Mechanical sliders develop dead spots and crackle as the track wears, and the failure is "
       "gradual. Both types drift with temperature and supply voltage, so ratiometric reading "
       "against the same reference the ADC uses is important."),

"S155": dict(modality="Optical", phenomena=["distance-point", "proximity", "illuminance"],
 inferences=["object-present", "container-fullness", "obstacle-ahead", "someone-present", "tank-level"],
 contact="Standoff", privacy="None", environment=["Indoor"],
 range="0-100mm (plus ambient light sensing)", accuracy="±1mm class at short range",
 resolution="1mm", rate="Up to ~50Hz", i2c_addr="0x29 (shared with the entire VL53 family)",
 pins=2, logic_3v3=True, pwr_ua=1700.0, pwr_sleep_ua=5.0, hazard=["Laser"], calibration="One-point",
 consumable="None", lifecycle="Mature", maturity="Good",
 esp32_compat="Any variant. Multiple units need XSHUT sequencing or a multiplexer because of the "
 "fixed address.",
 requires="Cover-glass crosstalk calibration if you mount it behind a window",
 substitutes="VL53L0X/L1X for longer range; VCNL4040 for smooth proximity with no dead zone; "
             "capacitive sensing for through-wall level",
 link="https://www.st.com/en/imaging-and-photonics-solutions/vl6180x.html",
 confidence="High", as_of="2026-07",
 fools="Like the whole VL53/VL6180 family it sits at a FIXED 0x29, so two on one bus is impossible "
       "without pulling each XSHUT low and reassigning addresses at boot — the single most common "
       "reason multi-sensor ToF builds never work. Cover glass reflects light straight back into "
       "the receiver and must be calibrated out or every reading is short. Dark and specular "
       "targets return far less signal, so range collapses on matt black and mirrors alike. "
       "Strong sunlight saturates the receiver."),

"S156": dict(modality="Mechanical", phenomena=["displacement-linear", "resistance"],
 inferences=["object-moved"], contact="Contact", privacy="None", environment=["Indoor"],
 range="±30° gimbal travel on two axes", accuracy="Coarse; centre position varies unit to unit",
 rate="Instant", pins=3, logic_3v3=True, pwr_ua=100.0, hazard=[], calibration="One-point",
 consumable="Potentiometer tracks wear", lifecycle="Active", maturity="Excellent",
 esp32_compat="Two ADC channels plus a button. Keep both on ADC1 — ADC2 stops working when Wi-Fi "
 "is active, which produces a joystick that freezes the moment the node connects.",
 requires="Per-unit centre calibration and a deadband, because the spring-return centre is never "
          "exactly mid-scale",
 substitutes="TLV493D 3D magnetic sensor for a sealed, wear-free joystick; a capacitive touch strip "
             "for flat panels",
 link="https://www.adafruit.com/product/512", confidence="High", as_of="2026-09",
 fools="The mechanical centre is not the electrical centre, and it differs per unit and drifts with "
       "temperature — without a deadband a robot will creep constantly. The two axes interact "
       "slightly at the extremes. The push-button switch bounces and shares ground with the "
       "potentiometers, so pressing it can nudge the axis readings."),

# ---------------------------------------------------------------- GNSS
"S157": dict(modality="RF", phenomena=["position-global", "radio-time"],
 inferences=["where-am-i", "how-fast-moving", "how-far-travelled", "asset-location",
             "crossed-boundary", "vehicle-speed"],
 contact="Remote", privacy="Identifiable", environment=["Indoor", "Outdoor"],
 range="Global", accuracy="~2.5m CEP open sky", rate="1-5Hz",
 pins=2, logic_3v3=True, pwr_ua=45000.0, pwr_sleep_ua=1000.0, hazard=[], calibration="None",
 consumable="Backup battery for the almanac; a dead one means a cold start every time",
 lifecycle="EOL", maturity="Excellent",
 esp32_compat="Any variant with a spare UART. Use a hardware UART — SoftwareSerial drops NMEA "
 "characters at 9600 baud under Wi-Fi load.",
 requires="Clear sky view; the ceramic patch antenna must face upward with ground plane beneath",
 substitutes="MAX-M10S is dramatically better in cities and uses less power; LC29H for cheap RTK",
 link="", confidence="High", as_of="2026-07",
 fools="The NEO-6M is a genuinely old single-constellation part and is outclassed in urban canyons "
       "where multi-constellation receivers still hold a fix. Cold start takes 30+ seconds and much "
       "longer with a dead backup battery, which many cheap clones ship with. Position "
       "'wanders' by several metres while stationary — averaging helps, but reporting raw fixes as "
       "movement is a classic false-positive source for geofences. It reports altitude far less "
       "accurately than horizontal position, typically by a factor of two or three. Many clone "
       "modules are counterfeit or relabelled."),

"S158": dict(modality="RF", phenomena=["position-global", "radio-time"],
 inferences=["where-am-i", "how-fast-moving", "how-far-travelled", "asset-location",
             "crossed-boundary", "heat-island"],
 contact="Remote", privacy="Identifiable", environment=["Outdoor"],
 range="Global, four constellations", accuracy="~1.5m CEP", rate="Up to 10Hz multi-GNSS",
 i2c_addr="0x42 (u-blox DDC)", pins=2, logic_3v3=True,
 pwr_ua=25000.0, pwr_sleep_ua=15.0, hazard=[], calibration="None", consumable="None",
 lifecycle="Active", maturity="Excellent",
 esp32_compat="Speaks UART or I2C; the I2C (DDC) interface saves pins and is well supported by the "
 "SparkFun library.",
 requires="Clear sky view; an active antenna for anything mounted indoors or under a canopy",
 substitutes="ZED-F9P or LC29H for centimetre RTK; NEO-6M only if cost dominates",
 link="https://www.u-blox.com/en/product/max-m10s-module", confidence="High", as_of="2026-07",
 fools="Multi-constellation improves availability far more than it improves accuracy — you get a "
       "fix in places the NEO-6M cannot, but the fix is still metres. The M10's low power comes "
       "from duty-cycled tracking modes that trade update rate for current, so headline power and "
       "headline rate cannot both be had. Position still wanders while stationary. Anything "
       "carrying continuous location is Identifiable data regardless of how you store it."),

"S159": dict(modality="RF", phenomena=["position-global", "heading", "radio-time"],
 inferences=["where-am-i", "which-way-facing", "how-far-travelled", "returned-to-spot",
             "structure-moved", "asset-location"],
 contact="Remote", privacy="Identifiable", environment=["Outdoor"],
 range="Global with a correction source", accuracy="1cm + 1ppm RTK fixed; ~1m standalone",
 rate="Up to 20Hz", i2c_addr="0x42", pins=2, logic_3v3=True,
 pwr_ua=130000.0, hazard=[], calibration="None",
 consumable="None", lifecycle="Mature", maturity="Good",
 esp32_compat="The ESP32 makes an excellent NTRIP client, pulling corrections over Wi-Fi and "
 "pushing them into the receiver over UART or I2C.",
 requires="A correction stream — either your own base station (a second receiver) or an NTRIP "
          "service — plus a multi-band antenna, which is a significant additional cost",
 substitutes="ZED-X20P is the successor; LC29H or UM980 give RTK far more cheaply; MAX-M10S if "
             "metre accuracy is enough",
 link="https://www.u-blox.com/en/product/zed-f9p-module", confidence="Verified", as_of="2026-07",
 fools="The advertised centimetre accuracy applies only in RTK FIXED state — in FLOAT it is "
       "decimetres and standalone it is metres, and code that does not check the fix-type flag will "
       "happily report float solutions as if they were fixed. It needs continuous corrections; a "
       "dropped NTRIP connection silently degrades accuracy by two orders of magnitude. A proper "
       "multi-band antenna costs as much again as the receiver and a cheap one negates the whole "
       "purchase. Convergence to fixed takes tens of seconds and restarts after signal loss. "
       "Budget for two receivers, since a rover needs a base."),

"S160": dict(modality="RF", phenomena=["radio-time"],
 inferences=["where-am-i"], contact="Remote", privacy="None", environment=["Outdoor"],
 range="Global", accuracy="PPS edge ~±50ns; end-to-end on an ESP32, microseconds",
 rate="1Hz", pins=3, logic_3v3=True, pwr_ua=30000.0, hazard=[], calibration="None",
 consumable="None", lifecycle="Active", maturity="Workable",
 esp32_compat="Attach the PPS pin to a GPIO interrupt and discipline a local timer against it. "
 "Interrupt latency and jitter, not the GNSS module, set your real accuracy.",
 requires="A GNSS module that exposes PPS, plus NMEA parsing to know which second the pulse marks",
 substitutes="A chip-scale atomic clock or a GPSDO for genuine metrology; NTP over Wi-Fi for "
             "millisecond-class sync at zero hardware cost",
 link="https://www.adafruit.com/product/746", confidence="High", as_of="2026-09",
 fools="The nanosecond figure belongs to the pulse edge, not to anything the ESP32 can timestamp — "
       "GPIO interrupt latency and FreeRTOS scheduling add microseconds of jitter, and Wi-Fi "
       "activity makes it worse. The pulse also keeps arriving when the module has lost its fix "
       "and is free-running, so you must check the validity flag or you will silently synchronise "
       "to drifting time. Cable length matters at this precision. Indoors it simply will not fix."),

# ---------------------------------------------------------------- thermal imaging
"S161": dict(modality="Thermal", phenomena=["temperature-field", "temperature-remote"],
 inferences=["overheating", "someone-present", "how-many-people", "person-fell",
             "machine-state", "bearing-failing", "mould-risk", "stove-left-on"],
 contact="Standoff", privacy="Aggregate", environment=["Indoor"],
 range="-40 to 300°C, 32x24 pixels", accuracy="±1.5°C typical", resolution="0.1°C NETD ~0.1K",
 rate="0.5-64Hz (higher rates halve effective resolution)",
 i2c_addr="0x33", pins=2, logic_3v3=True, pwr_ua=20000.0, pwr_sleep_ua=8.0,
 hazard=[], calibration="None", consumable="None", lifecycle="Active", maturity="Good",
 esp32_compat="Needs ~1.5KB per frame plus float maths — comfortable on an S3 or a WROVER with "
 "PSRAM, tight on a C3. Requires 1MHz I2C for usable frame rates.",
 requires="1MHz I2C, and enough RAM for the frame plus the calibration parameter set",
 substitutes="MLX90641 for a quarter of the pixels and less RAM; AMG8833 for cheap 8x8; FLIR Lepton "
             "for real radiometric imaging",
 link="https://www.melexis.com/en/product/MLX90640", confidence="High", as_of="2026-07",
 fools="Emissivity is the whole game and it is silently assumed: shiny metal has low emissivity and "
       "reads far cooler than it is, which means a thermal scan of a bare copper busbar "
       "underestimates a dangerous hotspot. Glass and most plastics are opaque to this band, so it "
       "cannot see through a window — it reads the window. The chip's own temperature enters the "
       "calculation, so it needs minutes to stabilise after power-up and drifts if mounted next to "
       "anything warm. Frames are noisy at high refresh rates; averaging is usually necessary."),

"S162": dict(modality="Thermal", phenomena=["temperature-field", "temperature-remote"],
 inferences=["overheating", "someone-present", "how-many-people", "machine-state", "stove-left-on"],
 contact="Standoff", privacy="Aggregate", environment=["Indoor"],
 range="-40 to 300°C, 16x12 pixels", accuracy="±1°C typical", rate="0.5-64Hz",
 i2c_addr="0x33", pins=2, logic_3v3=True, pwr_ua=18000.0, pwr_sleep_ua=8.0,
 hazard=[], calibration="None", consumable="None", lifecycle="Active", maturity="Good",
 esp32_compat="Quarter the pixels of the MLX90640 means quarter the RAM — this one is comfortable "
 "on a C3 where the 90640 is not.",
 requires="Nothing beyond I2C", substitutes="MLX90640 when you need the resolution; AMG8833 for cost",
 link="https://www.melexis.com/en/product/MLX90641", confidence="Estimate", as_of="2026-07",
 fools="192 pixels is genuinely coarse — a person at 4m occupies a handful of pixels, so this "
       "answers 'where is the heat' rather than 'what shape is it'. Same emissivity trap as the "
       "MLX90640: shiny surfaces read cold. Same warm-up and self-heating sensitivity. The wide "
       "110° field of view means each pixel covers a large area and averages everything in it, "
       "which hides small hotspots entirely."),

"S163": dict(modality="Thermal", phenomena=["temperature-field", "temperature-remote", "image-depth"],
 inferences=["overheating", "someone-present", "how-many-people", "person-fell", "bearing-failing",
             "machine-state", "fire-present"],
 contact="Standoff", privacy="Identifiable", environment=["Indoor", "Outdoor"],
 range="-10 to 140°C radiometric (high-gain), 160x120 pixels", accuracy="±5°C or 5%",
 resolution="NETD <50mK", rate="8.7Hz (export-controlled ceiling)",
 pins=6, logic_3v3=True, pwr_ua=160000.0, hazard=[], calibration="None",
 consumable="Shutter mechanism cycles", lifecycle="Mature", maturity="Workable",
 esp32_compat="The SPI video stream is demanding — an ESP32-S3 with PSRAM can buffer frames, but "
 "many builds use the ESP32 for control and hand video to a host.",
 requires="A breakout with the correct 2.8V/1.2V rails and a socket; VoSPI timing is unforgiving",
 substitutes="MLX90640 for a tenth of the price if 32x24 suffices; InfiRay P2 Pro as a phone module",
 link="https://www.sparkfun.com/purethermal-mini-pro-jst-sr-with-flir-lepton-3-5.html",
 confidence="Verified", as_of="2026-09",
 fools="A microbolometer needs periodic flat-field correction — the shutter clicks and the image "
       "freezes briefly, which will interrupt any real-time loop that does not expect it. The "
       "8.7Hz limit is regulatory, not technical, and higher-rate variants are export controlled. "
       "VoSPI has no flow control: miss the sync and you must resynchronise the whole stream, "
       "which is where most first implementations fail. At 160x120 faces become recognisable "
       "enough that this is genuinely Identifiable data, unlike the coarse thermopile arrays."),

"S164": dict(modality="Thermal", phenomena=["temperature-field", "temperature-remote"],
 inferences=["someone-present", "how-many-people", "occupancy-duration", "no-movement-alarm"],
 contact="Standoff", privacy="Aggregate", environment=["Indoor"],
 range="4x4 pixels, 5 to 50°C people-detection band", accuracy="±1.5°C",
 rate="~4Hz", i2c_addr="0x0A", pins=2, logic_3v3=False, pwr_ua=5000.0,
 hazard=[], calibration="None", consumable="None", lifecycle="Active", maturity="Workable",
 esp32_compat="5V part — check the module's logic levels before wiring to a 3.3V GPIO.",
 requires="5V supply; Omron's application notes are essentially required reading to get useful "
          "people-detection out of 16 pixels",
 substitutes="AMG8833 gives 64 pixels for less money; LD2410 mmWave detects stillness better and "
             "costs a tenth",
 link="https://www.components.omron.com/product-detail?partId=396", confidence="Verified",
 as_of="2026-09",
 fools="Sixteen pixels is very few: two people standing close merge into one blob, and a person at "
       "the edge of the field is a fraction of a pixel. It was tuned to separate humans from warm "
       "backgrounds, but sunlit floors, radiators and recently-vacated chairs still produce false "
       "positives. It cannot see through glass. At 4Hz, fast movement smears across frames."),

# ---------------------------------------------------------------- cameras
"S165": dict(modality="Optical", phenomena=["image-visible"],
 inferences=["object-present", "someone-present", "object-identity", "object-count",
             "growth-rate", "intrusion", "machine-state"],
 contact="Standoff", privacy="Raw-imagery", environment=["Indoor"],
 range="1600x1200 stills, 640x480 streaming", rate="~15-25fps at VGA",
 pins=16, logic_3v3=True, pwr_ua=180000.0, pwr_sleep_ua=1000.0,
 hazard=[], calibration="None", consumable="None", lifecycle="Mature", maturity="Good",
 esp32_compat="Requires PSRAM and consumes roughly 16 GPIO — this is why camera projects need a "
 "WROVER or an S3 and cannot be done on a C3.",
 requires="A 5V supply capable of 500mA (brownout during camera init is the classic failure), and "
          "PSRAM enabled in the build",
 substitutes="OV5640 for autofocus and resolution; XIAO ESP32S3 Sense for a far nicer package; "
             "Person Sensor if you want faces detected without ever handling an image",
 link="https://www.digikey.com/en/products/detail/universal-solder-electronics-ltd/Ai-Thinker-ESP32-CAM-WiFi-BT-BLE/14319899",
 confidence="High", as_of="2026-09",
 fools="Camera initialisation draws a current spike that browns out marginal supplies, and the "
       "resulting failure looks like a dead board rather than a power problem — this wastes more "
       "beginner time than anything else in the catalog. The fixed-focus lens is often badly set "
       "from the factory and can be rotated by hand to fix. Rolling shutter smears anything moving "
       "quickly. It runs hot enough to affect a co-located temperature sensor. And it is the one "
       "genuinely Raw-imagery part here: consider where it points before you mount it."),

"S166": dict(modality="Optical", phenomena=["image-visible"],
 inferences=["object-present", "object-identity", "object-genuine", "growth-rate", "colour-match"],
 contact="Standoff", privacy="Raw-imagery", environment=["Indoor"],
 range="2592x1944 stills with autofocus", rate="~15fps at 1080p on an S3",
 pins=16, logic_3v3=True, pwr_ua=200000.0, hazard=[], calibration="None", consumable="None",
 lifecycle="Active", maturity="Good",
 esp32_compat="Realistically needs an ESP32-S3 with PSRAM. The autofocus voice-coil needs its own "
 "firmware blob loaded at init, which several libraries omit.",
 requires="PSRAM, a solid 5V supply, and autofocus firmware upload at initialisation",
 substitutes="OV2640 when resolution does not matter; Arducam Mega for an SPI camera that frees "
             "GPIO; a dedicated vision module if you only need detections",
 link="https://www.seeedstudio.com/OV5640-Camera-for-XIAO-ESP32S3-Sense-With-Heat-Sink-p-5739.html",
 confidence="Verified", as_of="2026-09",
 fools="Autofocus does not work until the AF firmware is uploaded to the module at startup, and a "
       "camera that returns permanently blurry images is almost always this rather than a fault. "
       "Full-resolution frames are large enough that PSRAM is mandatory and Wi-Fi upload takes "
       "seconds per image. The higher pixel count does not help in low light — the pixels are "
       "smaller, so it is noisier than the OV2640 in the dark."),

# ---------------------------------------------------------------- bio
"S217": dict(modality="Biological", phenomena=["biopotential-ecg", "ppg-optical"],
 inferences=["heart-rate", "heart-variability", "blood-oxygen", "breathing-rate", "stress-arousal"],
 contact="Contact", privacy="Identifiable", environment=["Indoor"],
 range="ECG plus red/IR PPG, synchronised", rate="Up to 1600 SPS PPG, 200 SPS ECG",
 i2c_addr="0x5E", pins=2, logic_3v3=True, pwr_ua=800.0, pwr_sleep_ua=2.0,
 hazard=[], calibration="Periodic", consumable="Gel electrodes if used", lifecycle="Active",
 maturity="Workable",
 esp32_compat="The synchronised FIFO is the point — read both streams together or the "
 "pulse-transit-time calculation is meaningless.",
 requires="Dry or gel electrodes with good skin contact, and a stable mechanical mounting",
 substitutes="MAX30102 for PPG alone; AD8232 for ECG alone; MAX30001 for a cleaner clinical-grade "
             "front end",
 link="https://www.analog.com/en/products/max86150.html", confidence="Verified",
 as_of="2026-09",
 fools="Motion artefacts dominate both channels and are far larger than the signals you want — "
       "this is the central problem of wearable physiology, not sensor accuracy. Pulse transit "
       "time is a genuine research route to cuffless blood-pressure TRENDS, but it requires "
       "per-person calibration against a real cuff and drifts with posture, temperature and "
       "vascular tone; treating it as absolute blood pressure is not defensible. Electrode contact "
       "impedance changes as the skin sweats, so a signal that looks clean at minute one degrades "
       "by minute twenty."),

"S218": dict(modality="Thermal", phenomena=["temperature-contact", "flow-gas", "respiration"],
 inferences=["breathing-rate", "breathing-stopped", "sleep-stage-proxy"],
 contact="Contact", privacy="Identifiable", environment=["Indoor"],
 range="Breath-phase detection, not calibrated flow", rate="Fast bead NTC responds in ~100ms",
 pins=1, logic_3v3=True, pwr_ua=100.0, hazard=[], calibration="One-point",
 consumable="None", lifecycle="Active", maturity="Raw",
 esp32_compat="Read through an ADS1115 — the swings are small and the ESP32's own ADC is too noisy "
 "to resolve them reliably.",
 requires="A fast bare-bead thermistor (a potted probe is far too slow), and a stable mounting in "
          "the airstream",
 substitutes="Radar respiration for contactless breathing; a chest stretch band for effort rather "
             "than flow; a proper differential-pressure spirometer for real volumes",
 link="", confidence="Estimate", as_of="2026-07",
 fools="It senses temperature difference, not airflow, so it detects breath PHASE and rate but "
       "tells you nothing about volume — and it fails entirely when ambient air is near body "
       "temperature, which is exactly when a warm bedroom matters. Mouth breathing bypasses a "
       "nasal sensor completely. Any device on the face is disturbed by movement and by the "
       "wearer's awareness of it. This is a learning and biofeedback build, not a diagnostic one."),

# ---------------------------------------------------------------- industrial
"S219": dict(modality="Magnetic", phenomena=["inductance", "proximity"],
 inferences=["object-present", "rotation-speed", "machine-running", "cycle-complete",
             "object-count", "door-state"],
 contact="Standoff", privacy="None", environment=["Harsh", "Outdoor"],
 range="4mm (M12) / 8mm (M18) to ferrous metal", accuracy="Switching, not measuring",
 rate="Up to ~500Hz-1kHz", pins=1, logic_3v3=False, pwr_ua=10000.0,
 hazard=[], calibration="None", consumable="None", lifecycle="Active", maturity="Good",
 esp32_compat="NPN open-collector at 6-36V — MUST be level-shifted or pulled up to 3.3V. Pulling up "
 "to the 24V supply destroys the GPIO. Count pulses with PCNT.",
 requires="A pull-up to 3.3V (never to the sensor supply), and ideally optoisolation in an "
          "industrial environment",
 substitutes="Hall sensor plus a magnet for non-ferrous targets; photoelectric beam for any "
             "material; LDC1612 when you need distance rather than a switch",
 link="", confidence="High", as_of="2026-07",
 fools="It only sees FERROUS metal at the rated distance — aluminium, brass and stainless are "
       "detected at a fraction of the range or not at all, and the specified sensing distance "
       "assumes a mild-steel target of a specified size. The quoted range is for a standard target; "
       "a small screw head is detected much closer. Mounting it in a metal bracket detunes the "
       "oscillator, so shielded and unshielded versions have different flush-mounting rules. Its "
       "output rail is the supply rail, which is the hardware-destroying trap."),

"S220": dict(modality="Optical", phenomena=["proximity", "distance-point"],
 inferences=["object-present", "object-count", "crossed-boundary", "vehicle-approaching",
             "perimeter-crossed", "container-fullness"],
 contact="Standoff", privacy="None", environment=["Harsh", "Indoor"],
 range="3-80cm, potentiometer-adjustable", rate="Sub-millisecond", pins=1, logic_3v3=False,
 pwr_ua=25000.0, hazard=[], calibration="One-point", consumable="None",
 lifecycle="Active", maturity="Good",
 esp32_compat="5V NPN open-collector — pull up to 3.3V, not to 5V.",
 requires="A pull-up to 3.3V and a target with reasonable reflectivity",
 substitutes="Through-beam pair for reliability at distance; VL53L1X for actual distance rather "
             "than a threshold; inductive prox where optics would foul",
 link="", confidence="High", as_of="2026-07",
 fools="It is a diffuse-reflective sensor, so its trip distance depends on the target's colour and "
       "finish — a matt black object is detected at a fraction of the distance of a white one, and "
       "a highly angled surface may never be seen. The adjustment potentiometer drifts with "
       "temperature and vibration. Direct sunlight can saturate the receiver despite the modulated "
       "carrier. Dust and spider webs on the lens produce a permanently-triggered output, which is "
       "the usual outdoor failure."),

"S221": dict(modality="Optical", phenomena=["proximity"],
 inferences=["object-count", "rotation-speed", "cycle-complete", "crossed-boundary", "flow-rate"],
 contact="Standoff", privacy="None", environment=["Indoor"],
 range="A few mm across the slot", rate="Microsecond edges", pins=1, logic_3v3=True,
 pwr_ua=20000.0, hazard=[], calibration="None", consumable="None",
 lifecycle="Active", maturity="Excellent",
 esp32_compat="Needs a pull-up on the phototransistor collector; PCNT counts edges with zero CPU cost.",
 requires="A collector pull-up resistor and a current-limiting resistor for the LED — neither is "
          "included on bare parts",
 substitutes="Reed switch for zero standby power; Hall sensor for a sealed slot; inductive prox "
             "where optics would foul",
 link="", confidence="High", as_of="2026-07",
 fools="Bare parts are not modules: without a collector pull-up you read nothing, and without an "
       "LED current-limiting resistor you destroy the emitter. The output is slow-edged and noisy "
       "unless you follow it with a Schmitt trigger, which produces multiple counts per event — "
       "the usual reason a counter over-reads. Ambient IR (sunlight, incandescent lamps) leaks "
       "into the slot and can hold the output permanently on. Dust in the slot is a silent killer."),

"S222": dict(modality="Chemical", phenomena=["gas-concentration"],
 inferences=["machine-state", "abnormal-current", "overheating"],
 contact="Immersed", privacy="None", environment=["Harsh"],
 range="Rich/lean switch either side of stoichiometric", accuracy="A switch, not a measurement",
 rate="~100ms once hot", warmup="Heater must reach ~350°C — tens of seconds, and readings before "
 "that are meaningless", pins=1, logic_3v3=True,
 pwr_ua=1500000.0, hazard=["HotSurface", "HighCurrent"], calibration="None",
 consumable="Cell poisons with leaded fuel, silicone and oil; typically 1-3 years in service",
 lifecycle="Active", maturity="Workable",
 esp32_compat="The 0-1V cell output suits an ADS1115. The heater needs its own 12V supply at "
 "1-2A — never from the ESP32 rail.",
 requires="A separate 12V heater supply, and an ADC that can resolve tens of millivolts",
 substitutes="A wideband LSU plus a CJ125 controller if you need an actual linear O2 reading; an "
             "electrochemical O2 cell for ambient air rather than exhaust",
 link="https://www.bosch-mobility.com/en/solutions/sensors/switching-type-lambda-sensor/",
 confidence="Verified", as_of="2026-09",
 fools="A narrowband sensor is a switch, not a meter — its output is steeply non-linear and only "
       "meaningful within a hair of stoichiometric, so using it to 'measure' combustion efficiency "
       "across a range is a category error. It only works hot, and it reads garbage during warm-up. "
       "Silicone sealants, oil and leaded fuel poison the cell permanently. The heater draws amps "
       "and will brown out anything sharing its supply."),

"S223": dict(modality="RF", phenomena=["rf-backscatter", "pressure-absolute", "temperature-contact"],
 inferences=["object-identity", "overheating", "drift-from-baseline", "machine-state"],
 contact="Remote", privacy="Identifiable", environment=["Outdoor", "Harsh"],
 range="A few metres from wheel to receiver", rate="Senders transmit every 30-60s while moving",
 pins=4, logic_3v3=True, pwr_ua=16000.0, hazard=[], calibration="None",
 consumable="The in-wheel senders have sealed batteries lasting 5-10 years and are not replaceable",
 lifecycle="Active", maturity="Raw",
 esp32_compat="CC1101 over SPI. Decoding is the hard part, not the radio.",
 requires="Knowledge of your specific senders' protocol; rtl_433's decoder set is the practical "
          "starting point",
 substitutes="A commercial aftermarket TPMS display if you only want the numbers; a direct "
             "pressure sensor if you can plumb into the system",
 link="https://www.ti.com/product/CC1101", confidence="Estimate", as_of="2026-09",
 fools="Sender protocols are manufacturer-specific and undocumented, and some are now encrypted or "
       "rolling-coded, so there is no guarantee your particular wheels are readable at all. Senders "
       "sleep when stationary and only transmit while rolling, so bench testing gives you nothing. "
       "Transmission is infrequent by design to preserve battery, so this is a slow-leak monitor "
       "rather than a blowout detector. Receiving other people's tyre data as they drive past is a "
       "privacy consideration worth thinking about before you log everything you hear."),

"S224": dict(modality="Electrical", phenomena=["capacitance", "dielectric-constant"],
 inferences=["contamination", "lubrication-failing", "drift-from-baseline", "moisture-content"],
 contact="Immersed", privacy="None", environment=["Harsh"],
 range="Relative dielectric shift, not an absolute unit", accuracy="Trend instrument only",
 i2c_addr="0x50 (FDC1004)", pins=2, logic_3v3=True, pwr_ua=750.0,
 hazard=[], calibration="Two-point",
 consumable="Probe fouling changes the baseline over time", lifecycle="Active", maturity="Raw",
 esp32_compat="FDC1004 over I2C. Shield drive is essential; long unshielded probe cables swamp the "
 "femtofarad signal.",
 requires="A stable concentric probe geometry, shielded cabling, and a temperature sensor — "
          "dielectric constant is strongly temperature dependent",
 substitutes="Send a sample to a lab for real oil analysis; a particle counter for wear debris",
 link="https://www.ti.com/product/FDC1004", confidence="Estimate", as_of="2026-09",
 fools="Dielectric constant moves with temperature far more than with mild contamination, so "
       "without temperature compensation you are mostly plotting how warm the oil is. It cannot "
       "distinguish water ingress from oxidation from metal particles — all raise the reading, so "
       "it tells you something changed rather than what. Probe geometry must be rigid and "
       "unchanging; a probe that shifts a millimetre invalidates the entire baseline. Varnish "
       "buildup on the electrodes drifts the zero over months."),

# ---------------------------------------------------------------- materials
"S225": dict(modality="Electrical", phenomena=["capacitance", "resistance", "pressure-tactile"],
 inferences=["object-present", "someone-present", "posture", "object-moved"],
 contact="Contact", privacy="None", environment=["Indoor"],
 range="Touch and pressure over sewn areas", accuracy="Qualitative",
 pins=1, logic_3v3=True, pwr_ua=50.0, hazard=[], calibration="One-point",
 consumable="Thread oxidises and abrades; resistance rises with washing and wear",
 lifecycle="Active", maturity="Workable",
 esp32_compat="Works with the ESP32's native touch pins (classic/S2/S3 only — C3/C6/H2 have NO "
 "touch peripheral) or with an MPR121 for many pads.",
 requires="Mechanical strain relief where thread meets rigid electronics — this joint is where "
          "e-textiles always fail",
 substitutes="Velostat for pressure matrices; EeonTex for repeatable piezoresistive fabric; "
             "conductive fabric tape for larger areas",
 link="https://www.adafruit.com/product/640", confidence="Verified", as_of="2026-09",
 fools="Stainless thread has meaningful resistance per metre, so a long run behaves like a resistor "
       "in series with your sensor and shifts the reading. Washing raises resistance permanently "
       "and repeated flexing eventually breaks strands, producing intermittent faults that are "
       "very hard to locate. Capacitive sensing through fabric changes completely with humidity "
       "and with whether the wearer is sweating. The thread-to-PCB joint is the standard failure "
       "point and needs a mechanical anchor, not just solder."),

"S226": dict(modality="Optical", phenomena=["ir-near", "moisture-material"],
 inferences=["plant-thirsty", "growth-rate", "drift-from-baseline"],
 contact="Contact", privacy="None", environment=["Indoor", "Outdoor"],
 range="Relative leaf thickness change", accuracy="Relative to a per-plant baseline only",
 rate="Minutes — the diurnal cycle is the signal", pins=1, logic_3v3=True,
 pwr_ua=20000.0, hazard=[], calibration="One-point", consumable="Clip foam compresses over weeks",
 lifecycle="Active", maturity="Raw",
 esp32_compat="Pulse the emitter and sample synchronously to reject ambient light; an ADS1115 "
 "helps considerably.",
 requires="A gentle, constant clamping force — too tight damages the leaf and changes what you are "
          "measuring; and a per-plant, per-leaf baseline",
 substitutes="Soil tension for the conventional measurement; thermal imaging for canopy temperature "
             "as a stress proxy; a dendrometer for woody stems",
 link="", confidence="Estimate", as_of="2026-07",
 fools="It measures light transmission, which changes with leaf thickness AND with chlorophyll "
       "content, leaf angle, dust and the clip slipping — so drift over days may be the plant, the "
       "clip, or the leaf ageing. Ambient light leaks into the detector unless the emitter is "
       "pulsed and sampled differentially. The leaf grows and eventually outgrows the calibration. "
       "This is a genuinely experimental technique, not a product."),

"S227": dict(modality="Optical", phenomena=["colour", "spectral-power", "ph"],
 inferences=["colour-match", "water-ph", "water-nutrients", "food-fresh", "contamination"],
 contact="Standoff", privacy="None", environment=["Indoor"],
 range="As good as the indicator chemistry allows", accuracy="Depends entirely on the media",
 i2c_addr="0x29 (TCS34725)", pins=2, logic_3v3=True, pwr_ua=3000.0,
 hazard=[], calibration="Two-point", consumable="The indicator media itself — strips, gels, cards",
 lifecycle="Active", maturity="Workable",
 esp32_compat="Any variant. Note the TCS34725 also sits at 0x29, colliding with the entire VL53 "
 "ToF family — a real conflict if you combine colorimetry with ranging.",
 requires="A light-tight chamber with a controlled illuminant, a white reference, and a fixed "
          "geometry between sensor, sample and light",
 substitutes="AS7341 for spectral resolution rather than three broad channels; a dedicated "
             "colorimeter for anything quantitative",
 link="https://www.adafruit.com/product/1334", confidence="Estimate", as_of="2026-09",
 fools="Everything about this technique is geometry and illumination: change the distance, the "
       "angle or the ambient light and the numbers move more than the chemistry does. Indicator "
       "media age, are batch-variable and are usually temperature dependent. Most strips are "
       "designed for a human eye reading against a printed chart at a specified time after "
       "dipping, so timing matters as much as colour. The 0x29 address collision with VL53 ToF "
       "sensors is easy to overlook until nothing on the bus responds."),

# ---------------------------------------------------------------- frontier
"S228": dict(modality="RF", phenomena=["rf-channel-state"],
 inferences=["someone-present", "through-wall-motion", "breathing-rate", "person-fell", "how-many-people"],
 contact="Remote", privacy="Aggregate", environment=["Indoor"],
 range="Room to building scale", accuracy="Research-grade; not characterised",
 rate="Up to hundreds of packets/s", pins=0, logic_3v3=True,
 pwr_ua=80000.0, hazard=[], calibration="Reference",
 consumable="None", lifecycle="Active", maturity="Raw",
 esp32_compat="Needs the esp-csi component and a firmware build that exposes CSI callbacks — this "
 "is not an Arduino sketch.",
 requires="At least two ESP32s (transmitter and receiver), a stable RF environment, and a machine-"
          "learning pipeline; the raw CSI stream is not directly interpretable",
 substitutes="mmWave radar does the same job far more reliably today for about five dollars; PIR "
             "plus mmWave for a robust production answer",
 link="https://github.com/espressif/esp-csi", confidence="Estimate", as_of="2026-07",
 fools="Published accuracy figures come from controlled environments and degrade sharply in real "
       "rooms — moving furniture, a new device joining the network, an open door or someone "
       "walking outside the room all change the channel and invalidate a trained model. It needs "
       "retraining per environment and often per week. The technique is genuinely exciting and "
       "genuinely not production-ready; treat demonstrations, including your own, with suspicion."),

"S229": dict(modality="Electrical", phenomena=["capacitance", "temperature-contact", "rf-power"],
 inferences=["someone-present", "object-present", "overheating", "who-is-it"],
 contact="Contact", privacy="Aggregate", environment=["Indoor"],
 range="Touch on up to 10 pads (classic/S2/S3 only)", accuracy="Relative",
 rate="Fast enough for UI", pins=0, logic_3v3=True, pwr_ua=10.0, pwr_sleep_ua=5.0,
 hazard=[], calibration="One-point", consumable="None", lifecycle="Mature", maturity="Good",
 esp32_compat="⚠ Touch exists on classic/S2/S3 ONLY — the C3, C6 and H2 have no touch peripheral. "
 "The internal hall sensor was REMOVED in ESP-IDF v5 and is unavailable on newer chips.",
 requires="Baseline calibration at boot, because absolute touch values drift with humidity, "
          "temperature and what the board is sitting on",
 substitutes="MPR121 for twelve properly-conditioned pads; TTP223 for a single reliable button; "
             "BLE RSSI (ESPresense) for room-level phone presence",
 link="https://www.espressif.com/en/products/socs/esp32", confidence="High", as_of="2026-09",
 fools="Of the four 'free sensors' this promises, three are effectively gone: the hall sensor was "
       "removed from the SDK, the internal temperature sensor reads self-heated die temperature "
       "and is useless as an ambient reading, and RSSI is a link metric rather than a calibrated "
       "sensor. Touch is the one that genuinely works, and even it drifts with humidity and needs "
       "re-baselining. Water on a touch pad reads as a permanent press."),

# ---------------------------------------------------------------- water
"S239": dict(modality="Chemical", phenomena=["dissolved-oxygen", "temperature-contact"],
 inferences=["water-oxygen", "compost-active", "livestock-wellbeing", "contamination"],
 contact="Immersed", privacy="None", environment=["Submersible", "Outdoor"],
 range="0-100 mg/L (0-600% saturation)", accuracy="±0.05 mg/L with careful calibration",
 resolution="0.01 mg/L", rate="~1 reading/s", warmup="Galvanic probes need ~30-60 min to "
 "stabilise after immersion", i2c_addr="0x61 (Atlas EZO default, changeable)",
 pins=2, logic_3v3=True, pwr_ua=10000.0, hazard=[], calibration="Two-point",
 consumable="Membrane cap and electrolyte — 6-12 months; the probe itself lasts years",
 lifecycle="Active", maturity="Good",
 esp32_compat="EZO circuits speak I2C or UART; I2C is easier but note EZO devices need their "
 "address set individually before sharing a bus.",
 requires="Water movement across the membrane — a galvanic probe CONSUMES oxygen at its surface "
          "and under-reads badly in still water; plus temperature and salinity compensation",
 substitutes="Optical (luminescent) DO probes need no flow and no membrane but cost more; a cheap "
             "analog DO kit for trends only",
 link="https://atlas-scientific.com/kits/dissolved-oxygen-kit/", confidence="Estimate", as_of="2026-07",
 fools="Galvanic probes consume oxygen as they measure, so a probe sitting in still water depletes "
       "its own boundary layer and reads progressively low — this single fact invalidates most "
       "casual pond deployments, which is why commercial installations always stir or pump. "
       "Readings must be compensated for temperature, salinity and altitude; uncompensated numbers "
       "can be tens of percent out. The membrane fouls with biofilm within weeks in a real pond. "
       "Calibration drifts and needs redoing monthly for data you intend to act on."),

# ------------------------------------------------- 2026-09 sourcing pass
# Purchase and datasheet links, and vendor SKU / library-name corrections,
# from the September 2026 sourcing pass. Every URL below was fetched and
# named the part. The evidence for each line — and the reason each sensor
# still without a link was left null rather than guessed — is in
# ../SOURCING_LOG.md.
"S004": dict(lib="Adafruit-MAX31855-library"),
"S007": dict(lib="Adafruit-MLX90614-Library"),
"S015": dict(
 brd="Adafruit 4099 weatherproof (ships an SHT30 element), cable probe versions"),
"S022": dict(link="https://cfsensor.com/product/xgzp6897d/", confidence="Verified",
 as_of="2026-09"),
"S025": dict(link="https://www.adafruit.com/product/5606", confidence="Verified",
 as_of="2026-09"),
"S026": dict(link="https://www.sparkfun.com/smoke-sensor-mq-2.html", as_of="2026-09"),
"S027": dict(link="https://www.sparkfun.com/products/8880", as_of="2026-09"),
"S028": dict(link="https://www.sparkfun.com/carbon-monoxide-sensor-mq-7.html",
 as_of="2026-09"),
"S029": dict(link="https://www.winsen-sensor.com/sensors/voc-sensor/mq135.html",
 as_of="2026-09"),
"S030": dict(link="https://www.adafruit.com/product/3199", confidence="Verified",
 as_of="2026-09"),
"S031": dict(
 link="https://www.digikey.com/en/products/detail/amphenol-sgx-sensortech/MICS-6814/15816395",
 as_of="2026-09"),
"S032": dict(link="https://www.adafruit.com/product/3709", confidence="Verified",
 as_of="2026-09"),
"S034": dict(link="https://www.winsen-sensor.com/sensors/ch2o-gas-sensor/ze08-ch2o.html",
 as_of="2026-09"),
"S035": dict(link="https://www.winsen-sensor.com/product/mh-741a.html", as_of="2026-09"),
"S038": dict(link="https://www.winsen-sensor.com/sensors/co2-sensor/mh-z19c.html",
 as_of="2026-09"),
"S039": dict(link="https://senseair.com/product/s8/", confidence="Verified",
 as_of="2026-09"),
"S044": dict(link="https://www.dfrobot.com/product-531.html", as_of="2026-09"),
"S046": dict(link="https://www.adafruit.com/product/4831", as_of="2026-09"),
"S047": dict(link="https://www.adafruit.com/product/1918", confidence="Verified",
 as_of="2026-09"),
"S049": dict(link="https://www.sparkfun.com/products/9088", as_of="2026-09"),
"S050": dict(link="https://www.sparkfun.com/sparkfun-spectral-uv-sensor-as7331-qwiic.html",
 confidence="Verified", as_of="2026-09"),
"S051": dict(brd="Adafruit 1334 (white LED, no STEMMA QT; discontinued)"),
"S052": dict(link="https://www.adafruit.com/product/4698", as_of="2026-09"),
"S053": dict(
 link="https://www.sparkfun.com/sparkfun-spectral-sensor-breakout-as7263-nir-qwiic.html",
 as_of="2026-09"),
"S054": dict(link="https://www.adafruit.com/product/3595", as_of="2026-09"),
"S056": dict(link="https://www.sparkfun.com/ultrasonic-distance-sensor-3-3v-hc-sr04.html",
 confidence="Verified", as_of="2026-09"),
"S061": dict(link="https://en.benewake.com/TFLuna/index.html", as_of="2026-09"),
"S062": dict(link="https://www.slamtec.com/en/c1", as_of="2026-09"),
"S063": dict(
 link="https://www.sparkfun.com/infrared-proximity-sensor-sharp-gp2y0a21yk.html",
 confidence="Verified", as_of="2026-09"),
"S064": dict(link="https://www.dfrobot.com/product-1935.html", as_of="2026-09"),
"S067": dict(link="https://www.hlktech.net/index.php?id=1094", as_of="2026-09"),
"S068": dict(link="https://www.hlktech.com/en/Goods-226.html", as_of="2026-09"),
"S069": dict(
 link="https://www.mouser.com/en/new/seeed-studio/seeed-studio-mr60bha2-sensor-kit",
 as_of="2026-09"),
"S071": dict(link="https://www.adafruit.com/product/3538", confidence="Verified",
 as_of="2026-09"),
"S072": dict(
 link="https://www.digikey.com/en/products/detail/tdk-invensense/MPU-6050/4038009",
 confidence="Verified", as_of="2026-09"),
"S081": dict(link="https://www.qstcorp.com/en_comp_prod/QMC5883L", confidence="Verified",
 as_of="2026-09"),
"S082": dict(link="https://www.adafruit.com/product/5579", confidence="Verified",
 as_of="2026-09"),
"S083": dict(
 lib="Infineon TLV493D-A1B6-3DMagnetic-Sensor Arduino library (archived Sep 2024; successor "
     "XENSIV TLx493D); Adafruit ships a CircuitPython driver only",
 link="https://www.adafruit.com/product/4366", confidence="Verified", as_of="2026-09"),
"S084": dict(
 link="https://automation.honeywell.com/us/en/products/sensing-solutions/sensors/magnetic-sensors/ss39et-ss49e-ss59et-linear-sensor-ics",
 as_of="2026-09"),
"S085": dict(link="https://www.adafruit.com/product/375", as_of="2026-09"),
"S086": dict(link="https://www.adafruit.com/product/4022", confidence="Verified",
 as_of="2026-09"),
"S087": dict(
 link="https://product.tdk.com/en/search/sw_piezo/mic/mems-mic/info?part_no=INMP441",
 as_of="2026-09"),
"S088": dict(link="https://www.adafruit.com/product/6049", as_of="2026-09"),
"S089": dict(link="https://www.adafruit.com/product/1713", confidence="Verified",
 as_of="2026-09"),
"S090": dict(link="https://www.adafruit.com/product/3421", confidence="Verified",
 as_of="2026-09"),
"S091": dict(link="https://www.sparkfun.com/piezo-element.html", as_of="2026-09"),
"S092": dict(link="https://www.dfrobot.com/product-1663.html", confidence="Verified",
 as_of="2026-09"),
"S094": dict(link="https://www.seeedstudio.com/Grove-Vibration-Sensor-SW-420.html",
 as_of="2026-09"),
"S096": dict(link="https://www.sparkfun.com/products/11744", confidence="Verified",
 as_of="2026-09"),
"S097": dict(link="https://www.sparkfun.com/products/9197", confidence="Verified",
 as_of="2026-09"),
"S100": dict(link="https://www.adafruit.com/product/1361", confidence="Verified",
 as_of="2026-09"),
"S101": dict(link="https://www.sparkfun.com/sparkfun-load-cell-amplifier-hx711.html",
 as_of="2026-09"),
"S102": dict(link="https://www.sparkfun.com/mini-load-cell-100g-straight-bar-tal221.html",
 as_of="2026-09"),
"S107": dict(link="https://bela.io/products/trill-touch-sensors/", confidence="Verified",
 as_of="2026-09"),
"S108": dict(link="https://www.dfrobot.com/product-1493.html", as_of="2026-09"),
"S109": dict(link="https://www.sparkfun.com/products/10264", as_of="2026-09"),
"S111": dict(
 link="https://www.digikey.com/en/products/detail/bend-labs-inc/100080101-01-EVAL/10484572",
 as_of="2026-09"),
"S112": dict(
 brd="GY-MAX30102, generic MAX30102 breakout (SparkFun sells MAX30101, not MAX30102)"),
"S115": dict(link="https://www.sparkfun.com/myoware-2-muscle-sensor.html",
 confidence="Verified", as_of="2026-09"),
"S116": dict(link="https://wiki.seeedstudio.com/Grove-GSR_Sensor/", as_of="2026-09"),
"S117": dict(lib="Adafruit-MLX90614-Library"),
"S120": dict(link="https://www.adafruit.com/product/4651", confidence="Verified",
 as_of="2026-09"),
"S121": dict(link="https://www.sparkfun.com/products/15901", as_of="2026-09"),
"S122": dict(link="https://www.sparkfun.com/weather-meter-kit.html", as_of="2026-09"),
"S123": dict(link="https://www.sparkfun.com/rain-gauge.html", as_of="2026-09"),
"S125": dict(link="https://www.sparkfun.com/products/12705", confidence="Verified",
 as_of="2026-09"),
"S129": dict(link="https://www.dfrobot.com/product-1385.html", confidence="Verified",
 as_of="2026-09"),
"S130": dict(link="https://www.jxct-iot.com/product/showproduct.php?id=197",
 confidence="Verified", as_of="2026-09"),
"S131": dict(link="https://www.adafruit.com/product/1965", as_of="2026-09"),
"S132": dict(link="https://www.adafruit.com/product/3846", as_of="2026-09"),
"S133": dict(link="https://www.adafruit.com/product/381", as_of="2026-09"),
"S138": dict(link="https://www.dfrobot.com/product-1517.html", as_of="2026-09"),
"S140": dict(link="https://www.adafruit.com/product/464", confidence="Verified",
 as_of="2026-09"),
"S142": dict(
 link="https://www.dypcn.com/integrated-waterproof-ultrasonic-liquid-level-sensor-ds1603-v1-0-product/",
 as_of="2026-09"),
"S167": dict(link="https://www.sparkfun.com/person-sensor-by-useful-sensors.html",
 confidence="Verified", as_of="2026-09"),
"S168": dict(link="https://www.dfrobot.com/product-1989.html", confidence="Verified",
 as_of="2026-09"),
"S171": dict(link="https://ecosense.io/products/radoneye", as_of="2026-09"),
"S177": dict(link="https://www.sparkfun.com/products/18768", confidence="Verified",
 as_of="2026-09"),
"S179": dict(link="https://www.dfrobot.com/product-2282.html", as_of="2026-09"),
"S180": dict(link="https://www.dfrobot.com/product-195.html", as_of="2026-09"),
"S181": dict(
 link="https://www.infineon.com/cms/en/product/sensor/radar-sensors/radar-sensors-for-iot/60ghz-radar/bgt60tr13c/",
 as_of="2026-09"),
"S183": dict(link="https://sensirion.com/products/catalog/SDP810-500Pa", as_of="2026-09"),
"S184": dict(link="https://www.winsen-sensor.com/product/mq-8.html", as_of="2026-09"),
"S186": dict(link="https://www.irrometer.com/200ss.html", as_of="2026-09"),
"S189": dict(link="https://www.adafruit.com/product/4566", as_of="2026-09"),
"S196": dict(
 link="https://www.sparkfun.com/sparkfun-proximity-sensor-breakout-20cm-vcnl4040-qwiic.html",
 confidence="Verified", as_of="2026-09"),
"S197": dict(link="https://www.adafruit.com/product/4019", as_of="2026-09"),
"S198": dict(link="https://maxbotix.com/products/mb7389", as_of="2026-09"),
"S199": dict(link="https://www.winsen-sensor.com/sensors/combustible-sensor/mq4.html",
 as_of="2026-09"),
"S200": dict(link="https://www.winsen-sensor.com/product/mq-6.html", as_of="2026-09"),
"S201": dict(link="https://www.winsen-sensor.com/sensors/o3-gas-sensor/mq131-l.html",
 as_of="2026-09"),
"S202": dict(link="https://www.adafruit.com/product/5593", confidence="Verified",
 as_of="2026-09"),
"S203": dict(
 link="https://industrial.panasonic.com/ww/products/pt/papirs/models/EKMC1603111",
 confidence="Verified", as_of="2026-09"),
"S206": dict(
 link="https://product.tdk.com/en/search/sensor/mortion-inertial/imu/info?part_no=MPU-9250",
 confidence="Verified", as_of="2026-09"),
"S207": dict(
 link="https://www.sparkfun.com/sparkfun-triple-axis-accelerometer-breakout-kx132-qwiic.html",
 confidence="Verified", as_of="2026-09"),
"S208": dict(link="https://www.adafruit.com/product/1063", confidence="Verified",
 as_of="2026-09"),
"S210": dict(link="https://www.adafruit.com/product/381", as_of="2026-09"),
"S211": dict(
 link="https://mouser.com/ProductDetail/SST-Sensing/LLC200D3SH?qs=3jNSNtuqJTJkvCfMBevuGw%3D%3D",
 confidence="Verified", as_of="2026-09"),
"S216": dict(link="https://www.murata.com/en-us/products/sensor/overview/item/scl3300-d01",
 as_of="2026-09"),
"S230": dict(link="https://www.sparkfun.com/products/14351", confidence="Verified",
 as_of="2026-09"),
"S233": dict(link="https://www.vernier.com/product/nitrate-ion-selective-electrode/",
 confidence="Verified", as_of="2026-09"),
"S236": dict(link="https://www.sparkfun.com/ultrasonic-distance-sensor-3-3v-hc-sr04.html",
 as_of="2026-09"),
"S255": dict(link="https://www.dfrobot.com/product-1863.html", confidence="Verified",
 as_of="2026-09"),
"S258": dict(link="https://www.sparkfun.com/obd-ii-to-db9-cable.html",
 confidence="Verified", as_of="2026-09"),
"S260": dict(link="https://automation.omron.com/en/us/products/family/E3Z/e3z-r61",
 as_of="2026-09"),
"S261": dict(
 link="https://www.digikey.com/en/products/detail/omron-automation-and-safety/E3Z-T61/408006",
 confidence="Verified", as_of="2026-09"),
"S262": dict(
 link="https://www.bannerengineering.com/us/en/products/machine-safety/safety-light-curtains/simple-rugged-safety-light-curtains-ls-series.html",
 as_of="2026-09"),
"S267": dict(
 link="https://www.sparkfun.com/sparkfun-simultaneous-rfid-reader-m6e-nano.html",
 as_of="2026-09"),
"S269": dict(link="https://www.nxp.com/products/PN5180A0HN", confidence="Verified",
 as_of="2026-09"),
"S271": dict(
 link="https://www.nxp.com/products/rfid-nfc/nfc-hf/connected-nfc-tags/ntag-ic-plus-2k-nfc-forum-type-2-tag-with-ic-interface:NTAG_I2C",
 confidence="Verified", as_of="2026-09"),
"S272": dict(link="https://www.priority1design.com.au/animal_tag_rfid_reader.html",
 as_of="2026-09"),
"S273": dict(link="https://www.hidglobal.com/products/proxpoint-plus", as_of="2026-09"),
"S274": dict(link="https://www.dfrobot.com/product-2051.html", confidence="Verified",
 as_of="2026-09"),
"S318": dict(
 link="https://ams-osram.com/products/sensor-solutions/ambient-light-color-spectral-proximity-sensors/ams-tcs3200-color-sensor",
 as_of="2026-09"),
"S323": dict(link="https://www.adafruit.com/product/2748", as_of="2026-09"),
"S331": dict(
 lib="ST VL53L4CD ULD driver (official portable C), vendor Arduino wrapper library"),
"S332": dict(lib="ST VL53L4CX ULD driver (official C), stm32duino VL53L4CX (Arduino)"),
"S334": dict(
 link="https://shop.pimoroni.com/en-us/products/pmw3901-optical-flow-sensor-breakout",
 confidence="Verified", as_of="2026-09"),
"S335": dict(
 link="https://shop.pimoroni.com/en-us/products/paa5100je-optical-tracking-spi-breakout",
 confidence="Verified", as_of="2026-09"),
"S340": dict(link="https://en.ai-thinker.com/pro_view-140.html", as_of="2026-09"),
"S341": dict(link="https://hlktech.net/index.php?cateid=755&id=1076", confidence="Verified",
 as_of="2026-09"),
"S349": dict(link="https://www.dfrobot.com/product-1797.html", confidence="Verified",
 as_of="2026-09"),
"S350": dict(
 link="https://www.gfps.com/int/en/products-solutions.catalog.html/measurement/flow/paddlewheel-sensors/~108393.html",
 as_of="2026-09"),
"S354": dict(
 link="https://www.vega.com/en-us/products/product-catalog/level/guided-wave-radar",
 as_of="2026-09"),
"S360": dict(link="https://implexx.io/products/implexx-sap-flow-sensor", as_of="2026-09"),
"S389": dict(link="https://www.microchip.com/en-us/product/at42qt1070", as_of="2026-09"),
"S390": dict(link="https://www.goodix.com/en/product/touch/touch_screen_controller",
 as_of="2026-09"),
"S392": dict(link="https://www.sparkfun.com/load-cell-200kg-s-type-tas501.html",
 as_of="2026-09"),
"S393": dict(link="https://www.sparkfun.com/products/13332", confidence="Verified",
 as_of="2026-09"),
"S394": dict(link="https://www.futek.com/store/torque-sensors/reaction-torque-sensor",
 as_of="2026-09"),
"S395": dict(link="https://www.adafruit.com/product/1361", as_of="2026-09"),
"S396": dict(link="https://www.adafruit.com/product/3669", as_of="2026-09"),
"S398": dict(link="https://www.adafruit.com/product/1168", confidence="Verified",
 as_of="2026-09"),
"S400": dict(link="https://www.st.com/en/mems-and-sensors/mp34dt05-a.html",
 as_of="2026-09"),
"S401": dict(link="https://www.cetaceanresearch.com/hydrophones/c57-hydrophone/index.html",
 as_of="2026-09"),
"S405": dict(link="https://www.semtech.com/products/wireless-rf/lora-connect/sx1262",
 as_of="2026-09"),
"S406": dict(
 link="https://www.digikey.com/en/products/detail/onsemi/MICROFC-SMA-60035-GEVB/9744738",
 as_of="2026-09"),
"S407": dict(link="https://www.vishay.com/en/product/81521/", as_of="2026-09"),
}
