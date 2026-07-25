"""Additional invention seeds (v6).

Written to spread evenly across all sixteen themes rather than clustering in the
easy ones, and deliberately NOT to restate any sensor's own `spark` — v5's seeds
were largely re-headed sparks, which made the sheet redundant.

`sensors` holds catalog part NAMES; resolve_ids.py converts them to stable IDs so
the workbook can compute the BOM.
"""

SEEDS_EXTRA = [

# ---------------------------------------------------------------- Home
dict(name="The Honest Thermostat",
 pitch="Most thermostats measure the air next to one wall. This one measures what a body "
       "actually feels: air temperature, radiant wall temperature, humidity and air movement, "
       "combined into a comfort index — then heats to THAT instead of to a number.",
 sensors="SHT41 humidity + temp · MLX90614 IR thermometer · FS3000 air velocity · LD2410 mmWave presence",
 parts="ESP32, relay or OpenTherm interface, ePaper display", bom=70, diff=3,
 themes="Home, Energy, Health", market="Anyone with a cold room they can't explain; retrofit heating",
 why="Radiant asymmetry is why a 21°C room with cold walls feels wrong. Nobody sells a "
     "domestic thermostat that measures it, and the physics is well documented."),

dict(name="Doorway Weather Station",
 pitch="A sensor sandwich either side of the front door measures exactly how much conditioned "
       "air you lose every time it opens — in watts, and in pennies.",
 sensors="SHT41 humidity + temp · BMP390 precision barometer · Reed switch · FS3000 air velocity",
 parts="ESP32, two small enclosures, magnet", bom=55, diff=3,
 themes="Home, Energy, Time", market="Energy-conscious households, retrofit assessors, landlords",
 why="Differential sensing across a boundary: neither absolute reading matters, the gradient "
     "is the whole signal. Turns an abstract nag into a number people argue about."),

dict(name="Laundry Finished, Actually",
 pitch="A vibration puck on the machine learns its cycle signature and tells you when the drum "
       "genuinely stops — not when a timer guesses. Then keeps nagging until the door opens.",
 sensors="ADXL345 accelerometer · Reed switch",
 parts="ESP32-C3, magnet on the door, LiPo", bom=20, diff=2,
 themes="Home, MachineHealth, Time", market="Every household with a washing machine",
 why="A perfect first temporal-pattern project: the classifier is trivial, the payoff is daily, "
     "and the same vibration trace later tells you the bearings are going."),

dict(name="Which Window Is Lying",
 pitch="A roaming node that parks on each windowsill for a day and ranks your windows by actual "
       "heat loss — surface temperature versus room temperature versus outside.",
 sensors="MLX90614 IR thermometer · SHT41 humidity + temp · VEML7700 high-accuracy lux",
 parts="ESP32-C3, LiPo, magnetic mount", bom=35, diff=2,
 themes="Home, Energy, Invisible", market="Homeowners deciding which windows to replace first",
 why="Window replacement is expensive and usually decided by guesswork. One cheap roaming "
     "sensor produces a ranked list and a payback estimate."),

# ---------------------------------------------------------------- Health
dict(name="Breathing Room",
 pitch="A meditation object that senses your breath contactlessly and breathes light back at "
       "you, gradually slowing to guide your rate down. No wearable, no app, no screen.",
 sensors="Seeed MR60BHA2 vital-sign radar · VEML7700 high-accuracy lux",
 parts="ESP32, WS2812 ring, diffuser, wooden shell", bom=55, diff=3,
 themes="Health, Play, Home", market="Meditation and wellness, anxiety support, gift market",
 why="Paced breathing works and is well evidenced; the friction is always the device. "
     "Contactless radar removes the strap, which is the thing people abandon."),

dict(name="Range of Motion Coach",
 pitch="A strap-on joint-angle sensor that speaks your live angle aloud during physio and logs "
       "whether you actually hit the prescribed range, the prescribed number of times.",
 sensors="BNO086 high-perf fusion IMU · Bend Labs digital flex (1-axis)",
 parts="ESP32-C3, I2S speaker, strap, LiPo", bom=95, diff=3,
 themes="Health, Robots, Time", market="Physiotherapy, post-op recovery, sports rehab",
 why="Home-exercise compliance is the single biggest predictor of recovery and the least "
     "measured. Angle plus count plus audio feedback is the whole intervention."),

dict(name="The Chair That Notices",
 pitch="A pressure mat under a cushion that reads posture, fidget rate and time-seated — then "
       "nudges rather than nags, because it knows when you're actually concentrating.",
 sensors="Velostat pressure sheets · FSR402 force resistor",
 parts="ESP32, CD74HC4067 multiplexer, haptic motor", bom=45, diff=4,
 themes="Health, Touch, Time", market="Desk workers, occupational health, ergonomics",
 why="Fidget rate is a surprisingly good proxy for both discomfort and focus, and a pressure "
     "matrix is cheap to build. The restraint in the interaction design is the product."),

dict(name="Silent Night Audit",
 pitch="Bedside node correlating snoring acoustics, room CO2, temperature and movement to "
       "explain why last night was bad — with an actionable single sentence each morning.",
 sensors="INMP441 I2S MEMS mic · SCD41 true CO2 · SHT41 humidity + temp · LD2410 mmWave presence",
 parts="ESP32-S3, ePaper, wooden case", bom=75, diff=3,
 themes="Health, Air, Home", market="Poor sleepers, partners of snorers, sleep-curious",
 why="Sleep trackers say WHAT happened; almost none say WHY. Environmental correlation is the "
     "missing half and it is entirely buildable."),

# ---------------------------------------------------------------- Wild
dict(name="Dawn Chorus Census",
 pitch="A weatherproof node that records the first hour after sunrise every day for a year and "
       "counts distinct bird vocalisations — a garden biodiversity index that improves with time.",
 sensors="ICS-43434 I2S mic · VEML7700 high-accuracy lux · SHT31 weatherproof probe",
 parts="ESP32-S3, SD card, solar, weatherproof case", bom=70, diff=4,
 themes="Wild, Time, Play", market="Birders, conservation groups, schools, rewilding projects",
 why="Acoustic biodiversity monitoring is a real scientific method with an active open-data "
     "community, and the light sensor gives you a true local sunrise rather than a calculated one."),

dict(name="The Stream Knows",
 pitch="A culvert node that learns the normal relationship between rainfall and water level, "
       "then raises the alarm when the stream rises faster than the rain justifies — which "
       "means a blockage downstream.",
 sensors="JSN-SR04T waterproof ultrasonic · Tipping bucket rain gauge · DS18B20 digital temp probe",
 parts="ESP32, LoRa, solar, pole mount", bom=85, diff=3,
 themes="Wild, Water, Safety", market="Flood-prone communities, councils, landowners",
 why="Anomaly against a learned baseline beats a fixed threshold. This detects the cause of a "
     "flood before the flood, which no simple level alarm can do."),

dict(name="Tree Health Diary",
 pitch="A dendrometer that measures a trunk's daily swelling and shrinking — trees fatten at "
       "night and shrink under water stress by day. Two years of that is a health record.",
 sensors="Bend Labs digital flex (1-axis) · DS18B20 soil temp spear · SHT31 weatherproof probe",
 parts="ESP32-C3, stainless band, solar, LoRa", bom=110, diff=4,
 themes="Wild, Grow, Time", market="Arboriculture, orchards, urban forestry, research",
 why="Micro-variation in stem diameter is an established plant-water-status method that almost "
     "no hobbyist has built. The signal is real and the daily rhythm is beautiful."),

# ---------------------------------------------------------------- Grow
dict(name="Seed Starting Oracle",
 pitch="Soil temperature at sowing depth plus a rolling seven-day average, matched against "
       "germination tables — it tells you which vegetable to sow this weekend, and which to wait on.",
 sensors="DS18B20 soil temp spear · Capacitive soil moisture v2 · SHT31 weatherproof probe",
 parts="ESP32-C3, solar, ePaper garden sign", bom=45, diff=2,
 themes="Grow, Time, Home", market="Vegetable gardeners, allotments, school gardens",
 why="Everyone sows by calendar and loses seed to cold soil. Soil temperature is the actual "
     "governing variable and nobody measures it."),

dict(name="Compost Thermophile Tracker",
 pitch="A multi-depth lance charting the heat curve of a compost heap, telling you exactly when "
       "to turn it — and warning you well before a hay-style self-heating event.",
 sensors="Compost / hay temp lance · SHT31 weatherproof probe · MQ-135 air quality",
 parts="ESP32, steel lance, LoRa, solar", bom=60, diff=3,
 themes="Grow, Safety, Time", market="Serious composters, community gardens, smallholdings, stables",
 why="Hot composting is a controlled microbial process people run blind. The same lance is a "
     "genuine fire-prevention device for stored hay."),

dict(name="Pollinator Traffic Counter",
 pitch="An optical gate at a hive entrance or a flower patch counting insect crossings by hour, "
       "correlated with temperature, light and wind — a foraging-activity dataset from a garden.",
 sensors="Through-beam slot / photo-interrupter · SHT31 weatherproof probe · VEML7700 high-accuracy lux",
 parts="ESP32-C3, 3D-printed tunnel, solar", bom=40, diff=3,
 themes="Grow, Wild, Time", market="Beekeepers, ecologists, citizen science, schools",
 why="Counting is the gateway analytic, and pollinator activity versus weather is a genuinely "
     "publishable backyard dataset."),

# ---------------------------------------------------------------- Water
dict(name="Shower Economics",
 pitch="Inline flow and temperature turn every shower into litres, kilowatt-hours and pence, "
       "shown on a display outside the bathroom door. Nobody is nagged; everybody sees it.",
 sensors="YF-S201 flow sensor · DS18B20 water temp + flow combo",
 parts="ESP32, plumbing tees, ePaper display", bom=45, diff=3,
 themes="Water, Energy, Home", market="Households, student housing, gyms, hotels",
 why="Flow times temperature difference is real thermal energy, so this is a genuine "
     "kWh meter for the single biggest hot-water draw in most homes."),

dict(name="Pond Dawn Watch",
 pitch="Dissolved oxygen crashes just before sunrise, which is when fish die. This node watches "
       "the overnight curve and starts the aerator on trajectory, not on a threshold.",
 sensors="Dissolved oxygen kit (Atlas EZO-DO) · DS18B20 digital temp probe · Turbidity sensor",
 parts="ESP32, aerator relay, float mount, solar", bom=230, diff=4,
 themes="Water, Grow, Safety", market="Koi keepers, aquaculture, ornamental ponds",
 why="Acting on the rate of change rather than the level buys hours of warning. Expensive "
     "sensor, but the fish are usually worth more."),

dict(name="Well Whisperer",
 pitch="Clamp-on flow plus pump current tells you the well's real yield, the pump's efficiency "
       "trend, and whether the water table is dropping season over season — without a plumber.",
 sensors="Transit-time ultrasonic flow (clamp-on) · ACS712 Hall current · JSN-SR04T waterproof ultrasonic",
 parts="ESP32, RS-485 adapter, enclosure", bom=140, diff=4,
 themes="Water, MachineHealth, Time", market="Rural households on wells, smallholdings, irrigators",
 why="Non-invasive metering on existing pipework, plus a pump-health signature that predicts "
     "the failure everyone finds out about at the worst moment."),

# ---------------------------------------------------------------- Air
dict(name="Kitchen Truth Hood",
 pitch="A hood that runs because of what cooking is actually producing — particulates, VOCs and "
       "humidity — rather than because someone remembered to press a button.",
 sensors="PMS5003 particulate · SGP40 VOC index · SHT41 humidity + temp · MLX90614 IR thermometer",
 parts="ESP32, fan speed control, magnet mount", bom=60, diff=3,
 themes="Air, Home, Health", market="Home cooks, open-plan kitchens, rental retrofits",
 why="Gas and even electric hobs are a major indoor pollution source, and extraction is almost "
     "always run too little and too late. The IR spot on the pan is the anticipation trick."),

dict(name="The Commute You Breathe",
 pitch="A handlebar or backpack node logging particulates and gases against GPS, producing a "
       "personal pollution map — then routing you down the cleaner parallel street.",
 sensors="PMSA003I particulate · MiCS-6814 tri-gas · NEO-6M GPS · SHT41 humidity + temp",
 parts="ESP32-C3, LiPo, SD, printed mount", bom=90, diff=3,
 themes="Air, Health, Wild", market="Cyclists, runners, parents with prams, asthma community",
 why="Personal exposure differs enormously from the city average, and one street over is often "
     "dramatically cleaner. Nobody knows this until they measure it."),

dict(name="Cellar Damp Detective",
 pitch="Distinguishes the three causes of a damp wall — condensation, rising damp and a leak — "
       "by comparing surface temperature against dew point over weeks.",
 sensors="MLX90614 IR thermometer · SHT41 humidity + temp · Capacitive soil moisture v2",
 parts="ESP32, wall mount, ePaper", bom=45, diff=3,
 themes="Air, Home, Time", market="Homeowners, surveyors, landlords, damp-proofing trades",
 why="Damp is routinely misdiagnosed and expensively mistreated. Surface temperature versus "
     "dew point separates condensation from everything else — that one comparison is the diagnosis."),

# ---------------------------------------------------------------- Energy
dict(name="Solar Honesty Meter",
 pitch="Measured irradiance against measured array output gives a live performance ratio — so "
       "dirt, shading and degradation show up as pounds per month rather than a vague feeling.",
 sensors="Pyranometer (solar irradiance) · INA226/INA228 precision power · DS18B20 digital temp probe",
 parts="ESP32, DC current shunt, weatherproof case", bom=110, diff=3,
 themes="Energy, Wild, Time", market="Solar owners, installers, community energy schemes",
 why="Inverter apps report output but never expected output. The ratio is the only number that "
     "tells you whether cleaning the panels is worth doing."),

dict(name="Standby Assassin",
 pitch="A rotating per-socket meter that spends a week on each appliance and produces a ranked "
       "list of what your house wastes doing nothing — with an annual cost against each.",
 sensors="PZEM-004T AC power module",
 parts="ESP32-C3, socket passthrough enclosure, display", bom=35, diff=3,
 themes="Energy, Home, Time", market="Households, landlords, efficiency programmes",
 why="Phantom load is invisible and universally underestimated. A ranked list with money "
     "attached changes behaviour in a way a dashboard never does."),

dict(name="Off-Grid Energy Ledger",
 pitch="Three-channel monitoring of solar in, battery store and load out, with a running "
       "energy balance — so an off-grid node can prove it banks more than it spends.",
 sensors="INA3221 triple-channel power · DS18B20 digital temp probe",
 parts="ESP32, MPPT module, supercap or LiPo, SD", bom=60, diff=3,
 themes="Energy, Wild, Time", market="Off-grid installations, remote sensing, vanlife, boats",
 why="Every remote node eventually dies at 4am in February. Coulomb-level accounting is the "
     "only way to know whether the design actually closes."),

# ---------------------------------------------------------------- Safety
dict(name="Workshop Cooldown Guardian",
 pitch="After you finish soldering, welding or using a heat gun, it watches the bench for 30 "
       "minutes with flame and thermal sensing — the period when workshop fires actually start.",
 sensors="IR flame detector (flicker) · Grid-EYE AMG8833 thermal array · MQ-2 smoke/LPG gas",
 parts="ESP32, buzzer, smart plug control", bom=70, diff=3,
 themes="Safety, MachineHealth, Home", market="Makerspaces, home workshops, jewellers, schools",
 why="Hot-work fires are famously delayed — the ignition happens after everyone has left. "
     "A timed post-work watch is a genuinely novel and cheap intervention."),

dict(name="Ladder Angle Buddy",
 pitch="A magnetic puck on a ladder rung that vibrates and lights green only at a safe 75° "
       "angle, and warns if the ladder shifts while you are up it.",
 sensors="Inclinometer SCL3300 · LIS3DH budget accel",
 parts="ESP32-C3, LiPo, haptic motor, magnet mount", bom=55, diff=2,
 themes="Safety, Motion, Home", market="Trades, DIY, facilities, insurers",
 why="Ladder falls are a leading cause of serious domestic and workplace injury, and the "
     "correct angle is a single measurable number that almost nobody checks."),

dict(name="Freezer Grace Period",
 pitch="Watches the door, the temperature and the compressor current together, so it can tell "
       "'door left ajar' from 'compressor has died' — and tells you how many hours of food you have left.",
 sensors="MCP9808 precision temp · Reed switch · ACS712 Hall current",
 parts="ESP32-C3, LiPo backup, push alerts", bom=35, diff=2,
 themes="Safety, Home, MachineHealth", market="Households, chest-freezer owners, small food businesses",
 why="A plain temperature alarm fires far too late. Diagnosing the CAUSE from three cheap "
     "signals is what turns an alert into an actionable hour count."),

# ---------------------------------------------------------------- MachineHealth
dict(name="Bearing Prophet",
 pitch="A high-rate accelerometer on a motor, an FFT on the ESP32, and a baseline recorded when "
       "everything was healthy. Alerts on the spectral drift that precedes failure by weeks.",
 sensors="KX132 low-power accel · MLX90614 IR thermometer · ACS712 Hall current",
 parts="ESP32-S3, magnetic mount, MQTT", bom=45, diff=4,
 themes="MachineHealth, Industry, Time", market="Workshops, HVAC contractors, small manufacturers, farms",
 why="Vibration, temperature and current together are far more reliable than any one of them. "
     "The 25kHz sample rate is what makes bearing frequencies visible at all."),

dict(name="3D Printer Sixth Sense",
 pitch="Listens to the printer's frame and watches its power draw to detect layer shifts, "
       "filament runout and spaghetti failures — without a camera or a cloud subscription.",
 sensors="Piezo contact mic / disc · ACS712 Hall current · VL53L0X ToF laser",
 parts="ESP32-S3, pause relay or Klipper webhook", bom=35, diff=4,
 themes="MachineHealth, Play, Time", market="3D printing (enormous hobby), print farms",
 why="Acoustic and current signatures catch failure modes a camera misses, and the ToF spool "
     "gauge answers 'will this print finish' before you start it."),

dict(name="Compressor Duty Diary",
 pitch="Logs every start, run and pressure cycle of a compressor or fridge, revealing shortening "
       "cycles and lengthening runs — the two signatures of a system losing charge.",
 sensors="ACS712 Hall current · MPRLS ported pressure · DS18B20 digital temp probe",
 parts="ESP32, current clamp, tee fitting", bom=50, diff=3,
 themes="MachineHealth, Energy, Time", market="Workshops, refrigeration trades, food businesses",
 why="Cycle-time trend is a leading indicator that requires no domain expertise to interpret "
     "once you have the baseline."),

# ---------------------------------------------------------------- Robots
dict(name="Teach-and-Repeat Arm",
 pitch="Magnetic encoders on every joint let you move a robot arm by hand to teach a motion, "
       "then replay it exactly. Programming by demonstration, no kinematics required.",
 sensors="AS5048A 14-bit angle · BNO086 high-perf fusion IMU",
 parts="ESP32-S3, servos or steppers, printed arm, teach button", bom=180, diff=5,
 themes="Robots, Play, Touch", market="Makerspaces, education, small automation, animatronics",
 why="Teaching by demonstration is how industrial robots are actually programmed, and it makes "
     "robotics tangible in a way code never does."),

dict(name="Terrain-Aware Rover",
 pitch="Optical flow for true ground speed, IMU for attitude, and ToF for obstacles — a rover "
       "that knows when its wheels are slipping rather than just how fast they are turning.",
 sensors="PMW3901 optical flow · BNO086 high-perf fusion IMU · VL53L1X long-range ToF",
 parts="ESP32-S3, motor drivers, chassis, LiPo", bom=140, diff=4,
 themes="Robots, Motion, Wild", market="Robotics hobbyists, agricultural robotics, education",
 why="Wheel encoders lie the moment there is slip, which outdoors is constantly. Optical flow "
     "is the cheap fix and is under-used in hobby robotics."),

dict(name="Follow-Me Cart",
 pitch="A UWB tag in your pocket and three anchors on a cart give centimetre-accurate relative "
       "position, so a trolley, mower or camera rig follows you at a fixed distance and bearing.",
 sensors="DW3000 UWB module · BNO086 high-perf fusion IMU · VL53L1X long-range ToF",
 parts="ESP32, motor drivers, cart frame, LiPo", bom=200, diff=5,
 themes="Robots, Motion, Access", market="Warehousing, film and photography, accessibility, gardening",
 why="UWB made relative positioning cheap and precise, and following a person is a far easier "
     "problem than autonomous navigation while feeling just as magical."),

# ---------------------------------------------------------------- Play
dict(name="The Weather Instrument",
 pitch="A physical instrument whose pitch, timbre and rhythm are driven by live weather — wind "
       "speed to tremolo, pressure to pitch, rain to percussion. Your house, audible.",
 sensors="Anemometer cup sensor · BMP390 precision barometer · Tipping bucket rain gauge · Wind vane",
 parts="ESP32-S3, I2S DAC, amplifier, speaker", bom=95, diff=3,
 themes="Play, Wild, Time", market="Installation artists, galleries, science museums, gift market",
 why="Data sonification is genuinely underexplored and weather is the most emotionally legible "
     "dataset there is. It also runs forever with no interaction."),

dict(name="Gravity Well",
 pitch="A table that senses where people stand around it and moves projected light as if their "
       "mass warped a shared surface — general relativity you can feel.",
 sensors="LD2450 multi-target tracking radar · VL53L5CX 8x8 ToF array",
 parts="ESP32-S3, short-throw projector, PC or Pi for rendering", bom=180, diff=4,
 themes="Play, Motion, Invisible", market="Science museums, galleries, festivals, universities",
 why="Multi-target radar makes crowd-responsive art tractable without cameras, which is what "
     "gets installations approved in public venues."),

dict(name="Memory Jar",
 pitch="An object that records the ambient conditions of a moment — light, sound level, "
       "temperature, who was present via BLE — and replays them as colour and tone a year later.",
 sensors="VEML7700 high-accuracy lux · INMP441 I2S MEMS mic · SHT41 humidity + temp",
 parts="ESP32-C3, WS2812, speaker, glass vessel, flash storage", bom=45, diff=3,
 themes="Play, Time, Home", market="Gift market, makers, memorial objects, weddings",
 why="Sensing as sentiment rather than utility. The technical content is modest; the emotional "
     "content is the whole point, and that is a legitimate design target."),

# ---------------------------------------------------------------- Invisible
dict(name="The Wall Has Wires",
 pitch="A sweepable wand that maps what is behind a wall — metal via inductance, live wiring via "
       "field, studs via capacitance — and draws it as you move across the surface.",
 sensors="LDC1612 inductive sensing · MLX90393 wide-range 3D mag · FDC1004 capacitive sensing",
 parts="ESP32-S3, small TFT, printed wand, wheel encoder", bom=75, diff=5,
 themes="Invisible, Home, MachineHealth", market="Trades, DIY, renovators, facilities",
 why="Commercial multi-mode detectors are expensive and give a beep. Building the map as you "
     "sweep is both more useful and a genuinely satisfying sensor-fusion exercise."),

dict(name="Radio Weather Map",
 pitch="A slowly rotating directional antenna logging RF power by bearing and frequency — a "
       "polar map of your electromagnetic environment, updated hourly.",
 sensors="EMF / RF field probes · QMC5883L compass",
 parts="ESP32, stepper, directional antenna, mast", bom=90, diff=5,
 themes="Invisible, Wild, Time", market="Radio amateurs, EMC hobbyists, spectrum researchers",
 why="Direction plus time turns a meaningless scalar into a map that reveals your neighbours' "
     "transmitters, interference sources and diurnal patterns."),

dict(name="Bat Corridor Mapper",
 pitch="Several time-synced ultrasonic nodes along a hedgerow reveal not just that bats are "
       "present but which way they commute, and when — a flight-corridor map.",
 sensors="Ultrasonic mic experiments · GPS PPS time source · SHT31 weatherproof probe",
 parts="ESP32-S3 x3, SD, solar, weatherproof cases", bom=170, diff=5,
 themes="Invisible, Wild, Fleet", market="Ecological consultants, conservation, planning objections",
 why="Bat commuting routes are legally protected and expensive to survey. Time-synced nodes "
     "turn presence detection into directional data, which is the part that matters."),

# ---------------------------------------------------------------- Industry
dict(name="Legacy Machine Digital Twin",
 pitch="Bolts onto a machine with no data interface at all and reconstructs its state from the "
       "outside: current, vibration, temperature, cycle counts. A 1980s machine on a dashboard.",
 sensors="ACS712 Hall current · KX132 low-power accel · MLX90614 IR thermometer · Inductive proximity switch M12/M18",
 parts="ESP32, DIN enclosure, 24V supply, Modbus or MQTT uplink", bom=120, diff=4,
 themes="Industry, MachineHealth, Time", market="Small manufacturers, job shops, agriculture, packaging",
 why="Most machines in the world predate connectivity and will never be replaced. External "
     "instrumentation is the entire retrofit market, and it is mostly unserved at this price."),

dict(name="Cold Chain Black Box",
 pitch="A tamper-evident logger that rides with a shipment recording temperature, humidity, "
       "shock, tilt and light — light meaning the box was opened.",
 sensors="TMP117 ultra-precise temp · SHT41 humidity + temp · High-g accel ADXL375 · VEML7700 high-accuracy lux",
 parts="ESP32-C3, LiPo, flash, NFC readout", bom=70, diff=3,
 themes="Industry, Access, Time", market="Pharma, specialty food, art shipping, laboratory logistics",
 why="Light as an intrusion sensor is the elegant part: a sealed box should be dark, so any "
     "photon is an event. NFC readout means the box never has to be opened to be read."),

dict(name="Loop-Powered Bridge",
 pitch="Reads existing 4-20mA industrial transmitters — the sensors already installed in every "
       "plant room on earth — and republishes them as MQTT without touching the control system.",
 sensors="4-20mA loop receiver · RS-485 soil NPK/EC probe",
 parts="ESP32, 250R precision resistor, isolated ADC, DIN rail, 24V supply", bom=90, diff=4,
 themes="Industry, Energy, Fleet", market="Facilities, building services, water treatment, agriculture",
 why="4-20mA is the most widely deployed sensor interface in existence and the most ignored by "
     "makers. Reading it is a resistor and an ADC, and it unlocks decades of installed hardware."),

# ---------------------------------------------------------------- Fleet
dict(name="Street Temperature Quilt",
 pitch="Twenty lent-out nodes across a neighbourhood produce a street-by-street heat map, "
       "showing which roads are ovens and which tree-lined stretches actually work.",
 sensors="AHT20 temp/humidity · VEML7700 high-accuracy lux",
 parts="ESP32-C3 x20, solar cases, LoRa or Wi-Fi, public map", bom=280, diff=3,
 themes="Fleet, Wild, Home", market="Climate resilience groups, councils, journalists, schools",
 why="Urban heat islands kill people and are invisible at city-average resolution. Twenty cheap "
     "nodes produce evidence that gets trees planted."),

dict(name="Building Occupancy Mesh",
 pitch="One presence node per room, meshed over ESP-NOW, produces a live floor plan of where "
       "people actually are — and a month of it reveals which rooms are wasted.",
 sensors="LD2410 mmWave presence · SCD41 true CO2",
 parts="ESP32-C3 x10, USB power, gateway, dashboard", bom=200, diff=3,
 themes="Fleet, Home, Energy", market="Offices, schools, churches, community buildings, co-working",
 why="Space is the second-largest cost for most organisations and is allocated on assumption. "
     "Camera-free occupancy data survives the privacy conversation."),

dict(name="Neighbourhood Quake Net",
 pitch="Ten seismic nodes across a few streets, time-synced by GPS, that detect P-waves and "
       "share a warning seconds before the shaking — and log the local ground response.",
 sensors="ADXL355 low-noise accel · GPS PPS time source",
 parts="ESP32 x10, concrete mounts, ESP-NOW or MQTT", bom=450, diff=5,
 themes="Fleet, Wild, Safety", market="Seismic regions, schools, community groups, researchers",
 why="P-waves arrive before S-waves, so even a few seconds of local warning is real. Community "
     "seismic networks are a proven model with an active open-data community."),

# ---------------------------------------------------------------- Access
dict(name="Tool Crib Conscience",
 pitch="Every tool carries a tag; the rack knows what left, when and with whom — and the "
       "dangerous machines only start for someone trained on them.",
 sensors="RC522 RFID reader · Fingerprint reader R503 · Inductive proximity switch M12/M18",
 parts="ESP32, contactor, RGB indicators, roster database", bom=110, diff=3,
 themes="Access, Industry, Safety", market="Makerspaces, schools, workshops, construction sites",
 why="Combines accountability and safety interlocking in one system, which is exactly what "
     "insurers and workshop managers ask for and rarely find affordably."),

dict(name="Tangible Playlist Shelf",
 pitch="A shelf of wooden tokens, each an album or a story. Place one on the pad and it plays; "
       "take it off and it stops. No screen, no account, no search.",
 sensors="PN532 NFC controller · VCNL4040 proximity + lux",
 parts="ESP32, I2S DAC and amp, speaker, wooden tokens, NFC stickers", bom=70, diff=2,
 themes="Access, Play, Home", market="Families with young children, elderly relatives, gift market",
 why="Tangible interfaces beat touchscreens decisively for both children and people with "
     "dementia. This is the single most-loved build in the maker canon for good reason."),

dict(name="Tap-to-Provision Fleet",
 pitch="Onboarding infrastructure for everything else here: tap your phone to a new node and it "
       "receives its Wi-Fi credentials, its name and its room over NFC.",
 sensors="PN532 NFC controller",
 parts="ESP32, NFC antenna, provisioning app or NDEF tags", bom=25, diff=3,
 themes="Access, Fleet, Home", market="Anyone deploying more than three nodes",
 why="Provisioning is where fleet projects die. Solving it once, properly, is what separates a "
     "demo from a deployment — and it is the UX commercial products use."),
]
