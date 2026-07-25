"""Anti-Catalog II — more walls, and what each one teaches.

The original Anti-Catalog is the best sheet in the atlas and one of the smallest.
That is backwards: knowing what is impossible is worth more than knowing what is
possible, because the impossible things are where months disappear.

Each wall here is a genuine physical limit, not an engineering inconvenience —
stated with the number that makes it a wall, what the wall teaches, and the
nearest honest thing you CAN measure instead.
"""

WALLS = [

("Reading a stationary person with a PIR",
 "A pyroelectric element produces charge only when its temperature CHANGES. A person radiating "
 "steadily at constant position produces a constant flux and therefore, after the element "
 "equilibrates, exactly zero signal. This is not a sensitivity limit that a better PIR fixes — "
 "it is what pyroelectricity IS.",
 "Some sensors measure a quantity and some measure its derivative. Read the transduction "
 "mechanism, not the marketing: 'motion sensor' and 'presence sensor' are different physics, and "
 "the word on the box is chosen by whoever is selling it.",
 "mmWave radar senses the micro-motion of breathing and works on the motionless. Thermopile "
 "arrays sense the steady flux directly. A $5 LD2410 solves what no PIR ever will."),

("Non-contact temperature of a shiny surface",
 "Infrared thermometry inverts the Stefan–Boltzmann law, which contains emissivity ε as a "
 "multiplier. Polished aluminium has ε ≈ 0.05, so it emits a twentieth of what a blackbody at the "
 "same temperature does — and it reflects its surroundings instead. The instrument cannot "
 "separate 'cool object' from 'shiny object reflecting a cool room' because both produce the same "
 "photons.",
 "When a measurement depends on an unknown material property, no amount of instrument quality "
 "recovers it. You must either measure the property, fix it, or change measurement entirely.",
 "Fix ε by putting a square of matt tape or a dab of paint on the surface, then measure that. Or "
 "abandon radiometry and use contact: a $2 thermistor with thermal paste beats a $200 thermal "
 "camera on bare metal, every time."),

("Sub-millimetre ranging with 40 kHz ultrasound",
 "A 40 kHz wave in air is 8.6 mm long. You cannot resolve features much finer than a wavelength, "
 "and the transducer's own ring-down blinds the receiver for the first several hundred "
 "microseconds — which is a dead zone of 20-25 cm before resolution even becomes the issue.",
 "Wavelength sets both the resolution floor and the target size you can grip. Wanting finer "
 "detail means choosing a shorter wavelength, not a better vendor — this is cheat code 18 stated "
 "as a prohibition.",
 "Optical time-of-flight (940 nm) resolves millimetres because its wavelength is 10,000× shorter. "
 "For sub-millimetre at short range, a VL6180X or a capacitive gap sensor; for sub-micron, "
 "interferometry or an inductive probe."),

("Weighing anything in a moving vehicle with a load cell alone",
 "A load cell measures force, and force is mass × acceleration. In a moving vehicle the "
 "acceleration is not 9.81 m/s² and is not known — so weight and acceleration are mathematically "
 "inseparable from one measurement. A pothole and a heavier load produce identical outputs.",
 "One equation cannot solve two unknowns. When a measurement is confounded by an unknown, you "
 "need either a second independent measurement or a condition where the confound vanishes.",
 "Add an accelerometer and subtract, which works to a few percent. Or exploit the condition: "
 "weigh only when the IMU says the vehicle is stationary and level. The second answer is far "
 "cheaper and far more accurate."),

("Getting more than about ten honest bits from the ESP32's ADC",
 "The ESP32's SAR ADC has integral non-linearity of tens of LSBs, a non-zero and part-dependent "
 "offset, a reference that moves with supply and temperature, and ADC2 that stops working "
 "entirely when the radio transmits. Twelve bits are converted; roughly ten are meaningful, and "
 "fewer near the rails.",
 "Resolution is not accuracy (cheat code from the ceiling section). A converter's bit count "
 "describes its step size, not its truthfulness, and the datasheet's headline number is the "
 "former.",
 "An ADS1115 at $3 gives genuine 16-bit differential readings with a programmable gain stage. "
 "This single part upgrades roughly a third of this catalog, and it is the cheapest large "
 "improvement available anywhere in the atlas."),

("Measuring radon quickly",
 "Radon decays are rare events and obey Poisson statistics. At a typical indoor 100 Bq/m³, a "
 "1-litre detection chamber sees 0.1 decays per second. To reach ±10% you need 100 counts, which "
 "is 1,000 seconds; consumer detectors have far smaller effective volumes, which is why they "
 "quote hours to days. No electronics makes a decay happen sooner.",
 "When the physics delivers events at a fixed rate, precision is bought with TIME and nothing "
 "else — √N is the whole story. An instrument that promises a fast radon reading is either "
 "extrapolating or lying.",
 "Accept the integration time and design around it: radon is a long-term health exposure, so a "
 "24-hour average is the medically meaningful number anyway. Use pressure and ventilation as "
 "fast proxies for when radon is LIKELY to be rising."),

("Identifying which VOC is present with one broadband sensor",
 "A metal-oxide sensor produces a single resistance. One number cannot resolve many unknowns — "
 "it is one equation with N variables. Ethanol, hydrogen, CO and cooking fumes all move it the "
 "same direction, and no calibration recovers which one did it.",
 "Dimensionality is a hard limit. To separate N species you need at least N independent "
 "measurements: multiple sensors with different selectivities, or one sensor swept through "
 "multiple states.",
 "Sweep the heater through several temperatures and the SAME element gives several partially "
 "independent readings — this is what BME688 and its AI-Studio workflow actually exploit. Or use "
 "an electrochemical cell, which is selective by construction, for the one gas you care about."),

("State of charge from voltage on a LiFePO₄ cell",
 "LiFePO₄'s discharge curve is famously flat: from roughly 20% to 80% state of charge, terminal "
 "voltage moves by about 0.1 V out of 3.2 V. With cell-to-cell variation, temperature "
 "dependence and load-dependent sag all of the same magnitude, voltage simply does not encode "
 "charge across the useful range.",
 "A monotonic relationship is not enough — it must be STEEP relative to its confounds. When the "
 "slope approaches the noise, the inversion is meaningless no matter how precisely you measure.",
 "Coulomb counting: integrate current in and out. It is exact in principle and drifts only "
 "through integration error, which periodic full-charge resets correct. This is why every serious "
 "battery gauge counts charge rather than reading volts."),

("Seeing through a wall optically",
 "Wavelengths that penetrate plasterboard (radio, low-frequency) are metres to centimetres long "
 "and therefore cannot resolve centimetre detail. Wavelengths that resolve fine detail (visible, "
 "IR) are stopped by the first hundred microns of paint. Penetration and resolution trade against "
 "each other through the same wavelength parameter — you cannot have both.",
 "Two desirable properties controlled by ONE parameter is a trade, not a problem. Recognising a "
 "trade early stops you searching for a product that cannot exist.",
 "Accept coarse: 24-60 GHz radar sees motion and rough position through drywall at centimetre-to-"
 "decimetre resolution, which is enough for presence, breathing and falls. For structure rather "
 "than motion, ultrasound through the material or a borescope through a 6 mm hole."),

("Absolute chemical accuracy from any uncalibrated probe, indefinitely",
 "pH glass ages and its Nernst slope degrades. Electrochemical cells consume their electrolyte. "
 "MOX baselines wander with humidity history. Optical windows foul. Every chemical sensor is a "
 "consumable in slow motion, and drift is not a defect but the mechanism working.",
 "Chemistry keeps receipts in both directions — the same irreversibility that makes chemical "
 "sensing possible makes it impermanent. Budget calibration as a recurring cost, like printer ink.",
 "Two-point calibration on a schedule, with buffer sachets and standards costing a few pounds. "
 "Or measure RELATIVE change against a co-located identical sensor, where shared drift cancels — "
 "cheat code 23 applied to chemistry."),

("Distinguishing cause from correlation by adding more sensors",
 "More channels give you more correlations, and correlations multiply faster than insight. With "
 "enough sensors logging in one room, something will correlate with anything at any significance "
 "level you like. This is a statistical certainty, not a data-quality problem.",
 "Causation requires INTERVENTION, not observation. The only reliable way to establish that A "
 "causes B is to change A deliberately and watch B — which is a design decision, not a sensing "
 "one.",
 "Build the ability to perturb into the system from the start: a fan you can switch, a heater you "
 "can pulse, a window actuator you can command. A modest sensor array that can intervene beats a "
 "large one that can only watch."),

("Optical time-of-flight through fog, steam or dust",
 "Scattering, not absorption, is what defeats it. Suspended droplets return photons early and "
 "from everywhere, so the detector sees a bright, diffuse return that swamps the true first "
 "surface. The sensor confidently reports a much shorter distance — it is not confused, it is "
 "correctly ranging the fog.",
 "A sensor failing silently by reporting a plausible wrong number is far more dangerous than one "
 "reporting nothing. Ask of every sensor: what does it do when its assumptions break?",
 "Ultrasound is largely indifferent to fog and steam because 8 mm waves ignore micron droplets — "
 "the same wavelength argument that made it useless for fine detail makes it excellent here. "
 "77 GHz radar is better still, and this is exactly why cars use it."),
]
