# 06 — Transmissive finger-clip pulse oximeter

> **This is a wellness and research build. It is not a medical device.** Nothing described here is
> validated, cleared or calibrated to any clinical standard, and no number it produces may be used
> to make a clinical decision, to withhold care, or to reassure anyone that they are well. If you
> are worried about someone's breathing, call a clinician — do not consult a breadboard.

**Incumbent:** Takuo Aoyagi's 1972 insight, productised through the 1980s: pulse two LEDs at ~660 nm
(red) and ~940 nm (infrared) through a fingertip, isolate the pulsatile (AC) part of each from the
steady (DC) part, form the ratio of ratios, and read saturation off an empirical curve fitted to
controlled desaturation studies in healthy volunteers — historically light-skinned ones.
**Claims to detect:** Arterial oxygen saturation, SpO2, as a percentage.
**Actually measures:** `R = (AC₆₆₀/DC₆₆₀) / (AC₉₄₀/DC₉₄₀)` — a dimensionless ratio of modulation
depths at two wavelengths. Saturation is not measured at all; it is looked up.

## The gap
R is a property of whatever pulsates in the optical path, not of arterial blood specifically. The
inference from R to SpO2 assumes that the only thing modulating absorbance at the pulse frequency is
arterial haemoglobin, that only two species absorb, and that the tissue between the LED and the
photodiode matches the population the curve was fitted on. Every one of those assumptions is
routinely false: motion modulates the path length, venous blood sloshes, melanin and nail polish sit
in the beam as fixed attenuators that change DC without changing AC, carbon monoxide absorbs almost
exactly like oxygen at 660 nm, and a cold finger shrinks AC toward the noise floor. The device
cannot tell any of this apart, because a lookup table has one input.

## What fools it
| Fools it | Why, physically | Atlas source |
| --- | --- | --- |
| Carbon monoxide | COHb absorbs almost identically to O₂Hb at 660 nm, so two wavelengths cannot separate them | `S368` `fools`: "A two-wavelength oximeter is blind to carboxyhaemoglobin, which absorbs almost identically to oxyhaemoglobin at 660nm — a poisoned patient reads a reassuring 98%." |
| Skin pigmentation | The calibration curve is empirical and its population was not representative | `S368` `fools`: "published work (Sjoding et al., NEJM 2020) found commercial oximeters over-estimated saturation about three times as often in patients with darker skin, meaning a home-brewed curve inherits an even larger bias." |
| Motion | Any path-length modulation at the pulse frequency enters R as if it were blood | `S112` `fools`: "Motion artefact is the dominant error and it is not a small effect: any movement swamps the pulse waveform completely, which is exactly why every serious wearable pairs this with an IMU purely to throw beats away." |
| Squeezing the clip | Contact pressure changes both AC and DC, and unequally at the two wavelengths | `S112` `fools`: "Contact pressure changes both signal amplitude and the apparent SpO2 ratio, so squeezing the sensor changes the 'oxygen saturation'." |
| Nail polish, cold fingers, low perfusion | They cut AC until beat detection tracks noise | `S368` `fools`: "Dark nail polish, acrylic nails, cold fingers, hypotension and vasoconstriction all shrink the pulsatile signal until beat detection starts tracking noise." |
| Room lighting | 100/120 Hz LED ripple leaks around the clip and aliases into the pulse band | `S112` `fools`: "Ambient light leaking around the edge of the sensor injects mains-frequency ripple — 100/120 Hz from LED lighting aliases straight into the pulse band at low sample rates." |
| The wrist, generally | Reflective AC is 0.1–1% of DC, so R is a quotient of two tiny noisy numbers | `S369` `fools`: "the ratio of ratios that saturation depends on is a quotient of two tiny, noisy numbers whose errors do not cancel... regulators treat wrist saturation as wellness rather than measurement." |

## What the underlying phenomenon actually is
The phenomenon worth measuring is **pulsatile optical absorbance in tissue, and the conditions under
which that absorbance is interpretable**. The transduction path is unchanged — **Electroluminescence**
drives the LEDs and **Photoelectric / photovoltaic** conversion reads the photodiode, both named in
`data/physics.py` — but the honest design does not try to replace the R-curve. It measures the
things the R-curve silently assumes: how much the finger is moving (**Capacitive** MEMS
accelerometry), how well it is perfused (the perfusion index PI = AC_IR/DC_IR the front end already
computes), what the tissue's baseline optical density is (broadband reflectance, as a pigment proxy),
what the ambient light is doing (a flicker channel), and how vasoconstricted the finger is
(**Thermoresistive** skin temperature). Then it adds one channel that needs no optical calibration at
all: **pulse transit time**, the delay between the ECG R-wave and the arrival of the pressure pulse
at the finger, which is a timing measurement, not an absorbance one.

