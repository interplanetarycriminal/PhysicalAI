#!/usr/bin/env python3
"""Price and provenance corrections.

The review found prices that were wrong by 2x or more, and single `usd` figures
covering merged products with a 4x spread. Each fix asserts an exact single match.

VERIFIED = fetched from the vendor page during this pass (2026-07).
ESTIMATE = corrected by reasoning from the review; flagged so the reader knows.
"""
import sys
from pathlib import Path

DATA = Path(__file__).parent / "data"

FIXES = [
# ---- verified against vendor pages this pass
("part3_light_distance.py",
 'iface="I2C", v="2.7-3.6V", usd=14, diff=2, pwr="<1mA",\n spec="Irradiance in µW/cm² per band", buy="SF,DK,MO",',
 'iface="I2C", v="2.7-3.6V", usd=27.5, diff=2, pwr="<1mA",\n spec="Irradiance in µW/cm² per band. Genuinely separates UV-C from sunlight UV, which nothing cheaper does.", buy="SF,DK,MO",',
 "VERIFIED 2026-07: SparkFun lists the AS7331 Qwiic board at $27.50; v5 said $14."),

("part8_gps_thermal_camera_rf.py",
 'iface="UART/I2C/SPI/USB", v="3.3-5V", usd=190, diff=4, pwr="130mA",',
 'iface="UART/I2C/SPI/USB", v="3.3-5V", usd=260, diff=4, pwr="130mA",',
 "VERIFIED 2026-07: SparkFun GPS-RTK2 (ZED-F9P) is $259.95; v5 said $190. Note a full "
 "RTK setup needs a base as well as a rover, so budget roughly double."),

# ---- merged products split apart or re-scoped
("part6_bio_weather_soil.py",
 'dict(n="Pyranometer (solar irradiance)", pn="DFRobot SEN0562 / Apogee SP-110", cat="Weather & Outdoor", sub="Solar energy",',
 'dict(n="Pyranometer (solar irradiance)", pn="DFRobot SEN0562 (Gravity)", cat="Weather & Outdoor", sub="Solar energy",',
 "v5 priced a ~$60 DFRobot module and a ~$225 Apogee research instrument under one usd figure."),

("part6_bio_weather_soil.py",
 'brd="DFRobot Gravity, Apogee (research-grade)", lib="analogRead/Modbus",',
 'brd="DFRobot Gravity SEN0562. Step up: Apogee SP-110 (~$225) or SP-510 for research-grade work — same measurement, an order of magnitude better traceability.", lib="analogRead/Modbus",',
 "Research-grade option kept as an explicit upgrade path rather than hidden in a merged price."),

("part7_water_power_position.py",
 'spec="±0.1pH calibrated; probes age (~1yr), keep wet", buy="DFR,AE,AMZ,AT",',
 'spec="±0.1pH once calibrated. The glass electrode is a consumable — roughly 12-18 months, and it must never dry out. Two-point calibration with buffer sachets is mandatory, not optional.", buy="DFR,AE,AMZ",',
 "v5 listed Atlas Scientific as a vendor against a $30 price; the Atlas pH kit is ~$150+. "
 "Atlas is now referenced as the lab-grade tier in `substitutes` instead."),

("part7_water_power_position.py",
 'dict(n="Dissolved oxygen kit", pn="Atlas EZO-DO / DFRobot SEN0237", cat="Water & Liquid", sub="Water chemistry",',
 'dict(n="Dissolved oxygen kit (Atlas EZO-DO)", pn="Atlas Scientific EZO-DO + probe", cat="Water & Liquid", sub="Water chemistry",',
 "v5 merged a DFRobot analog kit and the Atlas EZO stack under one price despite a large spread."),

# ---- prices the review flagged as implausibly low; corrected and marked
("part8_gps_thermal_camera_rf.py",
 'iface="I2C", v="3.3V", usd=30, diff=2, pwr="18mA",',
 'iface="I2C", v="3.3V", usd=60, diff=2, pwr="18mA",',
 "ESTIMATE: SparkFun's MLX90641 board is ~$60, not the $30 v5 listed."),

("part8_gps_thermal_camera_rf.py",
 'iface="I2C", v="4.5-5.5V", usd=25, diff=2, pwr="5mA",\n spec="4x4, ±1.5°C, human-detection app notes", buy="DK,MO,SS",',
 'iface="I2C", v="4.5-5.5V", usd=55, diff=2, pwr="5mA",\n spec="4x4, ±1.5°C, with Omron application notes specifically for distinguishing humans from warm backgrounds", buy="DK,MO,SS",',
 "ESTIMATE: the Omron D6T-44L is ~$50-70 at distributors, not $25."),

("part2_air_gas.py",
 'iface="Analog (needs AFE) or UART modules", v="3.3V AFE", usd=35, diff=4, pwr="µA cell, mA AFE",',
 'iface="Analog (needs AFE) or UART modules", v="3.3V AFE", usd=80, diff=4, pwr="µA cell, mA AFE",',
 "ESTIMATE: SPEC DGS UART modules are ~$70-90; v5's $35 was closer to a bare cell."),

("part9_classics_and_gaps.py",
 'iface="Analog", v="5V", usd=8, diff=3, pwr="150mA",',
 'iface="Analog", v="5V", usd=30, diff=3, pwr="150mA",',
 "ESTIMATE: the low-concentration (10ppb-2ppm) MQ-131 variant this entry describes is "
 "~$30+; $8 buys the high-range version, which cannot do the job described."),

("part8_gps_thermal_camera_rf.py",
 'iface="SPI/UART (dev kits)", v="3.3-5V", usd=40, diff=5, pwr="~150mW",',
 'iface="SPI/UART (dev kits)", v="3.3-5V", usd=110, diff=5, pwr="~150mW",',
 "ESTIMATE: Infineon BGT60 dev shields are ~$100+, not $40."),
]


def main():
    changed = {}
    for fname, old, new, why in FIXES:
        path = DATA / fname
        text = changed.get(fname) or path.read_text()
        n = text.count(old)
        if n != 1:
            print(f"✗ FAIL [{fname}] expected 1 match, found {n}\n   why: {why}\n   {old[:100]!r}")
            sys.exit(1)
        changed[fname] = text.replace(old, new)
    for fname, text in changed.items():
        (DATA / fname).write_text(text)
    print(f"✓ applied {len(FIXES)} price/provenance corrections across {len(changed)} files")


if __name__ == "__main__":
    main()
