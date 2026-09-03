# Outcome Solver — the canonical run

**405 sensors · 151 outcomes · 2401 sensor→outcome edges.** This is the Maximum Coverage Problem. Solving it exactly is NP-hard, but greedy selection is provably within (1 − 1/e) ≈ 63% of optimal, and it is proven that no polynomial-time algorithm beats that bound unless P = NP. Greedy is therefore the best available answer, not a shortcut.

- Optimising **outcomes per pound**: 58 sensors, $733, 100% coverage.
- Optimising **outcomes per part**: 39 sensors, $1263, 100% coverage.

---

## The inversion: specificity is anti-recombinatory

Run the optimiser by cost and the parts it reaches for first are the cheapest and dumbest in the catalog — a 50p piezo disc, a 50p reed switch, a 30p thermistor, a 20p photoresistor, a £2 IMU. The expensive specific instruments arrive last and buy one outcome each. This is not a quirk of the data, it is what specificity MEANS: a sensor engineered to respond to exactly one thing has been engineered to ignore everything else. Generic transducers are cheap BECAUSE they are unselective, and unselective is precisely what makes them recombinatory.

## Therefore the omniscience kit is cheap

Half of everything this atlas knows how to infer is reachable for the price of a takeaway. The constraint 'nothing over $5' still reaches nearly three quarters of all outcomes. If your instinct is that broad capability requires expensive instruments, the arithmetic says the opposite — and it says so decisively.

## What the expensive parts actually buy

They buy the tail. Each of the last additions is the SOLE route to one outcome: lightning distance, radon accumulation, isotope identity, belt slip, atmospheric charge. Those are worth buying when you want that specific outcome, and worth nothing to general capability. Read the irreplaceability table as a shopping list for intentions, not for breadth.

## Where the real leverage is

It is not in the sensor list at all — it is in TIME and FUSION. A generic transducer plus a baseline plus a second modality produces outcomes that neither sensor claims alone. The optimiser below counts only what each sensor supports BY ITSELF, so every number here is a LOWER BOUND on what the kit can actually do once the Derived Quantities and Combination Grammar sheets are applied to it.

## How to use this sheet

Pick the row you want from Outcome → Kit. If you want breadth, buy a tier. If you want a domain, buy its kit. If you have a constraint, read what it costs you in outcomes BEFORE you commit — the constraint table is the only place in this atlas that prices a design decision in capability rather than in money.

---

## The four kits

| Tier | Sensors | Outcomes | % | Cost | What it adds |
|---|--:|--:|--:|--:|---|
| **FOUNDATION** | 13 | 79 | 52% | $18 | Piezo contact mic / disc · Reed switch · NTC thermistor 10k · Photoresistor (LDR) · MPU-6050 6-axis IMU · Wi-Fi CSI sensing (the router IS the sensor) · INA219 current/power monitor · AHT20 temp/humidity · MQ-2 smoke/LPG gas · RC522 RFID reader · QMC5883L compass · BMP280 budget barometer · DS18B20 digital temp probe |
| **CORE** | 27 | 114 | 75% | $62 | Capacitive soil moisture v2 · HC-SR04 ultrasonic · HC-SR501 PIR motion · MQ-135 air quality · A3144 / SS49E Hall switches · TCS3200 frequency-output colour sensor · BPW34 PIN photodiode · MAX30102 pulse oximeter · ADS1115 16-bit ADC (the analog fixer) · BL0940 calibration-free mains metering IC · LD2410 mmWave presence · Ultrasonic mic experiments · NEO-6M GPS · IR flame detector (flicker) |
| **BROAD** | 43 | 136 | 90% | $149 | US-100 ultrasonic w/ temp comp · PIN photodiode radiation detector · MQ-7 carbon monoxide · ML8511 / VEML6075 UV outdoor · EC / TDS sensor · ZMPT101B voltage sensor · Thermistor airflow (nasal) kit · Photoelectric beam sensor E18-D80NK · SI4432/CC1101 sub-GHz sniffer · Vertical float level switch (reed) · LDC1612 inductive sensing · HX711 + load cell · Azoteq IQS7211 / IQS263 proximity + touch · FSR402 force resistor · MLX90614 IR thermometer · Flex sensor 2.2" |
| **COMPLETE** | 58 | 151 | 100% | $733 | Bat/dolphin: 40kHz ranging array · RD-03D 24GHz multi-target tracking radar · GSR / EDA sensor · Gypsum soil moisture block · Ikea VINDRIKTNING hack · Atmospheric electricity (field mill lite) · AS3935 lightning detector · ZE08-CH2O formaldehyde · BioAmp EXG Pill · AS7331 spectral UV · MQ-131 ozone · IIS3DWB wideband vibration sensor · SiPM photodetector module · ORP (redox) probe · RD200 radon sensor |

## The run, step by step (cost-optimal)

| # | Sensor | $ | Buys | Total | % | Cum $ | Outcomes this step bought |
|--:|---|--:|--:|--:|--:|--:|---|
| 1 | Piezo contact mic / disc | 0.5 | +14 | 14 | 9% | 0 | Is compressed air leaking, and where?; Is a bearing starting to fail?; Has the cycle finished?; Has this drifted from how it behaved when new?; Did glass break?; Has someone entered who shouldn't have?; How much is this machine actually used?; Is it on?; Is it idle, loaded, or jammed?; Was it dropped, and how hard?; Is anyone here?; Has someone interfered with it?; Did something sound wrong?; Is water escaping where it shouldn't? |
| 2 | Reed switch | 0.5 | +10 | 24 | 16% | 1 | How full is it?; Is it open or closed?; Did they come in, or go out?; How fast is water flowing?; Is it raining, and how hard?; How many went past?; Is the thing there?; How fast is it turning?; How much is in the tank?; How much water was used, by whom, and when? |
| 3 | NTC thermistor 10k | 0.3 | +4 | 28 | 19% | 1 | Will there be frost tonight?; How hot is that surface?; Is something running hotter than it should?; Is the water at the right temperature? |
| 4 | Photoresistor (LDR) | 0.2 | +4 | 32 | 21% | 2 | Did something cross this line?; Did someone leave it switched on?; Has this plant had enough light today?; Is the sky clear or clouded? |
| 5 | MPU-6050 6-axis IMU | 2 | +8 | 40 | 26% | 4 | Is this level, and by how much is it off?; How is this person walking?; Is it out of balance or misaligned?; Has it been moved or disturbed?; What posture is this body in?; How much have they moved today?; Has this structure shifted or tilted since last time?; Is there a tremor, and at what frequency? |
| 6 | Wi-Fi CSI sensing (the router IS the sensor) | 0 | +4 | 44 | 29% | 4 | How fast are they breathing?; How many people are in this space?; Did someone fall?; Is something moving on the other side of that wall? |
| 7 | INA219 current/power monitor | 2.5 | +8 | 52 | 34% | 6 | Is it drawing an abnormal amount of power?; How much charge is left?; Is this battery degrading?; Will this node survive on its battery until spring?; What is draining power while doing nothing?; How much power is being used right now?; Is the solar array performing as it should?; Which appliance just turned on? |
| 8 | AHT20 temp/humidity | 2 | +6 | 58 | 38% | 8 | Is this room stuffy — does it need fresh air?; Has the paint, resin or glue finished curing?; Are conditions right for fungal disease?; How much hotter is this spot than the next street?; Is this surface going to grow mould?; Is the air dry enough to damage wood, skin or instruments? |
| 9 | MQ-2 smoke/LPG gas | 2 | +5 | 63 | 42% | 10 | Is someone cooking?; Is there a flammable gas leak?; Is there smoke?; Was the hob left on with nobody there?; Did something start off-gassing or smelling? |
| 10 | RC522 RFID reader | 2 | +5 | 68 | 45% | 12 | Where is this thing right now?; Is this person allowed to operate this?; Which specific object is this?; How long has this desk/room/seat been in use?; Which specific person is this? |
| 11 | QMC5883L compass | 2 | +4 | 72 | 48% | 14 | Where is the wiring or metal inside this wall?; Is there ferrous metal or a field distortion here?; Is a vehicle arriving?; Which way am I pointing? |
| 12 | BMP280 budget barometer | 1.5 | +3 | 75 | 50% | 16 | What altitude or floor am I on?; Am I back at the exact same place?; Is a storm coming? |
| 13 | DS18B20 digital temp probe | 2.5 | +4 | 79 | 52% | 18 | Is the compost heating properly — or dangerously?; Is this food still good?; Is the soil warm enough to sow?; How much heat did this water actually carry? |
| 14 | Capacitive soil moisture v2 | 2 | +3 | 82 | 54% | 20 | How fast is it growing?; How wet is this material?; Does this plant need water? |
| 15 | HC-SR04 ultrasonic | 1.5 | +2 | 84 | 56% | 22 | How much is left, and how long until it runs out?; Is there something in the way? |
| 16 | HC-SR501 PIR motion | 1.5 | +2 | 86 | 57% | 23 | Has nobody moved for worryingly long?; Has this person's daily routine changed? |
| 17 | MQ-135 air quality | 2.5 | +3 | 89 | 59% | 26 | Are the animals comfortable and behaving normally?; What does this smell like — which known smell is it?; Is ventilation actually working? |
| 18 | A3144 / SS49E Hall switches | 0.4 | +1 | 90 | 60% | 26 | How windy is it, and from where? |
| 19 | TCS3200 frequency-output colour sensor | 4 | +4 | 94 | 62% | 30 | Does this colour match the reference?; Is it ripe?; What is this made of?; Is the water cloudy — sediment, algae, runoff? |
| 20 | BPW34 PIN photodiode | 1 | +1 | 95 | 63% | 31 | How much radiation is here? |
| 21 | MAX30102 pulse oximeter | 6 | +5 | 100 | 66% | 37 | What is the blood oxygen saturation?; What is the heart rate?; How stressed or recovered is this body?; What sleep stage is this, roughly?; Is this person's arousal or stress rising? |
| 22 | ADS1115 16-bit ADC (the analog fixer) | 3 | +2 | 102 | 68% | 40 | How concentrated is the nutrient solution?; Is the water too acidic or alkaline? |
| 23 | BL0940 calibration-free mains metering IC | 1.5 | +1 | 103 | 68% | 41 | What did that actually cost to run? |
| 24 | LD2410 mmWave presence | 5 | +3 | 106 | 70% | 46 | Are they asleep, and how well?; Is someone still here, sitting perfectly still?; Whereabouts in the room are they? |
| 25 | Ultrasonic mic experiments | 6 | +3 | 109 | 72% | 52 | Is there electrical arcing or partial discharge?; Is lubrication breaking down?; What is making noise above human hearing? |
| 26 | NEO-6M GPS | 8 | +4 | 113 | 75% | 60 | How far have I gone?; How fast am I moving?; How fast are vehicles going past?; Where am I on Earth? |
| 27 | IR flame detector (flicker) | 2 | +1 | 114 | 75% | 62 | Is there a flame? |
| 28 | US-100 ultrasonic w/ temp comp | 4 | +2 | 116 | 77% | 66 | Is water rising, and how fast?; How deep is the snow? |
| 29 | PIN photodiode radiation detector | 2 | +1 | 117 | 77% | 68 | How many cosmic rays are passing through? |
| 30 | MQ-7 carbon monoxide | 2.5 | +1 | 118 | 78% | 71 | Is there carbon monoxide? |
| 31 | ML8511 / VEML6075 UV outdoor | 6 | +2 | 120 | 79% | 77 | How much solar energy is available?; How much UV have I accumulated today? |
| 32 | EC / TDS sensor | 12 | +4 | 124 | 82% | 89 | How concentrated is this solution?; Has this been contaminated?; Is the filter blocked?; What is the nutrient status of this soil? |
| 33 | ZMPT101B voltage sensor | 3 | +1 | 125 | 83% | 92 | Is the supply voltage clean and stable? |
| 34 | Thermistor airflow (nasal) kit | 3 | +1 | 126 | 83% | 95 | Has breathing become irregular or stopped? |
| 35 | Photoelectric beam sensor E18-D80NK | 3 | +1 | 127 | 84% | 98 | Was the boundary crossed, and where along it? |
| 36 | SI4432/CC1101 sub-GHz sniffer | 4 | +1 | 128 | 85% | 102 | What is transmitting nearby, and how strongly? |
| 37 | Vertical float level switch (reed) | 4 | +1 | 129 | 85% | 106 | Is the pump about to run dry? |
| 38 | LDC1612 inductive sensing | 9 | +2 | 131 | 87% | 115 | What material is this?; Is this authentic or counterfeit? |
| 39 | HX711 + load cell | 5 | +1 | 132 | 87% | 120 | What is the beehive doing? |
| 40 | Azoteq IQS7211 / IQS263 proximity + touch | 6 | +1 | 133 | 88% | 126 | Is someone actually looking at this? |
| 41 | FSR402 force resistor | 7 | +1 | 134 | 89% | 133 | Which muscle is working, and how hard? |
| 42 | MLX90614 IR thermometer | 8 | +1 | 135 | 89% | 141 | Is body temperature drifting — fever, ovulation, heat stress? |
| 43 | Flex sensor 2.2" | 8 | +1 | 136 | 90% | 149 | What angle is this joint at, through its range? |
| 44 | Bat/dolphin: 40kHz ranging array | 8 | +1 | 137 | 91% | 157 | What is the shape of the space around me? |
| 45 | RD-03D 24GHz multi-target tracking radar | 9 | +1 | 138 | 91% | 166 | How many are waiting, and for how long? |
| 46 | GSR / EDA sensor | 10 | +1 | 139 | 92% | 176 | Are they likely dehydrated? |
| 47 | Gypsum soil moisture block | 10 | +1 | 140 | 93% | 186 | How hard must roots work to get water? |
| 48 | Ikea VINDRIKTNING hack | 13 | +1 | 141 | 93% | 199 | How polluted is the air right now? |
| 49 | Atmospheric electricity (field mill lite) | 15 | +1 | 142 | 94% | 214 | Is the atmosphere electrically charged? |
| 50 | AS3935 lightning detector | 20 | +1 | 143 | 95% | 234 | How far away is the lightning? |
| 51 | ZE08-CH2O formaldehyde | 22 | +1 | 144 | 95% | 256 | Is new furniture or flooring off-gassing? |
| 52 | BioAmp EXG Pill | 25 | +1 | 145 | 96% | 281 | Did they blink or move their eyes? |
| 53 | AS7331 spectral UV | 27.5 | +1 | 146 | 97% | 308 | Is the sanitiser actually working? |
| 54 | MQ-131 ozone | 30 | +1 | 147 | 97% | 338 | Is something emitting ozone? |
| 55 | IIS3DWB wideband vibration sensor | 45 | +1 | 148 | 98% | 383 | Is the belt or coupling slipping? |
| 56 | SiPM photodetector module | 60 | +1 | 149 | 99% | 443 | Which radioactive isotope is this? |
| 57 | ORP (redox) probe | 110 | +1 | 150 | 99% | 553 | Is there enough oxygen for fish or microbes? |
| 58 | RD200 radon sensor | 180 | +1 | 151 | 100% | 733 | Is radon accumulating? |

