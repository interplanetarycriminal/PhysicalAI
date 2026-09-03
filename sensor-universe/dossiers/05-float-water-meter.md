# 05 — Domestic water meter

**Incumbent:** A nutating-disc or oscillating-piston positive-displacement meter: water pushes a
disc that wobbles once per fixed chamber volume, a magnet on the disc spindle turns a gear train,
and a mechanical register counts revolutions. The architecture is essentially unchanged since the
Kennedy and Worthington disc meters of the 1870s–80s; the only modern additions are a magnetic
coupling through the case and, sometimes, a reed pulse output.
**Claims to detect:** How much water your house used, in cubic metres, for billing.
**Actually measures:** The cumulative number of revolutions of one mechanical element, integrated
over a month, above the flow rate at which the disc will move at all.

## The gap
A positive-displacement meter is an integrator with a dead band and no clock. It answers exactly
one question — how many chamber-volumes have passed since installation — and it answers it at a
temporal resolution of whenever a human walks up and reads the dial. That single scalar cannot be
differentiated back into fixtures, because everything downstream of the meter shares one pipe, and
it cannot be differentiated in time, because nobody sampled it in time. Below the disc's starting
torque the count is not merely inaccurate, it is zero: a running toilet or a pinhole leak passes
water the register never sees. And a burst pipe and a normal Tuesday produce the same object — a
larger number — distinguishable only after the bill arrives.

**Note on sourcing:** the domestic nutating-disc meter is not itself a record in this dataset. The
atlas's nearest analogues, quoted below, are the turbine meter `S138` (same dead-band physics, same
integrating role) and the reed pickup `S085` that retrofit pulse kits bolt to utility meters.

## What fools it
| Fools it | Why, physically | Atlas source |
| --- | --- | --- |
| A running toilet, a dripping tap, a pinhole | Below the mechanism's starting flow nothing turns, so the leak you bought it for is invisible | `S138` `fools`: "below about 1 L/min the impeller does not turn and a dripping tap, a slow toilet fill or a pinhole leak — the exact things you bought it for — are completely invisible. This is why 'zero flow at 3 am' is a far better leak signal than 'a small flow'." |
| Short draws (a hand-wash, a kettle fill) | Startup inertia means the first few hundred millilitres are under-registered every time | `S138` `warmup`: "the impeller takes a few hundred millilitres to spin up from rest, so short draws like a hand-wash are systematically under-counted" |
| Air in the main after plumbing work | The mechanism counts volume, not mass; entrained air manufactures litres | `S138` `fools`: "Air in the line spins the impeller freely and manufactures litres, so totals inflate after any plumbing work or in a system that gulps air." |
| Grit, scale, a seized mechanism | A jammed meter reads flat, which is indistinguishable from an empty house | `S138` `fools`: "one piece of pipe swarf jams the impeller and the reading drops to zero, which looks exactly like nobody using water." |
| The retrofit reed pulse kit | Contact bounce multiplies counts; a magnet defeats it entirely | `S085` `fools`: "Contacts bounce for up to a millisecond, so an interrupt handler without debounce counts one door opening as five... Any magnet held near it holds the switch closed" |
| A leak inside a wall | Floor-level leak ropes only see water that reaches the floor, hours or days late | `S141` `fools`: "Most expensive water damage starts inside a wall, above a ceiling or behind an appliance and reaches the floor hours or days later, by which time the flooring is gone — a rope is a last line, not an early warning." |

