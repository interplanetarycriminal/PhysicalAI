"""Route-level commentary for the Inference Atlas.

The Atlas computes WHICH parts can answer a question. This file adds what no
computation can: the failure modes that belong to the METHOD rather than to any
one part, what the answer unlocks once you have it, and who cares enough to pay.

Not every inference needs a note — these are the ones where the naive approach
usually fails, or where the payoff is bigger than it first looks.
"""

NOTES = {
"someone-present": dict(
 fools="Every cheap route answers a subtly different question. PIR detects CHANGE in "
       "infrared, so it goes blind the moment you sit still — the classic 'lights off "
       "while I'm reading' failure. CO2 rise is unambiguous but lags by 10-20 minutes. "
       "A door sensor tells you someone crossed a threshold, not that they are still "
       "inside. mmWave sees breathing but also sees ceiling fans, curtains and rain on "
       "glass, and it sees through plasterboard into the next room unless you gate by zone.",
 unlocks="Presence is the keystone signal of every building: it gates lighting, HVAC, "
         "security, energy attribution and safety logic. Almost every other automation "
         "gets better once presence is reliable.",
 market="Smart home, facilities management, hot-desking, energy retrofits, hospitality"),

"someone-still-present": dict(
 fools="This is the question PIR fundamentally cannot answer, and the reason mmWave "
       "took over. But radar's sensitivity cuts both ways: at high gain it detects a "
       "sleeping person two rooms away through a stud wall. Tune the distance gates "
       "before you trust it, and expect to re-tune after you move the furniture.",
 unlocks="Rooms that stop switching the lights off on people who are reading, sleeping "
         "or working quietly — the single most-complained-about failure in smart homes.",
 market="Smart home, offices, hotels, care settings"),

"how-many-people": dict(
 fools="Counting is much harder than detecting. Two people walking abreast through a "
       "doorway read as one. A person pausing in the beam double-counts. Thermal blob "
       "counting merges people who stand close. Every counting route drifts over hours "
       "unless you periodically reset to a known-empty state — a nightly zero at 4am is "
       "usually the cheapest fix.",
 unlocks="Occupancy analytics without cameras: demand-controlled ventilation, room "
         "booking that reflects reality, retail footfall, and safe-egress counts.",
 market="Retail, museums, facilities, events, building services"),

"person-fell": dict(
 fools="The hard part is not detecting impact but rejecting everything that looks like "
       "it. Sitting down heavily, dropping the device, and a dog jumping on the bed all "
       "produce fall-shaped accelerometer signatures. Impact alone is not enough: the "
       "reliable pattern is impact FOLLOWED by prolonged stillness at floor level. "
       "Wearable routes fail because people don't wear them; radar routes work in "
       "bathrooms and at night, which is where falls actually happen.",
 unlocks="Independent living that families can accept. The privacy-safe routes matter "
         "enormously here — camera-based fall detection is refused by the people who "
         "most need it.",
 market="Elder care, assisted living, insurance, hospital estates"),

"who-is-it": dict(
 fools="Identity is the point where privacy law arrives. Tags identify the TAG, not the "
       "person carrying it. Biometrics identify the person but create sensitive personal "
       "data with real obligations. BLE phone presence is convenient and trivially "
       "spoofed. Be clear which one your build actually needs — most 'who' problems are "
       "really 'is this an authorised somebody' problems, which a tag solves without "
       "storing anything personal.",
 unlocks="Per-person automation, tool and machine authorisation, medication adherence, "
         "and attribution of energy or resource use.",
 market="Workshops, makerspaces, healthcare, access control, shared facilities"),

"bearing-failing": dict(
 fools="Absolute vibration numbers are almost meaningless — machines differ, mountings "
       "differ, and the same reading means different things on different days. Only the "
       "TREND against that machine's own baseline is informative. Sample rate is the "
       "other trap: bearing defect frequencies live in the kHz, so a 100Hz accelerometer "
       "sees nothing useful no matter how carefully you analyse it. Mounting matters more "
       "than the sensor: a magnet mount rolls off above ~2kHz, and double-sided tape is worse.",
 unlocks="Predictive maintenance — replacing parts on evidence rather than on a calendar "
         "or after a failure. The economics are unusually favourable: one avoided "
         "unplanned stoppage typically pays for instrumenting an entire workshop.",
 market="Manufacturing, facilities, HVAC contractors, makerspaces, agriculture"),

"which-appliance": dict(
 fools="Non-intrusive load monitoring is a genuinely hard, well-studied problem. Devices "
       "with similar power draws are near-indistinguishable from aggregate real power "
       "alone; the discriminating information is in the switch-on transient and the "
       "harmonic signature, which needs high-rate sampling rather than one reading a "
       "second. Variable-speed and inverter appliances defeat naive approaches entirely.",
 unlocks="Itemised energy without a smart plug on every device — and, more interestingly, "
         "activity inference: which appliance ran, when, tells you about the household's "
         "day without any sensor in a room.",
 market="Energy retailers, efficiency programmes, insurers, elder-care monitoring"),

"air-stuffy": dict(
 fools="Use real CO2, not 'eCO2' from a VOC sensor — eCO2 is inferred from unrelated "
       "chemistry and will happily report fresh air in a crowded room, or alarm because "
       "someone opened a bottle of solvent. Real NDIR and photoacoustic sensors need "
       "ambient-pressure compensation, and their automatic self-calibration assumes the "
       "room reaches ~400ppm at least weekly. In a continuously occupied space that "
       "assumption is false and the sensor slowly, silently under-reads.",
 unlocks="Ventilation you can argue about with evidence. CO2 is also the cleanest proxy "
         "for occupancy density and for airborne-infection risk in shared rooms.",
 market="Schools, offices, gyms, venues, landlords, ventilation contractors"),

"particulate-level": dict(
 fools="Optical particle counters measure how much light particles scatter, then convert "
       "to mass using an assumed particle density and refractive index. When humidity "
       "rises above roughly 75% the particles absorb water and swell, so the sensor "
       "over-reads badly — fog and morning dew read like smoke. Always log humidity "
       "alongside and correct, or your wildfire alarm will fire on a damp morning.",
 unlocks="Air-quality response that happens before you smell anything: purifiers that "
         "pre-empt smoke infiltration, and exposure maps that show which streets to avoid.",
 market="Households in wildfire regions, cyclists, asthma community, citizen science, councils"),

"water-leak": dict(
 fools="Point leak sensors only detect water that reaches the exact spot you put them. "
       "Flow-based detection catches leaks anywhere but needs a behavioural baseline to "
       "distinguish a running toilet from a long shower. The genuinely reliable signal is "
       "flow with no occupancy — that combination has almost no false positives.",
 unlocks="Automatic mains shutoff. Water damage is among the most common and most "
         "expensive household insurance claims, and this is one of the few sensing "
         "projects with an unambiguous financial return.",
 market="Homeowners, landlords, insurers, facilities, holiday properties"),

"plant-thirsty": dict(
 fools="Cheap resistive soil probes corrode away within weeks and measure salinity as "
       "much as water; use capacitive ones. Even capacitive readings are meaningless "
       "across different soils without per-soil calibration, because they respond to "
       "dielectric constant, which varies with soil type and compaction. The metric "
       "agriculture actually schedules on is soil water TENSION, not water content — "
       "how hard roots must pull, rather than how much water is present.",
 unlocks="Irrigation driven by plant need rather than a timer, and — via the decay "
         "curve between waterings — a health signal that appears days before wilting.",
 market="Growers, vineyards, orchards, greenhouses, serious gardeners"),

"machine-state": dict(
 fools="'Is it on' is easy; 'what is it doing' is where the value is, and a single "
       "threshold cannot express it. Current draw distinguishes idle from loaded from "
       "stalled, but only after you have recorded what normal looks like for that "
       "specific machine. Soft starters and variable-frequency drives flatten the "
       "signatures that make this work.",
 unlocks="Utilisation data that justifies (or refuses) capital purchases, jam detection "
         "that prevents damage, and the raw material for predictive maintenance.",
 market="Manufacturing, makerspaces, workshops, laundries, agriculture"),

"storm-approaching": dict(
 fools="Lightning detectors are notorious for false triggers: switching power supplies, "
       "fluorescent lamps, motor brushes and nearby electronics all produce impulses that "
       "look like a distant strike. Antenna tuning and noise-floor calibration are not "
       "optional, and the distance estimate is a statistical inference from signal "
       "energy, not a measurement — it is meaningfully wrong for individual strikes.",
 unlocks="Automatic protection with real financial value: retracting awnings, closing "
         "windows, unplugging equipment, and clearing pools and sports fields.",
 market="Homeowners, sports facilities, marinas, agriculture, outdoor events"),

"frost-tonight": dict(
 fools="Air temperature is the wrong signal — ground frost forms while the air is still "
       "several degrees above zero, because surfaces radiate heat to a clear sky and cool "
       "below air temperature. The informative measurement is sky temperature via an "
       "infrared thermometer pointed upward: a very cold sky reading means clear skies "
       "and strong radiative cooling. Cloud cover changes the answer completely.",
 unlocks="Frost warnings hours earlier and more locally than any forecast, which is the "
         "difference between covering the tomatoes and losing them.",
 market="Gardeners, vineyards, orchards, nurseries, growers"),

"consumable-remaining": dict(
 fools="Weight is the honest measure and almost nobody uses it. Load cells creep under "
       "sustained load and drift with temperature, so a scale left under a gas bottle for "
       "months needs periodic re-zeroing. Tare state must survive reboots or your readings "
       "become nonsense after a power cut.",
 unlocks="'Days remaining' rather than 'it's empty' — for gas bottles, filament, coffee, "
         "animal feed, brewing gas and reagents. Weight-over-time is one of the most "
         "underused household and workshop signals there is.",
 market="Households, workshops, makerspaces, hospitality, small farms"),

"tank-level": dict(
 fools="Every route has a characteristic failure. Ultrasonic has a blind zone near the "
       "sensor (typically 20-25cm) and is fooled by foam, steam and condensation on the "
       "transducer. Pressure-based depth needs a vent to atmosphere or it tracks the "
       "weather instead of the water. Capacitive through-wall sensors are defeated by "
       "residue and scale on the inside of the tank wall.",
 unlocks="Rainwater harvesting that pre-drains before a storm, dry-run pump protection, "
         "and any reservoir that should never run empty or overflow.",
 market="Rainwater harvesting, agriculture, marine and RV, hydroponics, industry"),

"radiation-dose": dict(
 fools="Radiation counting is statistical: short samples are inherently noisy, and a "
       "reading that doubles for one minute usually means nothing. Background varies with "
       "altitude, geology and even weather (rain washes down radon daughters and briefly "
       "raises readings). A Geiger tube tells you THAT something is radioactive; only "
       "spectroscopy tells you WHAT.",
 unlocks="A whole category of visible-invisible projects, plus genuine utility in "
         "identifying uranium glaze, thorium mantles and radon accumulation.",
 market="Educators, museums, rockhounds, science communicators, radon remediation"),

"through-wall-motion": dict(
 fools="This is the least mature route in the document and it deserves scepticism. Wi-Fi "
       "channel-state sensing works impressively in a controlled demonstration and "
       "degrades sharply with furniture changes, new devices joining the network, and "
       "anything moving outside the room. Treat published accuracy figures as an upper "
       "bound obtained under favourable conditions.",
 unlocks="Presence sensing with no sensor in the room at all — the endgame of invisible "
         "instrumentation, if it can be made robust.",
 market="Research, security, elder care, smart buildings"),

"hive-state": dict(
 fools="No single hive signal is interpretable alone. Weight rises with nectar flow but "
       "falls with foraging departures, so a daily rhythm is normal and only the trend "
       "matters. Acoustic signatures shift with temperature and time of day as much as "
       "with colony state. Opening the hive to verify changes the thing you are measuring.",
 unlocks="Swarm prediction, nectar-flow timing, and overwinter survival monitoring "
         "without disturbing the colony — a rare case where the sensing is genuinely "
         "kinder than the manual alternative.",
 market="Beekeepers, apiaries, agricultural research, conservation"),

"gas-leak": dict(
 fools="This is the inference where hobby sensing must know its limits. Cheap metal-oxide "
       "gas sensors are broadly cross-sensitive, drift substantially over months, need "
       "days of burn-in, and are heated elements — which makes them an ignition source, "
       "and therefore unsuitable for siting inside any volume where flammable gas can "
       "accumulate. They are useful for TRENDS in ventilated spaces.",
 unlocks="Awareness and data — early warning of a slowly failing regulator, or a map of "
         "how gas migrates through a building.",
 market="Only ever alongside certified detection. A certified alarm is the safety device; "
        "your build is the logger that sits next to it."),

"which-isotope": dict(
 fools="Energy resolution is everything and it is hard-won: temperature stability of the "
       "photodetector, light coupling to the crystal, and careful pulse shaping all "
       "matter more than raw counts. Cheap setups produce broad peaks that cannot "
       "separate nearby isotopes. Calibrate against known sources before believing any "
       "identification.",
 unlocks="Turning 'this is radioactive' into 'this is thorium-232' — a qualitative leap "
         "that makes mineral identification, ceramic testing and fallout archaeology possible.",
 market="Physics education, museums, mineral collectors, science communication"),

"soil-fertility": dict(
 fools="Be sceptical of cheap 'NPK' probes. They measure bulk electrical conductivity and "
       "infer nutrient content from it, which is not the same thing — conductivity "
       "responds to salinity, moisture and temperature as much as to nitrogen. Treat the "
       "numbers as relative trends within one plot, never as a substitute for a "
       "laboratory soil test.",
 unlocks="Fertiliser applied where and when it is needed, and a record of how a plot "
         "changes across seasons.",
 market="Growers, community gardens, agricultural education, smallholders"),

"vehicle-speed": dict(
 fools="Two-point timing is only as good as your clock and your geometry: a small error "
       "in the measured baseline propagates directly into the speed. Wide vehicles trip "
       "sensors at different points than narrow ones. If the data is meant to persuade "
       "anyone, document the method and the uncertainty, because the first response will "
       "be to question it.",
 unlocks="Evidence. Traffic-calming decisions respond to logged distributions far better "
         "than to complaints, and this is one of the few civic projects a resident can "
         "credibly run alone.",
 market="Residents' associations, schools, councils, urbanists"),

"body-temp-trend": dict(
 fools="Skin temperature is not core temperature and tracks the environment strongly. "
       "Trends within one person are informative; absolute values compared between people "
       "are not. Non-contact infrared thermometers are heavily affected by distance, "
       "angle, emissivity and any airflow across the target.",
 unlocks="Fever onset detection a day early, ovulation-window tracking, and heat-stress "
         "warning for outdoor workers and athletes.",
 market="Households, fertility tracking, occupational health, sports"),

"heart-variability": dict(
 fools="HRV is exquisitely sensitive to how you measure it. Motion artefacts corrupt "
       "optical routes; electrode contact quality dominates electrical ones. Values are "
       "not comparable between devices, between measurement windows, or between people — "
       "only against your own baseline, measured the same way, at the same time of day.",
 unlocks="A usable proxy for autonomic stress and recovery, which can drive lighting, "
         "notifications, training load or breathing feedback.",
 market="Athletes, wellness, occupational health, biofeedback and interactive art"),

"where-in-room": dict(
 fools="Coordinates look more precise than they are, and the digits are the trap. An LD2450 "
       "reports X and Y to a tenth of a metre while its cross-range accuracy at the field "
       "edge is half a metre or worse, and a stationary person's position swims 10-30 cm "
       "frame to frame - without zone hysteresis that jitter alone generates hundreds of "
       "spurious events an hour. Track IDs are not identities: two people crossing paths "
       "swap IDs, and anyone standing still is dropped and re-acquired as a new one, "
       "silently breaking dwell-time logic. Three targets is a hard firmware ceiling on the "
       "LD2450 and the RD-03D, and one person at close range splits into two tracks as head "
       "and torso return separately. All 24 GHz radar passes through plasterboard and "
       "glass, so the person outside the window becomes a target inside the room. BLE RSSI "
       "swings +/-10 dB on multipath alone - one metre or eight from the same beacon - and "
       "UWB carries a fixed antenna-delay offset of up to a metre until calibrated, with a "
       "positive non-line-of-sight bias. And at 4 m a person occupies about one AMG8833 "
       "pixel.",
 unlocks="Zone-level automation and analytics without a camera - lighting that follows the "
         "person, desk and space utilisation, queue and dwell measurement, and safety "
         "geofencing around machinery.",
 market="Smart buildings, retail analytics, hospitality, industrial safety, elder care"),

"entered-or-left": dict(
 fools="Direction is the hard part. Two-zone time-of-flight counting breaks on the cases "
       "that matter: two abreast count as one, a carried box as one or three, a "
       "stop-and-reverse in the doorway as a phantom entry - and because the "
       "region-of-interest coordinates are in mirrored SPAD space, almost every first build "
       "has entry and exit swapped. Radar track IDs are not identities: two people crossing "
       "paths swap IDs, anyone who stands still is dropped and re-acquired as a new ID, and "
       "a stationary person's reported position swims 10-30 cm frame to frame, which "
       "without zone hysteresis generates hundreds of spurious crossings an hour. PIR "
       "counts zone crossings, so it is far less sensitive to radial approach than to "
       "tangential motion and its rated 12 m assumes someone walking across the field "
       "rather than up the corridor at it - and it goes nearly blind as ambient temperature "
       "approaches skin temperature. And a 134.2 kHz implant lying perpendicular to the "
       "reader's field is simply invisible.",
 unlocks="Anonymous footfall and true occupancy without cameras: safe-egress counts, "
         "demand-controlled ventilation, and room booking that reflects reality.",
 market="Retail, museums, facilities, events, transport"),

"are-they-looking": dict(
 fools="Neither route answers the question asked. The Person Sensor detects FACES, and its "
       "'is facing' flag is coarse and flickers at the edges of the cone, so 'not looking' "
       "and 'not detected' become the same output — while it detects faces in photographs, "
       "posters and video calls with full confidence, and a window behind the subject "
       "blinds it completely. The Azoteq IQS7211/IQS263 route is not gaze at all: it senses "
       "body capacitance, its range depends on electrode size and the user's ground "
       "coupling rather than on the datasheet, and at useful sensitivity it picks up the "
       "whole person instead of a head. What you can honestly report is orientation, not "
       "attention.",
 unlocks="Attention-gated interfaces: a display that wakes when looked at rather than when "
         "approached, and exhibit analytics that log genuine dwell without a camera stream "
         "leaving the device.",
 market="Retail displays, museums, kiosks, digital signage, driver monitoring"),

"person-asleep": dict(
 fools="Every route infers sleep from stillness, and stillness is not sleep. Under-mattress "
       "ferroelectret film senses movement rather than airflow and cannot tell whose - a "
       "second person, a cat or a washing machine on spin all inject signal, an electric "
       "blanket couples mains hum straight into a gigaohm input node, and mattress "
       "construction dominates sensitivity, so a build that works on thin foam fails on a "
       "thick pocket-sprung bed. 60 GHz radar reads breathing well from a still supine "
       "subject at close range and produces confident nonsense otherwise: it emits a "
       "plausible heart rate rather than an unknown, and with two people in a bed it can "
       "report one person's breathing as the other's. 24 GHz presence radar sees through "
       "plasterboard and doors, so a sleep log may be tracking someone in the next room, "
       "and its static-presence path drops a motionless person after 30-60 seconds and "
       "reacquires them on a twitch. A quiet bedroom also sits at the microphone's own "
       "29-33 dB(A) noise floor. And none of these routes sees sleep stages.",
 unlocks="Sleep-quality trends and bed-exit alerts without a wearable or a camera, which is "
         "exactly what makes them acceptable in a bedroom at all.",
 market="Elder care, sleep wellness, hotels, insurers, veterinary"),

"no-movement-alarm": dict(
 fools="An alarm on absence inverts every sensor's weakness: a blind spot manufactures a "
       "false alarm, and an unnoticed detection resets the timer. PIR cannot see stillness "
       "at all, so a person reading quietly is indistinguishable from an empty room. "
       "Radar's static-presence path is still a change detector: a motionless person can "
       "drop out after 30-60 seconds and reappear on a twitch. 24 GHz also passes through "
       "plasterboard and ceilings, so the flat upstairs resets your timer all night, and a "
       "ceiling fan or rain down a window is genuine micro-motion. Pressure mats fail both "
       "ways: Velostat's hysteresis keeps loaded cells reading for tens of seconds after "
       "someone gets off, and its resistance falls with temperature, so body heat under a "
       "bed mat looks like increasing weight through the night. The bed sensor is the "
       "dangerous case, because silence read as safety is the whole risk: an empty bed "
       "produces the same flat trace as a subject in trouble, so an independent occupancy "
       "check is mandatory.",
 unlocks="Independent living that families can accept, and escalation that fires on a real "
         "change in routine rather than on a sensor going quiet.",
 market="Elder care, assisted living, housing associations, insurers, hospital estates"),

"routine-broken": dict(
 fools="The statistics are harder than the sensing, and the sensing is already unreliable. "
       "An HC-SR501 reports CHANGE, so an hour of stillness looks like an empty house — "
       "while sunlight crossing the floor, a heating vent, a cat and, unshielded beside an "
       "ESP32, the Wi-Fi transmit burst itself all fire it, so a motion log that correlates "
       "perfectly with your MQTT publish interval is a known failure rather than a routine. "
       "An LD1125H holds stillness and then sees through the wall, so a neighbour or a "
       "corridor joins the subject's routine unless the distance gates are set. A YF-S201 "
       "water-flow meter is the most specific signal in the set and is blind below about 1 "
       "L/min. Then the inference: 'different from usual' needs weeks of baseline and an "
       "explicit false-alarm budget, because alerting on a lie-in trains the family to "
       "ignore the system.",
 unlocks="Passive wellbeing monitoring an older person will actually accept at home, and a "
         "change signal — not an emergency alarm — that gives family a reason to phone "
         "before a crisis.",
 market="Elder care, assisted living, insurance, housing associations, healthcare"),

"occupancy-duration": dict(
 fools="The hard part is not detecting the person, it is deciding when they LEFT. An "
       "HC-SR501 cannot do it at all: it senses change in mid-IR, so a still person "
       "vanishes within the hold time, and the timeout you add to paper over that IS the "
       "measurement. mmWave sees stillness and then over-reaches — fans, curtains and rain "
       "on glass are all micro-motion, and 24GHz passes straight through plasterboard, so a "
       "lounge sensor holds 'occupied' on someone in the hallway; the LD2410's configurable "
       "1-1500s hold time smooths this over well enough that installs feel fine until you "
       "read the raw target stream. CO2 is unambiguous about humans and slow, and the "
       "SCD41's and MH-Z19C's automatic self-calibration assumes the room reaches ~400ppm "
       "weekly, which is false in a continuously occupied office. An nRF52 badge left in a "
       "drawer books the desk all week.",
 unlocks="Desk and room booking that reflects reality rather than calendars, "
         "demand-controlled ventilation, and the utilisation evidence behind any decision "
         "to reconfigure a floor.",
 market="Corporate real estate, facilities, coworking, hospitality, education"),

"queue-length": dict(
 fools="A queue is a count and a dwell time, and the routes are weak at both. Multi-target "
       "radar has a hard firmware ceiling of three tracks, so five people become three "
       "tracks jumping between bodies; one person at close range splits into two returns as "
       "head and torso reflect separately; and azimuth accuracy falls apart past roughly 45 "
       "degrees, where a target 3 m out can be reported a metre wide of the truth. Worse "
       "for this question, track IDs are not identities - anyone who stands still long "
       "enough is dropped and re-acquired as a new ID, and standing still is what queueing "
       "is, so any dwell-time logic built on ID continuity breaks silently on exactly the "
       "people you are counting. Vision routes are trained on your lighting and angle and "
       "degrade off both, judge each frame independently so a marginal person flickers in "
       "and out, and at single-digit frame rates miss anyone crossing in 200 ms. The honest "
       "build counts arrivals and departures at two lines - which fails the moment somebody "
       "leaves without being served.",
 unlocks="Staffing that responds to the queue rather than to the rota, and dwell-time "
         "evidence for service-level claims that currently rest on anecdote.",
 market="Retail, quick-service food, transport hubs, healthcare waiting rooms, events"),

"crossed-boundary": dict(
 fools="A crossing is directed; most routes report an interruption. A single beam cannot say "
       "which way, and invents crossings: a slow-edged phototransistor without a Schmitt "
       "trigger gives several counts per event, dust and cobwebs hold the output triggered, "
       "and an Omron E3Z pair with 10-100x excess gain shoots through thin cardboard. "
       "Two-zone time-of-flight counting breaks on the cases that matter - two abreast "
       "count as one, a carried box as one or three, a pause-and-reverse as a phantom entry "
       "- and the VL53L1X's ROI coordinates are in mirrored SPAD space, so most first "
       "builds have entry and exit swapped. Sunlight cuts that sensor from 4 m to under 1 "
       "m, and dark hair returns so little 940 nm that a head reads as no target. An "
       "LD2450's 10-30 cm jitter generates hundreds of spurious events an hour without zone "
       "hysteresis, and a UHF RFID portal reads the box next door. And a Type 4 light "
       "curtain's OSSD pair goes to a safety relay, never an ESP32: it pulse-tests itself "
       "to 0 V for 100-300 us.",
 unlocks="Directional counts and threshold events without a camera: footfall, occupancy, "
         "livestock movement, queue length, and the audit trail behind an access decision.",
 market="Retail, transport, facilities, agriculture, events, industrial safety (as "
        "monitoring only)"),

"heart-rate": dict(
 fools="Every route reports a number even when it is measuring nothing, and that is the "
       "failure that matters. Optical PPG on a MAX30102 is dominated by motion artefact — "
       "the reason every serious wearable pairs it with an IMU purely to throw beats away — "
       "and ambient light leaking around the sensor injects 100/120Hz lighting ripple that "
       "aliases into the pulse band, producing a rock-steady false heart rate with no "
       "finger present at all. Electrical routes are cleaner and more fragile: the AD8232 "
       "has no notch filter, and its DC-based leads-off detection reports 'connected' as "
       "soon as any resistance path exists, so dry electrodes look attached while the trace "
       "is noise. Radar is the weakest claim in the set — the MR60BHA2 keeps emitting a "
       "plausible number rather than 'unknown' when it loses the signal, which is the "
       "dangerous behaviour, because your logs look healthy.",
 unlocks="The anchor signal for everything else in wearable physiology — HRV, recovery, "
         "sleep staging, arrhythmia screening — and the one number a non-specialist will "
         "actually act on.",
 market="Wellness, sports, elder care, clinical research, biofeedback"),

"blood-oxygen": dict(
 fools="The calibration curve is the limit, and no hobby build has one. Saturation comes "
       "from a ratio of ratios mapped onto SpO2 by a curve from a controlled human "
       "desaturation study - the FDA's 2024 pulse-oximeter guidance describes at least ten "
       "participants and 200-plus paired points across 70-100 % SaO2, with accuracy "
       "root-mean-square under 3.0 % for transmittance sensors and 3.5 % for reflectance. "
       "Without that, the device emits a number with no defensible units. The pulsatile "
       "component is roughly 1-10 % of the DC level through a fingertip and 0.1-1 % at the "
       "wrist, so the MAXM86161 route divides two tiny noisy numbers whose errors do not "
       "cancel. Two-wavelength oximetry is also blind to carboxyhaemoglobin, which absorbs "
       "almost identically to oxyhaemoglobin at 660 nm, so a CO-poisoned person reads a "
       "reassuring 98 %. Motion swamps everything, and Sjoding et al. (NEJM 2020) found "
       "commercial oximeters over-estimated saturation about three times as often in "
       "patients with darker skin.",
 unlocks="Trend-level oxygenation for altitude, sleep and respiratory self-tracking - and, "
         "more usefully, an honest demonstration of why a medical-grade number is hard.",
 market="Wellness devices, sports and altitude training, engineering education, research "
        "prototyping"),

"breathing-rate": dict(
 fools="Almost every route measures chest MOVEMENT rather than air moving. Impedance "
       "pneumography on a MAX30001 or ADS1292R reads only about 0.5-2 ohms on a 300-800 ohm "
       "thoracic baseline, so a 1mm electrode shift changes amplitude more than a real "
       "change in tidal volume — and in obstructive apnea the chest heaves against a closed "
       "airway while nothing moves, which is the event people buy it for. An MR60BHA2 has "
       "the opposite blindness: a fan, a hanging plant in a draught or an aquarium pump all "
       "land in the 10-25 breaths/min band and produce a confident 'occupied and breathing' "
       "in an empty room. Stretch cords creep for tens of seconds and drift with body heat, "
       "so they give rate and never volume. Only a flow measurement sees air, and there the "
       "orifice equation is square-law, so resolution dies in the last 20% of the "
       "exhalation.",
 unlocks="Respiration is the most informative vital sign nobody measures at home: rate and "
         "its variability flag deterioration earlier than heart rate, and drive sleep "
         "staging and biofeedback.",
 market="Sleep tech, elder care, wellness, veterinary, clinical research"),

"breathing-stopped": dict(
 fools="None of the cheap routes detects the event people buy them for. Impedance "
       "pneumography and the under-mattress ferroelectret film measure the chest changing "
       "shape rather than air moving, and in obstructive apnoea the chest keeps heaving "
       "against a closed airway, so the trace looks like normal breathing throughout the "
       "event you were watching for. A nasal thermistor senses a temperature difference, "
       "not flow, so it fails when ambient air approaches body temperature, which is "
       "precisely the warm bedroom that matters, and mouth breathing bypasses it entirely. "
       "60 GHz radar recovers respiration well from a still supine subject and cannot "
       "distinguish a breathing human from any periodic motion in the 10-25 breaths per "
       "minute band and with two people in a bed it locks onto whichever chest reflects "
       "strongest. The shared dangerous failure is that silence reads as safety: an empty "
       "bed and a subject in trouble produce the same flat trace, so an independent "
       "occupancy check is mandatory in any alarm logic.",
 unlocks="Respiratory-rate and sleep-disturbance trends without a mask or a clinic, and "
         "early warning of deterioration in the trend rather than in the event.",
 market="Sleep research, elder care, veterinary, wellness - never a safety-critical alarm"),

"muscle-effort": dict(
 fools="Surface EMG has no absolute unit and never will. Move an electrode pair 1 cm along "
       "the arm and the amplitude changes several-fold, so nothing is comparable between "
       "sessions unless you mark the skin, and the same muscle re-electroded tomorrow gives "
       "a different scale factor. Crosstalk then answers a different question than the one "
       "you asked: forearm flexors and extensors sit millimetres apart, so a grip channel "
       "picks up wrist extension too. The signal also drifts within a session - sweat "
       "lowers skin impedance and raises the apparent amplitude, so a threshold set at "
       "minute one is wrong at minute thirty, while dry or aged electrodes push contact "
       "impedance into the hundreds of kilohms and mains hum converts from common-mode to "
       "differential and buries everything. The envelope outputs that make EMG easy add "
       "tens of milliseconds of deliberate smoothing, fine for a prosthetic grip and "
       "useless for anything rhythmically expressive. And force is not effort: EMG "
       "amplitude tracks activation, which rises with fatigue at constant force.",
 unlocks="Prosthetic and assistive control, biofeedback for rehabilitation, and ergonomic "
         "assessment of which muscle is actually doing the work in a task.",
 market="Prosthetics, physiotherapy, sports science, occupational health, interactive art"),

"joint-angle": dict(
 fools="An ink flex strip integrates curvature along its whole length, so a sharp 90-degree "
       "crease and a gentle 90-degree arc read differently, its resistance creeps "
       "permanently upward as the ink micro-cracks, and it spreads plus or minus 30 percent "
       "between units at the same angle - so last month's calibration is wrong and no two "
       "sensors agree. Carbon-rubber cord is worse: hysteresis of tens of percent means the "
       "reading depends on whether you are stretching or releasing, it keeps creeping for "
       "tens of seconds after motion stops, and body heat under a garment produces a slow "
       "upward drift. Even the good capacitive parts report the total bend of the strip, so "
       "they cannot separate joint rotation from translation of the mount, and a knee "
       "produces a blend of both unless one end floats. The IMU route swaps these problems "
       "for drift: differencing two IMUs gives a joint angle whose yaw has no absolute "
       "reference and walks degrees per minute, and indoors the magnetometer that would fix "
       "it is routinely 20-30 degrees wrong because of rebar and nearby DC current.",
 unlocks="Range-of-motion tracking for rehabilitation, ergonomic exposure assessment, and "
         "gesture gloves that stay calibrated for longer than one session.",
 market="Physiotherapy, sports science, occupational health, VR and animation, prosthetics"),

"gait-quality": dict(
 fools="Gait metrics are exquisitely sensitive to where the sensor sits and barely sensitive "
       "to who is wearing it. The on-chip engines are trained for a wrist: a BMI270 step "
       "counter on a torso or a walking frame counts hand gestures while seated and misses "
       "an escalator entirely, and an LSM6DSOX's machine-learning core still emits a class "
       "after you move it to a harness — just the wrong one. Every IMU conflates gravity "
       "with linear acceleration, and vibration above half the output data rate aliases "
       "straight into the stride band as convincing asymmetry. Pressure mats look direct "
       "and are not: Velostat crosstalks so a diagonal load reads as a cross, and "
       "hysteresis keeps cells loaded for tens of seconds after the foot lifts.",
 unlocks="Fall-risk screening that runs continuously rather than once a year in a clinic, "
         "and detection of the slow gait changes that precede a great many falls.",
 market="Elder care, physiotherapy, sports science, orthopaedics, insurance"),

"tremor-present": dict(
 fools="The answer is a frequency, so the sampling chain is the whole story, and almost "
       "every route aliases. An LSM6DSOX or BMI270 folds any vibration above half its "
       "output data rate into the band you care about, so a 26 Hz ODR near a running "
       "machine invents slow content that does not exist, and a BMA400's 800 Hz ceiling "
       "with no real anti-alias filter does the same higher up. Mounting compliance "
       "counterfeits too: double-sided foam tape behaves as a spring and adds a 50-200 Hz "
       "resonance that looks exactly like a mechanical fault. Then bias - an MPU-6050's "
       "gyro zero-rate offset is up to +/-20 deg/s from the factory, changes at every "
       "power-up and drifts about 0.03 deg/s per degC, so integrating it manufactures a "
       "slow phantom rotation, and an L3GD20H is additionally linear-acceleration sensitive "
       "at a fraction of a degree per second per g. And a MyoWare envelope is smoothed by "
       "tens of milliseconds, useless for anything rhythmic, while moving the electrode "
       "pair 1 cm changes amplitude several-fold.",
 unlocks="Objective, repeatable tremor records between clinic visits - enough to see whether "
         "a medication change or a fatigue state moved the amplitude, which recall and a "
         "five-minute appointment cannot.",
 market="Neurology research, telehealth, occupational health, assistive technology, "
        "precision trades"),

"posture": dict(
 fools="Posture is a shape and every route samples it at a handful of points. One IMU gives "
       "orientation, not configuration: the accelerometer cannot separate gravity from "
       "linear acceleration, and an LSM6DSV16X's game rotation vector has no absolute yaw "
       "and walks degrees per minute, so which way the torso faces is not recoverable — and "
       "indoors the magnetometer that would fix it is unreliable anyway. Multi-IMU rigs "
       "import a calibration burden, because an LSM6DSOX's machine-learning core trained on "
       "a collar still emits a class from a harness, just the wrong one. Pressure mats "
       "image posture and lie about it: Velostat crosstalks so a diagonal body reads as a "
       "cross, and hysteresis holds cells loaded for tens of seconds. A VL53L5CX's 64 zones "
       "are roughly 40cm across at 3m — enough for 'left half', nowhere near enough for a "
       "raised hand.",
 unlocks="Ergonomic feedback that works at a desk rather than in a gait lab, pressure-injury "
         "prevention, and fall context — a person on the floor is a different event from a "
         "person sitting down.",
 market="Occupational health, elder and hospital care, physiotherapy, sports, motion capture"),

"hydration-proxy": dict(
 fools="Neither route measures hydration. An AD5941 bioimpedance front end measures body "
       "water and then a population regression converts it on the assumption that fat-free "
       "mass is about 73% water — which is exactly the assumption that breaks when someone "
       "is dehydrated, so the technique is least reliable precisely where you want it, and "
       "wrong in a perfectly repeatable way. Electrode preparation dominates the rest: the "
       "same person measured ten minutes apart with electrodes re-applied can shift 20-40 "
       "ohms, and a two-wire measurement folds hundreds of ohms of contact impedance into "
       "the answer. Skin conductance is not hydration at all — EDA tracks sympathetic "
       "sweat, so a warm room or a deep breath produces a textbook-looking response, and "
       "roughly one person in ten barely responds.",
 unlocks="Fluid-balance trends for athletes, outdoor workers and dialysis patients, where "
         "the useful signal is a person's own day-to-day change rather than any absolute "
         "number.",
 market="Sports science, occupational health, elder care, clinical research"),

"stress-arousal": dict(
 fools="Every route measures a correlate of arousal, and arousal is not stress. "
       "Electrodermal activity is the cleanest signal and the most easily counterfeited: "
       "room temperature, effort, a cough, a deliberate deep breath or simply pressing the "
       "electrodes harder all produce textbook-looking responses — the deep breath being "
       "the classic demonstration that the polygraph channel can be gamed — and roughly one "
       "person in ten barely responds at all. Most cheap GSR modules get the physics wrong "
       "twice over, measuring resistance rather than conductance and applying an "
       "unregulated voltage that tracks the supply rail, so two identical modules disagree "
       "and neither number is in microsiemens. The response is also slow and blunt, with a "
       "1-3s onset and a 5-10s recovery that merges closely spaced events. And every "
       "consumer EEG 'attention' signal, ADS1299-based included, is one a jaw clench can "
       "counterfeit.",
 unlocks="Biofeedback that responds to the body rather than to a timer, workload monitoring "
         "for high-stakes roles, and interactive art that reads the room honestly.",
 market="Wellness, occupational health, sports, biofeedback and interactive art, research"),

"blink-or-eye-move": dict(
 fools="Every route here detects the corneo-retinal potential moving, not where the eye "
       "points. The DC-ish component that encodes gaze angle is what the front end's "
       "high-pass filter is built to remove, so blinks and saccade edges are reliable while "
       "a held gaze angle is not recoverable at all: a blink switch works, an eye tracker "
       "does not. Facial muscle is the dominant contaminant: jaw clenching swamps an EOG "
       "channel and an eyebrow lift mimics a blink almost perfectly, so a demo that appears "
       "to read intent is usually reading the face. On EEG-grade parts the relationship "
       "inverts and the blink becomes the artefact: a single blink saturates the frontal "
       "channels. Electrode impedance decides the rest: dry electrodes sit at 20-200 kOhm "
       "against the 5-10 kOhm clinical practice demands, and above roughly 10 kOhm "
       "common-mode mains hum converts to differential and buries the signal. And with a "
       "gain chain running to about 10,000, any DC offset from mismatched electrodes rails "
       "the output into a flat, plausible-looking line.",
 unlocks="Hands-free switching and accessibility input that works with the eyes closed and "
         "in the dark, plus drowsiness detection from blink rate and duration.",
 market="Accessibility, HCI research, automotive driver monitoring, interactive art"),

"step-count": dict(
 fools="A step counter is a peak detector on a filtered acceleration magnitude, and anything "
       "oscillating at walking cadence is a step to it. The on-chip pedometers are tuned "
       "for one mounting position - a wrist - so on a torso, in a pocket or on a collar the "
       "count becomes fiction: it counts hand gestures while seated and cobbles under a "
       "vehicle, and misses an escalator ride entirely, while the decision-tree engines "
       "that classify walking and running are trained on a single placement and, once "
       "moved, still output a class, just the wrong one. The low-power modes that make an "
       "always-on counter possible are the ones that lie most: at a 1.6 Hz output rate and "
       "12 bits there are one or two LSBs of noise on a 16 mg step, and a 10 Hz mode with "
       "about 5 Hz of anti-alias bandwidth folds a 50 Hz compressor down into a convincing "
       "slow wander. And steps are not distance: stride length varies with speed and "
       "terrain by tens of percent, so a kilometre figure carries that on top of the "
       "counting error.",
 unlocks="Activity trends that mean something against a person's or an animal's own history "
         "- mobility decline, rehabilitation progress, herd behaviour - rather than a "
         "number to compare between people.",
 market="Wellness and wearables, elder care, physiotherapy, veterinary and livestock, "
        "insurers"),

"sleep-stage-proxy": dict(
 fools="Nothing here stages sleep; the honest output is quiet or restless, not REM. Staging "
       "is defined by simultaneous EEG, eye movement and chin muscle tone, and every "
       "channel is weak here. An ADS1299-class front end records eye movement ten to a "
       "hundred times larger than the alpha rhythm, jaw and forehead muscle fill everything "
       "above 20 Hz, and a single blink saturates the frontal channels - and with dry "
       "electrodes at 20-200 kOhm against the 5-10 kOhm clinical EEG demands, mains hum "
       "converts to differential noise and buries what is left. Actigraphy conflates lying "
       "still with being asleep, and a BMI270's activity engine is tuned for a wrist, so on "
       "a torso it is fiction. A MAX30102's pulse waveform is swamped by any movement, and "
       "a 60 GHz vital-signs radar keeps emitting a plausible breathing rate under a duvet "
       "and locks onto whichever chest reflects strongest - dangerous because the logs look "
       "healthy. And a ferroelectret bed film senses movement, not airflow, so an "
       "obstructive apnea reads as normal breathing throughout.",
 unlocks="Night-to-night self-tracking that tells you honestly whether you were restless, "
         "when you settled and when you woke - enough to test a change in habit, and enough "
         "to know when to ask for a real study.",
 market="Consumer sleep tracking, wellness, occupational fatigue, research prototyping"),

"object-present": dict(
 fools="'Present' means something different to every modality. Reflectance routes like the "
       "VCNL4040 measure returned infrared rather than distance, so matte black at 3cm and "
       "a white wall at 15cm give the same count — and the Sharp GP2Y0A21 is worse, because "
       "its curve is double-valued and an object at 4cm reads identically to one at 40cm, "
       "so a robot closing on a wall sees 'plenty of room'. Time-of-flight is honest about "
       "distance and dishonest about status: VL53L0X sketches that skip RangeStatus print "
       "8190mm as though it were a measurement, so the build reads 'clear ahead' exactly "
       "when it has been blinded. An FDC2214 detects a dielectric, so condensation and a "
       "hand near the electrode both read as present. Weight on an HX711 is the most "
       "trustworthy and it creeps 0.02-0.05% of applied load in the first half hour.",
 unlocks="The foundation under inventory, tool control, safety interlocks and 'did I leave "
         "it behind' — the answer most other automation silently assumes it already has.",
 market="Manufacturing, retail, logistics, workshops, smart home"),

"object-identity": dict(
 fools="Tags identify the tag, cameras identify the appearance, and neither identifies the "
       "object. The identifier routes are trivially copied — the RC522's CRYPTO1 broken "
       "since 2008, the RDM6300's EM4100 forty bits in the clear, magic UID-writable cards "
       "sold for the purpose — and their physics fails in ways that present as faults: "
       "metal detunes 13.56MHz to nothing, water absorbs 900MHz so a tag on a full bottle "
       "barely reads, and an M6E-Nano's linear-polarised antenna loses about 20dB on a tag "
       "rotated 90 degrees, which looks exactly like a missing item. Vision routes return a "
       "softmax score rather than a probability, so 0.9 on a class the model has never seen "
       "is routine unless you deliberately train a background class. If the question is "
       "really 'is this the unit I logged', pair a tag with one corroborating physical "
       "property.",
 unlocks="Asset registers that stay true without stocktakes, provenance for tools and "
         "equipment, and warranty decisions based on the unit rather than on the paperwork.",
 market="Logistics, equipment hire, laboratories, libraries and archives, veterinary"),

"object-moved": dict(
 fools="Alarming on a change in tilt angle measures temperature as much as motion. Every "
       "MEMS accelerometer's zero-g offset drifts: an LIS3DH is +/-40 mg typical with 10 % "
       "sensitivity tolerance, an ADXL345 moves up to +/-150 mg across temperature, and "
       "even an ADXL355 drifts about 0.15 mg/degC per axis, roughly 0.01 degrees per degC - "
       "so most object-is-tilting plots are the diurnal temperature cycle, and the fix is "
       "to log temperature and regress it out, not to filter harder. The cheap threshold "
       "parts fail the other way: an SW-420 stops producing edges entirely under sustained "
       "vibration, so a machine running hard reads like one switched off, and a ball tilt "
       "switch's trip angle varies by 10 degrees between parts from one bag. A bike alarm "
       "armed at 20 mg fires on wind and passing lorries all night. A lift two floors away "
       "moves an MMC5603 by many times its noise floor. Optical flow cannot tell the object "
       "moving from the world moving underneath it. And an AS5600 or AS5048A is single-turn "
       "absolute, so a power cut mid-travel loses position silently.",
 unlocks="Asset tracking that reports the event rather than the position: tamper-evident "
         "shipping, unattended tool logs, and the movement history a loss adjuster or an "
         "auditor will accept.",
 market="Logistics, insurance, plant hire, museums and galleries, laboratories"),

"object-dropped": dict(
 fools="Free-fall detection is a threshold on vector magnitude, so it fires when someone "
       "with the device in a pocket sits down, and a brisk lift triggers it too. Bandwidth "
       "is where most builds silently fail: an impact lasts a couple of milliseconds, and "
       "at a default 100 Hz output rate the anti-alias filter smears it into almost "
       "nothing, so you need at least 1600 Hz plus the FIFO to record the peak at all. "
       "Range is the other half - a drop onto concrete is hundreds of g, so a plus or minus "
       "16 g part clips silently and a clipped sample destroys any integration or spectrum "
       "computed afterwards, while the plus or minus 200 g part that does not clip has a 49 "
       "mg LSB and is effectively blind below about 0.5 g. The number you record is then "
       "mostly a property of your mounting: the same impact reads around 100 g through a "
       "hard shell and 30 g through a foam liner, and part-to-part sensitivity tolerance of "
       "plus or minus 10 percent means a fleet of loggers disagrees by 20 g on one event. "
       "So peak g is comparable within one build and never between projects - and nothing "
       "maps g to damage.",
 unlocks="Shipping-damage evidence that survives a dispute, and handling data that "
         "identifies which leg of a route is breaking stock.",
 market="Logistics, insurers, electronics and glass shippers, laboratory equipment, sports "
        "safety"),

"object-count": dict(
 fools="Counting is far harder than detecting, and every route fails the same handful of "
       "cases: two people abreast count as one, a person carrying a large box as one or "
       "three, and someone who pauses and reverses generates a phantom entry. Optical "
       "routes go blind selectively rather than uniformly — dark hair returns so little "
       "940nm that a head reads as 'no target' while the shoulders read fine, and a sunlit "
       "patch of floor cuts a VL53L1X from 4m to well under 1m. Mechanical routes fail the "
       "other way: a reed switch bounces, so one event becomes five. And an M6E-Nano UHF "
       "reader reads straight through cardboard and plasterboard, so a doorway portal "
       "counts the box in the next room, while multipath means 'no read' never means 'not "
       "present'.",
 unlocks="Footfall, throughput and inventory movement without a camera — which is the "
         "difference between a counting system a workforce or a public accepts and one it "
         "does not.",
 market="Retail, events, manufacturing, logistics, conservation"),

"container-fullness": dict(
 fools="Choose the route by what is in the container. Ultrasonic has a blind zone - 20-25 cm "
       "on an HC-SR04, 25 cm on a JSN-SR04T, and the MB7389 reports its 30 cm dead band as "
       "300, indistinguishable from a target genuinely at 30 cm - so it goes blind when the "
       "vessel is nearly full. Foam absorbs the ping completely, so an aerated tank reads "
       "empty, which is the dangerous direction, and the speed of sound moves about 0.6 "
       "percent per degC, so a water butt swinging from 0 to 35 degC shifts a 2 m reading "
       "by roughly 12 cm. Capacitive strap-on switches see a dielectric change rather than "
       "liquid, so condensation, sludge or a hand on the puck all read as full, while oils "
       "near permittivity 2 rather than water's 80 often fail to trigger at any setting. "
       "Float switches are density devices: they sink in petrol and foam, and scale glues "
       "them to the stem. And hydrostatic routes measure depth times density, so a probe "
       "scaled in water reads about 16 percent low in diesel, while a blocked vent "
       "capillary makes the level track barometric pressure, turning a 30 mbar front into a "
       "phantom 300 mm.",
 unlocks="Reorder-before-empty for gas, feed, chemicals and rainwater; pump dry-run "
         "protection; and collection routing that only visits containers that are actually "
         "full.",
 market="Waste management, agriculture, hospitality, chemicals, rainwater harvesting"),

"door-state": dict(
 fools="The reed switch is the cheapest route and the most defeatable: any magnet held near "
       "it holds the contact closed, which is the classic alarm bypass. Contacts bounce for "
       "up to a millisecond so one opening counts as five; reeds are directional, so a "
       "magnet mounted 90 degrees round never closes them; and a slammed door eventually "
       "cracks the glass, after which 'not opened in three days' looks exactly like a quiet "
       "house. Tilt and angle routes tell you the leaf moved, not that the latch engaged. "
       "The barometric route is real physics — a BMP390 resolves about ±3Pa — but wind "
       "across an enclosure opening produces tens of pascals of Bernoulli suction, so a "
       "gust and an opened door are genuinely indistinguishable without a shielded static "
       "port.",
 unlocks="The keystone event for security, energy attribution and behaviour: HVAC that knows "
         "the door is open, fridge-ajar alerts, and the timestamps that make occupancy "
         "logic honest.",
 market="Smart home, security, facilities, cold chain, insurance"),

"object-material": dict(
 fools="Colour is not chemistry - two different dyes matched to the same colour are "
       "indistinguishable, and a board without IR-blocking glass reads every warm-lit "
       "surface far too red because silicon stays wide open past 700 nm. Filter-array NIR "
       "stops around 860-940 nm, short of the carbon-hydrogen overtones at 1100-1800 nm "
       "that would separate polymers, so it sees colour and surface finish: the same "
       "material reads differently glossy, matt or scuffed, and curvature changes the "
       "returned light more than material does. Inductive sensing genuinely discriminates "
       "metals - steel raises a coil's inductance while aluminium and copper lower it - but "
       "that same property makes a distance calibration silently wrong the moment the "
       "target metal changes, and the coil responds to the bench and a hand at 10 cm. The "
       "nuclear routes answer only whether something is radioactive: an SBM-20 is blind to "
       "alpha and poor below about 60 keV, and at 7 percent FWHM the 583 and 609 keV lines "
       "merge, so identification means matching a family of peaks against a library.",
 unlocks="Automated sorting on a known set, substitution and counterfeit checks, and mineral "
         "or ceramic identification that used to need a laboratory.",
 market="Recycling, scrap and metals trade, museums and collectors, manufacturing QC, "
        "education"),

"object-genuine": dict(
 fools="Only one of the two families here resists an attacker. Tag-based routes - NTAG, "
       "ST25DV, ISO15693 cards - answer with a number, and anyone who hears that number "
       "once can repeat it forever; a UID is an identifier, not a secret, and cloning is a "
       "commodity. A challenge-response secure element changes that, and its weaknesses are "
       "procedural: the configuration zone must be written and permanently locked, with no "
       "undo, so a wrong slot template scraps a whole reel; it authenticates a chip, not a "
       "product, so harvesting genuine chips out of real units and soldering them into "
       "fakes is the standard attack; and it only helps if the host issues a fresh random "
       "challenge every time, because a stored signature is a replay bug. An AS7263 or "
       "AS7265x stops at 860-940 nm, short of the 1100-1800 nm C-H overtones, so a black PP "
       "part and a black PET part are identical to it, and a 2 mm change in standoff shifts "
       "every channel by 20 %, so a classifier scoring 98 % is measuring your jig. And a "
       "gamma spectrometer identifies a family of peaks rather than a line.",
 unlocks="Provenance you can check at the point of use - spare parts, consumables, "
         "calibration standards, art and collectables - and an accessory ecosystem that "
         "cannot be trivially copied.",
 market="Brand protection, spare parts and consumables, art and collectables, laboratory "
        "supply chains"),

"object-temperature": dict(
 fools="Non-contact routes measure emitted infrared and then assume an emissivity, usually "
       "0.95. Bare metal sits near 0.1, so a hot aluminium heatsink reads close to room "
       "temperature while mirroring whatever is behind you - the most dangerous error here, "
       "because the hotspots people hunt are usually bare copper or steel. Field of view "
       "destroys more projects than emissivity: a standard MLX90614 sees roughly 90 "
       "degrees, so at 1 m it averages a 2 m circle. The sensor's own package temperature "
       "enters every calculation, so carrying one from a cold car into a warm room leaves "
       "it 3-5 degC wrong for several minutes. Glass and most plastics are opaque at 8-14 "
       "microns, so you cannot read a surface through an enclosure window - you read the "
       "window. Contact routes trade all that for coupling and lag: a stainless probe "
       "strapped to a pipe mostly reads room air unless it is bedded in paste and "
       "insulated, an air-filled thermowell can lag by minutes, and a board-mounted digital "
       "part reads its own PCB, where an ESP32 a centimetre away is worth 1-3 degC, twenty "
       "times a TMP117's own specification.",
 unlocks="Hotspot surveys of panels, motors and bearings, cooking and process control, and "
         "thermal-comfort mapping of the surfaces people actually touch rather than the "
         "air.",
 market="Electrical contractors, HVAC, manufacturing, food service, building surveyors"),

"asset-location": dict(
 fools="Signal strength does not measure distance: multipath alone swings a stationary BLE "
       "beacon by plus or minus 10 dB, an apparent one metre or eight from the same tag, "
       "and a body costs another 10-20 dB because 2.4 GHz is absorbed by water, so a beacon "
       "in a trouser pocket reads a room further away than the same beacon on a lanyard. "
       "Ultra-wideband does measure time of flight, and its error is one-sided: "
       "non-line-of-sight bias is always positive, adding 10-30 cm through a body, so UWB "
       "reads long and never short - and shipping it without the antenna-delay calibration "
       "puts up to a metre of fixed offset on every range. Tag routes tell you a tag passed "
       "a reader, not where the object is now, and UHF reads through cardboard and "
       "plasterboard, so a doorway portal counts the box next door; multipath makes range "
       "non-monotonic, so a no-read never means not-present. And fingerprinting dies "
       "silently when someone swaps a router, failing by confident mislocation rather than "
       "by degrading.",
 unlocks="Knowing what you own and where it is: tool-crib accountability, hospital equipment "
         "searches, and work-in-progress tracking that does not depend on someone scanning "
         "a barcode.",
 market="Construction, hospitals, logistics, makerspaces, film and events"),

"tamper-detected": dict(
 fools="Tamper is the one question here with an adversary, which changes what counts as a "
       "failure. A reed switch is held closed by any magnet held near it, which is why real "
       "security contacts are balanced-biased types detecting an added external field; a "
       "magnetometer seal goes the same way, and an MMC5603 folds back past +/-30 gauss, so "
       "overwhelming it is easier than fooling it. Accelerometer routes are beaten by "
       "patience: a threshold set above the noise floor to avoid nuisance alarms is also "
       "above a slow, careful lift, and one set near it fires on wind and lorries all "
       "night. Capacitive routes fail wet - a droplet on an ESP32 touch pad reads exactly "
       "like a finger, while a TTP223 baselines whatever rests on it at power-up, so an "
       "object placed before boot calibrates in as untouched. And the deeper problem is "
       "architectural: a tamper log inside the device is deletable by whoever opened it, "
       "every one of these sensors has a power-off state in which it detects nothing, and "
       "even a secure element authenticates a chip rather than an enclosure.",
 unlocks="Evidence rather than suspicion, for sealed instruments, metering, evidence bags "
         "and shared tools - knowing not just that something changed but when, and being "
         "able to prove it.",
 market="Metering and utilities, laboratories, logistics and pharma cold chain, evidence "
        "handling"),

"machine-running": dict(
 fools="On or off is where the quietest failures live. A vibration switch saturates: "
       "sustained vibration holds the contact open and it stops producing edges, so a "
       "machine running hard reads like one switched off. Current is the honest signal and "
       "carries three classic traps - clamping a current transformer around a whole flex "
       "cancels the live and neutral fields and reads zero; a metering chip's no-load "
       "threshold makes small loads vanish; and soft starters and variable-frequency drives "
       "flatten the very signature that would distinguish idle from loaded from stalled. "
       "Acoustic and contact routes hear the whole building: a microphone bolted to a panel "
       "reports footsteps upstairs. A bare Doppler module like the RCWL-0516 triggers on "
       "the ESP32's own Wi-Fi burst, on a switching regulator and on someone upstairs, and "
       "because it holds its output high under continuous movement, always-on and "
       "genuinely-running become indistinguishable. And thermal routes lag by minutes and "
       "read emissivity rather than temperature - a bare metal housing well above ambient "
       "reads close to room temperature.",
 unlocks="Utilisation data that justifies or refuses a capital purchase, billing by machine "
         "hour, and the baseline against which every predictive-maintenance trend is "
         "measured.",
 market="Manufacturing, makerspaces, laundries, workshops, equipment rental"),

"machine-duty-cycle": dict(
 fools="The measurement is easy and the DEFINITION is the hard part: 'running' can mean "
       "powered, spinning, loaded or producing, and those four numbers routinely differ by "
       "a factor of two on the same machine. Current is the best proxy and has floors you "
       "must respect — an ACS712 ±30A part cannot usefully see 200mA, and the INA219's "
       "±100uV shunt offset is ±1mA across the stock 0.1 ohm shunt, so standby and off are "
       "one reading. The SW-420 is the classic false economy: no amplitude discrimination, "
       "tens of pulses per event, and a contact held open under sustained vibration, so a "
       "hard-running machine reads as switched off. And a 1Hz poller misses every cycle "
       "shorter than two seconds, under-reporting utilisation in exactly the direction that "
       "loses the capital argument.",
 unlocks="Utilisation data that justifies or refuses a purchase, honest chargeback in shared "
         "workshops, and the denominator for maintenance intervals expressed in running "
         "hours.",
 market="Manufacturing, makerspaces, equipment hire, facilities, agriculture"),

"imbalance": dict(
 fools="Imbalance and misalignment are diagnosed by which harmonic of running speed carries "
       "the energy and whether it appears radially or axially, which needs a spectrum, a "
       "known shaft speed and two axes - so any route reporting a single number cannot "
       "answer it. The 801S outputs an envelope you cannot transform, and the SW-420 is "
       "worse than useless here because sustained vibration holds its contact open and it "
       "stops producing edges entirely, so a machine running hard reads exactly like a "
       "machine switched off. With a proper accelerometer the mount dominates above about 1 "
       "kHz: foam tape behaves as a spring and adds a 50-200 Hz resonance, a magnet base "
       "rings around 2-5 kHz in every spectrum, and only a stud or a cyanoacrylate bond "
       "gets you past 5 kHz. Aliasing manufactures faults too - an accelerometer at a 26 Hz "
       "output rate on a machine turning at 3000 rpm invents slow content that does not "
       "exist, which is why the parts built for this spend their silicon on more than 70 dB "
       "of anti-alias filtering. And absolute amplitudes are close to meaningless across "
       "machines: only the trend against that machine's own baseline is informative.",
 unlocks="Catching a loose coupling or a fouled fan before it eats a bearing, and hard "
         "evidence for whether an alignment or balancing job actually worked.",
 market="Manufacturing, HVAC contractors, pumps and fans, wind, makerspaces"),

"overheating": dict(
 fools="Hotter than it should be needs a reference and almost nobody has one: an absolute "
       "threshold fails because the same motor runs far hotter in August, so the "
       "informative quantity is the rise above ambient at a known load - two sensors and a "
       "load signal, not one thermometer. Contact routes read whatever they are bonded to: "
       "a board-mounted digital part sits 1-3 degC above ambient on a shared copper pour, a "
       "probe strapped to a pipe reads room air unless bedded and insulated, and a "
       "thermocouple front end adds its own die temperature through the cold junction; the "
       "classic symptom is a rig reading 30 degC high in the afternoon. Thermocouple type "
       "is a register setting, and a J probe read as K is wrong by roughly 15 percent, "
       "smoothly and believably. Non-contact routes are dominated by emissivity: a thermal "
       "scan of a bare copper busbar under-reports a dangerous hotspot, and glass is opaque "
       "at 8-14 microns. And the fault bits matter more than the number - a MAX31855 "
       "reports open-circuit and short conditions that most sketches ignore, so a snapped "
       "probe reads 0 degC and a controller heats forever.",
 unlocks="Catching a failing bearing, a loose electrical joint or a blocked filter days "
         "before anyone smells it - the highest-value early warning in the whole "
         "machine-health family.",
 market="Electrical contractors, manufacturing, data centres, EV and battery, facilities"),

"belt-slipping": dict(
 fools="One route, and it is a spectrum problem rather than a level one: slip appears as "
       "belt-pass and shaft-order sidebands, so without a shaft-speed reference a rise in "
       "vibration is indistinguishable from a rise in load. Above 1kHz the mount IS the "
       "measurement — tape rolls off before 1kHz, a magnet base rings at 2-5kHz and appears "
       "in every spectrum you take, and 100mm of unsupported cable adds a repeatable "
       "resonance that looks convincingly like a fault. The IIS3DWB's 6.3kHz -3dB band also "
       "misses the 20-40kHz acoustic-emission region entirely. A slipping belt dumps its "
       "lost power as heat, so an IR thermometer on the pulley usually confirms the "
       "diagnosis before the spectrum does.",
 unlocks="Catching slip before it glazes the belt and scores the pulley — and separating "
         "'the belt is slipping' from 'the load has risen', two faults with one symptom and "
         "different repairs.",
 market="Manufacturing, HVAC contractors, agriculture, workshops, facilities"),

"filter-clogged": dict(
 fools="Differential pressure is honest, but the tap is the measurement. A port facing into "
       "the flow reads high; ports at different heights in a warm duct add roughly 0.04 Pa "
       "per centimetre of height; a burr near the tap creates a local pressure unrelated to "
       "average flow. Match the range to the job: +/-3 % of reading is excellent at 300 Pa "
       "and worthless at 2 Pa. An SDP810's +/-0.2 Pa offset does not walk, whereas a "
       "piezo-resistive XGZP6897D drifts several pascals across a day, teaching a +/-100 Pa "
       "monitor that the filter is permanently new. The failure that bites is a droplet: "
       "condensation in one tube sticks the reading at a constant that reads as still "
       "clean. And dP is not flow - the dP-to-CFM curve belongs to that exact filter. An "
       "FS3000 hot-wire is a point sensor where velocity varies 2-3x across the section, "
       "reports mass flow as velocity, fouls with dust and grease, and is unidirectional: a "
       "back-drafting extract reads as small positive flow. Optical PM sensors either side "
       "both over-read above ~75 % RH, so their ratio survives humidity better than either "
       "alone.",
 unlocks="Changing filters on evidence: no more early replacement on a calendar, no more "
         "running a fan against a blocked element until the motor cooks or the room goes "
         "unventilated.",
 market="HVAC contractors, cleanrooms, indoor air quality, industrial extraction, dust "
        "collection"),

"air-leak": dict(
 fools="Everything in a plant is loud at 40kHz — air tools, steam, cavitating pumps, VFD "
       "switching — so an ultrasonic probe finds the loudest path to itself, not your leak, "
       "and structure-borne ultrasound carries metres along a pipe. Attenuation runs about "
       "1dB/m at 40kHz and worse in dry air, so the same leak reads differently on a damp "
       "day, and remounting a contact sensor on the same spot shifts it 6-10dB. The classic "
       "error is aliasing: sample 40kHz on an ESP32 ADC and you get a smooth, meaningless "
       "waveform that looks exactly like data. The gas routes answer a different question "
       "entirely — an INIR-ME5% NDIR module cannot see hydrogen at all, because H2 has no "
       "infrared dipole.",
 unlocks="Compressed air is usually the most expensive utility per unit of useful work, and "
         "leaks run around the clock. A repeatable survey turns 'the compressor runs a lot' "
         "into a ranked list of fittings.",
 market="Manufacturing, facilities, workshops, energy auditors, HVAC contractors"),

"abnormal-current": dict(
 fools="Nothing here measures abnormality; every route measures current and leaves the "
       "drifting baseline to you. The first failure is geometric: a split-core CT or a Hall "
       "part like the SS49E clamped around a whole two-core flex reads near zero, because "
       "live and neutral carry equal and opposite currents whose fields cancel a centimetre "
       "away - a kettle pulling 10 A reads nothing. Then dynamic range: an SCT-013 or an "
       "ATM90E32AS on a 100 A CT works inside half an LSB on a 40 W standby load, and an "
       "Eastron SDM120 is Class 1 only above about 1 % of its 45 A rating, so the drift you "
       "were hunting is below the floor by design. The INA219's +/-100 uV shunt offset is "
       "+/-1 mA across its 0.1 ohm shunt, and it samples rather than integrates, so a 250 "
       "mA Wi-Fi burst inside a 532 us conversion is either missed or believed to be the "
       "average. And an unburdened CT on a live conductor becomes a step-up transformer and "
       "can develop lethal voltages across its terminals.",
 unlocks="A per-machine current signature that separates idle from loaded from stalled - the "
         "raw material for jam detection, utilisation accounting, and attribution of who "
         "spends the energy on a shared supply.",
 market="Manufacturing, facilities, makerspaces, energy retrofits, laundries"),

"drift-from-baseline": dict(
 fools="The question assumes the sensor is stable and the world is changing, and that is "
       "wrong more often than not. Almost everything here drifts on a timescale comparable "
       "to the thing you are trending: polymer humidity sensors age a few tenths of a "
       "percent RH a year and acquire semi-permanent offsets after a night above 80 percent "
       "RH, metal-oxide gas elements fall by tens of percent over their first weeks and "
       "never stop moving, load cells creep 0.02-0.05 percent of the applied load in half "
       "an hour and shift 0.01-0.05 percent of full scale per degree, gypsum soil blocks "
       "physically dissolve, optical particle sensors read 20-30 percent low after a year "
       "of fan-drawn lint, and NDIR CO2 cells with automatic baseline correction quietly "
       "re-zero themselves to the cleanest air of the week. The environment is the other "
       "confound and usually the largest: most multi-month trends are a temperature or "
       "humidity curve. The only real defence is a reference: a second identical sensor "
       "kept in a known state, a periodic recalibration against a fixed point, or a "
       "differential measurement in which both channels drift together.",
 unlocks="Condition-based maintenance and warranty evidence: the ability to say that a thing "
         "has changed, which is a far stronger claim than saying that a thing is bad.",
 market="Manufacturing, facilities, instrumentation, agriculture, research"),

"arc-or-discharge": dict(
 fools="A 40 kHz piezo or ultrasonic MEMS mic hears arcing, but so are compressed air, steam "
       "and VFD switching, and structure-borne ultrasound travels metres along a pipe, so "
       "this panel is often the pump two bays away. Remount a contact sensor on the same "
       "spot and 6-10 dB moves, larger than most real fault progressions. Undersampling is "
       "the silent failure: 40 kHz digitised on an ESP32 ADC aliases into a smooth, "
       "meaningless low-frequency waveform. An AD8318 log detector integrates 1 MHz to 8 "
       "GHz into one number, so your own Wi-Fi and the microwave add to whatever you are "
       "hunting. Healthy switch-mode supplies leak by design through their Y-capacitors, "
       "and a DC or high-frequency leakage component can bias an RV4145A's toroid toward "
       "saturation so it stops responding to the AC fault it was fitted to catch. Real "
       "partial-discharge work uses a calibrated coupling capacitor; this is a screening "
       "tool.",
 unlocks="Finding a loose termination, a tracking insulator or a failing cable joint while "
         "it is still a warm spot rather than a fire, and doing it from outside the "
         "enclosure without a shutdown.",
 market="Facilities, electrical contractors, substations, data centres, industrial "
        "maintenance"),

"lubrication-failing": dict(
 fools="The dielectric route is the least specific: oil's dielectric constant moves with "
       "temperature far more than with mild contamination, so without a temperature channel "
       "you plot how warm the sump is, and water, oxidation and metal particles all raise "
       "the reading identically. Probe geometry is the calibration: a probe that shifts a "
       "millimetre invalidates the baseline, and varnish on the electrodes drifts the zero "
       "over months. The acoustic route is more fragile. Remount the same sensor on the "
       "same spot and 6-10 dB moves, more than most fault progressions, and structure-borne "
       "ultrasound travels metres along a frame in a plant room already loud at 40 kHz, so "
       "this bearing is often the pump two metres away. The vibration route has a coverage "
       "gap: an IIS3DWB is flat to 6.3 kHz, well below the 20-40 kHz acoustic-emission band "
       "where the earliest distress appears. And above 1 kHz the mount dominates - tape "
       "rolls off before 1 kHz, a magnet base has a 2-5 kHz resonance that appears in every "
       "spectrum.",
 unlocks="Relubricating on condition rather than on a calendar, which both prevents the "
         "bearing failures that come from too little grease and the ones that come from too "
         "much.",
 market="Manufacturing, HVAC, wind and hydro, fleet maintenance, condition-monitoring "
        "services"),

"rotation-speed": dict(
 fools="Counting edges is easy; counting the right ones is not. A reed switch bounces for up "
       "to a millisecond, so one magnet pass becomes five counts, and an A3144 is unipolar "
       "- present the north pole and nothing happens. Its release threshold sits well below "
       "its operate threshold, so a slowly passing magnet gives one pulse while a vibrating "
       "one gives a burst. A bare photo-interrupter without a Schmitt trigger gives "
       "multiple counts per slot, dust kills it silently, and ambient sun can hold the "
       "output permanently on. Voltage level kills hardware: an LPD3806 encoder's "
       "open-collector output swings to whatever you pull it up to, and an inductive "
       "proximity switch's output follows its supply rail, so a 24 V install destroys the "
       "GPIO. An AS5600 or AS5048A measures the direction of all the field, so a motor 20 "
       "mm away bends it into a repeatable error that looks like backlash, and 0.25 mm of "
       "magnet eccentricity turns +/-0.05 degrees into +/-0.5. And belt slip or a "
       "variable-frequency drive means motor speed and machine speed are different numbers.",
 unlocks="Real utilisation and load data - cycle counts, slip, speed profiles - and the "
         "reference frequency that makes vibration spectra interpretable at all.",
 market="Manufacturing, workshops, HVAC, agriculture, motorsport and fabrication"),

"cycle-complete": dict(
 fools="'Finished' and 'quiet for a while' are different statements, and most builds "
       "conflate them. The SW-420 is the classic trap and fails in the dangerous direction: "
       "it chatters tens of pulses per event, cannot distinguish amplitude at all, and "
       "sustained vibration holds its contact open — so a machine running hard reads "
       "exactly like one switched off. Current is the better proxy and needs a per-machine "
       "baseline, and its floor bites: the INA219's ±100uV shunt offset is ±1mA across the "
       "stock 0.1 ohm shunt, so standby and off are one reading. What actually works is a "
       "state machine over the whole cycle signature with an explicit minimum run time and "
       "a timeout, never a single threshold and never a single quiet second.",
 unlocks="Machines that tell you they are done — laundry, kilns, CNC jobs, prints, "
         "autoclaves — plus the cycle-time data that shows where a process really loses its "
         "hours.",
 market="Manufacturing, laundries, makerspaces, laboratories, smart home"),

"ventilation-adequate": dict(
 fools="The answer needs real CO2. Any eCO2 number from a VOC sensor is arithmetic rather "
       "than measurement - a reducing-gas reading scaled by the assumption that humans are "
       "the only source - so an alcohol wipe pins it to thousands of parts per million with "
       "no CO2 present. Even a genuine NDIR or photoacoustic cell has an assumption baked "
       "in: automatic baseline correction assumes the sensor sees outdoor air, around "
       "400-420 ppm, at least once a week and re-zeros to the lowest value it saw, so in a "
       "bedroom occupied every night or a sealed grow tent it silently subtracts hundreds "
       "of ppm over a few weeks - precisely the space you installed it to document. "
       "Pressure is the second systematic error: NDIR readings move roughly 1-1.6 percent "
       "per 10 hPa, so weather and altitude bias them permanently unless the pressure "
       "register is fed, and most firmware exposes none. And differential-pressure routes "
       "measure the tap, not the duct: a port facing into the flow reads high, ports at "
       "different heights in a warm duct add roughly 0.04 Pa per centimetre, and one "
       "droplet sticks the reading at a constant.",
 unlocks="An argument you can win with a landlord, a school or a facilities team, and "
         "demand-controlled ventilation that saves energy without letting a room go stuffy.",
 market="Schools, offices, gyms, landlords and letting agents, ventilation contractors"),

"smoke-present": dict(
 fools="None of these is a smoke alarm, and that matters more here than anywhere else in the "
       "atlas. Optical particle counters are blind below about 0.3 microns, where most of "
       "what a smouldering fire or a candle emits by number lives, so a genuine early-stage "
       "event is a routine false negative - and they over-read badly above roughly 75 "
       "percent RH because particles absorb water and swell. Metal-oxide routes respond to "
       "everything reducing - alcohol, fresh paint and, critically, humidity - so an MQ-2 "
       "reads a bathroom after a shower as a gas event, and its baseline moves by tens of "
       "percent across 20-80 percent RH with no compensation. The carbon monoxide route "
       "maps to real danger and is handled worst: an MQ-7 yields one valid sample per "
       "150-second heater cycle, so a plume that arrives and clears between samples is "
       "invisible; it responds to hydrogen roughly as strongly as to CO; and below about 50 "
       "ppm its output is noise - while the WHO Guidelines for Indoor Air Quality: Selected "
       "Pollutants set 35 mg/m3 (about 30 ppm) as the one-hour value and 100 mg/m3 as the "
       "fifteen-minute value, to keep carboxyhaemoglobin below 2 percent.",
 unlocks="Minutes of extra warning from a cooking, smouldering or wildfire-infiltration "
         "event, and a record of what actually happened rather than a beep nobody was "
         "present to hear.",
 market="Alongside a certified alarm only: security installers, insurers, landlords, "
        "wildfire monitoring"),

"co-present": dict(
 fools="Know what a real alarm does first. EN 50291-1:2018 defines CO alarms by response "
       "time, not by a reading: at 50 ppm one must stay silent for 60 minutes and fire "
       "before 90; at 100 ppm wait 10 minutes and fire before 40; at 300 ppm fire in under "
       "3; and 30 ppm must not trigger it before 120 minutes at all. The MQ-7 answers to "
       "hydrogen roughly as strongly as to CO, plus alcohol and methane, so a garage with "
       "petrol vapour reads as a CO event; it samples only at the end of its 90-second "
       "low-temperature heater phase, so a plume that arrives and clears between samples is "
       "invisible; and below about 50 ppm its output is noise, which is the region the "
       "standard cares about. MiCS-5524 and MiCS-6814 baselines move more between a dry "
       "morning and a humid evening than a 20 ppm event does. Even an electrochemical cell "
       "responds to hydrogen at 20-60 % of its CO response, drifts a few tenths of a "
       "percent per degC, and keeps emitting a plausible number after it has aged out. "
       "Build the logger; buy the alarm.",
 unlocks="Understanding a specific appliance or workshop - when a flue spills, how a plume "
         "migrates, whether a heater degrades - alongside a certified alarm that makes the "
         "safety decision.",
 market="Landlords, boiler and stove installers, workshops, caravan and boat owners, "
        "indoor-air research"),

"voc-event": dict(
 fools="A metal-oxide sensor is one resistance responding to every reducing gas at once, so "
       "it detects that something changed and never what. Alcohol dominates by a wide "
       "margin, so hand sanitiser and a whiteboard marker outrank almost anything harmful, "
       "and an SGP40-trained detector fires enthusiastically at nail varnish. Water vapour "
       "is a reducing gas to a hot tin-oxide film: a 10 % change in relative humidity moves "
       "gas resistance more than most of the smells you care about, so a shower two rooms "
       "away is indistinguishable from a real event unless you feed temperature and "
       "humidity back in. Sensirion's VOC Index is relative by design - 100 always means "
       "typical for this room over the past 24 hours - so a solvent-laden workshop sits at "
       "100 while a clean bedroom hits 300 because someone uncapped a pen, and "
       "deep-sleeping the host without persisting the algorithm state resets it every wake. "
       "The eCO2 output from an SGP30, ENS160 or BME688 assumes human breath is the "
       "dominant source. And siloxanes from curing RTV or silicone cable poison all of "
       "these irreversibly.",
 unlocks="Event detection with a timestamp: when a new material started off-gassing, when a "
         "room was cleaned, when a fridge failed - the questions where something changed is "
         "genuinely the answer you want.",
 market="Indoor air quality, facilities, food and cold chain, manufacturing hygiene, home "
        "automation"),

"mould-risk": dict(
 fools="Room humidity is the wrong variable — mould responds to RH at the SURFACE, and a "
       "cold surface in a warm room sits far higher than the air does. Portland State's "
       "review of the IEA criteria puts germination near 80% surface RH and visible growth "
       "above about 85%, with the critical curve essentially flat from 15 to 40°C, so what "
       "decides the outcome is hours above threshold rather than any instantaneous reading. "
       "Every part here measures the air about a millimetre from its own cap: an SHT41 "
       "reports a comfortable 60% while the wall behind it sits at 95% microns away, and "
       "self-heating from a co-located ESP32 adds 1-3°C, which costs roughly 6 points of RH "
       "per degree. Alarm on dew-point margin against an MLX90640 surface temperature, and "
       "never pot the sensor in silicone.",
 unlocks="Intervening before there is anything to see or smell, and settling landlord-tenant "
         "arguments with a dew-point-margin record rather than opinions about airing.",
 market="Landlords and tenants, surveyors, insurers, museums and archives, growers"),

"too-dry": dict(
 fools="Relative humidity is defined against the sensor's own temperature, which makes "
       "self-heating the dominant error in almost every build: an ESP32 on the same board "
       "raises the die by 1-3 degC, and 1 degC of error is roughly 6 points of RH, so a "
       "node reading 32 percent may sit in a room at 38. The polymer is also poisoned by "
       "silicone: fresh RTV, conformal coating and even some hand creams cause an "
       "irreversible sensitivity loss that presents as slow drift, so potting one throws it "
       "away. Parts with no on-chip heater cannot burn off a night at high humidity and "
       "keep the offset afterwards; the SHT4x family can, at the cost of a fraction of a "
       "degree for a minute. The deeper mismatch is that all of these sensors measure the "
       "air about a millimetre from their cap, while wood, canvas and a violin respond to "
       "their own equilibrium moisture content over days - a wall bone dry to touch can sit "
       "at 95 percent RH microns away. And in a sealed case the same absolute moisture "
       "swings RH by roughly 25 points for a 10 degC overnight cooling with no water moving "
       "at all, which is why alarming on dew-point margin beats alarming on RH.",
 unlocks="Humidification, case design and loan conditions driven by what an object actually "
         "experiences, with a record that stands up in an insurance or condition report.",
 market="Museums and archives, instrument makers, furniture and joinery, wine storage, "
        "dermatology"),

"radon-level": dict(
 fools="Radon is a weather-driven flux, not a level, and the number in front of you is "
       "usually the wrong statistic. The WHO Handbook on Indoor Radon is explicit that high "
       "temporal variation makes short-term measurements unreliable, that a factor of two "
       "or more commonly separates repeated short-term measurements, and that deployment "
       "should run from one month to one year, a year being standard for homes: a house "
       "measured closed up overestimates the annual mean and one measured with windows open "
       "underestimates it. Every mitigation threshold you will read about is an annual "
       "average, so acting on a bad Tuesday is not acting on that number. An ion chamber "
       "counts, so a spike shorter than an hour is Poisson statistics rather than gas, and "
       "an RD200 displays a rolling average that trails a real change by hours. A falling "
       "barometer sucks soil gas into the building, so radon correlates more strongly with "
       "pressure than with anything you control. Moving the unit resets its settling, "
       "sustained humidity degrades the chamber, and thoron inflates readings near a wall.",
 unlocks="A year-long, hour-resolved picture of how a specific house breathes - which rooms, "
         "which weather and which ventilation habits actually change the exposure, rather "
         "than a single test kit result.",
 market="Home owners and buyers, radon remediation, landlords, public health, building "
        "science"),

"ozone-present": dict(
 fools="All three routes are oxidiser detectors that have been labelled ozone. Nitrogen "
       "dioxide gives a strong positive response on an electrochemical ozone cell, and "
       "chlorine, chlorine dioxide and peracetic acid all read as ozone, so bleach in the "
       "room gives a confident wrong number; outdoors the same cell reads O3 plus NO2 "
       "unless you subtract a second cell. The MQ-131's resistance increases with ozone, "
       "the reverse of the rest of the MQ family, so libraries written for an MQ-2 or MQ-4 "
       "report ozone falling as it rises. Ozone is also destroyed by almost every surface "
       "it touches - a metre of silicone tubing removes half of it - so this must sit in "
       "the air it is measuring, with no sample line, grille or dusty enclosure, or it "
       "under-reads by an unknowable factor. Resolution flatters the parts badly: a ZE25-O3 "
       "quotes 0.01 ppm while outdoor background ozone runs 0.02-0.06 ppm, right at the "
       "noise floor. And there is no reference gas in a hobby build, against a stated "
       "two-year cell life.",
 unlocks="Knowing when a purifier, ioniser, UV lamp or laser printer is putting ozone into "
         "an occupied room, and how fast it clears when you ventilate.",
 market="Indoor air quality, print and copy rooms, water treatment, occupational health"),

"formaldehyde-level": dict(
 fools="Both routes are indirect. The electrochemical HCHO cell responds to other aldehydes "
       "and to alcohols - Winsen's own datasheet lists significant ethanol "
       "cross-sensitivity - so an alcohol wipe or a hand-sanitiser dispenser all read as "
       "formaldehyde. Anything below about 0.03 ppm is noise, and like every "
       "electrochemical part it keeps producing confident numbers after the cell has aged "
       "out. A photoionisation detector is worse here: it reports every ionisable compound "
       "as one number in isobutylene equivalents whose response factors vary more than "
       "tenfold, its response is suppressed by a third from 20 to 90 percent RH, and its "
       "lamp dims over 5000-6000 hours. Keep the scale in view - the WHO Guidelines for "
       "Indoor Air Quality: Selected Pollutants derive their formaldehyde figure from a "
       "0.63 mg/m3 human NOAEL for sensory irritation with an assessment factor of 5, "
       "giving 0.125 mg/m3 as a 24-hour value, roughly 0.1 ppm and only about three times "
       "the cheap cell's noise floor. A hobby build can show a decay curve; it cannot "
       "declare a room safe.",
 unlocks="Watching a renovation off-gas down over weeks, so you know when a room is usable "
         "rather than guessing from the smell - and whether a new item restarted the clock.",
 market="Households after renovation, flooring and furniture trade, air consultants, rental "
        "disputes"),

"cooking-detected": dict(
 fools="Cooking is trivial to detect and almost impossible to detect specifically. Every "
       "metal-oxide route - MQ-2, MQ-135 - is one resistance responding to all reducing "
       "gases at once, so hand sanitiser or a fresh coat of paint produces a bigger step "
       "than frying does, and the MQ family's baseline moves by tens of percent across "
       "20-80% RH with no compensation. Optical particle counters like the PMS5003 see "
       "cooking best and mislead worst — they over-read above roughly 75% RH because "
       "particles absorb water and swell, so a kettle or a shower reads like a pan of oil, "
       "and they are blind below 0.3um, which is where a gas hob's emissions actually live. "
       "The MLX90614 fails on geometry rather than chemistry: a 90 degree cone averages a "
       "2m circle at 1m, so pointed at the hob it is mostly measuring the wall.",
 unlocks="Extractor fans that run because cooking happened rather than because someone "
         "remembered, cooker-left-on alerts, and honest exposure accounting — cooking is "
         "the largest indoor PM source in most homes.",
 market="Smart home, elder care, ventilation, insurance, indoor air quality"),

"smell-signature": dict(
 fools="A BME688 metal-oxide array measures the total reducing atmosphere through a hot "
       "tin-oxide film, and water vapour is a reducing gas as far as that film is concerned "
       "— a 10% RH change moves gas resistance more than most of the smells you care about, "
       "which is why a model trained in winter fails in summer. Baseline drift is "
       "relentless, falling tens of percent over the first weeks and never settling, so "
       "every feature must be relative; the SGP40 makes this explicit by defining 100 as "
       "'typical for this room over the past 24 hours', so a solvent-laden workshop sits at "
       "100 while a clean bedroom hits 300 because someone uncapped a pen. Parts are not "
       "interchangeable — unit-to-unit variation exceeds the class separation you are "
       "trying to learn. And siloxanes poison the film silently: it keeps producing "
       "numbers, just different ones.",
 unlocks="Narrow, well-posed classification jobs: spoilage in one product, a leak of one "
         "known solvent, a roast reaching one known stage — a nose for one question rather "
         "than for everything.",
 market="Food and beverage production, industrial process, environmental compliance, "
        "agriculture, research"),

"is-raining": dict(
 fools="The tipping bucket is the only route with real units, and it under-reads exactly the "
       "storm you cared about: water keeps arriving while the bucket is mid-tip, costing "
       "10-15% above roughly 50mm/h, and wind across the orifice steals another 5-20%. Its "
       "reed bounces, so one tip becomes three millimetres of phantom rain, and blockage by "
       "leaves or a spider web makes the record read zero — indistinguishable from dry "
       "weather, for months. The capacitive plate and leaf-wetness routes detect surface "
       "WETNESS instead: dew, fog and a hand waved 10cm above all register, they saturate "
       "once the surface is covered so drizzle and a downpour read the same, and drying "
       "time rather than rainfall decides when they clear.",
 unlocks="Irrigation that skips a cycle because it actually rained, harvesting that "
         "pre-drains before a storm, and a local intensity record no regional forecast can "
         "give you.",
 market="Gardeners, growers, rainwater harvesting, hydrology, citizen science"),

"wind-conditions": dict(
 fools="Siting beats sensor quality: any obstacle within about ten times its own height "
       "upwind ruins the reading, a roof-ridge mount can read 30 percent high in the "
       "speed-up over the ridge or far too low in its wake, and a mast beside a building "
       "measures the building's wake. Cup anemometers are blind below their starting "
       "threshold of roughly 0.5-1.4 m/s, so light air is reported as dead calm, and as the "
       "bearing ages that threshold climbs until a 5 km/h breeze reads zero - while in "
       "turbulence they over-read by typically 5-10 percent. Direction is quantised to 16 "
       "points, so plus or minus 22.5 degrees is the best possible, and aligning to true "
       "north by eye adds 10-20 degrees; half the positions are made by two reeds closing "
       "at once, and their parallel resistance sits close to a neighbouring single-reed "
       "value, so 5 percent resistor tolerance or one corroded contact aliases adjacent "
       "sectors. And the classic software bug is averaging degrees - the mean of 350 and 10 "
       "is 180, exactly backwards - so average sine and cosine, gate direction on a minimum "
       "wind speed, and report a 3-second gust and a 10-minute mean.",
 unlocks="Local wind that a regional forecast cannot give you: crane and drone go/no-go, "
         "spray-drift windows, sailing and kiting decisions, and siting evidence for a "
         "small turbine.",
 market="Construction and cranes, agriculture and spraying, marinas, drone operators, "
        "renewables"),

"lightning-distance": dict(
 fools="The distance is not a measurement. The AS3935 infers range from received signal "
       "energy alone, so a strong strike at 25km and a weak intra-cloud discharge at 5km "
       "can land in the same bin, and its fifteen non-linear bins shift as the storm's "
       "character changes — which is why a storm appears to retreat and is then overhead. "
       "It gives no bearing, and two units cannot be triangulated because their event "
       "timestamps are not synchronised. Detection lives or dies on the noise floor: "
       "switching supplies, LED drivers, electric fences and the ESP32's own boost "
       "converter all radiate at 500kHz, so out of the box it reports dozens of disturbers "
       "a minute, and rejection cranked high enough to silence them starts missing real "
       "strikes. Inside a steel-framed building 40km becomes 3km.",
 unlocks="The ten to thirty minutes of warning that lets you clear a pool, a pitch or a "
         "marina and unplug equipment — a lead time no forecast gives you at the resolution "
         "of one site.",
 market="Sports facilities, marinas, outdoor events, agriculture, homeowners"),

"snow-depth": dict(
 fools="Snow is close to the worst target for both routes. Fresh dry powder scatters an 850 "
       "nm pulse deep into the pack rather than off the surface, so a TF02-class laser "
       "reads a few centimetres too deep - and the error changes as the snow ages and "
       "crusts, drifting through the period you are measuring. Powder is also highly "
       "absorbent, so a JSN-SR04T or US-100 gets a weak echo or none and reports its "
       "maximum rather than an error. Then the compensation lies to you: the speed of sound "
       "moves about 0.6 % per degC, around 12 cm at 5 m over a 40 degC swing, and the "
       "on-board thermometer of a US-100 or MB7389 sits on the PCB inside your housing, so "
       "a sun-warmed case corrects for the housing, not the air column. Falling snow, rain "
       "and fog put flickering short readings in the path during the event you deployed "
       "for. An MB7389 reports 300 for a target genuinely at 30 cm and for anything closer, "
       "ice on a laser window freezes the reading at a plausible constant, and depth is not "
       "water equivalent because the pack settles.",
 unlocks="Local, hourly snow depth where forecasts only offer a region - avalanche and "
         "access decisions, roof-load warnings, and a hydrological record of what is "
         "actually stored on the ground.",
 market="Mountain communities, ski areas, roads and utilities, hydrology, roof safety"),

"solar-resource": dict(
 fools="The cheap route - DFRobot's SEN0562 - is a silicon cell pretending to be a broadband "
       "instrument, and ISO 9060:2018 says so: it grades spectral error at ±0.5% for Class "
       "A, ±1% for Class B and ±5% for Class C, and Apogee's own comparison places its "
       "silicon SP-110 at about ±4% against ±2% for the SP-510 thermopile. A silicon cell "
       "responds roughly 400-1100nm while sunlight extends past 2500nm, so heavy cloud, a "
       "low sun angle or any grow light produces 10-25% error with nothing in the data to "
       "reveal it. Without a proper diffuser the cosine response falls faster than "
       "cos(theta) beyond about 60 degrees, so daily kWh/m2 totals come out systematically "
       "low — and two degrees out of level is 1-3% at low sun. A horizontal pyranometer "
       "also cannot tell you what a 35-degree array receives, which is how this measurement "
       "is most often misused.",
 unlocks="Yield modelling and performance ratios you can defend, and siting decisions for "
         "arrays and glasshouses based on the site rather than on a regional average.",
 market="Solar PV, controlled-environment agriculture, meteorology, building services, "
        "research"),

"uv-exposure": dict(
 fools="The UV Index is not ultraviolet light but erythemally weighted ultraviolet, and the "
       "weighting is brutal. ISO 17166:1999 / CIE S 007 defines the reference action "
       "spectrum as 1.0 from 250 to 298 nm, then falling as 10^(0.094*(298-lambda)) to 328 "
       "nm and 10^(0.015*(140-lambda)) beyond - effectiveness at 328 nm is already about "
       "0.32, and by 400 nm roughly 0.3 % of the UVB peak. Every affordable sensor sits on "
       "the wrong side of it. An LTR-390 cannot see UVB, so its printed index is a fit to "
       "clear midday sun that is wrong under cloud and behind glass, which passes UVA and "
       "blocks UVB: a windowsill sensor reports an index that does not physically exist. An "
       "ML8511 peaks near 365 nm and carries a 1.0 V zero-UV offset that drifts with "
       "temperature; a GUVA-S12SD has +/-30 % unit-to-unit spread. The SI1145 has no UV "
       "photodiode at all - its index is a polynomial fitted to visible and infrared "
       "channels under open sky, and it reports UVI 3 from a desk lamp. And cosine error "
       "attacks the dose in exactly the morning and evening hours a daily integral must "
       "include.",
 unlocks="A personal or per-location dose record that is honest about its own units - useful "
         "for sun-safety habits, for photosensitive conditions, and for checking UV-curing "
         "and germicidal equipment.",
 market="Consumer wearables, dermatology and photosensitivity, outdoor work, sports, reptile "
        "keeping"),

"sky-clear": dict(
 fools="Inferring cloud from visible light measures the wrong thing. The informative signal "
       "is downward long-wave radiation: an infrared thermometer pointed up reads -20 degC "
       "or lower under a clear sky, because there is almost nothing above to radiate back, "
       "and close to ambient under thick cloud - but that same part has a roughly 90-degree "
       "field of view, so it averages a large patch of sky along with any tree or roofline "
       "inside the cone, and its ambient compensation takes minutes to settle. "
       "Visible-light routes confuse cloud with time of day, haze, dew and the enclosure: "
       "any window in front of an ambient light sensor changes the calibration by 20-50 "
       "percent, dew halves the reading over an hour, and both the TSL2561 and TSL2591 "
       "saturate abruptly and then return a low lux value, so direct sun can read darker "
       "than cloud unless you check the overflow flags. UV routes are worse for this "
       "question - a UV-A part cannot see UV-B at all, so the index it prints is a "
       "clear-midday fit that diverges under exactly the cloud you were trying to detect.",
 unlocks="Automated observatory roofs and imaging schedules, single-site solar yield "
         "forecasting, and frost warnings that depend on whether the sky is actually open.",
 market="Amateur astronomy, solar, horticulture, weather enthusiasts, agriculture"),

"flood-rising": dict(
 fools="The rate matters more than the level, and most routes are worse at rate. Ultrasonic "
       "is fooled by exactly the conditions of a flood: spray and condensation on the "
       "transducer create a persistent near-field echo, foam and debris scatter the surface "
       "return, and a narrow standpipe behaves as a waveguide delivering wall echoes ahead "
       "of the true surface. Absolute-pressure depth sensors conflate weather with water: "
       "without a dry reference barometer a passing front is plus or minus 30 cm of "
       "apparent level, and a vented 4-20 mA probe dies at the vent, where a capillary "
       "blocked by condensed humid air turns a 30 mbar front into a phantom 300 mm of "
       "water. Leak rope only sees water reaching the exact spot you laid it, needs that "
       "water to conduct - clean rainwater may not trip a threshold set with tap water - "
       "and gets kicked aside during servicing. And the rain gauge that would have given "
       "you warning under-reads by 10-15 percent above about 50 mm/h, which is the storm "
       "you cared about.",
 unlocks="Hours of warning instead of minutes, and a local culvert or watercourse record "
         "that no regional forecast provides - including how fast the level is actually "
         "rising.",
 market="Local authorities, insurers, farms, marinas, householders in flood zones"),

"heat-island": dict(
 fools="The difference you want to report is often smaller than a badly built node's errors. "
       "A polymer humidity and temperature part reads its own board first: an AHT20 sharing "
       "a PCB with an ESP32 running Wi-Fi reads 1-2 degC high and several percent RH low, "
       "the entire effect under study. Sun on the housing is worse - an unshielded sensor "
       "outdoors reads 5-15 degC high, so a naturally aspirated radiation shield is not an "
       "accessory, it is the instrument. Comparing two streets means comparing two sensors, "
       "and part-to-part offsets of a few tenths of a degree are the same size as the "
       "signal, so co-locate every unit for a day and store per-unit offsets before "
       "deployment. Siting dominates the rest: a metre above asphalt and a metre above "
       "grass are different climates, so mounting height, wall proximity and time of day "
       "have to be logged. And adding a pollutant channel does not rescue the study - a "
       "B4-class electrochemical NO2 cell's zero current swings substantially and "
       "non-linearly with temperature, and Alphasense publish four different correction "
       "algorithms and tell you to pick the one matching your cell.",
 unlocks="Street-level evidence for shading, tree planting and cool-roof programmes that a "
         "single regional weather station cannot provide.",
 market="City councils, urban planners, community science, public health, architects"),

"flow-rate": dict(
 fools="Every meter has a floor, and the floor is where the interesting question lives. A "
       "YF-S201 does not rotate below about 1 L/min, so a dripping tap and a pinhole leak "
       "are invisible, and its K-factor is not 450 but 450 +/-15 % per unit and non-linear "
       "at both ends. Air in the line spins the impeller and manufactures litres; one piece "
       "of swarf drops the reading to zero, looking exactly like nobody using water; and "
       "its 5 V Hall output destroys an ESP32 pin. A paddlewheel stalls below about 0.3 m/s "
       "- a dead band, not rounding - and wants ten pipe diameters of straight run "
       "upstream, so an elbow shifts it 10-20 %. An electromagnetic meter is blind below "
       "about 5 uS/cm, ruling out deionised water, oils and fuels, and reports whatever "
       "fraction of its electrodes is wet. Clamp-on transit-time meters read nonsense on a "
       "partially full pipe with no way to know it, often get no signal through cast iron, "
       "and their +/-1 % is conditional on wall thickness you typed in. And almost all have "
       "a temperature-dependent zero.",
 unlocks="Water accounting that survives a dispute: per-fixture usage, leak detection by "
         "flow-with-no-occupancy, irrigation scheduling, and thermal power when paired with "
         "a delta-T.",
 market="Water utilities, landlords and insurers, agriculture, industrial process, district "
        "heating"),

"water-used-total": dict(
 fools="Every route counts what passes it, and the gaps are where the value was. Turbine "
       "meters have a genuine dead band rather than a rounding error: a YF-S201's impeller "
       "does not turn below about 1 L/min and a paddlewheel stalls below 0.3 m/s, so a "
       "dripping tap and a pinhole leak are invisible — which is why 'zero flow at 3am' "
       "beats 'a small flow' as a leak signal. OIML R 49-1 says the same thing formally, "
       "defining a minimum flowrate Q1 below which nothing is specified at all and "
       "permitting a Class 2 meter ±5% between Q1 and the transitional Q2. Air in the line "
       "manufactures litres; grit jams the impeller to a zero indistinguishable from nobody "
       "using water. And 'by whom' is not a flow question at all — attribution needs a "
       "meter per fixture, because the 1Hz update these give is far too slow to "
       "disaggregate.",
 unlocks="Leak detection with a financial return, per-fixture accounting that makes "
         "conservation arguments concrete, and metered billing in shared houses and marinas "
         "people accept as fair.",
 market="Water utilities, landlords and housing, agriculture, marinas and campsites, "
        "facilities"),

"pump-dry": dict(
 fools="Nearly every level route here fails toward 'there is liquid', which is the wrong "
       "direction for this question. A float switch is a DENSITY device: in petrol or a "
       "foaming detergent it sinks and reports empty in a full tank, and scale or biofilm "
       "glues it to its stem, after which it gives a perfectly steady, perfectly wrong "
       "reading indefinitely. JSN-SR04T and A02YYUW ultrasonic routes carry a 3-25cm blind "
       "zone and are absorbed completely by foam, so an aerated sump reads as empty — and "
       "some firmware returns the last good value rather than an error, so a falling tank "
       "appears to freeze. The XKC-Y26 capacitive through-wall switch reads condensation "
       "and sludge as liquid and often will not trigger on oils at all. Flow is the honest "
       "cross-check with its own floor: a YF-S201's impeller does not turn below about 1 "
       "L/min.",
 unlocks="Pumps that survive their installation. Dry-run protection is the difference "
         "between a cheap sensor and a replaced pump, and one of the few sensing builds "
         "with an unarguable payback.",
 market="Agriculture and irrigation, marine and RV, industry, hydroponics, water utilities"),

"water-ph": dict(
 fools="A glass electrode is a high-impedance voltage source sharing its reference with the "
       "water, and nearly every failure follows. Ground loops are the expensive one: the "
       "moment a pump, heater or second probe joins the tank the reading jumps by whole pH "
       "units, and an EC probe is the worst offender because its AC excitation swamps the "
       "pH reference. The source impedance also constrains the converter: an ADS1115's "
       "input impedance falls to a few hundred kilohms at its highest gain settings, which "
       "loads a pH electrode into meaninglessness unless you buffer it. Drift is both an "
       "offset and a slope change, roughly 0.1 pH a week in clean water and faster in "
       "nutrient solution, and temperature moves both the electrode slope and the true pH "
       "of the solution. And the colorimetric route trades electrochemistry for geometry: "
       "indicator media age, are batch-variable and temperature-dependent, and were made to "
       "be read by eye against a printed chart, so distance, angle and ambient light move "
       "the numbers more than the chemistry does.",
 unlocks="Dosing and alarms in hydroponics, aquaria, pools and fermentation that respond to "
         "the water rather than to a schedule, with a record of what the water actually "
         "did.",
 market="Hydroponics, aquaculture and aquaria, pools and spas, brewing, environmental "
        "monitoring"),

"water-nutrients": dict(
 fools="Conductivity is not nutrition. An EC or TDS probe counts every ion equally, so "
       "calcium and magnesium in hard water read exactly like fertiliser while sugar, "
       "alcohol and urea are invisible. The ppm figure is not even a measurement: it is "
       "conductivity multiplied by a convention factor of 0.5, 0.64 or 0.7, so two honest "
       "meters can disagree by 40 % on the same tank. Worse, EC hides the failure that "
       "matters: a reservoir whose nitrogen is exhausted while sodium and sulphate "
       "accumulate shows an unchanged EC while the plants starve. Temperature is the "
       "largest single error at roughly 2 % per degC, and it must be the water's. "
       "Two-electrode probes polarise under continuous DC excitation and walk steadily "
       "downward, and a month of declining EC is more often a biofilm-coated probe than a "
       "depleted solution. A nitrate electrode responds to chloride strongly enough that "
       "road salt reads as a fertiliser event, and a nonactin ammonium membrane responds to "
       "potassium almost as strongly as to ammonium.",
 unlocks="Dosing to what the solution actually lacks rather than to a single number, and "
         "catching salt accumulation before it stunts a crop - the failure that a stable EC "
         "reading actively conceals.",
 market="Hydroponics and vertical farming, aquaponics, greenhouse growers, aquaculture"),

"water-sanitised": dict(
 fools="Every one of these answers has pH hiding inside it. An ORP probe measures oxidising "
       "tendency, not chlorine: the same free-chlorine concentration reads roughly 80-100 "
       "mV lower at pH 8.0 than at pH 7.2, so a controller chasing an ORP setpoint without "
       "pH control doses chlorine forever into an alkaline pool. Cyanuric acid suppresses "
       "it further - 50 ppm of stabiliser can cost 100 mV at unchanged chlorine, so a "
       "properly sanitised outdoor pool may never reach the 650 mV rule of thumb. An "
       "amperometric membrane probe measures hypochlorous acid, not free chlorine, and its "
       "share is set by pH with a pKa of 7.54: about 75 % at pH 7.0, 24 % at pH 8.0. It is "
       "flow-dependent too, since the membrane consumes what it reads: around 30 L/h "
       "through the cell is typical, and a clogged strainer reads as a chlorine drop. "
       "Chlorine dioxide, ozone and bromine all reduce at the same cathode, and an "
       "electrochemical Cl2 cell gives roughly full-scale response to ozone. And a UV "
       "sensor reads irradiance at its own window, never dose, while germicidal tubes lose "
       "30-40 % of their output over about 9000 hours.",
 unlocks="Closed-loop sanitation that stays inside a safe band without over-dosing, and a "
         "defensible log of disinfection for a pool, a spa, a brewery or a small water "
         "system.",
 market="Pools and spas, water treatment, food and beverage, aquaculture, facilities"),

"water-oxygen": dict(
 fools="This is the one water measurement where the sensor consumes what it measures: a "
       "galvanic probe depletes oxygen in its own boundary layer, so in still water it "
       "reads progressively low, which is why every commercial installation stirs or pumps "
       "past the membrane. The number means nothing until corrected for temperature, "
       "salinity and barometric pressure — uncompensated readings run tens of percent out. "
       "Thresholds matter more than precision: the US EPA's aquatic-life benchmark is 5 "
       "mg/L, but EPA's own CADDIS materials note some mayflies show effects at 9 mg/L, and "
       "productive water swings from afternoon supersaturation to pre-dawn depletion, so "
       "the reading that kills fish is the one a daytime spot check never sees. And ORP is "
       "not an oxygen proxy: pH dominates it by 80-100mV between pH 7.2 and 8.0.",
 unlocks="Aeration that runs when the water needs it rather than all night, fish-kill "
         "prevention with hours of warning, and aerobic-process control in digesters and "
         "wastewater.",
 market="Aquaculture, wastewater treatment, aquaponics, environmental monitoring, "
        "fermentation"),

"water-clarity": dict(
 fools="The cheap board does not measure turbidity as the standards define it: NTU is "
       "scattered light at 90 degrees (ISO 7027 / EPA 180.1) and the SEN0189 measures how "
       "much gets THROUGH, which diverges completely at low turbidity where transmission "
       "barely changes — and the widely-copied NTU polynomial in its sample code is a fit "
       "to one unit in one cuvette at 25°C. Colour is indistinguishable from particles, so "
       "tannin-stained peat water reads as high turbidity with almost no suspended solids "
       "in it, collapsing the three things you were trying to separate into one number. "
       "Bubbles produce sharp false spikes, ambient light leaks straight in so the reading "
       "follows the sun through the day, and in very muddy water the response goes "
       "non-monotonic. Biofilm over 2-4 weeks drives it up monotonically — log every clean, "
       "or the dataset is a record of your maintenance schedule.",
 unlocks="Runoff and pollution events caught as they happen rather than reconstructed "
         "afterwards, and filtration or backwash triggered by the water rather than by a "
         "timer.",
 market="Water utilities, aquaculture, environmental agencies, citizen science, aquarium and "
        "pool"),

"water-hot-enough": dict(
 fools="Where you measure and how long you wait matter far more than the sensor's accuracy. "
       "HSE's HSG274 Part 2 sets the targets: hot water stored at 60 degC, reaching 50 degC "
       "at the outlet within one minute of running, and cold water below 20 degC after two "
       "minutes - all conditional on time, so a probe on a static pipe is reading the pipe, "
       "not the system. A probe in a brass tee reads the brass for the first 10-30 seconds "
       "of flow; a sensor clamped outside a pipe mostly reads room air unless bedded in "
       "paste and insulated; and an air-filled thermowell can lag by minutes, and needs "
       "about ten stem diameters of immersion. For thermal power the absolute accuracy is "
       "irrelevant and the relative offset is everything: two DS18B20s each inside their "
       "own plus or minus 0.5 degC specification but 0.4 degC apart turn a 3 K delta-T into "
       "a 13 percent error in kW. And counterfeit DS18B20s are the dominant hardware "
       "failure, announcing themselves with a stuck 85.00 degC, the power-on-reset "
       "scratchpad value meaning the conversion never completed.",
 unlocks="Legionella compliance evidence, scald protection, and honest solar-thermal or "
         "heat-pump performance figures instead of manufacturer claims.",
 market="Landlords and facilities, plumbing and heating, care homes, breweries, solar "
        "thermal"),

"thermal-energy-moved": dict(
 fools="The answer is a product of a temperature DIFFERENCE and a flow, and both halves fail "
       "multiplicatively. Absolute probe accuracy is nearly irrelevant and relative offset "
       "is everything: two DS18B20s reading 0.4°C apart in the same stirred glass turn a 3K "
       "delta-T into a 13% error in kW, so sort your probes in a bath and store per-probe "
       "offsets before plumbing anything. A probe in a brass tee reads the brass for the "
       "first 10-30 seconds of flow, so short draws systematically under-report. The flow "
       "half is worse — a YF-S201 is 450 pulses/L ±15% per unit and badly non-linear below "
       "2 L/min, and a clamp-on TUF-2000M transit-time meter reports tens of litres an hour "
       "at a closed valve unless zeroed with flow stopped. And kW = flow(L/s) x delta-T(K) "
       "x 4.186 is water's constant; a glycol loop carries a specific heat 10-20% lower.",
 unlocks="Heat-pump COP, solar-thermal yield and hot-water losses measured rather than "
         "modelled — the only way to tell an underperforming system from an over-optimistic "
         "specification.",
 market="Heat pumps and renewables, plumbing and heating trades, district heating, energy "
        "auditors"),

"soil-tension": dict(
 fools="Tension routes are slow by physics and blind at the end that matters. A gypsum block "
       "or granular-matrix sensor equilibrates over hours, a short irrigation comes and "
       "goes before the block notices. Both are resistance devices, so anything that "
       "changes soil salinity changes the reading - fertigation or saline irrigation water "
       "makes dry soil look wet - and the gypsum buffer that gives them their salinity "
       "tolerance is the part that dissolves away. Resistance falls roughly 3 percent per "
       "degree, so without a co-located soil temperature probe you get a daily sawtooth "
       "that looks convincingly like the plant drinking and sleeping. The wet end is the "
       "shared blind spot - above about -30 kPa a gypsum block has almost no resolution and "
       "a ceramic dielectric part saturates at -9 kPa, exactly the range around field "
       "capacity where over-watering happens. And a true water-filled tensiometer avoids "
       "the salinity problem and introduces air: one bubble breaks the suction path and it "
       "reports zero tension while the soil is bone dry.",
 unlocks="Irrigation scheduled on the energy a root must spend rather than on a moisture "
         "percentage that means different things in sand and in clay.",
 market="Vineyards, orchards, row crops, greenhouses, irrigation consultants"),

"soil-ready-to-plant": dict(
 fools="The question has a depth and a duration hidden inside it. Oregon State Extension's "
       "germination tables put the minimum at 50°F for corn and tomato and 60°F for beans, "
       "but the same tables show corn taking 22 days to emerge at 50°F against 7 days at "
       "68°F — so 'warm enough to germinate' and 'warm enough to be worth sowing' are weeks "
       "of rot risk apart, and Purdue's agronomy extension frames the practical rule as an "
       "average of 61-62°F per day at 4 inches rather than a threshold at all. Soil at 5cm "
       "and 15cm can differ by several degrees on a sunny afternoon, so a reading without a "
       "stated depth is meaningless and an afternoon value is the peak, not the day. And "
       "counterfeit DS18B20s miss the ±0.5°C spec by 2-4°C, while 85.00 is the "
       "power-on-reset register value rather than a temperature.",
 unlocks="Sowing dates set by the ground rather than the calendar — in a marginal spring, "
         "the difference between a crop and a reseed.",
 market="Growers, market gardens, agronomy, community gardens, horticulture education"),

"disease-pressure": dict(
 fools="Disease models are fed on leaf wetness hours and on humidity above a threshold, and "
       "both are weaker than the models assume. Leaf wetness has no traceable standard: "
       "mount the same board at 30 degrees instead of 45 and the wet-hours count changes, "
       "and the model you are feeding was calibrated on a different sensor. A wetness board "
       "is a PCB, not a leaf, so it dews and dries tens of minutes away from the crop. "
       "Dust, pollen and dried spray residue are hygroscopic, so a dirty board reads wet at "
       "80 % RH, and it develops over weeks like a seasonal trend. A DHT22 saturates above "
       "~95 % RH and takes hours to recover after condensation, and the Si7021's specified "
       "accuracy band stops at 80 % RH - precisely where infection lives. RH is referenced "
       "to the sensor's own temperature, so a board reading 1 degC high shifts humidity by "
       "roughly six points, and an unshielded probe in sun reads 5-15 degC high. And the "
       "sunlit and shaded sides of one tree report wildly different wetness hours.",
 unlocks="Spraying on infection risk rather than on the calendar, which cuts both fungicide "
         "cost and resistance pressure - and gives a defensible record of why a treatment "
         "was or was not applied.",
 market="Vineyards, orchards, protected cropping, agronomy advisers, turf management"),

"growth-rate": dict(
 fools="Growth is a slow trend under faster ones, and the fast ones are what you record. "
       "Load-cell creep sags a scale 0.02-0.05 % of applied load over the first thirty "
       "minutes, and temperature moves zero and span by 0.01-0.05 % of full scale per degC "
       "- outdoors, larger than a week of growth. A dendrometer is the sharpest instrument "
       "here and the most easily fooled: steel expands about 11 um per metre per degC and "
       "aluminium 23, while the signal is single-digit micrometres, so a metal-framed "
       "dendrometer through a 20 degC diurnal swing produces a fake growth-and-shrink cycle "
       "in phase with air temperature - which is why serious builds use Invar at 1.2 "
       "ppm/degC. Even done right, most of what it sees is water, not wood: the trunk "
       "swells overnight and shrinks through the day. Bark is hygroscopic and steps upward "
       "within minutes of rain, and mounting screws creep into the wood for weeks and read "
       "as a false decline. The proxies drift too: a capacitive soil probe wicks water up "
       "into the header, and a leaf clip changes with chlorophyll, dust and the leaf "
       "outgrowing it.",
 unlocks="Growth measured in days rather than seasons - stress detected before wilting, and "
         "a quantitative answer to whether a treatment, a nutrient change or a new cultivar "
         "actually did anything.",
 market="Research horticulture, forestry, breeding programmes, vertical farming, agronomy"),

"fruit-ripe": dict(
 fools="The honest limit is spectral coverage. The features that make near-infrared food "
       "science work - water at 1450 and 1940 nm, and the C-H overtones for sugar, fat and "
       "starch - sit beyond 1000 nm, where silicon photodiodes are blind. An AS7263 stops "
       "at 860 nm and an AS7265x at 940 nm, so you are measuring chlorophyll, scattering "
       "and surface colour: appearance, not composition. Geometry then beats chemistry. "
       "Reflectance falls as 1/d squared, so moving a sample 2 mm closer shifts every "
       "AS7265x channel by 20 %, and curvature does the same - a fruit's shoulder and its "
       "cheek classify differently. A glossy or wet skin bounces the sensor's own LED into "
       "the aperture and drowns the diffuse signal. The chips self-heat once the LEDs fire, "
       "so a spectrum taken 30 s into a run differs from one taken cold, and "
       "channel-to-channel gain matching is only about +/-12 % from the factory. A "
       "classifier scoring 98 % on your ten samples in your jig is measuring your fixture.",
 unlocks="Non-destructive sorting and harvest timing on a per-fruit basis, and a repeatable "
         "in-house grading standard where today the answer is a thumb and an opinion.",
 market="Growers and packhouses, farm shops, food research, retail quality control"),

"light-dose-daily": dict(
 fools="Lux is a human unit and a plant is not human. A BH1750 or VEML7700 carries a "
       "photopic filter shaped to the eye, which throws away the deep red and blue a plant "
       "uses, so a red/blue LED grow panel can read at half its true photosynthetic output; "
       "the right quantity is photosynthetic photon flux, and converting lux to it needs a "
       "factor for your lamp. Even as lux meters these parts are +/-10-20 % against nothing "
       "traceable. Vishay publishes a non-linearity correction for the VEML6030 and "
       "VEML7700 at high gain, and firmware that skips it under-reads bright sunlight by "
       "20-30 %, which looks like endless cloud. A TSL2561 or TSL2591 does worse: both "
       "channels saturate abruptly and the standard formula then returns a low number, so "
       "direct sun can read darker than a dim room unless you check the overflow bit. A "
       "daily integral compounds any systematic error across every sample rather than "
       "averaging it out, and cosine error without a diffuser under-reports mornings and "
       "evenings. And PPFD a metre from a lamp says nothing about a canopy 300 mm lower.",
 unlocks="Supplementary lighting driven by what the plant actually received rather than by a "
         "timer, and an honest per-position audit of a grow tent or greenhouse instead of "
         "the best spot somebody found.",
 market="Indoor growing, greenhouses, vertical farming, houseplant products, horticultural "
        "research"),

"compost-active": dict(
 fools="Surface temperature is the opposite of the answer: a stack radiates from its face "
       "while the core can be 50 degC hotter, so an infrared thermometer is useless. The "
       "lance replacing it lies twice. Steel is a heat pipe, so an exposed section conducts "
       "heat out and the shallowest sensor reads low, and water tracking down it shorts "
       "sensors into a uniform profile that reads as a well-mixed pile. One lance samples "
       "about 20 mm of a 20-tonne stack, and hay fires start in a localised wet pocket. The "
       "signal is the rate of rise: 55-65 degC is a healthy thermophilic pile, above 70 "
       "degC the microbes that made the heat begin dying, and a stack climbing 5 degC a day "
       "toward 70 is worse than one flat at 65 - while a pile that suddenly cools may be "
       "venting up a chimney of its own. An STC31 is a thermal-conductivity meter told to "
       "assume CO2 in air, so a saturated headspace costs whole percent and methane drives "
       "it wrong, and an SCD30's self-calibration assumes ~400 ppm fresh air weekly, false "
       "in a covered heap.",
 unlocks="Turning the heap on evidence rather than on a schedule, and - for hay, silage and "
         "large green-waste piles - an early warning of spontaneous combustion that surface "
         "inspection cannot give.",
 market="Community composting, farms and stables, municipal green waste, insurers"),

"livestock-wellbeing": dict(
 fools="Welfare is a composite and every channel in it lies in a barn. Metal-oxide sensors "
       "are the worst: an MQ-135's ammonia response is real but swamped by 90 percent RH "
       "and by the night-to-day temperature swing, so without a co-located RH sensor and a "
       "multi-day baseline you are logging the weather, and the MiCS-6814's three channels "
       "are not independent - its oxidising channel reads lower in the presence of reducing "
       "gases, and its ammonia channel responds to any amine and to alcohols. A proper "
       "electrochemical NH3 cell fixes selectivity and adds stickiness: ammonia adsorbs "
       "onto tubing and the cell's own membrane, so your reading lags reality by most of a "
       "shift, and NH3 cells are among the shortest-lived electrochemical types at well "
       "under two years in continuous service. Load cells creep under sustained load and "
       "move with temperature outdoors, and an FDX-B ear tag reader is blind to a tag lying "
       "perpendicular to its field or sitting within a few centimetres of a steel gate. And "
       "comfortable is a judgement, not a measurement.",
 unlocks="Earlier intervention on ventilation, heat stress and disease, and a documented "
         "welfare record for assurance schemes rather than a stockman's recollection.",
 market="Poultry and pig producers, dairy, assurance schemes, veterinary, agricultural "
        "research"),

"power-now": dict(
 fools="A current transformer alone gives apparent power in VA, which for anything with a "
       "motor or a switching supply differs substantially from watts: a fridge compressor "
       "measured as RMS volts times RMS amps can be 40 percent wrong. Real power needs "
       "voltage and current sampled at the same instant, which is why a multiplexed "
       "converter is the wrong tool: an ADS1115 runs its four channels sequentially through "
       "one ADC, and even a three-channel INA3221 lands its readings milliseconds apart, "
       "which is why an energy balance on a switching MPPT never closes however reasonable "
       "each number looks. Transducer phase is the next error: split-core CTs have a phase "
       "shift that grows as current falls, several degrees at 1 percent of rating, so a "
       "small load reports a wildly wrong power factor until the per-channel "
       "phase-calibration registers are set - and size the CT to the load, because a 100 A "
       "CT watching a 40 W standby load works inside half an LSB. And the safety layer is "
       "not optional - a shunt-based metering chip puts your whole low-voltage side at line "
       "potential, and an unburdened CT clipped around a live conductor behaves as a "
       "step-up transformer.",
 unlocks="Real watts and real kWh - the number a tariff, a payback calculation or a solar "
         "self-consumption strategy actually needs, rather than a plausible one that is "
         "systematically wrong.",
 market="Energy retailers, solar installers, facilities, landlords, EV charging"),

"phantom-load": dict(
 fools="The no-load threshold is the enemy and it is deliberate: metering chips suppress "
       "small readings to keep noise out of the energy total, so the thing you are hunting "
       "is engineered out of the answer. A BL0940 reads a flat zero below its threshold, an "
       "ADE7953's no-load setting will make a 2 W standby load vanish entirely, and an "
       "Eastron SDM120 is Class 1 only above about 1 % of its rated current, which on a 45 "
       "A meter means a 2 W phantom is noise. Transducer sizing does the same. An SCT-013 "
       "rated to 100 A has poor accuracy at low currents, and a 100 A CT reading a 40 W "
       "load on an ATM90E32AS works inside half an LSB. A CT alone also gives apparent "
       "power, and standby loads are the ones with terrible power factor - a switch-mode "
       "supply idling can draw several times the current its watts suggest. A PZEM-004T "
       "reports real power but updates once a second. And clamped around a whole flex "
       "containing live and neutral, the fields cancel and the meter reads zero.",
 unlocks="An itemised standby budget, which is usually the cheapest kilowatt-hours a "
         "household or office will ever save, and the evidence to justify switching or "
         "replacing specific equipment.",
 market="Energy retailers and efficiency programmes, facilities, landlords, IT estates"),

"solar-performance": dict(
 fools="Comparing production against a horizontal pyranometer, which cannot tell you what a "
       "35-degree array receives, is the commonest error here. The sensor is also "
       "spectrally narrow: a silicon cell responds roughly 400-1100 nm while sunlight "
       "extends past 2500 nm, so heavy cloud, a low sun angle or snow reflection produce "
       "10-25 % error, invisible in the data. Cosine error without a good diffuser "
       "under-reports mornings and evenings, so daily kWh/m2 totals come out low, and two "
       "degrees out of level is 1-3 % at low sun. A thermopile's 10-20 second response "
       "cannot follow broken cumulus. An INA3221's 26 V common-mode maximum is absolute, "
       "and a 24 V panel sits at 36-45 V open-circuit, which destroys the chip. Its three "
       "channels share one ADC and convert sequentially, so on a switching MPPT the energy "
       "balance will not close while every number looks reasonable. And module temperature "
       "costs several percent on a hot roof, so soiling, shading, degradation and a warm "
       "day explain one shortfall.",
 unlocks="Knowing whether an underperforming array is dirty, shaded, hot, mis-strung or "
         "genuinely failing - which is the difference between a cleaning visit and a "
         "warranty claim.",
 market="Solar installers and O&M, off-grid households, commercial estates, insurers"),

"battery-charge": dict(
 fools="Voltage-only gauges never measure current, so every number comes off a curve. Switch "
       "on a 500 mA load and internal resistance drops terminal voltage instantly - "
       "reported state of charge falls off a cliff, then crawls back over several minutes "
       "after the load stops. On LiFePO4 and most sodium chemistries the discharge curve is "
       "flat within roughly 100 mV from 20 to 80 percent, which makes a voltage gauge "
       "useless over exactly the range you care about. Coulomb counting trades that for "
       "shunt error: a 10 mOhm resistor at 1 percent tolerance plus a few microvolts of "
       "amplifier offset is a percent per day of drift, correctable only when the pack "
       "genuinely rests - under a permanent trickle load it never gets a clean open-circuit "
       "voltage. Impedance-tracking gauges learn real capacity only after an uninterrupted "
       "cycle - full charge, two hours rest, steady discharge to terminate - which a solar "
       "node breaks every day, after which the gauge reports against the DesignCapacity you "
       "typed in. And a plain INA219 cannot see sleep current at all: plus or minus 100 uV "
       "of shunt offset across 0.1 Ohm is plus or minus 1 mA.",
 unlocks="Runtime estimates you can act on, and the separation of two very different "
         "statements: the battery is low today, and the battery has aged.",
 market="Off-grid and solar, robotics, wearables, e-bikes and e-mobility, instrumentation"),

"battery-health": dict(
 fools="Health is not charge. A voltage-only gauge never sees current, so a 400 mAh and a "
       "4000 mAh cell at 3.80 V report the same percentage and neither reports health - and "
       "on LiFePO4, flat within about 100 mV from 20 % to 80 %, it barely works as a fuel "
       "gauge. Coulomb counters do better only if their shunt behaves: a 10 mOhm resistor "
       "at 1 % tolerance plus a few microvolts of amplifier offset becomes percent-per-day "
       "drift, and the MAX17260 can only correct it when the pack genuinely rests, which a "
       "trickle-loaded node never does. The BQ27441 learns real capacity only after an "
       "uninterrupted charge, two-hour rest and steady discharge to terminate voltage - "
       "interrupt it, as a solar node does daily, and it keeps reporting the DesignCapacity "
       "you typed in. Anything wired around the sense resistor, such as a bodged 5 V tap, "
       "is invisible. And the MQ-8 hydrogen route is a 300 degC tin-oxide bead that also "
       "answers to alcohol and CO: an ignition source installed where the fuel collects.",
 unlocks="Replacing cells on evidence rather than on a calendar, and predicting the winter a "
         "solar node will not survive before it dies in the field.",
 market="Off-grid solar, e-mobility, UPS and backup estates, product engineering"),

"energy-cost": dict(
 fools="The metering silicon is rarely the error; the transducers and the tariff are. Real "
       "power is the time average of v(t)i(t), which a PZEM-004T computes and a clamp meter "
       "multiplying RMS volts by RMS amps reports apparent power and can be 40% wrong on a "
       "fridge compressor, and a split-core CT's phase shift reaches several degrees at 1% "
       "of rating unless the ATM90E32AS per-channel phase registers are set. Size the CT to "
       "the load: an Eastron SDM120 is Class 1 only over its specified current range, and "
       "below about 1% of rating the reading is noise, so a 45A meter cannot see a 2W "
       "phantom load. Then the larger error — kWh is not cost. Time-of-use bands, standing "
       "charges and export rates mean a correct kWh figure times an average unit price is "
       "wrong by more than any metering error.",
 unlocks="Arguments you can win: the true cost of a dryer cycle, a kiln firing or an "
         "always-on server, and a replacement's payback computed from your own tariff "
         "rather than a label.",
 market="Households, landlords, small business, energy retailers, makerspaces"),

"power-quality": dict(
 fools="Power quality is defined by aggregation, not by a reading, which is what these "
       "routes get wrong. EN 50160 specifies supply characteristics at the customer "
       "terminals over a one-week campaign: the 10-minute mean voltage within Un +/-10 % "
       "for 95 % of the week, frequency within 50 Hz +/-1 % for 95 % of it, total harmonic "
       "distortion at or below 8 %, and long-term flicker Plt at or below 1, with up to 5 % "
       "of samples non-conforming. An instrument that cannot produce 10-minute aggregates "
       "over a week is not answering that question. A PZEM-004T updates once a second, so "
       "it tells you the average is fine and never sees the sag that rebooted your "
       "equipment. A ZMPT101B preserves the waveform, but its core saturates and flattens "
       "exactly the peaks a swell would show, its gain trimpot ships at an arbitrary "
       "position, and sampling must lock to whole mains cycles or the RMS wanders. "
       "Split-core CTs have a phase shift of several degrees at 1 % of rating, and crest "
       "factors above 3 clip the current channel. And an AMC1311's isolation rating is the "
       "die's, not your board's.",
 unlocks="Evidence in a dispute with a utility or a landlord, protection for sensitive "
         "equipment, and a diagnosis for the intermittent faults that only ever happen when "
         "nobody is watching.",
 market="Facilities, IT and data centres, manufacturing, solar installers, electrical "
        "contractors"),

"device-left-on": dict(
 fools="The cheap routes each answer a different question. A light sensor sees the indicator "
       "LED, not the load, and every photopic part is deliberately blind to infrared, so it "
       "cannot verify a heater element or a 940 nm illuminator at all; and the LDR version "
       "adds tens of percent of part-to-part spread and a memory effect that takes minutes "
       "to settle after darkness. Current routes miss standby loads by construction: a "
       "metering chip's no-load threshold exists to stop noise creeping into the energy "
       "total, and set too high it makes a 2 W phantom load vanish entirely; a 100 A CT "
       "reading a 40 W load is working inside half an LSB; and an INA219 cannot resolve "
       "microamps, because plus or minus 100 uV of shunt offset across 0.1 Ohm is plus or "
       "minus 1 mA. The commonest wiring error kills the whole build: clamp a current "
       "transformer around a whole flex containing live and neutral and the equal and "
       "opposite fields cancel, so a kettle drawing 10 A reads zero.",
 unlocks="Automatic shutoff for irons, hobs, soldering stations and printers, and a "
         "standby-load audit that names the devices rather than reporting one house-level "
         "number.",
 market="Households, insurers, makerspaces, schools, facilities"),

"energy-budget-node": dict(
 fools="The question is an integral over months, and most instruments cannot see the term "
       "that dominates it. Sleep current is the whole budget, and an INA219 cannot resolve "
       "it: +/-100 uV of shunt offset across 0.1 ohm is +/-1 mA of zero error, so an "
       "ESP32's deep-sleep draw cannot be measured with the stock board. An INA3221 is "
       "worse, with roughly a 0.4 mA floor on 100 mOhm shunts, so a 10 uA sleeping node is "
       "invisible. A voltage-model fuel gauge knows nothing about your pack's capacity, "
       "reads 15-20 % low on a cold cell at 0 degC, and drops off a cliff when a 500 mA "
       "load switches on; a BQ27441 only learns real capacity after an uninterrupted "
       "charge, rest and full discharge, which a solar node interrupts every day, after "
       "which it reports the number on the label. And a horizontal pyranometer cannot tell "
       "you what a tilted panel receives, its silicon cell carries 10-25 % spectral error "
       "under cloud and low winter sun, and cosine error under-reports mornings and "
       "evenings.",
 unlocks="Deploying a sensor once and not visiting it again - the difference between a "
         "monitoring network and a maintenance liability.",
 market="Environmental monitoring, agriculture, utilities, remote infrastructure, "
        "conservation"),

"intrusion": dict(
 fools="An intrusion detector is judged on its false-alarm rate: an alarm nobody believes is "
       "worse than none. A reed switch is held closed by any magnet held near it - which is "
       "why real security contacts are balanced-biased types that detect an added external "
       "field - and its contacts bounce for up to a millisecond, so an undebounced ISR logs "
       "one door opening as five. PIR reports change in mid-infrared, so a motionless "
       "intruder vanishes while a sunlit patch or steam from a kettle fires it, and above "
       "about 30 degC the body-to-background contrast collapses. Every 24 GHz radar here "
       "sees through plasterboard, hollow doors and glass, so your lounge sensor reports "
       "the neighbour; per-gate masking is not tuning, it is the install. An RCWL-0516 also "
       "triggers on its own board's Wi-Fi burst and on rain down a window. A fibre fence "
       "line cannot say where or what, and a gust on chain-link outweighs a person leaning "
       "on it. And Wiegand-26 has no authentication at all: a cheap cloner copies a card in "
       "a second.",
 unlocks="Alarms people act on. Corroborating two independent modalities - and logging the "
         "raw stream rather than only the verdict - is what turns a nuisance sensor into "
         "evidence.",
 market="Home security, small business, self-storage, agriculture, remote sites"),

"glass-broken": dict(
 fools="A real glass-break signature is a low-frequency thump as the pane flexes followed "
       "within milliseconds by a high-frequency shatter, and almost every cheap route sees "
       "one half of it. A comparator module trips on instantaneous amplitude with no "
       "frequency discrimination, so a door slam and mains hum on a long lead are "
       "indistinguishable from breaking glass - and one event produces 5-30 output edges "
       "over a few milliseconds, which a naive counter reads as several breaks. A raw MEMS "
       "microphone can see both bands, and then the enclosure lies to you: a 2 mm port "
       "makes a Helmholtz resonator that adds 3-8 dB somewhere between 2 and 8 kHz, a "
       "microphone bolted to a wall becomes a contact microphone reporting footsteps "
       "upstairs, and a quiet room at night sits at the part's own 29-33 dB(A) noise floor. "
       "Contact routes listen to the pane and bring their own distortions: a bare 27 mm "
       "piezo disc rings around 3-7 kHz; the bond changes sensitivity by more than 20 dB; "
       "and PVDF film is pyroelectric, so sunlight crossing it looks like a bend.",
 unlocks="Perimeter alarm coverage for a whole room from one sensor, without a contact and a "
         "wire on every pane, and a signature you can review after an alarm rather than a "
         "bare trigger.",
 market="Security installers, insurers, retail, holiday properties, museums"),

"vehicle-approaching": dict(
 fools="Detection is easy; 'vehicle' and 'approaching' are the hard words. Magnetic routes "
       "are the most specific and the most fragile — Earth's field is only 25-65uT, so a "
       "lift two floors away or a charger being plugged in moves an MMC5603 by many times "
       "its noise floor. An E18-D80NK beam cannot separate a car from a cyclist or a "
       "wheelie bin, and dust or a spider web on the lens leaves the output permanently "
       "triggered. An SM-24 geophone hears the approach and hear wind through a fence post "
       "just as loudly. The routes that give closing speed mislead characteristically: the "
       "TF-Luna emits 0 on a weak return, so code that ignores its amplitude field reads "
       "dropouts as 'obstacle at 0cm', and an AWR1642's Doppler clutter filtering deletes a "
       "stationary vehicle entirely — which is precisely how early automotive radars drove "
       "into parked cars.",
 unlocks="Gates, lighting and cameras that respond before the vehicle arrives rather than "
         "after, plus delivery alerts on long drives and traffic counts at a site entrance.",
 market="Smart home, agriculture, logistics and yards, security, parking"),

"fire-present": dict(
 fools="The cheap KY-026-class IR flame modules are near-infrared level detectors with a "
       "potentiometer and nothing more. Sunlight, a halogen lamp, a quartz heater and your "
       "TV remote all saturate them, and anything modulated in the 1-15Hz flame band — a "
       "fan blade past a window, sun through leaves — defeats even a good flicker filter. "
       "They go blind in the other direction too, which is the dangerous one: alcohol and "
       "hydrogen flames emit almost nothing in the 760-1100nm band, so a methanol fire is "
       "invisible, and ordinary glass is transparent in the near-IR so the sensor happily "
       "'detects' a bonfire outside. Thermocouple routes lie quietly — the MAX31855 reports "
       "open-circuit fault bits most sketches ignore, so a snapped probe reads 0 degrees C "
       "and a control loop heats forever.",
 unlocks="Early warning where a smoke detector is too slow or in the wrong place: kilns, "
         "forges, laser cutters, biomass boilers and unattended 3D printers.",
 market="Only ever alongside certified detection. Makerspaces, workshops, laboratories, "
        "industrial process"),

"unusual-sound": dict(
 fools="Unusual means unlike this place's own baseline, and most cheap routes destroy the "
       "information needed to build one. A comparator module has no frequency "
       "discrimination and no hysteresis, so its sensitivity setting is a knife edge that a "
       "few degrees of temperature moves, and one event yields 5-30 edges over a few "
       "milliseconds. An AGC microphone normalises loudness, which is the point and also "
       "the trap: it can tell you a sound happened and roughly what it sounded like but "
       "never how loud, and its release time means a second bang 300 ms after the first "
       "measures quieter. A sound-level module reports A-weighted fast SPL and nothing "
       "else, A-weighting discounts the low frequencies that dominate a complaint about the "
       "party next door. Raw MEMS microphones give you the spectrum and inherit the "
       "enclosure: a 2 mm port is a Helmholtz resonator adding 3-8 dB somewhere between 2 "
       "and 8 kHz, wind across an unshielded port produces tens of dB that is not sound at "
       "all, and a quiet room sits at the part's own 29-33 dB(A) noise floor. And a piezo "
       "disc on a wall is a contact microphone for the room next door.",
 unlocks="Anomaly detection that does not require recording speech: a failing pump, a broken "
         "window, a distressed animal, a machine that has changed its note.",
 market="Security, facilities, manufacturing, veterinary, urban noise studies"),

"perimeter-crossed": dict(
 fools="Two questions hide in one, and most routes answer only 'whether'. An intensity-based "
       "fibre run along a fence gives no location at all; wind on chain-link produces a "
       "larger signal than a person leaning on it; and every tight zip tie is a permanent "
       "microbend, so the 'distributed' sensor is really a handful of accidental hot spots "
       "with dead zones between them — and one strimmer cut takes the whole run offline "
       "with no indication of where. An SM-24 geophone localises well and hears wind "
       "through a fence post just as loudly. Beam routes are unambiguous and easy to step "
       "over: a light curtain protects a PLANE, not a volume, and its safe mounting "
       "distance is an ISO 13855 calculation from response and stopping time. And nothing "
       "here separates a person from a deer.",
 unlocks="Boundary alerting that says where as well as whether — the difference between an "
         "alert people act on and one that gets muted in the second week.",
 market="Agriculture, critical infrastructure, construction sites, conservation, industrial "
        "safety"),

"stove-left-on": dict(
 fools="Emissivity decides whether the thermal routes work, and a kitchen is full of "
       "surfaces that defeat them: a stainless pan or a glass-ceramic hob reads far cooler "
       "than it is, and a shiny surface also shows the sensor a reflection of the ceiling. "
       "Resolution is next: an AMG8833 is 64 pixels, so an object at a few metres is "
       "averaged with the wall behind it, giving a 3 degC signal against a +/-2.5 degC "
       "accuracy spec, and an MLX90614's roughly 90-degree field of view averages a 2 m "
       "circle at 1 m. Glass and most plastics are opaque at 8-14 um, so there is no "
       "looking through an oven door, and the frame drifts with the sensor's own die "
       "temperature after power-up. The flame and gas routes are worse: a KY-026 is "
       "saturated by sunlight, a halogen lamp or a boiled kettle and is blind to alcohol "
       "and hydrogen flames, while an MQ-2 or MQ-4 responds to frying oil, cleaning spray "
       "and humidity in the same direction as gas. And a hob just switched off looks "
       "exactly like one still on.",
 unlocks="Automatic hob shutoff and a reassuring 'the kitchen is safe' check - one of the "
         "few sensing projects with a documented life-safety payoff for people living with "
         "dementia.",
 market="Elder care, assisted living, insurers, student accommodation, housing associations"),

"authorised-to-use": dict(
 fools="Tags answer 'which token is present'. on an RC522/MFRC522, MIFARE Classic's CRYPTO1 "
       "has been broken since 2008 and the UID is neither secret nor unique; an RDM6300 "
       "reads EM4100's 40 bits in the clear; and Wiegand-26 carries just 24 usable bits, so "
       "duplicate card numbers across sites are arithmetic rather than a defect, while an "
       "inline sniffer behind the reader replays every credential that passes. Biometrics "
       "move the problem instead of solving it — the R503 is an OPTICAL reader imaging "
       "ridges, so a gelatin cast defeats it, and its default UART password is all zeros. "
       "The ATECC608B is the only clone-resistant route here, and only if the host issues a "
       "fresh random challenge every time.",
 unlocks="Machine authorisation that reflects training records rather than who is in the "
         "room, plus per-user tool logging and consumable billing in shared workshops.",
 market="Makerspaces, workshops, manufacturing, laboratories, equipment hire"),

"where-am-i": dict(
 fools="A fix that looks respectable can be tens of metres wrong. Reflected signals are "
       "still valid codes that merely arrived late, so a receiver by a window will happily "
       "report a position 20-50 m out with a healthy-looking HDOP. Multi-constellation "
       "improves availability far more than accuracy - you get a fix where a "
       "single-constellation part cannot, and it is still metres - and position wanders "
       "several metres while stationary, which a naive geofence reads as movement. Height "
       "is the least trustworthy number in the sentence: vertical error is typically 1.5-3 "
       "times horizontal, and the receiver reports height above the WGS84 ellipsoid unless "
       "a geoid model is applied, tens of metres from the height on your map. RTK changes "
       "the scale of the error without making it obvious: centimetres apply only in the "
       "FIXED state, decimetres in float and metres standalone, and corrections older than "
       "a couple of seconds silently degrade you from fixed to float. And any continuously "
       "logged position is identifiable personal data.",
 unlocks="Geofencing, asset recovery, field survey and mapping - and, with RTK, machine "
         "guidance at a price that until recently was professional-only.",
 market="Agriculture, surveying, logistics, drones and robotics, outdoor sport"),

"which-way-facing": dict(
 fools="Two families of route, and each fails exactly where the other does not. A QMC5883L "
       "or BMM350 gives an absolute reference and mostly measures your own project: Earth's "
       "field is only 25-65uT, so a 200mA LED strip 3cm away, a motor or the ESP32's own "
       "switching regulator swamps it — heading wobbles every time Wi-Fi transmits — and "
       "held at any tilt it reports a heading wrong by roughly the tilt angle. Indoors, "
       "rebar and steel studs make absolute heading unrecoverable at any price. Gyros have "
       "no such distortion and no north at all: an L3GD20H reports up to ±25 degrees/s "
       "while sitting perfectly still at power-on, and even the tactical-grade "
       "ADIS16505-2's 3 degrees/hr bias stability integrates to about 3 degrees of heading "
       "in an hour. The seam is where people trip — a BNO086's Game Rotation Vector is "
       "beautifully smooth and has no absolute yaw whatsoever.",
 unlocks="Reliable heading is the difference between a robot that returns to its dock and "
         "one that spirals, and between an antenna or tracker that points where you told it "
         "and one that quietly does not.",
 market="Robotics, drones, marine, surveying, agriculture"),

"how-far-travelled": dict(
 fools="Every route's error grows with distance, and each grows differently. GNSS is bounded "
       "and noisy, which is the trap: a stationary NEO-6M wanders several metres, so "
       "summing successive fixes turns jitter into kilometres of phantom travel across a "
       "day — take a SAM-M10Q's Doppler-derived speed instead, which is far quieter than "
       "differencing positions. Wheel routes are precise and systematically wrong, since a "
       "slipping wheel under-reads and tyre wear changes the circumference. A PMW3901 "
       "optical-flow sensor cannot tell whether it moved or the world did, goes blind below "
       "about 60 lux, and drifts a few percent of distance travelled even when well tuned. "
       "The only architecture that survives is an absolute fix resetting the dead-reckoned "
       "estimate before its error exceeds what you care about.",
 unlocks="Odometry you can trust for maintenance intervals and route logging — and, in sport "
         "and rehabilitation, distance not quietly inflated by a stationary receiver's "
         "wander.",
 market="Robotics, sports, agriculture, fleet management, rehabilitation"),

"how-fast-moving": dict(
 fools="Speed is easy to compute and hard to trust. Differentiating successive GNSS "
       "positions is much noisier than the Doppler-derived speed the receiver already gives "
       "you, and a fix wandering several metres while stationary becomes a phantom walking "
       "pace. Inertial dead reckoning is bounded only by bias: gyro zero-rate offset moves "
       "with temperature at roughly 0.03-0.05 deg/s per degC on consumer parts, and an "
       "accelerometer cannot separate gravity from linear acceleration at all, so braking "
       "and a slope are the same signal - which is why a dedicated automotive "
       "dead-reckoning receiver diverges within 30-60 seconds of tunnel without a "
       "wheel-tick input. Optical flow measures image motion, not ground motion: pure "
       "rotation looks identical to translation unless you subtract gyro yaw, wet tarmac "
       "hands it a moving reflection of the ceiling, and every count is in pixels until you "
       "multiply by a measured height. And radar reads only the radial component, so a "
       "target crossing obliquely reads slow, while the Doppler clutter filtering that "
       "makes a radar usable erases anything with no radial velocity.",
 unlocks="Speed you can defend: traffic evidence, sports telemetry, and robot odometry that "
         "survives a GNSS dropout instead of freezing or jumping to a wall.",
 market="Sports and coaching, robotics, traffic engineering, motorsport, agriculture"),

"am-i-level": dict(
 fools="Every accelerometer route measures the direction of gravity plus every other "
       "acceleration, so a boom or a vehicle reads wrong the whole time it is moving and "
       "tells the truth only once it stops. Vibration rectification decides whether an "
       "inclinometer works on a real machine: broadband vibration is converted into a "
       "genuine DC offset by the sensor's own slight nonlinearity, and almost nobody checks "
       "that spec. Temperature is the next term - an ADXL345's zero-g offset moves up to "
       "150 mg over its range, a couple of degrees, and even the quiet ADXL355 drifts about "
       "0.15 mg per degC per axis, roughly 0.01 degrees per degC, so a sunlit enclosure "
       "manufactures tilt. The ball tilt switch at the bottom of the range is not a sensor: "
       "it reports that a threshold somewhere between 15 and 30 degrees was crossed, and "
       "that threshold varies by 10 degrees between parts from one bag. And none of these "
       "routes sees yaw, so a structure that rotates about the vertical without tilting is "
       "invisible.",
 unlocks="Machines, masts, solar trackers, printer beds and camera rigs that can level "
         "themselves and report how far out they are, rather than needing a spirit level "
         "and a person.",
 market="Construction plant, structural monitoring, machine setup, photography and AV, "
        "agriculture"),

"how-high": dict(
 fools="Barometric altitude is a fiction without a live sea-level reference: an ordinary "
       "weather system moves pressure 20-30 hPa, which is 200-250 m of apparent altitude, "
       "so a static altimeter drifts several floors overnight. Relative altitude over "
       "minutes is excellent - a BMP390 resolves about 25 cm, a BME280 about 20 cm over an "
       "hour - which is why barometers work for a rocket and fail at which floor am I on "
       "tomorrow. The DPS310 has a specific trap: skip the temperature read at cold start "
       "and the compensation uses the wrong coefficient source, giving a smooth, stable "
       "pressure about 60 hPa wrong, roughly 500 m. Two DPS310s side by side can disagree "
       "by 1 hPa, about 8 m, while each tracks its own changes to centimetres - useless for "
       "comparing nodes, which is what a multi-floor deployment does. Indoors an air "
       "handler moves room pressure by several pascals, and an unshielded case reads wind "
       "as altitude. GNSS vertical error is typically 1.5-3x horizontal, and its height is "
       "above the WGS84 ellipsoid unless a geoid model is applied.",
 unlocks="Floor-level location for indoor navigation, lift and stair analytics, drone and "
         "rocket altitude hold, and emergency-responder positioning where a horizontal fix "
         "is not enough.",
 market="Building services, emergency services, drones and model rocketry, indoor navigation"),

"map-surroundings": dict(
 fools="Every route maps one thing and quietly omits another. A 2D scanning LiDAR - RPLIDAR, "
       "LD19 - maps a single horizontal slice, so a tabletop, a step, a cable or a dog is "
       "completely invisible if it does not cross the plane — which is how mapping robots "
       "still drive into things — and matt black absorbs 905nm, leaving holes exactly where "
       "the obstacles are. Glass and mirrors are worse than holes: the beam maps the room "
       "next door, or builds a mirrored ghost room that SLAM fuses in permanently. The "
       "Livox Mid-360's non-repetitive scan leaves large empty wedges in any 0.1s frame, so "
       "a fast-moving obstacle can be genuinely absent. A 40kHz ultrasonic array loses "
       "anything tilted past about 15 degrees, and an AWR1642's Doppler clutter filtering "
       "deletes a stationary person outright.",
 unlocks="Autonomy without a prior map: robots that navigate a space they have never seen, "
         "as-built floor plans in minutes, and navigation aids that do not depend on a "
         "camera.",
 market="Robotics, surveying and AEC, accessibility, warehouse automation, research"),

"obstacle-ahead": dict(
 fools="Every route has a class of object it cannot see, and fails silently. Ultrasound is "
       "specular: anything more than about 15 degrees off perpendicular bounces the ping "
       "away and reads as empty space, so an angled wall or a car bonnet is invisible, "
       "while soft targets absorb and a person in a wool coat drops out. Time-of-flight "
       "optics fail on the other axis: matt black fabric returns about 5 % and halves the "
       "range, while direct sun collapses a VL53L4CD from 1.3 m to 0.4-0.6 m and blinds "
       "whole columns of a VL53L8CX array. Glass and calm water are worse than holes: the "
       "beam either ranges the room beyond or builds a mirrored ghost that SLAM will "
       "happily fuse into the map. Scanning LiDAR sees one horizontal slice, so a tabletop, "
       "a step or a floor cable does not exist. The status byte is the most dangerous "
       "detail: a TF-Luna emits 0 or a low-amplitude flag on a weak return, ST's "
       "RangeStatus likewise, and most example sketches print 8190 mm as though it were a "
       "distance. 77 GHz radar removes stationary targets by design.",
 unlocks="Autonomy that fails safe: robots, wheelchairs, drones and machinery that stop for "
         "the obstacle class they cannot see rather than driving confidently into it.",
 market="Robotics, mobility aids, agricultural machinery, warehouse automation, drones"),

"returned-to-spot": dict(
 fools="Define 'same place' first, because the routes disagree about what same means. A "
       "ZED-F9P gives centimetres only in RTK FIXED state — float is decimetres and "
       "standalone is metres — and code that never reads the carrier-solution flag reports "
       "float as fixed, which makes the whole dataset unfalsifiable. Barometric routes are "
       "precise and completely unanchored: a BMP280's ±0.12hPa relative repeatability is "
       "about a metre, but weather moves pressure 20-30hPa, which is 200-250m of apparent "
       "altitude, so a shelf drifts several floors overnight. Magnetic and Wi-Fi "
       "fingerprints die silently when a filing cabinet moves or a router is swapped, and "
       "the failure is confident mislocation rather than graceful degradation. A DW1000 is "
       "the strongest indoor route and reads long, never short — a body between tag and "
       "anchor adds 10-30cm.",
 unlocks="Repeatable return: a robot that docks the same way every time, and survey or "
         "structural monitoring where the question is always 'has it moved since last "
         "time'.",
 market="Robotics, surveying, construction monitoring, agriculture, warehousing"),

"structure-moved": dict(
 fools="The sensor is almost never the limiting error. A precision inclinometer's "
       "0.001-degree-per-year stability is the silicon's; over a year the dominant error is "
       "the bracket relaxing, the fixings creeping, thermal expansion of the mount and, "
       "outdoors, the ground moving with soil moisture. Temperature is the other confound "
       "and normally bigger than the signal: an ADXL355 drifts about 0.15 mg per degC per "
       "axis, roughly 0.01 degrees per degC, so a 20-degree diurnal swing is a fifth of a "
       "degree of apparent tilt, and most published wall-movement plots are a temperature "
       "cycle until somebody regresses it out. Any accelerometer also measures every other "
       "acceleration, so wind on a pole or traffic through a retaining wall lands in the "
       "band you want to trend, which makes heavy averaging and a companion vibration "
       "channel part of the design. And the GNSS route buys a different trap: the "
       "advertised centimetre applies only in RTK fixed state, decimetres in float and "
       "metres standalone.",
 unlocks="Evidence that a crack, a retaining wall, a scaffold or a heritage structure is or "
         "is not moving, at a cost that makes continuous monitoring plausible rather than "
         "an annual survey.",
 market="Civil engineering, insurers, construction, mining and quarrying, heritage"),

"material-type": dict(
 fools="Cheap spectral sorting stops where the chemistry starts. The carbon-hydrogen "
       "overtones that make industrial NIR plastic sorting work live at 1100-1800 nm and "
       "silicon photodiodes are blind past about 1000 nm, so a filter-array part topping "
       "out at 860 nm classifies colour, additives and surface texture rather than polymer "
       "chemistry - a black PP part and a black PET part are identical to it, and carbon "
       "black is unsortable for the same reason industrial sorters cannot do it either. "
       "Inductive sensing genuinely discriminates metals, since steel raises a coil's "
       "inductance while aluminium and copper lower it, but the coil responds to every "
       "conductor in the field including the bench and the mounting screws, and it goes "
       "blind at roughly one coil diameter. And the reported accuracy is usually a "
       "measurement of your fixture rather than of the physics: a classifier trained on "
       "your ten samples in your jig collapses on someone else's samples in theirs, so a 98 "
       "percent figure means nothing without a held-out set collected on a different day.",
 unlocks="Sorting that is good enough for a known, closed set - your own recycling stream, "
         "your own stock room, your own scrap bin - which is where most of the value "
         "actually is.",
 market="Recycling, makerspaces, scrap metal, manufacturing QC, education"),

"moisture-content": dict(
 fools="Nearly every route measures permittivity and calls it water - water sits near 80, "
       "soil minerals near 4 - but the confounders are large and invisible. Excitation "
       "frequency decides how badly: cheap capacitive probes run at a few hundred kHz to a "
       "few MHz, where salinity and texture shift the same board 15-20 percentage points "
       "between sand and clay at identical water content. A METER TEROS 12 at 70 MHz "
       "suppresses that without abolishing it - above roughly 8 dS/m bulk EC the reading "
       "inflates - and a true TDR probe at gigahertz loses the end-of-rod reflection "
       "entirely above about 5 dS/m pore-water EC. Air gaps are invisible in the data and "
       "dominate the error budget: the field sits within a few millimetres of the needles, "
       "so a 1 mm void reads about 0.05 m3/m3 low. Topp's equation is for mineral soils, so "
       "coco, peat and rockwool are wrong by 5-15 points. Frozen material reads exactly "
       "like dry, because ice has a permittivity near 3. And an SHT41 measures air a "
       "millimetre from its cap, so a wall bone dry to touch can sit at 95 % RH microns "
       "away.",
 unlocks="Drying, curing and storage decisions made on the material rather than on elapsed "
         "time - grain, timber, plaster, silage, substrate - and mould risk caught before "
         "it is visible.",
 market="Construction and restoration, grain and timber storage, horticulture substrates, "
        "food processing"),

"food-fresh": dict(
 fools="Nothing here measures spoilage; these parts measure conditions and appearances. "
       "Temperature is the only honest route, and it is a HISTORY problem rather than a "
       "reading: spoilage integrates hours spent warm, so a spot check of a cold fridge "
       "says nothing about the afternoon the pallet spent on a loading dock, and a logger "
       "that was unpowered through the outage has no answer at all. Precision then measures "
       "the wrong thing: a TMP117 is ±0.1°C and measures its own package, reading 1-3°C "
       "high on the same copper pour as an ESP32. Gas routes are wishful, since the MQ-3 "
       "answers to acetone, isopropanol and hand sanitiser at least as strongly as ethanol, "
       "and the AS7263 stops at 860nm while the NIR bands for water, fat and protein sit "
       "past 1100nm — so it is classifying appearance, not composition.",
 unlocks="Cold-chain evidence rather than cold-chain faith: a fridge or delivery box that "
         "can prove what happened to it, and a decision about a doubtful item based on "
         "logged exposure.",
 market="Cold chain, hospitality, retail, households, food banks"),

"colour-match": dict(
 fools="Colour measurement is geometry and illumination first and chemistry never. Signal "
       "falls as one over distance squared, so a 1 mm change in standoff at 5 mm shifts raw "
       "counts by around 20 percent, and on a multi-chip spectral sensor 2 mm shifts every "
       "channel by 20 percent - without a fixed jig, nothing measured today is comparable "
       "to yesterday. The illuminant is the second trap: the TCS34725's own white LED is a "
       "blue-pumped phosphor type with a spike near 450 nm and a dip near 480 nm, so cyans "
       "and some magentas read wrong. Parts without IR-blocking glass - the TCS3200, the "
       "APDS-9960's RGB channels - read every incandescent or sunlit surface far too red, "
       "because silicon stays wide open past 700 nm. Saturation is silent here: a Clear "
       "channel pinned at 65535 still yields a plausible hue that is wrong. And the deepest "
       "limit is metamerism - overlapping 20 nm-wide filter bands cannot resolve a narrow "
       "spectral feature, so two dyes matched to the same colour never separate.",
 unlocks="Repeatable colour QC on paint, print, textiles and food without a laboratory "
         "spectrophotometer, provided you build and keep the jig.",
 market="Printing, paint and coatings, textiles, food processing, makerspaces"),

"concentration-liquid": dict(
 fools="Conductivity counts ions, not solutes: sugar and alcohol are essentially invisible "
       "while calcium in hard water reads exactly like fertiliser, and 'ppm' is "
       "conductivity multiplied by a convention factor of 0.5, 0.64 or 0.7 — so two honest "
       "TDS meters can disagree by 40%. Ionic mobility rises about 2% per degree, so a "
       "probe without the water's temperature is tracing the day. Ion-selective electrodes "
       "are more specific and far more brutal: at 59mV per decade, 1mV of drift is a 4% "
       "error and 15mV is a factor of 1.8, against 5-20mV a day of normal field drift — and "
       "each has an assassin, chloride for nitrate, potassium for ammonium, hydroxide for "
       "the LaF3 fluoride electrode unless TISAB pins the pH at 5.0-5.5. Optical routes "
       "measure your fixture: a TCS34725's signal falls as 1/d2, so 1mm of standoff at 5mm "
       "shifts counts by 20%.",
 unlocks="Dosing that responds to the solution rather than to a recipe — nutrient control, "
         "plating and cleaning-bath maintenance, and effluent monitoring with an auditable "
         "number.",
 market="Hydroponics, brewing, water treatment, plating and finishing, environmental "
        "monitoring"),

"contamination": dict(
 fools="Contaminated with what? Every route answers a narrower question, and the negative "
       "result is the dangerous one. Conductivity and TDS see only ions: near zero in sugar "
       "syrup, while hard water's calcium and magnesium read exactly like fertiliser. "
       "Turbidity boards measure transmission, not the 90-degree scattering that defines "
       "NTU under ISO 7027 and EPA 180.1, so peat water reads as turbid with almost no "
       "suspended solids, and biofilm over 2-4 weeks drives the reading up like a real "
       "trend. Every ion-selective electrode has an assassin: chloride swamps a nitrate "
       "ISE, potassium reads as ammonium on a nonactin membrane, hydroxide reads as "
       "fluoride above about pH 8, and because the response is logarithmic a 15 mV drift - "
       "inside a probe's normal 5-20 mV per day - is a factor of 1.8. An AS7263 or AS7265x "
       "stops at 860-940 nm while the C-H overtones live at 1100-1800 nm, so it classifies "
       "colour. A PID cannot see above 10.6 eV, so methane, CO, CO2 and water read zero. "
       "And a Geiger tube says something is radioactive, never what: at 7 % FWHM even the "
       "583 and 609 keV lines merge into one hump.",
 unlocks="A cheap first-pass screen that says 'this changed, send it to a lab' - and, where "
         "you own the baseline, continuous watch on a process that would otherwise be "
         "sampled monthly.",
 market="Water utilities, food and brewing, environmental monitoring, recycling, education"),

"coating-cured": dict(
 fools="Every route measures solvent leaving, not chemistry finishing — a VOC index goes "
       "quiet while a two-pack epoxy crosslinks for days. The SGP40's index is defined "
       "against its own rolling 24-hour baseline, so a workshop that always smells of "
       "solvent sits at 100 while the fresh coat barely registers, and the budget AGS02MA "
       "runs no baseline correction and no temperature or humidity compensation at all. "
       "Winsen's own ZE08-CH2O datasheet lists significant ethanol cross-sensitivity, so a "
       "solvent-rich coating reads as formaldehyde. And the humidity route carries a cruel "
       "irony: curing silicone permanently poisons polymer RH elements, so an SHT41 "
       "watching an RTV bead cure is being destroyed by the thing it is measuring.",
 unlocks="Knowing when to demould, recoat, handle or ship. The commonest cause of finish "
         "failures is working the surface too early; the second is waiting far longer than "
         "necessary.",
 market="Woodworking, composites, coatings, 3D printing, small manufacturing"),

"rf-activity": dict(
 fools="A broadband log detector integrates everything from 1 MHz to 8 GHz into one number - "
       "your own ESP32's Wi-Fi, the microwave oven and a broadcast tower all add together - "
       "so it tells you that RF exists and never what is transmitting. Its log slope and "
       "intercept both shift with frequency, and on the AD8318 the intercept moves by "
       "roughly 20 dB between 900 MHz and 5.8 GHz, which makes an uncalibrated dBm figure "
       "fiction. The antenna then dominates: moving a 50-ohm probe 10 cm, usually changes "
       "the reading more than the source does, and a probe held near a wall measures the "
       "wall. An unintegrated coil probe measures the rate of change of the field rather "
       "than the field, so its output rises with frequency and a dimmer's harmonics read "
       "far louder than the 50 Hz fundamental you thought you were measuring - and the loop "
       "formed by your own lead wires is part of the antenna. Finally there is no such "
       "quantity as EMF: H-field in A/m, E-field in V/m and RF power density in W/m2 are "
       "three different things, and every consumer meter quietly picks one.",
 unlocks="Finding what is actually radiating - a failing switching supply, an unshielded "
         "dimmer, a rogue transmitter - and mapping coverage instead of guessing at it.",
 market="EMC troubleshooting, amateur radio, IT and building services, security, education"),

"hidden-wiring": dict(
 fools="The physics beats you before the sensor does. A live cable's field falls as 1/r "
       "while a permanent magnet's falls as 1/r cubed, so a hand-held wand is mostly "
       "mapping how close you held it unless the probe rides on a spacer. Mains detection "
       "is then defeated by cancellation: live and neutral in the same twin-and-earth carry "
       "equal and opposite currents that nearly cancel a centimetre away, so a heavily "
       "loaded ring main can read lower than an unloaded lighting drop, and an unloaded "
       "cable radiates nothing. Earth's field of about 50 uT swamps most anomalies, so "
       "everything must be done in differences, and below roughly 100 uT an MLX90393's "
       "offset drift dominates. Anything ferrous within a few centimetres - your own "
       "enclosure screws included - becomes part of the sensor. An LDC1612 responds only to "
       "about its coil diameter, so a 14 mm coil is blind past 14 mm, and ferrous and "
       "non-ferrous targets shift the frequency in opposite directions. Capacitive sensing "
       "reads your own hand as readily as a stud, and a broadband RF probe integrates 1 MHz "
       "to 8 GHz into one number that says only that RF exists. None of this is a permit to "
       "drill.",
 unlocks="Finding services before cutting - and, more interestingly, mapping a building's "
         "hidden infrastructure without opening it up.",
 market="Renovation trades, facilities, surveying, home owners, archaeology of buildings"),

"magnetic-anomaly": dict(
 fools="Anomaly means a difference: treat a reading as an absolute and you are measuring "
       "your own build. Earth's field is only about 25-65 uT, and a 200 mA LED strip 3 cm "
       "away, a steel screw or the ESP32's own regulator swamp it - hard-iron offsets from "
       "fixed ferrous parts are calibratable, but soft-iron distortion changes with "
       "orientation and needs an ellipsoid fit. An uncompensated magnetometer also reports "
       "a heading wrong by roughly the tilt angle, so walking with one in your hand swings "
       "the reading 20 degrees. Sensitivity carries about 0.1 %/degC, so an outdoor survey "
       "wanders through the day, and a QMC5883L with no set/reset coil walks its offset "
       "over hours. An MMC5603 resolves 0.0625 mG, far finer than the world is stable - a "
       "lift two floors away moves it by many times its noise floor, which makes "
       "fingerprinting work and an absolute-field alarm useless - and it folds back past "
       "+/-30 gauss, which a fridge magnet at 1 cm reaches. The inductive route is blind "
       "past its own coil diameter, and steel and aluminium shift its frequency in opposite "
       "directions.",
 unlocks="Surveying what is buried or built in without digging - reinforcement, pipes, "
         "ordnance, archaeological iron - and detecting when a large ferrous object has "
         "moved.",
 market="Surveying, archaeology, utilities, security screening, science education"),

"cosmic-flux": dict(
 fools="A single detector cannot tell a muon from a terrestrial gamma ray, from a beta "
       "emitted by the potassium-40 in the concrete around you, or from an electrical "
       "glitch - everything is a pulse, which is why the honest build is two detectors "
       "required to fire within tens of nanoseconds of each other. Almost everything that "
       "looks like a fault here is real physics: the rate falls roughly 0.1-0.2 percent per "
       "hPa of barometric pressure, rises about thirtyfold at 11 km cruising altitude, and "
       "follows roughly the cosine squared of zenith angle. SiPM dark count rate roughly "
       "doubles every 8-10 degC, so a threshold set on a cool bench floods with counts in a "
       "warm room unless the bias is temperature-compensated - and any light leak swamps "
       "the detector instantly and will destroy a SiPM that is biased at the time. A Geiger "
       "tube is the wrong instrument entirely: its counts are dominated by terrestrial "
       "background, which itself rises on a granite worktop and after rain.",
 unlocks="A genuinely portable particle-physics experiment: the pressure and altitude "
         "dependence, the cosine-squared angular distribution, and air-shower coincidence "
         "between two units.",
 market="Physics education, museums, science communication, high-altitude ballooning"),

"ultrasonic-activity": dict(
 fools="Both routes are uncalibrated by construction. The SPU0410LR5H is specified flat only "
       "to 10kHz and the manufacturer does not characterise it above that at all, so any "
       "amplitude you report in the ultrasonic band is relative only, two units disagree, "
       "and its response has peaks and nulls you cannot correct without a calibrated source "
       "you almost certainly do not own. The medium fights you too: absorption is roughly "
       "1dB/m at 40kHz and several dB/m at 80kHz and changes sharply with humidity, so the "
       "same bat at the same distance reads differently on a damp night. Almost every "
       "machine is an ultrasonic source — switch-mode supplies, LED drivers, a running tap. "
       "And the classic failure is undersampling: you need 192kSPS to reach 96kHz of "
       "bandwidth, and sampling at 44.1kHz produces beautifully convincing 'bat calls' at "
       "8kHz that are aliases, not detections.",
 unlocks="A whole band of the world becoming legible: bat surveys, electrical arcing and "
         "corona discharge, steam-trap and air-leak work, and rodent activity — none of it "
         "visible to any other sensor here.",
 market="Ecology and conservation, facilities and maintenance, utilities, pest control, "
        "science education"),

"atmospheric-charge": dict(
 fools="The one route here is honest about being an experiment. A passive high-impedance "
       "electrode is a leakage-current instrument pretending to be a field meter: surface "
       "leakage across the PCB - flux residue, fingerprints, condensation - dominates, and "
       "morning dew shifts the reading further than a thunderstorm does. That leakage sets "
       "an RC time constant, so the electrode high-passes the atmosphere: the steady "
       "fair-weather field of roughly +100 to +150 V/m is invisible, and no field cannot be "
       "told from a large steady field. What is left is the rate of change, and "
       "triboelectric charge counterfeits it - rain striking the electrode, blown dust, a "
       "nylon jacket three metres away. Corona discharge from any sharp point turns the "
       "sensor into a charge source exactly when the field is most interesting; a real "
       "field mill chops a DC field into AC with a rotating shutter. And an exposed "
       "electrode on a mast is a lightning attachment point: its failure mode is "
       "destruction by the event it exists to observe.",
 unlocks="A local, seconds-ahead warning of charge separation overhead, and a way to watch "
         "the electrical weather that no consumer instrument reports.",
 market="Science education, amateur meteorology, museums, outdoor-safety research"),
}
