"""Expansion part 12 — the families whose authoring agents hit the session limit.

Covers touch, force, flex, textiles, sound, RF and radiation, which were left as
the thinnest categories in the catalog.
"""

SENSORS = [

# ================================================================ TOUCH & CAPACITIVE
dict(catalog="sensor", n="CAP1188 8-channel capacitive touch", pn="CAP1188",
 cat="Touch & Capacitive", sub="Multi-pad controller", modality="Electrical",
 phenomena=["capacitance", "proximity"], inferences=["object-present", "someone-present"],
 meas="Eight independent capacitive touch channels with per-channel LED drivers",
 how="Each channel charges its electrode and measures how long it takes; a finger adds capacitance "
     "and slows it. Automatic recalibration tracks slow drift from humidity and temperature, which "
     "is what separates a controller from a raw touch pin.",
 range="Through up to ~5mm of plastic or glass", accuracy="Threshold-based, not proportional",
 rate="Up to 125Hz per channel", iface=["I2C", "SPI"], v="3.0-5.5V", logic_3v3=True,
 i2c_addr="0x28-0x2D", pins=2, esp32_compat="Works on every variant including C3/C6/H2, which have "
 "no touch peripheral of their own — this is how you get touch on those chips.",
 contact="Through-barrier", privacy="None", environment=["Indoor"],
 pwr="~50µA standby, 500µA active", pwr_ua=500.0, pwr_sleep_ua=50.0,
 usd=8.0, buy=["AF", "DK", "MO"], brd="Adafruit 1602", lib="Adafruit_CAP1188",
 link="https://www.microchip.com/en-us/product/CAP1188",
 lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="Water on a pad reads exactly like a finger, so anything in a kitchen or bathroom needs "
       "either a guard channel or logic that rejects simultaneous all-channel activation. Ground "
       "coupling matters more than people expect: a battery device with no earth reference is far "
       "less sensitive than the same board on a mains supply, so a design tuned on USB power can "
       "fail on a LiPo. Thick or high-permittivity overlays change sensitivity dramatically, and "
       "an air gap between the electrode and the panel destroys it.",
 hazard=[], calibration="One-point", consumable="None",
 requires="Electrodes bonded flush to the overlay with no air gap; recalibration at power-up",
 substitutes="MPR121 for twelve channels; ESP32 native touch on classic/S2/S3; TTP223 for one button",
 diff=2, use="Sealed control panels, appliance interfaces, e-textile buttons, hidden switches, "
 "museum exhibits.",
 spark="Because it works through a solid panel, a control surface can have no holes at all — the "
       "enabling trick for anything that must be washed down, sealed against dust, or survive "
       "being rained on.",
 pair="Conductive paint or copper tape electrodes; an OLED for feedback", tags=["Home", "Play", "Industry"]),

dict(catalog="sensor", n="AT42QT1070 / QT1010 touch controller", pn="AT42QT1070 (7ch) / AT42QT1010 (1ch)",
 cat="Touch & Capacitive", sub="Self-calibrating touch", modality="Electrical",
 phenomena=["capacitance"], inferences=["object-present"],
 meas="Robust touch detection with automatic drift compensation and adjacent-key suppression",
 how="Microchip's QTouch charge-transfer method plus Adjacent Key Suppression, which lets only the "
     "strongest-touched key register — the thing that makes a dense keypad feel right rather than "
     "triggering two keys at once.",
 range="Through 3-5mm overlay", rate="~18ms response", iface=["I2C"], v="1.8-5.5V",
 logic_3v3=True, i2c_addr="0x1B", pins=2,
 esp32_compat="Any variant. QT1010 is a single-channel part that needs no bus at all — one pin, one "
 "output.",
 contact="Through-barrier", privacy="None", environment=["Indoor"],
 pwr="~50µA low-power mode", pwr_ua=200.0, pwr_sleep_ua=50.0,
 usd=4.0, buy=["DK", "MO", "AE"], brd="Bare SOIC; SparkFun and generic breakouts",
 lib="Community AT42QT libraries, or raw I2C", link="",
 lifecycle="Active", maturity="Workable", confidence="Estimate", as_of="2026-07",
 fools="Its automatic drift compensation is a double-edged feature: a finger held on a key for many "
       "seconds is slowly calibrated OUT and the key appears to release, which breaks any 'press "
       "and hold' interaction. Recalibration also happens at power-up, so a device switched on with "
       "something resting on a pad will treat that as the baseline and never detect it.",
 hazard=[], calibration="None", consumable="None",
 requires="A stable ground reference; no object resting on the pads at power-up",
 substitutes="CAP1188 for LED drivers; MPR121 for more channels; Azoteq IQS for proximity plus touch",
 diff=2, use="Keypads, appliance controls, single-button wake, sealed panels.",
 spark="Adjacent-key suppression is what makes a numeric keypad behind glass feel like real buttons "
       "instead of a frustrating guess — worth the part on its own.",
 pair="Any sealed enclosure needing buttons", tags=["Home", "Industry", "Play"]),

dict(catalog="sensor", n="GT911 / FT6236 touchscreen controller", pn="GT911 (5-point) / FT6236 (2-point)",
 cat="Touch & Capacitive", sub="Touchscreen digitiser", modality="Electrical",
 phenomena=["capacitance", "position-relative"], inferences=["object-present"],
 meas="Multi-touch X/Y coordinates from a capacitive glass panel",
 how="A grid of transparent electrodes on the glass is scanned to find where capacitance changed. "
     "The controller reports actual coordinates and touch count, so your code deals in points "
     "rather than raw channels.",
 range="Panel-sized, up to 5 simultaneous touches", accuracy="Sub-millimetre",
 rate="~100Hz", iface=["I2C"], v="2.8-3.6V", logic_3v3=True, i2c_addr="0x5D or 0x14 (GT911)",
 pins=4, esp32_compat="Pairs with SPI TFT panels; LVGL has drivers for both controllers.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~20mA active, µA sleep", pwr_ua=20000.0, pwr_sleep_ua=10.0,
 usd=6.0, buy=["AE", "AMZ", "DFR"], brd="Usually bonded to a TFT panel rather than sold separately",
 lib="LVGL drivers, TAMC_GT911, FT6236 libraries", link="",
 lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="The GT911's I2C address depends on the state of its INT pin during reset, so the reset "
       "sequence must be exactly right or the device simply does not appear on the bus — this is "
       "the single most common bring-up failure. Capacitive panels do not work through gloves or "
       "with wet fingers. Panel and controller are usually a matched pair; mixing them gives "
       "mirrored or scaled coordinates that need software correction.",
 hazard=[], calibration="One-point", consumable="None",
 requires="A precise reset-and-address sequence; a matched panel",
 substitutes="Resistive touch (XPT2046) works with gloves and styluses but is single-touch and "
             "needs calibration; physical encoders where a screen is overkill",
 diff=3, use="Handheld instruments, control panels, smart displays, kiosks.",
 spark="A touchscreen is what makes a project legible to someone who did not build it — the "
       "difference between a device you demonstrate and a device you hand over.",
 pair="SPI TFT panel, LVGL, ESP32-S3 with PSRAM", tags=["Play", "Industry", "Home"]),

dict(catalog="sensor", n="Azoteq IQS7211 / IQS263 proximity + touch", pn="Azoteq IQS series",
 cat="Touch & Capacitive", sub="Proximity and gesture", modality="Electrical",
 phenomena=["capacitance", "proximity"], inferences=["object-present", "someone-present", "are-they-looking"],
 meas="Detects a hand approaching before it arrives, plus touch and simple gestures",
 how="Extremely sensitive charge-transfer sensing with automatic tuning, capable of detecting a "
     "hand tens of centimetres away — which lets a device wake as you reach for it rather than "
     "after you touch it.",
 range="Touch, plus proximity to ~10-30cm with a large electrode",
 rate="Configurable, tens of Hz", iface=["I2C"], v="1.8-3.6V", logic_3v3=True,
 i2c_addr="Part-dependent", pins=3,
 esp32_compat="Any variant; the interrupt output suits deep-sleep wake-on-approach.",
 contact="Standoff", privacy="Aggregate", environment=["Indoor"],
 pwr="Single-digit µA in proximity-watch mode", pwr_ua=20.0, pwr_sleep_ua=5.0,
 usd=6.0, buy=["DK", "MO"], brd="Azoteq evaluation boards; the parts appear inside many consumer devices",
 lib="Azoteq reference code; community Arduino ports are thin", link="https://www.azoteq.com/",
 lifecycle="Active", maturity="Workable", confidence="Estimate", as_of="2026-07",
 fools="Proximity range depends almost entirely on electrode size and the user's ground coupling, "
       "so the datasheet figures assume a large plate and a mains-referenced device — a small "
       "battery gadget achieves a fraction of it. Sensitive proximity settings pick up the user's "
       "whole body, not their hand, which makes gesture discrimination unreliable. Configuration is "
       "register-heavy and the tooling assumes their own IDE.",
 hazard=[], calibration="One-point", consumable="None",
 requires="A generously sized electrode, and tuning against the final enclosure and mounting",
 substitutes="VCNL4040 for optical proximity with far simpler setup; mmWave for room-scale presence",
 diff=4, use="Wake-on-approach displays, touchless controls, hidden interfaces, ultra-low-power "
 "presence in a small device.",
 spark="Single-digit microamps watching for an approaching hand means a battery device can appear "
       "instantly responsive while being asleep essentially all the time.",
 pair="A display that wakes on approach; deep-sleep interrupt wake", tags=["Home", "Play", "Energy"]),

# ================================================================ FORCE & WEIGHT
dict(catalog="sensor", n="S-type load cell", pn="S-type tension/compression cell, 50-500kg",
 cat="Force & Weight", sub="Load cell form factor", modality="Mechanical",
 phenomena=["force", "weight", "strain"],
 inferences=["consumable-remaining", "container-fullness", "object-present", "hive-state"],
 meas="Tension or compression along one axis, from tens to thousands of kilograms",
 how="A steel S-shaped body with strain gauges bonded at its high-stress points. The shape means it "
     "reads pull as well as push, which beam cells cannot do — the right choice for hanging loads "
     "and cable tension.",
 range="50kg to 5t depending on part", accuracy="0.02-0.05% of full scale",
 rate="Amplifier-limited", iface=["Analog"], v="5-10V excitation", logic_3v3=False, pins=4,
 esp32_compat="Needs an HX711 or NAU7802; the millivolt output is far below anything the ESP32 can "
 "read directly.",
 contact="Contact", privacy="None", environment=["Indoor", "Harsh", "Outdoor"],
 pwr="Excitation current only, ~10mA", pwr_ua=10000.0,
 usd=35.0, buy=["AE", "AMZ", "DK"], brd="Various; look for an IP-rated body for outdoor use",
 lib="HX711 or SparkFun NAU7802", link="",
 lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="Off-axis loading is the enemy: any side force or bending moment produces error far larger "
       "than the rated accuracy, so mounting hardware must allow the cell to see pure axial load — "
       "rod ends and swivels exist for exactly this. Overload past about 150% permanently deforms "
       "the element and the zero never returns. Cable length affects readings unless you use "
       "six-wire sense connections.",
 hazard=["Mechanical"], calibration="Two-point",
 consumable="None if never overloaded",
 requires="An HX711 or NAU7802, rod ends or swivels to eliminate side loading, and mechanical "
          "overload stops",
 substitutes="Bar/beam cells for platform scales; button cells for compression only; hydraulic load "
             "pins for very large forces",
 diff=3, use="Crane and hoist monitoring, cable tension, hanging tanks and hoppers, beehive scales, "
 "silo weight, test rigs.",
 spark="A hanging tank whose weight you log continuously tells you consumption rate, leak rate and "
       "refill timing from one measurement — weight over time is the most information-dense signal "
       "in this catalog.",
 pair="NAU7802 or HX711; a temperature sensor to compensate drift", tags=["Grow", "Industry", "Home"]),

dict(catalog="sensor", n="Button / pancake load cell", pn="Button compression cell, 5-500kg",
 cat="Force & Weight", sub="Load cell form factor", modality="Mechanical",
 phenomena=["force", "weight", "pressure-tactile"],
 inferences=["object-present", "someone-present", "posture", "consumable-remaining"],
 meas="Compression force through a small, low-profile disc",
 how="A compact steel puck with gauges inside, designed to be squeezed between two flat surfaces. "
     "Its thinness is the point — it fits under a foot, a bed leg or a machine mount where nothing "
     "else will.",
 range="5kg to 500kg", accuracy="0.1-1% depending on grade and mounting",
 iface=["Analog"], v="5-10V excitation", logic_3v3=False, pins=4,
 esp32_compat="HX711 or NAU7802 required.",
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 pwr="~10mA excitation", pwr_ua=10000.0, usd=25.0, buy=["AE", "AMZ", "DK"],
 brd="Various button and pancake cells", lib="HX711 / NAU7802", link="",
 lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="It only reads compression, and only through its centre: load applied off-centre or through "
       "an edge reads low and non-linearly, so it needs a load button or a hardened ball to "
       "concentrate force at the middle. It is very sensitive to the flatness of the surfaces it "
       "sits between. Four cells under a platform must be summed and individually calibrated, and "
       "a platform that rocks on three of four cells gives nonsense.",
 hazard=["Mechanical"], calibration="Two-point", consumable="None",
 requires="A load button or ball to centre the force, flat mating surfaces, and an amplifier",
 substitutes="Bar cells for cheap platform scales; FSRs where 'how hard' is qualitative; Velostat "
             "mats for pressure distribution rather than total",
 diff=3, use="Bed and chair occupancy, machine mount force, press monitoring, four-corner platform "
 "scales, force plates.",
 spark="Four button cells under a bed's legs give centre-of-mass as well as total weight — enough to "
       "infer breathing, restlessness and whether someone got up, with nothing worn and no camera.",
 pair="NAU7802 x4 or a summing junction; TCA9548A if using several I2C amplifiers", tags=["Health", "Home", "Industry"]),

dict(catalog="sensor", n="Rotary torque sensor", pn="Static/rotary reaction torque transducer",
 cat="Force & Weight", sub="Torque", modality="Mechanical",
 phenomena=["torque", "strain"], inferences=["machine-state", "abnormal-current", "lubrication-failing"],
 meas="Twisting force on a shaft, in newton-metres",
 how="Strain gauges bonded at 45° to a shaft measure the shear strain that torque produces. "
     "Reaction types measure the housing's resistance instead, which avoids slip rings entirely.",
 range="0.1 to hundreds of Nm", accuracy="0.1-0.5% of full scale",
 iface=["Analog"], v="Excitation or integrated amplifier", logic_3v3=False, pins=4,
 esp32_compat="Bare bridges need an HX711 or instrumentation amplifier; amplified units often give "
 "0-10V or 4-20mA and need the corresponding front end.",
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 pwr="10-50mA", pwr_ua=25000.0, usd=180.0, buy=["AE", "DK", "MO"],
 brd="Reaction torque sensors are far cheaper than rotating ones", lib="HX711 or 4-20mA reader",
 link="", lifecycle="Active", maturity="Workable", confidence="Estimate", as_of="2026-07",
 fools="Rotating torque measurement needs slip rings or telemetry to get the signal off a spinning "
       "shaft, which is where most of the cost and most of the failures live — reaction "
       "(non-rotating) sensors avoid this entirely and are the right choice whenever the housing "
       "can be restrained. Bending loads from misaligned couplings corrupt the reading badly. "
       "Temperature affects both zero and span.",
 hazard=["Mechanical"], calibration="Two-point", consumable="Slip rings wear on rotating types",
 requires="Precise shaft alignment, flexible couplings, and a rigid reaction mount",
 substitutes="Motor current as a torque proxy — far cheaper and adequate for detecting states "
             "rather than measuring them; a brake dynamometer for characterisation",
 diff=4, use="Motor characterisation, mixer and auger load monitoring, test rigs, fastener torque, "
 "pump and fan curve measurement.",
 spark="For most workshop purposes motor current is a good enough torque proxy at a fiftieth of the "
       "price — reach for a real torque sensor only when you need the number rather than the state.",
 pair="An encoder for speed, so torque times speed gives real mechanical power", tags=["MachineHealth", "Industry", "Robots"]),

dict(catalog="sensor", n="Tactile pressure array", pn="Velostat/EeonTex matrix or commercial tactile skin",
 cat="Force & Weight", sub="Pressure mapping", modality="Mechanical",
 phenomena=["pressure-tactile", "resistance"],
 inferences=["posture", "someone-present", "object-present", "gait-quality", "object-identity"],
 meas="A 2D map of pressure distribution rather than a single total",
 how="Rows and columns of conductor sandwich a piezoresistive layer; scanning row by row while "
     "reading columns gives a pressure value at every crossing point. The image is the product.",
 range="Set by the material; typically a few kPa to a few hundred", accuracy="±10-25%, poor "
 "repeatability — this is imaging, not metrology",
 rate="Scan-rate limited, typically 10-50Hz for a modest matrix",
 iface=["Analog", "Digital"], v="3.3V", logic_3v3=True, pins=8,
 esp32_compat="Needs multiplexers on both axes; a CD74HC4067 pair gives a 16x16 grid from a handful "
 "of pins.",
 contact="Contact", privacy="Aggregate", environment=["Indoor"],
 pwr="Scan dependent, tens of mA", pwr_ua=30000.0, usd=25.0, buy=["AF", "AE", "DIY"],
 brd="DIY from Velostat and conductive fabric; commercial tactile skins exist at far higher cost",
 lib="Custom row/column scanning", link="",
 lifecycle="Active", maturity="Raw", confidence="Estimate", as_of="2026-07",
 fools="Crosstalk between adjacent cells is the central problem: current sneaks through neighbouring "
       "paths and smears the image unless you ground unscanned rows, which most DIY implementations "
       "do not. Velostat drifts substantially under sustained load and is strongly temperature "
       "dependent, so a mat left under a sleeping person reads differently at hour six than at hour "
       "one. Repeatability is poor enough that absolute pressure claims are not defensible.",
 hazard=[], calibration="Periodic", consumable="Piezoresistive film fatigues with repeated compression",
 requires="Multiplexers on both axes and grounding of unscanned lines to suppress crosstalk",
 substitutes="Four load cells for accurate total and centre of mass; a single FSR for 'is something "
             "there'; a ToF array for contactless posture",
 diff=4, use="Sleep posture, pressure-sore prevention, seat occupancy and posture, gait analysis, "
 "robot gripper skin, interactive floors.",
 spark="A bed-sized mat costs perhaps forty dollars in materials against thousands for a clinical "
       "one — and for pressure-sore prevention the useful signal is 'this region has been loaded "
       "for two hours', which needs relative data, not calibrated data.",
 pair="CD74HC4067 multiplexers; a load cell for absolute calibration", tags=["Health", "Play", "Robots"]),

# ================================================================ FLEX & STRETCH
dict(catalog="sensor", n="EeonTex piezoresistive fabric", pn="EeonTex LTT-SLPA / NW170-SLPA",
 cat="Flex & Stretch", sub="Piezoresistive textile", modality="Mechanical",
 phenomena=["pressure-tactile", "stretch", "resistance"],
 inferences=["posture", "breathing-rate", "object-present", "someone-present"],
 meas="Pressure and stretch across a fabric area",
 how="A knit or non-woven textile coated with conductive polymer whose resistance falls under "
     "compression or stretch. Unlike Velostat it drapes and breathes, so it can be sewn into "
     "clothing rather than laid under it.",
 range="Wide, material dependent", accuracy="Qualitative; significant hysteresis",
 iface=["Analog"], v="3.3V divider", logic_3v3=True, pins=1,
 esp32_compat="Read through an ADS1115; the resistance range is wide and the ESP32's ADC is too "
 "coarse at the extremes.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="Divider current only", pwr_ua=100.0, usd=15.0, buy=["AF", "SF"],
 brd="Sold by the sheet; cut and sew", lib="analogRead plus smoothing", link="",
 lifecycle="Active", maturity="Workable", confidence="Estimate", as_of="2026-07",
 fools="Hysteresis is large and slow: the resistance after releasing a press does not return to "
       "where it started for seconds or minutes, so absolute readings drift with use history. "
       "Washing degrades the coating. Contact resistance where the fabric meets its electrodes "
       "often dominates the measurement, which means how you attach it matters more than the "
       "material's own behaviour. Humidity and body moisture shift the baseline.",
 hazard=[], calibration="Periodic", consumable="Coating wears with flexing and washing",
 requires="Large-area electrodes with consistent contact pressure, and baseline tracking in software",
 substitutes="Conductive rubber cord for one-dimensional stretch; Bend Labs for calibrated angle; "
             "an IMU for posture without any textile at all",
 diff=4, use="Smart garments, breathing bands, posture shirts, soft robotics, plush interfaces, "
 "seat and mat sensing.",
 spark="A breathing band made of fabric is worn all night without complaint, which is the entire "
       "difference between a sleep sensor that produces data and one that ends up in a drawer.",
 pair="ADS1115, conductive thread, snap fasteners for washable connections", tags=["Health", "Play", "Home"]),

dict(catalog="sensor", n="Capacitive stretch sensor", pn="StretchSense-style capacitive silicone sensor",
 cat="Flex & Stretch", sub="Capacitive stretch", modality="Electrical",
 phenomena=["stretch", "capacitance"], inferences=["joint-angle", "breathing-rate", "posture", "gait-quality"],
 meas="Elongation measured as capacitance change, with far less hysteresis than resistive types",
 how="A silicone dielectric between two compliant electrodes forms a capacitor. Stretching makes it "
     "longer and thinner, which raises capacitance predictably — and because it is a capacitance "
     "rather than a resistance, it barely drifts.",
 range="Up to ~100% strain", accuracy="~1% of full scale, with low hysteresis",
 rate="Up to hundreds of Hz", iface=["I2C"], v="3.3V", logic_3v3=True, pins=2,
 esp32_compat="Commercial units have integrated capacitance-to-digital front ends; DIY versions need "
 "an FDC1004 or similar.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~1mA", pwr_ua=1000.0, usd=90.0, buy=["DK", "TIN"],
 brd="Commercial modules; DIY silicone-and-fabric versions are viable",
 lib="FDC1004 libraries for DIY builds", link="",
 lifecycle="Active", maturity="Workable", confidence="Estimate", as_of="2026-07",
 fools="Capacitance changes of a few picofarads are easily swamped by cable capacitance and by the "
       "proximity of the wearer's body, so shielded leads and a driven guard are not optional. "
       "Silicone takes a permanent set after prolonged stretching, shifting the zero. Sweat and "
       "moisture between the sensor and skin alter the reading.",
 hazard=[], calibration="Two-point", consumable="Silicone fatigues over thousands of cycles",
 requires="Shielded, short leads and a capacitance-to-digital converter with guard drive",
 substitutes="Conductive rubber cord at a twentieth of the price and far worse hysteresis; Bend "
             "Labs for angle; IMUs for limb orientation",
 diff=4, use="Motion capture garments, respiration bands, joint angle in rehabilitation, soft-robot "
 "proprioception, ergonomics research.",
 spark="Low hysteresis is the whole value: it makes a wearable that still reads correctly after an "
       "hour of movement, which resistive stretch sensors simply do not.",
 pair="FDC1004 for DIY builds; an IMU for combined orientation and articulation", tags=["Health", "Robots", "Play"]),

# ================================================================ MATERIALS & TEXTILES
dict(catalog="sensor", n="Conductive fabric and tape electrodes", pn="Silver-plated nylon, ripstop conductive fabric, copper tape",
 cat="Materials & Textiles", sub="Electrode material", modality="Electrical",
 phenomena=["capacitance", "resistance", "biopotential-ecg"],
 inferences=["object-present", "someone-present", "heart-rate", "muscle-effort"],
 meas="Provides the conductive surface that touch, biopotential and capacitive sensing need",
 how="Textiles plated with silver or nickel, or adhesive copper foil, giving a flexible conductor "
     "that can be cut to shape. It is the electrode, not the sensor — but the electrode usually "
     "determines whether the sensor works.",
 range="Ohms per square, material dependent", iface=["Analog"], v="any", logic_3v3=True, pins=0,
 esp32_compat="Works with native touch on classic/S2/S3, or with MPR121/CAP1188 on any variant.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="None of its own", pwr_ua=0.0, usd=12.0, buy=["AF", "SF", "AE"],
 brd="Sold by the metre or as adhesive sheet", lib="None — it is a material", link="",
 lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="Silver plating tarnishes and oxidises, and resistance rises steadily with age and washing — "
       "an electrode that worked when built can quietly stop working months later. Adhesive on "
       "conductive tape is usually NOT conductive, so overlapping two strips does not connect them "
       "unless you solder or crimp the joint, which is a very common silent failure. Dry textile "
       "electrodes for ECG have far higher contact impedance than gel electrodes and need a "
       "front-end designed for it.",
 hazard=[], calibration="None", consumable="Plating degrades with washing and abrasion",
 requires="Soldered or crimped joints rather than adhesive overlap; strain relief where fabric "
          "meets rigid electronics",
 substitutes="Conductive thread for sewn traces; gel electrodes for any serious biopotential work; "
             "copper PCB electrodes where flexibility is not needed",
 diff=2, use="Wearable ECG and EMG electrodes, e-textile touch surfaces, capacitive sensing "
 "electrodes, EMI shielding, soft switches.",
 spark="The electrode is usually the limiting factor in wearable biopotential work, not the "
       "amplifier — improving contact area and pressure beats upgrading the chip almost every time.",
 pair="MPR121 or CAP1188 for touch; BioAmp or AD8232 for biopotentials", tags=["Health", "Play", "Home"]),

dict(catalog="sensor", n="Embroidered / fabric antenna", pn="Conductive-thread antenna, flexible PCB antenna",
 cat="Materials & Textiles", sub="Wearable RF", modality="RF",
 phenomena=["rf-power"], inferences=["asset-location", "object-identity"],
 meas="Radiates and receives RF from a flexible, wearable structure",
 how="A conductive pattern sewn or printed onto fabric, dimensioned for the target frequency. It "
     "lets a garment carry its own antenna instead of a rigid stub.",
 range="Frequency and geometry dependent", accuracy="Detuning of several percent is normal",
 iface=["Analog"], v="passive", logic_3v3=True, pins=0,
 esp32_compat="Replaces a chip or wire antenna on a wearable node; matching network is essential.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="Passive", pwr_ua=0.0, usd=10.0, buy=["AE", "DIY"], brd="DIY embroidery or flex PCB",
 lib="None — RF design", link="",
 lifecycle="Active", maturity="Raw", confidence="Estimate", as_of="2026-07",
 fools="The human body is mostly water and absorbs 2.4GHz strongly, so an antenna against the body "
       "loses a great deal of its efficiency and radiates asymmetrically — bench measurements on a "
       "table are meaningless. Bending changes the electrical length and detunes it. Conductive "
       "thread has far higher loss than copper, so efficiency is poor before you start. Without a "
       "vector network analyser you are guessing at the match.",
 hazard=[], calibration="Reference", consumable="Thread degrades with washing",
 requires="A matching network tuned with the antenna in its actual worn position; a ground plane "
          "or counterpoise",
 substitutes="A small rigid chip antenna kept away from the body; an external whip on a short "
             "coaxial lead",
 diff=5, use="Wearable connectivity, RFID-enabled garments, body-area networks, research.",
 spark="A garment that is its own antenna removes the last rigid component from a wearable — "
       "genuinely interesting, and genuinely hard to do well without RF instrumentation.",
 pair="ESP32-C3 wearable node; an SWR meter or VNA to have any idea what you built", tags=["Play", "Health", "Invisible"]),

# ================================================================ SOUND & AUDIO
dict(catalog="sensor", n="PDM MEMS microphone", pn="MP34DT05 / SPM0405HD4H",
 cat="Sound & Audio", sub="PDM digital mic", modality="Acoustic",
 phenomena=["sound-pressure"], inferences=["unusual-sound", "someone-present", "machine-state", "glass-broken"],
 meas="Audio as a single-bit oversampled stream on two wires",
 how="Pulse-density modulation sends a one-bit stream at a few megahertz; the density of ones "
     "encodes the waveform. It needs only a clock and a data line, which is why it is used where "
     "pins are scarce.",
 range="~60Hz-20kHz", accuracy="64-65dB SNR typical", rate="1-3.5MHz clock",
 iface=["I2S"], v="1.6-3.6V", logic_3v3=True, pins=2,
 esp32_compat="ESP32-S3 has hardware PDM support; on other variants PDM-to-PCM conversion in "
 "software costs meaningful CPU.",
 contact="Standoff", privacy="Raw-imagery", environment=["Indoor"],
 pwr="~650µA", pwr_ua=650.0, pwr_sleep_ua=1.0, usd=3.0, buy=["DK", "MO", "AE"],
 brd="Bare SMD; several XIAO and dev boards include one", lib="ESP-IDF I2S PDM mode",
 link="", lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="PDM output is not audio — it must be decimated and filtered to PCM before it means "
       "anything, and getting the filter wrong produces an aliased mess that sounds like a broken "
       "microphone. The port hole must be acoustically sealed to the enclosure opening, and a "
       "cavity behind it creates a resonance that colours everything. Any microphone is "
       "Raw-imagery from a privacy standpoint: it captures speech whether or not you process it.",
 hazard=[], calibration="Two-point", consumable="None",
 requires="A gasket sealing the port to the enclosure hole; a decimation filter",
 substitutes="I2S mics (INMP441, ICS-43434) are far easier on non-S3 chips; analog mics with an "
             "AGC amplifier for simple level detection",
 diff=3, use="Voice interfaces, acoustic event detection, sound level monitoring, wearables where "
 "pin count matters.",
 spark="Two PDM mics a known distance apart give direction of arrival by time difference — enough "
       "to point a camera at whoever is speaking, without any beamforming library.",
 pair="ESP32-S3 for hardware PDM; TinyML audio classifiers", tags=["Play", "Home", "Safety"]),

dict(catalog="sensor", n="Hydrophone", pn="Piezo hydrophone element, potted",
 cat="Sound & Audio", sub="Underwater acoustics", modality="Acoustic",
 phenomena=["sound-underwater", "sound-pressure"],
 inferences=["unusual-sound", "water-leak", "machine-state", "livestock-wellbeing"],
 meas="Sound in water — marine life, machinery, leaks, rainfall on the surface",
 how="A piezo element potted in a compliant material whose acoustic impedance is close to water, so "
     "sound crosses into it instead of reflecting off. Water carries sound far better than air, so "
     "a hydrophone hears a long way.",
 range="Element dependent; tens of Hz to tens of kHz", accuracy="Uncalibrated unless bought as such",
 iface=["Analog"], v="passive, needs a preamp", logic_3v3=True, pins=1,
 esp32_compat="Needs a high-impedance preamp; feed the output to I2S-ADC or an external ADC.",
 contact="Immersed", privacy="None", environment=["Submersible", "Outdoor"],
 pwr="Passive element; preamp mA", pwr_ua=2000.0, usd=45.0, buy=["AE", "DIY", "DK"],
 brd="Commercial potted hydrophones; DIY from a piezo disc and polyurethane",
 lib="Custom; audio recording pipelines", link="",
 lifecycle="Active", maturity="Raw", confidence="Estimate", as_of="2026-07",
 fools="Piezo elements have very high output impedance, so the preamp must be right at the element "
       "— a long cable before amplification loses the signal entirely, and this is why DIY "
       "hydrophones so often produce nothing but hum. Potting compound with the wrong acoustic "
       "impedance reflects sound away. Cable strumming from water movement produces low-frequency "
       "noise that swamps everything, so strain relief and slack management matter. Water ingress "
       "at the cable entry is the usual death.",
 hazard=[], calibration="Reference", consumable="Potting degrades with UV and time",
 requires="A preamp at the element, careful potting, and cable strain relief",
 substitutes="A contact piezo on a pipe or hull for structure-borne sound; a commercial calibrated "
             "hydrophone for anything quantitative",
 diff=5, use="Marine mammal monitoring, fish activity, pipe and tank leak detection, boat machinery "
 "monitoring, rainfall measurement on water bodies.",
 spark="Water is an extraordinary acoustic medium — a single hydrophone in a pond or harbour hears "
       "further than any camera sees, and almost nobody is listening.",
 pair="ESP32-S3 recording to SD; a spectrogram classifier", tags=["Wild", "Water", "Invisible"]),

dict(catalog="sensor", n="40kHz ultrasonic transducer pair", pn="Open-structure 40kHz TX/RX pair",
 cat="Sound & Audio", sub="Ultrasound transducers", modality="Acoustic",
 phenomena=["ultrasound", "distance-point"],
 inferences=["air-leak", "obstacle-ahead", "object-present", "arc-or-discharge"],
 meas="Transmit and receive ultrasound at 40kHz as separate elements",
 how="Separate transmitter and receiver elements rather than a packaged rangefinder, which lets you "
     "control the drive, the gain and the timing — the difference between a distance module and an "
     "acoustic instrument.",
 range="Several metres with adequate drive", rate="40kHz carrier",
 iface=["Analog", "PWM"], v="Drive up to 20Vpp for range", logic_3v3=True, pins=2,
 esp32_compat="Generate the burst with LEDC or RMT; amplify the receiver before the ADC.",
 contact="Standoff", privacy="None", environment=["Indoor", "Harsh"],
 pwr="Burst dependent", pwr_ua=20000.0, usd=3.0, buy=["AE", "DK", "MO"],
 brd="Bare transducer pairs", lib="Custom drive and envelope detection", link="",
 lifecycle="Active", maturity="Workable", confidence="High", as_of="2026-07",
 fools="They are sharply resonant — drive them at 38kHz instead of 40kHz and output collapses, so "
       "the drive frequency must match the element. Range depends on drive voltage, and 3.3V "
       "produces a fraction of what a step-up transformer achieves. The receiver rings after each "
       "transmit burst, creating a blind zone of tens of centimetres that no software fix removes. "
       "Air temperature changes the speed of sound by about 0.6% per 10°C, so uncompensated "
       "distance drifts with the weather.",
 hazard=[], calibration="One-point", consumable="None",
 requires="A resonant drive at the element's exact frequency, a receiver amplifier, and temperature "
          "compensation for distance work",
 substitutes="HC-SR04 or US-100 for packaged ranging; MEMS ultrasonic (TDK Chirp) for compact "
             "solid-state versions",
 diff=4, use="Compressed-air leak detection, custom sonar, level measurement in awkward geometry, "
 "acoustic levitation, parametric speakers, bat-frequency experiments.",
 spark="A parabolic reflector plus one receiver and a heterodyne mixer makes an ultrasonic leak "
       "detector: every compressed-air leak whistles at 40kHz, and each one found typically pays "
       "for the whole build.",
 pair="Step-up drive transformer, envelope detector, parabolic dish", tags=["MachineHealth", "Invisible", "Play"]),

dict(catalog="sensor", n="MEMS ultrasonic ToF (Chirp)", pn="TDK CH101 / CH201",
 cat="Sound & Audio", sub="MEMS ultrasound", modality="Acoustic",
 phenomena=["ultrasound", "distance-point", "proximity"],
 inferences=["obstacle-ahead", "object-present", "someone-present", "container-fullness"],
 meas="Ultrasonic time-of-flight ranging from a chip-scale device",
 how="A piezoelectric MEMS transducer plus an on-chip processor doing the whole ranging calculation. "
     "It gives ultrasonic ranging's indifference to target colour and transparency in a package the "
     "size of an LED.",
 range="CH101 up to 1.2m, CH201 up to 5m", accuracy="±1% of range",
 rate="Up to ~100Hz", iface=["I2C"], v="1.8V core", logic_3v3=True, i2c_addr="0x45 configurable",
 pins=3, esp32_compat="Needs 1.8V rails; most breakouts handle the translation.",
 contact="Standoff", privacy="None", environment=["Indoor"],
 pwr="~15µA at 1Hz ranging", pwr_ua=15.0, pwr_sleep_ua=1.0,
 usd=15.0, buy=["DK", "MO"], brd="TDK evaluation modules; SparkFun has carried Chirp boards",
 lib="TDK SonicLib", link="", lifecycle="Active", maturity="Workable",
 confidence="Estimate", as_of="2026-07",
 fools="Ultrasound still cannot see soft or steeply angled targets — foam, fabric and a wall at 45° "
       "scatter the echo away, exactly as with a cheap rangefinder. Its narrow beam is an advantage "
       "for precision and a disadvantage for detection, since a target slightly off axis is "
       "invisible. Air temperature and humidity change the speed of sound and therefore the range. "
       "The driver library is more involved than a typical Arduino sensor.",
 hazard=[], calibration="One-point", consumable="None",
 requires="1.8V supply handling and the SonicLib driver",
 substitutes="VL53L1X for optical ToF with a different failure set (glass, sunlight); HC-SR04 for "
             "cheap and coarse",
 diff=4, use="Robot obstacle detection where glass and dark surfaces defeat optical sensors, "
 "presence detection, level sensing, gesture.",
 spark="It sees clear glass and matt black equally well, which is precisely where laser ToF fails — "
       "pairing the two covers each other's blind spots almost perfectly.",
 pair="VL53L1X as the complementary modality; an IMU for robot navigation", tags=["Robots", "Home", "Industry"]),

# ================================================================ RF & ELECTROMAGNETIC
dict(catalog="sensor", n="RTL-SDR receiver", pn="RTL2832U + R820T2 USB dongle",
 cat="RF & Electromagnetic", sub="Software-defined radio", modality="RF",
 phenomena=["rf-power", "rf-backscatter"],
 inferences=["rf-activity", "object-identity", "asset-location", "which-appliance"],
 meas="Receives and decodes almost any radio signal from 24MHz to 1.7GHz",
 how="A wideband tuner feeding a fast analog-to-digital converter streams raw IQ samples to a "
     "computer, where software does all the demodulation. One piece of hardware becomes any "
     "receiver you can write.",
 range="24MHz-1.7GHz", accuracy="Frequency error of a few ppm unless TCXO-equipped",
 rate="Up to 2.4 MS/s usable", iface=["USB"], v="USB powered", logic_3v3=True, pins=0,
 esp32_compat="⚠ This needs a host computer — an ESP32 cannot process 2.4 MS/s of IQ. The usual "
 "architecture is a Raspberry Pi running rtl_433 that republishes decoded data over MQTT, which "
 "ESP32 nodes then consume.",
 contact="Remote", privacy="Identifiable", environment=["Indoor"],
 pwr="~300mA from USB", pwr_ua=300000.0, usd=30.0, buy=["AMZ", "AE"],
 brd="RTL-SDR Blog V4 (TCXO, better filtering) is worth the premium over generic dongles",
 lib="rtl_433, SDR++, GNU Radio, rtl-sdr", link="https://www.rtl-sdr.com/",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="It is receive-only and cannot transmit, which surprises people expecting a transceiver. "
       "Cheap dongles drift with temperature enough to lose narrowband signals, and a TCXO version "
       "is worth the extra. The antenna supplied is almost always inadequate for the band you care "
       "about. Legality varies: receiving is generally permitted, but decoding and acting on other "
       "people's data may not be — and logging your neighbours' sensors is a privacy question even "
       "where it is legal.",
 hazard=[], calibration="One-point", consumable="None",
 requires="A host computer, and an antenna cut for your target band",
 substitutes="CC1101 or SX1262 for a specific band at a tenth the cost and complexity; HackRF for "
             "transmit capability",
 diff=4, use="Decoding 433MHz weather and soil sensors, TPMS, aircraft ADS-B, utility meters, "
 "protocol reverse-engineering, spectrum surveys.",
 spark="Run rtl_433 for an hour and you will discover dozens of sensors already broadcasting around "
       "you — neighbours' weather stations, tyre sensors, doorbells. Adopting that existing "
       "telemetry costs one dongle and no new hardware at all.",
 pair="A Raspberry Pi running rtl_433 into MQTT; ESP32 nodes as consumers", tags=["Invisible", "Home", "Fleet"]),

dict(catalog="sensor", n="SX1262 sub-GHz transceiver", pn="SX1262 / SX1276 LoRa transceiver",
 cat="RF & Electromagnetic", sub="Sub-GHz radio", modality="RF",
 phenomena=["rf-power", "rf-channel-state"], inferences=["rf-activity", "asset-location"],
 meas="Long-range low-rate radio link, and a capable sub-GHz receiver for sniffing",
 how="LoRa spreads a tiny amount of data across a wide bandwidth so it can be recovered from below "
     "the noise floor — which is why it reaches kilometres on milliwatts. It also does plain FSK "
     "and OOK, making it a competent general sub-GHz receiver.",
 range="2-15km line of sight; 1-5km urban", accuracy="RSSI and SNR reported per packet",
 rate="0.3-50 kbps", iface=["SPI"], v="1.8-3.7V", logic_3v3=True, pins=6,
 esp32_compat="Any variant with SPI; integrated boards (LilyGO LoRa32, Heltec) save the RF wiring.",
 contact="Remote", privacy="None", environment=["Outdoor", "Indoor"],
 pwr="~5mA receive, 20-120mA transmit depending on power", pwr_ua=5000.0, pwr_sleep_ua=1.0,
 usd=8.0, buy=["AE", "AMZ", "DK"], brd="Ra-01SH modules, LilyGO LoRa32, Heltec WiFi LoRa 32",
 lib="RadioLib, LoRaWAN stacks, Meshtastic", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Transmitting without an antenna connected damages the power amplifier, sometimes on the "
       "first packet — fit the antenna before applying power, every time. Duty-cycle limits are "
       "legally binding in the EU (typically 1% on 868MHz), and a chatty node is not merely "
       "impolite but non-compliant. Long range comes at the cost of airtime: at the slowest spreading "
       "factor a single small packet occupies the channel for over a second. Range claims assume "
       "line of sight; a building between nodes changes everything.",
 hazard=[], calibration="None", consumable="None",
 requires="An antenna fitted before power-up, matched to your regional band",
 substitutes="CC1101 for cheap OOK/FSK sniffing without LoRa; ESP-NOW where Wi-Fi range suffices; "
             "cellular where infrastructure exists",
 diff=3, use="Field sensor telemetry, off-grid messaging (Meshtastic), farm and forest monitoring, "
 "flood gauges, and receiving other sub-GHz devices.",
 spark="Meshtastic turns a pair of these into an off-grid text network in an afternoon — then every "
       "sensor in this catalog can ride that network as telemetry with no infrastructure at all.",
 pair="Solar power, deep sleep, remote environmental sensors", tags=["Wild", "Fleet", "Invisible"]),

# ================================================================ RADIATION & NUCLEAR
dict(catalog="sensor", n="SiPM photodetector module", pn="Silicon photomultiplier (MicroFC / Broadcom AFBR)",
 cat="Radiation & Nuclear", sub="Photon detector", modality="Nuclear",
 phenomena=["ionising-radiation", "irradiance", "gamma-spectrum"],
 inferences=["radiation-dose", "which-isotope", "cosmic-flux"],
 meas="Detects individual photons — the modern replacement for a photomultiplier tube",
 how="An array of avalanche photodiodes biased just past breakdown, so a single photon triggers a "
     "measurable avalanche. Coupled to a scintillator crystal it turns each gamma ray into a pulse "
     "whose height is proportional to that ray's energy, which is what makes spectroscopy possible.",
 range="Single photon to thousands", accuracy="Energy resolution ~7% with a good CsI crystal",
 rate="Nanosecond pulses; count rates to hundreds of kHz", iface=["Analog"],
 v="~25-30V bias, temperature-compensated", logic_3v3=False, pins=1,
 esp32_compat="The ESP32 can count pulses easily; capturing pulse HEIGHT for spectroscopy needs a "
 "peak-hold circuit or a fast external ADC.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~1mA plus bias supply", pwr_ua=1000.0, usd=60.0, buy=["DK", "MO", "AE"],
 brd="MicroFC-SMA modules, Open Gamma Detector boards", lib="Open Gamma Detector firmware",
 link="", lifecycle="Active", maturity="Workable", confidence="Estimate", as_of="2026-07",
 fools="Gain is strongly temperature dependent — roughly a percent per degree — so an uncompensated "
       "spectrum shifts as the room warms and peaks smear into uselessness over an evening. The "
       "bias voltage must be stable to millivolts. Dark counts rise sharply with temperature and "
       "with bias, so there is an optimum rather than 'more is better'. Optical coupling to the "
       "crystal must be void-free, with optical grease and a reflective wrap, or resolution "
       "collapses.",
 hazard=["HighVoltage"], calibration="Two-point",
 consumable="None, unlike a PMT — SiPMs do not age from light exposure",
 requires="A stable temperature-compensated bias supply, a scintillator crystal, void-free optical "
          "coupling, and light-tight enclosure",
 substitutes="A Geiger tube for counting only, at a fraction of the cost and complexity; a PIN "
             "photodiode for cheap alpha detection",
 diff=5, use="Gamma spectroscopy, isotope identification, muon detection, scintillation counting, "
 "physics education.",
 spark="A SiPM is what moved isotope identification from a laboratory to a desk — 'this is "
       "radioactive' becomes 'this is thorium-232', which is a qualitative leap in what a hobby "
       "instrument can say.",
 pair="CsI(Tl) or NaI scintillator, ESP32-S3 with a peak-hold front end", tags=["Invisible", "Play", "Safety"]),

dict(catalog="sensor", n="PIN photodiode radiation detector", pn="BPW34 / BPX61 as a particle detector",
 cat="Radiation & Nuclear", sub="Solid-state detector", modality="Nuclear",
 phenomena=["ionising-radiation"], inferences=["radiation-dose", "cosmic-flux"],
 meas="Detects alpha particles and energetic beta/gamma using an ordinary photodiode",
 how="An ionising particle passing through the depletion region creates electron-hole pairs — a "
     "tiny charge pulse. Cover the diode to exclude light and amplify enormously, and a fifty-pence "
     "photodiode becomes a radiation detector.",
 range="Alpha readily; beta and gamma with low efficiency", accuracy="Counting only, unless "
 "carefully calibrated for energy",
 rate="Pulse rate dependent", iface=["Analog"], v="Reverse bias 9-30V for a wider depletion region",
 logic_3v3=False, pins=1,
 esp32_compat="Count pulses on a GPIO after a comparator stage; the raw pulses are microvolts and "
 "need serious amplification first.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="Amplifier current, ~5mA", pwr_ua=5000.0, usd=2.0, buy=["DK", "MO", "AE"],
 brd="Bare BPW34; several open-source detector designs exist", lib="Custom amplifier plus counter",
 link="", lifecycle="Active", maturity="Raw", confidence="Estimate", as_of="2026-07",
 fools="It must be absolutely light-tight — a pinhole floods it and the amplifier saturates, which "
       "looks like a broken circuit rather than a light leak. Sensitivity to gamma is poor because "
       "the silicon is thin, so background counting rates are very low and statistics are painful. "
       "The signal is microvolts, so amplifier noise, layout and shielding dominate the design; "
       "most first attempts detect their own power supply. Alpha detection requires the source to "
       "be extremely close, since alpha particles are stopped by paper.",
 hazard=["HighVoltage", "Radiation"], calibration="Reference", consumable="None",
 requires="A charge amplifier, a light-tight metal enclosure, and a stable bias supply",
 substitutes="A Geiger tube for far better gamma sensitivity and far less analog difficulty; a SiPM "
             "with scintillator for spectroscopy",
 diff=5, use="Alpha detection, radon progeny counting, cosmic-ray experiments, teaching the physics "
 "of particle detection cheaply.",
 spark="It is remarkable that an ordinary photodiode detects individual atomic decays — the physics "
       "is more compelling than the instrument, which makes it an excellent teaching build.",
 pair="Charge amplifier, comparator, ESP32 pulse counter", tags=["Invisible", "Play"]),
]
