# 07 — Reed-switch door/window contact

**Incumbent:** A pair of ferrous reeds sealed in a glass envelope with an inert fill. Bring a magnet
near and the reeds magnetise, attract and snap shut; take it away and their own spring opens them.
Invented at Bell Labs by W. B. Ellwood in 1936 and mass-produced for telephone switching, it became
the alarm-industry door contact essentially unchanged: one glass tube on the frame, one magnet on
the door, one pair of wires.
**Claims to detect:** That the door or window is open.
**Actually measures:** Whether the magnetic flux threading a small glass capsule exceeds the reeds'
pull-in threshold — roughly 10–20 ampere-turns — in the one orientation the reeds are sensitive to.

## The gap
"The magnet is near the reed" and "the door is closed" are separate propositions that happen to
coincide when nobody is trying and nothing has moved. They come apart in every direction at once: a
second magnet held against the frame makes them coincide with the door wide open; a door lifted off
its hinges or a pane broken beside the frame leaves them coinciding while the opening is defeated;
a frame that settles 4 mm makes them stop coinciding while nothing at all has happened. And even
when the proposition is true, it is a bare binary with no arrow on it — the switch cannot say
whether the door swung in or out, whether one person or six passed through, or whether it opened at
all versus was simply left ajar. It also has to be powered to be reported, which is how a switch
that draws exactly zero ends up eating a coin cell every eighteen months.

## What fools it
| Fools it | Why, physically | Atlas source |
| --- | --- | --- |
| A second magnet | The reed integrates total flux; it cannot tell whose flux it is | `S085` `fools`: "Any magnet held near it holds the switch closed — that is the classic alarm bypass, and it is why real security reeds are balanced-biased types that detect an added external magnet." |
| Mounting the magnet 90° round | Reeds are directional and have a null axis | `S085` `fools`: "Reeds are directional: a magnet approaching in the null orientation will not close them at all, which is why a door sensor that worked on the bench fails when the magnet is mounted 90° round." |
| Contact bounce | Up to a millisecond of chatter reads as five openings | `S085` `fools`: "Contacts bounce for up to a millisecond, so an interrupt handler without debounce counts one door opening as five" |
| Vibration and slams | Shock chatters the contacts and eventually cracks the glass, silently | `S085` `fools`: "a door slam that hammers the reed against its housing cracks it — after which it fails silently stuck open or stuck closed, and 'the door has not opened in three days' looks exactly like a quiet house." |
| A settling frame | Alignment must hold to a few millimetres for years | `S085` `requires`: "a mechanical alignment that stays within a few millimetres for the life of the install — a settling door or a warped frame is the usual cause of a 'failed' sensor." |
| Wear | The contacts are the consumable, and arcing kills them fast | `S085` `consumable`: "roughly 10⁸ operations dry-switched, but arcing an inductive or capacitive load pits and welds them within thousands." |

## What the underlying phenomenon actually is
A door is not a magnet; a door is **a moving panel that displaces air, rotates about a hinge, and
transfers momentum into the frame**. Each of those is directly measurable. The air displacement is
the best of them: swinging a door pressurises the whole building envelope by a few pascals, and
`data/physics.py` gives the route as **Piezoresistive** transduction in a MEMS barometer, which now
resolves single pascals — so a sensor in a completely different room hears the door. The rotation is
**Capacitive** MEMS accelerometry plus a magnetometer for absolute swing angle and direction. The
impact and the glass are **Piezoelectric**. And whether anything actually went through the opening
is a **Photoelectric** time-of-flight measurement across the threshold. None of these can be spoofed
by holding a magnet against the frame, because none of them is asking about flux.

## Proposed ESP32 stack
| Role | Part | `pn` | id | ~USD | Captures |
| --- | --- | --- | --- | --- | --- |
| The cheap end, kept | Reed switch | `MKA14103 class / door sets` | `S085` | 0.5 | Zero-power baseline state and a deep-sleep wake source |
| Door-swing pressure transient | BMP390 precision barometer | `BMP390 / BMP388` | `S016` | 10 | ±3 Pa relative — the 0.3–3 Pa door pulse, from anywhere in the house |
| Swing angle and magnet spoofing | BMM350 TMR magnetometer | `BMM350` | `S300` | 7 | 3-axis field to ±2000 µT: an added magnet is a field vector that does not belong |
| Hinge motion, direction, force | BMA400 ultra-low-power accelerometer | `BMA400` | `S299` | 13 | 14.5 µA always-on; which way the panel rotated, and how hard |
| Did anyone go through | VL53L4CD short-range precision ToF | `VL53L4CD` | `S331` | 12 | 1 mm–1.3 m, real millimetres across the threshold |
| Glass and forced frame | Piezo shock/knock element | `LDT0-028K` | `S097` | 3 | Impact transients, glass break beside the frame |
| Clamp for the piezo | Input protection (TVS, PTC, series R) | `SMAJ5.0A TVS / PTC resettable fuse / Schottky clamps` | `G033` | 1 | `S097` delivers tens of volts on a hard strike |

**Board:** ESP32-C6 (`B006`, $6) · **Sensor total:** ~$46.5 · **Build:** ~$52.5

