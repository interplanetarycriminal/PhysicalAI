"""Physics Cheatsheet — the small set of ideas that generate every sensor.

Written to build INTUITION rather than to store formulas. The organising claim:

    There are only six kinds of energy, and every sensor is a door between two
    of them. Learn the doors and you can derive any sensor — including ones
    nobody has built.

Each idea carries a mnemonic short enough to memorise and true enough to reason
with. Where a mnemonic is a simplification, the entry says where it breaks,
because a mnemonic you cannot falsify is a superstition.
"""

# ---------------------------------------------------------------- the one idea

THE_ONE_IDEA = [
 ("What a sensor actually is",
  "A sensor is an energy converter with a small leak. Something in the world carries or modulates "
  "energy; the sensor lets a tiny, proportional amount of it cross into electrical form, where you "
  "can count it. That is the entire field. Everything else — packaging, calibration, protocols — is "
  "engineering around that one act of conversion."),
 ("Why this matters more than memorising parts",
  "A catalogue of 482 parts is a list of doors other people happened to build. The six energy "
  "domains and the effects that connect them are the WALL PLAN. Once you can see the plan, a part "
  "you have never met is obvious in ten seconds, and a door nobody has built yet becomes visible."),
 ("The six domains",
  "MECHANICAL (force, motion, pressure, strain) · THERMAL (heat, temperature) · ELECTRICAL (charge, "
  "current, field) · MAGNETIC (flux) · RADIANT (light, IR, RF, gamma — all electromagnetic waves) · "
  "CHEMICAL (concentration, reaction, ion activity). Some people add NUCLEAR. That is the whole "
  "inventory of what the universe can hand you."),
 ("The generative move",
  "Any ordered pair of domains is a potential transducer, so six domains give thirty-six doors. "
  "Most have a named effect and a part number. A few are wide open. When you want to sense "
  "something, ask: what domain is it in, and which door leads from there to electrical?"),
]

MNEMONIC_PRIME = "Six domains, thirty-six doors. Every sensor is one door; every clever sensor is two."

