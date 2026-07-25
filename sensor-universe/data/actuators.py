"""Actuators & Outputs — everything that changes the world.

v5 catalogued 238 ways to measure and zero ways to act, which makes it a
observation instrument rather than an invention one. Sense -> decide -> ACT.

`pair` names the sensor that closes the loop on each actuator, because an
actuator without feedback is a guess.
"""

PARTS = [

# ================================================================ ROTATION
dict(catalog="actuator", n="Hobby servo (SG90 / MG996R)", pn="SG90 (9g) / MG90S / MG996R",
 cat="Position & Rotation", sub="Positional servo", modality="Mechanical",
 phenomena=[], inferences=[],
 meas="Absolute angular position 0-180°, held under load",
 how="A DC motor, a gearbox and a potentiometer in a closed loop: you send a pulse whose WIDTH "
     "(1-2ms, repeated every 20ms) encodes the target angle, and internal electronics drive the "
     "motor until the pot agrees. The pulse is a position command, not a speed command.",
 range="0-180° (continuous-rotation variants give speed instead)", accuracy="±1-3° typical, worse under load",
 rate="~50Hz update", iface=["PWM"], v="4.8-6V (MG996R up to 7.2V)", logic_3v3=True, pins=1,
 esp32_compat="Use the LEDC peripheral, not delay-based bit-banging. 3.3V logic drives most servos "
 "fine, but the SERVO POWER must never come from the ESP32's 3.3V rail.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="SG90 ~100-250mA moving, ~700mA stall; MG996R ~500mA-2.5A stall", pwr_ua=250000.0,
 usd=2.0, buy=["AE", "AMZ", "AF", "SF", "DFR"], brd="SG90 plastic gear, MG90S metal gear, MG996R high torque",
 lib="ESP32Servo, ledcWrite", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Stall current is several times running current and will brown out an ESP32 sharing the "
       "supply — this is the single most common cause of 'my board reboots when the servo moves'. "
       "Give servos their own supply with a common ground and a big electrolytic close to them. "
       "Cheap servos jitter at rest because the pot is noisy; detach the signal when you don't "
       "need holding torque. They have no feedback to you: the ESP32 knows what it COMMANDED, not "
       "where the horn actually is, so a jammed servo looks identical to a happy one.",
 hazard=["Mechanical"], calibration="One-point", consumable="Plastic gears strip under shock load",
 requires="A separate 5-6V supply rated for stall current, plus a common ground",
 substitutes="Stepper for open-loop precision without a gearbox; AS5600 + gimbal motor for silent "
             "closed-loop; linear actuator for straight-line motion",
 diff=1, use="Robot joints, camera pan/tilt, valve and damper actuation, latches, animatronics.",
 spark="Add an AS5600 magnetic encoder on the output horn and you finally learn whether the servo "
       "reached the angle you asked for — turning an open-loop guess into a closed-loop system.",
 pair="AS5600 for true position feedback; ACS712 to detect stall by current", tags=["Robots", "Play", "Home"]),

dict(catalog="actuator", n="Stepper motor + A4988/DRV8825 driver", pn="NEMA17 + A4988 / DRV8825",
 cat="Position & Rotation", sub="Open-loop stepper", modality="Mechanical",
 phenomena=[], inferences=[],
 meas="Precise incremental rotation — typically 200 full steps per revolution, microstepped to thousands",
 how="Two coils energised in sequence pull a toothed rotor from tooth to tooth. Count pulses and "
     "you know the angle — as long as the motor never misses a step, which it does silently if you "
     "over-accelerate or overload it.",
 range="Continuous rotation, 1.8° per full step", accuracy="±5% of a step, non-cumulative",
 rate="Up to a few thousand steps/s with acceleration ramps", iface=["Digital"],
 v="Motor 12-24V; logic 3.3-5V", logic_3v3=True, pins=2,
 esp32_compat="STEP/DIR needs only two pins. Use hardware timers or the RMT peripheral for smooth "
 "pulse trains — software stepping stutters when Wi-Fi interrupts.",
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 pwr="0.5-2A per phase, continuous even when stationary (holding current)", pwr_ua=1000000.0,
 usd=12.0, buy=["AE", "AMZ", "DFR", "SF"], brd="A4988 (simpler), DRV8825 (higher current), NEMA17 motors",
 lib="AccelStepper, FastAccelStepper (ESP32 hardware-timed)", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="The current-limit potentiometer must be set with a multimeter before first use — ship it "
       "wrong and you either lose torque or cook the motor and driver. Steppers draw full current "
       "while HOLDING position and get hot doing nothing. Missed steps are silent and cumulative: "
       "the position you think you are at drifts away from reality with no error flag, which is why "
       "3D printers home before every print. Never disconnect a motor while the driver is powered "
       "— the inductive kick destroys the driver.",
 hazard=["Mechanical", "HotSurface"], calibration="One-point",
 consumable="None; drivers fail if the current limit is set too high",
 requires="Current limit set via Vref measurement; a 100µF+ capacitor across the motor supply; "
          "limit switches or an encoder for homing",
 substitutes="TMC2209 for silent operation and stall detection; closed-loop stepper if missed "
             "steps are unacceptable; servo for held position with less heat",
 diff=3, use="3D printers, CNC, camera sliders, precise dosing pumps, telescope mounts, blinds.",
 spark="Two steppers and a pen make a plotter; two steppers and a syringe make a laboratory dosing "
       "pump with microlitre resolution for a tenth of the lab price.",
 pair="Limit switches or inductive proximity for homing; AS5600 to detect missed steps", tags=["Robots", "Play", "Industry"]),

dict(catalog="actuator", n="TMC2209 silent stepper driver", pn="TMC2209",
 cat="Position & Rotation", sub="Silent stepper driver with stall detect", modality="Mechanical",
 phenomena=["force"], inferences=["machine-state", "obstacle-ahead"],
 meas="Stepper drive with near-silent operation and sensorless stall detection",
 how="StealthChop drives the coils with a smoothly varying voltage instead of hard current "
     "chopping, which moves the switching noise above hearing. StallGuard watches the motor's back-EMF "
     "and reports mechanical load — so the driver itself becomes a force sensor.",
 range="Up to 2A RMS per phase", rate="Up to 256 microsteps", iface=["Digital", "UART"],
 v="Motor 5-29V; logic 3.3-5V", logic_3v3=True, pins=3,
 esp32_compat="UART mode lets you set current and read StallGuard in software — far better than "
 "the potentiometer on an A4988.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="Set in software, typically 0.5-1.5A/phase", pwr_ua=800000.0,
 usd=8.0, buy=["AE", "AMZ", "AF", "DK"], brd="BigTreeTech TMC2209 v1.3, Watterott SilentStepStick",
 lib="TMCStepper, FastAccelStepper", link="https://www.analog.com/en/products/tmc2209.html",
 lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="StallGuard needs tuning per motor, per speed and per supply voltage, and it does not work "
       "at very low speeds where back-EMF is too small — sensorless homing that works at 40mm/s "
       "may fail completely at 5mm/s. StealthChop is quiet but produces less torque at speed than "
       "SpreadCycle; most firmware switches modes automatically and people then blame the driver "
       "for the noise.",
 hazard=["Mechanical"], calibration="Two-point",
 consumable="None", requires="UART wiring for software configuration; a motor supply capacitor",
 substitutes="A4988 if cost matters more than noise; closed-loop stepper for guaranteed position",
 diff=3, use="Silent blinds and curtains, 3D printers, anything indoors where a stepper whine is "
 "unacceptable, and sensorless limit detection.",
 spark="StallGuard means a motorised blind or gate can detect an obstruction — a pet, a hand — "
       "using nothing but the motor it already has. Safety sensing with zero added parts.",
 pair="Nothing needed for stall detect; add an encoder for absolute position", tags=["Home", "Robots", "Safety"]),

dict(catalog="actuator", n="DC motor + H-bridge (DRV8871 / TB6612)", pn="DRV8871 / TB6612FNG / L298N",
 cat="Position & Rotation", sub="Bidirectional DC drive", modality="Mechanical",
 phenomena=[], inferences=[],
 meas="Speed and direction of a brushed DC motor",
 how="Four switches arranged in an H let you reverse the voltage across a motor, and PWM on those "
     "switches sets average voltage and therefore speed. Everything from a robot wheel to a "
     "peristaltic pump is this.",
 range="TB6612: 1.2A/channel; DRV8871: 3.6A single", rate="PWM to ~100kHz",
 iface=["PWM", "Digital"], v="Motor 2.7-45V depending on part; logic 3.3V", logic_3v3=True, pins=3,
 esp32_compat="LEDC PWM. Avoid the ancient L298N — it drops ~2V and wastes it as heat; modern "
 "MOSFET bridges are far more efficient.",
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 pwr="Motor-dependent; stall current is the number that matters", pwr_ua=1000000.0,
 usd=5.0, buy=["AE", "AMZ", "AF", "SF", "DFR"], brd="Adafruit DRV8871, SparkFun TB6612, generic L298N",
 lib="Direct ledcWrite, or motor libraries", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Motor stall current can be five to ten times running current and is what actually sizes "
       "your driver and supply — sizing on running current is why drivers die. Brushed motors "
       "generate enormous electrical noise; without a capacitor across the terminals and a "
       "separate supply, an ESP32 nearby will reset or corrupt I2C. Motors have no position "
       "feedback at all, so 'run for 500ms' means different distances on a fresh battery and a "
       "flat one.",
 hazard=["Mechanical", "HighCurrent"], calibration="None",
 consumable="Brushes wear; expect hundreds to a few thousand hours",
 requires="Flyback protection (built into modern drivers), a motor-side capacitor, a supply rated "
          "for stall current",
 substitutes="BLDC + FOC for silent, efficient, controllable torque; stepper for open-loop position",
 diff=2, use="Robot drive wheels, pumps, fans, winches, conveyor belts, gates.",
 spark="Add a current sensor to the motor supply and the H-bridge becomes a torque sensor: you can "
       "tell an empty peristaltic tube from a blocked one without any extra mechanism.",
 pair="ACS712 or INA226 for stall/torque detection; encoder for closed-loop speed", tags=["Robots", "Industry", "Play"]),

dict(catalog="actuator", n="BLDC gimbal motor + SimpleFOC", pn="GM2804 / GM3506 + SimpleFOC driver",
 cat="Position & Rotation", sub="Field-oriented BLDC", modality="Mechanical",
 phenomena=["angle-absolute", "force"], inferences=["machine-state"],
 meas="Smooth, silent, precisely controlled torque and position from a brushless motor",
 how="Field-oriented control continuously computes the ideal current vector from the rotor angle, "
     "so torque is smooth and directly commandable rather than a side effect of speed. With an "
     "encoder it becomes a motor you can program to feel like a spring, a detent or a wall.",
 range="Continuous rotation with absolute position via encoder", accuracy="Encoder-limited, typically 0.1°",
 rate="Control loops of 1-10kHz", iface=["PWM", "I2C"], v="12-24V typical", logic_3v3=True, pins=6,
 esp32_compat="ESP32 is the reference platform for SimpleFOC; the S3's speed helps the control loop.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="0.2-2A depending on torque demand", pwr_ua=600000.0,
 usd=30.0, buy=["AE", "AMZ"], brd="SimpleFOC Mini/Shield, gimbal motors, AS5600 encoder",
 lib="SimpleFOC (Arduino)", link="https://simplefoc.com/",
 lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="It will not run at all without a correctly aligned position sensor — FOC is meaningless "
       "without knowing rotor angle, and the alignment calibration must run at every power-up "
       "unless you store the offset. Gimbal motors have high winding resistance and low current "
       "ratings: they produce lovely smooth torque and very little of it, so they are wrong for "
       "driving wheels. Tuning the PID loops takes real time.",
 hazard=["Mechanical"], calibration="Two-point",
 consumable="None — brushless motors have no brushes to wear",
 requires="A magnetic encoder (AS5600 or AS5048A) rigidly coupled to the shaft, and a 3-phase driver",
 substitutes="Stepper for cheap position; hobby servo for simple angles; industrial servo if you "
             "need real power",
 diff=5, use="Haptic knobs and dials, camera gimbals, robot joints with force control, "
 "force-feedback controls, silent precision motion.",
 spark="A knob that renders physical feel in software: detents, end stops, springs and textures "
       "that change with the mode you are in. One piece of hardware, infinite control surfaces.",
 pair="AS5600 or AS5048A encoder (mandatory); current sensing for torque control", tags=["Touch", "Robots", "Play"]),

dict(catalog="actuator", n="Linear actuator", pn="12V linear actuator, 50-300mm stroke",
 cat="Position & Rotation", sub="Linear motion", modality="Mechanical",
 phenomena=[], inferences=[],
 meas="Straight-line push/pull, typically 50-1500N",
 how="A DC motor driving a leadscrew inside a tube. Self-locking under load, which means it holds "
     "position with the power off — the property that makes it right for windows and lids.",
 range="50-500mm stroke typical", rate="5-40mm/s", iface=["Digital", "PWM"],
 v="12V or 24V", logic_3v3=False, pins=2,
 esp32_compat="Needs an H-bridge or two relays; never drive directly from a GPIO.",
 contact="Contact", privacy="None", environment=["Indoor", "Outdoor"],
 pwr="1-5A depending on load", pwr_ua=3000000.0,
 usd=30.0, buy=["AE", "AMZ"], brd="Generic 12V actuators with internal limit switches",
 lib="Any H-bridge control", link="",
 lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="Most have internal limit switches at the ends of travel but NO position feedback in "
       "between, so mid-stroke positioning requires timing (unreliable) or an added sensor. Duty "
       "cycle is often only 20-25% — they are not designed to run continuously and will overheat. "
       "IP ratings on cheap units are optimistic; water entering the tube is the usual failure.",
 hazard=["Mechanical", "HighCurrent"], calibration="One-point",
 consumable="Leadscrew and gearbox wear under frequent cycling",
 requires="An H-bridge or relay pair rated for stall current, and a 12V supply",
 substitutes="A servo with a linkage for short travel; a stepper and leadscrew for precise positioning",
 diff=2, use="Automatic windows and vents, greenhouse louvres, TV lifts, adjustable furniture, "
 "gates, awnings.",
 spark="Automatic greenhouse vents driven by a real dew-point and CO2 calculation rather than the "
       "wax-cylinder openers everyone uses, which only know one thing and know it late.",
 pair="Hall or reed switches for end detection; SHT41 + SCD41 for the control logic", tags=["Home", "Grow", "Industry"]),

# ================================================================ FLUID & SWITCHING
dict(catalog="actuator", n="Solenoid valve (water)", pn="1/2\" 12V normally-closed solenoid valve",
 cat="Water & Liquid", sub="On/off fluid control", modality="Mechanical",
 phenomena=[], inferences=[],
 meas="Open/closed control of water flow",
 how="A coil pulls a plunger against a spring to open a port. Most irrigation valves are "
     "'servo-assisted': they need a minimum line pressure to open at all, which is why they work "
     "on mains and fail on a gravity-fed rain barrel.",
 range="Typically 0.02-0.8 MPa working pressure", rate="Full open/close in ~100ms",
 iface=["Digital"], v="12V or 24VAC coil", logic_3v3=False, pins=1,
 esp32_compat="Drive through a relay or MOSFET with a flyback diode. Never from a GPIO.",
 contact="Immersed", privacy="None", environment=["Outdoor", "Harsh"],
 pwr="Coil ~500mA at 12V, continuous while open", pwr_ua=500000.0,
 usd=8.0, buy=["AE", "AMZ", "DFR"], brd="Plastic irrigation valves, brass inline valves",
 lib="digitalWrite via driver", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Servo-assisted valves need minimum inlet pressure — on a gravity-fed tank they simply do "
       "not open, which catches out most rainwater projects. They are directional: fitted "
       "backwards they leak or refuse to close. The coil runs hot when held open for hours; "
       "latching valves exist precisely for battery irrigation. A flyback diode is mandatory or "
       "the inductive spike destroys your driver.",
 hazard=["Mechanical"], calibration="None",
 consumable="Diaphragm and seals perish; grit causes a valve that will not fully close",
 requires="A flyback diode, a relay or MOSFET, and enough inlet pressure for servo-assisted types",
 substitutes="Motorised ball valve for full-bore, zero-pressure-drop and fail-safe positions; "
             "latching solenoid for battery use",
 diff=2, use="Irrigation zones, automatic top-off, dosing, water features, appliance control.",
 spark="A valve plus a flow sensor is a closed loop: dispense exactly 4.7 litres and verify it "
       "happened, rather than opening for a guessed number of seconds.",
 pair="YF-S201 flow sensor to verify delivery; leak rope as a failsafe", tags=["Water", "Grow", "Home"]),

dict(catalog="actuator", n="Motorised ball valve", pn="1/2\"-1\" 12V motorised ball valve (CR-02/CR-05)",
 cat="Water & Liquid", sub="Full-bore fluid shutoff", modality="Mechanical",
 phenomena=[], inferences=["door-state"],
 meas="Full-bore open/closed with position feedback",
 how="A geared motor turns a real ball valve through 90°. Unlike a solenoid it works at zero "
     "pressure, has almost no flow restriction, holds position with the power off, and most "
     "versions report their state on two feedback wires.",
 range="Full bore, DN15-DN25 typical", rate="5-15 seconds to travel",
 iface=["Digital"], v="12V or 24V (some 230V)", logic_3v3=False, pins=2,
 esp32_compat="Two relays for CR-02 style (open/close lines), plus two GPIO inputs for feedback.",
 contact="Immersed", privacy="None", environment=["Indoor", "Harsh"],
 pwr="~300mA while travelling, zero when parked", pwr_ua=300000.0, pwr_sleep_ua=0.0,
 usd=20.0, buy=["AE", "AMZ"], brd="CR-02 (2-wire), CR-05 (5-wire with feedback)",
 lib="Relay control + feedback read", link="",
 lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="Wiring variants are genuinely confusing and mislabelled: 2-wire, 3-wire and 5-wire "
       "versions all exist under similar names, and reversing polarity on the wrong type stalls "
       "the motor. Travel takes seconds, so this is not an emergency shutoff for a burst pipe — "
       "it is a controlled shutoff. Valves that sit unused for months can seize; exercise them "
       "monthly in software.",
 hazard=["Mechanical"], calibration="None", consumable="Seals; seizing if never exercised",
 requires="Two relays (or a DPDT) and a 12V supply; feedback wires read via GPIO",
 substitutes="Solenoid valve for fast, cheap, pressurised-only control",
 diff=3, use="Whole-house water shutoff, heating zone valves, tank isolation, gas-free fluid systems.",
 spark="This is the actuator that makes the leak-detection projects in this catalog actually worth "
       "building: detection without shutoff just tells you about the flood you are already having.",
 pair="Flow sensor + presence sensor for the leak-brain logic", tags=["Water", "Safety", "Home"]),

dict(catalog="actuator", n="Peristaltic dosing pump", pn="12V peristaltic pump, silicone tubing",
 cat="Water & Liquid", sub="Precise liquid dosing", modality="Mechanical",
 phenomena=[], inferences=[],
 meas="Metered liquid delivery, typically 5-100 ml/min",
 how="Rollers squeeze a flexible tube in sequence, pushing liquid along without the pump mechanism "
     "ever touching it. That isolation is why it is used for chemicals, nutrients and anything "
     "that must not be contaminated.",
 range="5-150 ml/min depending on tube and speed", accuracy="±5-10% without calibration; ±1% with",
 rate="Continuous", iface=["PWM", "Digital"], v="12V typical", logic_3v3=False, pins=2,
 esp32_compat="Drive via H-bridge or MOSFET. PWM gives crude flow control; step-counting a stepper "
 "version gives real volumetric dosing.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="200-500mA", pwr_ua=350000.0, usd=15.0, buy=["AE", "AMZ", "DFR", "AT"],
 brd="Generic 12V DC peristaltic, Atlas Scientific EZO-PMP for metered dosing",
 lib="H-bridge control; Atlas EZO I2C for the metered version", link="",
 lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="The tube is the consumable and it is the whole accuracy story: as silicone takes a set the "
       "delivered volume per revolution falls, so a pump calibrated in January under-doses by "
       "spring. Recalibrate by weighing the output monthly. Running dry does not damage the pump "
       "but wears the tube fast. They are self-priming but slow to prime a long line.",
 hazard=["Mechanical"], calibration="Periodic",
 consumable="Silicone tube — weeks to months of continuous use; keep spares",
 requires="An H-bridge or MOSFET with flyback; food/chemical-grade tubing for the application",
 substitutes="Diaphragm pump for higher flow; syringe pump for laboratory precision; Atlas EZO-PMP "
             "if you want the dosing maths done for you",
 diff=2, use="Hydroponic nutrient and pH dosing, aquarium chemistry, brewing additions, laboratory "
 "sampling, automatic plant feeding.",
 spark="Weigh the receiving vessel with a load cell while dosing and the pump calibrates itself "
       "continuously — the tube can age all it likes and the delivered dose stays correct.",
 pair="pH and EC probes to close the chemistry loop; a load cell to verify delivered mass", tags=["Grow", "Water", "Play"]),

dict(catalog="actuator", n="Relay module (mechanical)", pn="SRD-05VDC-SL-C on a 1/2/4/8-channel board",
 cat="Power & Electrical", sub="Isolated switching", modality="Electrical",
 phenomena=[], inferences=[],
 meas="Switching of mains or high-current DC loads, galvanically isolated from the ESP32",
 how="A small coil pulls a physical contact closed. The mechanical gap is what gives real isolation "
     "between your 3.3V logic and a 230V load — the reason relays persist despite being slow and noisy.",
 range="Typically 10A at 250VAC (believe about half of that)", rate="~10ms to switch, ~10Hz maximum",
 iface=["Digital"], v="Coil 5V; boards accept 3.3V logic if opto-isolated", logic_3v3=True, pins=1,
 esp32_compat="Most cheap boards are ACTIVE LOW and energise during boot before your code runs — "
 "which switches your load on unexpectedly at every reset. Check this before wiring anything.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~70mA per energised coil", pwr_ua=70000.0,
 usd=3.0, buy=["AE", "AMZ", "DFR", "CE"], brd="1/2/4/8-channel opto-isolated relay boards",
 lib="digitalWrite", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="The 10A rating is for a resistive load; motors, transformers and LED drivers are inductive "
       "or capacitive and will pit the contacts far sooner — derate hard. Cheap boards frequently "
       "have inadequate creepage between mains and logic tracks; look at the PCB before trusting "
       "it near mains. Coils draw significant current, so an 8-channel board with everything on "
       "needs more than a USB port. Contacts weld closed as a failure mode, which means the safe "
       "assumption is that a relay can fail ON.",
 hazard=["Mains", "HighCurrent"], calibration="None",
 consumable="Contacts erode; ~100,000 operations at rated load, far fewer if inductive",
 requires="Adequate coil supply; for mains, proper enclosure, fusing and competence",
 substitutes="SSR for silent high-cycle switching; MOSFET for DC; smart plug if you would rather "
             "not touch mains at all",
 diff=2, use="Lights, pumps, heaters, appliances, irrigation valves, anything needing isolation.",
 spark="Before wiring mains, consider whether a commercial smart plug flashed with ESPHome does "
       "the job — it is a certified enclosure with the relay already inside, and it costs less "
       "than doing it properly yourself.",
 pair="Current sensor on the switched load to confirm it actually turned on", tags=["Home", "Industry", "Safety"]),

dict(catalog="actuator", n="Solid-state relay (SSR)", pn="SSR-25DA / SSR-40DA, or a PCB-mount SSR",
 cat="Power & Electrical", sub="Silent high-cycle switching", modality="Electrical",
 phenomena=[], inferences=[],
 meas="Silent, wear-free AC switching at high cycle rates",
 how="An opto-coupled triac or thyristor switches at the AC zero crossing. No moving parts means "
     "millions of operations and silent, fast cycling — which is what makes real PID temperature "
     "control possible.",
 range="25-40A rated (heatsink dependent)", rate="Zero-cross switching, many Hz",
 iface=["Digital", "PWM"], v="Control 3-32VDC; load 24-380VAC", logic_3v3=True, pins=1,
 esp32_compat="Drives directly from a 3.3V GPIO, unlike a mechanical relay coil.",
 contact="Contact", privacy="None", environment=["Indoor", "Harsh"],
 pwr="~10mA control current", pwr_ua=10000.0,
 usd=8.0, buy=["AE", "AMZ", "DK"], brd="Fotek-style panel SSRs (many counterfeit), Crydom, Omron",
 lib="digitalWrite or slow PWM", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="A 40A-rated SSR without a heatsink is a 5A SSR — they dissipate roughly a watt per amp and "
       "thermal failure is the normal failure mode. Counterfeit Fotek units are endemic and are "
       "rated far below their markings; buy from a distributor for anything that matters. SSRs "
       "fail SHORT (permanently on), which is the dangerous direction for a heater, so a "
       "mechanical safety contactor or thermal cutout in series is not optional. They leak a few "
       "milliamps when off, enough to make a neon indicator glow. They do not switch DC unless "
       "specifically DC-rated.",
 hazard=["Mains", "HotSurface", "HighCurrent"], calibration="None", consumable="None",
 requires="A heatsink sized for the actual current, and an independent thermal cutout for any "
          "heating application",
 substitutes="Mechanical relay for DC or low cycle counts; triac dimmer for phase control",
 diff=3, use="PID temperature control, kilns, sous-vide, fermentation chambers, reflow ovens, "
 "heat mats.",
 spark="Slow PWM through an SSR gives genuine proportional heat control, which is the difference "
       "between a thermostat that overshoots by 5°C and a controller that holds 0.2°C.",
 pair="Thermocouple or RTD for the PID loop; a thermal cutout as the independent failsafe", tags=["Home", "Industry", "Grow"]),

dict(catalog="actuator", n="Logic-level MOSFET switch", pn="IRLZ44N / AO3400 / IRLB8721",
 cat="Power & Electrical", sub="DC switching", modality="Electrical",
 phenomena=[], inferences=[],
 meas="Fast, silent, efficient DC load switching from a GPIO",
 how="A voltage on the gate opens a channel between drain and source. With no moving parts and "
     "milliohms of resistance it can switch amps efficiently and at high frequency — which is what "
     "makes PWM dimming and motor speed control possible.",
 range="Tens of amps depending on part and heatsinking", rate="kHz to MHz",
 iface=["Digital", "PWM"], v="Load up to 30-55V; gate 3.3V for LOGIC-LEVEL parts only", logic_3v3=True, pins=1,
 esp32_compat="Must be a LOGIC-LEVEL MOSFET. A standard IRF540 will barely turn on from 3.3V and "
 "will overheat — this is the most common beginner failure with MOSFETs.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="Gate drive only, microamps in steady state", pwr_ua=100.0,
 usd=1.0, buy=["AE", "AMZ", "DK", "MO"], brd="Bare TO-220, or MOSFET breakout modules",
 lib="digitalWrite / ledcWrite", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="'Logic level' is the whole game and is often ignored: a non-logic-level MOSFET driven from "
       "3.3V sits half-on, dissipates heat and eventually fails. Always fit a 10k gate pull-down, "
       "or the gate floats at boot and the load switches on randomly. Inductive loads need a "
       "flyback diode. It switches the LOW side only, so the load's ground is not the system "
       "ground while off — which matters if anything else references it.",
 hazard=["HighCurrent"], calibration="None", consumable="None",
 requires="A gate resistor (~100Ω), a gate pull-down (10k), and a flyback diode for inductive loads",
 substitutes="Relay when you need isolation or to switch AC; a high-side switch IC when the load's "
             "ground must stay connected",
 diff=2, use="LED strips, heaters, fans, pumps, solenoids, and switching sensor power to cut sleep "
 "current.",
 spark="The single highest-value use in this catalog: switch your SENSORS' power with a MOSFET so "
       "a battery node draws microamps asleep instead of milliamps. It routinely multiplies "
       "battery life tenfold.",
 pair="INA219 to confirm the load actually drew current", tags=["Energy", "Home", "Play"]),

# ================================================================ THERMAL
dict(catalog="actuator", n="Peltier / TEC module", pn="TEC1-12706",
 cat="Temperature", sub="Solid-state heat pump", modality="Thermal",
 phenomena=[], inferences=[],
 meas="Moves heat from one face to the other — cooling below ambient without a compressor",
 how="Current through dissimilar semiconductors pumps heat from one ceramic face to the other. "
     "Reverse the current and it reverses direction, which makes it the only easy way to build a "
     "small controllable cooler.",
 range="ΔT up to ~60°C between faces under no load", rate="Seconds to respond",
 iface=["PWM"], v="12V", logic_3v3=False, pins=1,
 esp32_compat="Needs a high-current MOSFET or H-bridge; the current is far beyond any GPIO.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~5-6A at 12V for a TEC1-12706 — around 60W", pwr_ua=6000000.0,
 usd=5.0, buy=["AE", "AMZ"], brd="TEC1-12706 and larger; assembled cooler kits with heatsink and fan",
 lib="PWM via MOSFET", link="",
 lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="It is a heat PUMP, not a cooler: it moves heat plus all its own electrical waste, so the "
       "hot side dumps far more than the cold side removes. Without a serious heatsink and fan the "
       "hot side saturates and the cold side warms right back up — this is why most first Peltier "
       "projects fail. Condensation forms on the cold side and drips into your electronics. "
       "Thermal cycling cracks the internal junctions, so PWM it slowly or run it continuously "
       "with proportional voltage rather than switching hard.",
 hazard=["HotSurface", "HighCurrent"], calibration="None",
 consumable="Fatigues under repeated thermal cycling", requires="A heatsink and fan on the hot side "
 "sized for the FULL electrical input plus the pumped heat, thermal paste, and condensation management",
 substitutes="A compressor fridge for real cooling; a resistive heater if you only need heat",
 diff=4, use="Small sample coolers, dew-point condensation traps, cloud chambers, seed "
 "stratification, camera cooling, drink coolers.",
 spark="Cool a surface to exactly the dew point and you have a chilled-mirror hygrometer — the "
       "reference method for humidity, buildable from a Peltier, an IR temperature sensor and an "
       "optical detector.",
 pair="Thermistor or DS18B20 on both faces; PID control; a humidity sensor for dew-point work", tags=["Home", "Play", "Grow"]),

dict(catalog="actuator", n="PTC heater / heating film", pn="12V PTC heating element, silicone heat mat",
 cat="Temperature", sub="Resistive heating", modality="Thermal",
 phenomena=[], inferences=[],
 meas="Controlled heat input",
 how="Current through a resistance produces heat. PTC elements have the useful property that their "
     "resistance rises sharply at a design temperature, so they self-limit and cannot easily run "
     "away — which makes them far safer than plain nichrome.",
 range="Self-limiting types available at 60/110/220°C", rate="Seconds to tens of seconds",
 iface=["PWM", "Digital"], v="12V, 24V or mains versions", logic_3v3=False, pins=1,
 esp32_compat="MOSFET for DC, SSR for mains. Always with an independent thermal cutout.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="10-200W depending on element", pwr_ua=8000000.0,
 usd=8.0, buy=["AE", "AMZ"], brd="PTC elements with fins, silicone heat mats, reptile heat cable",
 lib="PWM/SSR control", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="A software thermostat is not a safety device. If the ESP32 crashes with the output on, or "
       "the temperature sensor falls off the surface it was reading, an unlimited heater becomes a "
       "fire — so use a self-limiting PTC element AND an independent mechanical thermal cutout in "
       "series. A sensor measuring air rather than the heated surface will always overshoot badly. "
       "Heat mats under plastic can melt it long before the air reaches setpoint.",
 hazard=["HotSurface", "HighCurrent", "Mains"], calibration="None", consumable="None",
 requires="An independent mechanical thermal cutout in series, plus a temperature sensor bonded to "
          "the heated surface rather than sensing air",
 substitutes="Peltier if you also need cooling; a heat pump for efficiency at scale",
 diff=3, use="Fermentation and proofing chambers, reptile enclosures, 3D-printer beds, seed "
 "propagation, dew-point defrosting, enclosure heating.",
 spark="A sealed outdoor enclosure with a tiny heater held just above dew point never fogs its "
       "optics or corrodes its contacts — the trick that makes outdoor camera and sensor boxes "
       "survive years instead of one winter.",
 pair="Thermocouple or DS18B20 bonded to the surface; a mechanical thermal cutout", tags=["Grow", "Home", "Safety"]),

dict(catalog="actuator", n="PWM fan with tachometer", pn="4-pin 12V PC fan (PWM + tach)",
 cat="Industrial & Automotive", sub="Airflow", modality="Mechanical",
 phenomena=["angular-rate"], inferences=["machine-running", "rotation-speed", "filter-clogged"],
 meas="Controllable airflow, with speed reported back",
 how="A brushless fan whose speed follows a 25kHz PWM duty cycle on a dedicated control pin, and "
     "which reports two tachometer pulses per revolution on another. The tach makes it one of the "
     "few actuators that tells you what it actually did.",
 range="Typically 500-2500 RPM", rate="25kHz PWM control", iface=["PWM", "Pulse"],
 v="12V (5V versions exist)", logic_3v3=True, pins=2,
 esp32_compat="LEDC at 25kHz for control; PCNT to count tach pulses with no CPU cost.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="50-500mA depending on size", pwr_ua=200000.0,
 usd=8.0, buy=["AE", "AMZ", "DK"], brd="Noctua, Arctic, generic 4-pin 120mm",
 lib="ledcWrite + PCNT", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="The PWM pin expects ~25kHz; drive it at 1kHz and the fan whines audibly. The tach output is "
       "open-collector and needs a pull-up to 3.3V — without one it reads nothing. Most fans stall "
       "below about 20% duty and will not restart until you kick them back up. Cheap 3-pin fans "
       "have no PWM input at all and must be speed-controlled by voltage instead.",
 hazard=["Mechanical"], calibration="None", consumable="Bearings; sleeve bearings last far less than ball",
 requires="A pull-up on the tach line; a 12V supply",
 substitutes="A blower for higher static pressure; an EC fan for large installations",
 diff=2, use="Enclosure cooling, filtration, fume extraction, grow tents, air quality response, "
 "sensor aspiration.",
 spark="Because it reports its own speed, a fan becomes a diagnostic: constant PWM with falling RPM "
       "means a clogged filter or a failing bearing, detected with no extra sensor at all.",
 pair="Differential pressure sensor across a filter; PM or CO2 sensors to drive the loop", tags=["Air", "MachineHealth", "Home"]),

# ================================================================ LIGHT
dict(catalog="actuator", n="WS2812B / SK6812 addressable LEDs", pn="WS2812B, SK6812 (RGBW)",
 cat="Light & UV", sub="Addressable RGB", modality="Optical",
 phenomena=[], inferences=[],
 meas="Individually controllable colour and brightness per LED on a single data wire",
 how="Each LED contains a tiny controller that reads the first 24 bits of the incoming stream, "
     "keeps them, and passes the rest on. Chain hundreds on one pin — the protocol is entirely "
     "timing-based, which is why it needs hardware help.",
 range="Hundreds of LEDs per chain", rate="~30fps for 500 LEDs", iface=["Digital"],
 v="5V (3.3V data is marginal — see below)", logic_3v3=True, pins=1,
 esp32_compat="Use the RMT peripheral (FastLED and NeoPixelBus do this) — bit-banging breaks when "
 "Wi-Fi interrupts. RMT channels are limited, so many parallel strips need care.",
 contact="Standoff", privacy="None", environment=["Indoor"],
 pwr="Up to 60mA per LED at full white — a 300-LED strip can demand 18A", pwr_ua=60000.0,
 usd=8.0, buy=["AE", "AMZ", "AF", "SF"], brd="Strips, rings, matrices, sticks; SK6812 adds a true white die",
 lib="FastLED, Adafruit_NeoPixel, NeoPixelBus, WLED", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Power is almost always underestimated: full white on a 5m strip needs a supply most people "
       "do not have, and injecting power only at one end produces a visible red-brown fade along "
       "the strip as voltage sags. 3.3V data into a 5V strip is marginal and works right up until "
       "it doesn't — the classic symptom is the first LED misbehaving or random flicker; fit a "
       "level shifter or power the strip at 4.5V. Always add a 300-500Ω series resistor on the "
       "data line and a large capacitor at the strip, or the first LED dies on power-up.",
 hazard=["HighCurrent"], calibration="None", consumable="Individual LEDs fail and break the chain "
 "downstream", requires="A 5V supply sized for peak brightness, power injection every 2-3m, a "
 "data-line resistor, a bulk capacitor, and a level shifter for long runs",
 substitutes="APA102/SK9822 use a clock line and are immune to timing problems; plain LED strip "
             "with MOSFETs when per-pixel control is not needed",
 diff=2, use="Ambient and status lighting, data visualisation, wearables, signage, stair lighting, "
 "installations.",
 spark="Use them as an instrument rather than decoration: a strip mapped to a single sensor's "
       "history turns an abstract number into something a whole household reads at a glance from "
       "the doorway.",
 pair="Any sensor at all — this is how measurements become visible", tags=["Play", "Home", "Light"]),

dict(catalog="actuator", n="High-power LED driver (constant current)", pn="MEAN WELL LDD-H / AL8860 / Recom",
 cat="Light & UV", sub="Constant-current driver", modality="Optical",
 phenomena=[], inferences=[],
 meas="Regulated current to high-power LEDs, dimmable by PWM",
 how="LEDs are current devices, not voltage devices — a tiny voltage change causes a huge current "
     "change. A constant-current driver fixes the current regardless of forward voltage, "
     "temperature or ageing, which is the only way to run power LEDs reliably.",
 range="350mA-1.5A typical per channel", rate="PWM dimming to kHz",
 iface=["PWM"], v="Input 9-56V", logic_3v3=True, pins=1,
 esp32_compat="PWM dimming input accepts 3.3V logic on most modules.",
 contact="Standoff", privacy="None", environment=["Indoor", "Harsh"],
 pwr="Driver efficiency ~90%; the LED consumes the rest", pwr_ua=1000000.0,
 usd=10.0, buy=["AE", "DK", "MO"], brd="MEAN WELL LDD-H series, AL8860 modules, Recom RCD-24",
 lib="ledcWrite", link="",
 lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="Driving power LEDs from a voltage source with a resistor works on the bench and fails in "
       "service: as the die warms its forward voltage drops, current rises, it warms further — "
       "thermal runaway. Power LEDs need real heatsinking; unheatsinked they lose output within "
       "minutes and die within hours. PWM dimming below a few percent gets non-monotonic on many "
       "drivers. Never disconnect the LED with the driver powered.",
 hazard=["Laser", "HotSurface", "HighVoltage"], calibration="None",
 consumable="LED output degrades over thousands of hours, faster when hot",
 requires="A heatsink sized to the LED's wattage, thermal interface material, and the driver's "
          "current set to the LED's rating",
 substitutes="Addressable strips for low power; mains LED fixtures with a triac dimmer for room lighting",
 diff=3, use="Grow lighting, machine vision illumination, underwater and dive lights, projection, "
 "UV curing, horticultural spectrum control.",
 spark="Independent drivers per LED colour give programmable spectrum: match a grow light to the "
       "plant's actual stage, or shift a room's colour temperature across the day on a real "
       "circadian curve rather than two presets.",
 pair="A PAR/quantum sensor to verify delivered light; a temperature sensor on the heatsink", tags=["Grow", "Light", "Play"]),

dict(catalog="actuator", n="E-paper display", pn="Waveshare 2.9\"/4.2\"/7.5\" e-Paper",
 cat="Cameras & Vision", sub="Bistable display", modality="Optical",
 phenomena=[], inferences=[],
 meas="A display that holds its image with zero power",
 how="Charged pigment particles move under an electric field and stay put. Power is needed only to "
     "CHANGE the image, which makes it the only display that suits a battery node that updates "
     "once an hour.",
 range="1.5\" to 12\"; mono, red/black, or 7-colour", rate="1-15 seconds for a full refresh",
 iface=["SPI"], v="3.3V", logic_3v3=True, pins=6,
 esp32_compat="Large panels need a decent framebuffer — an ESP32 with PSRAM is comfortable, a C3 "
 "is tight for anything above about 4 inches.",
 contact="Standoff", privacy="None", environment=["Indoor"],
 pwr="~20mA during refresh, ZERO holding the image", pwr_ua=20000.0, pwr_sleep_ua=0.0,
 usd=25.0, buy=["AE", "AMZ", "AF", "PI", "DFR"], brd="Waveshare and Good Display panels with HAT/driver boards",
 lib="GxEPD2, epdiy for large panels, LVGL", link="",
 lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="Refresh is slow and visibly flashes; anything animated is out. Leaving a static image "
       "indefinitely causes ghosting, so a periodic full refresh is required for panel health. "
       "Partial refresh is much faster but accumulates artefacts until you do a full one. Panels "
       "are fragile glass and dislike being flexed. Below about 0°C the particles move sluggishly "
       "and images smear — outdoor winter displays need care.",
 hazard=[], calibration="None", consumable="Panels degrade after very many refresh cycles",
 requires="A driver board matched to the exact panel; adequate RAM for the framebuffer",
 substitutes="OLED for small always-on status; TFT for colour and speed",
 diff=3, use="Battery dashboards, room signage, plant labels, weather displays, shelf labels, "
 "meeting-room status.",
 spark="Zero holding power means a display can live on a battery for a year — a garden sign that "
       "shows soil moisture and last watering, or a meeting-room CO2 sign, with no wiring at all.",
 pair="Any low-power sensor; deep sleep between updates", tags=["Home", "Energy", "Grow"]),

dict(catalog="actuator", n="SPI TFT display", pn="ILI9341 2.8\" / ST7789 1.3\" / ST7796 4\"",
 cat="Cameras & Vision", sub="Colour display", modality="Optical",
 phenomena=[], inferences=[],
 meas="Full-colour graphics, optionally with a touchscreen",
 how="A colour LCD driven over SPI, refreshed continuously from a framebuffer. Fast, cheap, and "
     "the default choice for anything handheld.",
 range="1.3\" to 4\", 240x240 to 480x320", rate="20-60fps over SPI at 40-80MHz",
 iface=["SPI"], v="3.3V", logic_3v3=True, pins=6,
 esp32_compat="ESP32-S3 with PSRAM handles full framebuffers comfortably; classic ESP32 manages "
 "with partial updates.",
 contact="Standoff", privacy="None", environment=["Indoor"],
 pwr="~40-120mA with backlight — the backlight is most of it", pwr_ua=80000.0,
 usd=10.0, buy=["AE", "AMZ", "AF", "DFR"], brd="Bare modules, or integrated boards like T-Display-S3",
 lib="TFT_eSPI, LovyanGFX, LVGL, Adafruit_GFX", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="The backlight dominates power and is usually on a separate pin you can PWM — many projects "
       "never do, and wonder why the battery lasts an hour. TFT_eSPI is configured by editing a "
       "header file in the LIBRARY folder rather than in your sketch, which surprises everyone "
       "once. Resistive touch overlays need calibration; capacitive ones need a separate I2C "
       "controller. Viewing angles on cheap TN panels are poor.",
 hazard=[], calibration="One-point", consumable="Backlight LEDs dim over years",
 requires="Correct library configuration for the exact controller and pin mapping",
 substitutes="E-paper for battery projects; OLED for small and simple; a smart display board to "
             "skip the wiring entirely",
 diff=2, use="Handheld instruments, thermal camera viewers, control panels, dashboards, games.",
 spark="A live thermal or spectral view turns an abstract sensor into an instrument you can hand "
       "to someone else — the moment a project stops being a demo and becomes a tool.",
 pair="MLX90640 thermal, AS7341 spectral, any sensor worth watching live", tags=["Play", "Industry", "Health"]),

dict(catalog="actuator", n="OLED display (SSD1306 / SH1107)", pn="0.96\" SSD1306 / 1.3\" SH1106",
 cat="Cameras & Vision", sub="Small monochrome display", modality="Optical",
 phenomena=[], inferences=[],
 meas="Crisp small monochrome text and graphics over I2C",
 how="Each pixel is its own organic LED, so black pixels emit nothing at all — perfect contrast, "
     "and power proportional to how much you light up.",
 range="0.66\" to 2.42\", 128x32 to 128x128", rate="Fast enough for simple animation",
 iface=["I2C", "SPI"], v="3.3-5V", logic_3v3=True, i2c_addr="0x3C / 0x3D", pins=2,
 esp32_compat="Any variant. Two wires shared with every other I2C sensor.",
 contact="Standoff", privacy="None", environment=["Indoor"],
 pwr="~10-20mA typical, less with a mostly-black screen", pwr_ua=15000.0,
 usd=3.0, buy=["AE", "AMZ", "AF", "SF", "CE"], brd="Ubiquitous 0.96\" I2C modules",
 lib="Adafruit_SSD1306, U8g2", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="OLEDs burn in: a static label left on for months leaves a permanent ghost. Shift the layout "
       "periodically or blank the screen. SH1106 controllers need a 2-pixel column offset that "
       "SSD1306 drivers do not apply, which produces the classic 'my display is shifted and wraps' "
       "problem — the modules are sold interchangeably. Address is 0x3C or 0x3D and collides with "
       "very little, but it does share the bus with everything else you own.",
 hazard=[], calibration="None", consumable="Blue and white OLED pixels dim over ~10,000 hours",
 requires="Nothing beyond I2C", substitutes="E-paper for zero standby; TFT for colour",
 diff=1, use="Status readouts, menus, debug output, small instruments, sensor displays.",
 spark="The fastest way to make a project feel finished: a device that shows its own state needs "
       "no laptop attached, which is what turns a breadboard into something someone else can use.",
 pair="Rotary encoder for menus; any sensor worth reading locally", tags=["Play", "Home", "Industry"]),

# ================================================================ SOUND & HAPTICS
dict(catalog="actuator", n="I2S DAC + amplifier (MAX98357A)", pn="MAX98357A",
 cat="Sound & Audio", sub="Digital audio output", modality="Acoustic",
 phenomena=[], inferences=[],
 meas="Clean digital audio to a speaker — speech, tones, music",
 how="Takes the ESP32's I2S digital audio stream, converts it and amplifies it in one chip. "
     "Class-D switching means little heat and no analog noise picked up from the ESP32's supply.",
 range="3.2W into 4Ω", rate="8-96kHz sample rates", iface=["I2S"], v="2.5-5.5V", logic_3v3=True, pins=3,
 esp32_compat="Any variant with I2S — which is all of them. Far better than the classic ESP32's "
 "internal DAC, which is noisy.",
 contact="Standoff", privacy="None", environment=["Indoor"],
 pwr="~2mA idle, up to 700mA at full output", pwr_ua=100000.0,
 usd=5.0, buy=["AE", "AF", "SF", "DFR"], brd="Adafruit MAX98357A breakout, generic modules",
 lib="ESP-IDF I2S, arduino-audio-tools, ESP8266Audio", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Class-D amplifiers are efficient but produce switching noise that couples into nearby "
       "analog sensors — keep it away from your ADC front end. It needs a real speaker, not a "
       "piezo buzzer. Peak current is high enough to brown out a marginal supply mid-word. The "
       "gain-select pin floating gives you a gain you did not choose.",
 hazard=[], calibration="None", consumable="None",
 requires="A 4-8Ω speaker and a supply able to handle transient peaks",
 substitutes="PCM5102 for line-level hi-fi output; a passive buzzer for beeps",
 diff=2, use="Voice prompts, alarms with spoken text, music, sonification, accessibility feedback.",
 spark="Spoken output changes who can use a device: a joint-angle sensor that SAYS the angle lets "
       "someone in physiotherapy keep their eyes on their body instead of a screen.",
 pair="Any sensor whose reading is more useful heard than seen", tags=["Health", "Play", "Safety"]),

dict(catalog="actuator", n="Piezo buzzer (active / passive)", pn="Active 5V buzzer / passive piezo element",
 cat="Sound & Audio", sub="Simple audible alert", modality="Acoustic",
 phenomena=[], inferences=[],
 meas="Beeps, tones and alarms",
 how="A piezoelectric disc flexes with applied voltage. ACTIVE buzzers contain an oscillator and "
     "beep at one pitch from a DC level; PASSIVE ones need you to supply the frequency, and can "
     "therefore play tunes.",
 range="Typically 2-4kHz resonance", rate="Instant", iface=["Digital", "PWM"],
 v="3-5V", logic_3v3=True, pins=1,
 esp32_compat="A passive buzzer on an LEDC channel gives you tones and simple melodies.",
 contact="Standoff", privacy="None", environment=["Indoor", "Outdoor"],
 pwr="~20-30mA", pwr_ua=25000.0, usd=1.0, buy=["AE", "AMZ", "SF", "CE"],
 brd="Active and passive modules; look for the resonant frequency in the datasheet", lib="tone() / ledcWriteTone",
 link="", lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Active and passive buzzers look identical and are constantly confused: driving an active "
       "one with PWM gives one pitch regardless, and driving a passive one with DC gives a click "
       "and then silence. Output is far louder at the element's resonant frequency, so an alarm "
       "tuned 500Hz away can be almost inaudible. A resonating enclosure changes the volume "
       "dramatically — mount it deliberately.",
 hazard=[], calibration="None", consumable="None",
 requires="A transistor for louder buzzers that exceed GPIO current",
 substitutes="I2S amp and speaker for anything that must convey more than urgency",
 diff=1, use="Alarms, confirmation beeps, timers, distance-to-pitch feedback, accessibility cues.",
 spark="Map a continuous sensor value to pitch and you get a Geiger-counter interaction: you hear "
       "the gradient while both hands and eyes stay on the task — the fastest possible feedback loop.",
 pair="Any sensor being used to search or aim", tags=["Safety", "Play", "Health"]),

dict(catalog="actuator", n="Haptic driver + LRA/ERM (DRV2605L)", pn="DRV2605L + LRA or ERM motor",
 cat="Touch & Capacitive", sub="Tactile feedback", modality="Mechanical",
 phenomena=[], inferences=[],
 meas="Precise vibration patterns — taps, buzzes, ramps, textures",
 how="A dedicated driver with a library of 123 tuned haptic effects and closed-loop control of the "
     "motor's resonance. The difference between a phone's crisp tap and a cheap toy's buzz is "
     "entirely this chip.",
 range="123 built-in effects plus arbitrary waveforms", rate="Millisecond-precise",
 iface=["I2C"], v="2-5.2V", logic_3v3=True, i2c_addr="0x5A", pins=2,
 esp32_compat="Any variant.", contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~50-100mA during an effect, µA idle", pwr_ua=75000.0, pwr_sleep_ua=2.0,
 usd=8.0, buy=["AF", "SF", "DK", "AE"], brd="Adafruit DRV2605L breakout with an LRA or ERM motor",
 lib="Adafruit_DRV2605", link="https://www.ti.com/product/DRV2605L",
 lifecycle="Active", maturity="Good", confidence="High", as_of="2026-07",
 fools="LRA and ERM motors need different driver configuration and auto-calibration — get it wrong "
       "and effects feel weak and muddy. LRAs only work at their resonant frequency, so a motor "
       "swap means recalibrating. The motor must be mechanically coupled to something with mass; "
       "loose on a bench it feels like nothing, and the same effect through a wrist strap is "
       "unmistakable.",
 hazard=[], calibration="One-point", consumable="ERM brushes wear; LRAs last far longer",
 requires="Auto-calibration run for the specific motor and mounting",
 substitutes="A plain vibration motor and a MOSFET if crudeness is acceptable",
 diff=2, use="Wearable alerts, silent notification, accessibility feedback, tactile UI, sensory "
 "substitution.",
 spark="Vibration is the only output channel that works when the eyes and ears are already busy or "
       "unavailable — which makes it the key to every sensory-substitution build in this catalog, "
       "from echolocation belts to navigation cues for cyclists.",
 pair="Distance sensors for sensory substitution; any wearable needing silent alerts", tags=["Health", "Touch", "Play"]),

# ================================================================ SPECIALIST
dict(catalog="actuator", n="Ultrasonic mist maker", pn="20mm / 16mm ultrasonic atomiser disc + driver",
 cat="Humidity & Moisture", sub="Atomisation", modality="Acoustic",
 phenomena=[], inferences=[],
 meas="Cold fog for humidification",
 how="A piezo disc vibrating at ~1.7MHz throws microscopic droplets off a water surface. No heat "
     "is involved, which is why it suits plants and mushrooms where a steam humidifier would cook them.",
 range="~300-500ml/hour per disc", rate="Instant on/off", iface=["Digital"],
 v="24V driver, 36V for some", logic_3v3=False, pins=1,
 esp32_compat="Switch the driver's supply with a relay or MOSFET; the disc itself needs its "
 "matched oscillator board.",
 contact="Immersed", privacy="None", environment=["Indoor"],
 pwr="~10-25W", pwr_ua=1000000.0, usd=8.0, buy=["AE", "AMZ"],
 brd="Disc plus matched driver PCB; float-mounted versions for varying water level", lib="Relay control",
 link="", lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="The disc must be submerged at a specific depth — usually 15-25mm — and it makes no fog "
       "either above or well below that, which is why floating holders exist. Running dry destroys "
       "the disc in seconds. Hard water leaves scale that kills output within weeks; distilled or "
       "filtered water roughly triples the life. The cold fog also raises the risk of condensation "
       "and mould in the chamber if there is no air movement.",
 hazard=["HighVoltage"], calibration="None",
 consumable="Disc erodes; weeks to months depending on water hardness",
 requires="A low-water cutoff, a fixed submersion depth, and air circulation to avoid condensation",
 substitutes="Evaporative humidifier for gentler control; a steam humidifier where sterility matters",
 diff=3, use="Mushroom fruiting chambers, propagation, terrariums, humidity control, fog effects.",
 spark="Held at 90% humidity with a tight hysteresis, a plastic tote becomes a mycology lab — the "
       "single build where precise humidity control produces the most visible difference in yield.",
 pair="SHT35 weatherproof probe for the control loop; a fan to prevent stagnation", tags=["Grow", "Home", "Play"]),

dict(catalog="actuator", n="Electric strike / solenoid lock", pn="12V fail-secure electric strike, solenoid latch",
 cat="Identity & Tags", sub="Access control", modality="Mechanical",
 phenomena=[], inferences=[],
 meas="Electrically released door latching",
 how="A solenoid retracts a latch or releases a keeper. FAIL-SECURE stays locked without power; "
     "FAIL-SAFE unlocks without power. Which one you choose is a fire-safety decision, not a "
     "convenience one.",
 range="n/a", rate="Instant", iface=["Digital"], v="12V", logic_3v3=False, pins=1,
 esp32_compat="Relay or MOSFET with a flyback diode; the inductive kick is substantial.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~500mA-1A while energised", pwr_ua=700000.0,
 usd=15.0, buy=["AE", "AMZ"], brd="Fail-secure strikes, cabinet solenoid latches, maglocks",
 lib="digitalWrite via driver", link="",
 lifecycle="Active", maturity="Good", confidence="Estimate", as_of="2026-07",
 fools="Fail-safe locks release in a power cut, which is required for escape routes and terrible "
       "for security; fail-secure does the opposite and can trap people. Getting this backwards is "
       "a safety and often a legal problem, not a preference. Continuous-duty and intermittent-duty "
       "solenoids are different parts — an intermittent one held energised overheats and burns out. "
       "The inductive spike will destroy an unprotected driver and can crash a nearby ESP32.",
 hazard=["Mechanical", "HighCurrent"], calibration="None",
 consumable="Solenoid coils and latch mechanisms wear",
 requires="A flyback diode, a supply rated for the inrush, a mechanical override, and a considered "
          "fail-safe/fail-secure choice",
 substitutes="A servo-driven latch for low-security cabinets; a commercial smart lock for a front door",
 diff=3, use="Tool cribs, cabinets, chicken coops, workshop doors, parcel boxes.",
 spark="Pair with the tool-crib RFID logic and the machine that must not be used untrained simply "
       "cannot be — the interlock is physical rather than advisory.",
 pair="RFID/NFC reader, fingerprint reader, reed switch to confirm the door actually closed", tags=["Access", "Safety", "Home"]),

dict(catalog="actuator", n="IR blaster LED", pn="940nm IR LED + transistor",
 cat="RF & Electromagnetic", sub="Remote control emulation", modality="Optical",
 phenomena=[], inferences=[],
 meas="Transmits infrared remote-control codes to existing appliances",
 how="Modulates a 940nm LED at ~38kHz with the same pulse patterns a remote uses. It lets an ESP32 "
     "control air conditioners, TVs and fans that have no network interface at all — a huge "
     "installed base of otherwise unreachable devices.",
 range="A few metres, line of sight (reflects off walls surprisingly well)", rate="38kHz carrier",
 iface=["PWM"], v="3.3-5V", logic_3v3=True, pins=1,
 esp32_compat="Use the RMT peripheral for accurate carrier timing — bit-banging is unreliable.",
 contact="Remote", privacy="None", environment=["Indoor"],
 pwr="~20-100mA in bursts, more for long range", pwr_ua=50000.0,
 usd=2.0, buy=["AE", "AMZ", "SF"], brd="Bare 940nm LEDs, IR blaster modules, ESP32 IR boards",
 lib="IRremoteESP8266 (huge protocol library), ESPHome remote_transmitter", link="",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="It is fire-and-forget: there is no acknowledgement, so the ESP32 never knows whether the "
       "air conditioner actually received the command. Air-conditioner protocols send the ENTIRE "
       "state (mode, temperature, fan, swing) in every message rather than deltas, so you must "
       "model the whole state, and if someone uses the physical remote your model is silently "
       "wrong. Range is poor without a driver transistor because a GPIO cannot supply enough current.",
 hazard=[], calibration="None", consumable="None",
 requires="A transistor and a current-limiting resistor for usable range",
 substitutes="A smart plug for simple on/off; a proper protocol integration if the device has one",
 diff=2, use="Air-conditioner control, TV automation, legacy appliance integration, fan control.",
 spark="An IR blaster plus a temperature sensor turns a dumb air conditioner into a properly "
       "controlled one — and a current clamp on its supply closes the loop, telling you whether "
       "the command was actually obeyed.",
 pair="A current clamp on the appliance to verify state; an IR receiver to learn the codes", tags=["Home", "Energy", "Access"]),

dict(catalog="actuator", n="Smart plug (ESPHome-flashable)", pn="Sonoff S31 / Athom / Tasmota-compatible plug",
 cat="Power & Electrical", sub="Certified mains switching", modality="Electrical",
 phenomena=["current-ac", "energy-accumulated"], inferences=["power-now", "device-left-on", "machine-running"],
 meas="Mains switching with energy metering, in a certified enclosure",
 how="A relay, a metering IC and an ESP chip inside a moulded, safety-tested plug. Reflashing it "
     "with ESPHome or Tasmota gives you local control and metering with no cloud account.",
 range="10-16A depending on model", rate="Instant switching, ~1Hz metering",
 iface=["Builtin"], v="Mains", logic_3v3=True, pins=0,
 esp32_compat="It IS an ESP device — you are replacing its firmware, not wiring to it.",
 contact="Contact", privacy="None", environment=["Indoor"],
 pwr="~1W standby", pwr_ua=300000.0, usd=12.0, buy=["AMZ", "AE"],
 brd="Sonoff S31, Athom plugs (ship with ESPHome), various Tasmota-compatible models",
 lib="ESPHome, Tasmota", link="https://esphome.io/",
 lifecycle="Active", maturity="Excellent", confidence="High", as_of="2026-07",
 fools="Manufacturers change the internal chip without changing the model number, so a plug that "
       "was flashable last year may ship with a non-ESP chip today — check the revision before "
       "buying in quantity. Some require opening the case and soldering; others flash over the "
       "air. Energy metering on cheap plugs is uncalibrated and can be 10-20% out until you "
       "correct it against a known load.",
 hazard=["Mains"], calibration="One-point", consumable="Relay contacts, as with any relay",
 requires="A compatible model and, for some, physical access to the serial pins",
 substitutes="A bare relay if you are competent and enclose it properly — but you lose the safety "
             "certification, which is the actual product here",
 diff=2, use="Appliance control and metering, phantom-load hunting, machine-state detection, "
 "anything mains that you would rather not build yourself.",
 spark="For most mains projects in this catalog this is the RIGHT answer: a certified enclosure "
       "with a relay and a metering IC for twelve pounds, running your firmware, is safer and "
       "cheaper than anything you would assemble.",
 pair="It is both actuator and sensor — the metering closes its own loop", tags=["Home", "Energy", "Safety"]),
]