## What the underlying phenomenon actually is
The thing worth measuring is not accumulated volume but the **time series of flow**, plus the
**structure-borne acoustic signature the flow imprints on the pipe wall**. A pressurised pipe is a
waveguide: every valve, every turbulent restriction and every leak orifice injects broadband noise
into the metal, and each fixture has a different orifice, a different flow rate and a different
opening transient. Four transduction routes in `data/physics.py` give access to it without cutting
the pipe: **Piezoelectric** (the pipe wall's vibration becomes charge, in the piezo disc),
**Convective cooling** (moving water strips heat from the pipe, which is how thermal flow works),
**Blackbody emission / conduction** (surface temperature separates a hot-line draw from a cold one),
and **Induction (Faraday)** (a CT clamp reads the booster or well pump without touching the wiring).
Transit-time ultrasound adds a genuinely quantitative velocity: sound with the flow arrives sooner
than sound against it, and the difference is the mean velocity across the bore.

## Proposed ESP32 stack
| Role | Part | `pn` | id | ~USD | Captures |
| --- | --- | --- | --- | --- | --- |
| Whole-house flow, nothing wetted | Transit-time ultrasonic flow (clamp-on) | `TUF-2000M + ESP32 Modbus` | `S234` | 85 | L/min at 1 Hz, totaliser, through the pipe wall |
| RS-485 to the meter | MAX485 RS-485 transceiver | `MAX485` | `G006` | 2 | Modbus RTU link (use the 3.3 V variant) |
| Pipe-wall acoustics ×2 | Piezo contact mic / disc | `27mm piezo disc` | `S091` | 0.5 ea | Structure-borne 200 Hz–5 kHz: fixture signature and leak hiss |
| Front end for the discs | Charge amplifier for piezo sensors | `LMP7721 / TL072-based charge amp` | `G021` | 6 | High-Z buffer so sub-100 Hz survives the ADC |
| Calibrated pipe vibration | LIS3DH budget accel | `LIS3DH` | `S078` | 3 | Wake-on-motion gate; real g for valve-slam transients |
| Hot and cold surface temp | DS18B20 digital temp probe ×2 | `DS18B20` | `S001` | 2.5 ea | Which line is running; energy in a hot draw |
| Pump / booster current | SCT-013 CT clamp | `SCT-013-000 (100A)` | `S147` | 10 | Pump duty cycle, well-pump short-cycling |
| ADC for the CT and piezo | ADS1115 / ADS1015 16-bit ADC | `ADS1115 (16-bit) / ADS1015 (12-bit)` | `G015` | 3 | 16-bit differential; ESP32 ADC2 dies with Wi-Fi on |

**Board:** ESP32 classic (WROOM-32E) (`B001`, $6) · **Sensor total:** ~$115 · **Build:** ~$121

**A gap I could not source.** The stack has no line-pressure channel, because the dataset does not
contain a cheap 0–10 bar water-line transducer. `S021` MPRLS (`MPRLS0025PA00001A`, $15) tops out at
25 PSI absolute — below mains supply pressure, so it would simply saturate. The only real option is
`S254` Gems 3100 series 4-20mA pressure transmitter ($150) plus `G002` RCV420 loop receiver ($22),
which doubles the build. I have left both out rather than pretend a $15 part covers it.

## The fusion
**Edge:** `pipe-leak-correlator` — Acoustic pipe-leak correlator (data/fusion.py)
**Math:** `Leak position from cross-correlation lag: x = (L − v·Δt)/2, v ≈ 1200–1400 m/s in water-filled metal pipe`
**Confound:** Plastic pipe attenuates and slows the wave (v drops to ~300–500 m/s and range shrinks): calibrate v with a deliberate tap at a known point first.

**Edge:** `leak-by-context` — Occupancy-gated leak detector (data/fusion.py)
**Math:** `Alarm when flow > 0 sustained > 10 min AND nobody-present > 30 min`
**Confound:** Washing machines and irrigation run legitimately when out: whitelist their schedules or their flow signatures first.
The `someone-present` half comes free here: `S091` lists `someone-present` among its inferences, so
the same discs that hear the pipe also hear the house.

**Edge:** `water-fixture-nilm` — **new edge — not in fusion.py**
**Math (mine, new):** `Segment the 1 Hz flow series on edges |ΔQ| > 0.3 L/min; classify each segment by the vector (ΔQ_step, rise time, piezo band power 200 Hz–5 kHz, hot-probe dT/dt, coincident pump ΔI_rms). A toilet refill is a 4–8 L monotonic fill terminated by an abrupt valve close; a shower is >5 min at near-constant Q with the hot probe rising 15–25 K; a washing machine is a fill–pause–fill sequence locked to its own motor current.`
**Confound (mine, new):** Two fixtures of similar bore running together are as fundamentally
inseparable as the kettle/toaster pair in `nilm-signature` — one measurement point cannot resolve
two simultaneous same-signature loads. Mixer taps blur the hot/cold discriminator. The piezo bond
ages, and `S091` `fools` is explicit that "any bond that ages shifts your baseline, which quietly
destroys trend-based maintenance", so the classifier needs periodic re-referencing.

**Why it beats the incumbent:** The register gives you one number a month; this gives you flow at
1 Hz, so a toilet that fills at 0.4 L/min for six hours is a visible 144-litre rectangle instead of
nothing at all. The occupancy gate turns "flow" into "leak" in ten minutes rather than in arrears,
and the correlator then tells you *where* to dig or open the wall — the same physics the water
utility's £10k correlator uses. Nothing is cut, nothing is wetted, and the utility meter stays
sealed and legal.

## What this costs you
- **Money and difficulty.** $121 against a meter that came with the house, and `S234` is `diff: 4`.
- **Install pain, not electronics.** `S234` `warmup`: "expect 15-30 minutes of adjusting transducer
  spacing, re-greasing and re-clamping before signal quality is above the usable threshold". It
  needs pipe outside diameter, **wall thickness** and material entered by hand; a 1 mm wall error
  gives a confidently wrong number. Cast iron often returns no signal at all.
- **Consumables.** `S234` `consumable`: "Ultrasonic couplant is the consumable... Silicone grease
  dries out and signal quality falls over weeks to months outdoors." Plan a re-grease schedule.
- **Drift.** `S234` `calibration: One-point`, and it "will happily report tens of litres per hour
  unless you perform a zero calibration with flow stopped — and that zero must be redone seasonally."
- **Power.** This is a mains build, not a coin cell: `S234` draws `pwr_ua: 167000` (2 W at 12–24 V),
  plus 18 mA-class housekeeping. The old meter drew nothing.
- **Mains safety.** `S147` carries `hazard: ['Mains']`. It clamps one conductor only; around a whole
  flex it reads zero.
- **Privacy.** `S234` is `privacy: Aggregate`, but `S091` is `privacy: Raw-imagery` — its `fools`
  warns "stuck to a wall it picks up conversation in the next room, a privacy consequence nobody
  anticipates". Filter and discard raw audio on-device; do not stream it.
- **Clone risk.** `S234` is `lifecycle: Clone-risk`: "the Modbus register map differs between
  firmware revisions and between clone vendors selling the identical-looking box."

## Verdict
**Strong on leaks, moderate on billing-grade metering.** Detecting a burst in minutes instead of a
month is a step change no amount of register-reading reaches, and the correlator's leak *location*
is a capability the incumbent does not have at any price. Fixture disaggregation is plausible but
unproven at this price: it would have to be true that each fixture's acoustic signature is stable
across bond ageing and that simultaneous draws are rare enough to ignore. Confidence: high on the
leak claim, medium on disaggregation, low on ever beating ±1% of a sealed utility meter.
