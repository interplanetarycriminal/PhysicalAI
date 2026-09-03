"""Physics Cheat Codes II — twelve codes the first ninety do not cover.

The first ninety are excellent. That is not the same as complete. Auditing them
for coverage rather than quality turns up whole techniques missing — including
two of the most powerful moves in all of instrumentation (synchronous detection
and matched filtering), an entire physical domain (nuclear attenuation), an
entire chemistry (biological selectivity), and the one thinking tool that
predicts answers before you solve anything (dimensional analysis).

Same five columns as the original sheet, deliberately.
"""

# Two numerical errors found in the original ninety, corrected in place and
# logged here so the change is not silent.
CORRECTIONS = [
 ("⬇️ Down is free truth", "10.3kPa per metre of water", "9.81kPa per metre of water",
  "10.3 is the number of METRES of water per atmosphere, not the kilopascals per metre. "
  "ρgh = 1000 × 9.81 × 1 = 9.81 kPa/m; 101.3 kPa ÷ 9.81 = 10.33 m. The two figures were "
  "swapped. This matters directly: every hydrostatic level sensor in the catalog converts "
  "pressure to depth with this constant, and a 5% error is a 5cm error per metre."),
 ("🥶 Evaporation is refrigeration you can read", "steals 2.26kJ", "steals ~2.45kJ at room temperature",
  "2.26 kJ/g is the latent heat of vaporisation at 100°C. Evaporative cooling and wet-bulb "
  "measurement happen at ambient, where it is about 2.45 kJ/g — roughly 8% higher. For a code "
  "about reading humidity from a wet surface, the ambient figure is the one you use."),
]