# ---------------------------------------------------------------- transduction grid
# (from_domain, to_domain, effect name, plain explanation, example from this catalog)
TRANSDUCTION = [
 ("Mechanical", "Electrical", "Piezoelectric",
  "Squeezing certain crystals pushes their charges out of balance, so force becomes voltage directly. "
  "Fast, sensitive, and it needs no power at all — the crystal is the battery.",
  "Piezo disc · knock sensors · hydrophones · acoustic emission"),
 ("Mechanical", "Electrical", "Piezoresistive",
  "Stretching a conductor makes it longer and thinner, so its resistance rises. The change is tiny "
  "(a strain gauge shifts ~0.2% at heavy load), which is why bridges and 24-bit amplifiers exist.",
  "Load cells · strain gauges · MEMS pressure sensors · BMP390"),
 ("Mechanical", "Electrical", "Capacitive",
  "Move one plate of a capacitor and its capacitance changes. Silent, driftless, no contact needed, "
  "and it works through plastic — which is why MEMS accelerometers and touch buttons both use it.",
  "MEMS accelerometers · capacitive touch · FDC1004 level sensing"),
 ("Mechanical", "Electrical", "Inductive / LVDT",
  "Moving metal near a coil changes the coil's inductance. Immune to oil, dust and light, which is "
  "why factories use it where optics would die.",
  "LJ12A3 proximity switch · LDC1612 · linear variable differential transformers"),
 ("Thermal", "Electrical", "Seebeck effect",
  "Join two dissimilar metals and a temperature difference across the junction produces a voltage — "
  "about 41 microvolts per °C for type K. Minuscule, but it needs no excitation and survives 1300°C.",
  "Thermocouples · MAX31855 · thermopiles inside every IR thermometer"),
 ("Thermal", "Electrical", "Thermoresistive",
  "Resistance changes with temperature: platinum does it linearly (RTD), semiconductors do it "
  "steeply and non-linearly (thermistor). Linear and dull, or sensitive and awkward — pick one.",
  "PT100 + MAX31865 · NTC thermistors · MEMS hotplates"),
 ("Thermal", "Electrical", "Pyroelectric",
  "Some crystals produce charge when their temperature CHANGES — not when it is high. That is "
  "exactly why a PIR sees you walk past and goes blind when you sit still.",
  "HC-SR501 and every PIR sensor ever made"),
 ("Radiant", "Electrical", "Photoelectric / photovoltaic",
  "A photon with enough energy knocks an electron free. Above the material's threshold you get "
  "current proportional to light; below it, nothing at all — which is why band gap decides colour.",
  "Photodiodes · solar cells · VEML7700 · camera sensors"),
 ("Radiant", "Thermal", "Absorption",
  "Anything that absorbs radiation warms up. This is the universal back door: when there is no "
  "direct photoelectric route — far infrared, terahertz — absorb the radiation and measure the heat.",
  "Thermopile IR thermometers · MLX90640 · microbolometers · FLIR Lepton"),
 ("Thermal", "Radiant", "Blackbody emission",
  "Everything above absolute zero radiates, and both how MUCH and what COLOUR depend only on "
  "temperature. Power goes as T⁴, and peak wavelength as 1/T. This is why you can read temperature "
  "from across a room without touching anything.",
  "MLX90614 · all non-contact thermometry · thermal imaging"),
 ("Magnetic", "Electrical", "Hall effect",
  "A magnetic field pushes moving charges sideways in a conductor, producing a voltage across it. "
  "Cheap, solid-state, and it senses through any non-magnetic barrier.",
  "A3144 switches · ACS712 current sensing · QMC5883L compass · AS5600"),
 ("Magnetic", "Electrical", "Induction (Faraday)",
  "A CHANGING magnetic field drives current in a loop. Note 'changing': a coil is blind to a "
  "stationary magnet, which is why induction reads speed and Hall reads position.",
  "Geophones · CT clamps · Rogowski coils · RFID · wireless charging"),
 ("Chemical", "Electrical", "Electrochemical",
  "A target species reacts at an electrode and the reaction's electrons ARE the signal — current "
  "proportional to concentration. Selective and quantitative, but the electrode is consumed.",
  "CO and O₂ cells · pH glass electrodes · dissolved oxygen probes"),
 ("Chemical", "Electrical", "Chemiresistive (MOX)",
  "Gas molecules react on a hot metal-oxide surface and change its conductivity. Cheap and "
  "sensitive; also cross-sensitive to nearly everything, which is the whole story of MQ sensors.",
  "MQ family · SGP40 · BME688 · ENS160"),
 ("Chemical", "Thermal", "Catalytic combustion",
  "Burn the target gas on a catalyst and measure the heat released. Combustible gases only, but it "
  "responds to the property you actually care about: flammability.",
  "Pellistor combustible-gas detectors"),
 ("Radiant", "Mechanical", "Photoacoustic",
  "Pulse light into a sealed gas cell; the gas absorbs, warms, expands and makes a pressure wave a "
  "microphone can hear. Radiant → thermal → mechanical → electrical, four domains in one chip.",
  "SCD41 photoacoustic CO₂ sensor"),
 ("Mechanical", "Thermal", "Convective cooling",
  "Moving fluid carries heat away from a warm body faster than still fluid. Heat something, hold "
  "the power constant, and its temperature drop measures flow.",
  "Hot-wire anemometers · FS3000 · thermal mass flow · SDP810"),
 ("Electrical", "Thermal", "Joule heating / Peltier",
  "Current through resistance makes heat; current through a thermoelectric junction MOVES heat. "
  "The second one is reversible, which makes it both a cooler and a generator.",
  "Heaters · sensor hotplates · TEC1-12706 Peltier modules"),
 ("Thermal", "Mechanical", "Thermal expansion",
  "Materials grow with temperature at different rates. Bond two together and the strip bends — the "
  "original thermostat, and still the failsafe in every heater you should be building.",
  "Bimetallic thermal cutouts · shape-memory alloy actuators"),
 ("Electrical", "Radiant", "Electroluminescence",
  "Electrons dropping across a semiconductor band gap emit photons of a specific colour. Run the "
  "same junction backwards and it detects that colour — an LED is a photodiode with ambitions.",
  "LEDs · lasers · IR emitters · and LED-as-detector tricks"),
 ("Radiant", "Chemical", "Photochemistry",
  "Photons drive reactions: photosynthesis, UV curing, ozone generation, photoresist. Mostly an "
  "actuator domain, but fluorescence runs it in reverse and is how optical DO probes work.",
  "UV curing · optical dissolved-oxygen probes · fluorescence sensing"),
 ("Nuclear", "Electrical", "Ionisation / avalanche",
  "One energetic particle rips electrons from atoms; a strong field multiplies that into a "
  "measurable pulse. A single subatomic event becomes a click you can count.",
  "Geiger tubes · SiPM detectors · PIN photodiode particle detection"),
]

MNEMONIC_GRID = ("When there is no direct door, go through HEAT. Everything talks to thermal — "
                 "which is why absorb-then-measure-the-warming is the most reused trick in sensing.")