## The same problem, fewest PARTS instead of fewest pounds

39 sensors instead of 58, but $1263 instead of $733. Optimising for part count reaches for capable multi-purpose modules; optimising for cost reaches for dumb cheap transducers. Both reach 100%.

| # | Sensor | $ | Buys | Total | % | Cum $ |
|--:|---|--:|--:|--:|--:|--:|
| 1 | Scale-hacking: NAU7802 | 12 | +16 | 16 | 11% | 12 |
| 2 | INMP441 I2S MEMS mic | 3 | +12 | 28 | 19% | 15 |
| 3 | Time-of-flight gesture radar 60GHz | 110 | +10 | 38 | 25% | 125 |
| 4 | LDC1612 inductive sensing | 9 | +9 | 47 | 31% | 134 |
| 5 | DS18B20 digital temp probe | 2.5 | +8 | 55 | 36% | 136 |
| 6 | BME688 gas + climate AI | 15 | +8 | 63 | 42% | 152 |
| 7 | INA219 current/power monitor | 2.5 | +8 | 71 | 47% | 154 |
| 8 | BNO086 high-perf fusion IMU | 22 | +7 | 78 | 52% | 176 |
| 9 | Grove Vision AI v2 | 16 | +6 | 84 | 56% | 192 |
| 10 | Analog pH kit | 30 | +5 | 89 | 59% | 222 |
| 11 | YF-S201 flow sensor | 5 | +5 | 94 | 62% | 227 |
| 12 | MAX30102 pulse oximeter | 6 | +4 | 98 | 65% | 233 |
| 13 | ML8511 / VEML6075 UV outdoor | 6 | +4 | 102 | 68% | 239 |
| 14 | Acoustic emission (ultrasonic contact) | 10 | +4 | 106 | 70% | 249 |
| 15 | Electrochemical gas cells | 80 | +3 | 109 | 72% | 329 |
| 16 | Tipping bucket rain gauge | 12 | +3 | 112 | 74% | 341 |
| 17 | NEO-6M GPS | 8 | +3 | 115 | 76% | 349 |
| 18 | Person Sensor (Useful Sensors) | 10 | +3 | 118 | 78% | 359 |
| 19 | Muon detector (CosmicWatch) | 100 | +3 | 121 | 80% | 459 |
| 20 | PMS7003 laser particle counter | 20 | +3 | 124 | 82% | 479 |
| 21 | TSL2591 high dynamic lux | 7 | +2 | 126 | 83% | 486 |
| 22 | TCS34725 RGB color | 7 | +2 | 128 | 85% | 493 |
| 23 | LD2410 mmWave presence | 5 | +2 | 130 | 86% | 498 |
| 24 | BioAmp EXG Pill | 25 | +2 | 132 | 87% | 523 |
| 25 | AS3935 lightning detector | 20 | +2 | 134 | 89% | 543 |
| 26 | PZEM-004T AC power module | 11 | +2 | 136 | 90% | 554 |
| 27 | Watermark granular-matrix soil water sensor | 45 | +2 | 138 | 91% | 599 |
| 28 | Ground vibration fence: fiber + photodiode | 10 | +2 | 140 | 93% | 609 |
| 29 | TMP117 ultra-precise temp | 11 | +1 | 141 | 93% | 620 |
| 30 | ZE08-CH2O formaldehyde | 22 | +1 | 142 | 94% | 642 |
| 31 | JSN-SR04T waterproof ultrasonic | 6 | +1 | 143 | 95% | 648 |
| 32 | Seeed MR60BHA2 vital-sign radar | 25 | +1 | 144 | 95% | 673 |
| 33 | GSR / EDA sensor | 10 | +1 | 145 | 96% | 683 |
| 34 | Dissolved oxygen kit (Atlas EZO-DO) | 170 | +1 | 146 | 97% | 853 |
| 35 | u-blox M10 GNSS | 20 | +1 | 147 | 97% | 873 |
| 36 | RD200 radon sensor | 180 | +1 | 148 | 98% | 1053 |
| 37 | Scintillating gamma spectrometer | 150 | +1 | 149 | 99% | 1203 |
| 38 | Atmospheric electricity (field mill lite) | 15 | +1 | 150 | 99% | 1218 |
| 39 | IIS3DWB wideband vibration sensor | 45 | +1 | 151 | 100% | 1263 |

## The multiplier — every kit, closed under fusion

The solver's coverage numbers count what each sensor supports alone — a stated lower bound. 52 authored fusion edges (from the atlas's Derived Quantities, Derived Instruments and Combination Grammar) compute the gap: 26 outcomes exist in no sensor's row, because only combinations provide them.

| Kit | Parts | Cost | Declared | Edges fired | Emergent | TOTAL |
|---|--:|--:|--:|--:|--:|--:|
| **FOUNDATION** | 13 | $18 | 79 | 11 | +8 | **87** |
| **CORE** | 27 | $62 | 114 | 25 | +13 | **127** |
| **BROAD** | 43 | $149 | 136 | 35 | +15 | **151** |
| **COMPLETE** | 58 | $733 | 151 | 38 | +18 | **169** |

### Best next purchase for emergence (from FOUNDATION)

| Add this | $ | New instruments | Which |
|---|--:|--:|---|
| BL0940 calibration-free mains metering IC | 1.5 | +5 | building-ua · inrush-signature · nilm-signature · pf-power-quality · which-room-energy |
| ADE7953 dual-channel single-phase energy meter | 3.5 | +5 | building-ua · inrush-signature · nilm-signature · pf-power-quality · which-room-energy |
| ATM90E32AS polyphase energy metering AFE | 4.0 | +5 | building-ua · inrush-signature · nilm-signature · pf-power-quality · which-room-energy |
| MLX90614 IR thermometer | 8 | +5 | black-ice-watch · cloud-cover-ir · condensation-watch · mould-forecast · stove-watch |
| PZEM-004T AC power module | 11 | +5 | building-ua · inrush-signature · nilm-signature · pf-power-quality · which-room-energy |
| MLX90632 miniature IR temp | 14 | +5 | black-ice-watch · cloud-cover-ir · condensation-watch · mould-forecast · stove-watch |
| MLX90614 forehead mode | 25 | +5 | black-ice-watch · cloud-cover-ir · condensation-watch · mould-forecast · stove-watch |
| Grid-EYE AMG8833 thermal array | 35 | +5 | black-ice-watch · cloud-cover-ir · condensation-watch · mould-forecast · stove-watch |
| Eastron SDM120-Modbus DIN energy meter | 38.0 | +5 | building-ua · inrush-signature · nilm-signature · pf-power-quality · which-room-energy |
| MLX90640 thermal camera | 45 | +5 | black-ice-watch · cloud-cover-ir · condensation-watch · mould-forecast · stove-watch |
| D6T thermal presence | 55 | +5 | black-ice-watch · cloud-cover-ir · condensation-watch · mould-forecast · stove-watch |
| MLX90641 thermal (16x12) | 60 | +5 | black-ice-watch · cloud-cover-ir · condensation-watch · mould-forecast · stove-watch |

### The instruments

