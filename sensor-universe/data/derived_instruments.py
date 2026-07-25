"""Derived Instruments — sensing methods worked out from first principles.

Everything else in this atlas is synthesis: real parts, real physics, real
failure modes, organised well. This sheet is different. Each entry is an
instrument DERIVED here by applying the transduction grid and the cheat codes to
a measurement problem, then tested with arithmetic before anything is bought.

Three of them come out DEAD, killed by their own numbers. Those are kept
deliberately — an inventor's notebook that contains only successes is a
marketing document, and the arithmetic that kills an idea in ten minutes is
worth more than the six months it saves.

Verdicts:
  BUILD     the numbers work with catalog parts, and nothing sold does this
  MARGINAL  it works, but only in a narrow band where the obvious answer fails
  DEAD      the arithmetic refuses; recorded so nobody re-derives it
"""

# (verdict, name, what it measures, the physics, the arithmetic, parts, what kills it, why it doesn't exist)
INSTRUMENTS = [

("BUILD", "Barometric door-and-window locator",
 "Which door or window in a house just opened, from anywhere in the house, with no sensor on any "
 "door.",
 "A house is a leaky pressure vessel. Swinging a door displaces air faster than the envelope can "
 "equalise, so the whole interior sees a brief pressure transient. Sound reaches every room in "
 "milliseconds; this pressure step propagates as a bulk flow over ~0.5-2s, and its SHAPE and "
 "ARRIVAL ORDER at several barometers encode which opening moved and in which direction.",
 "A BMP390 in low-noise mode resolves about 0.03 Pa RMS. Swinging an interior door displaces "
 "roughly 1-2 m³ in under a second; in a house with typical envelope leakage that produces a "
 "transient of order 1-10 Pa. That is 30 to 300 times the noise floor — not a marginal "
 "measurement, an obvious one. Three sensors give arrival-order; the sign of the step "
 "distinguishes opening from closing.",
 "3 × BMP390 or DPS310 ($10 each) · 3 × ESP32-C3 · ESP-NOW for a shared timebase. Under $50 "
 "for a whole house.",
 "HVAC, extractor fans and wind gusts also move whole-house pressure — you must gate on their "
 "signature (slower, sustained) versus a door's (fast step then decay). A very leaky house "
 "attenuates the transient; a passive-house-tight one amplifies it enormously.",
 "Because door sensors are cheap and obvious, so nobody asked whether the house itself is "
 "already a sensor. The pressure coupling is well known to building physicists and completely "
 "unexploited by makers."),

("BUILD", "Dual-probe heat-pulse soil water content",
 "Volumetric soil water content that is INSENSITIVE TO SALINITY — the confound that makes every "
 "cheap capacitive probe lie in fertilised or coastal soil.",
 "Capacitive probes measure dielectric constant, which responds to dissolved ions as well as "
 "water. Thermal properties do not care about ions. Fire a brief heat pulse into a line source "
 "and measure the temperature rise at a known small distance: the PEAK rise is inversely "
 "proportional to the soil's volumetric heat capacity C, and water contributes 4.18 MJ/m³K "
 "against dry mineral soil's ~2.0. So θ = (C − C_dry) / 4.18 directly.",
 "Standard practice uses ~60-100 J/m over 8s with probes 6mm apart, giving a peak rise of "
 "1-4 °C. Two small NTC beads resolve 0.01 °C easily with an ADS1115, so the measurement is "
 "20-400 times the noise floor. The salinity insensitivity is the whole point: thermal "
 "conductivity of soil water changes by under 1% across the salinity range that shifts a "
 "capacitive probe's reading by tens of percent.",
 "2 × glass-bead NTC ($0.60) · nichrome or constantan heater wire · ADS1115 ($3) · MOSFET · "
 "two hypodermic tubes 6mm apart. Under $10.",
 "Probe geometry must be rigid and identical between builds — the 6mm spacing enters the maths "
 "directly, so a bent probe is a miscalibrated one. Poor soil contact after installation "
 "invalidates it until the soil settles back.",
 "It exists in soil-science literature (the dual-probe heat-pulse method) and in $500 research "
 "instruments. It has never been packaged for makers, even though the parts cost under ten "
 "dollars and it solves the single most-complained-about failure in hobby soil sensing."),

("BUILD", "Thermal effusivity liquid identifier",
 "WHICH liquid a probe is sitting in — water, ethanol, oil, glycol, or air — from a single "
 "self-heated element, with no chemistry and no optics.",
 "Drive a small resistive element with constant power and watch its temperature rise. For short "
 "times the rise goes as 1/e where e = √(kρc) is thermal effusivity — a bulk property that "
 "differs enormously between liquids because it combines conductivity, density and heat "
 "capacity.",
 "Effusivity, J/(m²·K·√s): water 1580 · glycerol ~950 · ethanol ~600 · engine oil ~380 · air ~6. "
 "Water against ethanol is a 2.6:1 ratio and water against air is 260:1, so the temperature rise "
 "for the same power differs by the same factors. A 10mW pulse into a small NTC gives a rise of "
 "tenths of a degree in air and hundredths in water — trivially separable with an ADS1115. "
 "This also means it detects a probe that has fallen out of the liquid, instantly.",
 "1 × glass-bead NTC ($0.30) · one resistor · ADS1115 ($3) · a GPIO to pulse it. Under $5.",
 "Flow steals heat and looks like higher effusivity, so it must be measured in still liquid or "
 "with flow independently known. Coatings and biofilm on the probe change the contact and drift "
 "the calibration over months.",
 "Hot-wire anemometry uses this physics for flow; nobody markets the same element as a liquid "
 "IDENTIFIER, because industry solves liquid ID with refractometry or conductivity. For a maker "
 "wanting 'is this tank water or is it fuel', this is a five-dollar answer."),

("BUILD", "Helmholtz fill-level gauge (through the wall, no contact)",
 "How full a sealed container is — through its wall, touching nothing, with no port and no "
 "modification, using a speaker and a microphone.",
 "The headspace above a liquid is a Helmholtz resonator: f = (c/2π)·√(A/(V·L)), where V is the "
 "gas volume. Excite the container with a swept tone and the headspace resonance appears "
 "sharply. Because f goes as 1/√V, the resonance climbs as the container fills — the pitch IS "
 "the level.",
 "For a 5 L headspace with a 20mm neck 30mm long: f = (343/6.28)·√(3.14e-4 / (0.005 × 0.03)) "
 "≈ 79 Hz. Half-empty that headspace and V halves, so f rises by √2 to about 112 Hz — a 33Hz "
 "shift that any FFT on an ESP32 resolves to well under 1 Hz. That is roughly 1% level "
 "resolution from a speaker and a microphone.",
 "1 × small speaker + MAX98357A ($5) · 1 × INMP441 mic ($3) · ESP32-S3 for the FFT. Under $15, "
 "and it can be moved between containers.",
 "It needs a defined neck or opening to resonate; a fully sealed rigid tank has no Helmholtz "
 "mode and you get nothing. Foam and sloshing broaden the peak. Temperature changes the speed "
 "of sound by 0.6%/10°C, which is a 0.3% level error unless compensated.",
 "Brewers and acousticians know the physics; no product packages it because commercial level "
 "sensing sells ultrasonic and radar. For carboys, fermenters, kegs and jerry cans it is better "
 "than both, because it needs no line of sight to the surface."),

("BUILD", "CO₂ as a room tape-measure",
 "The VOLUME of a room, and its true air-change rate, using only a CO₂ sensor and a known "
 "source.",
 "Release a known mass of CO₂ into a space and the concentration rise gives you the volume "
 "directly: ΔC = m / (ρ_CO₂ · V). Then stop the source and watch the exponential decay: its time "
 "constant is the air-change rate. One sensor, two numbers, both of which are otherwise "
 "surprisingly hard to obtain.",
 "A human at rest exhales roughly 0.02 m³/h of CO₂ — about 40 g/h. In a 30 m³ bedroom that "
 "raises concentration by roughly 550 ppm per hour before ventilation is accounted for. An SCD41 "
 "resolves 1 ppm and is accurate to ±40 ppm, so the rise is 10-15 times the error band within "
 "the first hour. Run it in reverse — measure the rise from a known source — and the volume "
 "falls out to within a few percent.",
 "1 × SCD41 ($25) · a source of known rate: a small CO₂ cylinder with a needle valve, a measured "
 "mass of dry ice, or simply one seated adult and a stopwatch.",
 "It assumes the room mixes well; a stratified or partitioned space gives you the volume of the "
 "well-mixed zone, not the room. Open doors turn the measurement into a measurement of the whole "
 "connected volume — which is sometimes exactly what you wanted.",
 "Tracer-gas decay is standard in building science using SF₆ and thousand-pound kit. Nobody has "
 "pointed out that a $25 consumer CO₂ sensor and a human being make the same measurement to a "
 "few percent."),

("BUILD", "Mains frequency as a free distributed clock",
 "Sub-second time synchronisation between any two mains-powered nodes on the same grid — with no "
 "network, no GPS, and no shared radio.",
 "Grid frequency is identical everywhere on a synchronous interconnect at any instant, and it "
 "wanders continuously by ±0.05 Hz as load and generation chase each other. That wander is "
 "effectively a unique random signal broadcast to every socket in the country. Two nodes each "
 "logging mains frequency can cross-correlate their traces afterwards and recover their relative "
 "time offset.",
 "Measuring zero crossings over a 1-second window gives frequency to about 1 mHz, and the grid "
 "moves by tens of mHz over tens of seconds. Cross-correlating two 10-minute traces therefore "
 "aligns them to roughly one sample — sub-second — with no shared infrastructure at all. This is "
 "the same Electrical Network Frequency signature used forensically to date audio recordings.",
 "1 × ZMPT101B or an optocoupler on a low-voltage AC supply ($3) · any ESP32 · a timer capture "
 "pin. Effectively free if the node is mains-powered anyway.",
 "Only works within one synchronous grid — Britain, continental Europe and the various American "
 "interconnects are separate signals. Battery nodes are excluded by definition. Inverter and UPS "
 "output does not carry the grid's signature.",
 "ENF is well established in forensics and completely absent from maker sensing, where everyone "
 "reaches for NTP or GPS. For a distributed array in a building with no reliable network, this "
 "is a free and rather beautiful answer."),

("BUILD", "Electrolytic coulomb-counted flow standard",
 "A calibration reference for any flow sensor, generated on the bench from first principles, "
 "with no reference meter and no trip to a calibration lab.",
 "Faraday's law is exact: passing charge Q through water liberates gas in strict proportion — "
 "96,485 coulombs per mole of electrons. Electrolyse at a measured constant current for a "
 "measured time and you know the gas volume produced to the accuracy of your ammeter and clock, "
 "which is to say very well indeed. Displace liquid with that gas and you have a volumetric "
 "standard.",
 "1 A for 60 s = 60 C = 6.22e-4 mol of electrons = 3.11e-4 mol of H₂, which at room temperature "
 "and pressure is about 7.6 mL. Current measured to 0.5% with an INA226 and time to 0.01% gives "
 "volume to about 0.5% — better than any hobby flow sensor's specification, and traceable to "
 "physical constants rather than to another instrument.",
 "1 × INA226 ($6) · stainless electrodes · a graduated tube · the flow sensor under test. "
 "Under $15.",
 "Gas volume depends on temperature and pressure, so both must be measured (which the catalog "
 "already does). Some current goes into side reactions and dissolved gas, so it reads slightly "
 "low unless the water is pre-saturated.",
 "Calibration labs sell this traceability for hundreds of pounds. The physics is exact and the "
 "parts cost fifteen. Nobody packages it because calibration is a service business."),

("BUILD", "Role-swapping LED colorimeter that cancels its own ageing",
 "Optical absorbance measurements that stay calibrated for years, without a reference cuvette "
 "and without recalibrating for LED ageing or temperature drift.",
 "An LED is also a photodiode, most sensitive just short of its emission wavelength. Put two "
 "identical LEDs facing each other through the sample and alternate their roles: A emits while B "
 "detects, then B emits while A detects. Both readings contain the same sample absorbance but "
 "opposite LED drifts, so the geometric mean of the two cancels ageing and temperature to first "
 "order.",
 "LED output falls by roughly 20-30% over a few thousand hours and shifts about −0.5%/°C, which "
 "is catastrophic for absolute absorbance over months. The role-swapped product removes both to "
 "first order because each LED appears once as source and once as detector. Residual error comes "
 "only from the DIFFERENCE in their ageing rates, which for a matched pair from one reel is "
 "small.",
 "2 × identical LEDs ($0.20) · ADS1115 for the photocurrent ($3) · two GPIO. Under $5.",
 "LED photocurrents are nanoamps, so it needs a transimpedance stage or the ADS1115's narrowest "
 "range and patience. The two LEDs must genuinely be a matched pair — different bins age "
 "differently.",
 "The LED-as-detector trick is a well-loved curiosity; using it for SELF-REFERENCE rather than "
 "as a cheap photodiode is the step nobody takes. It converts a toy into an instrument."),

("MARGINAL", "Psychrometric humidity for the 90-100% band",
 "Relative humidity where every capacitive sensor fails: above 90%, in fog, in mushroom "
 "chambers, in greenhouses.",
 "Wet-bulb depression. A wetted thermometer cools by evaporation until the latent heat lost "
 "balances the sensible heat gained, and the depression below dry-bulb temperature is a direct "
 "function of humidity. It is the pre-electronic method and it does not saturate.",
 "At 20 °C and 50% RH the depression is about 6 °C. At 95% RH it is about 0.7 °C, and at 99% "
 "about 0.15 °C. Two DS18B20s at ±0.1 °C therefore give roughly ±2% RH at 95% and ±7% at 99% — "
 "worse than an SHT41 in the mid-range, but SHT41s saturate, hysteresis badly and can sit "
 "condensed and useless above 95%, where this keeps working.",
 "2 × DS18B20 ($5) · a cotton wick and a water reservoir · a small fan for the required 3 m/s "
 "airflow over the wet bulb.",
 "It needs continuous airflow and a wick that never dries out, so it is a maintained instrument "
 "rather than a fit-and-forget one. Below about 85% RH the electronic sensor simply wins.",
 "Psychrometers were replaced by capacitive sensors everywhere, and the industry forgot that the "
 "replacement is worse in exactly the band where growers live."),

("MARGINAL", "Crystal-drift thermometry from the Wi-Fi radio",
 "Ambient temperature with literally zero added components, on any ESP32 that is associated with "
 "an access point.",
 "The ESP32 runs from a plain AT-cut crystal whose frequency follows a cubic curve with "
 "temperature, roughly −0.04 ppm per °C² away from its turnover point. The Wi-Fi radio "
 "continuously measures its own carrier frequency offset against the AP, which is disciplined far "
 "better. That offset is therefore a thermometer that already exists in the silicon.",
 "Twenty degrees from turnover gives about 16 ppm of offset. If carrier frequency offset can be "
 "read to ~0.5 ppm, that is roughly 1.5 °C resolution at 20 °C from turnover. But the curve is "
 "FLAT at turnover, so near that temperature the resolution collapses to nothing. It is a good "
 "thermometer at the extremes and a useless one in the middle — the exact opposite of what you "
 "usually want.",
 "Nothing. Zero parts. It is a firmware read.",
 "The parabola's flat region, crystal-to-crystal variation in turnover point (each board needs "
 "its own two-point calibration), and self-heating from the ESP32 itself.",
 "Nobody frames a radio's frequency-offset register as a sensor. It will never beat a $2 "
 "thermometer, but for detecting that a sealed, potted, already-deployed node has gone outside "
 "its temperature envelope, it costs nothing and needs no new hardware."),

("MARGINAL", "Compressor health from the mains voltage dip at start",
 "The condition of any large motor in a building — fridge, pump, compressor, air conditioner — "
 "measured from a single socket anywhere on the same circuit.",
 "A motor's locked-rotor inrush is 5-8× its running current, and that surge pulls the local "
 "supply voltage down through the wiring impedance. The DEPTH of the dip scales with inrush "
 "current and the RECOVERY TIME with how quickly the rotor reaches speed. A motor with worn "
 "bearings or failing start capacitor takes longer to spin up, and says so in the voltage.",
 "A domestic circuit has perhaps 0.4 Ω of source impedance. A 10 A inrush therefore produces a "
 "4 V dip on a 230 V supply — about 1.7%. A ZMPT101B sampled at a few kHz resolves that easily. "
 "The signature is unmistakable; the difficulty is attributing it to the right appliance.",
 "1 × ZMPT101B ($3) · ESP32 sampling at 4 kHz · a mains-powered node anywhere on the circuit.",
 "Attribution. Every motor on the circuit produces a dip, and telling them apart needs their "
 "start signatures learned first. Grid-side events look similar. A stiff supply (short runs, "
 "large cable) shrinks the dip toward the noise.",
 "Power-quality analysers see this and cost thousands; NILM research focuses on steady-state "
 "signatures rather than start transients. The transient is far more diagnostic of mechanical "
 "health and nobody at hobby level looks at it."),

("DEAD", "Wi-Fi rain gauge",
 "Rainfall rate from the attenuation of an existing 2.4 GHz link between two nodes.",
 "Water absorbs microwaves, so rain between two antennas attenuates the link. Commercial "
 "microwave backhaul links are genuinely used this way for city-scale rainfall mapping, which is "
 "what makes the idea tempting.",
 "The arithmetic kills it. Specific attenuation from rain at 2.4 GHz is roughly 0.01-0.02 dB/km "
 "at 25 mm/h. Over a 50 m garden path that is 0.001 dB — about a thousandth of the "
 "packet-to-packet RSSI noise, and RSSI is typically quantised to 1 dB in the first place. The "
 "commercial technique works because those links run at 15-40 GHz, where attenuation is 100-1000× "
 "higher, over paths of kilometres.",
 "n/a",
 "Physics. Not implementation.",
 "Recorded so nobody re-derives it. The correct lesson is the one in cheat code 18: waves grip "
 "targets near their own size, and a 12.5 cm wave barely notices a 2 mm raindrop. If you want "
 "rain from RF, you need a much shorter wavelength — 24 GHz radar modules in the catalog will "
 "see it, 2.4 GHz never will."),

("DEAD", "Occupancy from building resonance",
 "How many people are in a room, from the shift in the floor's natural frequency as their mass "
 "loads it.",
 "Cheat code 40 is sound: a structure's eigenfrequency is set by mass and stiffness, ambient "
 "excitation rings it constantly, and adding mass lowers the pitch. So people should be weighable "
 "by listening to the floor.",
 "The arithmetic kills it for a building. A domestic floor bay has an effective modal mass of "
 "order 1000-2000 kg. Adding one 70 kg person shifts frequency by roughly −½·(70/1500) ≈ −2.3%, "
 "which sounds detectable — until you note that the same floor's frequency moves by several "
 "percent with humidity, temperature and where the furniture is, and that a person standing "
 "still versus walking changes the damping more than the mass changes the frequency. The signal "
 "is real and the confounds are larger.",
 "n/a",
 "Confound magnitude, not sensitivity.",
 "Worth recording because the idea keeps reappearing. It DOES work on structures with small "
 "modal mass and stable conditions — a footbridge, a scaffold plank, a hospital bed frame. Bed "
 "occupancy by resonance is genuinely viable; room occupancy by floor resonance is not."),

("DEAD", "Battery internal resistance as a thermometer",
 "Cell temperature from the change in its internal resistance, with no thermistor.",
 "Internal resistance falls as a cell warms because electrolyte conductivity and reaction "
 "kinetics both improve. So measure resistance, infer temperature, and delete a component.",
 "The arithmetic kills it on confounds. Internal resistance changes by roughly 1-2% per °C — a "
 "usable sensitivity in isolation. But it ALSO changes by 20-40% across state of charge, and it "
 "rises by 50-200% over the cell's life. Temperature is a small term inside two much larger ones "
 "that you would have to know precisely first, and if you knew those you would not need the "
 "thermometer.",
 "n/a",
 "Confounds an order of magnitude larger than the signal.",
 "Recorded because it is a good demonstration of cheat code 12 failing: the confound IS a sensor, "
 "but only when it is the LARGEST term. Here temperature is the smallest of three, so the "
 "inversion is hopeless. A 30-cent NTC ends the discussion."),
]

METHOD = [
 ("How these were derived",
  "Each started as a measurement problem, not a part. The procedure was: name the quantity "
  "physically, find which of the six energy domains it lives in, look up the transduction grid "
  "for a door to electrical, apply the cheat codes to look for an indirect route, and THEN do "
  "the arithmetic before touching a catalogue. Roughly half died at the arithmetic step."),
 ("Why the dead ones are here",
  "An inventor's notebook containing only successes is a marketing document. The Wi-Fi rain gauge "
  "took ten minutes to kill and would have taken a season to fail in a garden. The three dead "
  "entries below each cost one calculation and each saves someone a project."),
 ("What they have in common",
  "Every live entry replaces an expensive instrument with an indirect route through cheap parts, "
  "and every one exists because a well-funded industry solved the same problem a different, more "
  "profitable way. The gaps in the world are not where the physics is hard; they are where the "
  "business case was absent."),
 ("How to add your own",
  "Run the same loop. State the quantity. Find the domain. Look for the indirect door. Estimate "
  "the signal AND the largest confound, and compare them — if the confound is bigger, you are "
  "done, and you have saved yourself the build. Record the death alongside the birth."),
]