# ---------------------------------------------------------------- the moves
# (mnemonic, what it means, why it works, where you already saw it, what it invents, where it breaks)
MOVES = [
 ("Anything you can heat and measure becomes a flow sensor on the way down.",
  "Put power into something, watch how fast it cools. Moving fluid steals heat faster than still "
  "fluid, so the cooling rate IS the flow rate.",
  "Convective heat transfer scales with fluid velocity. Hold the heating power constant and "
  "temperature drop maps to flow; or hold temperature constant and the power needed maps to flow.",
  "Hot-wire anemometers, FS3000 air velocity, thermal mass flow meters, SDP810 differential pressure",
  "Any warm thing you already have becomes a flow sensor for free. A self-heating thermistor in a "
  "pipe. A resistor on a PCB in an airflow. Even an LED run hot. You do not need to buy a flow "
  "sensor — you need to notice that you already own one.",
  "Fails when ambient temperature drifts, because you are measuring a difference. Always measure "
  "ambient too, or heat in pulses and look only at the decay slope."),

 ("If it changes resistance, it is already a sensor — add one resistor.",
  "A voltage divider converts any resistance change into a voltage your ADC can read. Two "
  "components, no chip, no protocol.",
  "V_out = V_in × R_sensor / (R_sensor + R_fixed). Sensitivity peaks when the fixed resistor "
  "roughly equals the sensor's resistance in the range you care about — which is the one design "
  "decision people skip.",
  "Thermistors, photoresistors, flex sensors, FSRs, soil probes, gas sensors, potentiometers",
  "Any material whose resistance responds to anything becomes an instrument. Conductive thread, "
  "graphite pencil on paper, a wet sponge, your own skin. The material IS the sensor; the resistor "
  "just makes it legible.",
  "Ratiometric only: if the supply sags, the reading moves. Read against the same reference that "
  "excites the divider and the error cancels exactly."),

 ("Know the speed and timing becomes a ruler.",
  "If a signal travels at a known speed, measuring time gives you distance. Nothing else is needed.",
  "Sound in air: 343 m/s, so 1 ms of round trip is 17 cm of distance. Light: 30 cm per nanosecond, "
  "so measuring distance optically means measuring picoseconds — which is why laser ToF chips are "
  "clever and ultrasonic ones are cheap.",
  "HC-SR04, VL53L0X, LiDAR, UWB ranging, GNSS, radar, seismic surveying",
  "Anything with a known propagation speed becomes a ruler: sound through a pipe wall reveals its "
  "thickness, through soil reveals a buried object, through water reveals depth. Time-of-flight in "
  "an unusual medium is a wide-open invention space.",
  "The speed is never constant. Sound changes 0.6% per 10°C. Light slows in glass and water. "
  "Uncompensated ToF drifts with the weather."),

 ("Anything that rings, rings differently when loaded.",
  "Excite a resonator and measure its frequency. Add mass, stiffness or damping and the frequency "
  "shifts. Frequency is the easiest thing in the world to measure precisely.",
  "f ∝ √(stiffness/mass). Because you are measuring frequency rather than amplitude, this is "
  "immune to gain drift — the reason resonant sensors are extraordinarily stable.",
  "Quartz crystal microbalances, MEMS gyroscopes, tuning-fork density meters, vibrating-fork level "
  "switches, guitar tuners",
  "Deposit anything onto a resonator and you can weigh it in nanograms. A coated crystal becomes a "
  "specific chemical sensor. A resonating tube becomes a fluid density meter. This is how you "
  "measure things too small to weigh.",
  "Temperature shifts stiffness, so every resonant sensor needs temperature compensation. Damping "
  "from a viscous or wet environment can kill the resonance entirely."),

 ("Two identical sensors cancel everything except the difference.",
  "Deploy the same part twice and subtract. Whatever they share — drift, temperature, supply noise, "
  "ageing — vanishes. What remains is the signal you actually wanted.",
  "Common-mode rejection. Identical parts drift identically, so the difference is far more stable "
  "than either absolute reading. This is why the Wheatstone bridge has survived since 1833.",
  "Strain-gauge bridges, differential pressure, indoor/outdoor climate pairs, differential ADC "
  "inputs, instrumentation amplifiers",
  "Any measurement you cannot make absolutely, you can often make differentially. Two BME280s "
  "either side of a window measure heat loss. Two microphones give direction. Two GNSS receivers "
  "give centimetres instead of metres. When absolute accuracy is hard, stop needing it.",
  "Only cancels what the two sensors genuinely share. Different self-heating, different airflow or "
  "different sun exposure break the symmetry and the error comes straight back."),

 ("Move your signal to where the noise isn't.",
  "Do not measure a slow, quiet signal in a noisy world. Chop it, modulate it to a chosen "
  "frequency, and detect only that frequency.",
  "Noise is worst near DC (1/f noise) and at mains frequency. Shift your measurement to a few kHz "
  "and the noise floor can drop by orders of magnitude. Lock-in detection then rejects everything "
  "that is not exactly your frequency AND phase.",
  "38 kHz IR remotes, photoelectric sensors that ignore sunlight, lock-in amplifiers, AC-excited "
  "soil probes, capacitive touch controllers",
  "Any sensor drowning in ambient interference can be rescued by modulation. This is how a 5-cent "
  "IR receiver ignores the sun. It is the single most underused technique in hobby electronics, "
  "and it costs nothing but a square wave.",
  "You must control the modulation and the detection together. And you cannot modulate faster than "
  "the physical process responds — a thermal sensor chopped at 1 kHz just sees the average."),

 ("Everything eats specific colours. The gaps are its name.",
  "Shine broadband light through or onto a sample and see which wavelengths go missing. The "
  "pattern of absorption identifies the substance.",
  "Molecules absorb photons whose energy matches a vibrational or electronic transition. Those "
  "energies are unique per molecule, so absorption spectra are fingerprints. CO₂ absorbs strongly "
  "at 4.26 µm; that single fact is the entire NDIR industry.",
  "NDIR CO₂ sensors, AS7341 and AS7265x spectral sensors, NIR moisture measurement, pulse oximetry",
  "Pick any molecule, look up its absorption band, find an emitter and detector at that wavelength, "
  "and you have designed a selective sensor for it. This is the most systematic route to inventing "
  "a chemical sensor that exists.",
  "Water absorbs broadly in the infrared and drowns weaker bands. Overlapping absorptions between "
  "species cause cross-sensitivity — the honest limit of cheap optical gas sensing."),

 ("Big things block, small things bend.",
  "Particles interact with light differently depending on how their size compares to the "
  "wavelength. Measure the scattering and you learn size as well as quantity.",
  "Particles much larger than the wavelength cast shadows (geometric). Particles comparable to it "
  "scatter forward strongly (Mie). Much smaller, and scattering goes as 1/λ⁴ (Rayleigh) — which is "
  "why the sky is blue and sunsets are red.",
  "PMS5003 and SPS30 particle counters, turbidity sensors, nephelometers, smoke detectors",
  "Angle-resolved scattering tells you far more than a single detector does. Two detectors at "
  "different angles distinguish particle populations — the difference between 'there is dust' and "
  "'this is pollen, not smoke'.",
  "Optical sizing assumes a refractive index and a density to convert counts to mass. Humid air "
  "makes particles swell, so every optical PM sensor over-reads above ~75% RH."),

 ("A changing field makes current; a current makes a field. Both directions are sensors.",
  "Electromagnetism is symmetric, so every magnetic effect can be run either way — as a detector or "
  "as an emitter.",
  "Faraday: a changing flux through a loop induces voltage. Ampère: current creates flux. A coil is "
  "therefore both an antenna and a transmitter, both a pickup and an actuator.",
  "CT clamps, geophones, RFID, wireless charging, metal detectors, fluxgate magnetometers",
  "A coil around any wire measures its current without touching it. A coil near any moving magnet "
  "measures motion without contact. Non-invasive measurement of electrical systems is nearly always "
  "a coil problem, and coils you can wind yourself.",
  "Induction only sees CHANGE. A coil cannot detect a stationary magnet or a DC current — that "
  "needs a Hall sensor or a fluxgate. Confusing the two wastes a lot of time."),

 ("Squeeze a crystal for volts; volt a crystal for squeeze.",
  "Piezoelectricity runs both ways in the same lump of material, so one part is both microphone and "
  "speaker, both sensor and actuator.",
  "Mechanical stress displaces charge in a non-centrosymmetric crystal, and an applied field "
  "displaces the lattice. The coupling is genuinely bidirectional and remarkably efficient.",
  "Piezo buzzers, ultrasonic transducers, knock sensors, inkjet heads, quartz oscillators",
  "One element can transmit and then listen — which is all sonar is. It also means every piezo "
  "buzzer in your parts bin is a free vibration sensor, and every ultrasonic transmitter is a "
  "receiver you already own.",
  "Piezos generate charge, not voltage, so what you read depends on the capacitance you connect — "
  "including your cable. Without a charge amplifier the same sensor gives different numbers on "
  "different rigs."),

 ("Capacitance is proximity sensing for matter itself.",
  "The capacitance between two conductors depends on what is in the space around them. Anything "
  "that changes that space changes the reading — without contact.",
  "C = εA/d. Change the area, the distance, or the dielectric constant of what is between, and "
  "capacitance changes. Water has a dielectric constant of ~80 against air's 1, which is why "
  "capacitive sensing is so good at finding water.",
  "Touch sensing, soil moisture, through-wall liquid level, FDC1004, MEMS accelerometers, "
  "stud finders",
  "You can sense the presence, level or moisture of almost anything through a non-conductive wall "
  "with two pieces of copper tape and no contact at all. Contamination-free measurement of "
  "chemicals, food and fuel is largely a capacitance problem.",
  "It responds to everything nearby including your hand, the bench and humidity in the air. Guard "
  "electrodes and a stable ground reference are not optional. Conductive surroundings ruin it."),

 ("Motion writes itself onto frequency.",
  "A wave reflected from something moving comes back at a shifted frequency. The shift is "
  "proportional to velocity.",
  "Doppler: Δf/f = v/c. Because it measures frequency rather than amplitude, it is indifferent to "
  "target size and reflectivity — it sees motion and only motion.",
  "mmWave presence radar, RCWL-0516, police radar, ultrasonic Doppler flow, laser vibrometry",
  "Doppler detects the micro-motion of a chest wall, which is how a $5 radar module senses "
  "breathing through a duvet. Any repetitive motion — machinery, blood, insects — has a Doppler "
  "signature, and most of them are unexplored.",
  "It sees only the component of motion ALONG the beam. Something moving perpendicular is "
  "invisible, which is why radar presence sensors miss people walking across their field."),

 ("Enough volts turns one particle into a spark you can count.",
  "A single ionising event releases a few electrons. Accelerate them hard enough and each one "
  "liberates more, until a subatomic event becomes a pulse you can hear.",
  "Townsend avalanche. A few hundred volts across a gas gives gas multiplication of 10⁶ or more. "
  "Silicon photomultipliers do the same trick in solid state at ~30 V.",
  "Geiger tubes, SiPM detectors, photomultipliers, avalanche photodiodes",
  "Amplification in the physics rather than in the electronics is what makes single-photon and "
  "single-particle detection possible at all. Whenever a signal is too small for any amplifier, ask "
  "whether the physics can be made to multiply it first.",
  "Avalanche gain is exponentially temperature and voltage dependent, so it needs compensation to "
  "mean anything quantitative. Geiger tubes lose all energy information — every particle gives an "
  "identical click, which is why they count but cannot identify."),

 ("Wait long enough and inside equals outside.",
  "Any probe reports its OWN state, not the world's. It only tells you about the world once it has "
  "come into equilibrium with it.",
  "Thermal time constant τ = mc/hA. A big probe in still air can take minutes; a bare bead in "
  "moving water takes a second. Gas sensors behind a membrane take longer still, and a humidity "
  "sensor in a sealed enclosure may take hours.",
  "Every temperature probe, every gas sensor, every soil probe, every humidity sensor",
  "You can turn a lag into a measurement. The RATE at which a probe equilibrates depends on the "
  "medium around it, so response time itself measures flow, thermal conductivity, or contact "
  "quality. The thing everyone treats as a nuisance is a signal.",
  "The most common measurement error in this entire catalogue is reading a sensor before it has "
  "settled. A thermocouple strapped to a pipe without insulation never equilibrates with the pipe "
  "at all — it reads a weighted average of pipe and room, forever."),
]

