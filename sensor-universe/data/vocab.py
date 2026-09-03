"""Controlled vocabularies — categories, themes, phenomena, inferences.

PHENOMENON and INFERENCE are the two halves of the idea at the centre of this
document:

    A sensor never measures what you want to know. It measures a physical PROXY.
    The invention is the mapping from proxy to meaning.

    phenomena  = what the part physically transduces   (load cell -> force)
    inferences = what that lets you know about the world (load cell -> "the hive
                 is about to swarm", "the gas bottle is nearly empty", "someone
                 is sitting here", "the filament spool has 210g left")

Because the mapping is many-to-many, two navigations become possible and both are
sheets in the workbook:
    * one inference  -> many sensor routes  (choose by cost/privacy/power)  = Inference Atlas
    * one sensor     -> many inferences     (see everything one part unlocks) = Sensor Cards
"""

# --------------------------------------------------------------------------- categories
# Primary shelf only. Cross-cutting relationships live in phenomena/inferences,
# which is what lets us delete v5's "Specialty & Exotic" junk drawer.
#   cat -> (emoji, what this family does, when to reach for it)
CATEGORY = {
 "Temperature": ("🌡️", "Contact and non-contact temperature, from cryogenic to kiln.",
   "The universal first signal — almost every system reveals itself through temperature."),
 "Humidity & Moisture": ("💧", "Relative humidity, dew point, and moisture in materials.",
   "Comfort, condensation, mould, drying, curing, and anything that must not get damp."),
 "Pressure & Altitude": ("⛰️", "Absolute, gauge and differential pressure; barometric altitude.",
   "Height, weather trends, airflow through filters, liquid depth, vacuum, breath."),
 "Gas & VOC": ("☣️", "Chemical sniffing: combustibles, solvents, odours, specific toxics.",
   "Leaks, smells, off-gassing, combustion quality — when the nose needs numbers."),
 "CO2": ("🫁", "True CO2 by NDIR, photoacoustic or thermal conductivity.",
   "Ventilation truth, greenhouses, fermentation. Never accept an eCO2 estimate for these."),
 "Particulate": ("🌫️", "Laser and optical particle counters: smoke, dust, pollen, pollution.",
   "Wildfire seasons, kitchens, allergies, purifier control, citizen air networks."),
 "Light & UV": ("☀️", "Illuminance from starlight to sunburn, plus UV dosimetry and flame.",
   "Circadian work, grow lights, solar exposure, and day/night logic done properly."),
 "Colour & Spectral": ("🌈", "RGB through multi-channel spectrometry — colour as chemistry.",
   "Sorting, colorimetry, ripeness, material ID, light-quality auditing."),
 "Distance & Ranging": ("📏", "Ultrasonic, IR, laser ToF and LiDAR, from 1mm to 40m.",
   "Levels, navigation, counting, gesture — distance is the most versatile primitive there is."),
 "Presence & Occupancy": ("👤", "PIR, mmWave radar, thermopile arrays — is someone (still) there?",
   "The smart-building keystone. mmWave changed everything: stillness is now visible."),
 "Motion & Vibration": ("🌀", "Accelerometers, gyros, IMUs, seismic and impact sensing.",
   "Anything that moves, shakes, tilts, falls, swings — and every machine that is wearing out."),
 "Magnetic & Compass": ("🧲", "Heading, magnet tracking, Hall switches, field anomalies.",
   "Contactless position through walls and plastic, RPM, door state, hidden-wire finding."),
 "Sound & Audio": ("🎤", "MEMS mics, contact pickups, SPL meters, hydrophones, ultrasound.",
   "Voice, events, machine hums, and the entire acoustic world above and below hearing."),
 "Force & Weight": ("⚖️", "Load cells, strain gauges, FSRs, torque and pressure mapping.",
   "Depletion tracking, occupancy, grip, structural load. Weight-over-time is underrated telemetry."),
 "Touch & Capacitive": ("👆", "Touch on anything conductive — including ten free ESP32 pins.",
   "Invisible buttons, sealed controls, liquid level through walls, fruit pianos."),
 "Flex & Stretch": ("🪢", "Bend, elongation and soft deformation.",
   "Gloves, breathing bands, posture, soft robots — anything compliant that moves."),
 "Biometric & Health": ("❤️", "Pulse, SpO2, ECG, EMG, EDA, respiration, body temperature.",
   "Wearables, biofeedback, accessibility interfaces, quantified recovery."),
 "Weather & Outdoor": ("🌦️", "Wind, rain, lightning, solar irradiance, snow, leaf wetness.",
   "Weather stations are the gateway drug — and storm logic genuinely protects property."),
 "Soil & Agriculture": ("🌱", "Soil moisture, tension, chemistry and temperature; plant-direct sensing.",
   "Irrigation truth, planting timing, compost safety, agronomy at domestic scale."),
 "Water & Liquid": ("🌊", "Level, flow, leaks, and pH/EC/DO/ORP chemistry.",
   "Tanks, pools, aquariums, hydroponics, leak insurance, stream science."),
 "Power & Electrical": ("⚡", "Current, voltage, power, energy, battery state.",
   "Battery budgets, solar audits, appliance fingerprints, motor stall detection."),
 "Position & Rotation": ("🎛️", "Encoders, absolute angle, tilt, linear travel.",
   "Knobs, robot joints, machine feedback, anything that rotates or slides."),
 "GNSS & Positioning": ("🛰️", "Metre-class GNSS to centimetre RTK, UWB, and nanosecond time.",
   "Tracking, geofencing, surveying, robot navigation, distributed time sync."),
 "Thermal Imaging": ("🔥", "Heat pictures, from 16 to 19,200 thermal pixels.",
   "Insulation hunting, people counting, equipment hotspots, wildlife at night."),
 "Cameras & Vision": ("📷", "Image sensors and on-device neural vision modules.",
   "When the answer needs a picture — or a model watching one for you."),
 "Radiation & Nuclear": ("☢️", "Ionising radiation: GM tubes, scintillators, SiPM, radon.",
   "Dose rates, isotope identification, radon health, cosmic-ray physics."),
 "RF & Electromagnetic": ("📡", "Radio sensing: sub-GHz, RF power, EMF, channel state.",
   "Reading the invisible radio environment — and the devices already broadcasting in it."),
 "Identity & Tags": ("🪪", "RFID, NFC and biometric identification.",
   "Tangible interfaces, access control, inventory, tap-to-configure UX."),
 "Industrial & Automotive": ("🏭", "Sealed, threaded, 24V-world sensing: 4-20mA, Modbus, CAN.",
   "When hobby breakouts die: conveyors, vehicles, plant rooms, outdoors forever."),
 "Materials & Textiles": ("🧵", "Sewn, printed and material-embedded sensing.",
   "Garments, plush interfaces, surfaces-as-sensors, colour-change chemistry."),
 "Frontier Sensing": ("🚀", "Not commercially packaged — you build and validate it yourself.",
   "Wi-Fi CSI, e-nose arrays, acoustic emission, muon detection, atmospheric electricity."),
}

