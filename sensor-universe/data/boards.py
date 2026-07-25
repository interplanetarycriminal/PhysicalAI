"""Boards & Compute — which ESP32, and why.

The variants differ far more than people expect, and the differences bite late:
C3/C6/H2 have NO capacitive touch peripheral and NO DAC, only S2/S3/P4
realistically drive a camera, PSRAM availability varies, ADC quality and usable
channel count differ sharply, and deep-sleep current differs by an order of
magnitude. v5 recommended "ESP32-C3" in about fifteen places without once
mentioning that it cannot do touch.

`meas` = what the board brings. `range` = memory. `rate` = clock.
"""

PARTS = [

# ---------------------------------------------------------------- classic
dict(catalog="board", n="ESP32 classic (WROOM-32E)", pn="ESP32-WROOM-32E / DevKitC v4",
 cat="Industrial & Automotive", sub="Original dual-core Xtensa",
 modality="Electrical", phenomena=["temperature-contact", "capacitance"],
 inferences=["someone-present"],
 meas="The default ESP32: dual-core 240MHz Xtensa, Wi-Fi 4 + Bluetooth Classic and BLE, 34 GPIO, "
      "10 touch channels, 2 DACs, 2 ADCs",
 how="The chip that made this whole ecosystem. Two Xtensa LX6 cores at 240MHz with Wi-Fi and a "
     "Bluetooth radio that still does Classic (which none of the newer parts do), plus the "
     "richest peripheral set in the family — including the capacitive touch and DAC blocks that "
     "the RISC-V generation dropped.",
 range="520KB SRAM, 4-16MB flash, no PSRAM on WROOM (use WROVER for 8MB PSRAM)",
 rate="240MHz dual-core", iface=["Builtin"], v="3.3V (boards take 5V USB)", logic_3v3=True,
 pins=34, esp32_compat="This IS the reference. Anything in this catalog works on it except "
 "USB-native peripherals and camera work needing PSRAM.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~40-80mA idle with Wi-Fi, ~160-260mA transmit peaks, 10-20µA deep sleep",
 pwr_ua=80000.0, pwr_sleep_ua=15.0, usd=6.0, buy=["AE", "AMZ", "AF", "SF", "DFR", "CE"],
 brd="DevKitC v4, NodeMCU-32S, Wemos D1 R32, countless clones",
 lib="ESP-IDF, Arduino-ESP32, MicroPython, ESPHome",
 link="https://www.espressif.com/en/products/socs/esp32",
 lifecycle="Mature", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="ADC2 stops working the moment Wi-Fi is active — a silent failure that produces frozen or "
       "garbage analog readings and wastes an enormous amount of people's time. Put every analog "
       "sensor on ADC1 (GPIO32-39). The ADC itself is non-linear and noisy even on ADC1. GPIO34-39 "
       "are INPUT ONLY and have no internal pull-ups, so they cannot drive anything or read a "
       "button without an external resistor. GPIO6-11 are wired to the flash chip and using them "
       "bricks the boot. GPIO0, 2, 12 and 15 are strapping pins: pulling GPIO12 high at boot sets "
       "the flash voltage wrong and the board never starts. Many cheap clones have an undersized "
       "3.3V regulator that browns out on Wi-Fi transmit peaks, which presents as random reboots.",
 hazard=[], calibration="None", consumable="None",
 requires="A 5V supply able to deliver 500mA of peak current; a phone charger is often not enough "
          "for reliable Wi-Fi transmit",
 substitutes="ESP32-S3 for anything needing PSRAM, USB or AI; ESP32-C3 for cheap and low-power; "
             "ESP32-C6 if you want Thread, Zigbee or Matter",
 diff=1, use="The default choice for anything that doesn't need a specific newer feature: sensor "
 "hubs, gateways, controllers, and every tutorial ever written.",
 spark="The Bluetooth Classic radio is the sleeper feature: it is the only part in the family that "
       "can act as a plain Bluetooth serial port or an A2DP audio sink, so it can bridge to legacy "
       "car stereos, OBD dongles and industrial devices that never got BLE.",
 pair="ADS1115 to fix the ADC, and a proper 5V supply", tags=["Home", "Industry", "Play"]),

dict(catalog="board", n="ESP32-WROVER (PSRAM)", pn="ESP32-WROVER-E / WROVER-IE",
 cat="Industrial & Automotive", sub="Classic with external PSRAM",
 modality="Electrical", phenomena=[], inferences=[],
 meas="ESP32 classic plus 8MB PSRAM — the cheapest route to camera and buffer-heavy work",
 how="Physically the same silicon as the WROOM with a PSRAM die in the package. That extra RAM is "
     "the entire difference between 'can hold a camera frame or a thermal array' and 'cannot'.",
 range="520KB SRAM + 8MB PSRAM, 4-16MB flash", rate="240MHz dual-core",
 iface=["Builtin"], v="3.3V", logic_3v3=True, pins=34,
 esp32_compat="Required for MLX90640 full-frame buffering, camera work and large TFT framebuffers "
 "on the classic generation. PSRAM occupies some pins on -E variants.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="Similar to WROOM plus ~10mA for PSRAM when active", pwr_ua=90000.0, pwr_sleep_ua=20.0,
 usd=8.0, buy=["AE", "AMZ", "DK", "MO"], brd="ESP32-WROVER-KIT, Freenove boards, ESP32-CAM",
 lib="ESP-IDF (enable PSRAM in menuconfig), Arduino-ESP32",
 link="https://www.espressif.com/en/products/modules",
 lifecycle="Mature", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="PSRAM is not automatic — it must be enabled in the build configuration, and code that "
       "works fine until you allocate a large buffer will fail with an out-of-memory error that "
       "looks nothing like a configuration problem. PSRAM is also markedly slower than internal "
       "SRAM and is accessed over SPI, so DSP or FFT working buffers should stay in internal RAM. "
       "On WROVER-E the PSRAM shares GPIO16/17, so those pins are unavailable.",
 hazard=[], calibration="None", consumable="None", requires="PSRAM enabled in the build config",
 substitutes="ESP32-S3 with PSRAM is faster, has USB and vector instructions for barely more money",
 diff=2, use="Camera boards, thermal arrays, large displays, audio buffering, anything that needs "
 "more than half a megabyte at once.",
 spark="If a project 'mysteriously' cannot hold a frame, this is usually the fix — and it is a "
       "two-dollar upgrade rather than a redesign.",
 pair="OV2640/OV5640 cameras, MLX90640, large SPI TFTs", tags=["Play", "Home", "Industry"]),

# ---------------------------------------------------------------- S series
dict(catalog="board", n="ESP32-S3", pn="ESP32-S3-WROOM-1 / S3-DevKitC-1",
 cat="Industrial & Automotive", sub="Dual-core with AI and USB",
 modality="Electrical", phenomena=["capacitance"], inferences=[],
 meas="Dual-core 240MHz with vector instructions for AI, native USB OTG, up to 8MB PSRAM, "
      "14 touch channels, Wi-Fi 4 + BLE 5",
 how="The workhorse of the modern family. Adds SIMD vector instructions that make TinyML and audio "
     "processing several times faster, native USB (so it can be a keyboard, a mass-storage device "
     "or a host), and enough RAM to do camera and display work comfortably.",
 range="512KB SRAM + up to 8MB PSRAM, 4-32MB flash", rate="240MHz dual-core + vector unit",
 iface=["Builtin", "USB"], v="3.3V", logic_3v3=True, pins=45,
 esp32_compat="The best all-rounder. Has touch and camera support; has NO DAC (unlike the classic) "
 "— use an external I2S DAC or PWM for analog output.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~40-100mA active, ~250mA Wi-Fi peaks, 7-10µA deep sleep",
 pwr_ua=90000.0, pwr_sleep_ua=8.0, usd=8.0, buy=["AE", "AMZ", "AF", "SF", "SS", "DFR"],
 brd="S3-DevKitC-1, XIAO ESP32S3 (and Sense with camera), ESP32-S3-EYE, Freenove S3 boards",
 lib="ESP-IDF, Arduino-ESP32, ESP-DL, ESP-SR, TensorFlow Lite Micro",
 link="https://www.espressif.com/en/products/socs/esp32-s3",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="It has no DAC, which surprises people porting classic-ESP32 audio projects. Native USB and "
       "the UART bridge are separate ports on most dev boards, and picking the wrong one in the IDE "
       "is the most common 'it won't upload' cause. Octal-PSRAM variants consume more pins than "
       "quad-PSRAM ones, so the usable GPIO count on a datasheet is optimistic. As with all "
       "ESP32s, ADC2 is unusable while Wi-Fi is on.",
 hazard=[], calibration="None", consumable="None", requires="",
 substitutes="ESP32-S2 if you want USB without the cost of two cores and BLE; ESP32-P4 for serious "
             "camera and display work; ESP32-C6 if you need Thread or Zigbee",
 diff=1, use="Edge AI, wake-word detection, camera projects, USB devices, smart displays, audio, "
 "and anything that outgrew the classic chip.",
 spark="Native USB means the sensor node can present itself as a USB drive holding its own CSV log "
       "— plug it into any computer with no driver, no app and no cable protocol to invent.",
 pair="Cameras, I2S microphones, TinyML models, large TFTs", tags=["Play", "Health", "Industry"]),

dict(catalog="board", n="ESP32-S2", pn="ESP32-S2-WROOM / S2 Saola",
 cat="Industrial & Automotive", sub="Single-core with USB, no Bluetooth",
 modality="Electrical", phenomena=["capacitance"], inferences=[],
 meas="Single-core 240MHz, native USB OTG, Wi-Fi only — no Bluetooth at all",
 how="The odd one out: a single Xtensa core with native USB and touch, but the Bluetooth radio was "
     "deliberately omitted. That makes it cheap and simple for Wi-Fi-only USB peripherals, and "
     "useless for anything BLE.",
 range="320KB SRAM, up to 2MB PSRAM", rate="240MHz single-core",
 iface=["Builtin", "USB"], v="3.3V", logic_3v3=True, pins=43,
 esp32_compat="Has touch and DAC. NO Bluetooth — check this before choosing it, because it is the "
 "single most common S2 disappointment.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~30-70mA active, ~20µA deep sleep", pwr_ua=60000.0, pwr_sleep_ua=20.0,
 usd=6.0, buy=["AE", "AF", "DK"], brd="S2 Saola, Adafruit QT Py ESP32-S2, FeatherS2",
 lib="ESP-IDF, Arduino-ESP32, CircuitPython (strong support here)",
 link="https://www.espressif.com/en/products/socs/esp32-s2",
 lifecycle="Mature", maturity="Good", confidence="High", as_of="2026-07",
 fools="No Bluetooth of any kind. Single core means Wi-Fi housekeeping and your application share "
       "one CPU, so tight timing loops stutter during network activity in a way they don't on "
       "dual-core parts.",
 hazard=[], calibration="None", consumable="None", requires="",
 substitutes="ESP32-S3 adds BLE and a second core for roughly the same money — usually the better buy",
 diff=1, use="USB HID devices, CircuitPython projects, Wi-Fi-only sensor nodes, macropads.",
 spark="A USB device that is also a Wi-Fi node: a macropad that types your passwords locally and "
       "publishes its own key-usage statistics to MQTT.",
 pair="Touch pads, USB HID libraries", tags=["Play", "Home"]),

# ---------------------------------------------------------------- C series
dict(catalog="board", n="ESP32-C3", pn="ESP32-C3-MINI-1 / C3-DevKitM-1",
 cat="Industrial & Automotive", sub="Cheap single-core RISC-V",
 modality="Electrical", phenomena=[], inferences=[],
 meas="Single-core 160MHz RISC-V, Wi-Fi 4 + BLE 5, tiny and cheap, very low sleep current",
 how="The budget and battery choice. A single RISC-V core with a modern BLE 5 radio in a small "
     "package, at roughly half the price and half the sleep current of the classic ESP32.",
 range="400KB SRAM, 4MB flash, no PSRAM", rate="160MHz single-core RISC-V",
 iface=["Builtin"], v="3.3V", logic_3v3=True, pins=22,
 esp32_compat="⚠ NO capacitive touch peripheral and NO DAC. Only 6 ADC channels. No camera. "
 "Any project in this catalog relying on touchRead() or dacWrite() will not work on a C3.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~20-45mA active, ~130mA transmit peaks, ~5µA deep sleep",
 pwr_ua=45000.0, pwr_sleep_ua=5.0, usd=3.0, buy=["AE", "AMZ", "SS", "AF", "DFR"],
 brd="C3-DevKitM-1, XIAO ESP32C3, Lolin C3 Mini, countless tiny clones",
 lib="ESP-IDF, Arduino-ESP32, ESPHome",
 link="https://www.espressif.com/en/products/socs/esp32-c3",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="No touch peripheral and no DAC — this is the single most common wrong-chip choice in the "
       "ecosystem, because the C3 is cheap and gets recommended reflexively. Only six ADC "
       "channels, and ADC2 is again unusable with Wi-Fi active. GPIO8 and GPIO9 are strapping "
       "pins, and GPIO9 is the boot button on most boards, so using them for an I2C bus produces "
       "boards that intermittently refuse to start. Single core means the radio competes with "
       "your code for CPU.",
 hazard=[], calibration="None", consumable="None", requires="",
 substitutes="ESP32-C6 for Thread/Zigbee/Matter and Wi-Fi 6 at slightly more; classic ESP32 if you "
             "need touch or a DAC; ESP32-H2 for 802.15.4 without Wi-Fi",
 diff=1, use="Battery sensor nodes, BLE beacons, cheap fleets, anything where cost per node and "
 "sleep current matter more than peripherals.",
 spark="At three dollars and five microamps asleep, this is the chip that makes fleets rational: "
       "twenty nodes for the price of one commercial sensor is what turns a measurement into a map.",
 pair="I2C sensors with alert pins, LiPo + TP4056, ESP-NOW", tags=["Fleet", "Home", "Energy"]),

dict(catalog="board", n="ESP32-C6", pn="ESP32-C6-WROOM-1 / C6-DevKitC-1",
 cat="Industrial & Automotive", sub="Wi-Fi 6 + 802.15.4 (Thread/Zigbee/Matter)",
 modality="Electrical", phenomena=[], inferences=[],
 meas="RISC-V with Wi-Fi 6, BLE 5, and an 802.15.4 radio for Thread, Zigbee and Matter",
 how="The connectivity chip. Alongside Wi-Fi 6 and BLE it carries an 802.15.4 radio, which is what "
     "Thread and Zigbee run on — so it can join a Matter smart-home fabric natively instead of "
     "pretending to be a Wi-Fi device.",
 range="512KB SRAM, 4-8MB flash", rate="160MHz RISC-V + 20MHz low-power core",
 iface=["Builtin"], v="3.3V", logic_3v3=True, pins=30,
 esp32_compat="⚠ NO touch peripheral, NO DAC — same trap as the C3. Has a genuinely useful "
 "low-power core that can run while the main core sleeps.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~30-60mA active, ~7µA deep sleep", pwr_ua=55000.0, pwr_sleep_ua=7.0,
 usd=6.0, buy=["AE", "AMZ", "AF", "SF", "SS"],
 brd="C6-DevKitC-1, XIAO ESP32C6, Adafruit Feather C6",
 lib="ESP-IDF (Thread/Matter SDKs), Arduino-ESP32, ESPHome",
 link="https://www.espressif.com/en/products/socs/esp32-c6",
 lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="Matter and Thread are genuinely complex to commission — the radio is the easy part and the "
       "certification, fabric and border-router setup is the hard part. Wi-Fi 6 here means the "
       "power-saving features rather than headline speed. No touch and no DAC, as with the C3.",
 hazard=[], calibration="None", consumable="None",
 requires="A Thread border router (an Apple TV, Echo, or an OpenThread RCP) for Thread work",
 substitutes="ESP32-H2 if you want 802.15.4 without Wi-Fi; C3 if you only need Wi-Fi and BLE",
 diff=2, use="Matter-native smart-home devices, Zigbee sensors, Thread mesh nodes, low-power "
 "always-on sensing using the LP core.",
 spark="Matter compatibility means a sensor you build shows up natively in Apple Home, Google Home "
       "and Alexa without a bridge, a cloud account or a custom app — the thing that has always "
       "separated hobby devices from products.",
 pair="Thread border router, low-power sensors on the LP core", tags=["Home", "Fleet", "Access"]),

dict(catalog="board", n="ESP32-C5", pn="ESP32-C5",
 cat="Industrial & Automotive", sub="Dual-band 5GHz Wi-Fi 6",
 modality="Electrical", phenomena=[], inferences=[],
 meas="The first ESP32 with 5GHz Wi-Fi — dual-band Wi-Fi 6, BLE 5, 802.15.4",
 how="Adds the 5GHz band, which matters because 2.4GHz is congested almost everywhere and because "
     "many modern networks are increasingly 5GHz-first. Also carries 802.15.4 for Thread/Zigbee.",
 range="Typically 384KB SRAM + PSRAM options, 4-16MB flash", rate="240MHz RISC-V",
 iface=["Builtin"], v="3.3V", logic_3v3=True, pins=30,
 esp32_compat="Newer part — library and ESPHome support is still maturing relative to the C3/C6.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="Comparable to C6; 5GHz transmit costs more than 2.4GHz", pwr_ua=70000.0, pwr_sleep_ua=8.0,
 usd=8.0, buy=["AE", "DK", "MO"], brd="ESP32-C5-DevKitC-1, early third-party boards",
 lib="ESP-IDF (recent versions); Arduino support trails",
 link="https://www.espressif.com/en/products/socs/esp32-c5",
 lifecycle="Active", maturity="Workable", confidence="Estimate", as_of="2026-07",
 fools="5GHz has worse penetration through walls than 2.4GHz, so a chip that solves congestion can "
       "create a range problem instead. Being newer, expect fewer worked examples and some "
       "libraries that assume 2.4GHz-only behaviour.",
 hazard=[], calibration="None", consumable="None", requires="",
 substitutes="ESP32-C6 if you don't specifically need 5GHz — much better documented today",
 diff=3, use="Deployments in RF-congested environments, offices, apartment blocks, and anywhere "
 "the 2.4GHz band is unusable.",
 spark="In a block of flats, 2.4GHz can be so congested that reliable telemetry is impossible. "
       "This is the part that makes a sensor fleet viable in exactly those buildings.",
 pair="Same sensors as any ESP32; the difference is purely the link", tags=["Home", "Fleet", "Industry"]),

dict(catalog="board", n="ESP32-H2", pn="ESP32-H2-MINI-1",
 cat="Industrial & Automotive", sub="802.15.4 + BLE, no Wi-Fi",
 modality="Electrical", phenomena=[], inferences=[],
 meas="Thread/Zigbee/Matter and BLE 5 with NO Wi-Fi at all — built for low-power mesh endpoints",
 how="Deliberately drops Wi-Fi to save power and cost. For a battery sensor that joins a Thread or "
     "Zigbee mesh, Wi-Fi is dead weight — this is the part that admits that.",
 range="320KB SRAM, 2-4MB flash", rate="96MHz RISC-V",
 iface=["Builtin"], v="3.3V", logic_3v3=True, pins=26,
 esp32_compat="⚠ NO Wi-Fi, NO touch, NO DAC. It cannot host a web page or talk MQTT directly — it "
 "needs a border router or coordinator to reach IP.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~20-40mA active, ~5µA deep sleep", pwr_ua=35000.0, pwr_sleep_ua=5.0,
 usd=5.0, buy=["AE", "DK", "MO", "AF"], brd="H2-DevKitM-1, Adafruit/Seeed H2 boards",
 lib="ESP-IDF (Zigbee and Thread SDKs)",
 link="https://www.espressif.com/en/products/socs/esp32-h2",
 lifecycle="Active", maturity="Workable", confidence="High", as_of="2026-07",
 fools="No Wi-Fi is the whole point and the whole trap — every tutorial that connects to an SSID "
       "is inapplicable, and you must have mesh infrastructure before a single node is useful. "
       "96MHz is noticeably slower for any signal processing.",
 hazard=[], calibration="None", consumable="None",
 requires="A Zigbee coordinator or Thread border router",
 substitutes="ESP32-C6 if you want the same meshes plus Wi-Fi as a fallback",
 diff=3, use="Battery Zigbee/Thread sensors, door and window contacts, mesh endpoints in an "
 "existing smart-home fabric.",
 spark="A Zigbee door sensor you built yourself, joining the same hub as your commercial ones and "
       "reporting something no commercial sensor does — the mesh does the hard part.",
 pair="Reed switches, PIR, low-power I2C sensors", tags=["Home", "Fleet", "Energy"]),

# ---------------------------------------------------------------- P series
dict(catalog="board", n="ESP32-P4", pn="ESP32-P4 (+ ESP32-C6/C5 companion)",
 cat="Industrial & Automotive", sub="High-performance, MIPI camera/display, no radio",
 modality="Electrical", phenomena=[], inferences=[],
 meas="Dual-core 400MHz RISC-V with MIPI-CSI camera and MIPI-DSI display, H.264 encoder, up to "
      "32MB PSRAM — and no wireless of its own",
 how="The performance part. Roughly twice the clock of an S3 with proper camera and display "
     "interfaces and hardware video encoding, aimed at HMI panels and vision. It has NO radio: "
     "wireless comes from a companion chip (usually a C6 or C5) over SDIO or SPI.",
 range="768KB SRAM + up to 32MB PSRAM", rate="400MHz dual-core RISC-V + 40MHz LP core",
 iface=["Builtin", "Camera", "USB"], v="3.3V", logic_3v3=True, pins=55,
 esp32_compat="The only ESP32 with MIPI-CSI/DSI. Needs a companion radio chip for any network "
 "connectivity — budget for two chips, not one.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="Substantially higher than the S3; this is not a coin-cell part", pwr_ua=200000.0,
 pwr_sleep_ua=30.0, usd=15.0, buy=["AE", "DK", "MO", "SS"],
 brd="ESP32-P4-Function-EV-Board, Waveshare ESP32-P4-Module-DEV-KIT, Maker Go P4+C5 boards",
 lib="ESP-IDF v5.3+; Arduino support is early",
 link="https://www.espressif.com/en/products/socs/esp32-p4",
 lifecycle="Active", maturity="Workable", confidence="Estimate", as_of="2026-07",
 fools="No Wi-Fi and no Bluetooth on the chip itself — a genuine shock to people who assume every "
       "ESP32 is wireless. The companion-chip arrangement adds board complexity, firmware for two "
       "targets, and a shared-bus bottleneck. Tooling and examples are far behind the S3, so "
       "expect to be an early adopter rather than to follow a tutorial.",
 hazard=[], calibration="None", consumable="None",
 requires="An ESP32-C6 or C5 companion for wireless; MIPI camera or display modules to justify it",
 substitutes="ESP32-S3 for almost everything cheaper and better documented; a Raspberry Pi if you "
             "genuinely need a full OS",
 diff=4, use="Smart display panels, camera and vision products, video streaming, HMI front ends.",
 spark="MIPI-DSI means a proper high-resolution touch panel driven directly, which is the piece "
       "that has always separated a maker device from something that looks manufactured.",
 pair="MIPI cameras and displays, ESP32-C6 companion", tags=["Play", "Industry", "Home"]),

# ---------------------------------------------------------------- notable boards
dict(catalog="board", n="Seeed XIAO ESP32 series", pn="XIAO ESP32C3 / C6 / S3 / S3 Sense",
 cat="Industrial & Automotive", sub="Thumbnail form factor",
 modality="Electrical", phenomena=[], inferences=[],
 meas="Postage-stamp boards (21x17.5mm) with USB-C, battery charging and castellated edges",
 how="The same silicon in the smallest sensible package, with a LiPo charger and battery pads "
     "already on board — which removes the two things that usually make a wearable build ugly.",
 range="Varies by variant; S3 Sense adds PSRAM, a camera and a microphone",
 rate="Varies by variant", iface=["Builtin", "USB"], v="3.3V (USB-C or LiPo)", logic_3v3=True,
 pins=11, esp32_compat="Very few exposed GPIO — count your pins before committing. The C3 and C6 "
 "variants inherit the no-touch, no-DAC limitation.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="Variant-dependent; battery charging built in", pwr_ua=45000.0, pwr_sleep_ua=6.0,
 usd=7.0, buy=["SS", "AE", "AMZ", "DFR"], brd="XIAO ESP32C3, C6, S3, S3 Sense",
 lib="Arduino-ESP32, ESP-IDF, Seeed libraries",
 link="https://wiki.seeedstudio.com/xiao_esp32c3_getting_started/",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Eleven usable GPIO goes quickly: an I2C bus, a UART and two interrupts and you are out. "
       "The onboard charger has a fixed charge current that may be too high for a very small cell. "
       "Castellated edges are lovely for production and awkward on a breadboard without the header "
       "version.",
 hazard=[], calibration="None", consumable="None", requires="",
 substitutes="Adafruit QT Py or Feather for the same idea with a different connector ecosystem",
 diff=1, use="Wearables, tiny sensor nodes, anything where the enclosure is the constraint.",
 spark="Built-in LiPo charging plus a 6µA sleep current means a wearable that needs no charging "
       "circuit design at all — the board IS the power system.",
 pair="Small LiPo cells, I2C sensors, haptic drivers", tags=["Health", "Play", "Fleet"]),

dict(catalog="board", n="LilyGO T-Display / T-Beam / LoRa32", pn="TTGO T-Display S3 / T-Beam / LoRa32 V3",
 cat="Industrial & Automotive", sub="Board with integrated peripheral",
 modality="Electrical", phenomena=[], inferences=[],
 meas="ESP32 boards with a screen, a LoRa radio or a GNSS receiver already integrated",
 how="Saves you the integration: T-Display has a colour IPS panel, LoRa32 has an SX1262 radio and "
     "antenna connector, T-Beam adds GNSS and 18650 holder. All the fiddly RF and display wiring "
     "is done and tested.",
 range="Varies; S3 versions carry PSRAM", rate="Varies", iface=["Builtin"], v="3.3V / USB / 18650",
 logic_3v3=True, pins=20,
 esp32_compat="Integrated peripherals consume pins — check the pinout before planning your sensors.",
 contact="Contact", privacy="None", environment=["Indoor", "Outdoor"],
 pwr="Display and LoRa dominate; T-Beam with GNSS is not a low-power platform",
 pwr_ua=120000.0, pwr_sleep_ua=200.0, usd=25.0, buy=["AE", "AMZ"],
 brd="T-Display-S3, LoRa32 V3, T-Beam Supreme, T-Watch",
 lib="Arduino-ESP32, RadioLib, TinyGPSPlus, LVGL, Meshtastic firmware",
 link="https://www.lilygo.cc/",
 lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="Board revisions change pin assignments without changing the product name, which is the "
       "single biggest source of wasted time — always match your pin definitions to the exact "
       "revision printed on the PCB. Onboard 18650 holders often lack protection circuitry. The "
       "battery-voltage divider is frequently on an ADC2 pin, so it reads nonsense with Wi-Fi on.",
 hazard=[], calibration="None", consumable="None",
 requires="An antenna fitted BEFORE powering any LoRa variant — transmitting without one damages "
          "the radio",
 substitutes="A plain board plus a separate module, if you want to choose your own pins",
 diff=2, use="LoRa field nodes, Meshtastic, GPS trackers, handheld instruments with a screen.",
 spark="Flash Meshtastic onto a LoRa32 and you have an off-grid text network with your neighbours "
       "in an afternoon — then start attaching this catalog's sensors to it as telemetry.",
 pair="Solar charging, environmental sensors, Meshtastic", tags=["Wild", "Fleet", "Play"]),

dict(catalog="board", n="M5Stack Core / Stick / Atom", pn="M5Stack Core2 / M5StickC Plus2 / ATOM",
 cat="Industrial & Automotive", sub="Enclosed modular ecosystem",
 modality="Electrical", phenomena=["acceleration"], inferences=[],
 meas="ESP32 in a finished plastic case with a screen, battery, buttons and a stackable connector",
 how="The opposite philosophy to a bare dev board: it arrives as a finished object. Grove ports and "
     "stackable modules mean you can build something presentable without a 3D printer or a soldering iron.",
 range="Varies by model; Core2 has PSRAM", rate="240MHz", iface=["Builtin"], v="USB-C / internal LiPo",
 logic_3v3=True, pins=8,
 esp32_compat="Pins are largely committed to the built-in screen, IMU and power management. Expansion "
 "happens through Grove ports and stacked modules rather than free GPIO.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="Screen dominates; a few hours on the internal cell", pwr_ua=110000.0, pwr_sleep_ua=100.0,
 usd=35.0, buy=["SS", "AE", "AMZ", "DFR"], brd="Core2, CoreS3, M5StickC Plus2, ATOM Lite/Matrix",
 lib="M5Unified, UIFlow (block programming), Arduino, ESPHome",
 link="https://docs.m5stack.com/",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="You pay a large premium over a bare board, and you trade away GPIO freedom for the "
       "enclosure. The internal battery is small, so anything with the screen on is a "
       "mains-tethered device in practice.",
 hazard=[], calibration="None", consumable="None", requires="",
 substitutes="A bare ESP32 plus a printed case if you value pins and cost over finish",
 diff=1, use="Demos and prototypes that must look finished, classroom kits, handheld tools, "
 "installations where a case matters.",
 spark="The fastest route from an idea to something you can hand to a non-technical person without "
       "explaining the exposed wires — which is often the real bottleneck in getting a project used.",
 pair="Grove sensors, stacked modules", tags=["Play", "Home", "Industry"]),

dict(catalog="board", n="ESP32-CAM (AI-Thinker)", pn="ESP32-CAM + OV2640",
 cat="Cameras & Vision", sub="Cheapest camera platform",
 modality="Optical", phenomena=["image-visible"], inferences=["object-present", "someone-present"],
 meas="An ESP32 with PSRAM, a 2MP camera and a microSD slot for about eight dollars",
 how="A WROVER-class module, an OV2640 camera and an SD slot on one small board. Astonishing value, "
     "and correspondingly rough around the edges.",
 range="4MB PSRAM, microSD", rate="240MHz", iface=["Builtin", "Camera"], v="5V (needs a real supply)",
 logic_3v3=True, pins=4,
 esp32_compat="The camera consumes almost every GPIO; you have roughly four pins left, and they "
 "conflict with the SD card if you use it.",
 contact="Standoff", privacy="Raw-imagery", environment=["Indoor"],
 pwr="~180mA streaming, peaks over 300mA", pwr_ua=180000.0, pwr_sleep_ua=1000.0,
 usd=8.0, buy=["AE", "AMZ", "DFR", "CE"], brd="AI-Thinker ESP32-CAM plus an MB programmer shield",
 lib="esp32-camera, ESPHome camera component",
 link="https://docs.ai-thinker.com/en/esp32-cam",
 lifecycle="Mature", maturity="Good", confidence="High", as_of="2026-07",
 fools="It has no USB — you need a separate serial adapter and must ground GPIO0 to flash, which "
       "is where most people's first hour goes. The 5V supply must be solid; brownouts during "
       "camera initialisation are extremely common on phone chargers and are usually misdiagnosed "
       "as a broken board. It gets hot. Cheap OV2640 modules vary in focus and colour quality. "
       "Being a Raw-imagery device it is the one part in this catalog with a genuine privacy "
       "footprint — think about where it points before you mount it.",
 hazard=[], calibration="None", consumable="None",
 requires="A USB-serial adapter or the MB programmer shield, and a 5V supply capable of 500mA",
 substitutes="XIAO ESP32S3 Sense is far nicer to work with for a few dollars more; ESP32-S3-EYE "
             "for AI vision work",
 diff=2, use="Doorbells, wildlife cameras, time-lapse, print monitoring, QR reading.",
 spark="At this price a camera becomes disposable enough to point at things you would never risk a "
       "real camera on — inside a beehive, a compost heap, a kiln porthole, a nest box.",
 pair="PIR for wake-on-motion, SD card, solar", tags=["Play", "Wild", "Home"]),

dict(catalog="board", n="ESP32-Ethernet-Kit / PoE boards", pn="ESP32-Ethernet-Kit / Olimex ESP32-POE",
 cat="Industrial & Automotive", sub="Wired networking",
 modality="Electrical", phenomena=[], inferences=[],
 meas="ESP32 with a real Ethernet PHY, and on PoE variants power over the same cable",
 how="An RMII Ethernet PHY gives a wired link that does not care about Wi-Fi congestion, and "
     "Power-over-Ethernet means one cable does data and power — which is what makes a permanent "
     "installation tidy and reliable.",
 range="Varies; typically WROVER-class with PSRAM", rate="240MHz",
 iface=["Builtin"], v="PoE 802.3af or 5V", logic_3v3=True, pins=12,
 esp32_compat="The Ethernet PHY consumes a large block of pins, including some you might want for "
 "sensors. Check the pinout early.",
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 pwr="PoE-powered; the PHY adds ~100mA", pwr_ua=150000.0, pwr_sleep_ua=1000.0,
 usd=25.0, buy=["AE", "DK", "MO"], brd="ESP32-Ethernet-Kit, Olimex ESP32-POE and POE-ISO, WT32-ETH01",
 lib="ESP-IDF ETH driver, Arduino ETH class, ESPHome ethernet component",
 link="https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-ethernet-kit/",
 lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="Not a low-power option — the PHY alone rules out battery operation. Clock configuration for "
       "the PHY (GPIO0 vs GPIO17 as the 50MHz source) differs between boards and is the usual "
       "reason Ethernet 'doesn't initialise'. Non-isolated PoE variants can create ground loops "
       "with connected sensors; the ISO versions exist for good reason.",
 hazard=[], calibration="None", consumable="None",
 requires="A PoE switch or injector for the PoE variants",
 substitutes="Wi-Fi plus a USB supply if reliability is not critical",
 diff=3, use="Permanent building installations, industrial gateways, anything in an RF-hostile "
 "environment or that must never drop off the network.",
 spark="One cable to a ceiling-mounted sensor cluster — data and power — is what makes a "
       "whole-building deployment tidy enough that a facilities manager will actually approve it.",
 pair="Modbus/RS-485 sensors, DIN-rail mounting, permanent installations", tags=["Industry", "Home", "Fleet"]),

dict(catalog="board", n="ESP-Prog debugger", pn="ESP-Prog / ESP-Prog-2",
 cat="Industrial & Automotive", sub="Development tool",
 modality="Electrical", phenomena=[], inferences=[],
 meas="JTAG debugging and a serial programmer for ESP32 targets",
 how="Gives you real source-level debugging — breakpoints, single stepping, variable inspection — "
     "instead of scattering print statements and rebuilding. On chips with native USB you can get "
     "the same thing without extra hardware.",
 range="n/a", rate="n/a", iface=["USB"], v="3.3V/5V selectable", logic_3v3=True, pins=6,
 esp32_compat="S3, C3, C6 and H2 have built-in USB-JTAG and need no external probe. The classic "
 "ESP32 and WROVER do need one.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="USB powered", pwr_ua=50000.0, usd=25.0, buy=["AE", "DK", "MO", "AF"],
 brd="ESP-Prog, ESP-Prog-2", lib="OpenOCD, ESP-IDF debug, VS Code / Eclipse integration",
 link="https://docs.espressif.com/projects/esp-dev-kits/en/latest/other/esp-prog/",
 lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="The JTAG pins (GPIO12-15 on the classic ESP32) overlap with pins projects commonly use for "
       "SD cards or displays, so debugging and your peripheral can be mutually exclusive. GPIO12 "
       "is also a strapping pin. Setting up OpenOCD is genuinely fiddly the first time.",
 hazard=[], calibration="None", consumable="None", requires="",
 substitutes="Built-in USB-JTAG on S3/C3/C6/H2 — free and easier",
 diff=3, use="Debugging crashes and memory corruption, driver development, anything where "
 "print-statement debugging has stopped being enough.",
 spark="The moment a project outgrows serial prints — a heap corruption, a watchdog reset you "
       "cannot reproduce — this turns a week of guessing into an afternoon of looking.",
 pair="Any ESP32 project that has started crashing mysteriously", tags=["Industry", "Play"]),
]