## Proposed ESP32 stack
| Role | Part | `pn` | id | ~USD | Captures |
| --- | --- | --- | --- | --- | --- |
| Transmissive red/IR front end | AFE4490 transmissive pulse-oximetry front end | `AFE4490` | `S368` | 55 | Raw AC and DC at both wavelengths, with LED drive and AGC under your control |
| Synchronised ECG + PPG | MAX86150 ECG+PPG combo | `MAX86150` | `S217` | 23 | One FIFO, one timebase — the only honest way to compute PTT |
| Motion reference | BMI270 wearable IMU | `BMI270` | `S205` | 8 | Per-beat artefact veto; posture |
| Skin temperature | MAX30208 clinical-accuracy skin temperature | `MAX30208` | `S370` | 10 | ±0.1 °C — vasoconstriction and cold-finger gating |
| Ambient + pigment + flicker | AS7341 11-channel spectral | `AS7341` | `S052` | 14 | 350–1000 nm reflectance baseline; mains-flicker channel |
| Second, reflectance site | MAX30102 pulse oximeter | `MAX30102 / MAX30101` | `S112` | 6 | Cross-site agreement test — disagreement means one site is lying |

**Board:** ESP32-S3 (`B003`, $8) · **Sensor total:** ~$116 · **Build:** ~$124

The S3 is chosen for PSRAM: PTT needs both raw streams buffered at ≥250 sps, and the AS7341's
two-pass multiplexed read has to be time-stamped against them.

## The fusion
**Edge:** `spo2-conditions-gated` — **new edge — not in fusion.py.** No existing edge in
`data/fusion.py` requires `ppg-optical`; the closest relatives are `apnea-two-channel` (two
independent physics before escalating) and `sleep-two-signal` (movement gating a physiological
channel), and this edge applies the same discipline to oximetry.

**Math (mine, new):**
`Emit R = (AC₆₆₀/DC₆₆₀)/(AC₉₄₀/DC₉₄₀) for a beat only if ALL of: band-limited |a|₀.₅₋₁₀Hz < 20 mg over the beat window (BMI270); PI = AC_IR/DC_IR > 0.5 %; AS7341 flicker-channel power at 100/120 Hz < 1 % of the PPG DC level; MAX30208 skin temp > 30 °C. Report SpO2 only as an offset-corrected trend, SpO2_trend = f(R) − Δ_subject, where Δ_subject is fitted once at rest against a reference oximeter and is valid for that person only. Carry PTT = t(PPG_foot) − t(ECG_R) alongside as an independent, absorbance-free circulatory channel.`

**Confound (mine, new):** The gate improves *honesty*, not *accuracy* — it tells you when the number
is uninterpretable, and refuses to print one, which is the entire benefit. It cannot correct the
pigment bias: the AS7341 reflectance baseline is a proxy for optical density, not a melanin
measurement, and `S052` `fools` warns that its bands "blue-shift with the angle of incoming light"
and that "The photodiodes are read through a multiplexer in two passes", so a flickering source
makes the spectrum itself an artefact. PTT drifts too: `S217` `fools` states plainly that it
"requires per-person calibration against a real cuff and drifts with posture, temperature and
vascular tone; treating it as absolute blood pressure is not defensible." And the CO blindness is
structural — two wavelengths cannot become four by fusion.

**Why it beats the incumbent:** A finger clip prints 98% whether the finger is warm, cold, moving,
poisoned or nail-polished. This build prints a number only when four independent conditions say the
number is meaningful, and otherwise prints "not interpretable" — which is the correct output most of
the time and one no consumer oximeter will give you. PTT adds a circulatory channel that does not
route through the R-curve at all, so the two channels fail for different reasons.

## What this costs you
- **It refuses to answer more often than the incumbent does.** That is the design, and users hate it.
- **Warm-up.** `S368`: "2-10s for automatic gain control and the probe to settle on a finger."
  `S370`: "a skin patch takes 5-15 minutes to reach equilibrium after application". `S205`'s gyro
  needs its CRT self-trim at every power-up, and the ~8 kB Bosch config blob must be uploaded on
  every boot or you silently get accelerometer-only.
- **Calibration burden.** `S368`, `S112` and `S369` all carry `calibration: Reference` — the atlas's
  hardest class, "Needs lab standards or calibration gas to mean anything". `S112` is blunt: "no
  hobby build can produce the desaturation study that calibration actually requires."
- **Power.** `S368` `pwr_ua: 12000` and LED drive dominates; `S112`'s "600µA average figure hides"
  20–50 mA LED bursts that will brown out a coin cell. This is a LiPo build.
- **Consumables and wear.** Gel electrodes for the ECG channel are single-use. `S112`: "the optical
  window scratches and skin oil films it — a clouded window silently loses perfusion index over
  months of wear."
- **Privacy.** `S112` and `S217` are both `privacy: Identifiable`. A single-lead ECG is biometric —
  the atlas notes on `S362` that "a single-lead ECG is sufficient to identify a person in a closed
  set — the stored waveform is biometric data, not anonymous telemetry." Keep it on-device.
- **Difficulty.** `S217` is `diff: 4`. This is analog front-end work, not a Qwiic cable.

## Verdict
**Moderate — genuinely better epistemics, not better oximetry.** The reinvention replaces a device
that always answers with one that knows when it cannot, and it adds an independent timing channel;
both are real gains. It does not fix the two things that actually matter clinically — the pigment
bias in the R-curve and CO blindness — because fixing those needs more wavelengths and a desaturation
study, neither of which $124 buys. Confidence: high that the gating works, low that the resulting
SpO2 is more accurate than a $20 clip. This would be worth building only if you accept from the
outset that its output is a trend for one calibrated person, and never a diagnosis for anyone.
