"""Glue & Signal Chain — the parts that make the other parts work.

The expansion agents covered the industrial end (4-20mA, RS-485, CAN, IO-Link).
This file covers the core: conversion, amplification, multiplexing, translation,
timekeeping and power — the unglamorous components that decide whether an analog
sensor gives you data or noise.

The single most useful entry here is the ADS1115. The ESP32's own ADC is its
weakest organ, and roughly a third of this catalog reads better through a $3 chip.
"""

PARTS = [

# ================================================================ CONVERSION
dict(catalog="glue", n="ADS1115 / ADS1015 16-bit ADC", pn="ADS1115 (16-bit) / ADS1015 (12-bit)",
 cat="Power & Electrical", sub="Precision ADC", modality="Electrical",
 phenomena=["voltage"], inferences=[],
 meas="Four single-ended or two differential analog channels at true 16-bit, over I2C",
 how="A delta-sigma converter with a programmable gain amplifier in front of it. The PGA is the "
     "part people miss: set to ±0.256V it resolves 7.8 microvolts per bit, which is enough to read "
     "a thermocouple or a strain bridge directly.",
 range="±0.256V to ±6.144V programmable", accuracy="Gain error <0.1%, INL ±1 LSB",
 resolution="16-bit (ADS1115) — 7.8µV at the narrowest range", rate="8-860 SPS",
 iface=["I2C"], v="2.0-5.5V", logic_3v3=True, i2c_addr="0x48 / 0x49 / 0x4A / 0x4B (ADDR-strapped)",
 pins=2, esp32_compat="Any variant. This is the standard fix for the ESP32's non-linear internal "
 "ADC and for ADC2 becoming unusable the moment Wi-Fi starts.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="150µA continuous, 0.5µA in single-shot standby", pwr_ua=150.0, pwr_sleep_ua=0.5,
 usd=3.0, buy=["AF", "SF", "AE", "DK", "CE"], brd="Adafruit 1085, SparkFun Qwiic, generic purple modules",
 lib="Adafruit_ADS1X15", link="https://www.ti.com/product/ADS1115",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="860 SPS is a hard ceiling — people try to sample audio or mains waveforms with it and "
       "cannot. Setting a PGA range narrower than the actual signal clips silently, producing a "
       "flat-topped reading that looks like saturation of the sensor rather than of the ADC. "
       "Differential mode is the powerful feature and is almost always unused; single-ended "
       "readings inherit all the noise on your ground. It is ratiometric to its own supply, so a "
       "sagging 3.3V rail moves every reading.",
 hazard=[], calibration="One-point", consumable="None",
 requires="Nothing beyond I2C; a 0.1µF decoupling capacitor close to the chip",
 substitutes="ADS1256 for 24-bit and 30kSPS; MCP3424 for four differential channels; NAU7802 for "
             "bridge sensors; the internal ADC only when precision genuinely does not matter",
 diff=1, use="Every analog sensor in this catalog reads better through one: pH, EC, thermistors, "
 "current sensors, gas sensors, load cells, GSR, photodiodes.",
 spark="Buy three before you need them. The moment an analog reading looks noisy or non-linear, "
       "this is almost always the answer, and it converts a frustrating afternoon into a working "
       "instrument.",
 pair="Literally any analog sensor here", tags=["Energy", "Water", "Health"]),

dict(catalog="glue", n="ADS1256 24-bit ADC", pn="ADS1256",
 cat="Power & Electrical", sub="High-resolution ADC", modality="Electrical",
 phenomena=["voltage"], inferences=[],
 meas="Eight channels at 24-bit and up to 30,000 samples per second",
 how="A much faster and finer delta-sigma converter than the ADS1115 — the step up when you need "
     "both resolution and speed, such as capturing a seismic waveform or a strain event.",
 range="±5V with programmable gain to 64x", accuracy="0.0010% INL",
 resolution="24-bit (~23 noise-free bits at low rates)", rate="2.5 SPS to 30 kSPS",
 iface=["SPI"], v="5V analog, 1.8-3.6V digital", logic_3v3=True, pins=5,
 esp32_compat="Fast SPI; the ESP32 can keep up at moderate rates but sustained 30kSPS logging "
 "wants DMA and a buffer.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~38mW", pwr_ua=8000.0, usd=15.0, buy=["AE", "AMZ", "DK"],
 brd="Generic ADS1256 modules with onboard reference", lib="Community ADS1256 drivers",
 link="https://www.ti.com/product/ADS1256", lifecycle="Active", maturity="Workable",
 confidence="Estimate", as_of="2026-07",
 fools="24 bits of resolution does not mean 24 bits of accuracy — layout, reference noise and "
       "thermal EMF at connectors dominate long before the converter does, and most cheap modules "
       "deliver perhaps 18 useful bits. It needs a clean, separate analog supply to be worth "
       "having. The register interface is considerably more involved than the ADS1115's.",
 hazard=[], calibration="Two-point", consumable="None",
 requires="A clean analog supply and careful grounding; a stable voltage reference",
 substitutes="ADS1115 when 860 SPS is enough; ADS131M04 for simultaneous-sampling mains work",
 diff=4, use="Geophones and seismic logging, strain and load research, high-resolution "
 "electrochemistry, precision instrumentation.",
 spark="This is what turns a $30 geophone into a real seismometer — the sensor was never the "
       "limitation, the converter was.",
 pair="Geophones, strain bridges, ion-selective electrodes", tags=["Wild", "MachineHealth", "Invisible"]),

dict(catalog="glue", n="MCP4725 12-bit DAC", pn="MCP4725",
 cat="Power & Electrical", sub="Analog output", modality="Electrical",
 phenomena=[], inferences=[],
 meas="A programmable analog voltage from an I2C command",
 how="A resistor-ladder DAC with EEPROM, so it remembers its output across power cycles. This is "
     "how a C3 or C6 — which have no DAC at all — produce a real analog voltage.",
 range="0V to Vdd", accuracy="±0.2% of full scale", resolution="12-bit (0.8mV at 3.3V)",
 rate="Up to ~200kHz I2C-limited", iface=["I2C"], v="2.7-5.5V", logic_3v3=True,
 i2c_addr="0x60-0x67", pins=2,
 esp32_compat="Essential on C3/C6/H2 and the S2/S3, none of which have a DAC. The classic ESP32 "
 "has two DACs but they are only 8-bit and noisy.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~210µA", pwr_ua=210.0, pwr_sleep_ua=0.06, usd=4.0, buy=["AF", "SF", "AE", "DK"],
 brd="Adafruit 935, SparkFun Qwiic MCP4725", lib="Adafruit_MCP4725",
 link="https://www.microchip.com/en-us/product/MCP4725", lifecycle="Active", maturity="Excellent",
 confidence="High", as_of="2026-07",
 fools="Its output cannot drive a load — it is a voltage reference, not an amplifier, and connecting "
       "anything drawing more than a fraction of a milliamp drags it down. Buffer it with an op-amp "
       "if it must drive anything. Output is ratiometric to Vdd, so a noisy supply becomes a noisy "
       "output. The EEPROM has limited write endurance; writing it on every update wears it out.",
 hazard=[], calibration="One-point", consumable="EEPROM write endurance if abused",
 requires="An op-amp buffer if driving any real load",
 substitutes="PCM5102 for audio; PWM plus an RC filter for slow, cheap analog output; the classic "
             "ESP32's internal DAC for undemanding uses",
 diff=1, use="Setpoint generation, 0-10V industrial control (with a gain stage), function "
 "generators, analog control of legacy equipment, sensor simulation for testing.",
 spark="With a gain stage it produces the 0-10V signal that industrial dimmers, VFDs and valve "
       "actuators expect — the cheapest bridge between an ESP32 and the building-services world.",
 pair="Op-amp buffer, 0-10V output stage", tags=["Industry", "Play", "Energy"]),

dict(catalog="glue", n="NAU7802 24-bit bridge ADC", pn="NAU7802",
 cat="Force & Weight", sub="Load cell ADC", modality="Electrical",
 phenomena=["voltage", "strain"], inferences=["consumable-remaining", "container-fullness", "object-present"],
 meas="A 24-bit converter with a built-in bridge excitation supply — the modern HX711 replacement",
 how="Everything a strain-gauge bridge needs in one chip: a low-noise regulator to excite the "
     "bridge, a 128x programmable amplifier and a 24-bit converter, all on I2C so it shares a bus "
     "instead of demanding two dedicated pins.",
 range="±0.5V differential at gain 1", accuracy="Ratiometric to the excitation, so excitation drift "
 "cancels", resolution="24-bit, ~21 noise-free", rate="10-320 SPS",
 iface=["I2C"], v="2.7-5.5V", logic_3v3=True, i2c_addr="0x2A", pins=2,
 esp32_compat="Any variant. Far better than the HX711's bit-banged two-wire protocol, which is "
 "timing-sensitive and breaks under Wi-Fi interrupts.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~2mA active, µA in standby", pwr_ua=2000.0, pwr_sleep_ua=1.0,
 usd=12.0, buy=["SF", "AF", "DK"], brd="SparkFun Qwiic Scale NAU7802",
 lib="SparkFun NAU7802", link="", lifecycle="Active", maturity="Good",
 confidence="High", as_of="2026-07",
 fools="Load cells creep under sustained load and drift with temperature — the converter is rarely "
       "your accuracy limit, the mechanics are. Tare state must be stored in NVS or a reboot loses "
       "your zero. The fixed 0x2A address means multiple scales need a multiplexer. Mounting "
       "matters enormously: a load cell bolted to a flexing surface measures the surface.",
 hazard=[], calibration="Two-point", consumable="None",
 requires="A load cell or strain bridge, and rigid mounting with the correct overload stops",
 substitutes="HX711 is cheaper and everywhere in tutorials; ADS1256 if you need speed as well as "
             "resolution",
 diff=2, use="Scales, beehive weight, filament and gas-bottle gauges, force plates, strain "
 "measurement, dosing verification.",
 spark="Because it is I2C, several scales share one bus — a pantry where every container reports "
       "its own weight, which is the most underrated household telemetry there is.",
 pair="Load cells, strain gauges; a temperature sensor to compensate drift", tags=["Home", "Grow", "Health"]),

# ================================================================ AMPLIFICATION
dict(catalog="glue", n="INA333 instrumentation amplifier", pn="INA333 / AD8237",
 cat="Power & Electrical", sub="Instrumentation amp", modality="Electrical",
 phenomena=["voltage"], inferences=[],
 meas="Amplifies a tiny differential voltage while rejecting the noise common to both inputs",
 how="Three op-amps arranged so that whatever appears on BOTH inputs — mains hum, ground shifts, "
     "RF pickup — is subtracted away, while the difference between them is amplified. That common-"
     "mode rejection is what makes microvolt measurement possible in a noisy room.",
 range="Gain 1-1000 set by one resistor", accuracy="25µV max offset, 0.1µV/°C drift",
 iface=["Analog"], v="1.8-5.5V", logic_3v3=True, pins=1,
 esp32_compat="Feed its output into an ADS1115 rather than the ESP32's ADC, or you throw away the "
 "precision you just paid for.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="50µA", pwr_ua=50.0, usd=6.0, buy=["DK", "MO", "AE"],
 brd="Bare SOIC/MSOP, or breakout modules", lib="None — it is analog",
 link="https://www.ti.com/product/INA333", lifecycle="Active", maturity="Workable",
 confidence="High", as_of="2026-07",
 fools="Gain is set by a single external resistor and its tolerance directly becomes your gain "
       "error — a 5% resistor gives 5% gain error no matter how good the amplifier is. Input bias "
       "currents need a DC path to ground; leave the inputs floating and the output slams to a "
       "rail, which looks like a dead chip. Single-supply operation needs a mid-rail reference or "
       "you cannot represent negative differences at all.",
 hazard=[], calibration="Two-point", consumable="None",
 requires="A precision gain resistor, a DC return path for the inputs, and a reference voltage for "
          "single-supply use",
 substitutes="NAU7802 or HX711 if the source is a bridge; a differential ADS1115 input for modest gain",
 diff=4, use="Strain gauges, thermocouples, biopotential front ends, shunt current sensing, any "
 "microvolt-level differential signal.",
 spark="This is the part that lets you build a front end for a sensor nobody sells a module for — "
       "the difference between being limited to breakouts and being able to read anything.",
 pair="ADS1115 or ADS1256 behind it; precision resistors", tags=["Health", "MachineHealth", "Industry"]),

dict(catalog="glue", n="Transimpedance amplifier for photodiodes", pn="OPA381 / LMP7721 / OPA333",
 cat="Light & UV", sub="Photodiode front end", modality="Electrical",
 phenomena=["irradiance", "voltage"], inferences=[],
 meas="Converts a photodiode's picoamp-to-microamp current into a usable voltage",
 how="An op-amp with a large feedback resistor holds the photodiode at zero volts and converts its "
     "photocurrent to a voltage. The feedback resistor IS the gain, and it can be tens of megohms "
     "for low-light work.",
 range="Set by the feedback resistor", accuracy="Limited by op-amp bias current and resistor tolerance",
 iface=["Analog"], v="1.8-5.5V", logic_3v3=True, pins=1,
 esp32_compat="Output into an ADS1115. Keep the feedback network physically tiny and guarded.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~1mA", pwr_ua=1000.0, usd=5.0, buy=["DK", "MO"], brd="Bare op-amp plus a precision resistor",
 lib="None — analog", link="", lifecycle="Active", maturity="Raw",
 confidence="Estimate", as_of="2026-07",
 fools="At megohm gains, the layout matters more than the components: fingerprints and flux residue "
       "on the PCB conduct enough to swamp the signal, so the feedback network needs cleaning and "
       "often a guard ring. Stray capacitance across the feedback resistor turns the amplifier into "
       "an oscillator — a small compensation capacitor is mandatory. Photodiode dark current "
       "roughly doubles every 8°C, so a low-light instrument drifts with room temperature.",
 hazard=[], calibration="Two-point", consumable="None",
 requires="A guard ring, a compensation capacitor across the feedback resistor, and scrupulous "
          "board cleanliness",
 substitutes="An integrated light sensor (VEML7700, TSL2591) unless you need a specific photodiode "
             "or wavelength",
 diff=5, use="Custom optical sensing, scintillation detectors, laser measurement, colorimetry, "
 "flame detection, any photodiode without a matching module.",
 spark="Pair with a scintillator crystal and this becomes the front end of a gamma spectrometer — "
       "the amplifier is what separates counting particles from identifying isotopes.",
 pair="Photodiodes, SiPM detectors, scintillator crystals", tags=["Invisible", "Light", "Play"]),

dict(catalog="glue", n="Charge amplifier for piezo sensors", pn="LMP7721 / TL072-based charge amp",
 cat="Motion & Vibration", sub="Piezo front end", modality="Electrical",
 phenomena=["voltage", "vibration"], inferences=[],
 meas="Converts a piezo element's charge output into a proportional voltage",
 how="Piezo elements produce CHARGE, not voltage, and their apparent output depends on whatever "
     "capacitance you connect. A charge amplifier fixes that by integrating the charge into a known "
     "feedback capacitor, so the reading no longer depends on cable length.",
 range="Set by the feedback capacitor", iface=["Analog"], v="±5V or single supply with bias",
 logic_3v3=True, pins=1,
 esp32_compat="Output into an ADS1115 for slow events, or the ESP32's I2S-ADC mode for waveforms.",
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 pwr="~2mA", pwr_ua=2000.0, usd=6.0, buy=["DK", "MO", "DIY"], brd="DIY on protoboard; IEPE "
 "conditioners for industrial accelerometers", lib="None — analog", link="",
 lifecycle="Active", maturity="Raw", confidence="Estimate", as_of="2026-07",
 fools="Without one, a piezo's output changes when you change the cable — which is why the same "
       "sensor gives different readings on different rigs and people blame the sensor. The "
       "feedback capacitor needs a parallel resistor to define the low-frequency roll-off and stop "
       "the output drifting into a rail. Piezos can generate tens of volts on impact, so the input "
       "needs clamping diodes or the amplifier dies on the first hard knock.",
 hazard=[], calibration="Two-point", consumable="None",
 requires="Clamping diodes on the input, a bleed resistor across the feedback capacitor, and "
          "shielded cable",
 substitutes="A MEMS accelerometer with a digital output if you can accept its bandwidth; an IEPE "
             "conditioner for industrial sensors",
 diff=5, use="Acoustic emission, structural monitoring, impact measurement, drum triggers, "
 "machine-health vibration with piezo elements.",
 spark="Proper conditioning is what moves piezo work from 'it made a spike' to a calibrated "
       "measurement you can compare between machines and across months.",
 pair="Piezo discs, PVDF film, acoustic-emission sensors", tags=["MachineHealth", "Sound", "Play"]),

# ================================================================ EXPANSION
dict(catalog="glue", n="TCA9548A I2C multiplexer", pn="TCA9548A / PCA9548A",
 cat="Industrial & Automotive", sub="Bus expansion", modality="Electrical",
 phenomena=[], inferences=[],
 meas="Eight independent I2C buses from one, resolving address collisions",
 how="An addressable switch that connects the ESP32's bus to one of eight downstream buses at a "
     "time. It is the only practical way to run several sensors that share a fixed address.",
 range="8 channels", rate="Up to 400kHz", iface=["I2C"], v="1.65-5.5V", logic_3v3=True,
 i2c_addr="0x70-0x77 (so you can chain eight multiplexers)", pins=2,
 esp32_compat="Any variant. This is the fix for the catalog's most common wiring dead-end.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~100µA", pwr_ua=100.0, usd=4.0, buy=["AF", "SF", "AE", "DK"],
 brd="Adafruit 2717, SparkFun Qwiic Mux", lib="Adafruit_TCA9548A, or two lines of raw I2C",
 link="https://www.ti.com/product/TCA9548A", lifecycle="Active", maturity="Excellent",
 confidence="High", as_of="2026-07",
 fools="Only one channel is connected at a time, so anything needing continuous attention — an "
       "interrupt-driven sensor, a device you must not stall — behaves badly behind it. Pull-up "
       "resistors are needed on EVERY downstream branch, not just the main bus, and forgetting "
       "this produces channels that mysteriously do not work. Each branch adds capacitance, so "
       "long runs on several channels can push you below 400kHz.",
 hazard=[], calibration="None", consumable="None",
 requires="Pull-up resistors on each downstream branch",
 substitutes="Choosing sensors with configurable addresses; XSHUT sequencing for the VL53 family; "
             "a second I2C bus (the ESP32 has two)",
 diff=2, use="Multiple ToF sensors, several identical environmental sensors, sensor arrays, any "
 "bus with an address clash.",
 spark="The entire VL53 time-of-flight family sits at a fixed 0x29, so every multi-zone ranging "
       "project in this catalog — echolocation belts, people counters, shelf sensing — needs one "
       "of these or it simply cannot be built.",
 pair="Any two sensors sharing an address", tags=["Robots", "Home", "Industry"]),

dict(catalog="glue", n="CD74HC4067 analog multiplexer", pn="CD74HC4067 / 74HC4051",
 cat="Power & Electrical", sub="Analog channel expansion", modality="Electrical",
 phenomena=[], inferences=[],
 meas="Sixteen analog channels through one ADC pin",
 how="An analog switch array: four digital select lines choose which of sixteen inputs connects to "
     "the common pin. It expands scarce ADC channels at the cost of sampling them in sequence.",
 range="16 channels (4051 gives 8)", rate="Settling of a few microseconds per channel",
 iface=["Analog", "Digital"], v="2-6V", logic_3v3=True, pins=5,
 esp32_compat="Turns the ESP32's handful of usable ADC1 pins into many. Allow settling time between "
 "channel switches or you read the previous channel.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="<1µA static", pwr_ua=1.0, usd=2.0, buy=["AE", "SF", "AF", "DK"],
 brd="SparkFun and generic 16-channel breakouts", lib="digitalWrite the select lines",
 link="", lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="It has real on-resistance (~70Ω) which forms a divider with your source impedance — high-"
       "impedance sensors read low through it. Switching without a settling delay gives you a "
       "blend of the previous channel and the current one, which looks like crosstalk and is "
       "actually impatience. It cannot pass voltages outside its supply rails, so negative or "
       "above-rail signals are clipped or damaging.",
 hazard=[], calibration="One-point", consumable="None",
 requires="A settling delay after each channel change; a low-impedance source or a buffer",
 substitutes="ADS1115 boards at four different addresses for 16 buffered channels; a dedicated ADC "
             "per sensor where speed matters",
 diff=2, use="Thermistor arrays, pressure-mapping matrices, multi-zone soil sensing, "
 "keyboard/button matrices, Velostat mats.",
 spark="Sixteen cheap thermistors behind one of these becomes a thermal pixel wall or a "
       "multi-depth soil probe for the price of a sandwich — this is how you turn one measurement "
       "into a spatial map.",
 pair="Thermistors, FSRs, Velostat matrices, photoresistor arrays", tags=["Touch", "Grow", "Play"]),

dict(catalog="glue", n="MCP23017 I/O expander", pn="MCP23017 (I2C) / MCP23S17 (SPI)",
 cat="Industrial & Automotive", sub="GPIO expansion", modality="Electrical",
 phenomena=[], inferences=[],
 meas="Sixteen extra GPIO with interrupt support, over two wires",
 how="A register-based port expander with configurable direction, pull-ups and interrupt-on-change. "
     "The interrupt output is the important part: the ESP32 can sleep until a button somewhere on "
     "the expander actually changes.",
 range="16 pins, 8 devices per bus", rate="I2C-limited", iface=["I2C", "SPI"],
 v="1.8-5.5V", logic_3v3=True, i2c_addr="0x20-0x27", pins=2,
 esp32_compat="Very useful on pin-starved boards — a XIAO with eleven GPIO becomes one with "
 "twenty-five.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~1µA standby", pwr_ua=1000.0, pwr_sleep_ua=1.0, usd=3.0, buy=["AF", "AE", "DK", "MO"],
 brd="Adafruit 5346, generic modules", lib="Adafruit_MCP23X17",
 link="https://www.microchip.com/en-us/product/MCP23017", lifecycle="Active", maturity="Excellent",
 confidence="High", as_of="2026-07",
 fools="Expander pins cannot do anything requiring timing — no PWM, no interrupts you can time "
       "precisely, no bit-banged protocols; every access costs an I2C transaction. Output drive "
       "current is modest, so LEDs need resistors and anything more needs a transistor. The "
       "interrupt-on-change latch must be cleared by reading the port, and forgetting that gives "
       "you an interrupt line stuck low forever.",
 hazard=[], calibration="None", consumable="None",
 requires="Address strapping pins tied, not floating",
 substitutes="PCF8574 is cheaper and simpler with no interrupt sophistication; a shift register for "
             "outputs only; a bigger ESP32",
 diff=2, use="Button and switch banks, relay arrays, LED indicators, front panels, industrial "
 "input expansion.",
 spark="Sixteen reed switches on one expander with a single interrupt line means a whole house of "
       "door and window sensors on a battery node that sleeps until something actually opens.",
 pair="Reed switches, buttons, relay banks", tags=["Home", "Industry", "Access"]),

# ================================================================ TRANSLATION & ISOLATION
dict(catalog="glue", n="Bidirectional level shifter", pn="TXS0108E / BSS138 4-channel",
 cat="Industrial & Automotive", sub="Logic translation", modality="Electrical",
 phenomena=[], inferences=[],
 meas="Safely connects 5V logic to the ESP32's 3.3V pins, in both directions",
 how="A MOSFET per channel with clever biasing passes signals both ways while clamping the high "
     "side. The BSS138 style is passive and works on open-drain buses like I2C; the TXS0108E is "
     "active and faster.",
 range="4 or 8 channels", rate="BSS138 ~400kHz for I2C; TXS0108E to ~100MHz",
 iface=["Digital"], v="1.2-3.6V low side, up to 5.5V high side", logic_3v3=True, pins=0,
 esp32_compat="Necessary for 5V sensors, WS2812 data lines on long runs, and every industrial "
 "sensor whose output swings to a 12 or 24V rail (those need a divider or optocoupler instead).",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="µA", pwr_ua=10.0, usd=2.0, buy=["AF", "SF", "AE", "DK", "CE"],
 brd="Adafruit 757 (BSS138), SparkFun TXB0104, generic 8-channel TXS0108E",
 lib="None — hardware", link="", lifecycle="Active", maturity="Excellent",
 confidence="High", as_of="2026-07",
 fools="The TXS0108E has internal pull-ups and auto-direction sensing that fight open-drain buses — "
       "using it for I2C causes intermittent, maddening bus lockups, and the passive BSS138 board "
       "is the correct choice there. Both types are for LOGIC levels: a 24V industrial output needs "
       "a divider or an optocoupler, and connecting it to a level shifter destroys the shifter. "
       "Auto-direction shifters cannot drive strong loads.",
 hazard=[], calibration="None", consumable="None",
 requires="Both supply rails present; the low side powered before or with the high side",
 substitutes="A resistor divider for one-way 5V-to-3.3V; an optocoupler for isolation or higher "
             "voltages; choosing 3.3V-native sensors",
 diff=1, use="5V sensors, I2C bus mixing, WS2812 data, SD cards, legacy peripherals.",
 spark="Most 'this 5V sensor doesn't work' problems are level problems, and most people find out "
       "by destroying a GPIO first. Two dollars fixes it in advance.",
 pair="Any 5V sensor or actuator", tags=["Home", "Industry", "Play"]),

dict(catalog="glue", n="Optocoupler / digital isolator", pn="PC817 / 6N137 / ADuM1201",
 cat="Industrial & Automotive", sub="Galvanic isolation", modality="Electrical",
 phenomena=[], inferences=[],
 meas="Passes a signal across a barrier with no electrical connection at all",
 how="An LED shines onto a phototransistor across an insulating gap (or a coreless transformer does "
     "the same job magnetically in the ADuM parts). No shared ground means no ground loops and no "
     "path for a fault on one side to reach the other.",
 range="PC817 to ~10kHz; 6N137 to ~10MHz; ADuM to 150Mbps", iface=["Digital"],
 v="Both sides independent", logic_3v3=True, pins=1,
 esp32_compat="The right way to read 12V or 24V industrial outputs, and to keep motor and mains "
 "grounds away from your logic.",
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 pwr="LED current 5-20mA for the PC817", pwr_ua=10000.0, usd=1.0, buy=["AE", "DK", "MO"],
 brd="Bare DIP, 4-channel isolator modules, DIN-rail input cards", lib="None — hardware",
 link="", lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Isolation is only real if BOTH sides have genuinely separate supplies — powering both from "
       "the same rail gives you the part and none of the benefit, which is a very common and "
       "invisible mistake. The PC817's current transfer ratio varies widely between units and "
       "degrades with age, so a design at the margin works on the bench and fails in the field. "
       "Slow optocouplers smear fast edges into unusable mush.",
 hazard=[], calibration="None", consumable="LED output degrades over years",
 requires="Genuinely separate supplies on each side; a correctly sized LED current resistor",
 substitutes="ADuM digital isolators for speed and reliability; isolated DC-DC plus isolator for a "
             "fully floating front end",
 diff=3, use="Industrial 24V inputs, mains-adjacent sensing, motor control, CAN and RS-485 "
 "isolation, protecting an ESP32 from anything expensive.",
 spark="An isolated input stage is what lets you connect an ESP32 to machinery you did not design "
       "without risking either the machine or the ESP32 — the enabling part for the legacy-machine "
       "telemetry projects in this catalog.",
 pair="Any industrial sensor, any mains-adjacent circuit", tags=["Industry", "Safety", "MachineHealth"]),

# ================================================================ TIME
dict(catalog="glue", n="DS3231 precision RTC", pn="DS3231 / DS3231SN",
 cat="Industrial & Automotive", sub="Real-time clock", modality="Electrical",
 phenomena=["radio-time", "temperature-contact"], inferences=[],
 meas="Accurate timekeeping across power loss — ±2 minutes a year",
 how="A crystal oscillator with an integrated temperature sensor that continuously corrects for "
     "thermal drift, which is why it holds ±2ppm where a bare crystal drifts by minutes a month.",
 range="Year 2000-2099", accuracy="±2ppm (about ±1 minute per year) from 0-40°C",
 rate="1Hz square wave and two programmable alarms", iface=["I2C"], v="2.3-5.5V",
 logic_3v3=True, i2c_addr="0x68 (collides with MPU-6050, MPU-9250, ICM-20948)", pins=2,
 esp32_compat="The alarm output can wake the ESP32 from deep sleep, which is how you build a node "
 "that wakes at 06:00 rather than every N seconds.",
 contact="Contact", privacy="None", environment=["Indoor", "Outdoor"],
 pwr="~110µA active, 0.84µA on battery backup", pwr_ua=110.0, pwr_sleep_ua=0.84,
 usd=3.0, buy=["AE", "AF", "SF", "DK", "CE"], brd="ZS-042 modules (see the charging warning), "
 "Adafruit 3013", lib="RTClib, ESP32Time", link="https://www.analog.com/en/products/ds3231.html",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="The ubiquitous ZS-042 module includes a charging circuit intended for a rechargeable LIR2032 "
       "— fit the common non-rechargeable CR2032 that everyone fits and it is slowly charged, which "
       "can make it leak or vent. Removing one resistor disables the charger and is the standard "
       "fix. Its 0x68 address collides with almost every popular IMU, and unlike the IMU it usually "
       "cannot be moved. Backup batteries do die, and a node that silently reverts to 1 January "
       "2000 corrupts a dataset quietly.",
 hazard=[], calibration="None", consumable="Backup cell, several years",
 requires="A backup cell, and the charging resistor removed if using a non-rechargeable one",
 substitutes="NTP over Wi-Fi when always connected; GNSS PPS for precision; the ESP32's internal "
             "RTC for short sleeps only",
 diff=1, use="Data loggers, scheduled wake-ups, anything timestamped, offline nodes, alarm clocks.",
 spark="Timestamps are what turn readings into a story. Without a reliable clock, a logger's data "
       "is unmergeable with anything else — this is the three-dollar part that makes the Time "
       "theme in this catalog possible at all.",
 pair="SD logging, deep-sleep scheduling, any offline logger", tags=["Time", "Wild", "Home"]),

# ================================================================ POWER
dict(catalog="glue", n="TP4056 LiPo charger", pn="TP4056 with DW01 protection",
 cat="Power & Electrical", sub="Battery charging", modality="Electrical",
 phenomena=["current-dc"], inferences=["battery-charge"],
 meas="Single-cell lithium charging from USB, with protection",
 how="A constant-current, constant-voltage charger — full current until 4.2V, then tapering. The "
     "DW01 companion chip adds over-discharge, over-current and short-circuit protection, which is "
     "the part you must not omit.",
 range="Up to 1A, set by one resistor", accuracy="4.2V ±1.5%", iface=["Digital"],
 v="4.5-5.5V input", logic_3v3=True, pins=0,
 esp32_compat="Universal. Note the module's own quiescent draw adds to your sleep budget.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~50µA quiescent", pwr_ua=50.0, usd=1.0, buy=["AE", "AMZ", "CE"],
 brd="Micro-USB and USB-C variants — buy ONLY the version with the DW01 protection chip",
 lib="None — hardware", link="", lifecycle="Active", maturity="Excellent",
 confidence="High", as_of="2026-07",
 fools="Many cheap boards omit the protection circuit entirely and look identical — count the chips, "
       "and if there is no DW01 and dual MOSFET, do not use it with a bare cell. The default charge "
       "current is 1A, which is far too high for a small 300mAh cell and must be reset by changing "
       "the programming resistor. It has NO temperature sensing, so it will happily charge a "
       "freezing cell, which permanently damages lithium chemistry — outdoor winter nodes need a "
       "charge inhibit. Powering your load from the battery terminals while charging confuses the "
       "charge-termination logic.",
 hazard=["HighCurrent"], calibration="None", consumable="The cell itself",
 requires="A protected cell or the DW01 variant; the programming resistor matched to your cell "
          "capacity; a temperature cutoff for outdoor use",
 substitutes="MCP73871 for simultaneous load-sharing and charging; a fuel-gauge IC for real state "
             "of charge; a commercial power bank for prototypes",
 diff=2, use="Every battery-powered project in this catalog.",
 spark="Pair it with a MAX17048 fuel gauge and a node can report its own remaining days rather than "
       "a meaningless voltage — the difference between a battery reading and a battery forecast.",
 pair="MAX17048 fuel gauge, solar panel, LiPo cell", tags=["Energy", "Fleet", "Health"]),

dict(catalog="glue", n="BQ25570 energy-harvesting PMIC", pn="BQ25570",
 cat="Power & Electrical", sub="Energy harvesting", modality="Electrical",
 phenomena=["voltage"], inferences=["energy-budget-node"],
 meas="Harvests microwatts from a small solar cell, thermoelectric or piezo source and stores them",
 how="A boost converter that starts from as little as 330mV, tracks the source's maximum power "
     "point, and charges a supercapacitor or cell — plus a separate buck output for the load. It is "
     "what makes a genuinely battery-free node possible.",
 range="Cold start at 330mV, operates from 100mV", accuracy="MPPT to a programmable ratio",
 iface=["Analog"], v="0.1-5.1V input", logic_3v3=True, pins=0,
 esp32_compat="An ESP32's Wi-Fi transmit peak is enormous relative to harvested power — the design "
 "pattern is to harvest slowly into a supercapacitor and transmit rarely in short bursts.",
 contact="Contact", privacy="None", environment=["Indoor", "Outdoor"],
 pwr="488nA quiescent", pwr_ua=0.488, pwr_sleep_ua=0.488, usd=15.0, buy=["DK", "MO", "AE"],
 brd="TI EVM, Adafruit-style breakouts, e-peas alternatives", lib="None — hardware",
 link="https://www.ti.com/product/BQ25570", lifecycle="Active", maturity="Workable",
 confidence="Estimate", as_of="2026-07",
 fools="The arithmetic is unforgiving and catches everyone: an indoor solar cell may harvest a few "
       "hundred microwatts, while one Wi-Fi transmission costs hundreds of millijoules. Unless the "
       "duty cycle is extreme — one transmission per hour or less — the sums simply do not close, "
       "and no amount of clever hardware fixes it. Cold start needs the input above 330mV, so a "
       "shaded panel never starts at all. Supercapacitor leakage current can exceed your harvest.",
 hazard=[], calibration="Two-point", consumable="Supercapacitors degrade with heat and time",
 requires="A harvesting source, a supercapacitor or cell, and an honest energy budget calculated "
          "BEFORE building",
 substitutes="A larger battery and periodic charging — usually the pragmatic answer; LoRa instead "
             "of Wi-Fi to cut transmission energy by orders of magnitude",
 diff=5, use="Battery-free sensors, indoor solar nodes, thermoelectric harvesting, "
 "vibration-powered industrial monitors.",
 spark="Use the Power Budget sheet in this workbook before buying anything: it will tell you within "
       "a minute whether your harvesting idea closes, and it usually will not with Wi-Fi.",
 pair="Small solar cells, supercapacitors, ESP32-C3 with aggressive deep sleep, LoRa", tags=["Energy", "Wild", "Fleet"]),

dict(catalog="glue", n="Buck / boost converter modules", pn="MP1584 buck / MT3608 boost / TPS63020 buck-boost",
 cat="Power & Electrical", sub="Voltage conversion", modality="Electrical",
 phenomena=[], inferences=[],
 meas="Efficient conversion between supply voltages",
 how="A switching regulator stores energy in an inductor and releases it at a different voltage. "
     "Unlike a linear regulator it does not burn the difference as heat, which matters when "
     "dropping 12V to 3.3V.",
 range="Wide; typically 3-40V in, 1-35V out", accuracy="±2-3% typical",
 iface=["Analog"], v="Module dependent", logic_3v3=True, pins=0,
 esp32_compat="A buck-boost is the right choice for LiPo-powered nodes: a cell spans 4.2V down to "
 "3.0V, crossing 3.3V, so a plain buck browns out as the battery drains.",
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 pwr="Quiescent from µA (TPS63020) to mA (cheap modules)", pwr_ua=50.0, usd=2.0,
 buy=["AE", "AMZ", "DK"], brd="MP1584 mini buck, MT3608 boost, Pololu buck-boost regulators",
 lib="None — hardware", link="", lifecycle="Active", maturity="Excellent",
 confidence="High", as_of="2026-07",
 fools="Switching regulators inject noise at their switching frequency straight into any analog "
       "sensor sharing the rail — this is a very common and very confusing source of ADC noise, and "
       "the fix is a separate linear regulator for the analog section. Cheap modules have "
       "milliamp-class quiescent current that dwarfs a sleeping ESP32, so the regulator becomes the "
       "dominant load on a battery node. A plain buck cannot maintain 3.3V once a LiPo falls below "
       "3.3V, so the last third of the battery is unusable.",
 hazard=["HighCurrent"], calibration="One-point", consumable="Electrolytic capacitors age",
 requires="Output voltage set and VERIFIED before connecting anything — adjustable modules arrive "
          "at arbitrary settings and have destroyed a great many boards",
 substitutes="An LDO for low-noise analog rails; a buck-boost for battery operation; direct 3.3V "
             "supply where possible",
 diff=2, use="Powering 3.3V logic from 12V or 24V, boosting a single cell, running mixed-voltage "
 "systems, solar and battery power paths.",
 spark="Measure the quiescent current of your regulator before designing a sleeping node — it is "
       "very often larger than everything else on the board combined, and it is invisible until "
       "you look.",
 pair="INA219 to measure what the converter actually costs you", tags=["Energy", "Fleet", "Industry"]),

dict(catalog="glue", n="Supercapacitor + balancing", pn="2.7V 1-10F supercaps with balancing board",
 cat="Power & Electrical", sub="Energy storage", modality="Electrical",
 phenomena=[], inferences=["energy-budget-node"],
 meas="Fast-charging energy storage that survives hundreds of thousands of cycles",
 how="Stores charge electrostatically rather than chemically. That means it charges in seconds, "
     "works at temperatures that destroy lithium cells, and lasts effectively forever — at perhaps "
     "a fiftieth of the energy density.",
 range="1-100F at 2.7V per cell", rate="Charges in seconds", iface=["Analog"],
 v="2.7V per cell; series stacks need balancing", logic_3v3=True, pins=0,
 esp32_compat="Excellent for ride-through — keeping an ESP32 alive long enough to save state and "
 "shut down cleanly when power is cut.",
 contact="Contact", privacy="None", environment=["Indoor", "Outdoor", "Harsh"],
 pwr="Leakage typically tens of µA, rising with age and temperature", pwr_ua=30.0,
 usd=5.0, buy=["AE", "DK", "MO"], brd="Bare supercaps, balancing boards for series stacks",
 lib="None — hardware", link="", lifecycle="Active", maturity="Good",
 confidence="High", as_of="2026-07",
 fools="Voltage falls linearly as it discharges rather than sitting on a plateau like a battery, so "
       "you need a buck-boost to get usable power out of most of the stored energy. Leakage current "
       "is significant and grows with age — for very-low-power harvesting it can exceed what you "
       "collect. Series cells MUST be balanced or one takes more than its share and fails. Energy "
       "density is far below lithium: a 10F supercap holds a small fraction of a tiny LiPo.",
 hazard=["HighCurrent"], calibration="None", consumable="Capacitance falls and leakage rises over "
 "years, faster when hot",
 requires="A balancing circuit for series stacks; a buck-boost to use the full discharge curve; "
          "inrush limiting, because an empty supercap looks like a short circuit",
 substitutes="LiPo for energy density; a hybrid supercap-plus-cell for both burst and endurance",
 diff=3, use="Power-loss ride-through, burst transmission from harvested energy, cold-climate "
 "nodes where lithium fails, high-cycle applications.",
 spark="A supercapacitor sized for exactly one Wi-Fi transmission lets a harvested node behave like "
       "a mains one for the half-second that matters, then go back to sipping microwatts.",
 pair="BQ25570 harvester, buck-boost converter, ESP32 with deep sleep", tags=["Energy", "Wild", "Fleet"]),

dict(catalog="glue", n="Precision voltage reference", pn="REF3033 / LM4040 / ADR4525",
 cat="Power & Electrical", sub="Measurement reference", modality="Electrical",
 phenomena=["voltage"], inferences=[],
 meas="A stable, known voltage that everything else can be measured against",
 how="A bandgap circuit trimmed and compensated to hold its output within a few parts per million "
     "per degree. Every ratiometric measurement is only as good as its reference.",
 range="Common values 2.5V, 3.0V, 4.096V", accuracy="0.05-0.2% initial, 3-25ppm/°C drift",
 iface=["Analog"], v="Input above the output plus dropout", logic_3v3=True, pins=0,
 esp32_compat="The ESP32's internal ADC reference is neither accurate nor stable, which is a large "
 "part of why its readings are poor. An external reference plus an external ADC fixes both.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~50-100µA", pwr_ua=75.0, usd=3.0, buy=["DK", "MO", "AE"],
 brd="Bare SOT-23, or on precision ADC modules", lib="None — hardware",
 link="", lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="A measurement referenced to a noisy or drifting supply inherits every wobble of that supply "
       "— which is why the same sensor reads differently on USB power and on battery, and why "
       "readings drift as a room warms. A reference needs its recommended output capacitor or it "
       "can oscillate. Self-heating from a load on the reference itself causes slow drift.",
 hazard=[], calibration="None", consumable="Long-term ageing of a few ppm per year",
 requires="The specified decoupling capacitor; a buffer if anything draws current from it",
 substitutes="Ratiometric measurement (comparing against the same supply that excites the sensor), "
             "which cancels supply variation without needing a reference at all",
 diff=3, use="Precision ADC work, calibration rigs, long-term logging where drift matters, "
 "reference measurements for characterising cheaper sensors.",
 spark="A stable reference is what lets you build the 'sensor truth machine' — a rig that measures "
       "how wrong your cheap sensors actually are, which is worth more than any single sensor.",
 pair="ADS1115 or ADS1256, precision resistors", tags=["MachineHealth", "Industry", "Invisible"]),

dict(catalog="glue", n="Input protection (TVS, PTC, series R)", pn="SMAJ5.0A TVS / PTC resettable fuse / Schottky clamps",
 cat="Power & Electrical", sub="Protection", modality="Electrical",
 phenomena=[], inferences=[],
 meas="Keeps a surge, a reversed supply or a wrong voltage from destroying everything downstream",
 how="A TVS diode conducts hard above its breakdown voltage, shunting a surge away from your "
     "circuit. A resettable PTC fuse rises sharply in resistance when it heats, limiting fault "
     "current and then recovering. A series resistor limits how much current any mistake can deliver.",
 range="Chosen per rail", iface=["Analog"], v="Rail dependent", logic_3v3=True, pins=0,
 esp32_compat="Any long cable run into an ESP32 GPIO — a soil probe, a doorbell wire, an outdoor "
 "sensor — deserves protection; those wires collect surges.",
 contact="Contact", privacy="None", environment=["Outdoor", "Harsh"],
 pwr="Negligible", pwr_ua=1.0, usd=1.0, buy=["DK", "MO", "AE"],
 brd="Discrete components; some breakouts include protection", lib="None — hardware",
 link="", lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Protection sized wrong is protection that does not work: a TVS with a standoff voltage "
       "below your normal operating voltage conducts continuously and gets hot, while one rated too "
       "high never clamps in time. PTC fuses trip slowly, so they protect against sustained faults "
       "rather than fast transients. None of this substitutes for correct wiring — it buys you a "
       "second chance, not immunity.",
 hazard=[], calibration="None", consumable="PTC fuses degrade slightly with each trip",
 requires="Standoff voltage chosen above the working voltage and below the damage threshold",
 substitutes="Optocoupler isolation, which prevents the fault from reaching you at all",
 diff=3, use="Outdoor sensors, long cable runs, automotive and industrial inputs, anything "
 "connected to a system you did not design.",
 spark="The cheapest insurance in electronics. A few pence per input is the difference between one "
       "lightning-adjacent surge costing you a diode and it costing you the whole node.",
 pair="Every outdoor or long-cable sensor in this catalog", tags=["Safety", "Wild", "Industry"]),
]