# ---------------------------------------------------------------- limits
LIMITS = [
 ("You cannot measure quieter than the universe.",
  "Johnson noise", "Every resistor generates noise just by being warm: about 4 nV/√Hz for 1 kΩ at "
  "room temperature. Shot noise adds more wherever current is quantised. A 24-bit ADC in front of a "
  "megohm resistor is not delivering 24 bits of anything.",
  "Lower the resistance, lower the temperature, or narrow the bandwidth. Those are the only three "
  "moves, and narrowing bandwidth is nearly always the cheapest."),
 ("Every hertz of bandwidth you don't need is noise you invited in.",
  "Bandwidth", "Noise power scales with bandwidth, so a sensor sampled at 1 kHz when you only care "
  "about 1 Hz is admitting a thousand times more noise than necessary.",
  "Filter first, then sample. A single RC filter before the ADC often beats any amount of software "
  "averaging — because averaging cannot remove noise that has already aliased into your band."),
 ("Sample twice as fast as the fastest thing that matters, or it lies to you.",
  "Nyquist", "Anything above half your sampling rate does not disappear — it folds back and "
  "masquerades as a lower frequency. A 60 Hz hum sampled at 100 Hz appears as a convincing, "
  "entirely fictitious 40 Hz signal.",
  "An analog anti-alias filter before the converter. Not after. Once aliased, the data is "
  "unrecoverable and looks perfectly plausible, which is what makes it dangerous."),
 ("Averaging N samples buys you √N. It never fixes a bias.",
  "Random vs systematic", "Averaging a hundred readings improves signal-to-noise by ten. Averaging "
  "a million readings of a sensor with a 2 °C offset gives you an exquisitely precise wrong answer.",
  "Random error yields to averaging; systematic error yields only to calibration. Knowing which one "
  "you have is the difference between a fixable problem and a fundamental one."),
 ("More digits is not more truth.",
  "Resolution ≠ accuracy", "Resolution is the smallest change you can SEE. Accuracy is how close "
  "you are to reality. A 24-bit converter reading a ±2 °C thermistor gives you 0.0001 °C resolution "
  "and ±2 °C accuracy.",
  "Quote both, always. And remember that repeatability — how consistent you are with yourself — is "
  "often what actually matters, and is usually much better than absolute accuracy."),
 ("Double the distance, quarter the signal.",
  "Inverse square", "Energy from a point source spreads over a sphere whose area grows as r². "
  "Light, sound, radio and radiation all obey it. Moving a sensor twice as far away costs you 75% "
  "of the signal.",
  "Get closer. It is almost always cheaper than better electronics. Alternatively use a lens, a "
  "horn or a dish — concentrators buy back distance for very little money."),
 ("You cannot measure without disturbing.",
  "Observer effect (the practical kind)", "A probe has mass and it conducts heat. A voltmeter draws "
  "current. A flow sensor obstructs the flow. A dissolved-oxygen probe consumes the oxygen it is "
  "measuring, which is why it reads low in still water.",
  "Make the sensor small relative to what it measures, or make the measurement non-contact. When "
  "neither is possible, model the disturbance and subtract it."),
 ("Hot things glow, and how they glow is their temperature.",
  "Stefan–Boltzmann and Wien", "Radiated power goes as T⁴, so a body at 600 K radiates sixteen "
  "times what it does at 300 K. Peak wavelength goes as 1/T: room-temperature objects peak near "
  "10 µm, which is precisely why thermal cameras work in the 8–14 µm band.",
  "This is the physics behind every non-contact thermometer. It also means a small hot spot can "
  "dominate a reading — a thermal camera pointed at a wall with one hot pipe reports mostly pipe."),
 ("Shiny things lie about their temperature.",
  "Emissivity", "Blackbody laws assume the object radiates perfectly. Real surfaces emit a "
  "fraction: matt black is ~0.95, oxidised steel ~0.8, polished aluminium as low as 0.05. A shiny "
  "surface radiates little and reflects its surroundings instead.",
  "The single most common error in thermal imaging: a bare copper busbar scans cool while being "
  "dangerously hot. Fix it with a square of matt tape or a dab of paint at a known emissivity."),
 ("Small things are all surface.",
  "Scaling", "Surface area goes as L² and volume as L³, so the surface-to-volume ratio goes as 1/L. "
  "Halve the size and you double the relative surface.",
  "This is why MEMS sensors heat and cool in milliseconds while a probe takes minutes; why insects "
  "breathe through their skin; why microfluidics is always laminar; and why a MEMS hotplate gas "
  "sensor uses milliwatts where an MQ bead uses nearly a watt."),
 ("Shrink it and it gets faster.",
  "Resonance scaling", "A cantilever's resonant frequency scales roughly as thickness over length "
  "squared. Making something ten times smaller makes it about a hundred times faster.",
  "Why MEMS gyroscopes resonate in the tens of kilohertz, why small tuning forks are higher pitched, "
  "and why miniaturisation buys speed for free rather than as a trade-off."),
]