# (cheat code, the physics, catalog exploits, build it this weekend, how to spot the next one)
CODES_II = [

("🔒 Lock onto your own signal",
 "If YOU control when a signal happens, you can reject everything not in step with it. Modulate "
 "the excitation at a chosen frequency, multiply the return by that same reference, and average: "
 "anything correlated with your reference survives, everything else averages to zero. Noise "
 "rejection of a million to one is routine, and it costs a square wave.",
 "38kHz IR receivers that ignore sunlight · every photoelectric sensor that works in daylight · "
 "capacitive touch controllers · AC-excited soil probes (which is also why DC excitation "
 "electrolyses them)",
 "Blink an LED at 1kHz, read a photodiode, multiply your samples by a 1kHz square wave and "
 "average. It will see straight through room lighting that completely swamps the DC reading.",
 "When ambient interference is bigger than your signal, stop trying to shield it and start "
 "chopping it. Ask: can I make my signal blink on a schedule only I know?"),

("🧩 If you know its shape, you can find it under the noise",
 "Correlating a received signal against a known template concentrates the signal and scatters "
 "the noise, by the time-bandwidth product of the code. GPS arrives at about −130dBm — far below "
 "the thermal noise floor — and is recovered anyway, purely because the receiver knows exactly "
 "which pseudo-random sequence to look for.",
 "GPS and all GNSS · LoRa spread spectrum · ultrasonic ranging with coded bursts rather than "
 "single pings · radar pulse compression · Wi-Fi CSI",
 "Transmit a 10-bit pseudo-random burst on a 40kHz ultrasonic pair instead of one ping, and "
 "correlate the echo against it. Range and noise immunity both jump, with no extra hardware.",
 "When a signal is buried, do not reach for amplification — reach for correlation. Ask: do I "
 "know the SHAPE of what I am looking for? If yes, you can dig it out of noise far below it."),

("🎲 Add noise to see finer",
 "Dither. A steady signal sitting between two ADC codes reads the same number forever, and "
 "averaging cannot help. Add noise comparable to one least-significant bit and the reading now "
 "spends time in each code in proportion to the true value — so averaging N samples recovers "
 "resolution BELOW the converter's own step size, roughly half a bit per fourfold increase in N.",
 "The ESP32's own mediocre ADC · any 10 or 12-bit converter watching a slow signal · "
 "oversampling in audio converters · why a slightly noisy sensor can out-resolve a silent one",
 "Read a stable voltage on the ESP32 ADC and average a thousand samples — it barely moves. Now "
 "inject a few millivolts of noise (a length of floating wire is often enough) and average "
 "again: you will resolve steps smaller than a single ADC code.",
 "If a reading is quantised and stuck on one value, you are resolution-limited, not "
 "noise-limited — and the counter-intuitive fix is to add noise, then average it back out."),

("⚖️ The most accurate reading is zero",
 "Null methods compare an unknown against an adjustable known and detect only the DIFFERENCE, "
 "which you then drive to zero. At balance, the detector's gain, linearity, offset and drift "
 "stop mattering entirely — you are only asking 'is it zero yet?', which is the one question "
 "every detector on earth answers well.",
 "Wheatstone bridges · potentiometric pH · force-balance (servo) accelerometers · closed-loop "
 "Hall current transducers, which are accurate precisely because the Hall element only ever "
 "sees zero field",
 "Replace a thermistor's voltage divider with a bridge and null it with a potentiometer. Your "
 "reading becomes the pot's position rather than the ADC's honesty, and it stops caring what "
 "your supply rail is doing.",
 "When accuracy matters more than speed, stop measuring the quantity and start cancelling it. "
 "Ask: what could I balance this against, and what would tell me when I had?"),

("🩸 Every measurement takes something",
 "You cannot observe without extracting energy or matter. A voltmeter draws current. A "
 "thermometer absorbs heat. A galvanic dissolved-oxygen probe CONSUMES the oxygen it reports. A "
 "flow sensor obstructs the flow. The disturbance scales with how hard you look, which makes "
 "'sensitive' and 'non-invasive' opposing design goals.",
 "DO probes reading low in still water · a cold thermocouple cooling the thing it touches · a "
 "scope probe detuning an oscillator · a pitot tube disturbing the flow it samples",
 "Measure a high-impedance source — a pH electrode or a photodiode — first with an ordinary "
 "multimeter and then through a high-impedance buffer. The difference between the two readings "
 "IS the loading you were previously unaware of.",
 "Ask of every measurement: what am I taking from the system, and is the system small enough to "
 "notice? If it is, either shrink the probe or measure without contact."),

("🌈 One number decides what a semiconductor can be",
 "The band gap sets everything simultaneously: the longest wavelength the material can absorb, "
 "the colour it emits, its forward voltage, and how steeply all of that drifts with temperature. "
 "Silicon's 1.1eV means it is blind beyond about 1100nm no matter what you pay. InGaAs at "
 "0.75eV reaches 1700nm. A blue LED needs 2.7eV, which is why it arrived decades after the red one.",
 "Why silicon photodiodes cannot see SWIR · why a reverse-biased LED detects light shorter than "
 "it emits · why every silicon junction is a −2mV/°C thermometer whether you wanted one or not",
 "Reverse-bias a red LED and a blue LED into the same ADC under the same lamp. The red one "
 "responds to more of the spectrum. That is the band gap, visible on a breadboard for pennies.",
 "Before buying any optical sensor, look up the band gap rather than the marketing. It tells you "
 "what the part can physically never see, which no amount of gain will fix."),

("☢️ Attenuation reads density through anything",
 "Gamma and X-rays are absorbed exponentially with the mass in their path: I = I₀·e^(−μρx). A "
 "source on one side and a detector on the other therefore measures density × thickness through "
 "steel, concrete or a sealed vessel — no contact, no window, no opening it.",
 "Industrial level and density gauges on sealed reactors · bone densitometry · thickness control "
 "in rolling mills · security scanners · and, at hobby scale, a Geiger tube plus a check source",
 "With a Geiger tube and a small check source, measure count rate through an increasing stack of "
 "aluminium sheet. Plot log(counts) against thickness: it is a straight line, and its slope is "
 "the attenuation coefficient.",
 "When you must see inside something you are not allowed to open, ask what radiation passes "
 "through it and what fraction survives. The survivors carry the density."),

("🎯 Rare events arrive at random, and √N is your error bar",
 "Counting statistics are Poisson: count N events and your uncertainty is √N. Count 100 and you "
 "know it to ±10%. Count 10,000 and you know it to ±1%. There is no clever electronics that "
 "evades this — the ONLY way to halve your error is to count four times as long.",
 "Geiger counting · photon counting · optical particle counters · muon detection · any "
 "rare-event sensing where the scatter looks like a broken instrument and is not",
 "Log Geiger counts in ten-second bins for an hour. The scatter you see is not the tube "
 "misbehaving; compute √N for your average bin and you will find it matches almost exactly.",
 "Before blaming a counting sensor for noise, compute √N. If the observed scatter matches, the "
 "instrument is behaving perfectly and what you actually need is more time."),

("🧬 Biology already solved selectivity",
 "Enzymes and antibodies bind ONE target among thousands, at concentrations no electronic sensor "
 "approaches — selectivity refined over a billion years of evolution. Immobilise one on an "
 "electrode or a membrane and its binding event becomes a current, a colour change or a "
 "frequency shift you can read with the same electronics as anything else in this atlas.",
 "Glucose strips (glucose oxidase) · lateral-flow tests · BOD probes · aptamer sensors · "
 "enzyme-linked electrodes for lactate, ethanol and urea",
 "Read a commercial glucose test strip's electrode with your own potentiostat instead of the "
 "meter. The chemistry does the selective part; you are only measuring a small current, and the "
 "strips cost pennies.",
 "When you need to detect one specific molecule among many, stop looking for a physical effect "
 "and start looking for what already binds it. Physics is rarely selective; biology always is."),

("📐 You can predict the answer's shape before you solve anything",
 "Dimensional analysis. Any true equation must balance its units, which constrains the FORM of "
 "the answer before you know its constant. A pendulum's period can only be √(L/g) times some "
 "dimensionless number. Terminal velocity can only go as √(mg/ρA). You get the scaling free, and "
 "only a single constant needs an experiment.",
 "Predicting how any sensor scales before building it · sanity-checking every number in this "
 "atlas · knowing that halving a cantilever's length must roughly quadruple its frequency "
 "without touching a beam equation",
 "Before your next build, list what the answer depends on and combine those quantities into the "
 "right units. You will usually land within a factor of three, in ninety seconds, on paper, with "
 "no simulation and no datasheet.",
 "Facing an unfamiliar system, list the variables and their dimensions FIRST. The units alone "
 "eliminate almost every wrong answer, and what survives is nearly always close."),

("🔁 The loop's area is the energy you lost",
 "Anything with hysteresis — magnetic, mechanical, thermal, chemical — traces a loop when you "
 "cycle it, and the area enclosed is the energy dissipated per cycle. A wider loop is more "
 "waste, more heat and more wear, which makes loop area a direct efficiency and health metric.",
 "Magnetic core losses in transformers · rubber and damper self-heating · battery round-trip "
 "inefficiency · stiction in bearings and slides · why FSRs and Velostat drift under sustained load",
 "Log force against displacement while slowly compressing and then releasing a piece of foam. "
 "The two paths will not coincide; the gap between them is exactly the energy the foam turned "
 "into heat.",
 "Cycle anything and plot output against input rather than against time. If the up-path and the "
 "down-path differ, you have found a loss and a diagnostic in the same measurement."),

("👊 Calibrate by poking it",
 "Inject a KNOWN stimulus and measure the response, and you have just calibrated the entire "
 "chain — sensor, wiring, amplifier, converter and code — in place, without removing anything or "
 "trusting any single link. The known perturbation is a reference you can carry into the field.",
 "The self-test bit in most MEMS accelerometers · a known mass dropped on a load cell · shorting "
 "an ADC input to measure offset · injecting a reference tone into an audio chain · pulsing a "
 "heater to verify a thermal path",
 "Read your accelerometer's self-test register at every boot and log the result. A slowly "
 "drifting self-test response predicts sensor failure well before the actual data starts "
 "looking wrong.",
 "Ask of every deployed sensor: what known thing could I do to it that would prove it still "
 "works? Then do that on a schedule, and log the answer alongside the data."),
]
