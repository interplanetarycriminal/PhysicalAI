"""Fusion layer — outcomes no single sensor claims, as first-class data.

Everything before this file treats sensors as individuals. The solver's own
findings admit the consequence: every coverage number is a LOWER BOUND, because
the moment you combine two sensors (or one sensor with time) you get outcomes
neither claims alone. v50 documents that combining as prose — 48 Derived
Quantities, 30 Combination Grammar operators — but prose cannot be computed.

This file is the prose made computable. Each FUSION_EDGE is a hyperedge:
  requires  — capabilities, as (key, multiplicity) atoms. A capability key lives
              in vocab.PHENOMENON, vocab.INFERENCE, or EMERGENT (chaining).
              A kit covers an atom when at least `multiplicity` DISTINCT
              catalog parts in it cover that key. ×N therefore reads as
              "N independent measurement points"; N copies of one part also
              satisfies it in practice, so the computed closure stays a
              conservative lower bound.
  provides  — an EMERGENT key (an outcome new to the atlas) or an existing
              INFERENCE key (a new ROUTE to an outcome, reachable without any
              of the sensors that claim it directly).
  math      — the actual formula or logic. Real physics only; every constant
              is checkable.
  confound  — what kills it. An edge without a stated confound is marketing.

The edges were authored from the atlas's own material: the Derived Quantities
sheet, the Derived Instruments (dual-probe heat pulse, Helmholtz fill level,
CO2 tape measure...), the Combination Grammar's worked examples, and the
Anti-Catalog (the radon edge turns one of its walls into an instrument).
"""

# EMERGENT: key -> (question, domain). Domains reuse the 13 in vocab.INFERENCE.
# Keys are disjoint from INFERENCE and PHENOMENON — the validator enforces it.
EMERGENT = {
    "condensation-risk": ("Will water condense on that surface soon?", "Air & environment"),
    "air-changes-hour": ("How many air changes per hour does this room really get?", "Air & environment"),
    "air-density": ("What is the actual air density right now?", "Weather & outdoors"),
    "grid-stress": ("Is the electricity grid under stress at this moment?", "Energy"),
    "wet-bulb-heat-stress": ("How dangerous is this heat to a working human?", "Body & health"),
    "inrush-health": ("Is the compressor/motor getting harder to start?", "Machine health"),
    "building-heat-loss": ("How many watts does this building leak per degree?", "Energy"),
    "soil-water-volumetric": ("How much water is actually IN this soil, in percent?", "Plants & soil"),
    "recording-authenticity": ("Was this recording really made when it claims?", "Invisible worlds"),
    "sound-direction": ("Which direction did that sound come from?", "Security & safety"),
    "presence-verified": ("Is someone REALLY there — two physics agreeing?", "Human presence"),
    "feels-like-temperature": ("What does it feel like outside, honestly?", "Weather & outdoors"),
    "evapotranspiration": ("How much water did the garden lose to the sky today?", "Plants & soil"),
    "path-averaged-temperature": ("What is the average temperature along that whole path?", "Air & environment"),
    "which-door-opened": ("Which door, on which floor, just opened?", "Human presence"),
    "radon-risk-rising": ("Is radon LIKELY rising, before the slow meter can say?", "Air & environment"),
    "space-utilisation-map": ("Which desks and rooms actually get used?", "Human presence"),
    "thermal-map": ("Where are the cold corners, draughts and damp walls?", "Air & environment"),
    "personal-exposure-dose": ("What did YOU actually breathe today, block by block?", "Body & health"),
    "window-open-state": ("Is a window open right now?", "Air & environment"),
    "black-ice-risk": ("Is the road surface about to ice over?", "Weather & outdoors"),
    "cost-per-use": ("What does one run of this machine actually cost?", "Energy"),
    "leak-location": ("WHERE along the pipe is the leak?", "Water"),
    "thermal-time-constant": ("How long does this building hold its heat?", "Energy"),
    "room-volume-estimate": ("How big is this room, measured by breathing in it?", "Navigation & space"),
    "energy-waste-unoccupied": ("How much energy do empty rooms burn here?", "Energy"),
}

# ---------------------------------------------------------------------------
# The edges. Grouped by the pattern that powers them.
# Field order: key, name, pattern, requires, provides, math, why, confound, example.