# ---------------------------------------------------------------- anchors
# (quantity, value, why it is worth knowing by heart)
ANCHORS = [
 ("Speed of sound in air", "343 m/s at 20 °C (+0.6 m/s per °C)",
  "1 ms of echo = 17 cm of distance. Also: uncompensated ultrasonic ranging drifts ~0.6% per 10 °C."),
 ("Speed of sound in water", "~1480 m/s — over four times air",
  "Sound travels far in water with little loss, which is why one hydrophone hears further than any "
  "camera sees."),
 ("Speed of light", "30 cm per nanosecond",
  "Optical time-of-flight means timing picoseconds. UWB resolves ~15 ps, hence its ~5 mm precision."),
 ("Wavelength at 2.4 GHz", "12.5 cm (433 MHz ≈ 69 cm)",
  "Antenna size follows wavelength. It also explains why 2.4 GHz is absorbed by water and bodies, "
  "and why sub-GHz travels further through buildings."),
 ("Wavelength of 40 kHz ultrasound", "8.6 mm in air",
  "You cannot resolve detail finer than roughly a wavelength — the hard limit on ultrasonic imaging."),
 ("Peak thermal wavelength at room temperature", "~10 µm",
  "Why thermal cameras use the 8–14 µm band, and why ordinary glass — opaque there — blocks them."),
 ("Gravity", "9.81 m/s²",
  "An accelerometer at rest reads 1 g, not zero. Forgetting this is the most common IMU mistake."),
 ("Earth's magnetic field", "25–65 µT",
  "A fridge magnet is ~5 mT — a hundred times stronger. That is why a compass near any magnet, "
  "motor or speaker is useless."),
 ("K-type thermocouple output", "~41 µV per °C",
  "Microvolts. This is why thermocouples need a dedicated amplifier and why a bare ADC cannot read "
  "one."),
 ("Strain gauge sensitivity", "Gauge factor ~2: 1000 µε gives ~0.2% resistance change",
  "In a 5 V bridge that is about 2.5 mV. Load cells are microvolt instruments wearing steel jackets."),
 ("Human thermal output", "~100 W at rest, 37 °C core, ~1.8 m² skin",
  "A person is a 100 W heater. That is why occupancy is visible in temperature, CO₂ and IR alike."),
 ("Human exhaled CO₂", "~40,000 ppm against ~420 ppm outdoors",
  "One person raises a closed room's CO₂ measurably within minutes — the basis of every "
  "occupancy-by-CO₂ trick."),
 ("Full sunlight", "~1000 W/m², ~100,000 lux",
  "Office lighting is ~500 lux and moonlight ~0.1 lux. Six orders of magnitude, which is why light "
  "sensors quote logarithmic ranges."),
 ("Air properties", "1.2 kg/m³, specific heat ~1005 J/(kg·K)",
  "Heating a cubic metre of air by 1 °C takes about 1.2 kJ. Air holds almost no heat, which is why "
  "it responds fast and why water dominates any thermal system it is in."),
 ("Water specific heat", "4186 J/(kg·K) — 3500× air by volume",
  "Water is the thermal flywheel in nearly every system. It also means shower energy is large: "
  "kW = flow(L/s) × ΔT(K) × 4.186."),
 ("CR2032 coin cell", "~220 mAh at 3 V ≈ 0.66 Wh",
  "An ESP32 transmitting at 150 mA would flatten it in about ninety minutes. Coin cells are for "
  "microamp designs only."),
 ("18650 lithium cell", "~3000 mAh at 3.7 V ≈ 11 Wh",
  "Roughly sixteen coin cells. Also the reason a solar node's battery, not its panel, usually sets "
  "its winter survival."),
 ("ESP32 Wi-Fi transmit", "~150–260 mA in bursts",
  "The radio dominates every battery budget. Connection time matters more than transmit time, which "
  "is why ESP-NOW so often triples battery life."),
 ("Johnson noise of 1 kΩ", "~4 nV/√Hz at room temperature",
  "The floor beneath every voltage measurement. If your signal is nanovolts, no amplifier will save "
  "you — only cooling, lower resistance or less bandwidth."),
]