# --------------------------------------------------------------------------- themes
# Invention territories. Each is a QUESTION, not a bucket.
# v5's tags were quota-filled (91% of entries had exactly 3) and 7 of 16 were
# near-synonyms of a category, so they duplicated the shelf instead of cutting
# across it. These are chosen to be orthogonal to CATEGORY on purpose.
#   tag -> (display, description, the creative question, star parts, example inventions)
THEME = {
 "Home": ("Living Spaces", "Rooms that notice, adapt and quietly help.",
   "What would this room do if it could feel?",
   "LD2410 mmWave · SCD41 · VL53L1X · reed switches · CT clamps",
   "Rooms that breathe · lights that know you're reading · doors that report"),
 "Health": ("Body & Health", "Vitals, movement, stress, recovery, accessibility.",
   "What is my body saying that I can't hear?",
   "MAX30102 · AD8232 · MyoWare · MLX90632 · respiration radar",
   "Contactless sleep labs · tremor-aware utensils · blink-controlled switches"),
 "Wild": ("Outdoors & Earth", "Weather, wildlife, rivers, sky, quakes.",
   "What is happening out there when nobody is watching?",
   "AS3935 · SPS30 · geophone · TSL2591 · snow LiDAR",
   "Lightning-triggered cameras · bat census stations · seismic meshes"),
 "Grow": ("Food & Plants", "Soil, leaf, climate, harvest — closing the loop.",
   "What does this plant actually want right now?",
   "Capacitive soil · SCD30 · Watermark · leaf clip · pH/EC",
   "Hydroponic autopilots · mildew-hour predictors · beehive scales"),
 "Water": ("Water Worlds", "Levels, flows, chemistry, leaks.",
   "Where is water going, and what is it carrying?",
   "pH/EC/DO probes · flow meters · eTape · leak rope",
   "Self-dosing pools · flood early-warning · whole-house leak brains"),
 "Air": ("Air & Breath", "The invisible stuff you inhale 20,000 times a day.",
   "What's in this breath?",
   "SCD41 · PMS5003 · SGP41 · BME690 · electrochemical cells",
   "CO2 honesty lights · pre-emptive purifiers · exposure badges"),
 "Energy": ("Power & Energy", "Watts, joules, batteries, solar — made visible.",
   "Where does the energy actually go?",
   "INA228 · SCT-013 · PZEM-004T · pyranometer · fuel gauges",
   "Appliance fingerprinting · solar truth meters · phantom-load hunters"),
 "Safety": ("Guardians", "The bad day: fire, gas, leaks, falls, intrusion.",
   "What failure would hurt most, and what is its earliest signal?",
   "Certified gas alarms · flame detectors · leak rope · fall radar",
   "Stove sentinels · hay-fire lances · CO migration mappers"),
 "MachineHealth": ("Machine Whisperer", "Hearing machines age before they fail.",
   "What is this machine trying to tell me before it breaks?",
   "KX132 FFT · ACS712 · IR thermometers · acoustic emission",
   "Bearing prognosis · compressed-air leak audits · tool-state dashboards"),
 "Robots": ("Robots & Vehicles", "Perception for things that move themselves.",
   "What does my machine need to sense in order to act alone?",
   "LiDAR · encoders · IMU · RTK GNSS · UWB · ToF arrays",
   "RTK mowers · echolocation belts · teach-and-replay arms"),
 "Play": ("Play & Art", "Instruments, installations, toys, magic tricks with physics.",
   "What would make someone gasp or grin?",
   "Trill · gesture radar · LDR harps · RFID tokens · person sensor",
   "Laser harps · heartbeat rooms · art that performs only when watched"),
 "Invisible": ("Invisible Worlds", "Senses humans were never issued.",
   "What invisible layer of reality can I make visible?",
   "Geiger tubes · Wi-Fi CSI · CC1101 · muon detectors · EMF probes",
   "Through-wall presence · isotope identifiers · cosmic-ray flight logs"),
 "Industry": ("Work & Industry", "The 24V world: plants, workshops, vehicles, trades.",
   "What would a professional pay to stop guessing about?",
   "4-20mA transmitters · Modbus probes · CAN/OBD · inductive prox",
   "Digital twins of legacy plant · operator interlocks · fleet telemetry"),
 "Fleet": ("Fleets & Maps", "One node is a gadget; a hundred is a map.",
   "What changes when I measure this in a thousand places at once?",
   "ESP-NOW meshes · LoRa nodes · cheap duplicated sensors",
   "Street heat maps · community air networks · building-wide occupancy"),
 "Time": ("Time & Memory", "The cheapest superpower: the same sensor, logged.",
   "What does this look like as a trend rather than a reading?",
   "Any sensor + RTC + storage + a baseline",
   "Depletion curves · anomaly detection · seasonal fingerprints"),
 "Access": ("Identity & Access", "Who, and are they allowed?",
   "Should this thing behave differently depending on who is near it?",
   "RFID/NFC · fingerprint · BLE presence · UWB ranging",
   "Tool interlocks · tangible playlists · tap-to-provision fleets"),
}