FUSION_EDGES = [

    # ------------------------------------------------------------ differential
    dict(key="condensation-watch", name="Condensation forecaster",
         pattern="differential",
         requires=[("dew-point", 1), ("temperature-remote", 1)],
         provides="condensation-risk",
         math="Risk when T_surface − T_dew < 1.5°C (T_dew via Magnus: γ = ln(RH/100) + 17.62·T/(243.12+T))",
         why="Condensation is not about air humidity — it is about the COLDEST surface versus the "
             "air's dew point. One sensor reads the air, the other reads the wall; the difference "
             "is the entire answer.",
         confound="Emissivity: a shiny surface lies to the IR thermometer by 20× (Anti-Catalog II). "
                  "Put a strip of matt tape at the cold spot and aim at that.",
         example="SHT41 for dew point + MLX90614 aimed at the bathroom's coldest corner → alert "
                 "BEFORE the wall sweats, which is the mould sentinel working a week early."),

    dict(key="mould-forecast", name="Mould sentinel (surface-honest)",
         pattern="temporal",
         requires=[("condensation-risk", 1)],
         provides="mould-risk",
         math="Sustained surface-RH > 80% ≈ T_surface within 3°C of T_dew for >6 h/day, integrated over days",
         why="Mould does not grow on humid AIR, it grows on surfaces that stay near dew point for "
             "hours. Integrating the condensation-risk signal over time is the medically honest "
             "route — a chained edge: one derived instrument feeding another.",
         confound="Hidden surfaces: the coldest spot is usually behind the wardrobe where no sensor "
                  "points. Survey with the IR thermometer first, THEN mount.",
         example="The condensation watcher plus a daily accumulator = the £15 answer to a £2,000 "
                 "remediation bill."),

    dict(key="loop-heat-meter", name="Hydronic heat meter",
         pattern="differential",
         requires=[("flow-liquid", 1), ("temperature-contact", 2)],
         provides="thermal-energy-moved",
         math="P[W] = (flow[L/min]/60) × 4186 × ΔT[K]; energy = ∫P dt",
         why="Watts moving through any water loop are just flow times temperature drop. Two "
             "identical probes measure the drop, so their shared calibration error cancels — the "
             "differential pair IS the instrument.",
         confound="Probe placement: strap-on probes read pipe wall, not water; insulate over them "
                  "or the ΔT reads low. Air in the flow meter reads high.",
         example="YF-S201 + 2× DS18B20 strapped to a heat pump's pipes = the 'is my heat pump "
                 "lying?' meter, versus the $800 commercial heat meter."),

    dict(key="psychrometric-wetbulb", name="Wet-bulb heat-stress meter",
         pattern="differential",
         requires=[("temperature-contact", 2)],
         provides="wet-bulb-heat-stress",
         math="T_wet from psychrometric pair (one probe in a wet cotton wick, ~3 m/s airflow); "
              "T_wet ≥ 31°C = dangerous, ≥ 35°C = lethal to sustained human work",
         why="Wet-bulb temperature is the number heat physiology actually runs on — it is what "
             "sweating can still achieve. Two identical probes, one wet, one dry: the pair "
             "measures what no single hygrometer states plainly.",
         confound="The wick must stay wet and ventilated; a dry wick silently converges to the dry "
                  "bulb and the danger signal disappears exactly when it matters.",
         example="2× DS18B20, a shoelace wick, a small fan: a £6 outdoor-work safety instrument "
                 "for the climate we are actually getting."),

    dict(key="soil-heat-pulse", name="Dual-probe heat-pulse soil water",
         pattern="differential",
         requires=[("temperature-contact", 2)],
         provides="soil-water-volumetric",
         math="θ = (C − C_dry)/4.18 where C = q/(ρ_soil·ΔT_max·r²·e); heat pulse from a resistor wire",
         why="Water dominates soil's volumetric heat capacity, so the temperature rise a known "
             "heat pulse produces 6 mm away is a direct water-content measurement — research-grade "
             "physics from two thermistor beads.",
         confound="Probe spacing must be known to ±0.5 mm (r² term); root contact and stones "
                  "distort the thermal field. Calibrate the dry point once per soil.",
         example="Two glass-bead NTCs in hypodermic tubes + a heater wire: the £8 version of a "
                 "$400 TEROS — Derived Instruments row 2, now a computable capability."),

    dict(key="cloud-cover-ir", name="Sky thermometer cloud detector",
         pattern="differential",
         requires=[("temperature-remote", 1), ("temperature-contact", 1)],
         provides="sky-clear",
         math="Clear sky reads 25–45°C BELOW air temp in thermal IR; overcast reads within ~5°C",
         why="A clear sky is a window to space at 3 K, so an IR thermometer aimed up reads "
             "dramatically cold; clouds are water at roughly air temperature. The DIFFERENCE "
             "between sky and air temperature is a cloud-cover instrument.",
         confound="Rain on the sensor window reads as total overcast; high thin cirrus reads "
                  "half-way and fools the threshold. Angle it 10° off zenith with a rain shield.",
         example="MLX90614 face-up + any air thermometer = astronomy go/no-go, radiative frost "
                 "early warning, and a solar-forecast input, for £10."),

    dict(key="black-ice-watch", name="Road ice predictor",
         pattern="differential",
         requires=[("temperature-remote", 1), ("dew-point", 1)],
         provides="black-ice-risk",
         math="Alarm when T_road ≤ 1°C AND T_road ≤ T_dew + 0.5°C (frost deposition condition)",
         why="Black ice forms when the ROAD — not the air — drops below both freezing and the "
             "frost point. Road surface radiates to the sky and runs colder than air on clear "
             "nights; only the pair of measurements sees it coming.",
         confound="The IR spot must land on representative tarmac, not painted lines (different "
                  "emissivity) or the verge. Wind mixes the boundary layer and lifts T_road.",
         example="MLX90614 on a gatepost aimed at the drive + SHT41: know the drive is icing "
                 "before the council's gritter does — the same physics as a £30k RWIS station."),

    dict(key="filter-dp", name="Filter-health differential barometer",
         pattern="differential",
         requires=[("pressure-absolute", 2)],
         provides="filter-clogged",
         math="ΔP = P_upstream − P_downstream; alarm at 2–3× the clean-filter baseline",
         why="A clogging filter is a rising pressure drop. Two absolute barometers, one either "
             "side, subtract to a differential gauge — and because they are identical parts, "
             "their weather-driven drift is common-mode and cancels.",
         confound="A clean HVAC filter drops only 30–100 Pa, near the ±3 Pa relative floor of a "
                  "good barometer pair — zero the pair together first and average hard. Cheap "
                  "±100 Pa modules cannot do this job.",
         example="2× BMP390 taped either side of the furnace filter: change it when the numbers "
                 "say so, not when the calendar guesses."),

    dict(key="compost-core", name="Compost activity meter",
         pattern="differential",
         requires=[("temperature-contact", 2)],
         provides="compost-active",
         math="ΔT = T_core − T_ambient; active thermophilic compost holds ΔT ≈ 20–40°C",
         why="Microbial activity IS heat production. The core-minus-ambient difference removes "
             "weather entirely, leaving pure biology — a single probe confuses a sunny week with "
             "a working pile.",
         confound="Probe depth: the thermophilic core is the middle 30 cm; a shallow probe reads "
                  "the cool skin and declares a working pile dead.",
         example="Two DS18B20s — one on a stake in the core, one in the shade: turn the pile when "
                 "ΔT sags, harvest when it converges. Free process control."),

    dict(key="bearing-thermal", name="Bearing temperature-rise monitor",
         pattern="differential",
         requires=[("temperature-contact", 2)],
         provides="bearing-failing",
         math="ΔT = T_bearing − T_ambient; trend of ΔT at constant load is the health signal",
         why="A failing bearing turns friction into heat before it turns it into noise you can "
             "hear. Referencing against ambient kills the day/night and seasonal swing that makes "
             "a single probe useless for trending.",
         confound="Load changes move ΔT legitimately — trend at the SAME duty point, or normalise "
                  "by motor current. Direct sun on the housing wrecks the reading.",
         example="Two NTC beads, one epoxied to the bearing housing, one in free air: the £1 "
                 "vibration-analysis cross-check, and it catches lubrication failure earlier."),

    # ---------------------------------------------------------- compensation
    dict(key="air-density-live", name="Live air-density computer",
         pattern="compensation",
         requires=[("pressure-absolute", 1), ("temperature-contact", 1), ("humidity-relative", 1)],
         provides="air-density",
         math="ρ = (P_dry·M_d + P_vap·M_v)/(R·T); P_vap from RH × saturation pressure (Magnus)",
         why="Lift, combustion, anemometry and evaporation all secretly depend on air density, "
             "and everyone substitutes the sea-level constant. Three cheap measurements replace "
             "the guess with the number.",
         confound="Sensor self-heating biases T by up to 1°C on combo boards (BME280's known "
                  "flaw) — read fast, sleep long, or mount the thermometer separately.",
         example="One BME280 = drone payload margin on a hot day, carburettor tuning truth, and "
                 "the correction every anemometer in this catalog silently needs."),

    dict(key="feels-like", name="Feels-like temperature station",
         pattern="compensation",
         requires=[("temperature-contact", 1), ("humidity-relative", 1), ("wind-speed", 1)],
         provides="feels-like-temperature",
         math="T<10°C: wind chill (Environment Canada 2001 formula); T>20°C: heat index "
              "(Rothfusz regression); between: dry bulb",
         why="Human heat loss depends on wind (convection) and humidity (evaporation limit), so "
             "the honest 'how does it feel' number is a three-sensor fusion — each sensor "
             "compensates a failure mode of the bare thermometer.",
         confound="The anemometer must see YOUR microclimate: a sheltered patio and the rooftop "
                  "differ by the whole wind-chill term.",
         example="AHT20 + cup anemometer = the difference between 'it says 2°C' and 'it will feel "
                 "like −6 on the bike'."),

    dict(key="et0-station", name="Evapotranspiration (irrigation truth)",
         pattern="compensation",
         requires=[("temperature-contact", 1), ("humidity-relative", 1),
                   ("wind-speed", 1), ("irradiance", 1)],
         provides="evapotranspiration",
         math="FAO-56 Penman-Monteith ET₀ (or Hargreaves ET₀ = 0.0023·Ra·√ΔT·(T+17.8) when only "
              "temperature is available)",
         why="How much to water is not how dry the soil FEELS — it is how much water the "
             "atmosphere pulled out. Four measurements close the energy balance agriculture "
             "actually runs on; this is the equation behind every commercial irrigation "
             "controller worth owning.",
         confound="The radiation term dominates in summer: a dusty or shaded pyranometer silently "
                  "halves ET₀ and you under-water in exactly the week it matters.",
         example="The weather-station cluster this catalog already prices at ~$35 becomes a "
                 "closed-loop irrigation brain instead of a dashboard."),

    dict(key="muon-baro", name="Pressure-corrected cosmic-ray telescope",
         pattern="compensation",
         requires=[("ionising-radiation", 1), ("pressure-absolute", 1)],
         provides="cosmic-flux",
         math="Corrected rate = raw rate × e^(β·(P−P₀)), β ≈ 0.2%/hPa for muons",
         why="Atmospheric pressure is absorber mass overhead: high pressure literally shields you "
             "from muons. Uncorrected, a cosmic-ray monitor is mostly a slow barometer — the "
             "compensation term is the difference between logging weather and logging space.",
         confound="β depends on detector geometry and shielding; fit your own from a fortnight of "
                  "data rather than trusting the textbook value.",
         example="CosmicWatch + BMP390: see Forbush decreases (solar storms punching the cosmic "
                 "flux down) from a desk, which is about as close to space weather as £160 gets."),

    dict(key="ph-temp-honest", name="Temperature-honest pH",
         pattern="compensation",
         requires=[("ph", 1), ("temperature-contact", 1)],
         provides="water-ph",
         math="Nernst slope = −59.16 mV/pH × (T/298.15); correct slope, then report at 25°C",
         why="A pH electrode's millivolts-per-pH changes 0.2%/°C by physics (Nernst), before any "
             "ageing. Without the temperature channel a 15°C swing masquerades as 0.15 pH — the "
             "entire hydroponics adjustment band.",
         confound="This corrects the ELECTRODE's slope, not the solution's real chemistry shift "
                  "with temperature; report the measurement temperature alongside.",
         example="Any pH kit + DS18B20 in the same reservoir: the difference between chasing "
                 "phantom pH drift and dosing on truth."),

    dict(key="soil-moisture-tc", name="Temperature-corrected soil moisture",
         pattern="compensation",
         requires=[("dielectric-constant", 1), ("temperature-contact", 1)],
         provides="plant-thirsty",
         math="Correct raw counts by the probe's measured temperature coefficient (typ. 0.1–0.3%/°C), "
              "learned from a 24 h constant-moisture log",
         why="Capacitive probes drift with temperature through both electronics and soil "
             "dielectric physics. A day/night cycle reads as phantom watering; the co-located "
             "temperature channel subtracts it.",
         confound="Fast rain during the calibration day corrupts the learned coefficient — pick a "
                  "dry 24 h, or learn it under a cover.",
         example="Capacitive v2 probe + DS18B20 at root depth: irrigation triggered by plants, "
                 "not by sunrise."),

    dict(key="snow-sonic", name="Temperature-honest snow depth",
         pattern="compensation",
         requires=[("distance-point", 1), ("temperature-contact", 1)],
         provides="snow-depth",
         math="depth = mount_height − range × c(T)/c₀, with c(T) = 331.3 + 0.606·T m/s",
         why="Sound speed moves 0.18%/°C, and snow season IS temperature swing: a −20°C morning "
             "reads 7 cm short on a 2 m mount with no compensation. The air thermometer turns a "
             "toy into a gauge.",
         confound="Fresh powder absorbs 40 kHz and returns nothing (the ultrasonic absorption "
                  "wall); the US-100's onboard compensation helps but measure air temp on the "
                  "mount arm, in shade, for the real correction.",
         example="US-100 on a fence post + shaded NTC: a SNOTEL-style depth record for £6."),

    dict(key="pv-performance-ratio", name="Solar performance-ratio meter",
         pattern="compensation",
         requires=[("irradiance", 1), ("current-dc", 1)],
         provides="solar-performance",
         math="PR = P_actual / (G/1000 × P_rated); healthy arrays hold PR 0.75–0.85",
         why="Low solar output has two innocent explanations — clouds and season — and one "
             "expensive one: degradation or soiling. Only dividing by measured irradiance "
             "separates them; PR is the number the O&M industry runs on.",
         confound="The reference cell must share the panel's plane and its dirt: a clean sensor "
                  "next to dirty panels reports the panels as broken (or a dirty sensor hides "
                  "that they are).",
         example="Pyranometer + INA228 on the string: 'the array is fine, it is November' versus "
                 "'string 2 lost 12% since summer — check for soiling.'"),

    # ---------------------------------------------------------- cross-validation
    dict(key="fire-coincidence", name="Fire coincidence detector",
         pattern="cross-validation",
         requires=[("smoke-present", 1), ("co-present", 1)],
         provides="fire-present",
         math="Alarm = smoke AND (CO rising ≥ 5 ppm over baseline within 10 min); either alone = advisory",
         why="Combustion makes particles AND carbon monoxide; dust makes only particles; a "
             "blocked flue makes only CO. Requiring both physics to agree is how false alarms "
             "die — and a kit holding a smoke sensor plus a CO sensor gains a fire detector "
             "neither is alone. NOT a life-safety device — supplement, never replace, a "
             "certified alarm.",
         confound="Smouldering PVC and some foams are CO-rich but smoke-poor early on: keep the "
                  "single-channel advisory alerts, gate only the loud alarm.",
         example="MQ-2 + MQ-7 on one node: the Combination Grammar's coincidence gate, computed."),

    dict(key="presence-two-physics", name="Two-physics presence verifier",
         pattern="cross-validation",
         requires=[("someone-present", 2)],
         provides="presence-verified",
         math="Verified = both channels TRUE within a 5 s window; disagreement = log + keep watching",
         why="PIR false-triggers on HVAC heat plumes; radar false-triggers on fans and curtains; "
             "they almost never false-trigger TOGETHER, because the failure causes are "
             "uncorrelated physics. The field result in this atlas: 39 false triggers in 40 "
             "events alone, zero when cross-validated.",
         confound="Two sensors of the SAME physics (two PIRs) share failure causes and verify "
                  "nothing — the ×2 must span different mechanisms to earn the name.",
         example="HC-SR501 + LD2410 gating a heating zone: comfort automation that never fires "
                 "for an empty room."),

    dict(key="apnea-two-channel", name="Two-channel breathing sentinel",
         pattern="cross-validation",
         requires=[("respiration", 1), ("sound-pressure", 1)],
         provides="breathing-stopped",
         math="Escalate when radar respiration amplitude < threshold AND breath-band audio "
              "(0.1–0.5 Hz envelope) silent for > 20 s",
         why="A radar losing breathing might mean apnea — or a rolled-over sleeper out of beam. "
             "Breath sound is an independent physics witness; requiring both to vanish before "
             "escalating is the difference between a monitor and a 3 a.m. panic machine. NOT a "
             "medical device — an awareness aid.",
         confound="A partner's breathing bleeds into both channels; per-bed placement and the "
                  "radar's range gate must isolate one sleeper.",
         example="MR60BHA2 + INMP441 at the cot: the two-witness rule applied where false alarms "
                 "hurt most."),

    dict(key="enf-timestamp", name="ENF recording authenticator",
         pattern="cross-validation",
         requires=[("sound-pressure", 1), ("voltage", 1)],
         provides="recording-authenticity",
         math="Extract 50 Hz hum drift from audio; correlate against your logged grid-frequency "
              "history; genuine timestamps correlate r > 0.9 over minutes",
         why="Mains frequency wanders identically across an entire grid, and every indoor "
             "recording embeds that wander as hum. Log the grid yourself and you hold a "
             "timestamp oracle — forensics labs run exactly this; nothing stops a bench copy.",
         confound="Battery-powered outdoor recordings carry no hum; heavy audio compression "
                  "notches 50 Hz out. Absence of match ≠ forgery — it is absence of evidence.",
         example="ZMPT101B logging Δf 24/7 + any mic: verify when a voice note was REALLY "
                 "recorded. The Invisible Worlds domain earning its name."),

    # ---------------------------------------------------------- context-gating
    dict(key="leak-by-context", name="Occupancy-gated leak detector",
         pattern="context-gating",
         requires=[("flow-liquid", 1), ("someone-present", 1)],
         provides="water-leak",
         math="Alarm when flow > 0 sustained > 10 min AND nobody-present > 30 min",
         why="Water flowing is normal; water flowing in an EMPTY house is a burst pipe. The "
             "presence channel converts a flow logger into a leak alarm with near-zero false "
             "positives — most false alarms are true readings in the wrong context.",
         confound="Washing machines and irrigation run legitimately when out: whitelist their "
                  "schedules or their flow signatures first.",
         example="YF-S201 at the stopcock + any presence sensor: the insurance-claim-preventer, "
                 "two parts, £7."),

    dict(key="stove-watch", name="Stove-left-on sentinel",
         pattern="context-gating",
         requires=[("temperature-remote", 1), ("someone-present", 1)],
         provides="stove-left-on",
         math="Escalate when T_stove > 120°C AND kitchen empty > 15 min (advise), > 30 min (alarm)",
         why="A hot stove is cooking; a hot stove in an empty kitchen for half an hour is the "
             "leading cause of house fires. The gate is the entire product — elder-care systems "
             "charging £40/month are this rule.",
         confound="An IR thermometer sees one spot: aim at the hob centre, or use a thermal "
                  "array for whole-hob coverage. Reflective pans under-read (emissivity again).",
         example="MLX90614 over the hob + PIR: peace of mind for anyone whose parent forgets "
                 "the gas."),

    dict(key="window-detect", name="Window-state inferencer",
         pattern="context-gating",
         requires=[("temperature-contact", 1), ("co2-concentration", 1)],
         provides="window-open-state",
         math="Open = CO2 decay rate jumps > 3× baseline ACH while indoor–outdoor ΔT drives a "
              "simultaneous temperature slew",
         why="An open window is invisible to a thermostat but blindingly obvious in the CO2 decay "
             "curve — ventilation physics changes instantly. No contact sensor on the window, no "
             "install visit: the building's own air betrays the state.",
         confound="A door to a well-ventilated hallway mimics it; mechanical ventilation kicking "
                  "in mimics it too. Fingerprint each room's baseline first.",
         example="SCD41 + any thermometer: 'heating on + window open' detection for every room, "
                 "zero window hardware — the energy-retrofit killer feature."),

    dict(key="badge-attribution", name="Badge-in attribution gate",
         pattern="context-gating",
         requires=[("identity-token", 1), ("someone-present", 1)],
         provides="who-is-it",
         math="Attribute presence to token holder when RFID event and presence onset agree "
              "within 30 s; decay attribution when presence lapses",
         why="A badge reader knows WHO but not whether they stayed; a presence sensor knows "
             "SOMEONE is there but not who. The temporal join is identification without a "
             "camera — the privacy-preserving route to 'who is in the workshop'.",
         confound="Tailgating: two people, one badge. The gate attributes honestly only when "
                  "presence count ≈ badge count — pair with a people counter where it matters.",
         example="RC522 on the door + LD2410 inside: tool-room accountability with no lens and "
                 "no face database."),

    dict(key="radon-fast-proxy", name="Radon early-warning proxy",
         pattern="context-gating",
         requires=[("pressure-absolute", 1), ("air-changes-hour", 1)],
         provides="radon-risk-rising",
         math="Risk rising when P falling > 3 hPa/6 h (soil-gas pressure gradient reverses) AND "
              "measured ACH < 0.4",
         why="Radon entry is driven by the pressure difference between soil gas and the house, "
             "and its accumulation by ventilation. Both drivers are measurable in MINUTES — "
             "hours before a counting-statistics radon meter can confirm (√N wall, "
             "Anti-Catalog). The proxy tells you when to ventilate; the RD200 tells you if it "
             "worked. A chained edge: it consumes the ACH instrument.",
         confound="It predicts the DRIVERS, not the gas: a sealed slab breaks the correlation. "
                  "Calibrate the proxy against a real radon meter for one month per building.",
         example="BMP390 + the CO2-decay ACH meter: open the basement vent tonight, not next "
                 "week when the meter finally averages up."),

    dict(key="unoccupied-burn", name="Empty-room energy auditor",
         pattern="context-gating",
         requires=[("power-now", 1), ("someone-present", 1)],
         provides="energy-waste-unoccupied",
         math="Waste = ∫ P dt while unoccupied, per room per week; rank rooms by wasted kWh",
         why="The cheapest kilowatt-hour is the one an empty room did not burn. Power alone is a "
             "bill; presence alone is a log; their intersection is a ranked to-do list with "
             "payback periods — the number every retrofit business case is built on.",
         confound="Fridges and servers SHOULD run unoccupied: subtract each room's always-on "
                  "baseline first or the kitchen wins every audit unfairly.",
         example="BL0940 per circuit + PIR per room: 'the heater in the spare room burned 31 kWh "
                 "for nobody last month' — arguments end."),

    # ------------------------------------------------------------- temporal
    dict(key="ach-co2-decay", name="CO2-decay ventilation meter",
         pattern="temporal",
         requires=[("co2-concentration", 1)],
         provides="air-changes-hour",
         math="ACH = ln((C₁−C_out)/(C₂−C_out)) / Δt[h], C_out ≈ 420 ppm, after the room empties",
         why="When people leave, CO2 decays exponentially at exactly the air-change rate — the "
             "building tests itself every evening for free. ACH is the number building science "
             "runs on, normally bought with a £2,000 blower-door test.",
         confound="Anyone re-entering mid-decay corrupts the fit (gate on presence); wind-driven "
                  "infiltration makes ACH weather-dependent, so log the fits against wind and "
                  "you get the infiltration curve as a bonus.",
         example="One SCD41 and an empty meeting room: rate every room in the house in a "
                 "weekend — Derived Quantities row 47, computed."),

    dict(key="co2-room-volume", name="CO2 tape-measure",
         pattern="temporal",
         requires=[("co2-concentration", 1)],
         provides="room-volume-estimate",
         math="V = N·q / (d[CO2]/dt) with q ≈ 18 L/h CO2 per seated adult, sealed room, "
              "short window",
         why="A known source rate and a measured concentration slope give the mixing volume "
             "directly — one seated adult IS the calibrated source. Measuring a room's size by "
             "breathing in it is the kind of inversion this atlas exists for.",
         confound="Leaky rooms read big (the slope flattens); stratification before mixing reads "
                  "small. ±20% is the honest expectation — it is a tape-measure, not a laser.",
         example="SCD41 + one person + a stopwatch: Derived Instruments' CO2 tape-measure as a "
                 "party trick with a real use — sizing rooms for ventilation math."),

    dict(key="grid-frequency-watch", name="Grid-stress seismograph",
         pattern="temporal",
         requires=[("voltage", 1)],
         provides="grid-stress",
         math="f from zero-crossing timestamps; Δf from 50.000 Hz ∝ generation−load imbalance; "
              "df/dt during events = inertia signal",
         why="Grid frequency is the same number across an entire synchronous area, and its "
             "wander is the real-time balance of national generation versus load. One socket "
             "makes you a grid observer — every power station outage twitches your trace.",
         confound="Cheap zero-crossing detectors jitter with waveform distortion; average over "
                  "seconds. The ESP32's crystal drifts with temperature — discipline it against "
                  "NTP or GPS PPS for absolute honesty.",
         example="ZMPT101B + timer capture: watch a 1 GW plant trip from your kitchen, and "
                 "timestamp it — the sensor is the entire national grid."),

    dict(key="inrush-signature", name="Motor-start health tracker",
         pattern="temporal",
         requires=[("current-ac", 1)],
         provides="inrush-health",
         math="Trend inrush peak, spin-up time, and start count per day; rising start-time at "
              "constant voltage = mechanical or capacitor degradation",
         why="A compressor tells you it is dying at every start — the inrush transient stretches "
             "and grows for months before the hard failure. One current sensor plus memory turns "
             "the scariest appliance failure (fridge, heat pump, well pump) into a scheduled "
             "repair.",
         confound="Supply-voltage sag stretches starts too: log voltage at the same instant or a "
                  "brown-out week reads as imminent death.",
         example="SCT-013 on the compressor feed: 'the start capacitor is going — swap it this "
                 "month' for £4, versus the £300 emergency call-out."),

    dict(key="house-thermal-constant", name="Building thermal time-constant",
         pattern="temporal",
         requires=[("temperature-contact", 1)],
         provides="thermal-time-constant",
         math="τ from exponential fit of indoor T decay after heating stops (calm night); "
              "T(t) = T_out + (T₀−T_out)·e^(−t/τ)",
         why="τ — hours to lose 63% of the indoor–outdoor difference — is the building's honest "
             "thermal quality in ONE number, and every heating-off night measures it for free. "
             "Insulation upgrades change τ; receipts don't.",
         confound="Solar gain after sunrise and wind both bend the curve: fit only calm, dark "
                  "hours, and log wind to know which nights to trust.",
         example="Any indoor thermometer, logged: τ before and after loft insulation IS the "
                 "before/after — physics as a receipts-checker."),

    dict(key="nilm-signature", name="Appliance fingerprint disaggregator",
         pattern="temporal",
         requires=[("current-ac", 1)],
         provides="which-appliance",
         math="Event detection on ΔP edges; classify by (ΔP, ΔQ, inrush shape, duration) "
              "signature clusters",
         why="Every appliance switches with a signature — the kettle's clean 3 kW step, the "
             "fridge's inrush spike, the washer's drum rhythm. One meter plus time separates "
             "them; that is NILM, and it is the canonical proof that time is the cheapest "
             "sensor multiplier.",
         confound="Two similar-wattage resistive loads are indistinguishable from one point — "
                  "the toaster/kettle confusion is fundamental, not a firmware bug.",
         example="BL0940 at the consumer unit: an itemised electricity bill from one sensor, "
                 "no per-plug hardware."),

    dict(key="liquid-id-effusivity", name="Thermal-effusivity liquid identifier",
         pattern="active-probe",
         requires=[("temperature-contact", 1)],
         provides="material-type",
         math="Pulse a co-located resistor; ΔT(t) of the sensor tracks 1/e = 1/√(kρc); water "
              "e≈1580, oil ≈500, air ≈5.5 W·s^½/m²K",
         why="How fast a heated probe cools is a direct read of what surrounds it — water, oil, "
             "syrup and air separate by 3× steps in effusivity. The sensor supplies its own "
             "stimulus, so nothing else is needed: one bead, one resistor, one GPIO.",
         confound="Convection in thin liquids adds a flow term to the pure conduction model — "
                  "keep the pulse short (<2 s) and the energy small.",
         example="NTC + resistor in epoxy: is the tank water or diesel, is the fryer oil "
                 "degraded (e shifts with polymerisation) — Derived Instruments row 3, "
                 "computed."),

    dict(key="sonic-thermometer", name="Path-averaged sonic thermometer",
         pattern="active-probe",
         requires=[("ultrasound", 1)],
         provides="path-averaged-temperature",
         math="T = ((d/t_flight)² /400 approx from c² = 403·T[K]; practically T[°C] = "
              "(d/t − 331.3)/0.606 at fixed d",
         why="Fix the distance and a ranging sensor inverts into a thermometer that measures the "
             "AVERAGE temperature of the whole air path — no radiation error, no thermal mass, "
             "millisecond response. This is how professional sonic anemometers measure "
             "temperature.",
         confound="Wind along the path adds ±v/c error (use two opposite paths to cancel — which "
                  "then measures the wind too); humidity shifts c ~0.3%.",
         example="US-100 facing a wall at exactly 1.000 m: a thermometer with no thermometer in "
                 "it — Derived Quantities row 37, computed."),

    dict(key="helmholtz-level", name="Helmholtz through-wall fill gauge",
         pattern="active-probe",
         requires=[("sound-pressure", 1)],
         provides="container-fullness",
         math="f = (c/2π)·√(A/(V·L)): resonant frequency rises as headspace V shrinks; chirp "
              "and find the peak",
         why="Every container is a bottle you can blow across. A speaker chirps, a mic finds the "
             "resonance, and headspace volume falls out of the frequency — through the wall, no "
             "contact with the contents, movable between containers in seconds.",
         confound="Works on the AIR space: a brim-full rigid container has no resonator left; "
                  "foam on liquids damps the peak. Needs a port or flexible wall to couple.",
         example="MAX98357A speaker + INMP441: how full is the rice jar, the fuel can, the "
                 "sealed drum — Derived Instruments row 4, computed."),

    # --------------------------------------------------------- triangulation
    dict(key="tdoa-direction", name="Acoustic direction finder",
         pattern="triangulation",
         requires=[("sound-pressure", 2)],
         provides="sound-direction",
         math="θ = arcsin(Δt·343/d) from the arrival-time difference across a known baseline d",
         why="Two ears is all direction takes: sound crosses a 20 cm baseline in 580 µs, and "
             "I2S mics timestamp well inside that. Add a third mic and bearing becomes "
             "position — glass break, bark, knock: located, not just detected.",
         confound="Echoes in hard rooms produce phantom bearings — correlate on the FIRST "
                  "arrival only; the mics must share one clock (one I2S bus, not two ESP32s).",
         example="2× INMP441 on one bus: 'the sound came from the window side' for £6 — the "
                 "difference between an alert and actionable information."),

    dict(key="beam-speed-trap", name="Two-beam speed trap",
         pattern="triangulation",
         requires=[("proximity", 2)],
         provides="vehicle-speed",
         math="v = d/Δt between two beam-break timestamps a known distance apart; ±1% with "
              "µs timestamps",
         why="Speed is distance over time, and two interrupted beams measure exactly that — no "
             "radar, no calibration, no Doppler ambiguity. Direction comes free from beam "
             "order; length from occlusion time; that is classify-count-and-speed from two "
             "photogates.",
         confound="Works where traffic passes one at a time; two overlapping vehicles merge "
                  "into one long occlusion. Rain sensitivity depends on beam quality.",
         example="2× E18-D80NK across the drive, 2 m apart: evidence-grade 'how fast do they "
                 "really take our street', for £6."),

    dict(key="door-baro-locator", name="Barometric door locator",
         pattern="triangulation",
         requires=[("pressure-absolute", 3)],
         provides="which-door-opened",
         math="A door swing is a ~0.3–3 Pa transient; arrival order + amplitude ratio across 3 "
              "synced nodes localises the source",
         why="Every door pumps a pressure wave through the whole house, and modern barometers "
             "resolve single pascals. Three nodes with a shared timebase triangulate WHICH door "
             "— whole-home entry awareness with no sensor on any door and nothing visible "
             "anywhere.",
         confound="HVAC blower starts and wind gusts through vents make similar transients: "
                  "fingerprint each door's signature (fast attack, slow decay) during a quiet "
                  "week first.",
         example="3× BMP390 + ESP-NOW timestamps: Derived Instruments row 1 — invisible "
                 "security, computed."),

    dict(key="pipe-leak-correlator", name="Acoustic pipe-leak correlator",
         pattern="triangulation",
         requires=[("sound-structural", 2)],
         provides="leak-location",
         math="Leak position from cross-correlation lag: x = (L − v·Δt)/2, v ≈ 1200–1400 m/s "
              "in water-filled metal pipe",
         why="A pressurised leak hisses continuously INTO the pipe wall, and the pipe is a "
             "waveguide. Two contact pickups bracketing the run cross-correlate to the metre — "
             "this is exactly the £10k instrument water utilities carry, in principle and "
             "in math.",
         confound="Plastic pipe attenuates and slows the wave (v drops to ~300–500 m/s and "
                  "range shrinks): calibrate v with a deliberate tap at a known point first.",
         example="2× piezo discs clamped 20 m apart: dig ONE hole where the correlation says, "
                 "not five along the run."),

    # ---------------------------------------------------------------- fleet
    dict(key="desk-utilisation", name="Space-utilisation truth map",
         pattern="fleet",
         requires=[("occupancy-signal", 3)],
         provides="space-utilisation-map",
         math="Per-zone occupied-hours histograms; utilisation = occupied / available hours "
              "per zone per week",
         why="One presence sensor answers 'is anyone here'; a fleet answers 'which spaces earn "
             "their rent' — a spatial pattern invisible from any single point. Desk-booking "
             "vendors charge per-desk-per-month for exactly this histogram.",
         confound="Sensor placement bias: a PIR facing a walkway counts traffic as occupancy. "
                  "Aim each zone's sensor at the seat, not the aisle.",
         example="3+ PIR/radar nodes over ESP-NOW: 'the phone booths are rammed and the big "
                 "meeting room is empty 92% of the time' — floor-plan decisions from data."),

    dict(key="microclimate-grid", name="Thermal microclimate mapper",
         pattern="fleet",
         requires=[("temperature-contact", 3)],
         provides="thermal-map",
         math="Simultaneous ΔT across ≥3 fixed points; persistent cold spots + dew-point "
              "proximity = condensation/draught candidates",
         why="A single thermostat reads one point of a field that varies 5°C across a room. "
             "Three synchronised cheap probes see the STRUCTURE: the draught path, the cold "
             "wall, the stratification layer — where to point insulation money.",
         confound="Uncalibrated probes differ by ±0.5°C: swap positions for one day and any "
                  "offset that follows the probe is the probe, not the room.",
         example="3× DS18B20 on one bus: find the real reason the study is always cold before "
                 "paying for anything."),

    # -------------------------------------------------------- complementary
    dict(key="baro-gps-altitude", name="Fast-and-absolute altimeter",
         pattern="complementary",
         requires=[("pressure-absolute", 1), ("position-global", 1)],
         provides="how-high",
         math="Complementary filter: alt = LP(GPS_alt) + HP(baro_alt); baro gives cm-resolution "
              "dynamics, GPS pins the absolute and cancels weather drift",
         why="The barometer is precise but wanders with the weather; GPS altitude is absolute "
             "but noisy and slow. Each is the other's missing half — split them by frequency "
             "and you get an altimeter neither can be alone. This is how every drone does it.",
         confound="Indoor GPS starves the absolute reference and the filter slowly inherits the "
                  "weather drift; re-anchor when the fix returns.",
         example="BMP390 + NEO-6M: floor-accurate altitude outdoors, stair-step resolution "
                 "on the move."),

    dict(key="sleep-two-signal", name="Contactless sleep-stage estimator",
         pattern="complementary",
         requires=[("respiration", 1), ("acceleration", 1)],
         provides="sleep-stage-proxy",
         math="Actigraphy (movement bouts) × respiration regularity: still+regular ≈ deep, "
              "still+variable ≈ REM, moving ≈ light/wake",
         why="Movement alone cannot see REM (body still, breathing chaotic); breathing alone "
             "cannot date sleep onset (posture shifts). Together they reproduce the consumer "
             "sleep-staging that wearables sell — with nothing worn.",
         confound="Two sleepers in the beam mix signals (range-gate the radar per side); it is "
                  "a stage PROXY, not polysomnography, and honest naming keeps it useful.",
         example="MR60BHA2 + a bed-frame IMU: the £30 nightstand sleep lab, no wristband to "
                 "forget to charge."),

    dict(key="pm-gps-dosimeter", name="Personal exposure dosimeter",
         pattern="complementary",
         requires=[("particulate-mass", 1), ("position-global", 1)],
         provides="personal-exposure-dose",
         math="Dose = ∫ C(t)·V̇ dt segmented by GPS trace; map µg-minutes to street segments",
         why="City air averages hide the truth: half a day's particulate dose arrives in the "
             "ten minutes beside the main road. Position turns a concentration logger into a "
             "personal dosimeter and a WHERE-map — the number epidemiology wants and nobody "
             "measures.",
         confound="Optical PM counters over-read in fog and >75% RH (the known humidity wall): "
                  "log RH and flag humid segments rather than believing them.",
         example="PMS5003 + NEO-6M in a bag: after one week you will re-route your cycle "
                 "commute — SYNERGY's five-star AIR×BODY cell, computed."),

    dict(key="pf-power-quality", name="Power-factor and quality monitor",
         pattern="complementary",
         requires=[("current-ac", 1), ("voltage", 1)],
         provides="power-quality",
         math="PF = P/(V_rms·I_rms); THD from harmonic decomposition; sag/swell from cycle-by-"
              "cycle V_rms",
         why="Current alone prices energy; voltage alone sees the grid; simultaneously they see "
             "QUALITY — power factor, harmonics, the sag your machines feel. A motor at PF 0.6 "
             "and a warm neutral are invisible to either sensor alone.",
         confound="Phase alignment between the two channels IS the measurement: sample "
                  "simultaneously (one ADC, alternating) or the PF number is fiction.",
         example="ZMPT101B + SCT-013 into one ADS1115: know why the workshop lights dip when "
                 "the compressor starts."),

    dict(key="hive-triple", name="Hive vital-signs fusion",
         pattern="complementary",
         requires=[("weight", 1), ("sound-structural", 1), ("temperature-contact", 1)],
         provides="hive-state",
         math="Weight slope = forage/consumption; acoustic 200–500 Hz band = swarm prep; "
              "brood T held 34–36°C = queenright",
         why="Each channel sees one organ of the superorganism: scales see the economy, sound "
             "sees the mood, temperature sees the brood. Any one gives a guess; the triple "
             "gives a diagnosis — swarm prediction days out, queen loss in hours.",
         confound="Rain adds kilograms and wind shakes the scale: a roof and a local weather "
                  "log keep the weight channel honest.",
         example="HX711 platform + piezo on the wall + DS18B20 in the cluster: the £25 version "
                 "of the commercial hive monitor, and it winters better."),

    dict(key="frost-triple", name="Radiative frost forecaster",
         pattern="context-gating",
         requires=[("temperature-contact", 1), ("air-velocity", 1)],
         provides="frost-tonight",
         math="Frost when: sky-facing radiative loss (clear night) + wind < 2 m/s (no mixing) + "
              "T approaching 0 with dew point < 0 (deposition not dew)",
         why="Radiative frost needs THREE conditions at once — cold, calm, and clear. "
             "Temperature alone false-alarms on windy nights; the wind channel is what turns a "
             "thermometer into a frost forecaster the allotment can act on.",
         confound="Local cold-air pooling: a valley plot frosts 3°C before the sensor on the "
                  "shed wall. Site the probe at plant height, at the lowest point.",
         example="NTC at soil level + anemometer: fleece the beds only on the nights that "
                 "actually bite."),

    dict(key="building-ua", name="Whole-building heat-loss coefficient",
         pattern="differential",
         requires=[("energy-accumulated", 1), ("temperature-contact", 2)],
         provides="building-heat-loss",
         math="UA[W/K] = heating power ÷ (T_in − T_out), fitted over steady calm nights",
         why="Divide what the heating burned by the temperature difference it maintained and "
             "the building's entire thermal quality collapses to one number. Track UA across a "
             "winter and every insulation claim becomes checkable arithmetic.",
         confound="Solar gain, wind, and thermal mass all bend it: fit ONLY steady overnight "
                  "windows, and the differential temperature pair must straddle the envelope "
                  "(one in, one out).",
         example="A pulse-output meter reader + 2× DS18B20: 'the loft job cut UA from 210 to "
                 "150 W/K' — renovation with receipts."),

    dict(key="gait-corridor", name="Passive gait-speed corridor",
         pattern="temporal",
         requires=[("through-wall-motion", 1)],
         provides="gait-quality",
         math="Walking speed from range-rate through a fixed corridor; declining weekly median "
              "gait speed is a validated frailty predictor",
         why="Gait speed is the vital sign geriatrics calls the 'sixth vital sign', and a radar "
             "in a hallway measures it every single day without wearables, cameras, or "
             "cooperation. The TREND is the signal — no single walk matters.",
         confound="Multiple residents mix distributions: separate by height profile, schedule, "
                  "or accept household-level trending. Carried laundry legitimately slows "
                  "anyone.",
         example="LD2450 in the hallway: the daily walk to the kettle becomes a falls-risk "
                 "early warning, invisibly — elder care that respects dignity."),

    dict(key="which-room-energy", name="Per-use appliance cost meter",
         pattern="context-gating",
         requires=[("energy-accumulated", 1), ("cycle-complete", 1)],
         provides="cost-per-use",
         math="Cost/use = (E_end − E_start over one detected cycle) × tariff; distribution over "
              "cycles reveals degradation",
         why="'The dishwasher costs 43p a run, the tumble dryer £1.60' beats any kWh graph "
             "humans ignore. Cycle detection gates the energy integral into units people "
             "actually decide with — and a creeping cost-per-cycle is an early fault signal "
             "(scale build-up, blocked filters).",
         confound="Overlapping appliances on one metered circuit blur cycle boundaries — meter "
                  "the socket, or disaggregate first (the NILM edge feeds this one).",
         example="BL0940 socket + vibration cycle detector: the number that changes when "
                 "people run the eco programme."),
]