| Instrument | Pattern | Requires | Provides | Math |
|---|---|---|---|---|
| Condensation forecaster | differential | dew-point + temperature-remote | NEW: condensation-risk | Risk when T_surface − T_dew < 1.5°C (T_dew via Magnus: γ = ln(RH/100) + 17.62·T/(243.12+T)) |
| Mould sentinel (surface-honest) | temporal | condensation-risk | route: mould-risk | Sustained surface-RH > 80% ≈ T_surface within 3°C of T_dew for >6 h/day, integrated over days |
| Hydronic heat meter | differential | flow-liquid + ×2 temperature-contact | route: thermal-energy-moved | P[W] = (flow[L/min]/60) × 4186 × ΔT[K]; energy = ∫P dt |
| Wet-bulb heat-stress meter | differential | ×2 temperature-contact | NEW: wet-bulb-heat-stress | T_wet from psychrometric pair (one probe in a wet cotton wick, ~3 m/s airflow); T_wet ≥ 31°C = dangerous, ≥ 35°C = lethal to sustained human work |
| Dual-probe heat-pulse soil water | differential | ×2 temperature-contact | NEW: soil-water-volumetric | θ = (C − C_dry)/4.18 where C = q/(e·π·r²·ΔT_max) in MJ·m⁻³·K⁻¹, q = pulse energy per metre of heater wire [J/m]; heat pulse from a resistor wire |
| Sky thermometer cloud detector | differential | temperature-remote + temperature-contact | route: sky-clear | Clear sky reads 25–45°C BELOW air temp in thermal IR; overcast reads within ~5°C |
| Road ice predictor | differential | temperature-remote + dew-point | NEW: black-ice-risk | Alarm when T_road ≤ 1°C AND T_road ≤ T_dew + 0.5°C (frost deposition condition) |
| Filter-health differential barometer | differential | ×2 pressure-absolute | route: filter-clogged | ΔP = P_upstream − P_downstream; alarm at 2–3× the clean-filter baseline |
| Compost activity meter | differential | ×2 temperature-contact | route: compost-active | ΔT = T_core − T_ambient; active thermophilic compost holds ΔT ≈ 20–40°C |
| Bearing temperature-rise monitor | differential | ×2 temperature-contact | route: bearing-failing | ΔT = T_bearing − T_ambient; trend of ΔT at constant load is the health signal |
| Live air-density computer | compensation | pressure-absolute + temperature-contact + humidity-relative | NEW: air-density | ρ = (P_dry·M_d + P_vap·M_v)/(R·T); P_vap from RH × saturation pressure (Magnus) |
| Feels-like temperature station | compensation | temperature-contact + humidity-relative + wind-speed | NEW: feels-like-temperature | T<10°C: wind chill (Environment Canada 2001 formula); T>27°C and RH>40%: heat index (Rothfusz regression, invalid below that); between: dry bulb |
| Evapotranspiration (irrigation truth) | compensation | temperature-contact + humidity-relative + wind-speed + solar-irradiance | NEW: evapotranspiration | FAO-56 Penman-Monteith ET₀ (or Hargreaves ET₀ = 0.0023·Ra·√ΔT·(T+17.8) when only temperature is available) |
| Pressure-corrected cosmic-ray telescope | compensation | ionising-radiation + pressure-absolute | route: cosmic-flux | Corrected rate = raw rate × e^(β·(P−P₀)), β ≈ 0.2%/hPa for muons |
| Temperature-honest pH | compensation | ph + temperature-contact | route: water-ph | Nernst slope = −59.16 mV/pH × (T/298.15); correct slope, then report at 25°C |
| Temperature-corrected soil moisture | compensation | dielectric-constant + temperature-contact | route: plant-thirsty | Correct raw counts by the probe's measured temperature coefficient (typ. 0.1–0.3%/°C), learned from a 24 h constant-moisture log |
| Temperature-honest snow depth | compensation | distance-point + temperature-contact | route: snow-depth | depth = mount_height − range × c(T)/c₀, with c(T) = 331.3 + 0.606·T m/s |
| Solar performance-ratio meter | compensation | solar-irradiance + current-dc + voltage | route: solar-performance | PR = P_actual / (G/1000 × P_rated); healthy arrays hold PR 0.75–0.85 |
| Fire coincidence detector | cross-validation | smoke-present + co-present | route: fire-present | Alarm = smoke AND (CO rising ≥ 5 ppm over baseline within 10 min); either alone = advisory |
| Two-physics presence verifier | cross-validation | ×2 someone-present | NEW: presence-verified | Verified = both channels TRUE within a 5 s window; disagreement = log + keep watching |
| Two-channel breathing sentinel | cross-validation | respiration + sound-pressure | route: breathing-stopped | Escalate when radar respiration amplitude < threshold AND breath-band audio (0.1–1 Hz envelope — infants breathe 0.5–1 Hz, adults 0.2–0.33 Hz) silent for > 20 s |
| ENF recording authenticator | cross-validation | sound-pressure + voltage | NEW: recording-authenticity | Extract 50 Hz hum drift from audio; correlate against your logged grid-frequency history; genuine timestamps correlate r > 0.9 over minutes |
| Occupancy-gated leak detector | context-gating | flow-liquid + someone-present | route: water-leak | Alarm when flow > 0 sustained > 10 min AND nobody-present > 30 min |
| Stove-left-on sentinel | context-gating | temperature-remote + someone-present | route: stove-left-on | Escalate when T_stove > 120°C AND kitchen empty > 15 min (advise), > 30 min (alarm) |
| Window-state inferencer | context-gating | temperature-contact + co2-concentration | NEW: window-open-state | Open = CO2 decay rate jumps > 3× baseline ACH, confirmed by an indoor temperature slew when indoor–outdoor ΔT exists (mild weather: no slew — trust the CO2 channel alone) |
| Badge-in attribution gate | context-gating | identity-token + occupancy-signal | route: who-is-it | Attribute presence to token holder when RFID event and presence onset agree within 30 s; decay attribution when presence lapses |
| Empty-room energy auditor | context-gating | power-now + someone-present | NEW: energy-waste-unoccupied | Waste = ∫ P dt while unoccupied, per room per week; rank rooms by wasted kWh |
| CO2-decay ventilation meter | temporal | co2-concentration | NEW: air-changes-hour | ACH = ln((C₁−C_out)/(C₂−C_out)) / Δt[h], C_out ≈ 420 ppm, after the room empties |
| CO2 tape-measure | temporal | co2-concentration | NEW: room-volume-estimate | V = N·q / (d[CO2]/dt) with q ≈ 18 L/h CO2 per seated adult, sealed room, short window |
| Grid-stress seismograph | temporal | voltage | NEW: grid-stress | f from zero-crossing timestamps; Δf from 50.000 Hz ∝ generation−load imbalance; df/dt during events = inertia signal |
| Motor-start health tracker | temporal | current-ac | NEW: inrush-health | Trend inrush peak, spin-up time, and start count per day; rising start-time at constant voltage = mechanical or capacitor degradation |
| Building thermal time-constant | temporal | ×2 temperature-contact | NEW: thermal-time-constant | τ from exponential fit of indoor T decay after heating stops (calm night); T(t) = T_out + (T₀−T_out)·e^(−t/τ) |
| Appliance fingerprint disaggregator | temporal | current-ac | route: which-appliance | Event detection on ΔI_rms edges; classify by (ΔI_rms, inrush shape, harmonic content, duration) — the full P/Q signature plane needs the voltage channel too |
| Thermal-effusivity liquid identifier | active-probe | temperature-contact | route: material-type | Pulse a co-located resistor; ΔT(t) of the sensor tracks 1/e = 1/√(kρc); water e≈1580, oil ≈500, air ≈5.5 W·s^½/m²K |
| Path-averaged sonic thermometer | active-probe | ultrasound | NEW: path-averaged-temperature | T = ((d/t_flight)² /400 approx from c² = 403·T[K]; practically T[°C] = (d/t − 331.3)/0.606 at fixed d |
| Helmholtz through-wall fill gauge | active-probe | sound-pressure | route: container-fullness | f = (c/2π)·√(A/(V·L)): resonant frequency rises as headspace V shrinks. Chirp and find the peak — needs any small speaker or buzzer as the source (glue hardware, not a sensing capability). |
| Acoustic direction finder | triangulation | ×2 sound-pressure | NEW: sound-direction | θ = arcsin(Δt·343/d) from the arrival-time difference across a known baseline d |
| Two-beam speed trap | triangulation | ×2 proximity | route: vehicle-speed | v = d/Δt between two beam-break timestamps a known distance apart; ±1% with µs timestamps |
| Barometric door locator | triangulation | ×3 pressure-absolute | NEW: which-door-opened | A door swing is a ~0.3–3 Pa transient; arrival order + amplitude ratio across 3 synced nodes localises the source |
| Acoustic pipe-leak correlator | triangulation | ×2 sound-structural | NEW: leak-location | Leak position from cross-correlation lag: x = (L − v·Δt)/2, v ≈ 1200–1400 m/s in water-filled metal pipe |
| Space-utilisation truth map | fleet | ×3 occupancy-signal | NEW: space-utilisation-map | Per-zone occupied-hours histograms; utilisation = occupied / available hours per zone per week |
| Thermal microclimate mapper | fleet | ×3 temperature-contact | NEW: thermal-map | Simultaneous ΔT across ≥3 fixed points; persistent cold spots + dew-point proximity = condensation/draught candidates |
| Fast-and-absolute altimeter | complementary | pressure-absolute + position-global | route: how-high | Complementary filter: alt = LP(GPS_alt) + HP(baro_alt); baro gives cm-resolution dynamics, GPS pins the absolute and cancels weather drift |
| Contactless sleep-stage estimator | complementary | respiration + acceleration | route: sleep-stage-proxy | Actigraphy (movement bouts) × respiration regularity: still+regular ≈ deep, still+variable ≈ REM, moving ≈ light/wake |
| Personal exposure dosimeter | complementary | particulate-mass + position-global | NEW: personal-exposure-dose | Dose = ∫ C(t)·V̇ dt segmented by GPS trace; map µg-minutes to street segments |
| Power-factor and quality monitor | complementary | current-ac + voltage | route: power-quality | PF = P/(V_rms·I_rms); THD from harmonic decomposition; sag/swell from cycle-by-cycle V_rms |
| Hive vital-signs fusion | complementary | weight + sound-structural + temperature-contact | route: hive-state | Weight slope = forage/consumption; acoustic 200–500 Hz band = swarm prep; brood T held 34–36°C = queenright |
| Radiative frost forecaster | context-gating | temperature-contact + air-velocity + dew-point + sky-clear | route: frost-tonight | Frost when: sky-facing radiative loss (clear night) + wind < 2 m/s (no mixing) + T approaching 0 with dew point < 0 (deposition not dew) |
| Whole-building heat-loss coefficient | differential | energy-accumulated + ×2 temperature-contact | NEW: building-heat-loss | UA[W/K] = heating power ÷ (T_in − T_out), fitted over steady calm nights |
| Passive gait-speed corridor | temporal | through-wall-motion + distance-point | route: gait-quality | Walking speed from per-target range-rate (LD2450/RD-03D-class trackers — binary presence radars cannot); declining weekly median gait speed is a validated frailty predictor |
| Per-use appliance cost meter | context-gating | energy-accumulated + cycle-complete | NEW: cost-per-use | Cost/use = (E_end − E_start over one detected cycle) × tariff; distribution over cycles reveals degradation |
| Radon early-warning proxy | context-gating | pressure-absolute + air-changes-hour | NEW: radon-risk-rising | Risk rising when P falling > 3 hPa/6 h (soil-gas pressure gradient reverses) AND measured ACH < 0.4 |

## What a fixed budget buys

| Budget | Parts | Outcomes | % | Spent |
|--:|--:|--:|--:|--:|
| $10 | 11 | 63 | 42% | $9.9 |
| $25 | 18 | 88 | 58% | $24.4 |
| $50 | 25 | 107 | 71% | $48.4 |
| $100 | 35 | 127 | 84% | $97.9 |
| $250 | 50 | 143 | 95% | $233.9 |

## Single-domain kits

| Domain | Outcomes | Sensors | Cost | Kit |
|---|--:|--:|--:|---|
| Body & health | 16 | 8 | $69 | MPU-6050 6-axis IMU ($2) · MAX30102 pulse oximeter ($6) · Thermistor airflow (nasal) kit ($3) · FSR402 force resistor ($7) · MLX90614 IR thermometer ($8) · Flex sensor 2.2" ($8) · GSR / EDA sensor ($10) · BioAmp EXG Pill ($25) |
| Machine health | 15 | 8 | $62 | Piezo contact mic / disc ($0.5) · A3144 / SS49E Hall switches ($0.4) · NTC thermistor 10k ($0.3) · MPU-6050 6-axis IMU ($2) · RV4145A ground-fault / residual current detector ($2) · XGZP6897D low-range diff pressure ($6) · Ultrasonic mic experiments ($6) · IIS3DWB wideband vibration sensor ($45) |
| Human presence | 14 | 7 | $22 | HC-SR501 PIR motion ($1.5) · Wi-Fi CSI sensing (the router IS the sensor) ($0) · Reed switch ($0.5) · ESP32 internal sensors (free!) ($0) · LD2410 mmWave presence ($5) · Azoteq IQS7211 / IQS263 proximity + touch ($6) · RD-03D 24GHz multi-target tracking radar ($9) |
| Air & environment | 14 | 8 | $254 | MQ-2 smoke/LPG gas ($2) · AHT20 temp/humidity ($2) · MQ-135 air quality ($2.5) · MQ-7 carbon monoxide ($2.5) · Ikea VINDRIKTNING hack ($13) · ZE08-CH2O formaldehyde ($22) · MQ-131 ozone ($30) · RD200 radon sensor ($180) |
| Objects & assets | 13 | 7 | $15 | Reed switch ($0.5) · SW-420 vibration switch ($1) · NTC thermistor 10k ($0.3) · RC522 RFID reader ($2) · HC-SR04 ultrasonic ($1.5) · TCS3200 frequency-output colour sensor ($4) · PN532 NFC controller ($6) |
| Water | 12 | 9 | $152 | Reed switch ($0.5) · NTC thermistor 10k ($0.3) · Piezo contact mic / disc ($0.5) · ADS1115 16-bit ADC (the analog fixer) ($3) · DS18B20 digital temp probe ($2.5) · TCS3200 frequency-output colour sensor ($4) · Vertical float level switch (reed) ($4) · AS7331 spectral UV ($27.5) · ORP (redox) probe ($110) |
| Weather & outdoors | 11 | 8 | $35 | BMP280 budget barometer ($1.5) · NTC thermistor 10k ($0.3) · A3144 / SS49E Hall switches ($0.4) · Reed switch ($0.5) · AHT20 temp/humidity ($2) · US-100 ultrasonic w/ temp comp ($4) · ML8511 / VEML6075 UV outdoor ($6) · AS3935 lightning detector ($20) |
| Plants & soil | 11 | 8 | $40 | Photoresistor (LDR) ($0.2) · Capacitive soil moisture v2 ($2) · DS18B20 digital temp probe ($2.5) · DHT22 / AM2302 ($4) · TCS3200 frequency-output colour sensor ($4) · HX711 + load cell ($5) · Gypsum soil moisture block ($10) · EC / TDS sensor ($12) |
| Energy | 10 | 3 | $7 | BL0940 calibration-free mains metering IC ($1.5) · INA219 current/power monitor ($2.5) · ZMPT101B voltage sensor ($3) |
| Navigation & space | 10 | 6 | $23 | BMP280 budget barometer ($1.5) · MPU-6050 6-axis IMU ($2) · HC-SR04 ultrasonic ($1.5) · QMC5883L compass ($2) · NEO-6M GPS ($8) · Bat/dolphin: 40kHz ranging array ($8) |
| Security & safety | 9 | 5 | $16 | Piezo contact mic / disc ($0.5) · IR flame detector (flicker) ($2) · Photoelectric beam sensor E18-D80NK ($3) · RC522 RFID reader ($2) · NEO-6M GPS ($8) |
| Invisible worlds | 9 | 8 | $90 | QMC5883L compass ($2) · Wi-Fi CSI sensing (the router IS the sensor) ($0) · BPW34 PIN photodiode ($1) · PIN photodiode radiation detector ($2) · SI4432/CC1101 sub-GHz sniffer ($4) · Ultrasonic mic experiments ($6) · Atmospheric electricity (field mill lite) ($15) · SiPM photodetector module ($60) |
| Materials & chemistry | 7 | 6 | $30 | Capacitive soil moisture v2 ($2) · AHT20 temp/humidity ($2) · DS18B20 digital temp probe ($2.5) · TCS34725 RGB color ($7) · Capacitive proximity switch M18 ($7) · Color-changing material readers ($10) |

## What a constraint costs you, in outcomes

| Constraint | Eligible | Reachable | % | Kit cost | Lost entirely |
|---|--:|--:|--:|--:|---|
| 🔒 No privacy footprint | 350 | 150/151 | 99% | 63 parts, $903 | Did they blink or move their eyes? |
| 🔋 Battery, µA-class | 109 | 120/151 | 79% | 42 parts, $324 | Is radon accumulating? · Is there a flammable gas leak? · How polluted is the air right now? · Is new furniture or flooring off-gassing? · Is something emitting ozone? · Is there carbon monoxide? |
| 🚫 Never touches the subject | 236 | 131/151 | 87% | 55 parts, $852 | Is this person's arousal or stress rising? · What is the blood oxygen saturation? · How is this person walking? · Did they blink or move their eyes? · Are they likely dehydrated? · How much have they moved today? |
| 💵 Nothing over $5 | 75 | 110/151 | 73% | 34 parts, $73 | Is radon accumulating? · How polluted is the air right now? · Is new furniture or flooring off-gassing? · Is something emitting ozone? · What is the heart rate? · Is this person's arousal or stress rising? |
| 🧑‍🔧 Beginner-buildable | 216 | 139/151 | 92% | 48 parts, $346 | Is radon accumulating? · Did they blink or move their eyes? · What is making noise above human hearing? · Which radioactive isotope is this? · Is the atmosphere electrically charged? · What is transmitting nearby, and how strongly? |
| 🌦 Survives outdoors | 173 | 133/151 | 88% | 49 parts, $1073 | Is radon accumulating? · Is new furniture or flooring off-gassing? · What is the heart rate? · Did they blink or move their eyes? · Which muscle is working, and how hard? · Are they likely dehydrated? |

## Every outcome, and what buys it

| Domain | You want to know… | Routes | Rarity | Cheapest | No-contact | Privacy-safe |
|---|---|--:|---|---|---|---|
| Air & environment | Is ventilation actually working? | 36 |  | MQ-135 air quality ($2.5) | MQ-135 air quality ($2.5) | MQ-135 air quality ($2.5) |
| Air & environment | Is someone cooking? | 30 |  | MQ-2 smoke/LPG gas ($2) | MQ-2 smoke/LPG gas ($2) | MQ-2 smoke/LPG gas ($2) |
| Air & environment | Is this room stuffy — does it need fresh air? | 24 |  | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) |
| Air & environment | Did something start off-gassing or smelling? | 21 |  | MQ-2 smoke/LPG gas ($2) | MQ-2 smoke/LPG gas ($2) | MQ-2 smoke/LPG gas ($2) |
| Air & environment | Is this surface going to grow mould? | 19 |  | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) |
| Air & environment | Is there a flammable gas leak? | 17 |  | MQ-2 smoke/LPG gas ($2) | MQ-2 smoke/LPG gas ($2) | MQ-2 smoke/LPG gas ($2) |
| Air & environment | What does this smell like — which known smell is it? | 14 |  | MQ-3 alcohol sensor ($2.5) | MQ-3 alcohol sensor ($2.5) | MQ-3 alcohol sensor ($2.5) |
| Air & environment | Is there smoke? | 13 |  | MQ-2 smoke/LPG gas ($2) | MQ-2 smoke/LPG gas ($2) | MQ-2 smoke/LPG gas ($2) |
| Air & environment | How polluted is the air right now? | 12 |  | Ikea VINDRIKTNING hack ($13) | Ikea VINDRIKTNING hack ($13) | Ikea VINDRIKTNING hack ($13) |
| Air & environment | Is the air dry enough to damage wood, skin or instruments? | 11 |  | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) |
| Air & environment | Is there carbon monoxide? | 4 |  | MQ-7 carbon monoxide ($2.5) | MQ-7 carbon monoxide ($2.5) | MQ-7 carbon monoxide ($2.5) |
| Air & environment | Is something emitting ozone? | 3 | rare | MQ-131 ozone ($30) | MQ-131 ozone ($30) | MQ-131 ozone ($30) |
| Air & environment | Is new furniture or flooring off-gassing? | 2 | rare | ZE08-CH2O formaldehyde ($22) | ZE08-CH2O formaldehyde ($22) | ZE08-CH2O formaldehyde ($22) |
| Air & environment | Is radon accumulating? | 1 | SOLE ROUTE | RD200 radon sensor ($180) | RD200 radon sensor ($180) | RD200 radon sensor ($180) |
| Body & health | What posture is this body in? | 26 |  | MPU-6050 6-axis IMU ($2) | VL53L5CX 8x8 ToF array ($20) | MPU-6050 6-axis IMU ($2) |
| Body & health | How fast are they breathing? | 23 |  | Wi-Fi CSI sensing (the router IS the sensor) ($0) | DFRobot Gravity mmWave presence radar ($22) | Flex sensor 2.2" ($8) |
| Body & health | What is the heart rate? | 16 |  | Pulse sensor (PPG classic) ($5) | Seeed MR60BHA2 vital-sign radar ($25) | Conductive fabric and tape electrodes ($12) |
| Body & health | How is this person walking? | 16 |  | MPU-6050 6-axis IMU ($2) | — none | MPU-6050 6-axis IMU ($2) |
| Body & health | How much have they moved today? | 14 |  | MPU-6050 6-axis IMU ($2) | — none | MPU-6050 6-axis IMU ($2) |
| Body & health | Is this person's arousal or stress rising? | 12 |  | Pulse sensor (PPG classic) ($5) | — none | EDA done properly - constant-voltage skin conductance ($8) |
| Body & health | Is there a tremor, and at what frequency? | 11 |  | MPU-6050 6-axis IMU ($2) | Time-of-flight gesture radar 60GHz ($110) | MPU-6050 6-axis IMU ($2) |
| Body & health | What sleep stage is this, roughly? | 11 |  | Thermistor airflow (nasal) kit ($3) | DFRobot Gravity mmWave presence radar ($22) | Velostat pressure sheets ($5) |
| Body & health | How stressed or recovered is this body? | 10 |  | Pulse sensor (PPG classic) ($5) | — none | AFE4490 transmissive pulse-oximetry front end ($55) |
| Body & health | What angle is this joint at, through its range? | 10 |  | Flex sensor 2.2" ($8) | AS5048A 14-bit angle ($12) | Flex sensor 2.2" ($8) |
| Body & health | Which muscle is working, and how hard? | 7 |  | FSR402 force resistor ($7) | — none | FSR402 force resistor ($7) |
| Body & health | Has breathing become irregular or stopped? | 6 |  | Thermistor airflow (nasal) kit ($3) | Seeed MR60BHA2 vital-sign radar ($25) | Conductive rubber stretch cord ($10) |
| Body & health | Is body temperature drifting — fever, ovulation, heat stress? | 6 |  | MLX90614 IR thermometer ($8) | MLX90614 IR thermometer ($8) | MLX90614 IR thermometer ($8) |
| Body & health | What is the blood oxygen saturation? | 4 |  | MAX30102 pulse oximeter ($6) | — none | AFE4490 transmissive pulse-oximetry front end ($55) |
| Body & health | Did they blink or move their eyes? | 3 | rare | BioAmp EXG Pill ($25) | — none | — none |
| Body & health | Are they likely dehydrated? | 2 | rare | GSR / EDA sensor ($10) | — none | AD5941 bioimpedance / EIS analyser ($95) |
| Energy | Did someone leave it switched on? | 30 |  | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) |
| Energy | How much power is being used right now? | 18 |  | BL0940 calibration-free mains metering IC ($1.5) | ACS712 Hall current ($3) | BL0940 calibration-free mains metering IC ($1.5) |
| Energy | Which appliance just turned on? | 16 |  | BL0940 calibration-free mains metering IC ($1.5) | INMP441 I2S MEMS mic ($3) | BL0940 calibration-free mains metering IC ($1.5) |
| Energy | Will this node survive on its battery until spring? | 11 |  | INA219 current/power monitor ($2.5) | MAX44009 ultra-low-power lux ($3) | INA219 current/power monitor ($2.5) |
| Energy | How much charge is left? | 10 |  | INA219 current/power monitor ($2.5) | — none | INA219 current/power monitor ($2.5) |
| Energy | Is the solar array performing as it should? | 9 |  | INA219 current/power monitor ($2.5) | Pyranometer (solar irradiance) ($60) | INA219 current/power monitor ($2.5) |
| Energy | What is draining power while doing nothing? | 8 |  | BL0940 calibration-free mains metering IC ($1.5) | SCT-013 CT clamp ($10) | BL0940 calibration-free mains metering IC ($1.5) |
| Energy | What did that actually cost to run? | 7 |  | BL0940 calibration-free mains metering IC ($1.5) | — none | BL0940 calibration-free mains metering IC ($1.5) |
| Energy | Is this battery degrading? | 5 |  | INA219 current/power monitor ($2.5) | MQ-8 hydrogen sensor ($4) | INA219 current/power monitor ($2.5) |
| Energy | Is the supply voltage clean and stable? | 5 |  | ZMPT101B voltage sensor ($3) | — none | ZMPT101B voltage sensor ($3) |
| Human presence | Is anyone here? | 97 |  | ESP32 native touch pins ($0) | TTP223 single touch ($0.5) | NTC thermistor 10k ($0.3) |
| Human presence | Did something cross this line? | 38 |  | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) |
| Human presence | How long has this desk/room/seat been in use? | 33 |  | HC-SR501 PIR motion ($1.5) | HC-SR501 PIR motion ($1.5) | HC-SR501 PIR motion ($1.5) |
| Human presence | How many people are in this space? | 32 |  | Wi-Fi CSI sensing (the router IS the sensor) ($0) | RD-03D 24GHz multi-target tracking radar ($9) | RD-03D 24GHz multi-target tracking radar ($9) |
| Human presence | Whereabouts in the room are they? | 27 |  | LD2410 mmWave presence ($5) | LD2410 mmWave presence ($5) | LD2410 mmWave presence ($5) |
| Human presence | Did they come in, or go out? | 24 |  | Reed switch ($0.5) | Reed switch ($0.5) | Reed switch ($0.5) |
| Human presence | Did someone fall? | 18 |  | Wi-Fi CSI sensing (the router IS the sensor) ($0) | VL53L5CX 8x8 ToF array ($20) | Velostat pressure sheets ($5) |
| Human presence | Which specific person is this? | 14 |  | ESP32 internal sensors (free!) ($0) | nRF52 BLE beacon tag ($8) | ESP32 internal sensors (free!) ($0) |
| Human presence | Is someone still here, sitting perfectly still? | 12 |  | LD2410 mmWave presence ($5) | LD2410 mmWave presence ($5) | LD2410 mmWave presence ($5) |
| Human presence | Has nobody moved for worryingly long? | 12 |  | HC-SR501 PIR motion ($1.5) | HC-SR501 PIR motion ($1.5) | HC-SR501 PIR motion ($1.5) |
| Human presence | Are they asleep, and how well? | 9 |  | INMP441 I2S MEMS mic ($3) | INMP441 I2S MEMS mic ($3) | VEML7700 high-accuracy lux ($5) |
| Human presence | Has this person's daily routine changed? | 7 |  | HC-SR501 PIR motion ($1.5) | HC-SR501 PIR motion ($1.5) | HC-SR501 PIR motion ($1.5) |
| Human presence | How many are waiting, and for how long? | 5 |  | RD-03D 24GHz multi-target tracking radar ($9) | RD-03D 24GHz multi-target tracking radar ($9) | RD-03D 24GHz multi-target tracking radar ($9) |
| Human presence | Is someone actually looking at this? | 2 | rare | Azoteq IQS7211 / IQS263 proximity + touch ($6) | Azoteq IQS7211 / IQS263 proximity + touch ($6) | Azoteq IQS7211 / IQS263 proximity + touch ($6) |
| Invisible worlds | Is there ferrous metal or a field distortion here? | 9 |  | QMC5883L compass ($2) | QMC5883L compass ($2) | QMC5883L compass ($2) |
| Invisible worlds | Where is the wiring or metal inside this wall? | 7 |  | QMC5883L compass ($2) | QMC5883L compass ($2) | QMC5883L compass ($2) |
| Invisible worlds | Is something moving on the other side of that wall? | 7 |  | Wi-Fi CSI sensing (the router IS the sensor) ($0) | RCWL-0516 doppler radar ($1.2) | RCWL-0516 doppler radar ($1.2) |
| Invisible worlds | How much radiation is here? | 6 |  | BPW34 PIN photodiode ($1) | BPW34 PIN photodiode ($1) | BPW34 PIN photodiode ($1) |
| Invisible worlds | What is transmitting nearby, and how strongly? | 6 |  | SI4432/CC1101 sub-GHz sniffer ($4) | SI4432/CC1101 sub-GHz sniffer ($4) | SX1262 sub-GHz transceiver ($8) |
| Invisible worlds | How many cosmic rays are passing through? | 4 |  | PIN photodiode radiation detector ($2) | Geiger counter kit ($25) | PIN photodiode radiation detector ($2) |
| Invisible worlds | Which radioactive isotope is this? | 2 | rare | SiPM photodetector module ($60) | — none | SiPM photodetector module ($60) |
| Invisible worlds | What is making noise above human hearing? | 2 | rare | Ultrasonic mic experiments ($6) | Ultrasonic mic experiments ($6) | Acoustic emission (ultrasonic contact) ($10) |
| Invisible worlds | Is the atmosphere electrically charged? | 1 | SOLE ROUTE | Atmospheric electricity (field mill lite) ($15) | Atmospheric electricity (field mill lite) ($15) | Atmospheric electricity (field mill lite) ($15) |
| Machine health | Has this drifted from how it behaved when new? | 88 |  | NTC thermistor 10k ($0.3) | BMP280 budget barometer ($1.5) | NTC thermistor 10k ($0.3) |
| Machine health | Is it on? | 60 |  | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) |
| Machine health | Is it idle, loaded, or jammed? | 54 |  | Piezo contact mic / disc ($0.5) | KY-037/038 sound modules ($1) | KY-037/038 sound modules ($1) |
| Machine health | Has the cycle finished? | 40 |  | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) |
| Machine health | Is something running hotter than it should? | 33 |  | ESP32 internal sensors (free!) ($0) | IR flame detector (flicker) ($2) | NTC thermistor 10k ($0.3) |
| Machine health | How much is this machine actually used? | 21 |  | Piezo contact mic / disc ($0.5) | ACS712 Hall current ($3) | SW-420 vibration switch ($1) |
| Machine health | Is a bearing starting to fail? | 20 |  | Piezo contact mic / disc ($0.5) | INMP441 I2S MEMS mic ($3) | ADXL345 accelerometer ($3) |
| Machine health | Is it drawing an abnormal amount of power? | 18 |  | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) |
| Machine health | How fast is it turning? | 17 |  | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) |
| Machine health | Is it out of balance or misaligned? | 16 |  | MPU-6050 6-axis IMU ($2) | — none | MPU-6050 6-axis IMU ($2) |
| Machine health | Is compressed air leaking, and where? | 16 |  | Piezo contact mic / disc ($0.5) | INMP441 I2S MEMS mic ($3) | 40kHz ultrasonic transducer pair ($3) |
| Machine health | Is the filter blocked? | 14 |  | XGZP6897D low-range diff pressure ($6) | XGZP6897D low-range diff pressure ($6) | XGZP6897D low-range diff pressure ($6) |
| Machine health | Is there electrical arcing or partial discharge? | 7 |  | RV4145A ground-fault / residual current detector ($2) | 40kHz ultrasonic transducer pair ($3) | RV4145A ground-fault / residual current detector ($2) |
| Machine health | Is lubrication breaking down? | 7 |  | Ultrasonic mic experiments ($6) | Ultrasonic mic experiments ($6) | Acoustic emission (ultrasonic contact) ($10) |
| Machine health | Is the belt or coupling slipping? | 1 | SOLE ROUTE | IIS3DWB wideband vibration sensor ($45) | — none | IIS3DWB wideband vibration sensor ($45) |
| Materials & chemistry | Has this been contaminated? | 28 |  | Color-changing material readers ($10) | Color-changing material readers ($10) | Color-changing material readers ($10) |
| Materials & chemistry | What material is this? | 12 |  | Capacitive proximity switch M18 ($7) | Capacitive proximity switch M18 ($7) | Capacitive proximity switch M18 ($7) |
| Materials & chemistry | Does this colour match the reference? | 12 |  | TCS3200 frequency-output colour sensor ($4) | TCS3200 frequency-output colour sensor ($4) | TCS3200 frequency-output colour sensor ($4) |
| Materials & chemistry | How concentrated is this solution? | 12 |  | TCS34725 RGB color ($7) | TCS34725 RGB color ($7) | TCS34725 RGB color ($7) |
| Materials & chemistry | Has the paint, resin or glue finished curing? | 12 |  | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) |
| Materials & chemistry | How wet is this material? | 11 |  | Capacitive soil moisture v2 ($2) | Capacitive liquid/force FDC1004 ($9) | Capacitive soil moisture v2 ($2) |
| Materials & chemistry | Is this food still good? | 11 |  | DS18B20 digital temp probe ($2.5) | MQ-3 alcohol sensor ($2.5) | DS18B20 digital temp probe ($2.5) |
| Navigation & space | How fast am I moving? | 24 |  | MS5611 high-res altimeter ($6) | MS5611 high-res altimeter ($6) | MS5611 high-res altimeter ($6) |
| Navigation & space | Has this structure shifted or tilted since last time? | 24 |  | MPU-6050 6-axis IMU ($2) | LDC1612 inductive sensing ($9) | MPU-6050 6-axis IMU ($2) |
| Navigation & space | Is there something in the way? | 22 |  | HC-SR04 ultrasonic ($1.5) | HC-SR04 ultrasonic ($1.5) | HC-SR04 ultrasonic ($1.5) |
| Navigation & space | Which way am I pointing? | 21 |  | QMC5883L compass ($2) | QMC5883L compass ($2) | QMC5883L compass ($2) |
| Navigation & space | Am I back at the exact same place? | 20 |  | BMP280 budget barometer ($1.5) | BMP280 budget barometer ($1.5) | BMP280 budget barometer ($1.5) |
| Navigation & space | How far have I gone? | 18 |  | Linear potentiometer / softpot ($6) | NEO-6M GPS ($8) | Linear potentiometer / softpot ($6) |
| Navigation & space | Is this level, and by how much is it off? | 18 |  | SW-520D ball tilt switch ($0.5) | AS5600 magnetic angle ($3) | SW-520D ball tilt switch ($0.5) |
| Navigation & space | Where am I on Earth? | 12 |  | NEO-6M GPS ($8) | NEO-6M GPS ($8) | GPS PPS time source ($10) |
| Navigation & space | What altitude or floor am I on? | 12 |  | BMP280 budget barometer ($1.5) | BMP280 budget barometer ($1.5) | BMP280 budget barometer ($1.5) |
| Navigation & space | What is the shape of the space around me? | 6 |  | Bat/dolphin: 40kHz ranging array ($8) | Bat/dolphin: 40kHz ranging array ($8) | Bat/dolphin: 40kHz ranging array ($8) |
| Objects & assets | Is the thing there? | 69 |  | ESP32 native touch pins ($0) | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) |
| Objects & assets | Has it been moved or disturbed? | 48 |  | ESP32 native touch pins ($0) | RCWL-0516 doppler radar ($1.2) | SW-520D ball tilt switch ($0.5) |
| Objects & assets | How many went past? | 40 |  | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) |
| Objects & assets | How full is it? | 40 |  | Reed switch ($0.5) | Reed switch ($0.5) | Reed switch ($0.5) |
| Objects & assets | Is it open or closed? | 37 |  | ESP32 native touch pins ($0) | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) |
| Objects & assets | Has someone interfered with it? | 33 |  | ESP32 native touch pins ($0) | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) |
| Objects & assets | How much is left, and how long until it runs out? | 24 |  | HC-SR04 ultrasonic ($1.5) | HC-SR04 ultrasonic ($1.5) | HC-SR04 ultrasonic ($1.5) |
| Objects & assets | Where is this thing right now? | 22 |  | RC522 RFID reader ($2) | Wi-Fi and magnetic fingerprint positioning ($5) | Wi-Fi and magnetic fingerprint positioning ($5) |
| Objects & assets | How hot is that surface? | 20 |  | NTC thermistor 10k ($0.3) | MLX90614 IR thermometer ($8) | NTC thermistor 10k ($0.3) |
| Objects & assets | Which specific object is this? | 18 |  | RC522 RFID reader ($2) | NTAG I2C Plus 2K dual-interface tag ($6) | Embroidered / fabric antenna ($10) |
| Objects & assets | Was it dropped, and how hard? | 16 |  | Piezo contact mic / disc ($0.5) | — none | SW-420 vibration switch ($1) |
| Objects & assets | Is this authentic or counterfeit? | 12 |  | PN532 NFC controller ($6) | NTAG I2C Plus 2K dual-interface tag ($6) | ATECC608B secure element ($6) |
| Objects & assets | What is this made of? | 7 |  | TCS3200 frequency-output colour sensor ($4) | TCS3200 frequency-output colour sensor ($4) | TCS3200 frequency-output colour sensor ($4) |
| Plants & soil | Are the animals comfortable and behaving normally? | 18 |  | MQ-135 air quality ($2.5) | MQ-135 air quality ($2.5) | MQ-135 air quality ($2.5) |
| Plants & soil | How fast is it growing? | 17 |  | Capacitive soil moisture v2 ($2) | OV2640 camera (ESP32-CAM) ($8) | Capacitive soil moisture v2 ($2) |
| Plants & soil | Has this plant had enough light today? | 17 |  | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) |
| Plants & soil | Does this plant need water? | 16 |  | Capacitive soil moisture v2 ($2) | AS7263 NIR spectral ($27) | Capacitive soil moisture v2 ($2) |
| Plants & soil | Is the compost heating properly — or dangerously? | 14 |  | DS18B20 digital temp probe ($2.5) | DHT22 / AM2302 ($4) | DS18B20 digital temp probe ($2.5) |
| Plants & soil | Are conditions right for fungal disease? | 13 |  | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) |
| Plants & soil | What is the nutrient status of this soil? | 8 |  | EC / TDS sensor ($12) | — none | EC / TDS sensor ($12) |
| Plants & soil | Is it ripe? | 7 |  | TCS3200 frequency-output colour sensor ($4) | TCS3200 frequency-output colour sensor ($4) | TCS3200 frequency-output colour sensor ($4) |
| Plants & soil | Is the soil warm enough to sow? | 6 |  | DS18B20 digital temp probe ($2.5) | — none | DS18B20 digital temp probe ($2.5) |
| Plants & soil | How hard must roots work to get water? | 4 |  | Gypsum soil moisture block ($10) | — none | Gypsum soil moisture block ($10) |
| Plants & soil | What is the beehive doing? | 3 | rare | HX711 + load cell ($5) | — none | HX711 + load cell ($5) |
| Security & safety | Has someone entered who shouldn't have? | 27 |  | Reed switch ($0.5) | Reed switch ($0.5) | Reed switch ($0.5) |
| Security & safety | Is a vehicle arriving? | 15 |  | QMC5883L compass ($2) | QMC5883L compass ($2) | QMC5883L compass ($2) |
| Security & safety | Did something sound wrong? | 13 |  | Piezo contact mic / disc ($0.5) | KY-037/038 sound modules ($1) | KY-037/038 sound modules ($1) |
| Security & safety | Is this person allowed to operate this? | 12 |  | RC522 RFID reader ($2) | NTAG I2C Plus 2K dual-interface tag ($6) | ATECC608B secure element ($6) |
| Security & safety | Did glass break? | 9 |  | Piezo contact mic / disc ($0.5) | KY-037/038 sound modules ($1) | KY-037/038 sound modules ($1) |
| Security & safety | Was the boundary crossed, and where along it? | 9 |  | Photoelectric beam sensor E18-D80NK ($3) | Photoelectric beam sensor E18-D80NK ($3) | Photoelectric beam sensor E18-D80NK ($3) |
| Security & safety | Is there a flame? | 8 |  | IR flame detector (flicker) ($2) | IR flame detector (flicker) ($2) | IR flame detector (flicker) ($2) |
| Security & safety | Was the hob left on with nobody there? | 8 |  | MQ-2 smoke/LPG gas ($2) | MQ-2 smoke/LPG gas ($2) | MQ-2 smoke/LPG gas ($2) |
| Security & safety | How fast are vehicles going past? | 6 |  | NEO-6M GPS ($8) | NEO-6M GPS ($8) | Weight-in-motion: piezo cable ($15) |
| Water | How much is in the tank? | 39 |  | ESP32 native touch pins ($0) | Reed switch ($0.5) | Reed switch ($0.5) |
| Water | Is water escaping where it shouldn't? | 19 |  | Piezo contact mic / disc ($0.5) | HDC3022 humidity + temp ($7) | Capacitive soil moisture v2 ($2) |
| Water | Is the pump about to run dry? | 18 |  | Vertical float level switch (reed) ($4) | Water level capacitive strip ($7) | Vertical float level switch (reed) ($4) |
| Water | How fast is water flowing? | 11 |  | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) |
| Water | How much water was used, by whom, and when? | 9 |  | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) |
| Water | How concentrated is the nutrient solution? | 8 |  | ADS1115 16-bit ADC (the analog fixer) ($3) | TCS34725 RGB color ($7) | ADS1115 16-bit ADC (the analog fixer) ($3) |
| Water | Is the water at the right temperature? | 7 |  | NTC thermistor 10k ($0.3) | MLX90614 IR thermometer ($8) | NTC thermistor 10k ($0.3) |
| Water | Is the sanitiser actually working? | 5 |  | AS7331 spectral UV ($27.5) | AS7331 spectral UV ($27.5) | AS7331 spectral UV ($27.5) |
| Water | How much heat did this water actually carry? | 5 |  | DS18B20 digital temp probe ($2.5) | Transit-time ultrasonic flow (clamp-on) ($85) | DS18B20 digital temp probe ($2.5) |
| Water | Is the water too acidic or alkaline? | 4 |  | ADS1115 16-bit ADC (the analog fixer) ($3) | TCS34725 RGB color ($7) | ADS1115 16-bit ADC (the analog fixer) ($3) |
| Water | Is the water cloudy — sediment, algae, runoff? | 3 | rare | TCS3200 frequency-output colour sensor ($4) | TCS3200 frequency-output colour sensor ($4) | TCS3200 frequency-output colour sensor ($4) |
| Water | Is there enough oxygen for fish or microbes? | 2 | rare | ORP (redox) probe ($110) | — none | ORP (redox) probe ($110) |
| Weather & outdoors | Will there be frost tonight? | 17 |  | NTC thermistor 10k ($0.3) | AHT20 temp/humidity ($2) | NTC thermistor 10k ($0.3) |
| Weather & outdoors | Is the sky clear or clouded? | 17 |  | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) | Photoresistor (LDR) ($0.2) |
| Weather & outdoors | Is water rising, and how fast? | 16 |  | US-100 ultrasonic w/ temp comp ($4) | US-100 ultrasonic w/ temp comp ($4) | US-100 ultrasonic w/ temp comp ($4) |
| Weather & outdoors | Is a storm coming? | 11 |  | BMP280 budget barometer ($1.5) | BMP280 budget barometer ($1.5) | BMP280 budget barometer ($1.5) |
| Weather & outdoors | How deep is the snow? | 7 |  | US-100 ultrasonic w/ temp comp ($4) | US-100 ultrasonic w/ temp comp ($4) | US-100 ultrasonic w/ temp comp ($4) |
| Weather & outdoors | Is it raining, and how hard? | 5 |  | Reed switch ($0.5) | Reed switch ($0.5) | Reed switch ($0.5) |
| Weather & outdoors | How windy is it, and from where? | 5 |  | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) | A3144 / SS49E Hall switches ($0.4) |
| Weather & outdoors | How much UV have I accumulated today? | 5 |  | GUVA-S12SD UV analog ($4) | GUVA-S12SD UV analog ($4) | GUVA-S12SD UV analog ($4) |
| Weather & outdoors | How much hotter is this spot than the next street? | 4 |  | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) | AHT20 temp/humidity ($2) |
| Weather & outdoors | How much solar energy is available? | 3 | rare | ML8511 / VEML6075 UV outdoor ($6) | ML8511 / VEML6075 UV outdoor ($6) | ML8511 / VEML6075 UV outdoor ($6) |
| Weather & outdoors | How far away is the lightning? | 1 | SOLE ROUTE | AS3935 lightning detector ($20) | AS3935 lightning detector ($20) | AS3935 lightning detector ($20) |