# --------------------------------------------------------------------------- phenomena
# What a part physically transduces. Deliberately physical, not application-level.
PHENOMENON = {
 # thermal
 "temperature-contact": "Temperature of something it touches",
 "temperature-remote": "Surface temperature at a distance (IR emission)",
 "temperature-field": "A 2D map of temperatures",
 "heat-flux": "Rate of heat flow through a surface",
 # moisture
 "humidity-relative": "Water vapour in air, as % of saturation",
 "moisture-material": "Water content inside a solid (soil, grain, wood)",
 "water-tension": "How hard roots must pull to get water (matric potential)",
 "surface-wetness": "A film of liquid on a surface (dew, rain, condensation)",
 "dew-point": "Temperature at which air will condense",
 # pressure & flow
 "pressure-absolute": "Total pressure including atmosphere",
 "pressure-gauge": "Pressure relative to ambient",
 "pressure-differential": "Difference between two points — the basis of airflow",
 "altitude-barometric": "Height inferred from air pressure",
 "flow-liquid": "Volume of liquid per unit time",
 "flow-gas": "Volume or mass of gas per unit time",
 "air-velocity": "Speed of moving air",
 "liquid-level": "Height of a liquid surface",
 # light
 "illuminance": "Visible light intensity, human-weighted",
 "irradiance": "Radiant power per area across a band",
 "spectral-power": "Light intensity split into wavelength bands",
 "colour": "Chromaticity of light or a surface",
 "uv-a": "UV-A radiation (315-400nm)",
 "uv-b": "UV-B radiation (280-315nm)",
 "uv-c": "UV-C radiation (100-280nm), germicidal",
 "ir-near": "Near-infrared reflectance or emission",
 "flicker": "Modulation frequency of a light source",
 "image-visible": "A 2D visible-light image",
 "image-depth": "A 2D map of distances",
 # distance & space
 "distance-point": "Range to one target",
 "distance-field": "Range across many zones at once",
 "proximity": "Something is near, without a calibrated distance",
 "position-global": "Latitude/longitude on Earth",
 "position-relative": "Position relative to local anchors",
 "angle-absolute": "Absolute rotational position",
 "angle-relative": "Change in rotational position",
 "displacement-linear": "Linear travel along an axis",
 "tilt": "Orientation with respect to gravity",
 "heading": "Direction relative to magnetic north",
 # motion
 "acceleration": "Linear acceleration including gravity",
 "angular-rate": "Rate of rotation",
 "vibration": "Oscillatory mechanical energy, usually spectral",
 "shock-impact": "A single high-g event",
 "ground-motion": "Seismic velocity of the earth",
 "orientation-fused": "Full 3D attitude from fused sensors",
 # force
 "force": "Push or pull along an axis",
 "weight": "Force due to gravity on a mass",
 "strain": "Deformation of a structure under load",
 "torque": "Rotational force",
 "pressure-tactile": "Force distributed across a surface",
 "bend-angle": "Curvature of a flexible member",
 "stretch": "Elongation of a compliant material",
 # acoustic
 "sound-pressure": "Airborne acoustic pressure",
 "sound-structural": "Vibration travelling through a solid",
 "ultrasound": "Acoustic energy above human hearing",
 "sound-underwater": "Acoustic pressure in liquid",
 # electrical & magnetic
 "current-dc": "Direct current",
 "current-ac": "Alternating current",
 "voltage": "Electrical potential difference",
 "resistance": "Opposition to current flow",
 "capacitance": "Ability to store charge — changes with nearby matter",
 "inductance": "Magnetic coupling — changes with nearby metal",
 "impedance-bio": "Electrical impedance of tissue",
 "magnetic-field": "Magnetic flux density and direction",
 "electric-field": "Static or atmospheric electric field",
 "energy-accumulated": "Integrated power over time (kWh, coulombs)",
 # chemical
 "gas-concentration": "Concentration of a specific gas",
 "voc-index": "Aggregate volatile organic compound level",
 "co2-concentration": "Carbon dioxide concentration",
 "particulate-mass": "Mass of suspended particles per volume",
 "particulate-count": "Number of particles by size bin",
 "ph": "Hydrogen ion activity in a liquid",
 "conductivity-liquid": "Ionic conductivity — dissolved solids",
 "redox-potential": "Oxidation-reduction potential",
 "dissolved-oxygen": "Oxygen dissolved in water",
 "turbidity": "Cloudiness from suspended particles",
 "ion-specific": "Concentration of one specific ion",
 "dielectric-constant": "Permittivity — reveals material and moisture",
 # biological
 "ppg-optical": "Blood volume pulse via light absorption",
 "biopotential-ecg": "Electrical activity of the heart",
 "biopotential-emg": "Electrical activity of muscle",
 "biopotential-eog": "Electrical activity from eye movement",
 "skin-conductance": "Electrodermal activity — sympathetic arousal",
 "respiration": "Breathing movement or airflow",
 "fingerprint-pattern": "Ridge pattern of a finger",
 # RF & nuclear
 "rf-power": "Radio-frequency field strength",
 "rf-channel-state": "How a radio channel is distorted by the environment",
 "rf-backscatter": "Reflected identity from a passive tag",
 "radio-time": "Precise time from a radio source",
 "ionising-radiation": "Alpha, beta, gamma or cosmic particles",
 "gamma-spectrum": "Energy distribution of gamma photons",
 "radon-concentration": "Radon gas activity in air",
 # aggregate / derived-at-source
 "lightning-event": "Electromagnetic signature of a lightning discharge",
 "rainfall": "Depth of precipitation",
 "wind-speed": "Speed of air over ground",
 "wind-direction": "Bearing the wind comes from",
 "solar-irradiance": "Total solar power per area",
 "occupancy-signal": "A processed presence/target output from a smart module",
 "identity-token": "A unique identifier presented by a tag or credential",
 "object-class": "A classification produced on-module by a vision/AI sensor",
}