# ---------------------------------------------------------------- reciprocity
RECIPROCITY = [
 ("Piezo element", "Microphone ⟷ speaker / ultrasonic transmitter",
  "Same disc, both directions. Sonar is one element doing both jobs a millisecond apart."),
 ("LED", "Light emitter ⟷ photodiode",
  "Reverse-bias an LED and it detects light — most strongly at wavelengths slightly shorter than it "
  "emits. Two LEDs make a light-communication link with no photodiode at all."),
 ("Thermoelectric module", "Peltier cooler ⟷ Seebeck generator",
  "Apply current and it moves heat; apply a temperature difference and it makes current. One part, "
  "two entirely different products."),
 ("Coil", "Electromagnet ⟷ induction pickup",
  "Drive it to make a field; leave it passive to sense a changing one. Wireless charging and metal "
  "detection are the same coil with different firmware."),
 ("Motor", "Motor ⟷ generator ⟷ position sensor",
  "Back-EMF tells you speed with no encoder. Stall detection needs no sensor either — the motor is "
  "already reporting, if you listen to its current."),
 ("Antenna", "Transmitter ⟷ receiver",
  "Reciprocity theorem: an antenna's transmit and receive patterns are identical. Whatever it "
  "radiates well, it hears well."),
 ("Speaker", "Sound output ⟷ vibration sensor",
  "A speaker cone is a large, sensitive microphone. It is also a perfectly good seismometer for "
  "low frequencies."),
 ("Resistive heater", "Heater ⟷ temperature sensor",
  "Its resistance changes with its own temperature, so it can report its temperature while heating. "
  "Sensorless thermal control — the trick inside every self-regulating element."),
]