# --------------------------------------------------------------------- helpers

def matrix_capabilities(edges=None, INFERENCE=None, PHENOMENON=None):
    """THE single source of the Coverage Matrix column order: every INFERENCE
    key in vocab order, then only the PHENOMENON keys some edge references.
    Returns [(key, kind)]."""
    import vocab
    INFERENCE = INFERENCE or vocab.INFERENCE
    PHENOMENON = PHENOMENON or vocab.PHENOMENON
    edges = FUSION_EDGES if edges is None else edges
    ref = {c for e in edges for c, _m in e["requires"]}
    return ([(k, "inference") for k in INFERENCE]
            + [(k, "phenomenon") for k in PHENOMENON if k in ref])


def covers(record):
    """Capability set of one sensor: phenomena UNION inferences, vocab-filtered."""
    import vocab
    return ({p for p in record.get("phenomena") or [] if p in vocab.PHENOMENON}
            | {i for i in record.get("inferences") or [] if i in vocab.INFERENCE})


def topo_edges(edges=None):
    """Edges in dependency order (an edge that consumes another's `provides`
    comes after it). Raises ValueError on a cycle — the validator calls this,
    and the Kit Builder emits rows in this order so chained Excel formulas
    only ever reference earlier rows."""
    edges = FUSION_EDGES if edges is None else edges
    provided = {}
    for e in edges:
        provided.setdefault(e["provides"], []).append(e["key"])
    by_key = {e["key"]: e for e in edges}
    deps = {e["key"]: {k for c, _m in e["requires"] for k in provided.get(c, [])}
            for e in edges}
    order, placed = [], set()
    while len(order) < len(edges):
        progress = False
        for e in edges:
            if e["key"] in placed:
                continue
            if deps[e["key"]] <= placed:
                order.append(e)
                placed.add(e["key"])
                progress = True
        if not progress:
            cyc = [k for k in deps if k not in placed]
            raise ValueError(f"fusion edge dependency cycle among: {cyc}")
    return order