# --------------------------------------------------------------------------- inferences
# What you can KNOW. This is the reverse index that makes the document an
# invention tool rather than a parts list. Grouped by domain.
#   key -> (question a human would ask, domain)
INFERENCE = {
 # --- human presence & state
 "someone-present": ("Is anyone here?", "Human presence"),
 "someone-still-present": ("Is someone still here, sitting perfectly still?", "Human presence"),
 "how-many-people": ("How many people are in this space?", "Human presence"),
 "where-in-room": ("Whereabouts in the room are they?", "Human presence"),
 "entered-or-left": ("Did they come in, or go out?", "Human presence"),
 "who-is-it": ("Which specific person is this?", "Human presence"),
 "are-they-looking": ("Is someone actually looking at this?", "Human presence"),
 "person-fell": ("Did someone fall?", "Human presence"),
 "person-asleep": ("Are they asleep, and how well?", "Human presence"),
 "no-movement-alarm": ("Has nobody moved for worryingly long?", "Human presence"),
 "routine-broken": ("Has this person's daily routine changed?", "Human presence"),
 "occupancy-duration": ("How long has this desk/room/seat been in use?", "Human presence"),
 "queue-length": ("How many are waiting, and for how long?", "Human presence"),
 "crossed-boundary": ("Did something cross this line?", "Human presence"),
 # --- body & health
 "heart-rate": ("What is the heart rate?", "Body & health"),
 "heart-variability": ("How stressed or recovered is this body?", "Body & health"),
 "blood-oxygen": ("What is the blood oxygen saturation?", "Body & health"),
 "breathing-rate": ("How fast are they breathing?", "Body & health"),
 "breathing-stopped": ("Has breathing become irregular or stopped?", "Body & health"),
 "body-temp-trend": ("Is body temperature drifting — fever, ovulation, heat stress?", "Body & health"),
 "muscle-effort": ("Which muscle is working, and how hard?", "Body & health"),
 "joint-angle": ("What angle is this joint at, through its range?", "Body & health"),
 "gait-quality": ("How is this person walking?", "Body & health"),
 "tremor-present": ("Is there a tremor, and at what frequency?", "Body & health"),
 "posture": ("What posture is this body in?", "Body & health"),
 "hydration-proxy": ("Are they likely dehydrated?", "Body & health"),
 "stress-arousal": ("Is this person's arousal or stress rising?", "Body & health"),
 "blink-or-eye-move": ("Did they blink or move their eyes?", "Body & health"),
 "step-count": ("How much have they moved today?", "Body & health"),
 "sleep-stage-proxy": ("What sleep stage is this, roughly?", "Body & health"),
 # --- objects & assets
 "object-present": ("Is the thing there?", "Objects & assets"),
 "object-identity": ("Which specific object is this?", "Objects & assets"),
 "object-moved": ("Has it been moved or disturbed?", "Objects & assets"),
 "object-dropped": ("Was it dropped, and how hard?", "Objects & assets"),
 "object-count": ("How many went past?", "Objects & assets"),
 "container-fullness": ("How full is it?", "Objects & assets"),
 "consumable-remaining": ("How much is left, and how long until it runs out?", "Objects & assets"),
 "door-state": ("Is it open or closed?", "Objects & assets"),
 "object-material": ("What is this made of?", "Objects & assets"),
 "object-genuine": ("Is this authentic or counterfeit?", "Objects & assets"),
 "object-temperature": ("How hot is that surface?", "Objects & assets"),
 "asset-location": ("Where is this thing right now?", "Objects & assets"),
 "tamper-detected": ("Has someone interfered with it?", "Objects & assets"),
 # --- machine health
 "machine-running": ("Is it on?", "Machine health"),
 "machine-state": ("Is it idle, loaded, or jammed?", "Machine health"),
 "machine-duty-cycle": ("How much is this machine actually used?", "Machine health"),
 "bearing-failing": ("Is a bearing starting to fail?", "Machine health"),
 "imbalance": ("Is it out of balance or misaligned?", "Machine health"),
 "overheating": ("Is something running hotter than it should?", "Machine health"),
 "belt-slipping": ("Is the belt or coupling slipping?", "Machine health"),
 "filter-clogged": ("Is the filter blocked?", "Machine health"),
 "air-leak": ("Is compressed air leaking, and where?", "Machine health"),
 "abnormal-current": ("Is it drawing an abnormal amount of power?", "Machine health"),
 "drift-from-baseline": ("Has this drifted from how it behaved when new?", "Machine health"),
 "arc-or-discharge": ("Is there electrical arcing or partial discharge?", "Machine health"),
 "lubrication-failing": ("Is lubrication breaking down?", "Machine health"),
 "rotation-speed": ("How fast is it turning?", "Machine health"),
 "cycle-complete": ("Has the cycle finished?", "Machine health"),
 # --- air & environment
 "air-stuffy": ("Is this room stuffy — does it need fresh air?", "Air & environment"),
 "ventilation-adequate": ("Is ventilation actually working?", "Air & environment"),
 "smoke-present": ("Is there smoke?", "Air & environment"),
 "gas-leak": ("Is there a flammable gas leak?", "Air & environment"),
 "co-present": ("Is there carbon monoxide?", "Air & environment"),
 "voc-event": ("Did something start off-gassing or smelling?", "Air & environment"),
 "particulate-level": ("How polluted is the air right now?", "Air & environment"),
 "mould-risk": ("Is this surface going to grow mould?", "Air & environment"),
 "too-dry": ("Is the air dry enough to damage wood, skin or instruments?", "Air & environment"),
 "radon-level": ("Is radon accumulating?", "Air & environment"),
 "ozone-present": ("Is something emitting ozone?", "Air & environment"),
 "formaldehyde-level": ("Is new furniture or flooring off-gassing?", "Air & environment"),
 "cooking-detected": ("Is someone cooking?", "Air & environment"),
 "smell-signature": ("What does this smell like — which known smell is it?", "Air & environment"),
 # --- weather & outdoors
 "is-raining": ("Is it raining, and how hard?", "Weather & outdoors"),
 "wind-conditions": ("How windy is it, and from where?", "Weather & outdoors"),
 "storm-approaching": ("Is a storm coming?", "Weather & outdoors"),
 "lightning-distance": ("How far away is the lightning?", "Weather & outdoors"),
 "frost-tonight": ("Will there be frost tonight?", "Weather & outdoors"),
 "snow-depth": ("How deep is the snow?", "Weather & outdoors"),
 "solar-resource": ("How much solar energy is available?", "Weather & outdoors"),
 "uv-exposure": ("How much UV have I accumulated today?", "Weather & outdoors"),
 "sky-clear": ("Is the sky clear or clouded?", "Weather & outdoors"),
 "flood-rising": ("Is water rising, and how fast?", "Weather & outdoors"),
 "heat-island": ("How much hotter is this spot than the next street?", "Weather & outdoors"),
 # --- water
 "water-leak": ("Is water escaping where it shouldn't?", "Water"),
 "tank-level": ("How much is in the tank?", "Water"),
 "flow-rate": ("How fast is water flowing?", "Water"),
 "water-used-total": ("How much water was used, by whom, and when?", "Water"),
 "pump-dry": ("Is the pump about to run dry?", "Water"),
 "water-ph": ("Is the water too acidic or alkaline?", "Water"),
 "water-nutrients": ("How concentrated is the nutrient solution?", "Water"),
 "water-sanitised": ("Is the sanitiser actually working?", "Water"),
 "water-oxygen": ("Is there enough oxygen for fish or microbes?", "Water"),
 "water-clarity": ("Is the water cloudy — sediment, algae, runoff?", "Water"),
 "water-hot-enough": ("Is the water at the right temperature?", "Water"),
 "thermal-energy-moved": ("How much heat did this water actually carry?", "Water"),
 # --- plants & soil
 "plant-thirsty": ("Does this plant need water?", "Plants & soil"),
 "soil-tension": ("How hard must roots work to get water?", "Plants & soil"),
 "soil-fertility": ("What is the nutrient status of this soil?", "Plants & soil"),
 "soil-ready-to-plant": ("Is the soil warm enough to sow?", "Plants & soil"),
 "disease-pressure": ("Are conditions right for fungal disease?", "Plants & soil"),
 "growth-rate": ("How fast is it growing?", "Plants & soil"),
 "fruit-ripe": ("Is it ripe?", "Plants & soil"),
 "light-dose-daily": ("Has this plant had enough light today?", "Plants & soil"),
 "compost-active": ("Is the compost heating properly — or dangerously?", "Plants & soil"),
 "hive-state": ("What is the beehive doing?", "Plants & soil"),
 "livestock-wellbeing": ("Are the animals comfortable and behaving normally?", "Plants & soil"),
 # --- energy
 "power-now": ("How much power is being used right now?", "Energy"),
 "which-appliance": ("Which appliance just turned on?", "Energy"),
 "phantom-load": ("What is draining power while doing nothing?", "Energy"),
 "solar-performance": ("Is the solar array performing as it should?", "Energy"),
 "battery-charge": ("How much charge is left?", "Energy"),
 "battery-health": ("Is this battery degrading?", "Energy"),
 "energy-cost": ("What did that actually cost to run?", "Energy"),
 "power-quality": ("Is the supply voltage clean and stable?", "Energy"),
 "device-left-on": ("Did someone leave it switched on?", "Energy"),
 "energy-budget-node": ("Will this node survive on its battery until spring?", "Energy"),
 # --- security & safety
 "intrusion": ("Has someone entered who shouldn't have?", "Security & safety"),
 "glass-broken": ("Did glass break?", "Security & safety"),
 "vehicle-approaching": ("Is a vehicle arriving?", "Security & safety"),
 "vehicle-speed": ("How fast are vehicles going past?", "Security & safety"),
 "fire-present": ("Is there a flame?", "Security & safety"),
 "unusual-sound": ("Did something sound wrong?", "Security & safety"),
 "perimeter-crossed": ("Was the boundary crossed, and where along it?", "Security & safety"),
 "stove-left-on": ("Was the hob left on with nobody there?", "Security & safety"),
 "authorised-to-use": ("Is this person allowed to operate this?", "Security & safety"),
 # --- navigation & space
 "where-am-i": ("Where am I on Earth?", "Navigation & space"),
 "which-way-facing": ("Which way am I pointing?", "Navigation & space"),
 "how-far-travelled": ("How far have I gone?", "Navigation & space"),
 "how-fast-moving": ("How fast am I moving?", "Navigation & space"),
 "am-i-level": ("Is this level, and by how much is it off?", "Navigation & space"),
 "how-high": ("What altitude or floor am I on?", "Navigation & space"),
 "map-surroundings": ("What is the shape of the space around me?", "Navigation & space"),
 "obstacle-ahead": ("Is there something in the way?", "Navigation & space"),
 "returned-to-spot": ("Am I back at the exact same place?", "Navigation & space"),
 "structure-moved": ("Has this structure shifted or tilted since last time?", "Navigation & space"),
 # --- materials & chemistry
 "material-type": ("What material is this?", "Materials & chemistry"),
 "moisture-content": ("How wet is this material?", "Materials & chemistry"),
 "food-fresh": ("Is this food still good?", "Materials & chemistry"),
 "colour-match": ("Does this colour match the reference?", "Materials & chemistry"),
 "concentration-liquid": ("How concentrated is this solution?", "Materials & chemistry"),
 "contamination": ("Has this been contaminated?", "Materials & chemistry"),
 "coating-cured": ("Has the paint, resin or glue finished curing?", "Materials & chemistry"),
 # --- invisible worlds
 "radiation-dose": ("How much radiation is here?", "Invisible worlds"),
 "which-isotope": ("Which radioactive isotope is this?", "Invisible worlds"),
 "rf-activity": ("What is transmitting nearby, and how strongly?", "Invisible worlds"),
 "hidden-wiring": ("Where is the wiring or metal inside this wall?", "Invisible worlds"),
 "magnetic-anomaly": ("Is there ferrous metal or a field distortion here?", "Invisible worlds"),
 "cosmic-flux": ("How many cosmic rays are passing through?", "Invisible worlds"),
 "ultrasonic-activity": ("What is making noise above human hearing?", "Invisible worlds"),
 "atmospheric-charge": ("Is the atmosphere electrically charged?", "Invisible worlds"),
 "through-wall-motion": ("Is something moving on the other side of that wall?", "Invisible worlds"),
}

