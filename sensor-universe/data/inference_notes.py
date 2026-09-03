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
}