FUSION_FINDINGS = [
    ("The lower bound is now a measured distance",
     "Every solver number so far counted what each sensor supports ALONE, and admitted in "
     "writing that this was a lower bound. This sheet computes the gap. The same parts, plus "
     "time and arithmetic, fire the derived instruments below — outcomes with NO row in the "
     "catalog, because no part provides them. Kits do."),
    ("Emergence is cheap because the atoms are already there",
     "Almost every edge below consumes capabilities the cost-optimal kits already hold: "
     "temperature points, a barometer, a CO2 channel, a microphone, a current clamp. The "
     "marginal cost of a derived instrument held by your kit is ZERO parts — the instrument "
     "is the equation. That is why the closure numbers jump without the price moving."),
    ("Multiplicity is the honest fine print",
     "×N in an edge means N independent measurement points. The computation counts distinct "
     "catalog parts, so it UNDERSTATES you: two copies of one £2 probe satisfy a ×2 edge in "
     "practice. Every closure figure on this sheet therefore remains a conservative lower "
     "bound — the true reach of a kit is higher still."),
    ("The chains are where it compounds",
     "Two edges below consume the OUTPUT of other edges: the mould sentinel runs on the "
     "condensation watcher, the radon proxy runs on the ventilation meter. Derived "
     "instruments feeding derived instruments is how capability compounds — and why adding "
     "one cheap part sometimes unlocks three rows at once."),
]