INFERENCE_DOMAINS = []
for _k, (_q, _d) in INFERENCE.items():
    if _d not in INFERENCE_DOMAINS:
        INFERENCE_DOMAINS.append(_d)

# --------------------------------------------------------------------------- constraints
# Constraints generate inventions more reliably than open brainstorming.
#   key -> (the constraint as a designer states it, how to satisfy it)
CONSTRAINT = {
 "no-touch":     ("I can't touch or contaminate the thing",
                  "contact in {Through-barrier, Standoff, Remote}"),
 "through-wall": ("It's sealed inside something I can't open",
                  "contact == Through-barrier"),
 "no-power":     ("There is no mains power and I can't change batteries often",
                  "power_class in {Zero, Nanoamp, Microamp}"),
 "no-privacy":   ("It must not capture anything identifiable",
                  "privacy in {None, Aggregate}"),
 "invisible":    ("Nobody should see any hardware",
                  "small, hideable, or sensing through the surface it hides behind"),
 "underwater":   ("It has to work wet or submerged",
                  "environment includes Submersible"),
 "outdoors":     ("It has to survive weather for years",
                  "environment includes Outdoor, with an IP rating"),
 "cheap":        ("Under $5 per node because I need a lot of them",
                  "usd < 5"),
 "beginner":     ("I want it working this weekend",
                  "diff <= 2 and maturity in {Excellent, Good}"),
 "fast":         ("I need high sample rates, not one reading a second",
                  "rate in the kHz range"),
 "tiny":         ("It has to fit in something small and wearable",
                  "small package, low pin count, µA power"),
 "harsh":        ("Dust, vibration, chemicals, temperature extremes",
                  "environment includes Harsh"),
 "no-calibration":("I can't be recalibrating this forever",
                  "calibration in {None, One-point} and no consumables"),
 "safe-for-life":("Someone's safety depends on it",
                  "certified device required — hobby parts supplement, never replace"),
 "long-range":   ("The thing I'm sensing is far away",
                  "contact == Remote, or a radio link to a local sensor"),
 "no-line-of-sight": ("I can't see the target from where the sensor can go",
                  "RF, magnetic, acoustic or vibration paths instead of optical"),
}