The C6 is the right board here: 802.15.4 for Thread/Zigbee/Matter alongside Wi-Fi, and low sleep
current. Note `S085` `esp32_compat`: "C3/C6/H2 expose only a small set of wake-capable pins" — check
the pinout before assigning the reed, the BMA400 INT and the comparator output.

## The fusion
**Edge:** `door-baro-locator` — Barometric door locator (data/fusion.py)
**Math:** `A door swing is a ~0.3–3 Pa transient; arrival order + amplitude ratio across 3 synced nodes localises the source`
**Confound:** HVAC blower starts and wind gusts through vents make similar transients: fingerprint each door's signature (fast attack, slow decay) during a quiet week first.

**Cost of the edge, stated honestly:** it `requires` `('pressure-absolute', 3)` — *three* independent
pressure nodes with a shared timebase, not one. The build above is one full door node; completing
the triangulation needs two further barometer-only nodes at roughly $16 each (`S016` $10 + `B006`
$6), taking the house total to about **$85**. That is still under a single commercial "smart" door
sensor multipack, and it covers *every* door in the house rather than one.

**Second edge:** `passage-direction` — **new edge — not in fusion.py.**
**Math (mine, new):** `Direction = sign of the door's magnetometer heading change over the swing, cross-checked against the BMA400 rotation axis; passage = a ToF range collapse from >800 mm to <400 mm and back, lasting 0.3–1.5 s, occurring within the swing window. Count = number of such collapses per swing. Forced entry = a piezo impact > 3× the learned slam distribution with NO preceding magnetometer heading change.`
**Confound (mine, new):** `S331` `fools` is the limiting factor: its "18° cone is wide: at 1m it
covers a 32cm circle, so a doorframe or table edge clipping the cone wins over the target you
actually care about", and "Black matte fabric and dark car paint return about 5% and roughly halve
the range". Two people abreast count as one. `S300` `fools` warns that "a magnetometer inside your
own project mostly measures your own project" — the BMM350 must be mounted as far as physically
possible from the C6 module and any switching regulator, and needs a hard-iron/soft-iron fit in situ.

**Why it beats the incumbent:** The barometer answers "which door opened" with no sensor on any
door, so there is nothing to align, nothing to spoof and nothing visible to defeat. The magnetometer
turns the classic magnet bypass into a *detection*: a spoofing magnet is an anomalous field vector
that the reed reports as "closed" while the BMM350 reports as "an extra 300 µT appeared". The piezo
and the accelerometer see the two events a reed is structurally blind to — a door taken off its
hinges and a pane broken beside the frame. And the ToF answers the question the incumbent never
even asks: whether anyone actually came through.

## What this costs you
- **Power, badly.** The reed's `pwr_ua: 0.0` was the incumbent's best feature and it is gone.
  `S331` draws "~18mA average while ranging continuously, ~40mA peak during the VCSEL burst" — you
  must gate it on the reed or the BMA400 interrupt and range only during a swing. `S016` at 3.2 µA
  and `S299` at 14.5 µA are affordable always-on; the ToF is not. This is a rechargeable-cell or
  USB build, not a CR2032 build.
- **Warm-up and thermal drift.** `S016` `fools`: "a unit warming up after power-on, or sitting where
  sun crosses it, drifts several pascals — tens of centimetres of apparent altitude — over minutes,
  and it looks like the sensor is watching something move." Per `S016` `requires`, the static
  port must be vented but wind-shielded: "a plain hole in a box is not a static port."
- **Calibration.** `S300` is `calibration: Two-point` and needs a hard-iron/soft-iron ellipsoid fit
  per install. `S016` needs a one-week quiet-house fingerprinting run before the locator means
  anything, per the edge's own confound.
- **Wind and HVAC.** `S016` `fools`: "Wind across an enclosure opening creates Bernoulli suction of
  tens of pascals, so 'a door opened' and 'a gust hit the house' are indistinguishable without a
  properly shielded static port."
- **The piezo is a bad outdoor sensor.** `S097` `fools`: "PVDF is pyroelectric as well as
  piezoelectric — a warm hand near it, a draught, or sunlight moving across it produces a slow
  signal indistinguishable from a slow bend."
- **Privacy.** Every part here is `privacy: None` or `Aggregate`, which is the good news: this
  counts passages without identifying anyone. But a whole-house pressure log is a fine-grained
  record of when people moved between rooms, and should be treated as such.
- **Difficulty and price.** ~$52 per door node against $8 for a reed pair, and three nodes minimum
  before the headline capability exists at all.

## Verdict
**Strong on the security failures, moderate on everyday door state.** The magnet bypass, the door
off its hinges and the broken pane are three blind spots the incumbent cannot see by construction,
and this stack sees all three for the price of one commercial contact multipack. The barometric
locator is the genuinely new capability — whole-house entry awareness with nothing on any door.
Confidence: high on spoof detection and forced-entry detection; medium on the locator, which would
have to be true that your house is quiet enough for a 0.3 Pa transient to stand clear of HVAC and
wind, and that three nodes can hold a shared timebase over ESP-NOW well enough to order arrivals.
For simply knowing whether the back door is shut, the $0.50 reed is still the correct answer.
