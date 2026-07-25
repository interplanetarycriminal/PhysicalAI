#!/usr/bin/env python3
"""Phase 0 — correctness, safety and provenance fixes to the v5 sensor data.

Every fix asserts its target text was found EXACTLY once, so a silent no-op is
impossible. Run once; it is idempotent-checked by the assertions (re-running
after success will fail loudly, which is the intended signal).

Sources for each correction are recorded in CORRECTIONS[].why so the changelog
sheet can cite them.
"""
import sys
from pathlib import Path

DATA = Path(__file__).parent / "data"

# (file, old, new, why)
CORRECTIONS = [
# ---------------------------------------------------------------- SAFETY (highest severity)
("part5_sound_force_touch.py",
 'iface="Digital", v="5-24V (logic-safe out)", usd=7, diff=1, pwr="5mA",\n spec="Through-wall, no fluid contact, IP67", buy="AE,DFR,AMZ",',
 'iface="Digital (open-collector, pull-up to YOUR logic rail)", v="5-24V", usd=7, diff=1, pwr="5mA",\n spec="Through-wall, no fluid contact, IP67. ⚠ OUTPUT SWINGS TO VCC — at 12/24V it will destroy an ESP32 GPIO. Run the sensor at 5V and level-shift, or use a divider/optocoupler.", buy="AE,DFR,AMZ",',
 "v5 claimed 'logic-safe out'. The XKC-Y25 output follows VCC; wiring it at 12-24V per that claim destroys the ESP32."),

("part8_gps_thermal_camera_rf.py",
 ' use="Electrolysis experiments, battery-room monitoring (H2 from charging!), hydrogen projects.",\n spark="Off-grid battery rooms outgas hydrogen when overcharged — a $4 sensor + vent fan interlock prevents the classic battery-shed explosion.",',
 ' use="Electrolysis demonstrations and hydrogen experiments in OPEN, well-ventilated benches. NOT for deployment inside a battery room, gas locker or any space where hydrogen can accumulate.",\n spark="The instructive build is a ventilated test bench that shows how fast H2 accumulates above a charging lead-acid cell — the data is the point. For an actual battery room you need a certified, intrinsically-safe H2 detector: an MQ bead runs at ~300°C and is itself an ignition source.",',
 "v5 recommended installing a heated MQ bead inside a hydrogen-accumulating battery room and called it explosion prevention. An MQ element is a candidate ignition source in that atmosphere."),

("part9_classics_and_gaps.py",
 ' use="Caravan/boat gas lockers, BBQ bottle storage, garage propane.",\n spark="A gas-locker logger proving your slow leak: weekly ppm baseline creep catches the failing regulator a sniff test misses.",',
 ' use="Monitoring the ventilated SPACE OUTSIDE an LPG locker (low down — propane sinks), garage and plant-room air. Never inside the locker itself.",\n spark="Mount it low in the room outside the bottle store: baseline ppm creep over weeks catches a failing regulator a sniff test misses — without putting a 300°C heater inside the explosive volume.",',
 "v5 recommended an MQ-6 inside caravan/boat gas lockers — a heated element inside an LPG volume."),

# uniform life-safety disclaimer across the MQ family (MQ-7 already had one)
("part2_air_gas.py",
 'spec="200-10000ppm class detection, potentiometer threshold", buy="AE,AMZ,DFR,CE",',
 'spec="200-10000ppm class detection, potentiometer threshold. ⚠ NOT a life-safety device — supplement, never replace, a certified alarm. Heated element: keep out of explosive atmospheres.", buy="AE,AMZ,DFR,CE",',
 "MQ-2 made life-safety claims with no disclaimer while MQ-7 carried one. Now uniform."),

("part2_air_gas.py",
 'spec="Qualitative; often mislabeled as CO2 sensor (it isn\'t)", buy="AE,AMZ,DFR",',
 'spec="Qualitative; often mislabeled as a CO2 sensor (it is not). ⚠ NOT a life-safety device. Heated element: keep out of explosive atmospheres.", buy="AE,AMZ,DFR",',
 "Uniform MQ safety framing."),

("part9_classics_and_gaps.py",
 'spec="Qualitative; calibrate against known source for trends", buy="AE,AMZ,DFR",',
 'spec="Qualitative; calibrate against a known source for trends. ⚠ NOT a life-safety device — supplement, never replace, a certified alarm. Heated element: keep out of explosive atmospheres.", buy="AE,AMZ,DFR",',
 "MQ-4 claimed to be 'the difference between incident and anecdote' with no disclaimer."),

("part9_classics_and_gaps.py",
 'spec="Mount near floor level for LPG!", buy="AE,AMZ,DFR",',
 'spec="Mount near floor level — LPG is heavier than air and pools low. ⚠ NOT a life-safety device. Heated element: keep out of explosive atmospheres (see Uses).", buy="AE,AMZ,DFR",',
 "Uniform MQ safety framing."),

# ---------------------------------------------------------------- HARD FACTUAL ERRORS
("part3_light_distance.py",
 'spec="~10kΩ dark to ~1kΩ bright; CdS banned in some products (RoHS)"',
 'spec="~0.5-2MΩ in darkness, ~8-20kΩ at 10 lux, ~1kΩ in bright sun; pick the divider resistor for YOUR light range. CdS is RoHS-restricted in commercial products"',
 "v5 stated 10k-dark/1k-bright — wrong by ~2 orders of magnitude, which produces the wrong divider resistor."),

("part3_light_distance.py",
 'how="Times photons from an invisible 940nm laser pulse to target and back — measures actual flight time of light, immune to target color, in a chip the size of a grain of rice.",',
 'how="Times photons from an invisible 940nm laser pulse to the target and back — it measures the actual flight time of light, in a chip the size of a grain of rice. Range depends strongly on target reflectivity (ST quotes ~2m on a white target but ~0.8m on dark grey).",',
 "v5 claimed ToF is 'immune to target color'. Reflectivity is the dominant range/accuracy variable per ST's datasheet."),

("part1_temp_humidity_pressure.py",
 'meas="0-25 PSI gauge pressure via a physical port you can tube", how="A silicone-gel-protected MEMS die behind a barbed port — you push a tube on it, so it can measure squeeze bulbs, water columns, vacuum chambers and lungs.",',
 'meas="0-25 PSI ABSOLUTE pressure via a physical port you can tube", how="A silicone-gel-protected MEMS die behind a barbed port — you push a tube on it, so it can measure squeeze bulbs, water columns, vacuum chambers and lungs. It reads ABSOLUTE pressure (~14.7 PSI sitting on the bench), so for every gauge measurement you must subtract atmospheric — either by maths or with a second sensor open to air.",',
 "MPRLS0025PA is an absolute sensor; v5 called it gauge, which breaks every listed use case."),

("part1_temp_humidity_pressure.py",
 'pn="NTC 10k B3950 / 104GT"',
 'pn="NTC 10k B3950 (e.g. NTCLE100E3103 / generic 3950 bead)"',
 "The Semitec 104GT-2 is a 100k thermistor, not 10k — wrong divider and wrong Steinhart coefficients."),

("part3_light_distance.py",
 'how="Two photodiodes — one filtered to UV-A — give a real UV index, the same number weather apps publish, plus lux from the same chip.",',
 'how="Two photodiodes — one filtered to UV-A — give a UV-A irradiance count plus lux from the same chip. Note: the library\'s \'UV index\' is an APPROXIMATION. True UVI is erythemally weighted and dominated by UV-B, which this part cannot see. Excellent for relative dose tracking; not a substitute for a UVI instrument.",',
 "v5 claimed the LTR-390 gives 'a real UV index, the same number weather apps publish'. It has a single UV-A channel; UVI is UV-B weighted."),

("part8_gps_thermal_camera_rf.py",
 'dict(n="Soil tensiometer (real suction)", pn="Watermark 200SS + adapter", cat="Specialty & Exotic", sub="Plant-available water",\n meas="Soil water TENSION (what roots actually feel)", how="A gypsum-buffered granular matrix changes resistance with soil suction — measures how hard plants must work for water, the irrigation pro\'s metric.",',
 'dict(n="Watermark granular-matrix soil water sensor", pn="Watermark 200SS + adapter", cat="Soil & Agriculture", sub="Plant-available water",\n meas="Soil water tension / matric potential (what roots actually feel), 0-239 kPa", how="A gypsum-buffered granular matrix inside a porous shell equilibrates with the soil; its electrical resistance tracks soil suction. Strictly it is a granular-matrix resistance sensor, not a tensiometer (a true tensiometer is a water-filled tube with a pressure transducer — see the MPRLS entry), but it reports the same quantity irrigation professionals schedule on.",',
 "Mislabelled as a tensiometer, and filed in the Specialty junk drawer rather than Soil & Agriculture."),

("part10_industrial_exotic.py",
 'dict(n="Doppler ultrasonic flow (clamp-on)", pn="TUF-2000M + ESP32 Modbus", cat="Frontier Sensing", sub="Non-invasive flow",',
 'dict(n="Transit-time ultrasonic flow (clamp-on)", pn="TUF-2000M + ESP32 Modbus", cat="Water & Liquid", sub="Non-invasive flow",',
 "Named Doppler while its own description correctly describes transit-time measurement."),

("part8_gps_thermal_camera_rf.py",
 'dict(n="MEMS hydrogen sensor", pn="MQ-8 / DFRobot SEN0570", cat="Specialty & Exotic", sub="H2 (future fuel)",\n meas="Hydrogen gas 100-10000ppm", how="Doped MOX selective toward H2 — as hydrogen heating/vehicles arrive, leak sensing at the maker level arrives with it.",',
 'dict(n="MQ-8 hydrogen sensor", pn="MQ-8 (heated SnO2) / DFRobot SEN0570 (MEMS)", cat="Gas & VOC", sub="MQ analog (heated)",\n meas="Hydrogen gas 100-10000ppm (qualitative)", how="A tin-oxide bead heated to ~300°C whose resistance drops in hydrogen. It is NOT MEMS and NOT selective — it responds strongly to alcohol and CO too, so treat it as a trend instrument, never as an identification.",',
 "v5 called the MQ-8 a MEMS sensor and claimed selectivity; it is a heated SnO2 bead with heavy cross-sensitivity."),

("part10_industrial_exotic.py",
 'dict(n="O2 sensor (automotive narrowband)", pn="LSU/HEGO + ADC", cat="Industrial Sensing", sub="Combustion O2",\n meas="Exhaust oxygen (rich/lean) — combustion quality", how="A zirconia cell generates voltage from the oxygen differential between exhaust and air — the sensor that closed-loop fuel injection is built on.",\n iface="Analog (0-1V)", v="heater 12V", usd=15, diff=4, pwr="heater ~1A!",\n spec="Narrowband: rich/lean switch around stoich", buy="AMZ,AE,DK",\n brd="Bosch universal + ADS1115", lib="ADC + interpretation",',
 'dict(n="Narrowband O2 sensor (HEGO)", pn="Bosch/NTK universal HEGO (1-4 wire)", cat="Industrial Sensing", sub="Combustion O2",\n meas="Exhaust oxygen as a rich/lean switch around stoichiometric", how="A zirconia cell generates a voltage from the oxygen differential between exhaust and outside air — the sensor closed-loop fuel injection is built on. A NARROWBAND (HEGO) cell only tells you which side of stoichiometric you are on; it is not a linear O2 reading. Wideband LSU sensors look similar but are pump-cell devices that CANNOT be read with a plain ADC — they need a dedicated controller (Bosch CJ125 or equivalent).",\n iface="Analog 0-1V (narrowband only)", v="sensor cell passive; heater 12V", usd=15, diff=4, pwr="heater 1-2A @12V ⚠ separate supply, not from the ESP32 rail",\n spec="Narrowband switch ~0.45V at stoich. For a linear reading you need an LSU + CJ125 controller board (~$60+), not this.", buy="AMZ,AE,DK",\n brd="Bosch universal HEGO + ADS1115; for wideband use an LSU4.9 + CJ125 module", lib="ADC + interpretation",',
 "v5 merged narrowband HEGO and wideband LSU under one analog interface, implying an LSU can be read on an ADS1115. It cannot."),

("part8_gps_thermal_camera_rf.py",
 'dict(n="SEN0395 / mmWave 60GHz sleep radar", pn="DFRobot SEN0395/0623", cat="Specialty & Exotic", sub="Advanced radar",',
 'dict(n="DFRobot Gravity mmWave presence radar", pn="DFRobot SEN0395 (24GHz) / SEN0623 (60GHz)", cat="Presence & Occupancy", sub="mmWave radar",',
 "SEN0395 is a 24GHz part; v5's title said 60GHz. Also moved out of the Specialty junk drawer."),

("part1_temp_humidity_pressure.py",
 'meas="Air pressure + temp, ±2cm relative altitude class"',
 'meas="Air pressure + temp; ~±5cm relative altitude in low-noise modes"',
 "v5 stated ±2cm in meas and ±5cm in spec — two different numbers for the same quantity in one record."),

("part2_air_gas.py",
 'how="Three metal-oxide channels plus an on-chip algorithm that outputs ready-made air-quality numbers — no host-side blob library needed, unlike Bosch BSEC.",',
 'how="A four-hotplate metal-oxide array plus an on-chip algorithm that outputs ready-made air-quality numbers — no host-side blob library needed, unlike Bosch BSEC.",',
 "ScioSense specifies four hotplates, not three."),

("part2_air_gas.py",
 'dict(n="MH-Z19 style CH4 / propane NDIR", pn="MH-440D / MH-741A", cat="Gas & VOC", sub="NDIR (optical)",',
 'dict(n="NDIR methane / hydrocarbon module", pn="Winsen MH-741A / Cubic SJH-5 (CH4 NDIR)", cat="Gas & VOC", sub="NDIR (optical)",',
 "MH-440D is an NDIR CO2 module; naming a methane sensor after the MH-Z19 (also CO2) compounded the confusion."),

("part8_gps_thermal_camera_rf.py",
 'dict(n="AS7331+photodiode flame/UV-C", pn="Flame sensor 5ch / IR flame", cat="Specialty & Exotic", sub="Flame detection",\n meas="Open-flame presence via its UV/IR flicker signature", how="Flames emit characteristic UV and flickering IR (~10Hz); tuned photodiodes catch that signature far faster than smoke can reach a ceiling detector.",',
 'dict(n="IR flame detector (flicker)", pn="KY-026 / 5-channel IR flame array", cat="Light & UV", sub="Flame detection",\n meas="Open-flame presence via near-IR flicker (~1-10Hz)", how="A near-IR phototransistor (roughly 760-1100nm) watching for the characteristic flicker of a flame — faster than waiting for smoke to reach a ceiling detector. NOTE: these cheap modules are IR-only and are blind to the UV that true UV flame detectors use; sunlight, incandescent bulbs and hot surfaces will fool them.",',
 "v5's title named the AS7331 (a UV spectral sensor with its own entry) while describing a KY-026 IR module, and claimed UV sensitivity the part does not have."),

("part6_bio_weather_soil.py",
 'dict(n="Fingerprint reader R503", pn="R503 / GT-521F52", cat="Biometric & Health", sub="Identification",\n meas="Fingerprint enrolment + 1:N matching onboard", how="A capacitive imaging window with a processor that stores templates and does the matching — your ESP32 just hears \'finger #3 matched\' over UART.",',
 'dict(n="Fingerprint reader R503", pn="R503 (optical, round)", cat="RFID & NFC", sub="Biometric identification",\n meas="Fingerprint enrolment + 1:N matching onboard", how="An OPTICAL imaging window with a processor that stores templates and does the matching on-module — your ESP32 just hears \'finger #3 matched\' over UART. (Capacitive readers such as the GT-521F52 family work differently and are not interchangeable.)",',
 "R503 is optical, not capacitive; v5 also merged it with a different-technology part and filed identity tech under Biometric & Health."),

("part7_water_power_position.py",
 'iface="Pulse (PCNT)", v="5-18V (divider for echo)", usd=5, diff=1, pwr="15mA",',
 'iface="Pulse (PCNT)", v="5-18V supply; pulse output needs a divider or level shift to 3.3V", usd=5, diff=1, pwr="15mA",',
 "'divider for echo' was a copy-paste artifact from an ultrasonic distance entry."),

("part9_classics_and_gaps.py",
 ' spark="Quantify your sunglasses/window tint: side-by-side SI1145s prove what percentage of UV actually gets blocked.",',
 ' spark="Good for relative daylight/proximity work. Do NOT use it to certify UV blocking of sunglasses or window film — it infers UVI from visible+IR rather than measuring UV, so a tint that changes visible transmission will move the reading without telling you anything about UV. Use an AS7331 for that.",',
 "v5's own spec admitted the SI1145 infers UVI, then proposed a UV-transmission measurement it cannot make."),

("part4_presence_motion_magnetic.py",
 ' brd="Adafruit 5417, EVAL-ADXL355", lib="Adafruit_ADXL355",',
 ' brd="EVAL-ADXL355Z (Analog Devices), Sparkfun/3rd-party ADXL355 boards, CJMCU-355", lib="plasmapper/adxl355-arduino or a datasheet SPI driver (no Adafruit library exists)",',
 "VERIFIED FABRICATION: Adafruit product 5417 is a MicroPython Pyboard Lite, not an ADXL355 breakout, and no Adafruit_ADXL355 library exists."),

# ---------------------------------------------------------------- MISLEADING / OVERSTATED
("part2_air_gas.py",
 'how="Micro-machined hotplate version of the MQ concept — milliwatts instead of nearly a watt, so it actually works on batteries.",',
 'how="A micro-machined hotplate version of the MQ concept — the heater burns milliwatts instead of nearly a watt, and it warms up in seconds rather than minutes. Still ~32mA while on, so it needs duty-cycling (not continuous operation) to be viable on a battery.",',
 "v5 said 'actually works on batteries' while its own pwr field said 32mA continuous."),

("part2_air_gas.py",
 'iface="I2C", v="2.4-5.5V", usd=25, diff=1, pwr="0.5mA @ 1 meas/5min single-shot",\n spec="±(40ppm+5%), tiny footprint, low-power single-shot mode", buy="AF,SF,DK,MO,PI",',
 'iface="I2C", v="2.4-5.5V", usd=25, diff=1, pwr="0.5mA @ 1 meas/5min single-shot (~205mA peak during a measurement)",\n spec="±(40ppm+5%), tiny footprint, low-power single-shot mode. Set the ambient-pressure or altitude register — uncompensated readings drift with weather and are badly wrong above ~500m. SCD40 tops out at 2000ppm; SCD41 reaches 5000ppm.", buy="AF,SF,DK,MO,PI",',
 "No CO2 entry mentioned ambient-pressure compensation despite altitude and greenhouse builds; SCD40/41 ranges differ but shared one field."),

("part2_air_gas.py", 'sub="Photoacoustic NDIR"', 'sub="Photoacoustic"',
 "Photoacoustic and NDIR are different measurement principles; the SCD4x is photoacoustic."),

("part2_air_gas.py",
 'spec="±10% accuracy band, fan auto-clean, MCERTS-adjacent quality", buy="DK,MO,SS",',
 'spec="±10% accuracy band, fan auto-clean, 10yr lifetime spec. NOT MCERTS certified. Like all optical PM sensors it over-reads in high humidity (hygroscopic particle growth above ~75% RH) — log RH alongside and correct.", buy="DK,MO,SS",',
 "'MCERTS-adjacent quality' was marketing, not a spec; and no PM entry mentioned the humidity artifact."),

("part2_air_gas.py",
 'spec="0-500µg/m³, 6 size bins; PMSA003I is the I2C/STEMMA version", buy="AF,AE,DK,SS",',
 'spec="0-500µg/m³, 6 size bins; PMSA003I is the I2C/STEMMA version. Over-reads in humid air (particles swell above ~75% RH) — pair with an RH sensor and correct, or your wildfire numbers will also spike in fog.", buy="AF,AE,DK,SS",',
 "Humidity artifact affects every outdoor PM build and was unmentioned."),

("part6_bio_weather_soil.py",
 ' spark="Camera deadman: AS3935 interrupt fires a DSLR trigger within microseconds — catch the NEXT strike in the same storm cell automatically.",',
 ' spark="Storm-approach dashboard: log strike rate and estimated distance to watch a cell close in, and drive a pool/sports-field evacuation siren. (For lightning PHOTOGRAPHY the AS3935 is too slow — its interrupt arrives milliseconds after event validation; dedicated optical triggers are what photographers use.) Budget real time for antenna tuning and noise-floor calibration: false triggers from switching supplies and fluorescent lights are the #1 thing that ruins these builds.",',
 "v5 claimed microsecond DSLR triggering (it is milliseconds, post-validation) and never mentioned the notorious false-trigger problem."),

("part8_gps_thermal_camera_rf.py",
 'spec="±50ns class PPS jitter on hobby modules", buy="AE,SF,DK",',
 'spec="The PPS EDGE itself is ~±50ns on hobby modules — but an ESP32 GPIO interrupt timestamp adds microseconds of latency and jitter, so end-to-end you should expect µs-class sync, not ns. Good enough for TDOA over hundreds of metres; not for ns metrology.", buy="AE,SF,DK",',
 "v5 presented ~50ns as an achievable end-to-end timing figure for an ESP32."),

("part10_industrial_exotic.py",
 'spec="hallRead() classic only; RSSI per-packet free", buy="—",',
 'spec="⚠ Reality check: the internal hall sensor was REMOVED in ESP-IDF v5 / Arduino core 3.x and is unavailable on newer chips; the internal temperature sensor reads self-heated die temperature and is near-useless as an ambient reading; RSSI is a link metric, not a calibrated sensor. Touch is the one genuinely useful freebie (classic/S2/S3 only — C3/C6/H2 have no touch peripheral).", buy="—",',
 "v5 sold 'four sensors for $0'; three of the four are removed, unusable, or not a sensor."),

("part8_gps_thermal_camera_rf.py",
 ' spark="A cat-only cat door: HuskyLens face-recognises YOUR cat (and rejects the neighbour\'s) before the latch servo opens — the demo that explains edge AI to anyone.",',
 ' spark="A pet-aware door: HuskyLens\' object-tracking and tag-recognition modes reliably distinguish a tagged collar or a learned object; its FACE recognition is trained on human faces, so cat-face ID needs a custom model (Grove Vision AI V2) rather than the built-in mode. The honest build is tag-plus-shape, and it still explains edge AI to anyone.",',
 "HuskyLens face recognition is human-face trained; v5 promised cat-face recognition in two places."),

("part5_sound_force_touch.py",
 'spec="Sensitive to taps/flex; needs protection diodes for ESP32 ADC", buy="AE,AMZ,SF,CE",',
 'spec="Sensitive to taps/flex. ⚠ A struck piezo can generate tens of volts — you MUST clamp it (two diodes to 3.3V/GND) plus a ~1MΩ bleed resistor before it touches an ESP32 ADC pin.", buy="AE,AMZ,SF,CE",',
 "The clamping requirement was noted but understated for a part that can output tens of volts."),

# ---------------------------------------------------------------- HYGIENE
("part1_temp_humidity_pressure.py", ' spec_note="", spark=', ' spark=',
 "Stray schema key present on exactly one record and never read by the builder."),
]


def main():
    changed = {}
    for fname, old, new, why in CORRECTIONS:
        path = DATA / fname
        text = changed.get(fname) or path.read_text()
        n = text.count(old)
        if n != 1:
            print(f"✗ FAIL [{fname}] expected 1 match, found {n}\n   why: {why}\n   text: {old[:110]!r}")
            sys.exit(1)
        changed[fname] = text.replace(old, new)
    for fname, text in changed.items():
        (DATA / fname).write_text(text)
    print(f"✓ applied {len(CORRECTIONS)} corrections across {len(changed)} files")


if __name__ == "__main__":
    main()