# --------------------------------------------------------------------------- fusion grammar
# Eight named, generative patterns for combining sensors. The creative engine.
#   key -> (name, what it does, why it works, worked example)
FUSION = {
 "complementary": ("Complementary",
   "One sensor is fast but forgetful, the other slow but persistent — use both.",
   "Different sensors fail in different directions; pairing covers both failure modes.",
   "PIR fires instantly on entry but goes blind when you sit still; mmWave holds presence "
   "but reacts slower. Together: instant lights that never strand you in the dark."),
 "cross-validation": ("Cross-validation",
   "Require two independent modalities to agree before acting.",
   "Uncorrelated sensors rarely produce the same false positive at the same instant.",
   "Field testing found PIR alone produced 39 false triggers across 40 real events; "
   "requiring an ultrasonic distance confirmation eliminated all of them."),
 "compensation": ("Compensation",
   "One sensor corrects a known error in another.",
   "Most cheap sensors have a documented cross-sensitivity you can measure and subtract.",
   "Gas and VOC sensors drift with humidity and temperature; optical PM sensors over-read "
   "above ~75% RH; ultrasonic ranging shifts with air temperature. Add the cheap sensor "
   "that measures the thing corrupting your reading."),
 "context-gating": ("Context gating",
   "Only act when several unrelated conditions are simultaneously true.",
   "Most false alarms are true readings in the wrong context.",
   "Turn on the stair lights only if: motion AND dark AND after 22:00 AND nobody already "
   "downstairs. Four cheap signals beat one expensive one."),
 "differential": ("Differential",
   "Deploy two identical sensors; the difference between them is the signal.",
   "Identical parts share identical drift and calibration error, which cancels in the difference.",
   "Indoor and outdoor BME280s: neither absolute reading matters, but the gradient tells you "
   "whether opening the window will actually help. Same trick across a filter, a wall, a "
   "heat exchanger, or before/after a water filter."),
 "triangulation": ("Triangulation",
   "Use N copies of one sensor, spaced apart, to recover position or direction.",
   "Time or amplitude differences between spaced sensors encode geometry.",
   "Two ToF zones in a doorway give direction of travel. Three time-synced microphones "
   "locate a sound by time-difference-of-arrival. Two ranging strips give vehicle speed."),
 "temporal": ("Temporal",
   "One sensor plus time. Compare against its own history rather than an absolute threshold.",
   "Baselines make cheap, uncalibrated sensors useful — you stop needing absolute accuracy.",
   "The cheapest superpower in this document. A $1 vibration sensor whose daily average is "
   "creeping upward is a bearing wearing out. Weight-over-time is a depletion curve. "
   "Moisture decay rate is a plant's drinking speed and reveals illness before wilting."),
 "fleet": ("Fleet",
   "One sensor multiplied across many nodes becomes a map.",
   "Spatial structure is invisible from a single point and obvious from ten.",
   "Ten $2 temperature nodes reveal which rooms drift coldest and why. Street-level PM "
   "nodes reveal a heat island or a polluting neighbour. ESP-NOW makes the mesh nearly free."),
 "active-probe": ("Active probe",
   "Emit a known stimulus and read the response — sensor plus actuator become one instrument.",
   "A response to a stimulus YOU control carries information no passive reading can: the "
   "system's transfer function, not just its state.",
   "A speaker chirps at a jar and a mic finds the Helmholtz resonance: fill level through "
   "the wall. A resistor pulses heat into a thermistor bead: the cooling curve identifies "
   "the liquid around it. A ranging ping at a FIXED distance: the flight time reads air "
   "temperature. The Combination Grammar's Active Interrogation family, as a fusion kind."),
}