MNEMONIC_RECIPROCITY = ("Every transducer runs backwards. When you cannot find a sensor for "
                        "something, look for the ACTUATOR and reverse it.")

# ---------------------------------------------------------------- protocol
PROTOCOL = [
 ("1 · Name the physical quantity, honestly",
  "Not 'I want to detect a person' but 'a person is a 100 W infrared source, a 40,000 ppm CO₂ "
  "source, a 60 kg mass, a dielectric, a moving reflector and a sound source'. Most sensing "
  "problems are solved the moment you list what the target actually IS physically."),
 ("2 · Identify the energy domain",
  "Which of the six is your quantity in? If it is in several, you have several independent routes — "
  "and independent routes are what make robust systems, because they fail differently."),
 ("3 · Find the door to electrical",
  "Look up the transduction grid. Is there a direct effect? If not, route through THERMAL — heat is "
  "the universal intermediary and absorb-then-measure-the-warming works when nothing else does."),
 ("4 · Estimate the signal before you buy anything",
  "Work out the magnitude on the back of an envelope. Microvolts? You need an instrumentation "
  "amplifier. Picoamps? A transimpedance stage and a guard ring. Millivolts? An ADS1115 will do. "
  "This one calculation prevents most wasted purchases."),
 ("5 · Ask what sets the noise floor",
  "Johnson noise from your source resistance, shot noise from your current, 1/f from the amplifier, "
  "or interference from the room? The answer tells you which of the moves will help, and the other "
  "three will not."),
 ("6 · Try to escape the noise rather than out-amplify it",
  "Can you modulate to a quieter frequency? Make it differential so common-mode cancels? Narrow the "
  "bandwidth? These are usually free, and they beat a better amplifier."),
 ("7 · Ask what time buys you",
  "Can you integrate for longer? Compare against a baseline instead of an absolute? Watch a rate of "
  "change rather than a level? Time turns cheap, drifty sensors into good instruments — this is the "
  "single highest-leverage move in the whole catalogue."),
 ("8 · Ask what a second sensor buys you",
  "A different modality that fails differently turns a guess into a confirmation. Field testing "
  "found PIR alone produced 39 false triggers across 40 real events; requiring ultrasonic agreement "
  "eliminated every one."),
 ("9 · Write down how it will be fooled",
  "Before you build. If you cannot name three ways your measurement could be wrong, you do not yet "
  "understand it — and the field will teach you the same lesson far more expensively."),
]