## The two opposite rankings

Hubs cover many outcomes and are replaceable. Keys cover few and are the only route. A good kit needs both, and they anti-correlate.

| Irreplaceable (buy for intent) | $ | | Recombinatory (buy for breadth) | $ | per $ |
|---|--:|---|---|--:|--:|
| IIS3DWB wideband vibration sensor | 45.0 | SOLE: Is the belt or coupling slipping? | Piezo contact mic / disc | 0.5 | 28.0 |
| AS3935 lightning detector | 20 | SOLE: How far away is the lightning? | Reed switch | 0.5 | 26.0 |
| RD200 radon sensor | 180 | SOLE: Is radon accumulating? | A3144 / SS49E Hall switches | 0.4 | 22.0 |
| Atmospheric electricity (field mill lite) | 15 | SOLE: Is the atmosphere electrically charged? | NTC thermistor 10k | 0.3 | 14.0 |
| Ultrasonic mic experiments | 6 | 8 outcomes | Photoresistor (LDR) | 0.2 | 14.0 |
| Acoustic emission (ultrasonic contact) | 10 | 9 outcomes | ESP32 native touch pins | 0 | 12.0 |
| DS18B20 water temp + flow combo | 10 | 11 outcomes | Wi-Fi CSI sensing (the router IS the sensor) | 0 | 10.0 |
| Scintillating gamma spectrometer | 150 | 6 outcomes | SW-420 vibration switch | 1 | 8.0 |
| INA219 current/power monitor | 2.5 | 13 outcomes | TTP223 single touch | 0.5 | 8.0 |
| SiPM photodetector module | 60.0 | 3 outcomes | ESP32 internal sensors (free!) | 0 | 8.0 |
| DFRobot Gravity mmWave presence radar | 22 | 13 outcomes | SW-520D ball tilt switch | 0.5 | 8.0 |
| BioAmp EXG Pill | 25 | 8 outcomes | MPU-6050 6-axis IMU | 2 | 7.5 |
| INA3221 triple-channel power | 4 | 12 outcomes | KY-037/038 sound modules | 1 | 6.0 |
| Scale-hacking: NAU7802 | 12 | 16 outcomes | HC-SR04 ultrasonic | 1.5 | 5.33 |
| Weight-in-motion: piezo cable | 15 | 12 outcomes | INA219 current/power monitor | 2.5 | 5.2 |
| ORP (redox) probe | 110 | 6 outcomes | RCWL-0516 doppler radar | 1.2 | 5.0 |
| DS18B20 digital temp probe | 2.5 | 10 outcomes | Through-beam slot / photo-interrupter | 1 | 5.0 |
| Time-of-flight spectroscopy: AS7263 trick | 35 | 9 outcomes | INMP441 I2S MEMS mic | 3 | 4.67 |
| TCS34725 RGB color | 7 | 6 outcomes | BMP280 budget barometer | 1.5 | 4.67 |
| Person Sensor (Useful Sensors) | 10 | 8 outcomes | BL0940 calibration-free mains metering IC | 1.5 | 4.67 |
| LDC1612 inductive sensing | 9 | 13 outcomes | QMC5883L compass | 2 | 4.5 |
| MLX90614 IR thermometer | 8 | 12 outcomes | DS18B20 digital temp probe | 2.5 | 4.0 |
| Analog pH kit | 30 | 6 outcomes | HC-SR501 PIR motion | 1.5 | 4.0 |
| Electrochemical gas cells | 80 | 6 outcomes | ADXL345 accelerometer | 3 | 4.0 |
| HX711 + load cell | 5 | 14 outcomes | RC522 RFID reader | 2 | 4.0 |
| INMP441 I2S MEMS mic | 3 | 14 outcomes | AHT20 temp/humidity | 2 | 4.0 |
| Grove Vision AI v2 | 16 | 14 outcomes | TSOP38238 38kHz IR receiver | 1.0 | 4.0 |
| ATM90E32AS polyphase energy metering AFE | 4.0 | 7 outcomes | LIS3DH budget accel | 3 | 3.33 |
| Seeed MR60BHA2 vital-sign radar | 25 | 10 outcomes | 801S vibration sensor | 3 | 3.0 |
| ZE08-CH2O formaldehyde | 22 | 6 outcomes | Piezo shock/knock element | 3 | 3.0 |
| SI4432/CC1101 sub-GHz sniffer | 4 | 10 outcomes | IR flame detector (flicker) | 2 | 3.0 |
| Alphasense PID-AH2 photoionisation VOC | 320.0 | 5 outcomes | INA3221 triple-channel power | 4 | 3.0 |
| OpenBCI Cyton 8-channel biosensing board | 499.0 | 5 outcomes | HX711 + load cell | 5 | 2.8 |
| Reed switch | 0.5 | 13 outcomes | TMP36 analog temp | 1.5 | 2.67 |
| TCS3200 frequency-output colour sensor | 4.0 | 4 outcomes | ACS712 Hall current | 3 | 2.67 |
| BNO086 high-perf fusion IMU | 22 | 12 outcomes | 125kHz RDM6300 RFID | 3 | 2.67 |
| LSM6DSOX ML-core IMU | 10 | 15 outcomes | MQ-2 smoke/LPG gas | 2 | 2.5 |
| GSR / EDA sensor | 10 | 4 outcomes | AM312 mini PIR | 2 | 2.5 |
| PZEM-004T AC power module | 11 | 8 outcomes | Capacitive soil moisture v2 | 2 | 2.5 |
| LD2410 mmWave presence | 5 | 9 outcomes | SI4432/CC1101 sub-GHz sniffer | 4 | 2.5 |
| ML8511 / VEML6075 UV outdoor | 6 | 4 outcomes | US-100 ultrasonic w/ temp comp | 4 | 2.5 |
| MPU-6050 6-axis IMU | 2 | 15 outcomes | MQ-135 air quality | 2.5 | 2.4 |
| Time-of-flight gesture radar 60GHz | 110 | 11 outcomes | Inductive proximity switch M12/M18 | 2.5 | 2.4 |
| AHT20 temp/humidity | 2 | 8 outcomes | ICS-43434 I2S mic | 5 | 2.2 |
| LD1125H 24GHz respiration radar | 9 | 10 outcomes | Velostat pressure sheets | 5 | 2.2 |
| Dissolved oxygen kit (Atlas EZO-DO) | 170 | 4 outcomes | KX132 low-power accel | 6 | 2.17 |
| MAX30102 pulse oximeter | 6 | 8 outcomes | DHT22 / AM2302 | 4 | 2.0 |
| A3144 / SS49E Hall switches | 0.4 | 11 outcomes | BH1750 lux sensor | 2.5 | 2.0 |
| Pyranometer (solar irradiance) | 60 | 5 outcomes | Strain gauge + amp | 4 | 2.0 |
| ADS1299 8-channel EEG front end | 45.0 | 4 outcomes | SHTC3 tiny low-power RH/T | 4 | 2.0 |
| MPU-9250 9-axis (legacy) | 8 | 12 outcomes | MAX44009 ultra-low-power lux | 3 | 2.0 |
| ICM-20948 9-axis IMU | 15 | 11 outcomes | ADS1115 16-bit ADC (the analog fixer) | 3 | 2.0 |
| AD5941 bioimpedance / EIS analyser | 95.0 | 4 outcomes | Photoelectric beam sensor E18-D80NK | 3 | 2.0 |
| BMI270 wearable IMU | 8 | 12 outcomes | Capacitive rain/condensation plate | 3 | 2.0 |
| EMF / RF field probes | 12 | 7 outcomes | LD2410 mmWave presence | 5 | 1.8 |
| Piezo contact mic / disc | 0.5 | 14 outcomes | Si7021 humidity/temp | 4 | 1.75 |
| Geiger counter kit | 25 | 5 outcomes | AGS02MA TVOC budget | 4 | 1.75 |
| INA226/INA228 precision power | 6 | 8 outcomes | ATM90E32AS polyphase energy metering AFE | 4.0 | 1.75 |
| RS-485 soil NPK/EC probe | 40 | 6 outcomes | ADE7953 dual-channel single-phase energy meter | 3.5 | 1.71 |
| ADS1115 16-bit ADC (the analog fixer) | 3 | 6 outcomes | MMC5603 precision magnetometer | 6 | 1.67 |
| Draw-wire (string pot) sensor | 15 | 12 outcomes | MQ-3 alcohol sensor | 2.5 | 1.6 |
| Geophone SM-24 | 30 | 11 outcomes | MQ-7 carbon monoxide | 2.5 | 1.6 |
| MMC5603 precision magnetometer | 6 | 10 outcomes | VL53L0X ToF laser | 5 | 1.6 |
| Transit-time ultrasonic flow (clamp-on) | 85 | 8 outcomes | YF-S201 flow sensor | 5 | 1.6 |
| Color-changing material readers | 10 | 5 outcomes | MQ-4 methane / natural gas | 2.5 | 1.6 |
| ICS-43434 I2S mic | 5 | 11 outcomes | MLX90614 IR thermometer | 8 | 1.5 |
| TMP117 ultra-precise temp | 11 | 8 outcomes | LSM6DSOX ML-core IMU | 10 | 1.5 |
| MPRLS ported pressure | 15 | 8 outcomes | TLV493D 3D magnetic | 6 | 1.5 |
| LD2450 multi-target tracking radar | 12 | 10 outcomes | PN532 NFC controller | 6 | 1.5 |
| Apogee SQ-500 full-spectrum quantum (PAR) sensor | 400.0 | 4 outcomes | TSL2561 lux sensor | 4 | 1.5 |
| AS7263 NIR spectral | 27 | 6 outcomes | BMI270 wearable IMU | 8 | 1.5 |
| MLX90393 wide-range 3D mag | 8 | 11 outcomes | MPU-9250 9-axis (legacy) | 8 | 1.5 |
| YF-S201 flow sensor | 5 | 8 outcomes | INA700 power monitor with on-die shunt | 4.0 | 1.5 |
| Watermark granular-matrix soil water sensor | 45 | 6 outcomes | LDC1612 inductive sensing | 9 | 1.44 |
| Eastron SDM120-Modbus DIN energy meter | 38.0 | 6 outcomes | MCP9808 precision temp | 5 | 1.4 |
| BNO055 fusion IMU | 25 | 10 outcomes | MLX90393 wide-range 3D mag | 8 | 1.38 |
| MiCS-6814 tri-gas | 20 | 7 outcomes | SHT41 humidity + temp | 6 | 1.33 |
| MAX31865 RTD amplifier | 15 | 7 outcomes | BME280 climate combo | 6 | 1.33 |
| Capacitive liquid/force FDC1004 | 9 | 10 outcomes | Ultrasonic mic experiments | 6 | 1.33 |
| RPLIDAR / LD19 scanning LiDAR | 40 | 10 outcomes | MAX30102 pulse oximeter | 6 | 1.33 |
| MAX86150 ECG+PPG combo | 23 | 5 outcomes | INA226/INA228 precision power | 6 | 1.33 |
| BME688 gas + climate AI | 15 | 9 outcomes | MAX471 / shunt + ADS1115 | 3 | 1.33 |
| ADE7953 dual-channel single-phase energy meter | 3.5 | 6 outcomes | AS5600 magnetic angle | 3 | 1.33 |
| TSL2591 high dynamic lux | 7 | 6 outcomes | Scale-hacking: NAU7802 | 12 | 1.33 |
| Azoteq IQS7211 / IQS263 proximity + touch | 6.0 | 3 outcomes | PDM MEMS microphone | 3.0 | 1.33 |
| Alphasense OPC-N3 optical particle counter | 500.0 | 5 outcomes | 40kHz ultrasonic transducer pair | 3.0 | 1.33 |
| Ground vibration fence: fiber + photodiode | 10 | 8 outcomes | MAX9814 AGC mic amp | 7 | 1.29 |
| Velostat pressure sheets | 5 | 11 outcomes | SPH0645 I2S mic | 7 | 1.29 |
| QMC5883L compass | 2 | 9 outcomes | GUVA-S12SD UV analog | 4 | 1.25 |
| MyoWare 2.0 EMG | 40 | 6 outcomes | VEML7700 high-accuracy lux | 5 | 1.2 |
| TI AWR1642 77GHz automotive radar EVM | 299.0 | 6 outcomes | VCNL4040 proximity + lux | 6 | 1.17 |
| Muon detector (CosmicWatch) | 100 | 4 outcomes | MAX4466 adjustable mic amp | 6 | 1.17 |
| KX132 low-power accel | 6 | 13 outcomes | OBD-II port as a sensor bus | 6.0 | 1.17 |
| MQ-131 ozone | 30 | 4 outcomes | FSR402 force resistor | 7 | 1.14 |
| MiCS-5524 CO/VOC | 14 | 6 outcomes | Nano33-style 1kg beam scale kit | 8 | 1.12 |
| u-blox M10 GNSS | 20 | 6 outcomes | Capacitive liquid/force FDC1004 | 9 | 1.11 |
| BL0940 calibration-free mains metering IC | 1.5 | 7 outcomes | LD1125H 24GHz respiration radar | 9 | 1.11 |
| MAXM86161 reflective PPG module | 120.0 | 4 outcomes | DS18B20 water temp + flow combo | 10 | 1.1 |
| TF-Luna LiDAR | 25 | 9 outcomes | HDC3022 humidity + temp | 7 | 1.0 |
| Panasonic EKMC PIR (quality) | 12 | 9 outcomes | LPS22HB pressure sensor | 6 | 1.0 |
| SHT31 weatherproof probe | 12 | 8 outcomes | LTR-390 UV + ambient | 5 | 1.0 |
| ADXL345 accelerometer | 3 | 12 outcomes | JSN-SR04T waterproof ultrasonic | 6 | 1.0 |
| BME280 climate combo | 6 | 8 outcomes | MPR121 12-pad cap touch | 6 | 1.0 |
| HuskyLens AI camera | 45 | 11 outcomes | Pulse sensor (PPG classic) | 5 | 1.0 |
| AS7265x 18-channel spectral triad | 69.95 | 5 outcomes | MQ-8 hydrogen sensor | 4 | 1.0 |
| Grid-EYE AMG8833 thermal array | 35 | 10 outcomes | Bat/dolphin: 40kHz ranging array | 8 | 1.0 |
| DHT22 / AM2302 | 4 | 8 outcomes | Wi-Fi and magnetic fingerprint positioning | 5.0 | 1.0 |
| Ferroelectret bed sensor (ballistocardiography) | 130.0 | 5 outcomes | Stainless vertical float level switch | 5.0 | 1.0 |
| Turbidity sensor | 12 | 4 outcomes | TCS3200 frequency-output colour sensor | 4.0 | 1.0 |
| MAX30001 ECG + bioimpedance AFE | 45.0 | 5 outcomes | Vertical float level switch (reed) | 4.0 | 1.0 |
| AS7341 11-channel spectral | 14 | 6 outcomes | Acoustic emission (ultrasonic contact) | 10 | 0.9 |
| AS7331 spectral UV | 27.5 | 5 outcomes | OV2640 camera (ESP32-CAM) | 8 | 0.88 |
| Conductive rubber stretch cord | 10 | 7 outcomes | Grove Vision AI v2 | 16 | 0.88 |
| AFE4490 transmissive pulse-oximetry front end | 55.0 | 4 outcomes | TSL2591 high dynamic lux | 7 | 0.86 |
| Capacitive rain/condensation plate | 3 | 6 outcomes | TCS34725 RGB color | 7 | 0.86 |
| EC / TDS sensor | 12 | 6 outcomes | Water level capacitive strip | 7 | 0.86 |
| Benewake TF03 long-range industrial LiDAR | 180.0 | 7 outcomes | HLK-LD2412 24GHz presence radar | 7.0 | 0.86 |
| PN532 NFC controller | 6 | 9 outcomes | XGZP6897D low-range diff pressure | 6 | 0.83 |
| Chirp! plant sensor | 10 | 6 outcomes | APDS-9960 gesture/color/prox | 6 | 0.83 |
| METER TEROS 12 soil moisture, EC and temperature | 220.0 | 4 outcomes | LD2450 multi-target tracking radar | 12 | 0.83 |
| True TDR soil water content probe | 395.0 | 4 outcomes | LIS2DW12 nanoamp accelerometer | 6.0 | 0.83 |
| INA700 power monitor with on-die shunt | 4.0 | 6 outcomes | DS18B20 soil temp spear | 5 | 0.8 |
| Scent delivery + e-nose loop | 60 | 9 outcomes | Person Sensor (Useful Sensors) | 10 | 0.8 |
| DFRobot dB meter | 37 | 8 outcomes | Weight-in-motion: piezo cable | 15 | 0.8 |
| Snow/level laser (outdoor ToF) | 70 | 8 outcomes | Draw-wire (string pot) sensor | 15 | 0.8 |
| Alphasense NO2-B43F electrochemical cell | 120.0 | 4 outcomes | Ground vibration fence: fiber + photodiode | 10 | 0.8 |
| SHT41 humidity + temp | 6 | 8 outcomes | AMC1311 reinforced isolated voltage-sense amplifier | 5.0 | 0.8 |
| Winsen ZE25-O3 ozone module | 30.0 | 3 outcomes | ENS160 air quality | 9 | 0.78 |
| High-g accel ADXL375 | 18 | 8 outcomes | A02YYUW waterproof ultrasonic | 9 | 0.78 |
| US-100 ultrasonic w/ temp comp | 4 | 10 outcomes | Sharp GP2Y0A21 IR distance | 8 | 0.75 |
| NEO-6M GPS | 8 | 6 outcomes | Flex sensor 2.2" | 8 | 0.75 |
| SPH0645 I2S mic | 7 | 9 outcomes | Non-contact liquid level XKC-Y26 | 8 | 0.75 |
| PIN photodiode radiation detector | 2.0 | 2 outcomes | NEO-6M GPS | 8 | 0.75 |
| Si7021 humidity/temp | 4 | 7 outcomes | SI1145 UV/IR/visible | 8 | 0.75 |
| S-type load cell | 35.0 | 4 outcomes | Panasonic EKMC PIR (quality) | 12 | 0.75 |
| SHTC3 tiny low-power RH/T | 4 | 8 outcomes | AS5048A 14-bit angle | 12 | 0.75 |
| AD8232 ECG front-end | 10 | 6 outcomes | nRF52 BLE beacon tag | 8.0 | 0.75 |
| MAX9814 AGC mic amp | 7 | 9 outcomes | ICM-20948 9-axis IMU | 15 | 0.73 |
| Piezo shock/knock element | 3 | 9 outcomes | TMP117 ultra-precise temp | 11 | 0.73 |
| AS5048A 14-bit angle | 12 | 9 outcomes | PZEM-004T AC power module | 11 | 0.73 |
| Nano33-style 1kg beam scale kit | 8 | 9 outcomes | Capacitive proximity switch M18 | 7.0 | 0.71 |
| 4-wire PT100 RTD probe with thermowell | 25.0 | 5 outcomes | BMM350 TMR magnetometer | 7.0 | 0.71 |
| MQ-7 carbon monoxide | 2.5 | 4 outcomes | SGP30 eCO2/TVOC (legacy) | 10 | 0.7 |
| BQ27441-G1 Impedance Track fuel gauge | 18.0 | 4 outcomes | Conductive rubber stretch cord | 10 | 0.7 |
| Tipping bucket rain gauge | 12 | 4 outcomes | SCT-013 CT clamp | 10 | 0.7 |
| Bend Labs digital flex (1-axis) | 70 | 7 outcomes | SHT31 weatherproof probe | 12 | 0.67 |
| Livox Mid-360 3D LiDAR | 749.0 | 6 outcomes | MS5611 high-res altimeter | 6 | 0.67 |
| 125kHz RDM6300 RFID | 3 | 8 outcomes | VL53L1X long-range ToF | 12 | 0.67 |
| GUVA-S12SD UV analog | 4 | 5 outcomes | ML8511 / VEML6075 UV outdoor | 6 | 0.67 |
| MAX31855 thermocouple amp | 15 | 8 outcomes | VEML6030 ambient light sensor | 6.0 | 0.67 |
| MAX17260 ModelGauge m5 fuel gauge | 4.0 | 3 outcomes | RD-03D 24GHz multi-target tracking radar | 9.0 | 0.67 |
| PMS7003 laser particle counter | 20.0 | 5 outcomes | VL6180X short-range ToF | 8 | 0.62 |
| Leaf wetness sensor | 15 | 4 outcomes | BMI323 6-axis IMU | 8.0 | 0.62 |
| HLK-LD2412 24GHz presence radar | 7.0 | 6 outcomes | Thermocouple multiplexer board | 13 | 0.62 |
| MLX90614 forehead mode | 25 | 5 outcomes | BME688 gas + climate AI | 15 | 0.6 |
| LIS3DH budget accel | 3 | 10 outcomes | AD8232 ECG front-end | 10 | 0.6 |
| SI1145 UV/IR/visible | 8 | 6 outcomes | Chirp! plant sensor | 10 | 0.6 |
| MLX90640 thermal camera | 45 | 8 outcomes | DFRobot Gravity mmWave presence radar | 22 | 0.59 |
| ADS1292R 2-channel ECG + respiration front end | 70.0 | 4 outcomes | EMF / RF field probes | 12 | 0.58 |
| Soil/water nitrate ion-selective | 90 | 4 outcomes | DPS310 barometer | 7 | 0.57 |
| Hamamatsu C12880MA micro-spectrometer | 330.0 | 5 outcomes | MAX30205 clinical body temp | 9 | 0.56 |
| Ammonium ion-selective electrode | 189.0 | 4 outcomes | BNO086 high-perf fusion IMU | 22 | 0.55 |
| A02YYUW waterproof ultrasonic | 9 | 7 outcomes | MAX31855 thermocouple amp | 15 | 0.53 |
| LTR-390 UV + ambient | 5 | 5 outcomes | MPRLS ported pressure | 15 | 0.53 |
| RC522 RFID reader | 2 | 8 outcomes | BMP390 precision barometer | 10 | 0.5 |
| SCT-013 CT clamp | 10 | 7 outcomes | SGP40 VOC index | 12 | 0.5 |
| ADXL355 low-noise accel | 38 | 10 outcomes | EC / TDS sensor | 12 | 0.5 |
| IR flame detector (flicker) | 2 | 6 outcomes | Conductive thread + fabric pads | 8 | 0.5 |
| Thermocouple multiplexer board | 13 | 8 outcomes | Color-changing material readers | 10 | 0.5 |
| DS18B20 soil temp spear | 5 | 4 outcomes | ST25DV64K dual-interface NFC tag | 8.0 | 0.5 |
| Bat/dolphin: 40kHz ranging array | 8 | 8 outcomes | ICM-42688-P low-noise IMU | 10.0 | 0.5 |
| RD-03D 24GHz multi-target tracking radar | 9.0 | 6 outcomes | OPT3001 photometric lux sensor | 8.0 | 0.5 |
| Anemometer cup sensor | 12 | 3 outcomes | MAX31865 RTD amplifier | 15 | 0.47 |
| BMM350 TMR magnetometer | 7.0 | 5 outcomes | VL53L5CX 8x8 ToF array | 20 | 0.45 |
| HDC3022 humidity + temp | 7 | 7 outcomes | OPT4048 tristimulus color | 9 | 0.44 |
| RPLIDAR A1 360 degree triangulation LiDAR | 99.0 | 6 outcomes | High-g accel ADXL375 | 18 | 0.44 |
| MQ-2 smoke/LPG gas | 2 | 5 outcomes | MiCS-5524 CO/VOC | 14 | 0.43 |
| BMP280 budget barometer | 1.5 | 7 outcomes | AS7341 11-channel spectral | 14 | 0.43 |
| Inclinometer SCL3300 | 35 | 8 outcomes | Paddle flow switch | 12.0 | 0.42 |
| Wind vane | 12 | 3 outcomes | PN5180 long-range NFC / ISO15693 reader | 12.0 | 0.42 |
| MaxBotix MB7389 weather LV | 110 | 7 outcomes | ICM-45686 premium 6-axis IMU | 12.0 | 0.42 |
| BME690 gas + climate | 22.0 | 6 outcomes | VL53L4CD short-range precision ToF | 12.0 | 0.42 |
| SEN55 all-in-one air node | 50.0 | 6 outcomes | Seeed MR60BHA2 vital-sign radar | 25 | 0.4 |
| Acconeer XM125 pulsed coherent radar | 70.0 | 6 outcomes | BNO055 fusion IMU | 25 | 0.4 |
| LPS22HB pressure sensor | 6 | 6 outcomes | GSR / EDA sensor | 10 | 0.4 |
| RTL-SDR receiver | 30.0 | 4 outcomes | Water leak rope sensor | 10 | 0.4 |
| HC-SR501 PIR motion | 1.5 | 6 outcomes | Tire pressure TPMS receivers | 10 | 0.4 |
| ADXL1005 ultra-wideband analog accelerometer | 110.0 | 5 outcomes | VL53L4CX multi-target ToF | 15.0 | 0.4 |
| HLK-LD6001A 60GHz fall-detection radar | 35.0 | 6 outcomes | FDC2214 capacitive proximity front-end | 15.0 | 0.4 |
| Wi-Fi and magnetic fingerprint positioning | 5.0 | 5 outcomes | Optical infrared water-in-fuel | 18 | 0.39 |
| METER TEROS 21 soil water potential | 290.0 | 3 outcomes | BMA400 ultra-low-power accelerometer | 13.0 | 0.38 |
| ZED-F9P RTK centimetre GNSS | 260 | 6 outcomes | LSM6DSO32 high-range IMU | 13.0 | 0.38 |
| Fingerprint reader R503 | 20 | 7 outcomes | Geophone SM-24 | 30 | 0.37 |
| FLIR Lepton 3.5 | 240 | 7 outcomes | XY-MD02 Modbus RTU temperature & humidity transmitter | 11.0 | 0.36 |
| NTC thermistor 10k | 0.3 | 7 outcomes | TF-Luna LiDAR | 25 | 0.36 |
| Free-chlorine amperometric membrane probe | 390.0 | 3 outcomes | MLX90632 miniature IR temp | 14 | 0.36 |
| MQ-8 hydrogen sensor | 4 | 4 outcomes | MiCS-6814 tri-gas | 20 | 0.35 |
| Thermal flow: SDP + thermistor DIY | 40 | 8 outcomes | Fingerprint reader R503 | 20 | 0.35 |
| ENS160 air quality | 9 | 7 outcomes | PMS5003 particulate | 15 | 0.33 |
| SGP30 eCO2/TVOC (legacy) | 10 | 7 outcomes | Tipping bucket rain gauge | 12 | 0.33 |
| AGS02MA TVOC budget | 4 | 7 outcomes | Compost / hay temp lance | 15 | 0.33 |
| Gypsum soil moisture block | 10.0 | 2 outcomes | Turbidity sensor | 12 | 0.33 |
| JSN-SR04T waterproof ultrasonic | 6 | 6 outcomes | 600/1024PPR optical encoder | 12 | 0.33 |
| SCD41 true CO2 | 25 | 8 outcomes | OV5640 5MP autofocus cam | 15 | 0.33 |
| VL53L5CX 8x8 ToF array | 20 | 9 outcomes | Oil/quality dielectric probe | 12 | 0.33 |
| SAM-M10Q GNSS with integrated patch antenna | 40.0 | 5 outcomes | Conductive fabric and tape electrodes | 12.0 | 0.33 |
| FSR402 force resistor | 7 | 8 outcomes | SCD41 true CO2 | 25 | 0.32 |
| MAX4466 adjustable mic amp | 6 | 7 outcomes | BioAmp EXG Pill | 25 | 0.32 |
| PN5180 long-range NFC / ISO15693 reader | 12.0 | 5 outcomes | FS3000 air velocity | 26 | 0.31 |
| VEML7700 high-accuracy lux | 5 | 6 outcomes | u-blox M10 GNSS | 20 | 0.3 |
| ADS1298 8-channel clinical ECG front end | 160.0 | 3 outcomes | Grid-EYE AMG8833 thermal array | 35 | 0.29 |
| ACS712 Hall current | 3 | 8 outcomes | VL53L8CX 8x8 depth zone array | 25.0 | 0.28 |
| Thermistor airflow (nasal) kit | 3 | 3 outcomes | MH-Z19C budget NDIR CO2 | 18 | 0.28 |
| SGP40 VOC index | 12 | 6 outcomes | ZE08-CH2O formaldehyde | 22 | 0.27 |
| AMC1311 reinforced isolated voltage-sense amplifier | 5.0 | 4 outcomes | BME690 gas + climate | 22.0 | 0.27 |
| SDP810 differential pressure | 35 | 7 outcomes | Leaf wetness sensor | 15 | 0.27 |
| OV5640 5MP autofocus cam | 15 | 5 outcomes | Atmospheric electricity (field mill lite) | 15 | 0.27 |
| Alphasense CL2-A1 chlorine cell | 130.0 | 3 outcomes | EeonTex piezoresistive fabric | 15.0 | 0.27 |
| PMS5003 particulate | 15 | 5 outcomes | MEMS ultrasonic ToF (Chirp) | 15.0 | 0.27 |
| SPS30 premium PM | 45 | 5 outcomes | ADXL355 low-noise accel | 38 | 0.26 |
| Flex sensor 2.2" | 8 | 6 outcomes | Time-of-flight spectroscopy: AS7263 trick | 35 | 0.26 |
| MCP9808 precision temp | 5 | 7 outcomes | RPLIDAR / LD19 scanning LiDAR | 40 | 0.25 |
| SCD30 NDIR CO2 | 40 | 8 outcomes | BN-880 GNSS module with on-board compass | 20.0 | 0.25 |
| MAX30208 clinical-accuracy skin temperature | 10.0 | 3 outcomes | PMS7003 laser particle counter | 20.0 | 0.25 |
| ZMPT101B voltage sensor | 3 | 3 outcomes | LSM6DSV16X IMU with on-chip fusion | 20.0 | 0.25 |
| AS7343 14-channel spectral sensor | 19.95 | 4 outcomes | ISM330DHCX industrial IMU | 20.0 | 0.25 |
| DW3000 UWB ranging radio (FiRa generation) | 48.0 | 5 outcomes | L3GD20H gyro-only 3-axis | 20.0 | 0.25 |
| Paddle flow switch | 12.0 | 5 outcomes | HuskyLens AI camera | 45 | 0.24 |
| FS3000 air velocity | 26 | 8 outcomes | Inclinometer SCL3300 | 35 | 0.23 |
| ZED-X20P all-band centimetre GNSS | 90.0 | 5 outcomes | DWM1001C UWB module with ready-made RTLS firmware | 22.0 | 0.23 |
| UM980 triple-band RTK receiver | 200.0 | 5 outcomes | AS7263 NIR spectral | 27 | 0.22 |
| ADXL1002 wideband analog vibration sensor | 95.0 | 5 outcomes | STCC4 low-cost percent CO2 | 18.0 | 0.22 |
| 352C33 IEPE piezoelectric accelerometer | 450.0 | 5 outcomes | BQ27441-G1 Impedance Track fuel gauge | 18.0 | 0.22 |
| Wi-Fi CSI sensing (the router IS the sensor) | 0 | 5 outcomes | MAX86150 ECG+PPG combo | 23 | 0.22 |
| 801S vibration sensor | 3 | 9 outcomes | DFRobot dB meter | 37 | 0.22 |
| Oil/quality dielectric probe | 12 | 4 outcomes | AS7343 14-channel spectral sensor | 19.95 | 0.2 |
| Through-beam photoelectric pair | 95.0 | 6 outcomes | SDP810 differential pressure | 35 | 0.2 |
| Submersible hydrostatic level transmitter | 70.0 | 5 outcomes | SCD30 NDIR CO2 | 40 | 0.2 |
| Water leak rope sensor | 10 | 4 outcomes | SenseAir S8 CO2 | 25 | 0.2 |
| L3GD20H gyro-only 3-axis | 20.0 | 5 outcomes | Trill flexible touch sliders | 20 | 0.2 |
| Optical infrared water-in-fuel | 18 | 7 outcomes | MLX90614 forehead mode | 25 | 0.2 |
| MQ-135 air quality | 2.5 | 6 outcomes | Analog pH kit | 30 | 0.2 |
| Capacitive soil moisture v2 | 2 | 5 outcomes | Geiger counter kit | 25 | 0.2 |
| VL53L8CX 8x8 depth zone array | 25.0 | 7 outcomes | Thermal flow: SDP + thermistor DIY | 40 | 0.2 |
| Paddlewheel insertion flow sensor | 320.0 | 4 outcomes | 4-wire PT100 RTD probe with thermowell | 25.0 | 0.2 |
| MLX90632 miniature IR temp | 14 | 5 outcomes | Wiegand-26 access control reader | 20.0 | 0.2 |
| ZED-F9R dead-reckoning GNSS | 280.0 | 5 outcomes | PMW3901 optical flow | 25.0 | 0.2 |
| BN-880 GNSS module with on-board compass | 20.0 | 5 outcomes | PAA5100JE near-field optical flow | 25.0 | 0.2 |
| Flexible Rogowski coil with integrator | 150.0 | 4 outcomes | Tactile pressure array | 25.0 | 0.2 |
| BMP390 precision barometer | 10 | 5 outcomes | AS7331 spectral UV | 27.5 | 0.18 |
| Pulse sensor (PPG classic) | 5 | 5 outcomes | MLX90640 thermal camera | 45 | 0.18 |
| UM982 dual-antenna RTK with true heading | 260.0 | 5 outcomes | HLK-LD6001A 60GHz fall-detection radar | 35.0 | 0.17 |
| MAX44009 ultra-low-power lux | 3 | 6 outcomes | Ultrasonic liquid (through-wall) | 25 | 0.16 |
| MAX30205 clinical body temp | 9 | 5 outcomes | Button / pancake load cell | 25.0 | 0.16 |
| Photoelectric beam sensor E18-D80NK | 3 | 6 outcomes | Eastron SDM120-Modbus DIN energy meter | 38.0 | 0.16 |
| Omron D6T-32L 1024-pixel thermopile array | 200.0 | 6 outcomes | MyoWare 2.0 EMG | 40 | 0.15 |
| 40kHz ultrasonic transducer pair | 3.0 | 4 outcomes | RS-485 soil NPK/EC probe | 40 | 0.15 |
| Honeywell HPM particulate sensor | 40.0 | 4 outcomes | eTape liquid level | 40 | 0.15 |
| SEN66 six-in-one air module | 70.0 | 6 outcomes | Scent delivery + e-nose loop | 60 | 0.15 |
| MQ-4 methane / natural gas | 2.5 | 4 outcomes | STC31 percent-level CO2 | 28.0 | 0.14 |
| Compost / hay temp lance | 15 | 5 outcomes | Watermark granular-matrix soil water sensor | 45 | 0.13 |
| Water level capacitive strip | 7 | 6 outcomes | MQ-131 ozone | 30 | 0.13 |
| Non-contact liquid level XKC-Y26 | 8 | 6 outcomes | Cubic CM1107N dual-beam CO2 | 30.0 | 0.13 |
| eTape liquid level | 40 | 6 outcomes | RTL-SDR receiver | 30.0 | 0.13 |
| LC29H(DA) low-cost L1+L5 RTK rover | 55.0 | 5 outcomes | DW1000 UWB two-way ranging radio | 40.0 | 0.12 |
| OBD-II port as a sensor bus | 6.0 | 7 outcomes | SAM-M10Q GNSS with integrated patch antenna | 40.0 | 0.12 |
| KY-037/038 sound modules | 1 | 6 outcomes | YRM100 low-cost UHF reader module | 32.0 | 0.12 |
| High-range EC probe for salinity (K=10) | 70.0 | 4 outcomes | SEN55 all-in-one air node | 50.0 | 0.12 |
| RCWL-0516 doppler radar | 1.2 | 6 outcomes | Snow/level laser (outdoor ToF) | 70 | 0.11 |
| ST25DV64K dual-interface NFC tag | 8.0 | 4 outcomes | 134.2kHz FDX-B animal microchip reader | 35.0 | 0.11 |
| FDC2214 capacitive proximity front-end | 15.0 | 6 outcomes | LEM LA 55-P closed-loop Hall current transducer | 35.0 | 0.11 |
| SW-420 vibration switch | 1 | 8 outcomes | S-type load cell | 35.0 | 0.11 |
| SenXor MI0801 CMOS thermal imager | 95.0 | 5 outcomes | SPS30 premium PM | 45 | 0.11 |
| Electromagnetic (mag) flowmeter | 300.0 | 3 outcomes | IIS3DWB wideband vibration sensor | 45.0 | 0.11 |
| FLIR Lepton 3.1R radiometric thermal module | 180.0 | 5 outcomes | MAX30001 ECG + bioimpedance AFE | 45.0 | 0.11 |
| Figaro TGS6812 catalytic pellistor | 35.0 | 3 outcomes | DW3000 UWB ranging radio (FiRa generation) | 48.0 | 0.1 |
| Photoresistor (LDR) | 0.2 | 7 outcomes | Bend Labs digital flex (1-axis) | 70 | 0.1 |
| TLV493D 3D magnetic | 6 | 9 outcomes | Time-of-flight gesture radar 60GHz | 110 | 0.1 |
| Strain gauge + amp | 4 | 8 outcomes | Winsen ZE03-NH3 ammonia module | 40.0 | 0.1 |
| Capacitive stretch sensor | 90.0 | 4 outcomes | Honeywell HPM particulate sensor | 40.0 | 0.1 |
| MS5611 high-res altimeter | 6 | 4 outcomes | SCA3300 industrial inclinometer/accelerometer | 50.0 | 0.1 |
| Piera IPS-7100 ultrafine particle sensor | 70.0 | 4 outcomes | Transit-time ultrasonic flow (clamp-on) | 85 | 0.09 |
| LSM6DSV16X IMU with on-chip fusion | 20.0 | 5 outcomes | LC29H(DA) low-cost L1+L5 RTK rover | 55.0 | 0.09 |
| ADIS16505-2 tactical-grade IMU | 825.0 | 5 outcomes | ADS1299 8-channel EEG front end | 45.0 | 0.09 |
| nRF52 BLE beacon tag | 8.0 | 6 outcomes | Hydrophone | 45.0 | 0.09 |
| VL53L1X long-range ToF | 12 | 8 outcomes | SEN66 six-in-one air module | 70.0 | 0.09 |
| MQ-3 alcohol sensor | 2.5 | 4 outcomes | Acconeer XM125 pulsed coherent radar | 70.0 | 0.09 |
| Winsen ZE03-NH3 ammonia module | 40.0 | 4 outcomes | Pyranometer (solar irradiance) | 60 | 0.08 |
| Wiegand-26 access control reader | 20.0 | 4 outcomes | MLX90641 thermal (16x12) | 60 | 0.08 |
| Heimann HTPA32x32d thermopile array | 140.0 | 5 outcomes | MLX90621 16x4 fast thermal array | 60.0 | 0.08 |
| ICM-42688-P low-noise IMU | 10.0 | 5 outcomes | Electrochemical gas cells | 80 | 0.07 |
| Conductive fabric and tape electrodes | 12.0 | 4 outcomes | D6T thermal presence | 55 | 0.07 |
| DPS310 barometer | 7 | 4 outcomes | AFE4490 transmissive pulse-oximetry front end | 55.0 | 0.07 |
| MAX471 / shunt + ADS1115 | 3 | 4 outcomes | AS7265x 18-channel spectral triad | 69.95 | 0.07 |
| Through-beam slot / photo-interrupter | 1 | 5 outcomes | Submersible hydrostatic level transmitter | 70.0 | 0.07 |
| ANT-B10 Bluetooth angle-of-arrival anchor | 90.0 | 5 outcomes | Retro-reflective photoelectric sensor | 70.0 | 0.07 |
| 134.2kHz FDX-B animal microchip reader | 35.0 | 4 outcomes | MaxBotix MB7389 weather LV | 110 | 0.06 |
| NTAG I2C Plus 2K dual-interface tag | 6.0 | 3 outcomes | Through-beam photoelectric pair | 95.0 | 0.06 |
| Stainless vertical float level switch | 5.0 | 5 outcomes | RPLIDAR A1 360 degree triangulation LiDAR | 99.0 | 0.06 |
| OV2640 camera (ESP32-CAM) | 8 | 7 outcomes | Piera IPS-7100 ultrafine particle sensor | 70.0 | 0.06 |
| Rotary torque sensor | 180.0 | 3 outcomes | High-range EC probe for salinity (K=10) | 70.0 | 0.06 |
| PDM MEMS microphone | 3.0 | 4 outcomes | ADS1292R 2-channel ECG + respiration front end | 70.0 | 0.06 |
| MLX90641 thermal (16x12) | 60 | 5 outcomes | ZED-X20P all-band centimetre GNSS | 90.0 | 0.06 |
| HC-SR04 ultrasonic | 1.5 | 8 outcomes | ANT-B10 Bluetooth angle-of-arrival anchor | 90.0 | 0.06 |
| VL53L0X ToF laser | 5 | 8 outcomes | Vibrating-fork level switch | 90.0 | 0.06 |
| OPT4048 tristimulus color | 9 | 4 outcomes | ORP (redox) probe | 110 | 0.05 |
| SX1262 sub-GHz transceiver | 8.0 | 2 outcomes | ADXL1002 wideband analog vibration sensor | 95.0 | 0.05 |
| RV4145A ground-fault / residual current detector | 2.0 | 3 outcomes | SenXor MI0801 CMOS thermal imager | 95.0 | 0.05 |
| PMW3901 optical flow | 25.0 | 5 outcomes | Telaire T6713 I2C CO2 | 80.0 | 0.05 |
| M6E-Nano UHF RAIN RFID reader | 275.0 | 6 outcomes | MPS flammable gas and refrigerant sensor | 85.0 | 0.05 |
| TSL2561 lux sensor | 4 | 6 outcomes | ADXL1005 ultra-wideband analog accelerometer | 110.0 | 0.05 |
| Soil CO2 flux chamber (closed dynamic) | 95.0 | 3 outcomes | Soil/water nitrate ion-selective | 90 | 0.04 |
| BPW34 PIN photodiode | 1.0 | 3 outcomes | Capacitive stretch sensor | 90.0 | 0.04 |
| XGZP6897D low-range diff pressure | 6 | 5 outcomes | SenseAir K30 NDIR CO2 | 95.0 | 0.04 |
| LIS2DW12 nanoamp accelerometer | 6.0 | 5 outcomes | AD5941 bioimpedance / EIS analyser | 95.0 | 0.04 |
| Heimann HTPA80x64d thermopile array | 350.0 | 5 outcomes | Muon detector (CosmicWatch) | 100 | 0.04 |
| Hydrophone | 45.0 | 4 outcomes | Scintillating gamma spectrometer | 150 | 0.04 |
| DW1000 UWB two-way ranging radio | 40.0 | 5 outcomes | Benewake TF03 long-range industrial LiDAR | 180.0 | 0.04 |
| SprintIR-W fast wide-range NDIR CO2 | 190.0 | 4 outcomes | Ferroelectret bed sensor (ballistocardiography) | 130.0 | 0.04 |
| Sap flow probe (heat-ratio method) | 620.0 | 3 outcomes | Heimann HTPA32x32d thermopile array | 140.0 | 0.04 |
| ATECC608B secure element | 6.0 | 3 outcomes | 4-20mA loop pressure transmitter | 150.0 | 0.03 |
| BH1750 lux sensor | 2.5 | 5 outcomes | Alphasense NO2-B43F electrochemical cell | 120.0 | 0.03 |
| SDS011 particulate | 20 | 3 outcomes | MAXM86161 reflective PPG module | 120.0 | 0.03 |
| Ikea VINDRIKTNING hack | 13 | 3 outcomes | Omron D6T-32L 1024-pixel thermopile array | 200.0 | 0.03 |
| INIR NDIR methane module | 130.0 | 3 outcomes | FLIR Lepton 3.5 | 240 | 0.03 |
| Type 4 safety light curtain | 800.0 | 5 outcomes | FLIR Lepton 3.1R radiometric thermal module | 180.0 | 0.03 |
| LSM6DSO32 high-range IMU | 13.0 | 5 outcomes | Flexible Rogowski coil with integrator | 150.0 | 0.03 |
| MAX17048 ModelGauge fuel gauge | 6.0 | 2 outcomes | UM980 triple-band RTK receiver | 200.0 | 0.03 |
| LC709203F fuel gauge (end of life) | 8.0 | 2 outcomes | Dissolved oxygen kit (Atlas EZO-DO) | 170 | 0.02 |
| DWM1001C UWB module with ready-made RTLS firmware | 22.0 | 5 outcomes | ZED-F9P RTK centimetre GNSS | 260 | 0.02 |
| AM312 mini PIR | 2 | 5 outcomes | RD200 radon sensor | 180 | 0.02 |
| VCNL4040 proximity + lux | 6 | 7 outcomes | M6E-Nano UHF RAIN RFID reader | 275.0 | 0.02 |
| PAA5100JE near-field optical flow | 25.0 | 5 outcomes | Ammonium ion-selective electrode | 189.0 | 0.02 |
| EDA done properly - constant-voltage skin conductance | 8.0 | 3 outcomes | SprintIR-W fast wide-range NDIR CO2 | 190.0 | 0.02 |
| VL53L4CX multi-target ToF | 15.0 | 6 outcomes | TI AWR1642 77GHz automotive radar EVM | 299.0 | 0.02 |
| Vibrating-fork level switch | 90.0 | 5 outcomes | UM982 dual-antenna RTK with true heading | 260.0 | 0.02 |
| STCC4 low-cost percent CO2 | 18.0 | 4 outcomes | InfiRay P2 Pro USB-C thermal camera | 270.0 | 0.02 |
| AS5600 magnetic angle | 3 | 4 outcomes | METER TEROS 12 soil moisture, EC and temperature | 220.0 | 0.02 |
| XY-MD02 Modbus RTU temperature & humidity transmitter | 11.0 | 4 outcomes | ZED-F9R dead-reckoning GNSS | 280.0 | 0.02 |
| 4-20mA loop pressure transmitter | 150.0 | 5 outcomes | Alphasense PID-AH2 photoionisation VOC | 320.0 | 0.02 |
| ICM-45686 premium 6-axis IMU | 12.0 | 5 outcomes | Hamamatsu C12880MA micro-spectrometer | 330.0 | 0.02 |
| Tactile pressure array | 25.0 | 5 outcomes | Heimann HTPA80x64d thermopile array | 350.0 | 0.01 |
| OPT3001 photometric lux sensor | 8.0 | 4 outcomes | Paddlewheel insertion flow sensor | 320.0 | 0.01 |
| 600/1024PPR optical encoder | 12 | 4 outcomes | 352C33 IEPE piezoelectric accelerometer | 450.0 | 0.01 |
| NEO-F10T dual-band GNSS timing receiver | 120.0 | 3 outcomes | True TDR soil water content probe | 395.0 | 0.01 |
| 10MHz GPSDO — GNSS-disciplined oscillator | 130.0 | 2 outcomes | OpenBCI Cyton 8-channel biosensing board | 499.0 | 0.01 |
| BMI323 6-axis IMU | 8.0 | 5 outcomes | Alphasense OPC-N3 optical particle counter | 500.0 | 0.01 |
| SCA3300 industrial inclinometer/accelerometer | 50.0 | 5 outcomes | Apogee SQ-500 full-spectrum quantum (PAR) sensor | 400.0 | 0.01 |
| Capacitive proximity switch M18 | 7.0 | 5 outcomes | Livox Mid-360 3D LiDAR | 749.0 | 0.01 |
| InfiRay P2 Pro USB-C thermal camera | 270.0 | 5 outcomes | Type 4 safety light curtain | 800.0 | 0.01 |
| STC31 percent-level CO2 | 28.0 | 4 outcomes | ADIS16505-2 tactical-grade IMU | 825.0 | 0.01 |
| MPS flammable gas and refrigerant sensor | 85.0 | 4 outcomes |  |  |  |
| Inductive proximity switch M12/M18 | 2.5 | 6 outcomes |  |  |  |
| BMA400 ultra-low-power accelerometer | 13.0 | 5 outcomes |  |  |  |
| ID809 capacitive fingerprint module | 32.0 | 3 outcomes |  |  |  |
| VEML6030 ambient light sensor | 6.0 | 4 outcomes |  |  |  |
| ISM330DHCX industrial IMU | 20.0 | 5 outcomes |  |  |  |
| Retro-reflective photoelectric sensor | 70.0 | 5 outcomes |  |  |  |
| APDS-9960 gesture/color/prox | 6 | 5 outcomes |  |  |  |
| Vertical float level switch (reed) | 4.0 | 4 outcomes |  |  |  |
| NDIR methane / hydrocarbon module | 45 | 3 outcomes |  |  |  |
| Thermal microflow sensor for liquids | 150.0 | 3 outcomes |  |  |  |
| D6T thermal presence | 55 | 4 outcomes |  |  |  |
| VL53L4CD short-range precision ToF | 12.0 | 5 outcomes |  |  |  |
| TMP36 analog temp | 1.5 | 4 outcomes |  |  |  |
| Ultrasonic liquid (through-wall) | 25 | 4 outcomes |  |  |  |
| Sharp GP2Y0A21 IR distance | 8 | 6 outcomes |  |  |  |
| LEM LA 55-P closed-loop Hall current transducer | 35.0 | 4 outcomes |  |  |  |
| MH-Z19C budget NDIR CO2 | 18 | 5 outcomes |  |  |  |
| SenseAir S8 CO2 | 25 | 5 outcomes |  |  |  |
| YRM100 low-cost UHF reader module | 32.0 | 4 outcomes |  |  |  |
| MQ-6 LPG/propane | 2.5 | 3 outcomes |  |  |  |
| MLX90621 16x4 fast thermal array | 60.0 | 5 outcomes |  |  |  |
| SW-520D ball tilt switch | 0.5 | 4 outcomes |  |  |  |
| Frustration-free moisture: plant leaf clip | 5 | 3 outcomes |  |  |  |
| Point dendrometer (stem diameter) | 70.0 | 3 outcomes |  |  |  |
| Telaire T6713 I2C CO2 | 80.0 | 4 outcomes |  |  |  |
| MPR121 12-pad cap touch | 6 | 6 outcomes |  |  |  |
| ESP32 native touch pins | 0 | 6 outcomes |  |  |  |
| ESP32 internal sensors (free!) | 0 | 4 outcomes |  |  |  |
| LEM IT 60-S ULTRASTAB fluxgate current transducer | 900.0 | 3 outcomes |  |  |  |
| VL6180X short-range ToF | 8 | 5 outcomes |  |  |  |
| Fluoride ion-selective electrode (LaF3 crystal) | 320.0 | 2 outcomes |  |  |  |
| Tire pressure TPMS receivers | 10 | 4 outcomes |  |  |  |
| SenseAir K30 NDIR CO2 | 95.0 | 4 outcomes |  |  |  |
| Cubic CM1107N dual-beam CO2 | 30.0 | 4 outcomes |  |  |  |
| TSOP38238 38kHz IR receiver | 1.0 | 4 outcomes |  |  |  |
| EeonTex piezoresistive fabric | 15.0 | 4 outcomes |  |  |  |
| Button / pancake load cell | 25.0 | 4 outcomes |  |  |  |
| Narrowband O2 sensor (HEGO) | 15 | 3 outcomes |  |  |  |
| ALS-PT19 ambient light phototransistor | 3.0 | 3 outcomes |  |  |  |
| Linear potentiometer / softpot | 6 | 3 outcomes |  |  |  |
| Embroidered / fabric antenna | 10.0 | 2 outcomes |  |  |  |
| MEMS ultrasonic ToF (Chirp) | 15.0 | 4 outcomes |  |  |  |
| Guided-wave radar level transmitter | 290.0 | 3 outcomes |  |  |  |
| Conductive thread + fabric pads | 8 | 4 outcomes |  |  |  |
| GPS PPS time source | 10 | 1 outcomes |  |  |  |
| TTP223 single touch | 0.5 | 4 outcomes |  |  |  |
| KY-040 rotary encoder | 1 | 2 outcomes |  |  |  |
| Oscillometric blood-pressure module (cuff, pump, valve) | 60.0 | 2 outcomes |  |  |  |
| Trill flexible touch sliders | 20 | 4 outcomes |  |  |  |
| CAP1188 8-channel capacitive touch | 8.0 | 2 outcomes |  |  |  |
| Joystick module | 1.5 | 1 outcomes |  |  |  |
| AT42QT1070 / QT1010 touch controller | 4.0 | 1 outcomes |  |  |  |
| GT911 / FT6236 touchscreen controller | 6.0 | 1 outcomes |  |  |  |