# --------------------------------------------------------------------------- physical quantities
# PHYSQTY — the controlled vocabulary for the physics layer's cross-sensitivity
# field (`px_cross` in schema.FIELDS, kind `vocablist:PHYSQTY`). These are the
# quantities that ALSO move a sensor's output and are normally dismissed as
# noise; naming them is how the atlas records what actually fools a transducer.
#
# Deliberately physical, like PHENOMENON, but read from the other direction:
# PHENOMENON is what a part is FOR, PHYSQTY is what it cannot help responding to.
#
# TO EXTEND: append the new token to the list below, inside its physical group
# (or start a new group with a comment). Tokens are lowercase-hyphenated, one
# quantity each, no application-level words. Nothing else needs changing — the
# validator resolves `vocablist:PHYSQTY` through getattr(vocab, "PHYSQTY"), so a
# token is legal the moment it appears here.
PHYSQTY = [
    # thermal
    "temperature",
    "temperature-of-electronics",
    "self-heating",
    "thermal-gradient",
    # moisture
    "humidity",
    "condensation",
    "water-vapour",
    # fluid / atmosphere
    "pressure",
    "altitude",
    "airflow",
    "wind",
    # chemistry
    "gas-composition",
    "co2",
    "voc",
    "oxygen",
    "ph",
    "salinity-conductivity",
    "contamination-poisoning",
    "dust-fouling",
    "aerosol-size-distribution",
    # radiant
    "ambient-light",
    "light-flicker",
    "sunlight-load",
    "ir-radiation",
    "uv-radiation",
    "surface-emissivity",
    "target-reflectivity",
    "target-colour",
    "target-geometry",
    "multipath",
    # electromagnetic
    "magnetic-field",
    "electric-field",
    "emi-rf",
    "ionizing-radiation",
    # electrical front-end
    "supply-voltage",
    "ground-noise",
    "reference-drift",
    "contact-resistance",
    "cable-capacitance",
    "body-capacitance",
    # mechanical
    "mechanical-stress",
    "vibration",
    "acoustic-noise",
    "orientation-gravity",
    "acceleration",
    "rotation",
    "soil-density",
    "precipitation",
    # time
    "aging-drift",
    "hysteresis",
    "creep",
    "clock-drift",
]