# ---------------------------------------------------------------- traps
TRAPS = [
 ("A sensor reports itself, not the world",
  "Every reading is the sensor's own state. A thermocouple taped to a pipe reads a blend of pipe "
  "and room air. A humidity sensor in an enclosure reads the enclosure. Ask what the sensor is "
  "actually in equilibrium with — the answer is frequently not what you intended."),
 ("Ratiometric beats absolute",
  "If a sensor is excited by a supply and read against that same supply, supply variation cancels "
  "exactly. Read it against a different reference and every wobble of the rail becomes measurement "
  "error. This is free accuracy that most designs throw away."),
 ("Ground is not a place, it is a network",
  "Two points labelled 'ground' can differ by millivolts, and your signal may be microvolts. Ground "
  "loops are the leading cause of mysterious noise in analog sensing. Star grounding and "
  "differential measurement both dodge it."),
 ("Dissimilar metals make thermocouples whether you want them or not",
  "Every junction of different metals generates a thermoelectric voltage of tens of microvolts per "
  "degree. In a precision circuit your connectors and solder joints ARE thermocouples, and they "
  "drift as the room warms."),
 ("Self-heating changes what you are measuring",
  "Current through a thermistor warms it. An LED near a temperature sensor warms it. An ESP32 on "
  "the same PCB warms everything — routinely by 1–3 °C, which is an order of magnitude worse than "
  "a good sensor's rated accuracy."),
 ("Calibration is not a one-off",
  "Electrochemical cells age, pH glass ages, optical windows foul, load cells creep, MOX baselines "
  "wander. A calibration is a snapshot with a shelf life, and knowing that shelf life is part of "
  "knowing the sensor."),
 ("Correlation in a controlled room is not causation in a house",
  "Machine-learning models built on data from one environment routinely collapse in another. This "
  "is the honest limitation behind Wi-Fi CSI sensing, gas-sensor classification and most "
  "'AI sensing' demonstrations."),
 ("The datasheet number is the best case",
  "Accuracy figures assume 25 °C, after calibration, with the recommended layout, in the specified "
  "range. Your result will be worse. Design with margin and verify with a reference."),
]

CLOSING = (
 "The whole sheet in one paragraph: sensing is energy crossing a door between two of six domains. "
 "There are perhaps a dozen tricks for opening those doors, and they recur endlessly under "
 "different names. The limits are set by noise, bandwidth, sampling and the inverse square law, and "
 "you evade them by modulating, differencing, integrating over time, or getting closer. Every "
 "transducer runs backwards. Nothing is measured without being disturbed. And the most powerful "
 "cheap move available to you is TIME — a mediocre sensor with a baseline and a long memory "
 "outperforms an excellent one read once."
)
