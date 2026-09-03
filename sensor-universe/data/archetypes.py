"""The ten shapes almost every ESP32 sensing project actually takes.

Knowing which archetype you are building tells you the failure modes in advance,
which is usually more useful than knowing which sensor to buy.
"""

ARCHETYPES = [
dict(name="Battery sleeper node",
 what="Wakes on a timer or an interrupt, takes a reading, transmits, sleeps again. "
      "Spends >99.9% of its life asleep. The workhorse of remote sensing.",
 parts="ESP32-C3 or C6 · one or two I²C sensors with alert pins · LiPo or 18650 · "
       "TP4056 charger · a MOSFET to cut sensor power during sleep",
 power="Deep sleep 5-20µA. The radio, not the sensor, dominates: budget by "
       "connection time, not measurement time. Use ESP-NOW rather than Wi-Fi "
       "association and battery life often triples.",
 comms="ESP-NOW to a mains-powered gateway · LoRa where range matters",
 fails="Wi-Fi association takes 2-5s and eats the budget. A sensor left powered "
       "during sleep costs more than the sensor's own datasheet suggests. RTC "
       "memory is lost on brownout, so counters reset. Cold halves battery "
       "capacity and charging a LiPo below 0°C damages it permanently.",
 first="Fridge/freezer temperature alarm using an MCP9808's ALERT pin as the wake "
       "source — it sleeps at ~0.1µA and only boots when temperature drifts."),

dict(name="Always-on gateway",
 what="Mains-powered, permanently connected, aggregates many nodes and speaks to "
      "the outside world. Every fleet needs exactly one.",
 parts="ESP32 classic or S3 · Ethernet or Wi-Fi · optional SD for buffering · "
       "a real 5V supply, not a phone charger",
 power="Mains. Size the supply for radio peaks (~500mA), not average draw, and "
       "add bulk capacitance near the module.",
 comms="ESP-NOW or LoRa downward · MQTT/HTTP upward · Home Assistant or a broker",
 fails="Brownout resets from an undersized supply are the single most common "
       "cause of 'random' reboots. Wi-Fi channel must match the ESP-NOW peers. "
       "Buffer to SD or NVS or you lose data whenever the network blips.",
 first="An ESP-NOW → MQTT bridge. Build it before the second sensor node, not after."),

dict(name="Closed-loop controller",
 what="Reads a sensor, decides, drives an actuator, and keeps doing it. The "
      "moment a project stops reporting and starts ACTING.",
 parts="Sensor · ESP32 · relay/SSR/MOSFET/servo · a manual override switch · "
       "an independent hardware failsafe",
 power="Mains or a supply sized for the actuator, isolated from the logic rail.",
 comms="Local-first. It must keep controlling when the network is down.",
 fails="Hysteresis: without a deadband the output chatters and destroys relays. "
       "A crashed ESP32 leaves the output latched — use a hardware watchdog and a "
       "failsafe (thermal cutout, float switch, mechanical stop) that works with "
       "the micro dead. Never make the ESP32 the only thing between a heater and a fire.",
 first="A fermentation or reptile-enclosure thermostat: DS18B20, SSR, 0.5°C "
       "hysteresis, plus a mechanical thermal cutout in series."),

dict(name="Field station",
 what="Solar-powered, outdoors, unattended for months, reporting over long range.",
 parts="Weatherproof enclosure with a vented gland · solar panel · charge "
       "controller · 18650 with a protection board · LoRa · desiccant",
 power="Solar plus battery, sized for the WORST week of the year, not the average. "
       "Measure your own consumption with an INA226 before sizing anything.",
 comms="LoRa or LoRaWAN · store-and-forward when the link drops",
 fails="Water gets in through the cable gland and the vent, not the lid. "
       "Condensation inside the box is the real enemy: an RH sensor inside a "
       "'sealed' enclosure is the cheapest gasket-failure detector there is. "
       "Insects nest in vents. Panels foul, and winter sun is a fraction of summer.",
 first="A weather node: BME280 in a radiation shield, tipping-bucket rain gauge, "
       "solar plus LoRa. It teaches every bus and every outdoor failure mode."),

dict(name="Wearable / body node",
 what="Small, light, battery-powered, worn on a person. Comfort and safety "
      "constraints dominate every technical choice.",
 parts="ESP32-C3 in a small package · LiPo with protection · BLE · IMU · "
       "skin-safe electrodes or optical sensor · haptic feedback",
 power="Coin cell to small LiPo. BLE rather than Wi-Fi; wake on IMU motion "
       "rather than on a timer.",
 comms="BLE to a phone. Buffer locally, sync opportunistically.",
 fails="Motion artefacts swamp every optical and biopotential signal — this is "
       "THE problem in wearables, not sensor accuracy. Skin contact quality drifts "
       "as the wearer moves and sweats. LiPo cells near skin need protection "
       "circuitry and a mechanical guard. Nothing sharp, nothing hot.",
 first="An HRV band: MAX30102 plus an IMU used purely to reject motion-corrupted "
       "beats. The IMU is the interesting part."),

dict(name="Fleet / mesh",
 what="Many cheap identical nodes turning a measurement into a map. The moment a "
      "gadget becomes an instrument.",
 parts="10+ identical nodes · one gateway · a provisioning scheme · a dashboard",
 power="Per-node battery or USB. Standardise so you build one node ten times.",
 comms="ESP-NOW (no router, sub-10ms, ~250 byte payload) or LoRa for spread-out sites",
 fails="Provisioning ten nodes by hand is where the project dies — solve naming, "
       "credentials and OTA on node one. Nodes must be interchangeable: if node 7 "
       "reads 0.4°C high you need per-node calibration offsets. Clock sync matters "
       "the moment you compare nodes.",
 first="Room-by-room comfort mapping with ten $2 AHT20 nodes. The spatial pattern "
       "is invisible from any single point."),

dict(name="Logger / black box",
 what="Records faithfully to local storage, retrieved later. No network required, "
      "which is exactly why it survives where connected devices don't.",
 parts="ESP32 · microSD or SPI flash · RTC (DS3231) · a real-time clock battery",
 power="Whatever the deployment allows; logging is cheap, the radio is not.",
 comms="None during operation. That's the point.",
 fails="SD cards corrupt on power loss mid-write — flush often, or use SPI flash "
       "with a journalled scheme. Without an RTC your timestamps are meaningless "
       "after a reset. Log the units and the calibration state alongside the "
       "values, or the data is unreadable in six months.",
 first="A shipment abuse logger: high-g accelerometer plus RTC, recording every "
       "impact with a timestamp."),

dict(name="Camera trap",
 what="Sleeps until something happens, wakes, captures an image, stores or sends it.",
 parts="ESP32-S3 with PSRAM (not a C3) · OV2640/OV5640 · PIR or radar as the "
       "trigger · IR illuminator · large battery or solar",
 power="Deep sleep between events. The camera and Wi-Fi together are the whole "
       "budget — an image upload can cost more charge than a day of sleeping.",
 comms="Wi-Fi burst on event · SD for the full-resolution copy",
 fails="A DVP camera consumes ~16 GPIO, which is why this needs an S3. PIR "
       "false-triggers on sunlight and moving vegetation will flatten the battery "
       "overnight — gate the trigger. Night images need IR illumination and a "
       "camera without an IR-cut filter.",
 first="A wildlife or doorstep camera with a PIR wake and SD storage — get it "
       "working on USB power before adding a battery."),

dict(name="Bench instrument",
 what="A purposeful measuring device with a display, used in the hand rather than "
      "installed. Interaction design matters as much as sensing.",
 parts="ESP32-S3 · TFT or ePaper · rotary encoder or touch · LiPo · a case you "
       "are not embarrassed by",
 power="Rechargeable, with an honest battery indicator (a fuel gauge, not a voltage guess).",
 comms="Optional. USB for data export is usually enough.",
 fails="Display refresh dominates power and blocks the CPU. Analog front-ends "
       "pick up noise from the display's own supply — separate the grounds. "
       "Calibration must survive a reboot, which means NVS, not RAM.",
 first="A thermal camera viewer: MLX90640 plus an SPI TFT on an S3. Instantly "
       "useful, and it teaches PSRAM and framebuffers."),

dict(name="Installation / art piece",
 what="Sensing in service of an experience. Reliability under public abuse is the "
      "engineering problem; the sensing is often the easy part.",
 parts="ESP32 · presence or touch sensing · LEDs, DMX, sound or projection · "
       "a physical enclosure that survives the public",
 power="Mains, with everything on one switched supply so a gallery can turn it "
       "off at night and on in the morning without you.",
 comms="Local. Never depend on venue Wi-Fi.",
 fails="Must recover from a power cut with no human intervention — no setup "
       "screens, no pairing, no app. Ambient light and crowd noise vary wildly "
       "between the workshop and the venue, so auto-calibrate on boot. Anything "
       "reachable will be touched, pulled and leaned on.",
 first="A presence-reactive light: LD2410 plus a WS2812 strip, with graceful "
       "fades rather than binary switching — subtlety reads as magic."),
]
