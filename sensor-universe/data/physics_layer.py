"""The physics layer: what each transducer ACTUALLY responds to.

Every other field in the catalog describes a part as its vendor describes it —
"humidity sensor", "distance sensor", "CO2 sensor". That framing is a label, not
a mechanism, and it is what makes a sensor surprise you in the field. A
capacitive RH sensor does not measure humidity; it measures the dielectric
permittivity of a polymer film that sorbs water, which is why a solvent vapour
reads as rain and why a hot PCB reads as dry air. A time-of-flight ranger does
not measure distance; it measures the arrival-time distribution of returned
photons, which is why a black cat at 1 m and a white wall at 3 m can read the
same. This module records the mechanism, so the atlas can say what a signal
implies about the world rather than only what the box says it means.

Contract
--------
`PX` maps a frozen sensor id (`data/ids.json`) to a dict of the `px_*` fields
defined in `schema.FIELDS`. Nothing else. No derived values are authored here:
coverage counts are computed by `coverage()`, and the overlay is applied by
`loader.load_all()` after the three enrichment overlays, so a physics-layer
entry wins on conflict.

Any sensor with no entry here loads as `{"px_status": "unfilled"}`. That default
is what makes coverage honest by construction: the 405 sensors nobody has done
the physics for are marked unfilled because they ARE unfilled, not because
someone typed 405 stub records.

STATUS: 40 of the 405 sensors are authored, in four research groups (thermal /
chemical, optical / nuclear, mechanical / acoustic, electrical / RF / bio) —
36 `filled` against a versioned manufacturer datasheet, 4 `partial` whose
`px_ref` begins `VERIFY:` because no such document exists for the part. The
remaining 365 load as `unfilled`. Extending coverage means adding entries to
`PX` below and nothing else.

Rules for an entry (enforced by `px_report.py`, which exits non-zero if a
record claims `filled` and is not):
  * `px_status="filled"` requires ALL of measurand, units, effect, range,
    resolution, bandwidth, drift, implies, AND a citation (`px_ref` +
    `px_ref_kind`). Anything less is `"partial"`.
  * `px_range`, `px_resolution` and `px_bandwidth` are expressed in `px_units`
    — the units of the REAL measurand, which may not be the labelled ones.
  * `px_bandwidth` is the -3 dB bandwidth or response time constant. It is
    deliberately a different field from `rate`, which is sample rate: a sensor
    that reports at 10 Hz through a 30 s thermal time constant is not a 10 Hz
    instrument, and conflating the two is how people build filters that lie.
  * `px_cross` tokens must exist in `vocab.PHYSQTY` (extend that list — see the
    note there — if a real cross term has no token yet). `px_cross_note` says,
    per term, the mechanism, the sign, and the magnitude.
  * Never invent a number, a document title or a URL. If the mechanism is known
    but the figure is not, write `"VERIFY: …"` in the field and leave the record
    `"partial"` — a gap is worth more than a plausible lie.

Example of the exact shape (uncomment and replace with a real, cited record):

# PX = {
#     "S001": dict(
#         px_status="filled",
#         px_measurand="dielectric permittivity of a sorbing polymer film",
#         px_units="relative permittivity (dimensionless), read as pF",
#         px_effect="water sorption into a polymer dielectric; parallel-plate capacitance",
#         px_chain="Chemical,Electrical",
#         px_cross=["temperature", "voc", "condensation", "aging-drift"],
#         px_cross_note=(
#             "temperature: sorption isotherm shifts, +x %RH per K near saturation; "
#             "voc: solvents sorb into the same film and read as humidity, sign positive; "
#             "condensation: liquid water saturates the film, output pins until it dries"
#         ),
#         px_range="…, in px_units",
#         px_resolution="… noise floor / LSB, in px_units",
#         px_bandwidth="… response time constant, e.g. 8 s to 63% in still air",
#         px_drift="… per year, plus tempco",
#         px_implies=(
#             "what a reading from this part tells you about the world beyond its "
#             "label — e.g. a step with no temperature step is a solvent, not weather"
#         ),
#         px_ref="<document title> rev <n> — <url>",
#         px_ref_kind="datasheet",
#     ),
# }

Where the data goes: `PX` below.
"""

import schema

# ---------------------------------------------------------------- the table
# id -> {px_* field: value}. This is the ONLY place per-sensor physics data
# lives: never in `data/part*.py`, never in an enrichment overlay. Entries are
# grouped by the research group that authored them and sorted by frozen id
# inside each group. See the module docstring for the shape of one entry.
PX: dict[str, dict] = {

    # ========================================================================
    # Thermal and chemical — 10 sensors.
    # S001, S004, S006, S007, S012, S024, S036, S038, S134, S290
    # ========================================================================

    "S001": {
        "px_status": "filled",
        "px_measurand": (
            "Temperature of the DS18B20's own silicon die. The part does not sense the "
            "medium; it senses itself, and reports the medium only to the extent that the "
            "TO-92/probe package has come into equilibrium with it."
        ),
        "px_units": "K (reported as degC, 1/16 degC LSB)",
        "px_effect": (
            "Dual-oscillator ratiometric temperature-to-digital conversion: a low-tempco "
            "reference oscillator gates a counter clocked by a strongly "
            "temperature-dependent oscillator whose frequency follows the "
            "bandgap/carrier-mobility temperature dependence of the die. The ratio of the "
            "two counts is the temperature word. Bandgap-referenced, so the reading is "
            "nominally independent of VDD."
        ),
        "px_chain": "Thermal,Electrical",
        "px_cross": [
            "self-heating", "thermal-gradient", "supply-voltage", "contact-resistance",
            "cable-capacitance", "condensation", "aging-drift",
        ],
        "px_cross_note": (
            "self-heating: the datasheet gives 1.0-1.5 mA active supply current at 5 V, so "
            "~5-7.5 mW is dissipated in the die for the whole 750 ms of a 12-bit conversion. "
            "In a bare TO-92 in still air (junction-to-ambient on the order of 150-250 K/W) "
            "back-to-back conversions therefore push the reading high by several tenths of a "
            "degC; the same part in a stainless probe in water self-heats immeasurably. The "
            "self-heating error is a function of the medium, not of the sensor -- which is "
            "why it is exploitable (see px_implies). Sign is always positive. "
            "thermal-gradient: a probe on a 1 m cable conducts heat along its own leads and "
            "sheath; a 3 mm stainless spear in 60 degC compost with its head in 15 degC air "
            "reads low by a stem-conduction error that grows as the immersion depth falls "
            "below ~10 probe diameters. supply-voltage: second-order because the conversion "
            "is ratiometric and bandgap referenced (3.0-5.5 V spec), but parasite-power mode "
            "couples the bus pull-up directly into the conversion, and the datasheet forbids "
            "parasite power above +100 degC because die leakage then starves the internal "
            "storage capacitor. contact-resistance / cable-capacitance: 1-Wire is a "
            "slew-limited open-drain bus; tens of metres of cable plus a corroded splice "
            "slow the edges enough that CRC failures appear as an intermittent temperature, "
            "not as a comms error. The failure mode is silent, so cable state is aliased "
            "into the data. condensation: probe potting is the only barrier -- water ingress "
            "shows first as a leakage path on the 1-Wire line (bus stuck low, all-85 degC "
            "power-on-reset value) rather than as a temperature error. 85.00 degC exactly is "
            "a wetness/wiring alarm. aging-drift: datasheet quotes +/-0.2 degC after 1000 h "
            "at +125 degC, 5.5 V."
        ),
        "px_range": "-55 to +125 degC; +/-0.5 degC accuracy over -10 to +85 degC",
        "px_resolution": (
            "0.0625 degC LSB at 12-bit (9-12 bit programmable); quantisation, not noise -- "
            "the part is essentially noise-free at 12 bits and the error budget is the "
            "+/-0.5 degC absolute term."
        ),
        "px_bandwidth": (
            "Conversion takes 750 ms at 12 bits, but that is not the bandwidth. The thermal "
            "time constant of the packaging dominates: a bare TO-92 in still air is roughly "
            "20-60 s, the same die in a 6 mm stainless probe in stirred water is a few "
            "seconds, and that probe in still air is minutes. Read the datasheet number as a "
            "floor and the package as the real low-pass filter."
        ),
        "px_drift": (
            "+/-0.2 degC after 1000 h at +125 degC / 5.5 V (datasheet stress test). No "
            "annual drift figure is published; silicon bandgap references of this class are "
            "stable to well under 0.1 degC/yr at room temperature, and the practical "
            "long-term error in the field is probe corrosion and cable, not the die."
        ),
        "px_implies": (
            "A DS18B20 reading is a statement about the probe's thermal equilibrium, not "
            "about the air or the water. Three consequences nobody puts on the label: (1) "
            "two identical probes a known distance apart in the same medium measure heat "
            "flux, not temperature -- a wall stack with an inner and outer DS18B20 and a "
            "known R-value is a W/m2 sensor, and the same pair on a flow pipe with a known "
            "heater is a calorimetric flow meter; (2) the self-heating step is a free active "
            "experiment -- convert back-to-back for 10 s, then idle, and the size and decay "
            "of the resulting bump measures the local heat transfer coefficient, i.e. wet vs "
            "dry, buried vs exposed, still air vs draught, without any second sensor; (3) "
            "the time constant itself is the medium: a probe whose step response suddenly "
            "shortens has been immersed. Fill-level, irrigation onset, and a compost pile "
            "turning from aerobic to soaked are all readable from tau alone."
        ),
        "px_ref": (
            "DS18B20 Programmable Resolution 1-Wire Digital Thermometer, Maxim/Analog "
            "Devices, Rev 6, 7/19, "
            "https://www.analog.com/media/en/technical-documentation/data-sheets/ds18b20.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S004": {
        "px_status": "filled",
        "px_measurand": (
            "The net Seebeck EMF developed around the thermocouple loop -- an integral of "
            "the Seebeck coefficient along the wire between the hot end and the isothermal "
            "terminal block, plus the cold-junction die temperature measured separately "
            "on-chip. A thermocouple does not measure junction temperature; it measures the "
            "temperature difference across the wire, and the EMF is generated in the wire, "
            "not at the bead."
        ),
        "px_units": "V (K-type ~41 uV/K), reported as K after linearisation",
        "px_effect": (
            "Seebeck effect in a chromel/alumel pair, plus on-die cold-junction "
            "compensation. The MAX31855 assumes a single fixed sensitivity of 41.276 uV/degC "
            "(datasheet) and adds the cold-junction temperature; the true type-K Seebeck "
            "coefficient is not constant -- per the NIST ITS-90 thermocouple reference "
            "functions (SRD 60) it is about 39.5 uV/degC at 0 degC, peaks near 42 uV/degC "
            "around 300 degC, and falls again above 1000 degC. The linearisation error is "
            "folded into the datasheet's +/-2 degC (-200 to +700 degC) and +/-4 degC (+700 "
            "to +1350 degC) accuracy bands."
        ),
        "px_chain": "Thermal,Electrical",
        "px_cross": [
            "thermal-gradient", "temperature-of-electronics", "mechanical-stress",
            "contact-resistance", "ground-noise", "emi-rf", "supply-voltage", "aging-drift",
        ],
        "px_cross_note": (
            "thermal-gradient is the dominant error and it is an error in the *board*, not "
            "the probe. The MAX31855 measures the cold junction at its own die with 0.0625 "
            "degC resolution and +/-2 degC accuracy (-20 to +85 degC), but the actual "
            "copper-to-thermocouple transition is at the screw terminal a few millimetres "
            "away. Any gradient between die and terminal adds to the reading at ~1 degC per "
            "1 degC of gradient -- a nearby regulator, a fan, or sunlight on the board "
            "injects a full-scale-independent offset. The single most common field failure "
            "of a thermocouple channel is that somebody warmed the connector. "
            "temperature-of-electronics: same mechanism seen from the other side -- the "
            "reported hot-junction temperature is (EMF/41.276) + T_die, so any error in "
            "T_die passes straight through with unity gain regardless of how hot the tip is. "
            "A 1200 degC furnace reading inherits the board's 2 degC uncertainty in full. "
            "mechanical-stress: thermoelectric inhomogeneity. Cold-working, kinking or "
            "oxidising a length of chromel/alumel changes its local Seebeck coefficient, and "
            "because the EMF is generated wherever the wire crosses a gradient, a damaged "
            "spot matters only when it happens to lie in the gradient. Moving the same probe "
            "in the same furnace changes the reading by degrees. This also means a "
            "thermocouple is microphonic/position-sensitive in a way an RTD is not. "
            "contact-resistance: the MAX31855 is an open-circuit-detecting voltage input, so "
            "series resistance itself contributes little error, but its OC/SCG/SCV fault "
            "bits are the useful signal -- a rising intermittent OC rate is corrosion or a "
            "cracked sheath long before the temperature looks wrong. ground-noise and "
            "emi-rf: the loop is a ~40 uV/K source, so 40 uV of common-mode leakage is one "
            "whole degree. An ungrounded-tip probe touching a grounded machine frame creates "
            "a ground loop; a grounded-tip probe on a VFD-driven motor picks up "
            "kilovolt-per-microsecond common-mode steps. The datasheet's SCG/SCV bits catch "
            "the gross case; the subtle case is a quiet DC offset. supply-voltage: 3.0-3.6 "
            "V, 0.9-1.5 mA; the ADC is internally referenced so rail noise mostly appears as "
            "conversion-to-conversion jitter rather than gain error. aging-drift: type-K "
            "drifts by tens of degC after long exposure above ~600 degC (chromel green-rot "
            "in low-oxygen atmospheres, alumel oxidation); this is a property of the wire, "
            "and no amount of front-end quality fixes it."
        ),
        "px_range": (
            "K-type -200 to +1350 degC at the tip (datasheet -270 to +1372 degC with +/-6 "
            "degC over the full extended band); cold junction -55 to +125 degC."
        ),
        "px_resolution": (
            "0.25 degC per LSB on the thermocouple channel (14-bit), 0.0625 degC on the "
            "cold-junction channel. 0.25 degC corresponds to ~10 uV -- so the LSB, not the "
            "noise, is the floor for slow work; for fast work the useful resolution is set "
            "by how well you can keep 10 uV of interference off the leads."
        ),
        "px_bandwidth": (
            "70-100 ms conversion time, so ~10 samples/s. The physical bandwidth is entirely "
            "the probe: an exposed 0.25 mm bead junction in moving gas has a time constant "
            "of tens of milliseconds (genuinely useful for flame and exhaust transients), a "
            "3 mm grounded sheath is ~1 s, and a 6 mm mineral-insulated probe in a "
            "thermowell is 10-60 s. The same MAX31855 can be a 10 Hz instrument or a 0.02 Hz "
            "one depending on which probe you screw into it."
        ),
        "px_drift": (
            "Front end: +/-2 degC cold-junction accuracy over -20 to +85 degC, +/-3 degC "
            "over -40 to +125 degC. Wire: type-K special-limits tolerance is +/-1.1 degC or "
            "0.4 % of reading, and drift in service above 600 degC is the real long-term "
            "term, tens of degC over hundreds of hours in reducing atmospheres."
        ),
        "px_implies": (
            "Because the EMF comes from the wire crossing a temperature gradient, a "
            "thermocouple channel is really a gradient-position sensor with a thermometer "
            "bolted on. Off-label uses that follow: (1) the cold-junction register is a "
            "free, independent, 0.0625 degC board thermometer -- log it and you have an "
            "enclosure-temperature and solar-load channel you did not pay for, and its "
            "divergence from a nearby DS18B20 is a self-heating measurement of the "
            "enclosure; (2) the OC/SCG/SCV fault bits turn the part into a continuity and "
            "insulation monitor: a probe on a moving machine that intermittently asserts OC "
            "is reporting vibration and cable fatigue, not temperature; (3) inhomogeneity "
            "cuts both ways -- deliberately pulling a long thermocouple through a furnace "
            "wall and watching the EMF change tells you where the gradient is, so the probe "
            "becomes a crude 1-D temperature-profile scanner; (4) with a milliwatt heater at "
            "the tip, the same junction becomes a self-heated hot-junction anemometer that "
            "works at 800 degC where no semiconductor survives."
        ),
        "px_ref": (
            "MAX31855 Cold-Junction Compensated Thermocouple-to-Digital Converter, Maxim "
            "Integrated, 19-5793 Rev 5, 1/15, "
            "https://www.analog.com/media/en/technical-documentation/data-sheets/max31855.pdf"
            " (non-linearity context: NIST ITS-90 Thermocouple Database SRD 60, type K "
            "inverse coefficients, "
            "https://srdata.nist.gov/its90/type_k/kcoefficients_inverse.html)"
        ),
        "px_ref_kind": "datasheet",
    },

    "S006": {
        "px_status": "filled",
        "px_measurand": (
            "The temperature of the sintered metal-oxide bead itself, transduced as the "
            "bead's bulk DC resistance. The bead is a wide-gap semiconductor whose carrier "
            "concentration is thermally activated, so R falls exponentially with T."
        ),
        "px_units": "K (read out as ohms)",
        "px_effect": (
            "Thermally activated conduction in a Mn/Ni/Co spinel ceramic: R(T) = R25 * "
            "exp[B*(1/T - 1/T25)], refined by the Steinhart-Hart form the Vishay datasheet "
            "prints as R(T) = Rref * exp(A + B/T + C/T^2 + D/T^3). NTCLE100E3103: 10 kohm at "
            "25 degC, B25/85 = 3977 K +/-0.75 %. Sensitivity alpha = -B/T^2 = -4.5 %/K at 25 "
            "degC -- an order of magnitude larger than a Pt100's +0.39 %/K, which is why an "
            "NTC beats an RTD on resolution and loses to it on range and interchangeability."
        ),
        "px_chain": "Thermal,Electrical",
        "px_cross": [
            "self-heating", "airflow", "reference-drift", "supply-voltage",
            "contact-resistance", "humidity", "condensation", "emi-rf", "aging-drift",
        ],
        "px_cross_note": (
            "self-heating and airflow are the same mechanism and are the most useful "
            "cross-sensitivity in this whole record. The datasheet lists a still-air "
            "dissipation factor in the 7-8.5 mW/K band and a 15 s thermal time constant in "
            "air. A 10 k bead in a 10 k/3.3 V divider dissipates V^2/R = 1.65^2/10k = 0.27 "
            "mW at balance -> only +0.04 K of self-heat; drive the same bead directly from 5 "
            "V and it dissipates 2.5 mW -> +0.36 K, and that offset is not constant: forced "
            "convection raises the dissipation factor several-fold (King's law, delta ~ a + "
            "b*sqrt(v)), so the self-heat offset shrinks with wind speed. Sign: reading "
            "falls as airflow rises, at fixed excitation. reference-drift: in a divider the "
            "answer is R_ntc/R_series, so the series resistor's tempco is a direct error. A "
            "100 ppm/K series resistor sitting on a board that swings 30 K contributes 0.3 % "
            "in ratio = 0.07 K of apparent temperature; a 1 % carbon-film part at 500 ppm/K "
            "contributes 0.33 K. Put the reference resistor where the NTC is, or measure it. "
            "supply-voltage: a ratiometric divider read against the same rail cancels VDD to "
            "first order; an ESP32 ADC referenced internally does not, and its ~+/-1 % INL "
            "and attenuator nonlinearity are usually the dominant error, worth 0.2-0.5 K. "
            "contact-resistance: at 25 degC a 10 k bead has ~450 ohm/K of slope, so 1 ohm of "
            "lead/solder/connector resistance is only ~0.002 K -- negligible warm, but at "
            "-40 degC the bead is ~200 kohm and the same 1 ohm is invisible, while at +125 "
            "degC it is ~340 ohm and 1 ohm is now 0.03 K. The error is "
            "temperature-dependent. humidity / condensation: the failure is leakage, not "
            "calibration. A film of condensate across the lead pair is a resistor in "
            "parallel with the bead; because the bead is high-impedance when cold, surface "
            "leakage of 1 Mohm biases a -30 degC reading warm by degrees while doing nothing "
            "at +100 degC. Conformal coat or expect a humidity-shaped seasonal error. "
            "emi-rf: a bare high-impedance bead on a long unshielded pair is an antenna "
            "feeding a high-Z ADC input; RF rectification at the ADC shows up as a DC "
            "temperature offset that appears when a transmitter keys up. aging-drift: "
            "typical for this class is 0.2-0.5 % of R25 in the first year at moderate "
            "temperature, i.e. ~0.05-0.1 K, rising sharply if the part is operated near its "
            "150 degC short-term limit."
        ),
        "px_range": (
            "-40 to +125 degC continuously (<=150 degC short term), zero-power. R spans "
            "about 34 kohm at 0 degC to 3.6 kohm at 50 degC for B = 3977 K."
        ),
        "px_resolution": (
            "Set by the readout, not the bead. At balance dV/dT = (Vcc/4)*alpha = 37 mV/K on "
            "3.3 V, so a 12-bit ESP32 ADC (~0.8 mV LSB) quantises at ~0.02 K and averages to "
            "~0.005 K. Absolute accuracy is far worse: +/-0.75 % on B and +/-1 % on R25 give "
            "about +/-0.3 K at 0 degC and +/-0.9 K at -30 degC for an uncalibrated part."
        ),
        "px_bandwidth": (
            "15 s thermal time constant in still air for the radial-leaded bead (datasheet, "
            "'for information only'). ~1 s in stirred water, and sub-100 ms for a bare "
            "glass-encapsulated micro-bead in gas flow -- which is why the nasal-cannula "
            "airflow build in this catalogue works at breathing rates."
        ),
        "px_drift": (
            "B25/85 tolerance +/-0.75 % is a systematic, not a drift. Long-term: a few "
            "tenths of a percent of R25 per year under mild conditions; irreversible upward "
            "R shift after excursions above ~125 degC. Tempco of the whole channel is "
            "dominated by the series reference resistor (see cross note)."
        ),
        "px_implies": (
            "An NTC is not really a thermometer, it is a resistor whose value depends on how "
            "much power it can shed. Run it cold (microwatts) and it reports the medium's "
            "temperature; run it hot (milliwatts) and it reports the medium's ability to "
            "carry heat away, which is a function of velocity, density, phase and wetness. "
            "The same 10-cent bead is therefore an anemometer, a liquid-level switch (the "
            "dissipation factor jumps roughly 10x on immersion, so the self-heat offset "
            "collapses the instant the bead is wetted), a foam/froth detector, a vacuum "
            "gauge below about 10 mbar where conduction becomes pressure-dependent (the "
            "Pirani principle), and a presence detector for anything that changes the local "
            "draught. Two beads, one self-heated and one not, subtract out the ambient and "
            "give you flow directly. Reading the exponential the other way: because alpha is "
            "10x an RTD's, an NTC resolves millikelvin differences cheaply, so a matched "
            "pair is a differential calorimeter good enough to see a hand near a surface or "
            "a heat pipe start to work."
        ),
        "px_ref": (
            "NTC Thermistors, Radial Leaded, Standard Precision (NTCLE100E3 series), Vishay "
            "BCcomponents, Document Number 29049, revision 07-May-2025, "
            "https://www.vishay.com/docs/29049/ntcle100.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S007": {
        "px_status": "filled",
        "px_measurand": (
            "Net radiant power per unit area in the ~5.5-14 um band arriving at the "
            "thermopile from within the field of view, referenced to the sensor's own can "
            "temperature. That flux is emissivity-weighted and view-factor-weighted: it is "
            "sigma*(eps*T_obj^4 + (1-eps)*T_surround^4 - T_can^4) folded with the optics, "
            "not a temperature."
        ),
        "px_units": "W/m2 (reported as K after assuming an emissivity)",
        "px_effect": (
            "Thermopile radiometry: incoming IR heats a thin membrane, a series stack of "
            "thermocouple junctions on that membrane generates a Seebeck EMF proportional to "
            "the membrane-to-rim temperature difference, and an on-die PTAT sensor supplies "
            "the reference (T_a). Stefan-Boltzmann fourth-power law plus a user-settable "
            "emissivity register (range 0.1-1.0, factory value 1.0)."
        ),
        "px_chain": "Radiant,Thermal,Electrical",
        "px_cross": [
            "surface-emissivity", "target-reflectivity", "ir-radiation", "target-geometry",
            "thermal-gradient", "temperature-of-electronics", "sunlight-load", "condensation",
            "dust-fouling", "humidity",
        ],
        "px_cross_note": (
            "surface-emissivity is not a nuisance here, it is half the physics. With the "
            "register left at eps = 1.0, a target at 35 degC in a 22 degC room reads 0.6 "
            "degC low if its true emissivity is 0.95 and 1.2 degC low at 0.90 (solve T_meas "
            "= [eps*T^4 + (1-eps)*T_amb^4]^(1/4)). The error scales with (T_obj - "
            "T_surround), so it is near zero when the target is at room temperature and "
            "enormous on a hot target in a cold room -- and it inverts sign if the "
            "surroundings are hotter than the target. On polished metal (eps ~ 0.05) the "
            "instrument is essentially reading the room reflected in the target. "
            "target-reflectivity / ir-radiation: the (1-eps) term is a mirror. A shiny "
            "surface makes the MLX90614 a specular IR camera looking at whatever is behind "
            "the sensor -- including the operator's own face, and including the sun. "
            "target-geometry: the xAA parts have a 90 deg FOV, xBA 70 deg, xCC 35 deg. At 90 "
            "deg the spot diameter is about 2x the standoff distance, so at 300 mm you are "
            "averaging a 600 mm patch. A 'forehead temperature' at arm's length is a "
            "weighted average of forehead, hair, wall and window. Every reading is a "
            "view-factor average; there is no such thing as a point measurement with this "
            "part. thermal-gradient and temperature-of-electronics: the datasheet warns that "
            "IR sensors are 'inherently susceptible to errors caused by thermal gradients' "
            "and to avoid transient conditions. The measurement is differential against the "
            "TO-39 can, so if one side of the can is warmer than the other -- a hand holding "
            "it, a regulator underneath, a draught -- the object reading shifts by a large "
            "fraction of the gradient. After a thermal shock the part needs minutes, not "
            "milliseconds, to settle even though its digital output updates in 0.1 s. "
            "sunlight-load: direct sun both heats the can (gradient error) and puts "
            "shortwave energy through the silicon window; the germanium/silicon filter cuts "
            "most of it but the thermal loading remains. Outdoors, a sunlit MLX90614 reads "
            "its own solar gain as much as the sky. condensation / dust-fouling: the window "
            "is the aperture. A film of dew, grease or dust is an emitter at the sensor's "
            "own temperature in series with the target, which pulls every reading toward "
            "T_can -- so a fouled sensor looks stable and boring, the most dangerous failure "
            "mode there is. humidity: water vapour absorbs strongly in parts of the "
            "thermopile band, so over multi-metre paths (sky temperature, silo walls) the "
            "reading contains an atmospheric path term -- which is exactly what makes it a "
            "cloud sensor."
        ),
        "px_range": (
            "Object -70 to +380 degC, ambient -40 to +125 degC; +/-0.5 degC over 0-50 degC "
            "for both Ta and To (medical-grade DCI variants tighter over a narrow band)."
        ),
        "px_resolution": (
            "0.02 degC measurement resolution; ~0.05 degC RMS noise at the factory-default "
            "filter setting. In radiometric terms 0.05 degC on a 300 K target is about 0.3 "
            "W/m2 of flux -- roughly 0.1 % of the ~460 W/m2 a 300 K blackbody emits."
        ),
        "px_bandwidth": (
            "Two different bandwidths, and confusing them is the classic mistake. The "
            "radiometric channel settles in ~0.10 s at the factory IIR/FIR setting, so a "
            "passing warm object is resolvable at ~5-10 Hz. The ambient-compensation channel "
            "is limited by the thermal mass of the TO-39 can and its mount: minutes to "
            "re-equilibrate after being picked up, moved between rooms, or hit by sun. "
            "Polling at 100 Hz does not make the compensation faster."
        ),
        "px_drift": (
            "No annual drift figure is published; the dominant long-term terms are window "
            "contamination (monotonic pull toward T_can) and mechanical stress on the can "
            "from the mount. Ambient tempco is folded into the +/-0.5 degC over 0-50 degC "
            "and grows outside that band. Supply 4.5-5.5 V (Axx) at 1.3-2.5 mA."
        ),
        "px_implies": (
            "Because the output is emissivity- and view-factor-weighted, pointing an "
            "MLX90614 at a FIXED target turns it into an instrument for everything except "
            "temperature. On a fixed target at known temperature, changes in the reading are "
            "changes in emissivity and view factor, which means: (1) wetness detection -- "
            "water raises the emissivity of most dry materials toward 0.98 and cools the "
            "surface by evaporation, so a wet leaf, a sweating pipe or a damp patch of soil "
            "reads several degC different from its dry neighbour; (2) fill level through a "
            "wall -- liquid on the far side of a tank wall changes the wall's thermal mass "
            "and hence its surface temperature, so a vertical scan finds the meniscus "
            "without ever touching the contents; (3) occupancy and presence -- a 35 degC "
            "emitter entering a 20 degC field of view shifts the average by (spot "
            "fraction)*(15 K), so a 90 deg part is a slow, absolute-reading occupancy sensor "
            "that, unlike a PIR, still sees a person who has stopped moving; (4) "
            "sky-temperature / cloud detection -- pointed up, the reading is the effective "
            "radiating temperature of the atmosphere, typically -40 degC clear and near "
            "ambient under thick cloud, which makes a 3 dollar part a cloud-cover sensor, a "
            "frost-risk predictor (clear sky = radiative cooling below air temperature) and "
            "a dew-point alarm for anything outdoors; (5) as a differential emissivity "
            "probe, it separates materials -- painted vs bare metal, ice vs water, foam vs "
            "liquid -- at the same temperature."
        ),
        "px_ref": (
            "MLX90614 family -- Single and dual zone IR sensor in TO39, Melexis, datasheet "
            "Rev 021 (doc server rev 012), 02-Jun-2026, "
            "https://media.melexis.com/-/media/files/documents/datasheets/MLX90614-datasheet-"
            "melexis.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S012": {
        "px_status": "filled",
        "px_measurand": (
            "Water ACTIVITY at the surface of the sensor's hygroscopic polymer -- the "
            "equilibrium partial pressure of water vapour divided by the saturation pressure "
            "at the polymer's own temperature. Not water content, not absolute humidity, and "
            "not the humidity of the room unless the polymer is at the room's temperature. "
            "Plus, separately, the die temperature from an on-chip bandgap sensor."
        ),
        "px_units": "dimensionless water activity a_w (0-1, reported as %RH); K for the T channel",
        "px_effect": (
            "Capacitive humidity sensing: water sorbed into a thin polymer dielectric raises "
            "its permittivity (water's relative permittivity is ~80 against ~3 for the "
            "polymer), so a few hundred femtofarads of interdigitated capacitance tracks the "
            "polymer's equilibrium water uptake, which follows the sorption isotherm in "
            "activity. Temperature comes from a co-integrated bandgap sensor on the same "
            "die, which is what makes the pair thermodynamically meaningful."
        ),
        "px_chain": "Chemical,Electrical",
        "px_cross": [
            "temperature", "self-heating", "condensation", "hysteresis",
            "contamination-poisoning", "airflow", "aging-drift",
        ],
        "px_cross_note": (
            "temperature is not a cross-sensitivity here, it is a definitional coupling and "
            "it is enormous. RH is referenced to saturation pressure, which roughly doubles "
            "every 10 K, so at 50 %RH a 1 K error in the die temperature is about a 3 %RH "
            "error in the reported humidity -- three times the sensor's own +/-1.8 %RH typ "
            "accuracy. Every RH sensor is really a thermometer with a chemistry attached. "
            "self-heating: measurement current is 320-500 uA (about 1.6 mW at 3.3 V) against "
            "80 nA idle, and the on-chip heater can be commanded to 20, 110 or 200 mW. Any "
            "self-heat warms the die relative to the air and therefore biases RH LOW (the "
            "polymer sees a higher saturation pressure than the air does). Continuous "
            "high-repeatability polling on a small board with poor thermal isolation is "
            "worth a few tenths of a K and hence ~1 %RH; the 200 mW heater is worth many "
            "degrees and is meant to be used only in bursts. condensation: above ~95 %RH the "
            "polymer takes up bulk water and the reading pins and then recovers slowly "
            "(creep). Sensirion supplies the heater specifically for 'removal of condensed / "
            "spray water' and 'creep-free operation in high humid environments'. If you see "
            "100 %RH flat for hours, you are measuring a wet sensor, not wet air. "
            "hysteresis: 0.8 %RH at 25 degC. This is a memory of the wetting history, so a "
            "sensor cycled daily between 30 and 90 %RH reads systematically differently on "
            "the way up and the way down -- it matters for control loops and for any attempt "
            "to compare two sensors that have seen different histories. "
            "contamination-poisoning: the polymer is exposed to the air by design. Solvents, "
            "silicones, plasticisers, cigarette smoke and cleaning-agent vapours partition "
            "into it and shift the isotherm; Sensirion's own guidance is that recovery "
            "requires baking. VOC exposure is therefore a slow RH offset. airflow: the "
            "sensor responds to the air actually touching it. A 4 s tau63 is a "
            "still-air-boundary-layer number; in a dead pocket behind a filter or inside an "
            "enclosure the effective response is minutes and the reading is of the "
            "enclosure, not the room. aging-drift: typ <0.2 %RH/yr and <0.03 degC/yr -- "
            "unusually good, and the reason an SHT4x can be used as a transfer standard for "
            "cheaper parts."
        ),
        "px_range": "0-100 %RH (a_w 0-1), -40 to +125 degC",
        "px_resolution": (
            "0.01 %RH and 0.01 degC quantisation; repeatability 0.08 %RH / 0.04 degC at "
            "high, 0.15 %RH / 0.07 degC at medium, 0.25 %RH / 0.1 degC at low. Accuracy typ "
            "+/-1.8 %RH and +/-0.2 degC -- so the noise floor is 20x finer than the absolute "
            "accuracy, which makes the part far better at differences and rates of change "
            "than at absolute values."
        ),
        "px_bandwidth": (
            "tau63 = 4 s for RH, 2 s for T, in moving air with the sensor exposed. Behind a "
            "PTFE membrane or a filter cap, tens of seconds to minutes. The I2C interface "
            "will happily give you 10 Hz of correlated nonsense."
        ),
        "px_drift": (
            "typ <0.2 %RH/yr and <0.03 degC/yr; hysteresis 0.8 %RH at 25 degC; idle 0.08 uA, "
            "measurement 320-500 uA."
        ),
        "px_implies": (
            "RH and T on the same die let you compute dew point, and dew point -- unlike RH "
            "-- is conserved as air moves around and changes temperature. That single fact "
            "unlocks most of the off-label uses: (1) two SHT4x at the same dew point but "
            "different temperatures locate a heat source or a thermal bridge, and a surface "
            "whose temperature is below the room's dew point is going to get wet -- so an "
            "SHT4x plus any surface thermometer is a mould-risk and condensation-risk "
            "predictor with no extra hardware; (2) dew point rises when people breathe, "
            "cook, shower or water plants, so indoor absolute humidity is a fast occupancy "
            "and activity signal that PIRs miss; the step response of dew point after a door "
            "opens measures the air-change rate; (3) drive the on-chip heater at a fixed 110 "
            "or 200 mW and watch the temperature rise: the rise is inversely proportional to "
            "the local heat transfer coefficient, so the humidity sensor becomes an "
            "anemometer and a leak/draught detector; (4) because the part measures water "
            "ACTIVITY, sealed in a small headspace above a sample it becomes a "
            "water-activity meter for food, soil, grain and timber -- the quantity that "
            "actually predicts microbial growth, which no moisture-content meter gives you; "
            "(5) the hysteresis and creep behaviour is itself a wetting-history record."
        ),
        "px_ref": (
            "Datasheet SHT4x -- Humidity and Temperature Sensor, Sensirion, Version 7.1, "
            "March 2025, "
            "https://www.mouser.com/datasheet/3/1278/1/HT_DS_Datasheet_SHT4x_5.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S024": {
        "px_status": "filled",
        "px_measurand": (
            "Electrical conductance of a heated tin-oxide film, which responds to the net "
            "rate at which reducing species in the gas consume chemisorbed oxygen on the "
            "oxide surface. It is a non-selective redox-activity signal, not a concentration "
            "of any named gas: hydrogen, CO, ethanol, aldehydes, terpenes and siloxanes all "
            "move the same number."
        ),
        "px_units": "S (reported as SRAW ticks, proportional to log resistance, 0-65535)",
        "px_effect": (
            "Chemiresistance in a metal-oxide semiconductor film on a MEMS micro-hotplate. "
            "Atmospheric O2 chemisorbs on the SnO2 grain surfaces, trapping electrons and "
            "building a depletion layer that raises inter-grain barrier height; a reducing "
            "gas reacts with that adsorbed oxygen, releases the trapped electrons and lowers "
            "the barrier, so conductance rises roughly as a power law in partial pressure. "
            "Datasheet sensitivity: about -870 ticks per doubling of VOC concentration over "
            "0.3-30 ppm ethanol in clean air -- i.e. the raw signal is logarithmic in "
            "concentration."
        ),
        "px_chain": "Electrical,Thermal,Chemical,Electrical",
        "px_cross": [
            "humidity", "temperature", "self-heating", "gas-composition", "voc",
            "contamination-poisoning", "airflow", "supply-voltage", "aging-drift", "pressure",
        ],
        "px_cross_note": (
            "humidity is the largest interferent and the datasheet makes it structural: the "
            "measure_raw command REQUIRES relative humidity and temperature words to be sent "
            "with every measurement (RH/ticks = RH% * 65535, T/ticks = (T+45) * 65535), "
            "because adsorbed water dissociates on the oxide surface and donates electrons "
            "exactly as a reducing gas does. Sign: conductance rises (raw ticks fall) with "
            "rising RH. For MOX films of this class the uncompensated baseline shift across "
            "20-80 %RH at 25 degC is of the order of a factor of two in resistance -- "
            "comparable to a real VOC event, which is why an uncompensated SGP40 in a "
            "bathroom is a shower detector rather than an air-quality sensor. temperature "
            "and self-heating: the film is held on a temperature-controlled micro-hotplate "
            "(2.6 mA at 3.3 V running, 34 uA idle), so ambient temperature acts through the "
            "hotplate control loop and through the gas-phase kinetics; the specified "
            "operating window is only -10 to 50 degC. The hotplate also warms whatever sits "
            "beside it -- an SHT4x on the same PCB within a few millimetres will read warm "
            "and dry, corrupting the very RH value being fed back into the compensation. "
            "gas-composition / voc: there is no selectivity. Hydrogen and CO are strong "
            "responders; so is ethanol from hand sanitiser, so are terpenes from cleaning "
            "products, so is human skin emission. The 'VOC Index' is a rank statistic, not a "
            "concentration. contamination-poisoning: siloxanes are the classic MOX killer -- "
            "they decompose on the hot film and leave insulating SiO2. Sensirion's "
            "robustness claim is explicitly a test 'over simulated lifetime of 10 years in "
            "an indoor environment... continuous operation in 250 ppm of "
            "decamethylcyclopentasiloxane (D5) for 200 h'. Board wash and ultrasonic "
            "cleaning must be avoided and vapour-phase/manual soldering is forbidden -- flux "
            "residue is a permanent poison. airflow: the film reacts with the gas that "
            "reaches it; the <10 s tau63 assumes convective supply. Behind a mesh in still "
            "air the effective time constant is minutes. supply-voltage: the hotplate is "
            "power-controlled, so rail sag changes film temperature and hence the whole "
            "response surface -- a browning-out battery node produces a slow drift that "
            "looks like a real air-quality trend. aging-drift: the algorithm hides it. Raw "
            "resistance drifts substantially over months; the VOC Index re-normalises to a "
            "rolling window so the drift is expressed as a shrinking dynamic range rather "
            "than an offset. pressure: the reaction rate depends on the arrival rate of "
            "molecules at the surface, so at reduced total pressure (altitude, a sealed and "
            "cooling enclosure) the same mole fraction gives a smaller response. SAFETY: the "
            "sensing element is a micro-hotplate operated at several hundred degC. It is a "
            "small but real ignition source, it is not intrinsically safe, and it carries no "
            "flammable-gas certification. Do not use an SGP40 -- or any heated MOX part -- "
            "as a leak detector inside a volume that can reach the lower explosive limit of "
            "a fuel gas; that job needs a certified IR or an ATEX/IECEx-rated detector. The "
            "same warning applies with more force to pellistors and to the MQ-series parts "
            "elsewhere in this catalogue, whose bare heaters run at hundreds of milliwatts."
        ),
        "px_range": (
            "SRAW 0-65535 ticks (log-resistance); VOC Index 1-500 with 100 defined as the "
            "average indoor gas composition over the past 24 h. Specified over 0.3-30 ppm "
            "ethanol equivalent, -10 to 50 degC, 0-90 %RH non-condensing."
        ),
        "px_resolution": (
            "About -870 ticks per doubling of concentration, so one tick is ~0.08 % change "
            "in concentration-equivalent -- the quantisation is irrelevant next to the "
            "baseline uncertainty. Practically, the smallest trustworthy event is a few "
            "percent change in raw resistance over a few minutes."
        ),
        "px_bandwidth": (
            "tau63 < 10 s, tau90 < 30 s to a step in gas at the sensor face. But the VOC "
            "Index output is high-passed by a ~24 h adaptive baseline, so the system as "
            "delivered has a passband of roughly 0.03-0.1 Hz down to ~1e-5 Hz: it cannot see "
            "a slow, steady contamination at all, and it cannot see DC by construction."
        ),
        "px_drift": (
            "No absolute calibration exists to drift from; the specification is relative. "
            "Robustness is qualified by the D5 siloxane test above. Process the parts within "
            "1 year of delivery per the datasheet. Expect raw baseline resistance to move by "
            "tens of percent over the first weeks of operation (burn-in) and to keep moving "
            "slowly thereafter."
        ),
        "px_implies": (
            "The VOC Index is a normalised anomaly score against the last day of this room's "
            "own air -- so a value of 100 means 'normal for here, lately', not 'clean'. A "
            "permanently polluted room reads 100. Read that way, the part stops being an air "
            "quality sensor and becomes: (1) an event detector for anything that perturbs "
            "surface redox chemistry -- cooking, aerosol sprays, solvent use, a fridge door, "
            "a person entering, a 3D printer starting, alcohol on breath; the RAW signal, "
            "not the index, is what you want for this; (2) a humidity-transient detector, "
            "because of the RH cross-sensitivity: feed it constant fake RH/T and the raw "
            "signal becomes a fast (<10 s) proxy for water vapour steps, faster than most "
            "capacitive RH sensors behind filters; (3) a hydrogen detector at sub-ppm levels "
            "-- MOX films are unusually sensitive to H2, which makes an array of them a "
            "plausible early detector for lithium-cell off-gassing and for electrolysis "
            "leaks, but see the ignition warning above; (4) a smell-fingerprint channel when "
            "several parts are run at different hotplate temperatures or paired with an RH/T "
            "reference -- the differential between two MOX parts with different poisoning "
            "histories is itself informative; (5) a self-diagnosing contamination monitor: a "
            "collapsing dynamic range in RAW over weeks is a direct measurement of "
            "cumulative siloxane exposure in that room."
        ),
        "px_ref": (
            "Datasheet SGP40 -- Indoor Air Quality Sensor for VOC Measurements, Sensirion, "
            "version 1.2, February 2022, "
            "https://sensirion.com/media/documents/296373BB/6203C5DF/Sensirion_Gas_Sensors_Da"
            "tasheet_SGP40.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S036": {
        "px_status": "filled",
        "px_measurand": (
            "The amplitude of an acoustic pressure wave generated inside a sealed, "
            "gas-permeable cavity when a modulated IR pulse at the CO2 4.26 um band is "
            "absorbed by the CO2 molecules in that cavity and thermalised. The transducer is "
            "a MEMS microphone; the measurand is sound pressure, and CO2 is what modulates "
            "it. As with NDIR, the underlying quantity is molecular number density, not mole "
            "fraction."
        ),
        "px_units": "Pa (acoustic amplitude, reported as ppm CO2)",
        "px_effect": (
            "Photoacoustic spectroscopy (Sensirion PASens). Absorbed IR energy raises the "
            "local gas temperature at the modulation frequency; the sealed cavity converts "
            "that periodic heating into a periodic pressure, which a MEMS microphone detects "
            "synchronously. Because the signal is generated only where CO2 absorbs, the "
            "optical path can be millimetres instead of centimetres -- this is why the part "
            "is 10x10x7 mm while an NDIR module is a matchbox."
        ),
        "px_chain": "Electrical,Radiant,Chemical,Mechanical,Electrical",
        "px_cross": [
            "pressure", "altitude", "temperature", "humidity", "water-vapour", "self-heating",
            "acoustic-noise", "vibration", "airflow", "supply-voltage", "aging-drift",
        ],
        "px_cross_note": (
            "acoustic-noise and vibration are unique to this transduction and are the most "
            "surprising cross term in the whole thermal/chemical set: the detector is "
            "literally a microphone. Sensirion's design uses synchronous detection at the "
            "modulation frequency to reject ambient sound, but strong tonal noise or "
            "structure-borne vibration near that frequency (fans, compressors, ultrasonic "
            "cleaners, a phone speaker held against the module) degrades the measurement. "
            "Mounting the sensor rigidly to a vibrating panel is a measurable error source "
            "and is why datasheet design-in guidance is about mechanical isolation as much "
            "as about airflow. pressure and altitude: same Beer-Lambert-in-number-density "
            "argument as any NDIR part, and the datasheet exposes it directly -- "
            "set_ambient_pressure accepts 70000-120000 Pa and set_sensor_altitude accepts "
            "0-3000 m, and the reference pressure must be supplied before a forced "
            "recalibration. The datasheet does not print a %-per-hPa coefficient; the class "
            "figure of ~1.6 % of reading per kPa (Senseair K-30) is the right order. "
            "Uncompensated at 1500 m the reading is low by roughly a quarter. temperature: "
            "photoacoustic amplitude depends on the gas's heat capacity and on the cavity's "
            "thermal and acoustic properties, all temperature-dependent; the specification "
            "is quoted at 25 degC / 50 %RH and no separate CO2 tempco is published. "
            "self-heating: 15 mA typical at 3.3 V in periodic mode (about 50 mW) versus 3.2 "
            "mA in low-power and 0.45 mA single-shot. The datasheet states plainly that "
            "'SCD4x design-in, self-heating, operation mode and the surrounding environment "
            "affects RH/T sensor performance' -- the co-packaged RH/T channel reads warm and "
            "dry in periodic mode by a device- and enclosure-dependent amount, typically "
            "0.5-2 degC. Its +/-0.8 degC / +/-6 %RH specs already reflect this; do not use "
            "the SCD41's RH/T as a room measurement. humidity / water-vapour: water absorbs "
            "weakly in-band and, more significantly, changes the gas mixture's thermal "
            "properties and dilutes dry air by up to ~4 % at 30 degC/90 %RH. airflow: the "
            "cavity exchanges gas by diffusion through a membrane; tau63 is 60 s for a "
            "400-2000 ppm step. Enclosing the part without vents makes it a very slow "
            "integrator of its own box. aging-drift: 'additional accuracy drift per year, "
            "starting after five years: +/-(5 ppm + 0.5 % of reading)' -- excellent, but "
            "conditional on ASC ever seeing fresh air (the algorithm 'leverages the sensor's "
            "measurement history and the assumption that the sensor is exposed to a known "
            "minimum background CO2 concentration at least once during a period')."
        ),
        "px_range": (
            "400-5000 ppm (SCD41). Accuracy +/-(50 ppm + 2.5 % of reading) 400-1000 ppm, "
            "+/-(50 ppm + 3 %) 1001-2000 ppm, +/-(40 ppm + 5 %) 2001-5000 ppm."
        ),
        "px_resolution": "Repeatability typ +/-10 ppm; 1 ppm output quantisation.",
        "px_bandwidth": (
            "tau63 = 60 s for a 400-2000 ppm step -- diffusion-limited through the membrane. "
            "The signal update interval is 5 s in periodic mode, ~30 s in low-power mode, "
            "and the fastest single-shot interval is 5 s; none of those is the bandwidth. "
            "Sampling at 0.2 Hz over a 60 s time constant just gives you correlated samples."
        ),
        "px_drift": (
            "+/-(5 ppm + 0.5 % of reading) additional accuracy drift per year after the "
            "first five years, with ASC enabled and periodically exposed to a known "
            "background. FRC requires >=3 minutes of operation and a homogeneous, constant "
            "CO2 environment, with altitude/pressure set beforehand."
        ),
        "px_implies": (
            "Everything said about the MH-Z19C's rebreathed-air and air-change-rate physics "
            "applies here with better numbers, plus two things specific to photoacoustics: "
            "(1) the sensor is a calibrated microphone that happens to be selective to CO2 "
            "-- its susceptibility to structure-borne vibration means an SCD41 mounted on a "
            "machine reports, in its noise floor, when that machine is running. The "
            "correlation between CO2 residual noise and equipment state is a free "
            "machine-health channel; (2) because the measurand is number density and the "
            "pressure input is exposed as an API, running the part with a FIXED assumed "
            "pressure while the true pressure moves turns the CO2 residual into a barometric "
            "trace; run it with a real barometer and the same residual becomes a leak test "
            "for the enclosure it sits in. (3) the ASC baseline history is an "
            "occupancy-pattern record: the algorithm's own estimate of 'minimum background "
            "over the period' is the cleanest available signal for whether a room was ever "
            "unoccupied and ventilated. (4) CO2 decay after occupants leave gives air "
            "changes per hour directly, and the steady-state excess over outdoor gives "
            "litres/second/person of fresh air -- the two numbers that actually govern "
            "airborne transmission risk, neither of which is a carbon dioxide measurement in "
            "any meaningful sense."
        ),
        "px_ref": (
            "Datasheet SCD4x -- Breaking the size barrier in optical CO2 sensing, Sensirion, "
            "Version 1.7, April 2025, "
            "https://www.mouser.com/datasheet/3/1278/1/CD_DS_SCD4x_Datasheet_D1.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S038": {
        "px_status": "filled",
        "px_measurand": (
            "Fractional attenuation of a broadband IR beam through a fixed optical path, "
            "measured in a narrow band around the CO2 nu3 asymmetric-stretch fundamental "
            "near 4.26 um and ratioed against a reference band. That attenuation follows "
            "Beer-Lambert in the NUMBER DENSITY of CO2 molecules along the path -- molecules "
            "per cubic metre times path length -- not in mole fraction. The ppm output is a "
            "number-density measurement divided by an assumed total density."
        ),
        "px_units": "mol/m3 (column density, reported as ppm CO2 by volume)",
        "px_effect": (
            "Non-dispersive infrared absorption. An incandescent or MEMS IR emitter "
            "illuminates a folded gold-plated light pipe; a thermopile behind a 4.26 um "
            "bandpass filter sees the CO2-absorbed beam and a second detector (or a chopped "
            "reference) sees an unabsorbed band; the ratio cancels lamp aging and window "
            "dirt to first order."
        ),
        "px_chain": "Electrical,Radiant,Chemical,Thermal,Electrical",
        "px_cross": [
            "pressure", "altitude", "temperature", "humidity", "water-vapour", "airflow",
            "supply-voltage", "dust-fouling", "vibration", "aging-drift",
        ],
        "px_cross_note": (
            "pressure and altitude are the dominant, systematic, usually-uncorrected error "
            "and they follow directly from the physics: absorption counts molecules, so a "
            "fixed mole fraction absorbs less at lower total pressure. Senseair publishes "
            "the class figure for its NDIR modules as '+1.6 % of reading per kPa deviation "
            "from normal pressure, 100 kPa' (K-30 datasheet rev 1.3). That is about -1.6 % "
            "per kPa as you go up: a 30 hPa weather front is worth ~5 % (about 50 ppm at "
            "1000 ppm), and operating at 1500 m (~845 hPa) makes a true 1000 ppm read about "
            "740 ppm. The MH-Z19C has no pressure input, so this error is simply present. "
            "temperature: the datasheet states 'built-in temperature compensation' but gives "
            "no coefficient; physically both the emitter output and the thermopile "
            "responsivity are strongly temperature-dependent, and the ideal-gas number "
            "density at fixed mole fraction falls as 1/T -- about -0.34 %/K near room "
            "temperature. Operating window is only -10 to +50 degC. humidity / water-vapour: "
            "water has absorption features near the CO2 band and, more importantly, dilutes "
            "the dry-air fraction -- at 30 degC and 90 %RH, water vapour is about 3.8 % of "
            "the gas, so a dry-basis and a wet-basis ppm differ by nearly 4 %. Condensation "
            "inside the optical path is catastrophic and slow to clear. airflow: T90 < 120 s "
            "is a diffusion number set by the module's dust filter and vents, not by the "
            "optics (which respond in milliseconds). Forced flow across the vents shortens "
            "it several-fold; a clogged filter lengthens it without changing the "
            "steady-state reading, so response time is an independent health channel. "
            "supply-voltage: 5.0 +/-0.1 V required, <40 mA average with 125 mA peaks as the "
            "lamp fires. A thin supply that sags on the lamp pulse changes lamp colour "
            "temperature and therefore the band ratio -- an under-powered module reads "
            "systematically wrong and looks fine. dust-fouling: dirt on the light pipe is "
            "largely cancelled by the reference channel until it is not; the residual shows "
            "up as span error, not offset. vibration: the folded optical path and the "
            "filament are mechanical; shock shifts alignment and permanently changes span. "
            "aging-drift: the ABC self-calibration masks it -- see px_implies. Lifetime >5 "
            "yr."
        ),
        "px_range": (
            "400-2000 ppm standard, 400-5000 ppm optional; accuracy +/-(50 ppm + 5 % of "
            "reading) on the 400-2000 range."
        ),
        "px_resolution": (
            "1 ppm on the UART word; real short-term noise for this class is a few ppm rms "
            "with averaging, so the resolution is 1-2 orders better than the +/-(50 ppm + 5 "
            "%) accuracy. Like the SHT4x, this part is far better at changes and slopes than "
            "at absolute values."
        ),
        "px_bandwidth": (
            "T90 < 120 s (about a 50 s time constant) -- diffusion-limited by the filter and "
            "housing, NOT by the optics or by the 1 Hz-ish UART poll rate. Preheat 1 min. "
            "Anything you want to see faster than ~1 minute needs forced flow past the vents."
        ),
        "px_drift": (
            "No published ppm/yr figure; the module relies on ABC, which 'automatically "
            "calibrates every 24 hours since power-on' by assuming the lowest reading in "
            "that window corresponds to 400 ppm outdoor air. Lifespan >5 years. In a space "
            "that never reaches outdoor air, ABC silently drags the whole calibration down "
            "and the sensor under-reads by hundreds of ppm with no error flag."
        ),
        "px_implies": (
            "Three inferences that are not on the label: (1) because the measurement is "
            "number density, an NDIR module with a KNOWN, constant CO2 mole fraction is a "
            "barometer. Seal a module in a chamber with a reference gas, or simply note that "
            "outdoor CO2 is nearly constant on the hour scale, and the residual 1.6 %/kPa "
            "signal is atmospheric pressure -- a weather and altitude channel hidden inside "
            "a CO2 sensor; conversely, an uncorrected outdoor CO2 record contains the "
            "barometric pressure trace as a systematic artefact; (2) indoor CO2 above "
            "outdoor baseline is a direct measurement of rebreathed air. At steady state, "
            "excess CO2 = (per-person CO2 generation, ~0.005 L/s sedentary) / (ventilation "
            "rate per person), so a single module gives you either occupancy (if you know "
            "the ventilation) or litres-per-second-per-person of fresh air (if you know the "
            "occupancy). The exponential DECAY after everyone leaves needs neither: its time "
            "constant is the air-change rate of the room in ACH, measured directly. That "
            "makes an 18 dollar module an infiltration-rate meter, a duct-leakage tester and "
            "an airborne-infection-risk proxy; (3) the ABC correction is itself data. The "
            "size of the daily baseline adjustment measures whether the space ever gets "
            "outdoor air -- a room whose ABC correction is always zero is being ventilated; "
            "one whose correction grows is sealed. Log the correction, not just the ppm."
        ),
        "px_ref": (
            "Infrared CO2 Sensor Module (Model: MH-Z19C) User's Manual, Zhengzhou Winsen "
            "Electronics, Version 1.0, 2020-02-04, "
            "https://www.winsen-sensor.com/d/files/infrared-gas-sensor/mh-z19c-pins-type-co2-"
            "manual-ver1_0.pdf (pressure coefficient for the NDIR class: Datasheet K-30 "
            "Sensor, Senseair, rev 1.3, May 2015, "
            "https://img.ozdisan.com/ETicaret_Dosya/456729_1584920.PDF)"
        ),
        "px_ref_kind": "datasheet",
    },

    "S134": {
        "px_status": "filled",
        "px_measurand": (
            "The potential difference across a thin hydrated silicate gel layer on the "
            "outside of a glass bulb, generated by the difference in hydrogen-ion ACTIVITY "
            "between the sample and the fixed internal buffer. Activity, not concentration "
            "-- the electrode reports the thermodynamic availability of H+, which is why "
            "ionic strength changes the reading at fixed molarity. What the ESP32 actually "
            "sees is a millivolt signal from a ~100 Mohm source, buffered by the kit's "
            "op-amp board."
        ),
        "px_units": "V (mV across the membrane; reported as pH = -log10 a_H+)",
        "px_effect": (
            "Nernstian potentiometry at an ion-selective glass membrane, referenced to an "
            "Ag/AgCl half-cell through a porous liquid junction. Slope = -0.1984*(t + "
            "273.15) mV per pH unit: -57.2 mV/pH at 15 degC, -59.2 at 25 degC, -61.1 at 35 "
            "degC (Emerson/Rosemount). The kit's board is a high-impedance buffer plus "
            "offset and gain into the ADC; the electrode itself is a battery whose voltage "
            "is the answer."
        ),
        "px_chain": "Chemical,Electrical",
        "px_cross": [
            "temperature", "salinity-conductivity", "contamination-poisoning",
            "reference-drift", "ground-noise", "emi-rf", "cable-capacitance",
            "body-capacitance", "aging-drift", "contact-resistance",
        ],
        "px_cross_note": (
            "temperature enters twice and the two effects are usually confused. (a) The "
            "Nernst SLOPE is proportional to absolute temperature -- about 0.2 mV per pH "
            "unit per kelvin, i.e. roughly 0.33 %/K of the reading's DEVIATION FROM THE "
            "ISOPOTENTIAL POINT. Near pH 7 the temperature error is nearly zero; at pH 4 or "
            "pH 10 a 10 K excursion is about 0.06 pH; over the electrode's full 0-60 degC "
            "window it is 0.2-0.3 pH. This part is correctable if you measure the "
            "temperature. (b) The chemistry itself is temperature-dependent -- the pH of "
            "pure water is 7.47 at 0 degC and 6.14 at 60 degC -- and this is NOT an error "
            "and must not be compensated away. Most cheap kits do neither correction at all. "
            "salinity-conductivity: the electrode measures activity, and activity "
            "coefficients fall with ionic strength. Adding a neutral salt to a solution of "
            "fixed H+ molarity lowers the measured pH; the effect is of order 0.1 pH between "
            "deionised water and seawater-strength ionic media, and it also shifts the "
            "liquid-junction potential at the reference. Low-conductivity samples "
            "(rainwater, RO water, melt water) are the worst case: junction potential "
            "becomes unstable and readings drift for minutes. contamination-poisoning: "
            "'Dirty sensors often produce pH readings that drift... if the bulb is dirty or "
            "fouled, it may take some time for the liquid to diffuse through the coating'. "
            "Biofilm, oil, protein and soil colloids act as a diffusion barrier -- the "
            "electrode still responds, just slowly, so fouling shows up as a growing time "
            "constant before it shows up as an offset. reference-drift: the Ag/AgCl "
            "reference leaks KCl through a liquid junction; that junction develops a "
            "potential which depends on the sample's composition and on the cell's history "
            "('memory of past junction potentials can also lead to drift'). Sulfides, "
            "proteins and silver-complexing species poison the junction permanently. This, "
            "not the glass, is what usually kills a pH probe. ground-noise, emi-rf, "
            "cable-capacitance, body-capacitance: the source impedance is 'about 100 Mohm at "
            "25 degC' and rises steeply as temperature falls. At 100 Mohm, 1 nA of input "
            "bias is 100 mV = 1.7 pH, mains hum couples in capacitively, touching the BNC "
            "shifts the reading, and a second probe in the same tank (an EC meter, a pump, a "
            "heater with a leaky element) creates a galvanic loop that offsets pH by tenths "
            "without any chemistry changing. Isolated amplifiers exist for exactly this "
            "reason; the SEN0161/PH-4502C boards are not isolated. aging-drift: "
            "sodium/alkaline error grows as the glass ages -- 'above pH 11 the measured pH "
            "can be substantially less than expected', plateauing near 12.0 at a true pH of "
            "13, and 'sodium error tends to increase as the glass electrode ages'. A "
            "dry-stored bulb loses its gel layer and must be rehydrated for hours."
        ),
        "px_range": (
            "0-14 pH, 0-60 degC, accuracy +/-0.1 pH at 25 degC (kit spec). In millivolts "
            "that is roughly -414 to +414 mV about the isopotential point at 25 degC, and "
            "+/-0.1 pH = +/-6 mV."
        ),
        "px_resolution": (
            "Set by the ADC and the buffer, not the electrode. On a 5 V board scaled so 14 "
            "pH spans the ADC, a 12-bit ESP32 conversion is ~0.004 pH per LSB, while "
            "amplifier offset drift, junction potential and ground loops make anything "
            "better than 0.02-0.05 pH illusory in a real tank. Thermodynamic noise at the "
            "membrane is far below either."
        ),
        "px_bandwidth": (
            "<= 1 min response per the kit spec, and that is the CLEAN number: a new, "
            "well-hydrated bulb in stirred solution reaches 95 % in a few seconds, a fouled "
            "or cold one takes many minutes because the gel-layer diffusion and the 100 Mohm "
            "source impedance both slow down. There is no meaningful sense in which polling "
            "at 10 Hz gains information; the useful bandwidth is well under 0.1 Hz and the "
            "time constant is a diagnostic in its own right."
        ),
        "px_drift": (
            "Slope loss of a few percent per month in service is normal (a healthy electrode "
            "is >95 % of theoretical slope; below ~85 % it is dead). Offset drifts by "
            "millivolts per day from reference-junction effects. Two-point recalibration "
            "with pH 4.00 / 7.00 (and 10.01 for alkaline work) is a consumable maintenance "
            "task, not an optional one."
        ),
        "px_implies": (
            "Because a glass electrode is an activity sensor read through a 100 Mohm source, "
            "it is simultaneously three instruments: (1) an ionic-strength / salinity meter "
            "-- hold the chemistry fixed with a buffer and the residual pH shift is "
            "activity-coefficient change, so a buffered cell tracks total dissolved solids, "
            "road-salt runoff, or fertiliser dosing in hydroponics; (2) a sodium meter above "
            "pH 11, where the alkaline error is the signal rather than the artefact -- the "
            "same physics is exactly how a Na+ ISE works; (3) an electrometer good enough to "
            "detect stray currents in a tank. Two grounded instruments plus a pH probe make "
            "a galvanic-loop detector: a pH offset that appears the moment a pump starts is "
            "a leaking heater element or a bonding fault, and that is a shock-hazard "
            "finding, not a chemistry finding. Beyond the probe: in soil and water, pH is "
            "not an end in itself -- it sets the solubility and hence the bioavailability of "
            "phosphorus, iron, aluminium and heavy metals, so a pH trace is a proxy for "
            "nutrient availability and for metal mobilisation after rain. Paired with a CO2 "
            "measurement, pH in water gives dissolved inorganic carbon and hence a crude "
            "alkalinity/carbonate-system estimate; paired with an ORP probe it locates the "
            "redox boundary in a sediment or a compost pile. And the electrode's own time "
            "constant is a fouling/biofilm sensor."
        ),
        "px_ref": (
            "Theory and Practice of pH Measurement, Emerson/Rosemount Analytical, PN 44-6033 "
            "rev. D, December 2010, "
            "https://www.emerson.com/documents/automation/manual-theory-practice-of-ph-measur"
            "ement-en-70736.pdf ; kit-level specifications from DFRobot Wiki, 'Gravity: Lab "
            "Grade Analog pH Sensor Kit' SKU SEN0161, "
            "https://wiki.dfrobot.com/PH_meter_SKU__SEN0161_"
        ),
        "px_ref_kind": "appnote",
    },

    "S290": {
        "px_status": "filled",
        "px_measurand": (
            "Faradaic current at a working electrode held at a fixed potential by a "
            "potentiostat against a reference electrode. Because transport to the electrode "
            "is limited by a capillary and a gas-diffusion membrane, the current is "
            "proportional to the molar FLUX of NO2 arriving, not to its concentration -- "
            "which is why temperature, pressure and face velocity all enter. Two more "
            "electrodes (auxiliary and counter) exist to subtract the electrode's own "
            "background current."
        ),
        "px_units": "A (nA; -200 to -650 nA per ppm NO2)",
        "px_effect": (
            "Amperometric electrochemistry in a four-electrode cell: NO2 diffuses through a "
            "capillary and PTFE membrane to a catalysed working electrode wetted with acid "
            "electrolyte, where it is electro-reduced; the electrons are the signal. An "
            "activated-carbon filter in front of the cell removes ozone, which would "
            "otherwise be reduced at the same potential with a comparable sensitivity."
        ),
        "px_chain": "Chemical,Electrical",
        "px_cross": [
            "temperature", "humidity", "pressure", "gas-composition", "wind", "airflow",
            "contamination-poisoning", "aging-drift", "emi-rf", "reference-drift",
        ],
        "px_cross_note": (
            "temperature is the headline problem and it attacks the BACKGROUND, not the "
            "span. Alphasense's own correction note tabulates the nT scaling factor applied "
            "to the auxiliary electrode for NO2-B43F as 1.3 at -30/-20/-10/0 degC, 1.0 at 10 "
            "degC, 0.6 at 20 degC, 0.4 at 30 degC, 0.2 at 40 degC and -1.5 at 50 degC. A "
            "correction factor that runs from +1.3 to -1.5 across the operating range is not "
            "a trim, it is a sign inversion: an uncompensated cell is dominated by thermally "
            "driven background current, and at 25 ppb ambient NO2 (about -10 nA against an "
            "-80 to +80 nA zero window) the temperature term can exceed the signal several "
            "times over. Sensitivity itself also has a temperature dependence, but a much "
            "weaker one. gas-composition: the 'F' is an ozone filter with a stated capacity "
            "of <500 ppm.hr at 0.5 ppm O3. That capacity is finite and there is no "
            "end-of-life indicator. Once it is exhausted the cell reports NO2 + O3, and "
            "since urban O3 peaks in the afternoon while NO2 peaks in the traffic hours, an "
            "exhausted filter looks exactly like a change in the diurnal pollution pattern "
            "rather than like a fault. humidity: the electrolyte is hygroscopic. Sustained "
            "low RH dries it and slows response; sustained high RH swells it and can flood "
            "the capillary. Step changes in RH produce transient current excursions lasting "
            "minutes to hours that are easily mistaken for pollution events -- the classic "
            "'sensor sees the weather' artefact in low-cost air-quality networks. pressure: "
            "transport is diffusive through a capillary, and the binary diffusion "
            "coefficient scales roughly as T^1.75/P, so both altitude and weather move the "
            "sensitivity by a percent-level amount. wind / airflow: the capillary sits "
            "behind a face; wind over that face thins the external boundary layer and raises "
            "delivered flux, so an unshielded cell reads high in gusts. Roadside deployments "
            "need an aspirated or symmetric hood or wind is aliased into concentration. "
            "contamination-poisoning: the electrolyte is consumed by the target gas and by "
            "cross-reactants; solvents and high-concentration excursions permanently reduce "
            "sensitivity. Operating life is quoted as months until 50 % of original signal, "
            "with a 24-month equivalent change per year warranted in lab air. emi-rf and "
            "reference-drift: the front end is a sub-nanoamp transimpedance stage with "
            "gigaohm feedback; it is an electrometer, and unshielded it rectifies RF into an "
            "apparent concentration. The reference electrode potential must not be "
            "interrupted -- disconnecting the cell from its bias resistor for even seconds "
            "starts a hours-long re-equilibration that reads as a large false event."
        ),
        "px_range": (
            "Sensitivity -200 to -650 nA/ppm at 2 ppm NO2 (individually calibrated per "
            "cell); performance warranted to 20 ppm; zero current -80 to +80 nA in zero air "
            "at 20 degC. Noise given as +/-2 standard deviations equivalent to 15 ppb."
        ),
        "px_resolution": (
            "~15 ppb (2 sigma) at the cell, i.e. a few nanoamps. Note the ratio: 15 ppb of "
            "resolution against an +/-80 nA (roughly +/-200 ppb equivalent) zero-current "
            "window means the part resolves changes far better than it knows its own zero. "
            "Everything useful comes from differences, co-location and background modelling."
        ),
        "px_bandwidth": (
            "t90 < 80 s from zero to 2 ppm -- set by diffusion through the capillary, filter "
            "and membrane, not by the electronics (which are DC-coupled and could run at "
            "kHz). The practical bandwidth is lower still, because the temperature and "
            "humidity artefacts occupy the same 10-minute-to-hours band as real pollution "
            "events; useful data usually needs 1-15 minute averaging plus a co-located T/RH "
            "record."
        ),
        "px_drift": (
            "Life quoted as months until 50 % of original signal, with a 24-month-equivalent "
            "change per year in lab air. Zero drift with temperature dominates short-term "
            "(see the nT table). Ozone-filter capacity <500 ppm.hr at 0.5 ppm O3 is a "
            "consumable, not a spec."
        ),
        "px_implies": (
            "A four-electrode cell is a flux meter with a chemistry, and the auxiliary "
            "electrode is a second, gas-blind copy of the same cell. That structure gives "
            "you more than NO2: (1) the auxiliary channel alone is a slow, high-resolution "
            "thermometer of the electrolyte -- it tracks the cell's internal temperature "
            "with the same nT signature, so AE is a self-diagnostic and an "
            "enclosure-temperature channel, and WE-AE divergence that does NOT follow the nT "
            "curve means the cell is dying; (2) an NO2-B43F run alongside an unfiltered O3 "
            "cell lets you compute Ox = O3 + NO2 and back out each species -- and, more "
            "subtly, the DIVERGENCE between the two over months is a direct measurement of "
            "the carbon filter's remaining capacity, i.e. an in-situ consumable gauge; (3) "
            "because delivered flux depends on face velocity, a cell in a fixed enclosure "
            "with a known gas is an anemometer, and conversely a step in the signal that "
            "correlates with wind speed rather than with any plausible source is a wind "
            "artefact you can subtract; (4) the humidity transient response -- minutes-long "
            "current excursions after RH steps -- makes the cell an unintentional detector "
            "of rain onset, fog, and enclosure breaches; log RH alongside and the residual "
            "is either pollution or a leaking enclosure."
        ),
        "px_ref": (
            "NO2-B43F Nitrogen Dioxide Sensor 4-Electrode datasheet, Alphasense, version 1.0 "
            "(no date printed on the document), "
            "https://pdf.directindustry.com/pdf/alphasense/no2-b43f/16860-1025996.html ; "
            "temperature-correction factors from Alphasense Application Note AAN 803-05, "
            "'Correcting for Background Currents in Four Electrode Toxic Gas Sensors', March "
            "2019, https://lcqar.ufsc.br/novo/wp-content/uploads/2021/09/AAN-803-05.pdf"
        ),
        "px_ref_kind": "datasheet",
    },


    # ========================================================================
    # Optical and nuclear — 10 sensors.
    # S040, S044, S047, S052, S054, S059, S170, S188, S221, S369
    # ========================================================================

    "S040": {
        "px_status": "filled",
        "px_measurand": (
            "The rate and amplitude of light pulses scattered at a fixed angle by individual "
            "particles crossing a focused laser beam inside a fan-driven flow channel. The "
            "two primary quantities are particle count rate per unit sampled volume "
            "(reported as number of particles above 0.3, 0.5, 1.0, 2.5, 5.0 and 10 um in 0.1 "
            "L of air) and scattered-pulse amplitude, from which size is inferred. Mass "
            "concentration in ug/m^3 is not measured at all: it is computed from the "
            "count-and-size histogram under an assumed particle density and an assumed "
            "refractive index, using an undisclosed proprietary algorithm."
        ),
        "px_units": (
            "m^-3 (particle number concentration, reported per 0.1 L); W of scattered "
            "optical power per event (reported only indirectly as a size bin); kg/m^3 "
            "(reported as ug/m^3 mass concentration, a derived quantity)"
        ),
        "px_effect": (
            "Mie scattering -- elastic scattering by particles whose diameter is comparable "
            "to the illuminating wavelength, where the scattering cross-section depends on "
            "size parameter, refractive index and scattering angle in a strongly "
            "non-monotonic way. The sample is delivered by forced convection from a small "
            "fan, so the instrument also depends on a fluid-mechanical transport step that "
            "the optics cannot see."
        ),
        "px_chain": "Electrical,Mechanical,Radiant,Electrical",
        "px_cross": [
            "humidity", "water-vapour", "condensation", "aerosol-size-distribution",
            "temperature", "airflow", "wind", "dust-fouling", "contamination-poisoning",
            "vibration", "orientation-gravity", "aging-drift", "supply-voltage",
            "acoustic-noise",
        ],
        "px_cross_note": (
            "humidity is the dominant and best-quantified cross term, and its mechanism is "
            "hygroscopic growth: soluble aerosol (sulfate, nitrate, sea salt) takes up water "
            "above its deliquescence point and grows, increasing both the geometric "
            "cross-section and, through the higher refractive index contrast of a water "
            "shell, the Mie scattering efficiency. Sign is strongly positive. Magnitude: the "
            "US EPA's nationwide correction for PurpleAir monitors (which use paired "
            "PMS5003) is PM2.5 = 0.524 * PA_cf1 - 0.0862 * RH + 5.75, i.e. -0.086 ug/m^3 per "
            "percent RH plus a 0.52 overall scale factor (Barkjohn, Gantt and Clements, "
            "Atmos. Meas. Tech. 14, 4617-4637, 2021); above about 85% RH raw readings "
            "commonly run 1.5-2x reference. Fog and steam are the limiting case: pure water "
            "droplets contain essentially no dry mass and are reported as several hundred "
            "ug/m^3. aerosol-size-distribution: counting efficiency is 50% at 0.3 um and 98% "
            "at 0.5 um and above, so the sensor is effectively blind below ~0.3 um. Fresh "
            "combustion and vehicle-exhaust ultrafines peak near 0.02-0.1 um and are almost "
            "invisible to it, which means a PMS5003 systematically under-reports the most "
            "toxicologically relevant fraction while over-reporting cooking oil and fog. The "
            "proprietary mass conversion also assumes a fixed density (typically 1.65 g/cm^3 "
            "in this class of device) and a fixed refractive index; soot (~1.0 g/cm^3, "
            "strongly absorbing) and salt (~2.2 g/cm^3, non-absorbing) both violate it, in "
            "opposite directions. airflow/wind/orientation-gravity: the fan sets the sampled "
            "volume, and back-pressure from an enclosure, a filter, a headwind at an outdoor "
            "inlet or mounting the module on its side all change the flow and therefore the "
            "counts per nominal 0.1 L, with no flow sensor to catch it. "
            "dust-fouling/contamination-poisoning: deposition on the laser window and on the "
            "optical trap raises the stray-light baseline, which appears as an ever-rising "
            "floor -- the classic ageing failure, and the reason a PMS5003 that never reads "
            "below 3-5 ug/m^3 in clean air is dirty rather than in a polluted place. "
            "temperature: rated -10 to +60 C; laser output and photodiode gain both move "
            "with it, and the internal air is warmed by the electronics, lowering the RH of "
            "the sampled air relative to ambient by a few percent and slightly "
            "under-correcting for hygroscopic growth."
        ),
        "px_range": (
            "PM2.5 effective range 0 to 500 ug/m^3, maximum range at or above 1000 ug/m^3. "
            "Size channels 0.3-1.0, 1.0-2.5 and 2.5-10 um. Standard sampled volume 0.1 L. "
            "Supply 4.5-5.5 V typ 5.0 V, active current at or below 100 mA. Operating -10 to "
            "+60 C, 0-99% RH."
        ),
        "px_resolution": (
            "1 ug/m^3 reporting resolution, but consistency (unit-to-unit) is specified as "
            "+/-10 ug/m^3 over 0-100 ug/m^3 and +/-10% over 100-500 ug/m^3, so the reporting "
            "resolution is an order of magnitude finer than the accuracy. At low "
            "concentrations the true limit is Poisson counting noise on a small number of "
            "particles per 0.1 L: at 5 ug/m^3 a 1-second sample counts only tens of "
            "particles, giving 10-20% single-sample scatter, which is why raw 1 Hz data "
            "looks noisy and why averaging over 60 s is not optional."
        ),
        "px_bandwidth": (
            "Single-measurement response under 1 s, total response 10 s or less. The "
            "physical limit is the flow-channel residence and exchange time, roughly 1 s, "
            "which acts as a first-order low-pass: -3 dB near 0.16 Hz, and a step change in "
            "ambient concentration takes about 10 s to be fully reflected. The 1 Hz UART "
            "frame rate is a reporting rate, not a bandwidth, and the module already applies "
            "its own internal smoothing across frames."
        ),
        "px_drift": (
            "Laser diode output and fan speed both decline with operating hours; window and "
            "optical-trap deposition raise the zero. Field studies of this sensor family "
            "also report a step change in reported values associated with a "
            "manufacturing/firmware revision, so units bought years apart are not "
            "interchangeable without co-location. There is no zero-air or span calibration "
            "facility on the module -- the only practical field check is a HEPA-bagged zero."
        ),
        "px_implies": (
            "This is a nephelometer wearing a mass-concentration label. It reports scattered "
            "light and converts to ug/m^3 through assumed density, refractive index and size "
            "distribution, so what it truly measures is the aerosol's optical properties. "
            "That makes the standard failure modes into standalone sensors. A PM spike that "
            "coincides with an RH spike and no VOC or CO2 rise is condensation -- fog "
            "outdoors, a shower or a kettle indoors -- and the PMS5003 is therefore a fog "
            "and steam detector. A PM spike with simultaneous VOC and CO2 rises is "
            "combustion or cooking, and the ratio of the 0.3-0.5 um channel to the 2.5-10 um "
            "channel separates them: frying and candles load the fine bins, sweeping and "
            "vacuuming load the coarse ones. Because the count channels are far more "
            "physical than the mass channels, the ratio N(>0.3)/N(>0.5) is a "
            "size-distribution index that falls when droplets grow, giving a direct, "
            "sensor-internal humidity-growth flag that needs no external hygrometer. And in "
            "the long run, a slowly rising baseline at times when the concentration is known "
            "to be low is a self-diagnostic: the instrument is telling you its own window is "
            "dirty, which is a maintenance signal and, in an industrial setting, a proxy for "
            "cumulative aerosol exposure of the whole enclosure."
        ),
        "px_ref": (
            "Plantower, 'Digital universal particle concentration sensor PMS5003 series data "
            "manual', Version V2.3, 2016-06-01, "
            "https://cdn-shop.adafruit.com/product-files/3686/plantower-pms5003-manual_v2-3.p"
            "df (humidity correction coefficients from Barkjohn, Gantt and Clements, "
            "'Development and application of a United States-wide correction for PM2.5 data "
            "collected with the PurpleAir sensor', Atmos. Meas. Tech. 14, 4617-4637, 2021)"
        ),
        "px_ref_kind": "datasheet",
    },

    "S044": {
        "px_status": "filled",
        "px_measurand": (
            "Photocurrent generated in a silicon photodiode whose on-die filter approximates "
            "the CIE photopic V(lambda) curve, integrated (charge-accumulated) over a fixed "
            "window and reported as a count. The physical quantity is spectrally weighted "
            "irradiance -- the integral of E(lambda)*V_BH1750(lambda) dlambda, which equals "
            "illuminance only when the source spectrum matches the illuminant the part was "
            "trimmed against. The datasheet's own spectral response peaks at 560 nm, close "
            "to but not identical with the 555 nm photopic peak."
        ),
        "px_units": (
            "lx (lm/m^2); underlying quantity W/m^2 weighted by the sensor's own spectral "
            "response, scaled by the nominal 683 lm/W photopic constant"
        ),
        "px_effect": (
            "Internal photoelectric effect (photon absorption creating electron-hole pairs "
            "in a reverse-biased silicon p-n junction), followed by light-to-frequency "
            "conversion and boxcar integration of pulses over a hardware-timed window; there "
            "is no analogue front end whose gain can drift, only a counter and an oscillator."
        ),
        "px_chain": "Radiant,Electrical",
        "px_cross": [
            "target-colour", "ir-radiation", "light-flicker", "clock-drift", "temperature",
            "supply-voltage", "dust-fouling", "aging-drift", "reference-drift", "sunlight-load",
            "target-geometry",
        ],
        "px_cross_note": (
            "target-colour (source spectrum): the dominant error, and it is a feature. The "
            "V(lambda) approximation means a 450 nm blue LED and a 660 nm red LED delivering "
            "identical radiometric power read roughly 5-10x apart in counts, because "
            "V(450)~0.038 and V(660)~0.061 against V(555)=1.0. Reading the same scene "
            "against a second sensor with a different response (TSL2591 IR channel, AS7341 "
            "F1/F8) turns the pair into an illuminant classifier. ir-radiation: sign "
            "negative-going relative to a bare photodiode -- ROHM states 'the influence of "
            "infrared is very small', so an incandescent lamp whose radiant output is >80% "
            "beyond 780 nm reads far dimmer on a BH1750 than on an unfiltered BPW34. The "
            "BH1750/BPW34 ratio is therefore a direct incandescent-vs-LED discriminator with "
            "no spectrometer. light-flicker: the 120-180 ms H-resolution window is a boxcar "
            "whose transfer function has nulls at n/T; 100 Hz and 120 Hz mains ripple fall "
            "well inside the stopband and are averaged away, but a PWM dimmer at, say, "
            "200-800 Hz that is not commensurate with T beats against the window and "
            "produces a few-percent reading ripple whose beat period reveals the PWM "
            "frequency. clock-drift: the integration window is timed by an internal "
            "oscillator, and the reported lux is count / (1.2 * MTreg/69), so oscillator "
            "error enters as a direct multiplicative gain error -- an oscillator running 5% "
            "fast makes the world look 5% dimmer. This is a large part of the specified "
            "0.96-1.44 accuracy band. temperature: ROHM publishes only a "
            "temperature-characteristic curve, no numeric coefficient; the physical terms "
            "are photodiode dark current (roughly doubling every 8-10 K, but only 0-3 counts "
            "at 25 C so negligible below ~60 C) and RC-oscillator tempco (the larger term). "
            "dust-fouling/aging-drift: an attenuating film on the package is "
            "indistinguishable from a dimmer world -- the sensor has no way to separate "
            "transmittance from irradiance, which is exactly why a BH1750 behind a window is "
            "a window-cleanliness gauge when referenced to a clear-sky model. "
            "target-geometry: the package has no diffuser and no cosine correction, so a "
            "bare BH1750 under-reads off-axis light; the same part rotated is an "
            "angular-distribution probe."
        ),
        "px_range": (
            "1 to 65535 lx in the default H-resolution mode; extendable to a specified min "
            "0.11 lx and max 100000 lx by combining H-resolution mode 2 with the "
            "measurement-time register MTreg over its 31-254 range (sensitivity x0.45 to "
            "x3.68 about the default MTreg=69)."
        ),
        "px_resolution": (
            "1 lx/count nominal in H-resolution mode (0.83 lx/count at default MTreg after "
            "the 1.2 divisor); 4 lx/count in L-resolution mode; 0.5 lx nominal (0.42 "
            "lx/count) in H-resolution mode 2. Dark output is 0 to 3 counts at 0 lx, so the "
            "true noise floor in H-res mode 2 is roughly 1.3 lx, not the 0.5 lx quantisation "
            "step."
        ),
        "px_bandwidth": (
            "Not a bandwidth-limited analogue channel -- a boxcar integrator. H-resolution "
            "integration window is 120-180 ms (typ 120 ms), L-resolution 16-24 ms. The "
            "equivalent low-pass is sinc(f*T): for T = 150 ms the first null is at 6.7 Hz "
            "and the -3 dB point is near 2.7 Hz. Sampling faster than 1/T does not increase "
            "bandwidth; it only re-reads a stale integral, and any transient shorter than T "
            "is averaged into it rather than resolved."
        ),
        "px_drift": (
            "ROHM gives no numeric temperature coefficient, only a "
            "temperature-characteristic figure. The dominant stability term is part-to-part: "
            "the specified measurement accuracy factor is 0.96 to 1.44 against a nominal "
            "divisor of 1.2, i.e. roughly -20%/+20% absolute with no factory calibration "
            "constant to read back. Supply 2.4-3.6 V. Long-term drift in a real installation "
            "is dominated by optical-path fouling and by yellowing of any diffuser or "
            "enclosure window, not by the die."
        ),
        "px_implies": (
            "A lux number is a statement about a spectrum, not about power. Because the part "
            "is deliberately IR-blind and photopically weighted, its reading relative to any "
            "broadband or IR-biased sensor encodes what kind of light source is present, not "
            "just how much: sunlight, incandescent, fluorescent and white LED all have "
            "different (BH1750 lux)/(broadband W/m^2) ratios. Indoors, the diurnal envelope "
            "of a BH1750 with a flat top and abrupt edges is artificial light on a schedule "
            "(occupancy and routine), while a smooth cosine envelope with cloud-shaped "
            "notches is daylight through a window -- so a single lux log is an occupancy "
            "sensor, a shade-and-blind-position sensor, and a cloud-cover time series. The "
            "absence of a signal is also information: a 24 h flat zero from a sensor that "
            "previously saw daylight is a fouled window or a blocked aperture, and the "
            "recovery step when it is cleaned is a maintenance event marker. Under active "
            "illumination (drive a known LED, subtract the dark reading) the same part "
            "becomes a single-band reflectometer -- turbidity, surface soiling, fill-level "
            "in a translucent tank."
        ),
        "px_ref": (
            "ROHM Semiconductor, 'BH1750FVI -- Digital 16bit Serial Output Type Ambient "
            "Light Sensor IC', Technical Note, Rev.D, No.11046EDT01, November 2011, "
            "https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S047": {
        "px_status": "partial",
        "px_measurand": (
            "Photocurrent from a GaN Schottky-barrier photodiode with a nominal 240-370 nm "
            "response. The physical quantity is UV irradiance weighted by the diode's own "
            "responsivity curve -- the integral of E(lambda)*R(lambda) dlambda with R "
            "peaking near 0.14 A/W. On the common breakout the photocurrent is converted to "
            "a voltage by an on-board transimpedance amplifier, so what an ESP32 ADC "
            "actually reads is Vout = 4.3 V per uA of diode current, with 1 uA corresponding "
            "to roughly 9 mW/cm^2 of UV."
        ),
        "px_units": (
            "A (photocurrent); W/m^2 of UV irradiance after dividing by responsivity "
            "(breakout output in V)"
        ),
        "px_effect": (
            "Internal photoelectric absorption in a wide-bandgap semiconductor. GaN's ~3.4 "
            "eV bandgap is itself the optical filter: photons shorter than about 365 nm are "
            "absorbed and generate carriers, longer photons pass straight through. The part "
            "is therefore intrinsically visible-blind with no interference or absorptive "
            "filter to fade, which is the whole reason to use it rather than a filtered "
            "silicon diode."
        ),
        "px_chain": "Radiant,Electrical",
        "px_cross": [
            "temperature", "sunlight-load", "self-heating", "dust-fouling",
            "contamination-poisoning", "aging-drift", "supply-voltage", "emi-rf",
            "condensation", "humidity", "target-geometry", "ambient-light", "uv-radiation",
        ],
        "px_cross_note": (
            "temperature acts through the bandgap, and the sign matters: GaN's gap narrows "
            "by roughly 0.4-0.6 meV/K, so the long-wavelength cut-off red-shifts by about "
            "0.05-0.08 nm/K. Over a 40 K rise on a sunlit roof the cut-off moves 2-3 nm "
            "further into the UV-A, and because the solar spectrum rises steeply through "
            "360-380 nm, apparent UV can gain several percent purely from getting hot -- a "
            "positive, sun-correlated error that mimics the very signal being measured. "
            "target-geometry (cosine error) is the largest field error: a bare SMD diode is "
            "flat and uncorrected, so its response falls faster than cos(theta) at high "
            "incidence angles. At a 70 deg solar zenith the under-read can be tens of "
            "percent, meaning morning and evening UV are systematically low and the diurnal "
            "curve is too peaked. dust-fouling/contamination-poisoning: UV is attenuated by "
            "contamination far more strongly than visible light, and the polymer encapsulant "
            "itself solarises -- accumulated UV dose yellows it, so the sensor's sensitivity "
            "falls in proportion to how much it has been used. This is a sensor that "
            "measures itself away. emi-rf: the diode delivers nanoamps into a high-impedance "
            "node, so an unshielded run to the transimpedance amplifier picks up mains hum, "
            "switching-supply noise and ESD as apparent UV; a UV reading that correlates "
            "with a motor or a relay is EMI, not light. condensation: a water film on the "
            "window absorbs and scatters UV disproportionately, so dew produces a sharp dawn "
            "dip that recovers as the sun dries it -- a usable dew-burn-off timestamp. "
            "ambient-light: the GaN bandgap gives genuine visible blindness, but the "
            "breakout's op-amp and the diode's own 1 nA dark current set a floor of a few "
            "tens of mV that drifts with temperature; below about 0.05 mW/cm^2 the reading "
            "is offset, not signal."
        ),
        "px_range": (
            "Nominal 0 to about 10 mW/cm^2 of UV, corresponding to roughly 0 to 1.1 uA of "
            "photocurrent and 0 to 4.7 V at the breakout's 4.3 V/uA gain. Clear-sky summer "
            "noon UV-A at mid latitudes is of order 3-5 mW/cm^2, so the part is well matched "
            "to solar work and heavily over-ranged by a nearby welding arc."
        ),
        "px_resolution": (
            "Set by the transimpedance stage and the ADC, not by the diode. The 1 nA dark "
            "current gives roughly 4.3 mV of dark offset at the breakout gain, i.e. about "
            "0.01 mW/cm^2 equivalent -- so on a 12-bit ESP32 ADC at 3.3 V full scale (0.8 "
            "mV/LSB) the sensor's own dark current, not the converter, sets the floor."
        ),
        "px_bandwidth": (
            "The photodiode itself is fast -- an active area of about 0.076 mm^2 gives a "
            "small junction capacitance and an intrinsic response well into the megahertz. "
            "The practical bandwidth is set entirely by the transimpedance amplifier's "
            "feedback network, typically a few hundred hertz to a few kilohertz on hobby "
            "breakouts. That is still fast enough to resolve 100/120 Hz mains ripple and "
            "welding-arc transients, which an integrating ALS chip fundamentally cannot -- a "
            "decisive difference from every other light sensor in this group."
        ),
        "px_drift": (
            "GenUV publishes no numeric temperature coefficient. The physical terms are "
            "bandgap shift (about +0.05 to +0.08 nm/K on the cut-off, giving a few tenths of "
            "a percent per kelvin against a solar spectrum), dark-current doubling roughly "
            "every 8-10 K, and cumulative-dose solarisation of the encapsulant, which is "
            "irreversible and can cost tens of percent of responsivity over years of outdoor "
            "exposure. Operating -30 to +85 C, storage -40 to +90 C."
        ),
        "px_implies": (
            "The 'UV index' that every GUVA-S12SD sketch prints is a linear fudge with no "
            "physical basis. The diode's 240-370 nm response is not the CIE erythemal action "
            "spectrum, which peaks below 300 nm and falls roughly three decades by 340 nm; "
            "this part is dominated by UV-A while the UV index is dominated by UV-B. The "
            "Adafruit breakout's own rule -- UV index equals output volts divided by 0.1 V "
            "-- is an empirical fit valid only for one solar spectrum. Because the UV-A/UV-B "
            "ratio changes strongly with solar zenith angle, ozone column and cloud, a "
            "GUVA-derived index is systematically wrong at low sun and under thin cloud, and "
            "it will happily report zero for a 405 nm violet LED that is still bright enough "
            "to matter. What the part genuinely measures is total UV-A irradiance, and that "
            "opens several off-label uses. It is an excellent flame and arc detector: gas "
            "flames, welding arcs and electrical arcing emit strongly in the UV where "
            "sunlight at ground level is comparatively weak, so a UV/visible ratio spike is "
            "a flame signature that a thermal or IR sensor confuses with a hot object. It is "
            "a germicidal-lamp uptime and end-of-life monitor, since 254 nm sits inside its "
            "band and low-pressure mercury lamps lose output long before they stop glowing "
            "visibly. Ratioed against a broadband pyranometer or a lux sensor, it becomes a "
            "sky-condition classifier: UV is scattered far more strongly than visible light, "
            "so the UV/visible ratio RISES under thin cloud and haze even as total "
            "irradiance falls -- the Rayleigh signature -- which distinguishes 'cloudy' from "
            "'shaded' from 'dirty window' with two cheap sensors and no camera."
        ),
        "px_ref": (
            "VERIFY: Adafruit, 'Analog UV Light Sensor Breakout - GUVA-S12SD (PRODUCT ID: "
            "1918)', product/technical document dated 11/12/2015, "
            "https://media.digikey.com/pdf/Data%20Sheets/Adafruit%20PDFs/1918_Web.pdf -- "
            "this document is verified and is the source for the 240-370 nm range, the Vout "
            "= 4.3 * I_diode(uA) transfer and the 1 uA <-> 9 mW/cm^2 point. NOT verified: "
            "the manufacturer's own GenUV/Genicom GUVA-S12SD datasheet PDF could not be "
            "retrieved (the DigiKey HTML datasheet mirror returns HTTP 410). The GaN "
            "material, 0.076 mm^2 active area, 0.14 A/W responsivity, 1 nA dark current and "
            "-30/+85 C operating range are taken from distributor parameter listings "
            "(gophotonics.com/products/photodiodes/genuv/56-976-guva-s12sd and "
            "isweek.com/product/uv-a-sensor-guva-s12sd_976.html) rather than from a "
            "manufacturer document, and the temperature coefficient is inferred from GaN "
            "bandgap physics because no vendor figure exists."
        ),
        "px_ref_kind": "datasheet",
    },

    "S052": {
        "px_status": "filled",
        "px_measurand": (
            "Photocharge accumulated in each of eight band-limited silicon photodiodes plus "
            "a clear and a NIR diode, where each band is defined by a nano-optic deposited "
            "interference (Fabry-Perot) filter grown directly on the CMOS die. The measurand "
            "is band-integrated spectral irradiance: the integral over each passband of "
            "E(lambda) * T_filter(lambda) * R_Si(lambda) dlambda. A separate unfiltered "
            "photodiode feeds a flicker-detection channel that measures the modulation of "
            "the incident light in time rather than its spectrum."
        ),
        "px_units": (
            "counts, convertible to basic counts = raw / (gain * integration_time_ms); "
            "proportional to W/m^2 integrated across each channel's FWHM (26-52 nm)"
        ),
        "px_effect": (
            "Thin-film interference (Fabry-Perot resonance) selecting the passband, then "
            "internal photoelectric absorption in silicon and integration by six 16-bit "
            "light-to-frequency converters. The passband is a resonance condition, m*lambda "
            "= 2*n_eff*d*cos(theta), which is why it moves with angle of incidence and with "
            "the refractive index of the stack -- a property no absorptive dye filter has."
        ),
        "px_chain": "Radiant,Electrical",
        "px_cross": [
            "target-geometry", "target-colour", "light-flicker", "temperature", "ambient-light",
            "ir-radiation", "clock-drift", "supply-voltage", "dust-fouling", "aging-drift",
        ],
        "px_cross_note": (
            "target-geometry (angle of incidence) is the physics that turns this into a "
            "geometry sensor: an interference filter blue-shifts with off-normal incidence "
            "as lambda(theta) = lambda_0 * sqrt(1 - (sin(theta)/n_eff)^2). For a typical "
            "n_eff near 1.7, 30 deg off-normal shifts a 555 nm passband by roughly 12 nm -- "
            "comparable to a quarter of the 39 nm FWHM. Against a spectrally smooth source "
            "that is a few-percent error; against a narrow-line source (an LED, a laser, a "
            "sodium lamp) it is a large, monotonic, sign-known change in the channel ratio, "
            "so the F4/F5 ratio under fixed illumination reads incidence angle and hence "
            "surface tilt. temperature: interference passbands drift with dn/dT of the "
            "deposited stack (order 10 pm/K, i.e. small), but photodiode dark current "
            "roughly doubles every 8-10 K and the ams-specified dark counts (0-4 and 0-5 "
            "counts at 512x gain, ~98 ms) grow accordingly -- at 512x gain and long "
            "integration the low-signal channels (F1 at 415 nm, where silicon responsivity "
            "is already weak) are the first to become temperature readouts rather than light "
            "readouts. light-flicker: the dedicated FD channel flags 100 Hz and 120 Hz "
            "explicitly and buffers samples for external analysis up to 2 kHz. That channel "
            "is a mains-frequency meter and a lamp-technology classifier that ignores "
            "brightness entirely: incandescent flickers at 2x mains with low modulation "
            "depth because of thermal inertia, cheap LED drivers flicker at 2x mains with "
            "near-100% depth, a good driver is flat, and a PWM dimmer sits at its own "
            "carrier. clock-drift: integration time is (ATIME+1)*(ASTEP+1)*2.78 us from an "
            "internal oscillator, so oscillator tolerance is a direct multiplicative gain "
            "term shared by all channels -- it cancels in channel ratios and does not cancel "
            "in absolute readings, which is the argument for always working in ratios. "
            "ambient-light/ir-radiation: the NIR channel at 910 nm and the clear channel are "
            "unfiltered enough to see thermal and IR sources the visible channels miss; a "
            "hot filament or a 940 nm illuminator lights NIR with almost no F1-F8 response, "
            "which uniquely fingerprints it. dust-fouling: a neutral film scales all "
            "channels equally and so is invisible in ratios but corrupts absolute counts -- "
            "the clear/NIR ratio staying constant while both fall is exactly the signature "
            "of a dirty window rather than a darker world."
        ),
        "px_range": (
            "16-bit per channel, full scale (ATIME+1)*(ASTEP+1) capped at 65535 counts, with "
            "programmable gain 0.5x to 512x -- about 10^6:1 usable irradiance dynamic range "
            "per channel once gain and integration are swept. Channel centres 415, 445, 480, "
            "515, 555, 590, 630, 680 nm (FWHM 26, 30, 36, 39, 39, 40, 50, 52 nm) plus NIR at "
            "910 nm, a clear channel and the flicker diode."
        ),
        "px_resolution": (
            "ADC noise specified as 0.005% of full scale at 16x gain, 10 ms integration, "
            "i.e. roughly 3 counts rms on a 65535-count scale. Dark counts 0-4 (Dark_1) and "
            "0-5 (Dark_2) at 512x gain and ~98 ms integration, so the practical floor at "
            "maximum sensitivity is a handful of counts and the smallest resolvable "
            "channel-ratio change is of order 10^-3 when the channels are well filled."
        ),
        "px_bandwidth": (
            "Integration time tint = (ATIME+1)*(ASTEP+1)*2.78 us, spanning about 2.78 us to "
            "182 ms; ams recommend ASTEP=599, ATIME=29 giving 50 ms. This is a boxcar, so "
            "the spectral channels have a sinc response with the first null at 1/tint -- 20 "
            "Hz for the recommended 50 ms setting, hence roughly an 8 Hz -3 dB bandwidth. "
            "The flicker channel is the exception: it is sampled fast enough to resolve "
            "modulation up to 2 kHz and is the only part of the chip with real AC bandwidth."
        ),
        "px_drift": (
            "ams publishes no numeric per-channel temperature coefficient. Physical drift "
            "terms, in order: photodiode dark current (doubling per 8-10 K, matters only at "
            "high gain and long integration), oscillator tempco entering as a common gain "
            "error, and interference-stack index drift moving passband centres by order 10 "
            "pm/K. Long term the deposited filters are inorganic and do not fade the way dye "
            "filters do; the realistic ageing term is the enclosure window and any diffuser, "
            "not the die."
        ),
        "px_implies": (
            "Eight visible bands plus NIR is not a spectrometer, but the ratios are enough "
            "to make claims the label never mentions. (1) F8(680 nm) versus NIR(910 nm) "
            "straddles the chlorophyll red edge, so the (NIR-F8)/(NIR+F8) ratio under a "
            "broadband illuminant is a crude NDVI -- a plant-health and leaf-water-content "
            "signal from a 3-dollar light sensor. (2) F1(415)/F5(555)/F8(680) fitted to a "
            "Planckian locus gives correlated colour temperature, which under daylight is a "
            "cloud-cover and solar-zenith proxy: clear sky is blue-rich (high F1/F8, "
            "effective CCT above 10000 K near zenith), overcast collapses toward 6500 K, and "
            "a low sun reddens it -- so a fixed upward-looking AS7341 is a sky-condition "
            "classifier. (3) The flicker channel alone, with the spectral channels ignored, "
            "is a non-contact mains-frequency and grid-region detector and an "
            "appliance-state monitor. (4) With a white LED next to it the part becomes a "
            "reflectance spectrometer, which is what makes it read fruit ripeness, "
            "colourimetric test strips, blood or dirt in a fluid, and print density -- the "
            "AS7341 measures light, and the sample is only in the chain because you put it "
            "there."
        ),
        "px_ref": (
            "ams-OSRAM, 'AS7341 11-Channel Multi-Spectral Digital Sensor', Datasheet "
            "DS000504, v3-00, 2020-Jun-25, "
            "https://cdn.sparkfun.com/assets/0/8/e/2/3/AS7341_DS000504_3-00.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S054": {
        "px_status": "filled",
        "px_measurand": (
            "Two unrelated quantities on one die. (1) Proximity/gesture: the difference "
            "between photocurrent with the on-board 950 nm LED on and off, measured "
            "separately in four spatially separated IR photodiodes (up/down/left/right). "
            "This is retro-reflected irradiance, proportional to rho*A/d^2 -- it is NOT a "
            "distance measurement and contains no timing information. (2) ALS/colour: "
            "photocurrent in four filtered silicon photodiodes (red ~625 nm, green ~525 nm, "
            "blue ~465 nm, clear), integrated over ATIME."
        ),
        "px_units": (
            "W/m^2 of returned 950 nm irradiance at the detector (reported as 8-bit "
            "proximity counts); W/m^2 per colour band (reported as 16-bit ALS counts)"
        ),
        "px_effect": (
            "Internal photoelectric effect in silicon, with synchronous detection: the IR "
            "LED is pulsed and the ambient (LED-off) level is subtracted in hardware, so the "
            "proximity channel measures only the modulated return. Colour selectivity is by "
            "on-die absorptive filters, not interference filters, so it is angle-insensitive "
            "but has broad, overlapping passbands."
        ),
        "px_chain": "Electrical,Radiant,Radiant,Electrical",
        "px_cross": [
            "target-reflectivity", "target-geometry", "target-colour", "ambient-light",
            "sunlight-load", "ir-radiation", "condensation", "dust-fouling",
            "contamination-poisoning", "temperature", "supply-voltage", "aging-drift",
        ],
        "px_cross_note": (
            "target-reflectivity is not a cross term, it IS the measurand -- the label is "
            "what is wrong. Proximity count goes as rho/d^2, so a black cloth (rho ~0.05 at "
            "950 nm) at 3 cm and a white card (rho ~0.85) at 12 cm return the same 8-bit "
            "number; there is no way to separate them without moving something. Sign and "
            "magnitude: a factor 17 in reflectance is exactly cancelled by a factor 4.1 in "
            "distance. target-geometry: a specular surface at non-normal incidence returns "
            "almost nothing, so glass, water and polished metal read as 'far' regardless of "
            "distance -- and a wet finger reads farther than a dry one. "
            "dust-fouling/condensation: internal LED-to-detector crosstalk through the cover "
            "glass sets the proximity zero, which is why the part exposes POFFSET_UR and "
            "POFFSET_DL (+/-127, sign-magnitude). A fingerprint smudge or dew on the glass "
            "raises that floor, so the drift of the calibrated offset over hours is a direct "
            "read of window contamination and of condensation forming -- a free "
            "dew-point-crossing detector on any device that already has a proximity sensor. "
            "ambient-light/sunlight-load: hardware ambient subtraction removes DC, but "
            "sunlight at ~1000 W/m^2 with roughly half its power beyond 700 nm can saturate "
            "the IR photodiodes outright, at which point the subtraction has nothing left to "
            "work with and proximity pins or goes erratic. That saturation threshold is "
            "itself a coarse solar-irradiance alarm. ir-radiation: the emitter peaks at 950 "
            "nm with 30 nm half-power width, so a TV remote at 940 nm, another APDS-9960, a "
            "940 nm ToF illuminator or an incandescent lamp all inject correlated-looking "
            "energy; two of these parts facing each other interfere, which means one can be "
            "used deliberately as a receiver for the other over 10-20 cm. temperature: the "
            "datasheet gives no numeric coefficient but plots normalised LED current versus "
            "temperature over -60 to +100 C; GaAs/AlGaAs IR emitters lose roughly 0.5%/K of "
            "radiant output, so an uncompensated proximity reading falls about 5% per 10 K "
            "rise, which at fixed geometry masquerades as the target retreating by ~2.5%."
        ),
        "px_range": (
            "Proximity: 8-bit, 0-255 counts, usefully spanning roughly 0 to 100 mm against a "
            "white target and only a few centimetres against a dark one. ALS/colour: 16-bit, "
            "up to 65535 counts, with ATIME programmable 2.78 ms to 712 ms in 2.78 ms steps "
            "and gain 1x/4x/16x/64x. Dark count offset 0-3 counts."
        ),
        "px_resolution": (
            "Proximity quantisation is coarse -- 8 bits over the whole return range -- so "
            "the fractional resolution near the far end is poor and the sensor is far more "
            "precise as a change detector than as an absolute gauge. ALS floor is the 0-3 "
            "count dark offset against a 65535 full scale, i.e. roughly 5e-5 of full scale "
            "per integration."
        ),
        "px_bandwidth": (
            "The gesture engine converts in 1.39 ms per ADC cycle, so the four-pixel flow "
            "field is sampled at roughly 180-720 Hz depending on configuration -- that is "
            "the real bandwidth for motion, and it is what allows direction to be inferred "
            "from the time-ordering of the U/D/L/R channels. The ALS channels are boxcar "
            "integrators over ATIME (2.78-712 ms), giving a sinc low-pass with the first "
            "null at 1/ATIME: 1.4 Hz at the maximum 712 ms setting. Proximity and colour "
            "therefore have bandwidths three orders of magnitude apart on the same chip."
        ),
        "px_drift": (
            "IR emitter radiant output declines with cumulative forward-current hours "
            "(typically a few percent per 1000 h at rated drive) and with junction "
            "temperature, and both show up as an apparent increase in target distance. "
            "Crosstalk offset drifts with any change to the optical window. No factory "
            "reflectance calibration exists, so absolute proximity numbers are meaningful "
            "only against a fixed, re-zeroed geometry."
        ),
        "px_implies": (
            "This part is sold as a gesture sensor and is physically a four-pixel 950 nm "
            "imaging reflectometer running at up to ~700 Hz. Mounted at a fixed standoff "
            "looking at a fixed surface it reads that surface's near-IR reflectance, which "
            "changes with moisture (water has a weak but real absorption band near 970 nm), "
            "with soiling, with surface roughness and with the presence of any foreign "
            "object -- so it is a fill-level sensor, a paper/label-present sensor, a "
            "fabric-versus-skin discriminator, and a smudge detector. The four-pixel "
            "geometry makes it an optical-flow sensor for anything that passes at the right "
            "distance: fingers, yes, but equally a belt, a card, an insect, or a falling "
            "drop, and the U/D/L/R timing gives direction and speed without any image "
            "processing. With the LED disabled the same IR photodiodes are a 950 nm ambient "
            "meter, so the sensor tells you sun load and incandescent load while the RGB "
            "channels tell you visible illuminance -- the (IR ambient)/(clear) ratio is an "
            "illuminant classifier. Finally, the colour channels plus a pulsed white LED "
            "make it a colourimeter with a known illuminant, which is what makes cheap "
            "colour-change chemistry (pH strips, CO2 indicator gels, humidity cards) "
            "readable by an ESP32."
        ),
        "px_ref": (
            "Avago Technologies (now Broadcom), 'APDS-9960 Digital Proximity, Ambient Light, "
            "RGB and Gesture Sensor', Data Sheet AV02-4191EN, 8 November 2013, "
            "https://cdn.sparkfun.com/assets/learn_tutorials/3/2/1/Avago-APDS-9960-datasheet."
            "pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S059": {
        "px_status": "filled",
        "px_measurand": (
            "The arrival-time histogram of single 940 nm photons on a 16x16 SPAD array, "
            "referenced to the emission phase of an on-chip VCSEL. Three distinct quantities "
            "fall out of that histogram and only one of them is 'distance': (a) the "
            "histogram centroid, giving round-trip delay tau and distance d = c*tau/2; (b) "
            "the rate of photons correlated with the emitted pulse -- the signal rate in "
            "kcps and kcps/SPAD, which is proportional to target reflectivity and to 1/d^2; "
            "(c) the rate of uncorrelated photons -- the ambient rate in kcps/SPAD, which is "
            "a photon-counting measurement of 940 nm irradiance at the aperture and has "
            "nothing to do with the target at all."
        ),
        "px_units": (
            "m (distance channel, reported in mm); s^-1 per SPAD (signal-rate and "
            "ambient-rate channels, reported in kcps/SPAD)"
        ),
        "px_effect": (
            "Geiger-mode avalanche multiplication: each SPAD is reverse-biased above "
            "breakdown so a single photo-generated carrier triggers a self-sustaining "
            "Townsend avalanche, quenched and recharged, giving one digital timestamp per "
            "photon. Distance comes from correlating those timestamps against the VCSEL "
            "modulation -- it is a photon-counting statistical measurement, not an analogue "
            "pulse time-of-flight."
        ),
        "px_chain": "Electrical,Radiant,Radiant,Electrical",
        "px_cross": [
            "target-reflectivity", "ambient-light", "sunlight-load", "ir-radiation",
            "multipath", "target-geometry", "condensation", "dust-fouling", "target-colour",
            "temperature", "precipitation", "aging-drift",
        ],
        "px_cross_note": (
            "target-reflectivity is the largest term and is quantified directly in the "
            "datasheet: in the dark, long-distance mode reaches 360 cm on an 88% white "
            "target, 340 cm on 54% grey and 170 cm on 17% grey. Range scales as "
            "sqrt(reflectance) because the return rate scales as reflectance/d^2, so the "
            "88%-to-17% step (a factor 5.2 in reflectance) gives a factor 2.1 in range -- "
            "which means at a FIXED distance the signal-rate channel is a calibrated 940 nm "
            "reflectometer good to a few percent. ambient-light/sunlight-load: also "
            "quantified -- long mode on white falls from 360 cm (dark) to 166 cm at 50 "
            "kcps/SPAD and to 73 cm at 200 kcps/SPAD, and ST notes usual office lighting is "
            "about 5 kcps/SPAD. The ambient-rate register therefore spans roughly 5 "
            "kcps/SPAD indoors to >200 kcps/SPAD in sun: a 1.5-decade, spectrally narrow "
            "(940 nm) irradiance meter that is blind to visible-only LED lighting and so "
            "distinguishes solar and incandescent load from artificial white light. "
            "condensation/precipitation: a dry diffuse surface returns Lambertian; a water "
            "film makes it specular, so a non-normal-incidence return collapses and the "
            "driver reports RangeStatus 2 (signal fail, 'the return signal is too weak to "
            "return a good answer'). A downward-looking VL53L1X over a deck, road or "
            "greenhouse bench therefore reports rain onset, dew and ice as a signal-rate "
            "collapse at unchanged distance -- distance says the surface is still there, "
            "signal rate says it is now wet. multipath and target-geometry: a corner or a "
            "glossy target beyond the unambiguous range produces RangeStatus 7 (wraparound), "
            "which occurs 'when the target is very reflective and the distance to the "
            "target/sensor is longer than the physical-limited distance measurable'; the "
            "wraparound flag itself is a specularity detector. dust-fouling/aging-drift: "
            "crosstalk through the cover glass adds a near-zero-distance return that biases "
            "every measurement short; ST provides an offset and crosstalk calibration "
            "precisely because that term grows with dust, scratches and condensation on the "
            "window -- so the calibrated crosstalk value, re-measured periodically, is a "
            "window-cleanliness gauge. temperature: the VCSEL centre wavelength drifts of "
            "order 0.07 nm/K and the SPAD breakdown voltage moves with temperature, which "
            "changes photon detection efficiency and hence signal rate at fixed reflectance; "
            "distance is timing-based and largely immune, so a signal-rate change with an "
            "unchanged distance and unchanged ambient is a thermal, not an optical, event."
        ),
        "px_range": (
            "Distance channel: about 4 cm to 360 cm in long-distance mode against an 88% "
            "target in the dark, 170 cm against 17% grey, and 130 cm in short-distance mode "
            "across all reflectances. Signal and ambient channels: usable from roughly 1 "
            "kcps/SPAD (dark, distant grey target) to >200 kcps/SPAD (direct sun), where "
            "ranging itself degrades but the ambient number remains valid."
        ),
        "px_resolution": (
            "1 mm reporting LSB. Accuracy +/-20 mm in the dark and +/-25 mm under 50-200 "
            "kcps/SPAD ambient. Repeatability +/-1% down to +/-0.15% depending on timing "
            "budget -- i.e. the noise is set by photon statistics, so integrating longer "
            "genuinely buys precision, unlike a triangulation sensor."
        ),
        "px_bandwidth": (
            "Timing budget is programmable 20 ms to 1000 ms and ranging runs at up to 50 Hz. "
            "The measurement is an accumulation over the whole timing budget, not an "
            "instantaneous sample: a target moving during a 33 ms budget smears the "
            "histogram and biases the centroid toward wherever it spent most of the window. "
            "Effective -3 dB bandwidth is therefore roughly 0.44/T_budget -- about 13 Hz at "
            "a 33 ms budget, 0.4 Hz at 1 s -- and no amount of polling raises it."
        ),
        "px_drift": (
            "Offset and crosstalk calibration against a known target at a known distance are "
            "required after any cover glass is fitted, and drift after that is dominated by "
            "the optical window (dust, scratches, condensation) rather than by the die. "
            "VCSEL output falls with cumulative operating hours and with junction "
            "temperature, which shows as a slow decline in signal rate at unchanged geometry "
            "-- a directly measurable ageing indicator. Rated -20 to +85 C."
        ),
        "px_implies": (
            "The distance channel is the least informative output. A VL53L1X reporting "
            "'unchanged distance, halved signal rate' is telling you the surface got darker, "
            "wetter, rougher or tilted, not that it moved -- which is a road-wetness sensor, "
            "a liquid-level sensor through a meniscus, a snow-versus-bare-ground "
            "discriminator, and a leaf-turgor sensor. The ambient-rate channel, read with "
            "the VCSEL effectively irrelevant, is a narrowband 940 nm sun sensor: because it "
            "is blind to visible-only LEDs but wide open to sunlight and incandescent, "
            "ambient rate rising while a lux sensor stays flat means solar gain through a "
            "window, and both rising together means someone turned on a halogen lamp. "
            "Combining the two, signal rate * d^2 is a reflectance estimate independent of "
            "range, which is the quantity you actually want for material classification. And "
            "the RangeStatus codes are a free classifier: status 2 means dark or wet or "
            "absent, status 7 means specular and far, status 4 means out of zone -- three "
            "different physical worlds that the distance number alone flattens into 'error'."
        ),
        "px_ref": (
            "STMicroelectronics, 'VL53L1X -- A new generation, long distance ranging "
            "Time-of-Flight sensor based on ST FlightSense technology', Datasheet DS12385 "
            "Rev 8, August 2024, https://www.st.com/resource/en/datasheet/vl53l1x.pdf "
            "(signal-rate/ambient-rate register semantics and RangeStatus codes from "
            "STMicroelectronics UM2510 Rev 7, December 2025, "
            "https://www.st.com/resource/en/user_manual/um2510-a-guide-to-using-the-vl53l1x-u"
            "ltra-lite-driver-stmicroelectronics.pdf)"
        ),
        "px_ref_kind": "datasheet",
    },

    "S170": {
        "px_status": "filled",
        "px_measurand": (
            "The rate of ionising events that deposit enough energy in the tube's Ne + Br2 + "
            "Ar fill to initiate a self-quenching Geiger discharge. The measurand is a count "
            "rate -- events per second -- and nothing else. It is not dose, not dose rate, "
            "not activity, and not energy. Every Geiger discharge produces essentially the "
            "same charge pulse regardless of whether it was started by a 60 keV photon, a "
            "1.25 MeV photon, a beta particle or a cosmic-ray muon, so the tube has zero "
            "energy discrimination by construction."
        ),
        "px_units": "s^-1 (counts per second; conventionally reported as counts per minute)",
        "px_effect": (
            "Townsend avalanche in a gas at high field. A primary ion pair created anywhere "
            "in the fill is accelerated toward a thin anode wire at about 400 V, gains "
            "enough energy between collisions to ionise further, and the avalanche "
            "propagates along the entire anode as a UV-mediated discharge -- which is why "
            "the pulse height is independent of the initiating energy. The Br2 halogen "
            "quench absorbs the UV and the resulting ions recombine without re-triggering, "
            "so the tube recovers without external quenching but suffers a long dead period."
        ),
        "px_chain": "Radiant,Electrical",
        "px_cross": [
            "supply-voltage", "temperature", "altitude", "pressure", "emi-rf", "electric-field",
            "vibration", "acoustic-noise", "humidity", "aging-drift", "ionizing-radiation",
            "precipitation", "soil-density",
        ],
        "px_cross_note": (
            "supply-voltage: the plateau slope is specified at no worse than 10% per 100 V "
            "over an operating range of 350-475 V with a plateau of at least 100 V starting "
            "at 260-320 V. A boost converter sagging 40 V under a weak battery therefore "
            "changes the count rate by up to 4% with no change whatever in the radiation "
            "field -- a slow downward drift in reported CPM as a battery discharges is a "
            "battery measurement. temperature: rated -60 to +70 C. Gas density and, more "
            "importantly, the vapour pressure of the bromine quench move with temperature, "
            "shifting the plateau start; near the cold limit the tube can fall off the low "
            "knee and simply stop counting. altitude/pressure: cosmic-ray secondary flux "
            "increases with atmospheric depth roughly a factor of two per 1500-2000 m of "
            "altitude, and the tube's specified intrinsic background of 1 cps is "
            "substantially cosmic in origin. Sign positive and large: a flight at 11 km "
            "raises the count rate by roughly 30-50x, which makes an SBM-20 an altimeter, a "
            "shielding-thickness gauge and a barometric-pressure proxy. "
            "emi-rf/electric-field: the anode sits at 400 V behind a 5.1 Mohm resistor with "
            "only 4.2 pF of tube capacitance -- an almost ideal antenna for a high-impedance "
            "node. Switching-supply spikes, relay arcs, ESD, brush motors and even the "
            "counter's own inverter produce false counts, and a count rate that correlates "
            "with a nearby appliance is EMI, not radiation. vibration/acoustic-noise: the "
            "anode wire is under mechanical tension, so microphonic modulation of the "
            "anode-cathode spacing produces charge injection -- tapping the tube counts. "
            "humidity: surface leakage across the anode insulator at high RH degrades the "
            "pulse and can either suppress counts or produce a continuous discharge. "
            "aging-drift: rated life is at least 2e10 pulses; halogen-quenched tubes lose "
            "quench gas with every discharge, so the plateau shortens and the slope steepens "
            "toward end of life -- meaning a tube used near a strong source ages measurably "
            "faster than one sitting in background."
        ),
        "px_range": (
            "Manufacturer-stated exposure-dose-rate range 0.004 to 40 uR/s, equivalently "
            "0.014 to 144 mR/h. Gamma sensitivity 29 cps per mR/h for Ra-226 and 22 cps per "
            "mR/h for Co-60 -- note that these two numbers differ by 32% for the SAME dose "
            "rate, which is the energy dependence of the tube written down explicitly. "
            "Intrinsic (own) background 1 cps, measured in practice as roughly 19 CPM at a "
            "typical 0.12 uSv/h natural background. Dead time 190 us at 400 V, so at 1000 "
            "cps the observed rate is already about 19% low if uncorrected (true n = m/(1 - "
            "m*tau)); saturation and eventual paralysis set in above a few thousand cps."
        ),
        "px_resolution": (
            "Poisson-limited and entirely a function of integration time -- this is the "
            "number nobody prints on a hobby Geiger counter. The relative standard deviation "
            "of N counts is 1/sqrt(N), so resolving a 10% change against a 20 CPM background "
            "requires about 100 counts, i.e. 5 minutes of counting; resolving a 1% change "
            "requires 10000 counts, about 8 hours. Any CPM figure updated once per second "
            "from a background-level field is essentially all noise: a 20 CPM background "
            "gives 0.33 counts per second, so a 1 Hz display shows 0 or 1 almost at random."
        ),
        "px_bandwidth": (
            "Not a bandwidth-limited channel -- a counting process. The only hardware time "
            "constant is the 190 us dead time, which sets per-event recovery and the onset "
            "of rate saturation. The response time to a change in the field is set entirely "
            "by the integration window YOU choose, and that window is bounded below by the "
            "Poisson requirement above: you cannot see a change faster than the time needed "
            "to accumulate enough counts to distinguish it from shot noise. A Geiger counter "
            "with a fast display is lying about its bandwidth."
        ),
        "px_drift": (
            "Plateau slope at most 10% per 100 V; recommended operating point 400 V with an "
            "anode resistor of 5.1 Mohm. Life at least 2e10 pulses, with quench-gas "
            "depletion progressively steepening the plateau. The stainless-steel cathode "
            "wall is 50 um thick with an areal density of 40 mg/cm^2, which is a hard, "
            "unchanging physical filter: it stops alpha particles completely and blocks beta "
            "particles below roughly 0.3-0.4 MeV, so the tube's response to a mixed field "
            "depends on a geometry that no calibration can undo."
        ),
        "px_implies": (
            "A Geiger tube reports events, not dose, and every CPM-to-microsievert "
            "conversion is an assumption about which isotope you are standing next to. The "
            "tube's own numbers make this concrete: 29 cps/(mR/h) for Ra-226 versus 22 "
            "cps/(mR/h) for Co-60 is a 32% spread across just two gamma emitters, and the "
            "gap widens dramatically at low photon energies where the stainless cathode both "
            "attenuates and, through photoelectric interaction in a high-Z wall, "
            "over-responds. The 0.0057 uSv/h per CPM factor that circulates through nearly "
            "every hobby Geiger project has no traceable derivation; a documented derivation "
            "from the tube's own Cs-137 sensitivity, applying a human-phantom absorbed-dose "
            "coefficient of 0.00877 Gy/R, yields 0.00812 uSv/h per CPM instead -- a 42% "
            "difference produced purely by the choice of assumption, not by anything the "
            "sensor did. State the assumption or the number means nothing. Beyond that, the "
            "off-label readings are the good ones. (1) Count rate versus altitude is a "
            "cosmic-ray flux measurement and therefore an atmospheric-depth barometer; take "
            "the same tube up a mountain or in an aircraft and it reads height. (2) After "
            "rain begins, background reliably rises for 30-60 minutes as Pb-214 and Bi-214 "
            "radon progeny are washed out of the air and deposited on the ground, then "
            "decays with their 27 and 20 minute half-lives -- so an outdoor Geiger counter "
            "is a rainfall-onset detector with a characteristic, unmistakable decay "
            "signature. (3) Terrestrial gamma from potassium, uranium and thorium in soil is "
            "attenuated by any water above it, so a fixed outdoor tube's background falls "
            "with snow accumulation and with soil moisture: the count rate is a "
            "snow-water-equivalent and soil-moisture gauge, which is precisely how airborne "
            "gamma snow surveys work. (4) Through the EMI cross-sensitivity, the same "
            "instrument is an unintentional spark and ESD counter. Safety framing, stated "
            "factually: 1 cps of intrinsic background is normal and unavoidable; the tube "
            "cannot distinguish a harmless natural background fluctuation from a genuine "
            "source, cannot identify what it is detecting, cannot see alpha at all, and "
            "saturates rather than pinning in a very intense field -- so a low reading in an "
            "unknown situation is not by itself evidence of safety."
        ),
        "px_ref": (
            "'Parameters and characteristics - SBM-20 / SBM-20U' (transcribed Soviet/Russian "
            "tube specification, gas fill Ne+Br2+Ar, plateau 260-320 V start with at least "
            "100 V length and at most 10%/100 V slope, dead time 190 us at 400 V, background "
            "1 cps, 29 cps/(mR/h) Ra-226 and 22 cps/(mR/h) Co-60, wall 50 um stainless at 40 "
            "mg/cm^2, capacitance 4.2 pF, life at least 2e10 pulses, anode resistor 5.1 "
            "Mohm), "
            "https://www.commander1024.de/wordpress/wp-content/uploads/2022/12/Parameters-and"
            "-characteristics-SBM-20.pdf ; cross-checked against "
            "https://www.pocketmagic.net/tube-sbm-20-%D1%81%D0%B1%D0%BC-20-geiger-tube/ ; "
            "the CPM-to-dose derivation and the 0.00812 vs 0.0057 uSv/h per CPM discrepancy "
            "from 'Technical note: How to calculate the conversion factor for Geiger tube "
            "SBM20', IoT-devices, published 2023-04-12, "
            "https://iot-devices.com.ua/en/technical-note-how-to-calculate-the-conversion-fac"
            "tor-for-geiger-tube-sbm20/"
        ),
        "px_ref_kind": "datasheet",
    },

    "S188": {
        "px_status": "filled",
        "px_measurand": (
            "The energy deposited in a CsI(Tl) crystal by a single ionising event, recovered "
            "as a charge pulse whose integral is proportional to the number of 550 nm "
            "scintillation photons produced. CsI(Tl) yields 54 photons per keV of deposited "
            "gamma energy, so the measurand is genuinely energy, in electronvolts -- which "
            "is the entire difference between this detector and a Geiger tube. The secondary "
            "measurand, the event rate, is the same quantity a GM tube gives."
        ),
        "px_units": (
            "eV of deposited energy per event (read as coulombs of SiPM charge); s^-1 for "
            "the event rate"
        ),
        "px_effect": (
            "A two-stage conversion. First, photoelectric absorption, Compton scattering or "
            "pair production in a high-Z, high-density medium (CsI(Tl), density 4.51 g/cm^3, "
            "Cs Z=55, I Z=53) creates energetic electrons that excite the lattice; energy "
            "migrates to Tl+ activator sites, which de-excite radiatively with a 1000 ns "
            "primary decay, emitting at a peak wavelength of 550 nm with refractive index "
            "1.79. Second, those photons trigger Geiger-mode avalanches in the microcells of "
            "a silicon photomultiplier -- 18980 microcells at 64% fill factor on a 6 mm "
            "device -- giving a gain of 3e6 at 2.5 V of overvoltage. Energy resolution comes "
            "from the fact that the number of photons, and therefore the pulse integral, is "
            "proportional to deposited energy."
        ),
        "px_chain": "Radiant,Radiant,Electrical",
        "px_cross": [
            "temperature", "temperature-of-electronics", "self-heating", "supply-voltage",
            "ambient-light", "humidity", "condensation", "vibration", "acoustic-noise",
            "emi-rf", "magnetic-field", "aging-drift", "ionizing-radiation", "altitude",
        ],
        "px_cross_note": (
            "temperature is the dominant cross term and it corrupts the ENERGY axis, which "
            "is the whole point of the instrument. Two mechanisms stack. (a) The SiPM's "
            "breakdown voltage has a temperature coefficient of 21.5 mV/degC, so at fixed "
            "bias a 10 degC rise reduces overvoltage by 0.215 V; at a nominal 2.5 V "
            "overvoltage that is an 8.6% loss of overvoltage and a comparable loss of gain, "
            "since gain is close to linear in (V - Vbr). (b) CsI(Tl) light output peaks at "
            "about 25-30 degC and falls either side, so a hot detector makes fewer photons "
            "per keV as well. The combined effect can move a photopeak by several percent "
            "per 10 degC -- enough to relabel Cs-137 at 662 keV as something else entirely. "
            "Any CsI+SiPM system without either bias compensation at 21.5 mV/degC or a "
            "software gain-stabilisation loop on a known peak is not a spectrometer, it is a "
            "thermometer with an energy axis. supply-voltage: for the same reason, gain is "
            "proportional to (V - Vbr), so 100 mV of bias ripple at a 2.5 V overvoltage is a "
            "4% gain error -- bias supplies for SiPMs need millivolt-class stability, far "
            "tighter than the 400 V GM supply. ambient-light: the SiPM's dark count rate for "
            "the 6 mm device is already 1200-3400 kHz, and any light leak adds a DC "
            "photocurrent that raises the baseline, increases pile-up and destroys "
            "low-energy resolution. A pinhole in the wrapping is the classic failure and "
            "shows up as a rate that tracks room lighting. temperature again, via dark "
            "counts: SiPM DCR roughly doubles every 8-10 degC, so the counting rate below "
            "about 50 keV in a warm detector is thermal noise, not radiation. "
            "humidity/condensation: CsI(Tl) is only slightly hygroscopic, unlike NaI(Tl), "
            "but the crystal surface still fogs under condensation, which scatters the 550 "
            "nm light and degrades light collection and hence resolution. "
            "vibration/acoustic-noise: the optical coupling between crystal and SiPM (grease "
            "or pad) is the weakest mechanical link; a shifted crystal changes light "
            "collection and therefore the energy calibration, so a spectrometer that has "
            "been dropped needs recalibrating. magnetic-field: SiPMs are essentially immune, "
            "unlike photomultiplier tubes, which is a genuine advantage in motorised or "
            "MRI-adjacent settings. altitude: cosmic-ray muons deposit roughly 5.6 MeV/cm in "
            "CsI and produce a broad high-energy continuum that scales with altitude, "
            "contaminating the top of the spectrum."
        ),
        "px_range": (
            "For a typical 10x10x10 mm to 25x25x25 mm crystal, useful from roughly 25-30 keV "
            "(below which the wrapping, the entrance window and falling light yield cut in) "
            "to about 3 MeV (above which escape peaks and incomplete absorption dominate). "
            "SiPM spectral range 300-950 nm with peak photon detection efficiency of 41% at "
            "420 nm -- note this is a mismatch worth knowing: CsI(Tl) emits at 550 nm, well "
            "off the SiPM's blue-optimised peak, so real PDE at the emission wavelength is "
            "closer to 25-30% and the system throws away a significant fraction of its "
            "photons. Count-rate capability is set by the shaping time, roughly 100 kcps "
            "before serious pile-up."
        ),
        "px_resolution": (
            "Energy resolution, expressed as FWHM at 662 keV, is the figure of merit. Photon "
            "statistics alone would allow better than 2% (a 662 keV event makes about 36000 "
            "photons; even at 25% collection-and-detection that is roughly 9000 "
            "photoelectrons, giving a 1.1% Poisson term), but CsI(Tl) non-proportionality, "
            "light-collection non-uniformity and SiPM excess noise factor and crosstalk (7%) "
            "dominate, and practical hobby-scale CsI(Tl)+SiPM systems land at 6-9% FWHM at "
            "662 keV. That is enough to separate Cs-137 (662 keV) from K-40 (1461 keV) "
            "trivially, and enough to separate the Bi-214 lines at 609 and 1120 keV, but not "
            "enough to resolve closely spaced lines within a decay chain."
        ),
        "px_bandwidth": (
            "Set by the scintillator, not the electronics: the CsI(Tl) primary decay time of "
            "1000 ns forces a shaping time of roughly 1-3 us to collect most of the light, "
            "and that shaping time sets both the pulse-pair resolution and the noise "
            "bandwidth. Pile-up becomes significant above roughly 10-50 kcps. Note the "
            "inversion against the GM tube in this same group: the Geiger tube's 190 us dead "
            "time saturates near 1 kcps, so the scintillator handles about two orders of "
            "magnitude more rate -- but it pays for that with a shaping-time trade-off "
            "between energy resolution (longer shaping, less noise) and rate capability "
            "(shorter shaping, less pile-up), a trade the GM tube does not even have the "
            "option to make."
        ),
        "px_drift": (
            "SiPM breakdown voltage 24.7 V typical with a 21.5 mV/degC coefficient; dark "
            "count rate 1200-3400 kHz for the 6 mm/35 um device; crosstalk 7%; recommended "
            "overvoltage 1.0-5.0 V. The practical stability limit is thermal, and the "
            "standard remedy is a gain-stabilisation loop that locks the spectrum to a known "
            "always-present line -- K-40 at 1461 keV from ordinary building materials is the "
            "usual free reference, which is a nice illustration of a background contaminant "
            "being repurposed as a calibration standard."
        ),
        "px_implies": (
            "This is the sensor that turns 'there is radiation' into 'there is THIS "
            "radiation', and the identification is what makes it useful for things that have "
            "nothing to do with radiation safety. (1) Potassium assay: natural potassium is "
            "0.0117% K-40, so the 1461 keV line rate is directly proportional to how much "
            "potassium is in front of the detector. That makes a CsI spectrometer a "
            "non-contact potassium meter for fertiliser, salt substitute, bananas, wood ash, "
            "granite worktops and concrete aggregate -- and over long integrations, a "
            "soil-potassium and provenance tool. (2) Radon proxy: the 609, 1120 and 1764 keV "
            "lines of Bi-214 and the 352 keV line of Pb-214 are radon daughters, so an "
            "indoor spectrometer measures radon progeny with no radon cell, no pump and no "
            "consumable, and outdoors those same lines spike for tens of minutes after rain "
            "begins as the progeny are washed out. (3) Material and thickness gauging: place "
            "a known source on one side and the spectrometer on the other, and the ratio of "
            "transmitted intensities at two energies gives both areal density and effective "
            "atomic number, because photoelectric absorption scales roughly as Z^4-Z^5 at "
            "low energy while Compton scattering scales with electron density -- that is "
            "dual-energy X-ray discrimination, done with a natural or a check source. (4) "
            "Thermometry from noise: because SiPM dark count rate is a steep, monotonic "
            "function of temperature (doubling every 8-10 degC), the sub-threshold count "
            "rate of a sealed, source-free detector is a thermometer sensitive to a fraction "
            "of a degree, entirely from the sensor's own noise floor. Safety framing, "
            "factual: energy discrimination tells you which isotope is present and therefore "
            "whether a reading is ordinary natural background (K-40, U/Th series, radon "
            "progeny) or something introduced, which a GM tube can never do; it does not by "
            "itself tell you a dose, since converting a spectrum to dose still requires the "
            "detector's energy-dependent efficiency and the geometry of the field."
        ),
        "px_ref": (
            "Saint-Gobain Crystals (now Luxium Solutions), 'CsI(Tl), CsI(Na) Cesium Iodide "
            "Scintillation Material' material data sheet, 06-18, (c)2007-2018, "
            "https://luxiumsolutions.com/sites/default/files/2021-09/CsITl-and-Na-Material-Da"
            "ta-Sheet.pdf -- source for 4.51 g/cm^3, 550 nm emission, n=1.79, 1000 ns "
            "primary decay, 54 photons/keV, 45% photoelectron yield vs NaI(Tl), and the "
            "25-30 degC light-output maximum. SiPM parameters from onsemi, 'Silicon "
            "Photomultipliers (SiPM), Low-Noise, Blue-Sensitive C-Series SiPM Sensors', "
            "MICROC-SERIES/D Rev. 9, February 2022, "
            "https://www.mouser.com/datasheet/2/308/1/MICROC_SERIES_D-1489614.pdf -- "
            "MicroFC-60035: 18980 microcells, 64% fill factor, Vbr 24.7 V typ with 21.5 "
            "mV/degC coefficient, 1.0-5.0 V overvoltage, 41% PDE at 420 nm, DCR 1200-3400 "
            "kHz, gain 3e6 at Vbr+2.5 V, 7% crosstalk, 300-950 nm spectral range."
        ),
        "px_ref_kind": "datasheet",
    },

    "S221": {
        "px_status": "filled",
        "px_measurand": (
            "Nominally a binary occlusion state, but physically the irradiance reaching a "
            "photodiode across a 10 mm gap from a 950 nm GaAs emitter, compared against a "
            "threshold with hysteresis by an on-chip OPIC comparator. The output the system "
            "actually consumes is neither irradiance nor occupancy but the TIME of the logic "
            "edge -- so the useful measurand is an instant, in seconds, whose accuracy "
            "depends on how repeatably the beam crosses the threshold."
        ),
        "px_units": (
            "s (edge timestamp); underlying hidden quantity W/m^2 at the detector, "
            "thresholded"
        ),
        "px_effect": (
            "Geometric shadowing of a near-collimated 950 nm beam by an opaque vane, "
            "converted by the internal photoelectric effect and a Schmitt-triggered "
            "comparator. Because the aperture is a 1.8 +/- 0.1 mm slit, the transition is "
            "not a step: the edge time is set by the convolution of the vane edge with the "
            "slit, so the device is really an analogue integrator with a hard decision at "
            "the end."
        ),
        "px_chain": "Electrical,Radiant,Mechanical,Radiant,Electrical",
        "px_cross": [
            "ambient-light", "sunlight-load", "ir-radiation", "dust-fouling",
            "contamination-poisoning", "temperature", "humidity", "condensation", "vibration",
            "target-geometry", "aging-drift", "supply-voltage", "emi-rf", "precipitation",
        ],
        "px_cross_note": (
            "temperature is the term that quietly ruins encoder work: GaAs IR emitter "
            "radiant output falls roughly 0.5%/K, so across the rated -25 to +85 C span the "
            "beam power varies by about a factor of 1.7. The comparator threshold is "
            "specified as a forward-current equivalent of 1 to 7 mA with a hysteresis ratio "
            "of 0.55 to 0.95, so the effective threshold moves, and with a soft-edged vane "
            "crossing a 1.8 mm slit the apparent edge POSITION shifts by tens of "
            "micrometres. On a rotating vane that is a temperature-dependent duty-cycle "
            "error -- which means the pulse-width asymmetry of a photointerrupter encoder is "
            "a thermometer, and also that any 'phase drift' you see over a day is thermal, "
            "not mechanical. dust-fouling/contamination-poisoning: the 1-to-7 mA threshold "
            "spread is a 7:1 margin, so a device can tolerate about 85% beam attenuation in "
            "the best case and only about 30% in the worst; the duty cycle of the output "
            "against a known vane is therefore a direct, continuous read of beam "
            "attenuation, i.e. a contamination gauge built into every encoder you already "
            "own. ambient-light/sunlight-load/ir-radiation: the emitter is DC, not "
            "modulated, so there is no synchronous rejection at all. Sunlight through a "
            "window, an incandescent lamp, a 940 nm IR remote or a nearby ToF illuminator "
            "can hold the output in the light state regardless of the vane. That failure is "
            "a sensor: a photointerrupter that stops responding at the same time each "
            "afternoon is reporting where the sun is. condensation/precipitation: a droplet "
            "in the 10 mm gap acts as a lens and can either focus the beam (briefly raising "
            "the received power) or scatter it out of the aperture; a drop falling through "
            "the gap produces a pulse whose width, combined with free-fall velocity, gives "
            "drop diameter -- see px_implies. emi-rf: the OPIC output is a fast CMOS-level "
            "edge on a high-gain comparator, and motor brush noise or a relay coil coupling "
            "into the supply produces spurious edges; because the sensor is being read as an "
            "event counter, a single false edge is a permanent position error in an "
            "incremental encoder."
        ),
        "px_range": (
            "Binary output. The physical gap is 10 mm with a 1.8 +/- 0.1 mm detector slit, "
            "so any opaque object at least about 2 mm wide passing through the gap is "
            "detected; narrower objects only partially modulate the beam and may not cross "
            "the threshold. Supply 4.5 to 17 V, so it is not natively 3.3 V logic. Supply "
            "current 1.7-3.8 mA (output low) and 0.7-2.2 mA (output high)."
        ),
        "px_resolution": (
            "Timing resolution, not amplitude resolution. Propagation delays are tPLH 3 to 9 "
            "us and tPHL 5 to 15 us, with output transition times tr 0.1-0.5 us and tf "
            "0.05-0.5 us. The 6-10 us unit-to-unit spread is a fixed offset for any given "
            "device at a given temperature, so DIFFERENTIAL timing (period, duty cycle, "
            "edge-to-edge interval) is repeatable to roughly the sub-microsecond transition "
            "time, while ABSOLUTE latency is uncertain to about 15 us. An ESP32 "
            "input-capture peripheral therefore resolves a period far better than it "
            "resolves a phase."
        ),
        "px_bandwidth": (
            "Set by the slower propagation delay: 1/tPHL at the 15 us worst case gives about "
            "67 kHz theoretical, with a practical vane-passage limit of roughly 30-50 kHz "
            "before the asymmetry between tPLH and tPHL distorts the duty cycle beyond "
            "usefulness. Note that this is genuine analogue bandwidth, unlike every "
            "integrating light sensor in this group -- the device can resolve microsecond "
            "events, which is what makes it useful for ballistics and drop timing, not just "
            "for encoders."
        ),
        "px_drift": (
            "Emitter radiant output declines with cumulative forward-current hours, "
            "typically a few percent per 1000 h at rated drive, and roughly 0.5%/K with "
            "temperature; the comparator threshold and hysteresis (0.55-0.95 ratio) add a "
            "device-to-device spread. Since the design margin is only 7:1 at best, the "
            "combination of ageing plus dust plus a hot day is the normal failure path, and "
            "it fails as a slow narrowing of duty cycle long before it fails as a dead "
            "output."
        ),
        "px_implies": (
            "The output is not 'blocked or clear'. It is a timestamped edge, and everything "
            "interesting comes from what you put in the gap. Two edges and a known vane "
            "width give speed with no calibration constant and no drift -- a chronograph. "
            "The RATIO of on-time to off-time against a vane of known geometry gives beam "
            "attenuation, and therefore reads dust, oil mist, fog, smoke or condensation in "
            "the gap: a photointerrupter mounted with a fixed rotating chopper is a "
            "continuous obscuration meter, which is exactly how commercial opacity monitors "
            "work. A drop falling freely through the 10 mm gap from a known height has a "
            "known velocity, so the pulse width times that velocity is drop diameter -- "
            "turning a 30-cent part into a disdrometer that measures rainfall drop-size "
            "distribution, or a drip counter for an IV line or a leak, both with microsecond "
            "timing. Because the emitter is unmodulated, the sensor is also an unintentional "
            "950 nm ambient detector: a stuck-high output is a statement about sunlight, an "
            "incandescent lamp or a neighbouring IR device, and logging WHEN it sticks maps "
            "the sun's path across the machine. Finally, edge-to-edge jitter on a nominally "
            "constant-speed shaft is a vibration and bearing-wear signal -- the same data "
            "stream that gives you position gives you condition monitoring for free."
        ),
        "px_ref": (
            "Sharp Corporation, 'GP1A57HRJ00F -- OPIC Output Transmissive Photointerrupter', "
            "Sheet No. D3-A03901FEN, 3 October 2005, "
            "https://global.sharp/products/device/lineup/data/pdf/datasheet/gp1a57hr_e.pdf "
            "(the co-listed Everlight ITR9608-F, Technical Data Sheet DRX-0000076 Rev 2, "
            "2010/09/17, "
            "https://media.digikey.com/pdf/Data%20Sheets/Everlight%20PDFs/ITR9608-F.pdf, is "
            "the bare emitter/phototransistor variant of the same physics: 940 nm peak, ICEO "
            "100 nA max at VCE=20 V, tr/tf 15 us at IC=1 mA with RL=1 kohm, and no internal "
            "comparator, so its threshold is whatever you build)"
        ),
        "px_ref_kind": "datasheet",
    },

    "S369": {
        "px_status": "filled",
        "px_measurand": (
            "Photocurrent returned to a single silicon photodiode (peak sensitivity 860 nm, "
            "spectral bandwidth 420-1020 nm) while green (520-535 nm), red (660 nm) and IR "
            "(880 nm) LEDs are pulsed in sequence into a turbid, absorbing medium. The "
            "primary quantity is diffuse reflectance at three wavelengths, in amperes: a "
            "large DC term set by the bulk optical properties of whatever is in front of the "
            "module, and a small AC term (typically 0.1-2% of DC on skin) set by the "
            "time-varying path length through pulsating arterial blood."
        ),
        "px_units": (
            "A (photocurrent), digitised 19-bit over selectable full scales of 4.0, 8.0, "
            "16.0 or 32.0 uA"
        ),
        "px_effect": (
            "Modulated diffuse-reflectance photometry in a scattering medium: Beer-Lambert "
            "absorption by oxyhaemoglobin and deoxyhaemoglobin (whose extinction "
            "coefficients cross over near 800 nm, which is exactly why 660 nm and 880 nm "
            "were chosen) combined with Mie and Rayleigh scattering by tissue, with the "
            "pulsatile component arising from arterial volume change -- "
            "photoplethysmography. Ambient light is rejected by correlated double sampling "
            "around each LED pulse, specified at better than 70 dB at 120 Hz."
        ),
        "px_chain": "Electrical,Radiant,Chemical,Radiant,Electrical",
        "px_cross": [
            "target-reflectivity", "mechanical-stress", "acceleration", "vibration",
            "temperature", "self-heating", "ambient-light", "sunlight-load", "ir-radiation",
            "condensation", "humidity", "supply-voltage", "aging-drift",
        ],
        "px_cross_note": (
            "target-reflectivity (skin optical properties) sets the DC level over a range of "
            "more than 10:1 between lightly and heavily pigmented skin, because melanin "
            "absorption falls steeply with wavelength -- strong at 530 nm, much weaker at "
            "880 nm. Consequence: the LED drive current the automatic gain loop settles on "
            "is itself a melanin and perfusion measurement, and because the green channel is "
            "far more melanin-sensitive than the IR channel, the green/IR drive-current "
            "ratio is a pigmentation index. This is also the mechanism behind the "
            "well-documented bias of reflective pulse oximetry across skin tones -- it is an "
            "optics problem, not a firmware problem. mechanical-stress (contact pressure) is "
            "the second-largest term and has a known sign: increasing pressure expels venous "
            "blood and raises DC reflectance while compressing the arterial bed and REDUCING "
            "the AC amplitude, so perfusion index falls monotonically past an optimum; below "
            "that optimum, coupling gaps let ambient light in. acceleration/vibration: "
            "motion modulates both coupling and blood distribution at 0.5-5 Hz, precisely "
            "inside the pulse band, which is why every real PPG system fuses an "
            "accelerometer -- and conversely the PPG DC channel is a contact/motion sensor "
            "in its own right. temperature: LED radiant output falls roughly 0.3-0.5%/K for "
            "the InGaN green and 0.5-1%/K for the AlGaAs IR, while the photodiode's "
            "responsivity at 880 nm rises slightly; the net is a several-percent-per-10 K DC "
            "drift that is common-mode to AC/DC ratios and therefore mostly cancels in the "
            "ratio-of-ratios, which is the reason SpO2 algorithms use it. Skin temperature "
            "also changes peripheral vasoconstriction, which changes perfusion index by tens "
            "of percent -- a real physiological cross term, not an artefact. ambient-light: "
            "DC ambient rejection is specified up to 200 uA of photocurrent, five to fifty "
            "times the selected signal full scale, and better than 70 dB at 120 Hz; beyond "
            "that the front end saturates, so direct sunlight on an imperfectly sealed "
            "module kills the measurement outright. That saturation flag is a usable "
            "ambient-light alarm. condensation/humidity: sweat forms an index-matching film "
            "that raises coupling and DC, then a droplet layer that scatters and lowers it "
            "-- a slow DC ramp with no change in pulse amplitude is usually perspiration, "
            "which makes the DC channel a crude sweat-onset detector."
        ),
        "px_range": (
            "Photodiode full scale selectable 4.0 / 8.0 / 16.0 / 32.0 uA; LED drive full "
            "scale 31 / 62 / 93 / 124 mA; PPG sample rate 8 sps to 4096 sps; LED pulse width "
            "(integration) 14.8, 29.4, 58.7 or 117.3 us."
        ),
        "px_resolution": (
            "19-bit conversion over the selected full scale: 32 uA / 2^19 = 61 pA per LSB on "
            "the widest range, 4 uA / 2^19 = 7.6 pA on the narrowest. Dark current noise is "
            "specified below 50 pA rms, so on the 4 uA range the part is genuinely "
            "noise-limited rather than quantisation-limited -- roughly 1.3e-5 of full scale, "
            "which is what makes a 0.1%-of-DC pulsatile signal recoverable."
        ),
        "px_bandwidth": (
            "Do not confuse the 8-4096 sps sample rate with bandwidth. Each sample is an "
            "integration over the LED pulse width (14.8-117.3 us), and the useful signal "
            "band for a cardiac PPG is roughly 0.5-8 Hz (pulse fundamental 0.7-3.3 Hz plus "
            "dicrotic-notch harmonics). Running at 4096 sps buys ambient-rejection "
            "performance and averaging headroom, not extra physiological bandwidth; the "
            "practical -3 dB is set by whatever averaging and digital filtering you apply, "
            "typically 10-20 Hz."
        ),
        "px_drift": (
            "LED radiant output falls with cumulative drive-current hours and with junction "
            "temperature (self-heating at 124 mA pulsed is non-trivial in a module this "
            "small), so absolute DC reflectance is not stable over months without a "
            "reference. The part has no traceable optical calibration and no factory SpO2 "
            "curve: the ratio-of-ratios to saturation mapping must be supplied by the "
            "integrator and is empirically derived from human desaturation studies. Anything "
            "else is an uncalibrated number."
        ),
        "px_implies": (
            "The most important thing this sensor measures is not a heart rate. (1) The DC "
            "channel at three wavelengths is a reflectance spectrometer with a controlled "
            "illuminant -- point it at anything and it reports green/red/NIR reflectance, "
            "which is enough to grade fruit ripeness (chlorophyll at 660 nm), detect water "
            "content (the weak band near 970 nm is just inside the photodiode's 1020 nm "
            "edge), read ink density, or tell skin from fabric from table. (2) The AC/DC "
            "ratio, the perfusion index, is a peripheral vasoconstriction measurement, and "
            "vasoconstriction responds to cold, to sympathetic arousal and to pain -- so a "
            "PPG worn on a finger is a thermoregulation and stress sensor before it is a "
            "pulse sensor. (3) The pulse waveform SHAPE, not its rate, carries arterial "
            "stiffness information through the timing of the reflected wave, and the shape "
            "changes with posture because hydrostatic pressure at the sensor changes with "
            "height above the heart -- meaning a PPG plus an accelerometer resolves limb "
            "position. (4) With the LEDs off entirely the photodiode is a 420-1020 nm "
            "ambient meter with a 19-bit ADC and a sub-50 pA floor, which is a better "
            "low-light sensor than most dedicated ALS parts. (5) SpO2 itself is the weakest "
            "claim on the list: the part measures a ratio of modulation depths and every "
            "conversion to saturation rests on an empirical human calibration the silicon "
            "knows nothing about."
        ),
        "px_ref": (
            "Analog Devices, 'MAXM86161A Single-Supply Integrated Optical Module for HR and "
            "SpO2 Measurement', data sheet 19-102034, Rev 1, 1/26, "
            "https://www.analog.com/media/en/technical-documentation/data-sheets/maxm86161a.p"
            "df"
        ),
        "px_ref_kind": "datasheet",
    },


    # ========================================================================
    # Mechanical and acoustic — 10 sensors.
    # S020, S056, S072, S087, S094, S097, S098, S099, S151, S192
    # ========================================================================

    "S020": {
        "px_status": "filled",
        "px_measurand": (
            "Mass flow of gas through a small internal bypass channel, sensed thermally. "
            "Differential pressure is INFERRED from that flow via the known fluidic "
            "resistance of the channel -- there is no diaphragm and nothing in the part "
            "responds to pressure directly. That inversion is the whole story: the primary "
            "measurand is convective heat transport, so the reading depends on the gas's "
            "density and viscosity, and the part has no gravity-sensitive membrane to give "
            "it a position-dependent zero or a creeping long-term offset."
        ),
        "px_units": (
            "Pa (inferred); the primary physical quantity is mass flow in kg/s through the "
            "internal channel"
        ),
        "px_effect": (
            "Thermal anemometry (calorimetric / CMOSens): a micro-heater on a thin membrane "
            "sits between two symmetric thermopiles. With no flow the temperature profile is "
            "symmetric and the differential thermopile output is zero; forced convection "
            "tips the profile downstream, and the asymmetry is proportional to mass flow. "
            "Applied dP drives that flow through the bypass channel."
        ),
        "px_chain": "Mechanical,Thermal,Electrical",
        "px_cross": [
            "temperature", "thermal-gradient", "self-heating", "gas-composition", "humidity",
            "condensation", "pressure", "altitude", "dust-fouling", "contamination-poisoning",
            "airflow", "aging-drift",
        ],
        "px_cross_note": (
            "gas-composition/pressure/altitude: the deepest cross-sensitivity and the one "
            "that is invisible in the label. The element measures MASS flow but is "
            "calibrated to report the differential pressure that would produce that mass "
            "flow in air at reference conditions. Change the density and the mapping "
            "changes: at 2000 m the ambient pressure is ~80 kPa, air density is ~21% lower, "
            "and the same dP drives a different mass flow, so an uncorrected reading is "
            "wrong by of order that ratio [derived from the physics; the datasheet gives no "
            "altitude correction]. Substituting CO2 (higher density, different thermal "
            "conductivity and heat capacity) shifts it further. This is why the datasheet "
            "says 'calibrated for air'. temperature: span shift less than 0.5% of reading "
            "per 10 degC; compensated over -20 to +85 degC, measurement to -40 degC. "
            "thermal-gradient: a gradient imposed ALONG the channel by external heating "
            "breaks the thermopiles' symmetry directly and creates a false flow -- mounting "
            "the sensor with one port near a hot duct wall and one in room air is the "
            "classic installation error. self-heating: the heater is the sensing principle, "
            "not a parasitic; but it means the part warms the gas it measures, so at very "
            "low flow the reading is set by natural convection inside the channel, which is "
            "the physical origin of the 0.1 Pa zero-point limit. humidity/condensation: "
            "water vapour changes the gas's thermal conductivity and heat capacity (a few "
            "tenths of a percent at typical humidities); liquid condensate in the bypass "
            "channel changes the fluidic resistance drastically and can plug it silently -- "
            "the output then reads a plausible, stable zero. "
            "dust-fouling/contamination-poisoning: the bypass channel is small; particulate "
            "accumulation raises its resistance and progressively UNDER-reads dP, which in a "
            "filter-monitoring application is exactly the wrong direction. orientation: "
            "notably ABSENT as an error term -- with no diaphragm there is no gravity "
            "offset, which is why a zero-point accuracy of 0.1 Pa and an offset stability of "
            "less than 0.05 Pa/year are achievable at all, and why this part outperforms "
            "every piezoresistive differential sensor near zero by orders of magnitude."
        ),
        "px_range": (
            "SDP810-500Pa: -500 to +500 Pa (-2 to +2 inH2O). SDP810-125Pa: -125 to +125 Pa. "
            "Both 16-bit, calibrated for air, non-condensing gases. Operating -40 to +85 "
            "degC measurement, -20 to +85 degC compensated. Converted to other quantities "
            "[derived]: 500 Pa is 29 m/s of pitot air velocity (v = sqrt(2q/rho), rho = 1.2 "
            "kg/m^3), 51 mm of water column, or 42 m of air column."
        ),
        "px_resolution": (
            "Zero-point accuracy 0.1 Pa and zero-point repeatability 0.05 Pa (SDP810-500Pa; "
            "0.08 Pa and 0.04 Pa for the 125 Pa variant). No spectral density is published; "
            "with a 3 ms tau63 the equivalent noise bandwidth is ~53 Hz, so 0.05 Pa rms "
            "corresponds to roughly 7 mPa/sqrt(Hz) [derived]. In other units, 0.1 Pa is 0.41 "
            "m/s of pitot air velocity, 10 um of water column, or 8.3 mm of air column "
            "[derived] -- for near-zero differential pressure this part is about 13x finer "
            "than a BMP280 and, unlike the BMP280, it is measuring a genuine difference "
            "rather than two absolutes subtracted."
        ),
        "px_bandwidth": (
            "Flow step response time (tau63) less than 3 ms, i.e. a -3 dB bandwidth of about "
            "53 Hz [derived]. That is exceptionally fast for a pressure instrument and is a "
            "direct consequence of the thermal element's tiny thermal mass -- there is no "
            "compliant membrane to accelerate. It is fast enough to resolve the shape of a "
            "human breath, a damper's step response, or an individual gust."
        ),
        "px_drift": (
            "Offset stability better than 0.05 Pa per year -- essentially no zero drift, "
            "again because there is no diaphragm to creep. Span temperature coefficient less "
            "than 0.5% of reading per 10 degC. Span accuracy 3% of reading, span "
            "repeatability 0.5% of reading. The asymmetry is the design signature: the zero "
            "is nearly perfect and permanent, the span is only good to a few percent -- the "
            "exact opposite of a piezoresistive sensor, and it means this part should be "
            "trusted for SMALL differences and calibrated against something else for large "
            "ones."
        ),
        "px_implies": (
            "Label: HVAC filter monitoring and duct balancing. Physically it is a 0.1 Pa "
            "mass-flow-based differential gauge with a 53 Hz bandwidth and no zero drift, "
            "which opens several things the label never mentions. (1) With a pitot or "
            "orifice it is an anemometer usable from 0.41 m/s to 29 m/s [derived], which "
            "covers indoor air movement (the 0.1-0.3 m/s of a thermal plume is just below "
            "it) up to a strong wind -- and unlike a hot-wire it does not need to be exposed "
            "to the flow. (2) Human breath: a 3 ms response and a 500 Pa span across a fixed "
            "orifice yields the full flow-volume loop of a forced expiration, so the part is "
            "a spirometer -- peak expiratory flow, FEV1, breathing rate and apnoea all fall "
            "out of a signal that is nowhere in the datasheet. (3) Building physics: 0.1 Pa "
            "resolution over a doorway or between floors resolves stack effect and wind "
            "pressurisation directly, so a pair of tubes between two rooms reports door and "
            "window state, chimney draught reversal, and the building's neutral pressure "
            "plane -- a whole-building measurement from one 50 EUR part. (4) Water level to "
            "10 um of head with one tube in a standpipe [derived], because 10 Pa is 1 mm of "
            "water -- fine enough to see evaporation from an open vessel in real time. (5) "
            "Turned around: with a FIXED, known orifice the flow is known, so the reading "
            "becomes a measure of the gas's density and viscosity -- i.e. an indirect "
            "molecular-weight / CO2-concentration / humidity channel, exploiting exactly the "
            "cross-sensitivity that the calibration is trying to hide. (6) The design "
            "consequence: trust its zero absolutely (0.05 Pa/year), trust its span to 3%, "
            "and never mount it where one port is warmer than the other."
        ),
        "px_ref": (
            "Datasheet SDP8xx-Digital -- Digital Differential Pressure Sensor, Sensirion AG, "
            "Version 1.1, April 2019, "
            "https://sensirion.com/media/documents/90500156/6167E43B/Sensirion_Differential_P"
            "ressure_Datasheet_SDP8xx_Digital.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S056": {
        "px_status": "filled",
        "px_measurand": (
            "The round-trip transit time of a 40 kHz acoustic burst between the transmit "
            "transducer, a reflecting surface and the receive transducer -- a time interval, "
            "in seconds, and nothing else. Distance does not exist in this instrument: it is "
            "produced by multiplying the time by an ASSUMED speed of sound. Every 'distance "
            "error' in an HC-SR04 is really either a speed-of-sound error or a "
            "threshold-timing error, and separating those two is what makes the part "
            "reusable."
        ),
        "px_units": "s (round-trip time); m only after multiplying by an assumed c",
        "px_effect": (
            "Inverse piezoelectric effect drives an open-structure piezoceramic bimorph at "
            "its 40 kHz resonance to radiate an 8-cycle burst; the direct piezoelectric "
            "effect in an identical receiver converts the returning pressure wave to charge, "
            "which is amplified and passed to an envelope detector and a fixed-threshold "
            "comparator that sets the falling edge of the ECHO pulse."
        ),
        "px_chain": "Electrical,Mechanical,Electrical",
        "px_cross": [
            "temperature", "humidity", "wind", "airflow", "gas-composition", "pressure",
            "target-reflectivity", "target-geometry", "multipath", "acoustic-noise",
            "dust-fouling", "supply-voltage", "clock-drift",
        ],
        "px_cross_note": (
            "temperature: dominant, and it is not a defect but the physics -- c = 331.3 + "
            "0.606*T m/s, so dc/c = 0.176 % per degC at 20 degC. An instrument calibrated "
            "indoors at 20 degC and used at 0 degC reads 3.5% long, which is 7 cm at 2 m; "
            "over the full -20..+50 degC outdoor swing the span is 12%. humidity: c rises "
            "about 0.35% from dry to saturated air at 20 degC (moist air is less dense than "
            "dry air at the same pressure, because H2O is lighter than N2), so 100% RH reads "
            "~0.7 cm short at 2 m. wind/airflow: wind adds vectorially to c along the path "
            "-- 5 m/s of headwind on 343 m/s is 1.46%, i.e. 2.9 cm at 2 m, and it is "
            "asymmetric on the outbound and return legs only if the wind changes during the "
            "12 ms flight. gas-composition: c scales as sqrt(gamma*R*T/M), so a CO2-rich "
            "atmosphere (M = 44) reads long and helium (M = 4) reads about 3x short -- an "
            "HC-SR04 is a crude gas-molecular-weight sensor with a fixed target. pressure: c "
            "is independent of pressure for an ideal gas at fixed T, so altitude does NOT "
            "change the reading (only the echo amplitude, via density). "
            "target-reflectivity/target-geometry: the threshold detector fires when the "
            "envelope crosses a fixed level, so a weak echo crosses LATER on its rising "
            "envelope and the target reads FARTHER than it is -- soft, angled, small or "
            "absorbing targets are biased long, and a surface tilted more than about 15 "
            "degrees from normal, or made of foam, curtain, long grass or clothing, returns "
            "nothing at all. multipath: in a corridor or against a corner, a longer specular "
            "path can arrive with a bigger envelope than the true one and be reported "
            "instead; the ghosts are repeatable and geometry-dependent, which makes them "
            "information rather than noise. acoustic-noise: any 40 kHz source in the room -- "
            "another HC-SR04, a motion-detector, a jet of compressed air, some ultrasonic "
            "pest repellers, a set of keys -- triggers false echoes; several units on one "
            "robot must be time-multiplexed. dust-fouling: dust or water on the transducer "
            "face detunes the resonance and cuts the emitted amplitude, which biases "
            "everything long via the threshold mechanism. clock-drift: the range is an MCU "
            "timer measurement, so the ESP32's timebase error scales the distance directly "
            "(negligible at ppm level)."
        ),
        "px_range": (
            "2 cm to 4 m stated (round-trip 117 us to 23.3 ms in air at 20 degC [derived]); "
            "measuring angle 15 degrees, which is a 0.53 m diameter footprint at 2 m "
            "[derived]. 5 V supply, 15 mA working current, 40 kHz. Trigger is a 10 us TTL "
            "pulse; ECHO is a TTL pulse whose width is proportional to range, distance = "
            "(echo high time * c)/2."
        ),
        "px_resolution": (
            "Not limited by the ADC or by the timer: at 1 us of ESP32 timer resolution one "
            "count is 0.17 mm of range [derived]. The real resolution limit is the "
            "fixed-threshold envelope detector, whose firing instant depends on echo "
            "AMPLITUDE -- a target that halves its return signal shifts the reported edge by "
            "roughly one cycle of the 40 kHz carrier (25 us = 4.3 mm) for every 6 dB, so "
            "repeatability against a hard flat target is a few mm and against a soft or "
            "oblique target is centimetres. No noise density is specified anywhere in the "
            "user guide."
        ),
        "px_bandwidth": (
            "The transducers are high-Q resonators at 40 kHz -- that Q is why the part works "
            "at all (it puts all the energy in one band) and why it has a 2 cm minimum "
            "range: the transmitter rings down for roughly 1 ms after the burst, and the "
            "receiver, sitting next to it, is deafened for that time. The measurement "
            "repetition rate is bounded by reverberation, not by electronics: a cycle "
            "shorter than about 60 ms lets the previous burst's late multipath return be "
            "counted as this burst's echo. Update rate is therefore ~16 Hz maximum in a real "
            "room, which puts a hard Nyquist limit of ~8 Hz on anything moving."
        ),
        "px_drift": (
            "No zero drift -- time of flight has no offset to drift -- but a large SCALE "
            "drift through c(T,RH,wind): 0.176 %/degC. Transducer aging detunes the 40 kHz "
            "resonance and reduces amplitude, which shows up as a slow positive range bias "
            "via the threshold effect rather than as a loss of range."
        ),
        "px_implies": (
            "Label: a rangefinder. Physically it is a stopwatch for sound, and inverting the "
            "equation is where the value is. (1) Point it at a FIXED reflector at a known "
            "distance and it stops being a rangefinder and becomes a speed-of-sound meter: "
            "at 2 m the round trip is 11.65 ms, and 1 us of timing is 0.0086% of c, which is "
            "0.049 degC of air temperature [derived]. Averaged, that is a fast, contactless, "
            "whole-path air thermometer -- it measures the average temperature along the "
            "beam, not at a point, which no thermistor can do. The same rig reads humidity "
            "(0.35% of c from dry to saturated), wind component along the path (1.46% per 5 "
            "m/s), and gas composition (CO2 dilution shifts c measurably). (2) The "
            "threshold-amplitude bias, usually treated as an error, encodes target ACOUSTIC "
            "IMPEDANCE and roughness: a 'no echo' from a known-occupied direction means soft "
            "(a person, a curtain, foam, grass, snow) rather than missing, so absence of "
            "return is a material classification. (3) Repeatable multipath ghosts in a fixed "
            "installation are a geometric fingerprint of the room -- they change when "
            "furniture or a person moves, which turns a single static HC-SR04 into a crude "
            "occupancy/change detector without ever reading the primary echo. (4) A "
            "downward-facing unit over water or grain measures level, but note it is "
            "measuring the AIR COLUMN's temperature at the same time -- so an uncorrected "
            "tank gauge in a shed reports the shed's diurnal temperature superimposed on the "
            "level. (5) The design consequence: any HC-SR04 used for absolute distance to "
            "better than a few percent needs a co-located thermometer, and the dataset's "
            "US-100 exists precisely because that correction is the difference between a toy "
            "and an instrument."
        ),
        "px_ref": (
            "HC-SR04 Ultrasonic Module User Guide, ElecFreaks (document EF03085, no revision "
            "printed), "
            "https://elecfreaks.com/download/EF03085-HC-SR04_Ultrasonic_Module_User_Guide.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S072": {
        "px_status": "filled",
        "px_measurand": (
            "Specific force (proper acceleration) along three orthogonal axes, sensed as the "
            "displacement of a spring-suspended silicon proof mass; plus angular rate, "
            "sensed as the Coriolis force on a separate resonantly-driven mass. The "
            "accelerometer does not measure acceleration: it measures the net "
            "non-gravitational force per unit mass on the proof mass, and by the equivalence "
            "principle it cannot distinguish gravity from acceleration at all -- a "
            "stationary part reads 9.81 m/s^2 upward, a freely falling part reads zero. The "
            "gyroscope does not measure angle; angle exists only as an integral with no "
            "absolute reference."
        ),
        "px_units": "m/s^2 (specific force, datasheet in g); rad/s (angular rate, datasheet in deg/s)",
        "px_effect": (
            "Differential capacitance of a comb/parallel-plate MEMS structure as the proof "
            "mass deflects against its silicon springs (capacitive displacement of a proof "
            "mass); Coriolis coupling of a resonantly driven mass into an orthogonal sense "
            "mode for rate."
        ),
        "px_chain": "Mechanical,Electrical",
        "px_cross": [
            "temperature", "self-heating", "orientation-gravity", "acceleration", "rotation",
            "vibration", "acoustic-noise", "mechanical-stress", "supply-voltage", "aging-drift",
        ],
        "px_cross_note": (
            "temperature: gyro zero-rate output varies +/-20 deg/s over -40..+85 degC (rev "
            "3.4 electrical spec), i.e. ~0.32 deg/s per degC averaged, sign and shape "
            "device-specific and repeatable -- so an uncompensated heading integrated for 60 "
            "s after a 10 degC warm-up drifts ~190 deg. Accelerometer zero-g level changes "
            "+/-35 mg over 0..+70 degC (X/Y), ~0.5 mg/degC = 5 mm/s^2/degC, which is 0.03 "
            "deg of apparent tilt per degC. Gyro sensitivity scale factor varies +/-2% over "
            "temperature; accel cross-axis sensitivity +/-2%. self-heating: the die runs "
            "warm on 3.9 mA and the on-chip temperature sensor tracks it, so the same "
            "registers that corrupt the data also supply the compensation variable. "
            "orientation-gravity: this is not an error term, it is the signal -- 1 g of the "
            "2 g full scale is permanently consumed by gravity, and any tilt estimate is "
            "corrupted by translation and any acceleration estimate is corrupted by tilt; "
            "the two are physically indistinguishable in a single accelerometer. "
            "acceleration/rotation: centripetal acceleration at radius r couples into the "
            "accelerometer as omega^2*r, so a part 5 cm off a spin axis at 2 rev/s reads 79 "
            "mm/s^2 of spurious specific force. vibration/acoustic-noise: the accelerometer "
            "signal path is internally sampled at 1 kHz with an analog DLPF whose widest "
            "setting is 260 Hz, so energy near 1 kHz and its multiples -- motor whine, gear "
            "mesh, loud tonal sound coupled through the PCB -- folds down and appears as a "
            "slow, entirely fictitious bias drift. This is the single most common cause of "
            "'my IMU drifts on the robot'. mechanical-stress: reflow, board flex and a "
            "tightened case screw bend the LGA package and shift zero-g offset by tens of mg "
            "(initial zero-g tolerance is +/-50 mg X/Y and +/-80 mg Z, dominated by package "
            "stress), so an offset calibration is only valid for the mounting it was taken "
            "in. supply-voltage: the analog front end and the charge pump are "
            "supply-referred; a rail that sags under Wi-Fi TX bursts modulates the offsets "
            "at the burst rate. aging-drift: offsets walk over months; no bias-instability "
            "or Allan-variance spec is given -- the datasheet's silence is itself the "
            "finding for a consumer part."
        ),
        "px_range": (
            "Accelerometer +/-2 / +/-4 / +/-8 / +/-16 g = +/-19.6 to +/-157 m/s^2 (16384 "
            "LSB/g at +/-2 g, i.e. 61 ug = 0.60 mm/s^2 per LSB). Gyroscope +/-250 / +/-500 / "
            "+/-1000 / +/-2000 deg/s = +/-4.4 to +/-34.9 rad/s. Operating -40 to +85 degC."
        ),
        "px_resolution": (
            "Accelerometer noise power spectral density 400 ug/sqrt(Hz) at 10 Hz (AFS_SEL=0, "
            "ODR=1 kHz) = 3.92 mm/s^2/sqrt(Hz). Integrated: ~8.1 mg rms (79 mm/s^2) in the "
            "260 Hz DLPF setting, ~1.1 mg rms (11 mm/s^2) at the 5 Hz DLPF setting [derived, "
            "ENBW = 1.57*f_-3dB]. 1 mg of accel noise is 0.057 deg of tilt resolution. "
            "Gyroscope rate noise spectral density 0.005 deg/s/sqrt(Hz) at 10 Hz = 87 "
            "urad/s/sqrt(Hz); total 0.05 deg/s rms with DLPFCFG=2 (100 Hz). Nonlinearity "
            "0.5% accel, 0.2% gyro."
        ),
        "px_bandwidth": (
            "Accelerometer analog DLPF programmable 5-260 Hz (-3 dB); gyroscope DLPF 5-256 "
            "Hz. These are the anti-alias filters, not the output rate: the internal accel "
            "sample rate is 1 kHz and the gyro 8 kHz when the DLPF is bypassed, so anything "
            "the DLPF does not stop above those rates aliases irreversibly. The proof-mass "
            "mechanical resonance is not specified in rev 3.4 -- for this class of "
            "capacitive MEMS it sits several kHz above the widest DLPF, which is why "
            "out-of-band mechanical energy reaches the sampler at all."
        ),
        "px_drift": (
            "No bias-instability figure is published. Gyro ZRO variation +/-20 deg/s over "
            "the full -40..+85 degC range; gyro sensitivity scale factor variation +/-2% "
            "over temperature; accel zero-g change +/-35 mg over 0..+70 degC; accel initial "
            "zero-g offset +/-50 mg (X/Y) and +/-80 mg (Z), which is package/solder stress, "
            "not silicon. Practically: the gyro must be re-zeroed whenever the part is "
            "stationary, and the accelerometer must be re-zeroed whenever it is remounted."
        ),
        "px_implies": (
            "Label: motion tracking. Physically it is a three-axis specific-force meter with "
            "a 260 Hz ceiling, and everything below follows from that. (1) At rest the accel "
            "vector IS the local gravity vector, so the part is a two-axis inclinometer good "
            "to ~0.06 deg -- enough to read a door's swing angle, a solar tracker's pitch, a "
            "fridge left ajar, or the settling tilt of a post. (2) Rigidly bolted to a "
            "machine it is a vibrometer to 260 Hz with a 3.9 mm/s^2/sqrt(Hz) floor: motor "
            "imbalance shows at 1x shaft rate, misalignment at 2x, and a failing "
            "rolling-element bearing raises the broadband floor long before it is audible -- "
            "none of which is on the label. (3) Footsteps, doors and HVAC start-up couple "
            "through building structure as sub-20 Hz transients, so a part glued to a joist "
            "is an occupancy sensor. (4) The gyro is a yaw-rate sensor for things that "
            "pivot: gate position, turnstile counting, a washing-machine drum's rev counter. "
            "(5) The on-chip temperature register, nominally a compensation aid, is a free "
            "ambient thermometer with ~1 degC usefulness once self-heating is subtracted. "
            "The hard limit: because gravity and acceleration are the same quantity here, no "
            "amount of filtering separates 'the sensor tilted' from 'the sensor accelerated' "
            "-- that separation requires the gyro (short term) or a magnetometer/barometer "
            "(long term), which is precisely why this part is sold fused."
        ),
        "px_ref": (
            "MPU-6000 and MPU-6050 Product Specification, Revision 3.4, 08/19/2013, "
            "InvenSense (document PS-MPU-6000A-00), "
            "https://www.cdiweb.com/datasheets/invensense/mpu-6050_datasheet_v3%204.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S087": {
        "px_status": "filled",
        "px_measurand": (
            "Sound pressure -- the scalar deviation of absolute pressure from ambient -- at "
            "a single point (the bottom port), sensed as the displacement of a compliant "
            "MEMS diaphragm against a rigid perforated backplate. It is omnidirectional "
            "because it responds to pressure, not to a pressure gradient, so it carries no "
            "direction information whatsoever from one unit. It is a BROADBAND pressure "
            "transducer; 'audio' is a filtering choice made after the diaphragm, not a "
            "property of the diaphragm."
        ),
        "px_units": "Pa (datasheet in dB SPL re 20 uPa; 94 dB SPL = 1 Pa)",
        "px_effect": (
            "Variable capacitance between a polysilicon diaphragm and a fixed perforated "
            "backplate, held at constant charge by an on-chip charge pump so that "
            "displacement maps linearly to voltage; a vented back volume sets the "
            "low-frequency roll-off, and the resulting high-impedance signal is buffered and "
            "digitised by an on-chip sigma-delta modulator with an I2S output."
        ),
        "px_chain": "Mechanical,Electrical",
        "px_cross": [
            "vibration", "acoustic-noise", "temperature", "humidity", "condensation",
            "dust-fouling", "airflow", "wind", "pressure", "emi-rf", "supply-voltage",
            "clock-drift", "aging-drift",
        ],
        "px_cross_note": (
            "vibration: the diaphragm is a mass on a spring inside a package bolted to "
            "something. Structure-borne vibration accelerates the package and therefore "
            "displaces the diaphragm relative to it, producing an output that is "
            "indistinguishable from sound. This is normally called 'handling noise' and "
            "treated as a defect; it is the reason a MEMS mic pressed against a pipe or a "
            "motor casing works as a contact accelerometer. airflow/wind: a MEMS mic port is "
            "a hole, and turbulence over a hole generates pseudo-sound with enormous "
            "low-frequency energy -- outdoors an unshielded INMP441 is wind-noise-limited, "
            "not acoustics-limited, and the 60 Hz high-pass is the only thing keeping it "
            "from saturating. pressure: static ambient pressure changes bias the diaphragm's "
            "rest position and change back-volume compliance; this is a second-order "
            "sensitivity shift, but the vent that makes it small is also what kills DC "
            "response. temperature: sensitivity and the charge-pump bias both move with "
            "temperature; operating range -40 to +85 degC, and the part is specified for a "
            "nominal +/-1 dB-class sensitivity tolerance rather than being calibrated, so "
            "absolute SPL claims carry a few dB of part-to-part error regardless of "
            "temperature. humidity/condensation: water in the port or on the diaphragm "
            "mass-loads it and rolls off the high end; condensation inside the back volume "
            "shifts sensitivity by dB and is only partly reversible. dust-fouling: particles "
            "in the port do the same permanently. supply-voltage: power supply rejection -75 "
            "dBFS -- with a full-scale of 120 dB SPL that means supply ripple appears at an "
            "equivalent 45 dB SPL, ABOVE the 33 dBA SPL self-noise, so a noisy 3.3 V rail is "
            "the dominant noise source in most ESP32 builds, not the microphone. "
            "clock-drift: the part is a slave to the I2S bit clock and its internal "
            "decimation filter scales with it, so the anti-alias corner and hence the "
            "measured spectrum move with the master's sample rate -- an ESP32 I2S clock that "
            "is 0.5% off makes every measured frequency 0.5% off. emi-rf: the high-impedance "
            "diaphragm node is on-die and shielded, but the digital I2S lines radiate and, "
            "on long runs, reflect."
        ),
        "px_range": (
            "Acoustic overload point 120 dB SPL = 20 Pa (full scale of the digital output). "
            "Equivalent input noise 33 dBA SPL = 0.89 mPa A-weighted [derived], giving 87 dB "
            "of dynamic range. THD 3% at 105 dB SPL, so the usable linear top is nearer 105 "
            "dB SPL (3.6 Pa) than 120. Sensitivity -26 dBFS at 94 dB SPL, 1 kHz. Operating "
            "-40 to +85 degC."
        ),
        "px_resolution": (
            "SNR 61 dBA (20 Hz - 20 kHz, A-weighted); equivalent input noise 33 dBA SPL = "
            "0.89 mPa rms. Spread over an A-weighted noise bandwidth of order 13.5 kHz that "
            "is ~8 uPa/sqrt(Hz) [derived, not a datasheet figure] -- roughly a "
            "ten-thousandth of the BMP280's per-root-hertz pressure floor, which is the "
            "whole point: these two parts measure the same physical quantity in "
            "non-overlapping bands."
        ),
        "px_bandwidth": (
            "-3 dB at 60 Hz (low) and 15 kHz (high); flat between. The 60 Hz corner is a "
            "deliberate high-pass formed by the back-volume vent plus a digital DC blocker, "
            "and it is the single most destructive thing in the part's physics: infrasound "
            "and quasi-static pressure -- building sway, HVAC surge, the pressure step of a "
            "door closing in a sealed room, wind loading, a vehicle's cabin pressure pulse "
            "-- are attenuated to nothing. Above 15 kHz the diaphragm keeps responding (MEMS "
            "mic port/back-volume Helmholtz resonances typically sit in the 20-30 kHz region "
            "and produce a response peak) but the on-chip decimation filter, whose corner "
            "tracks the I2S sample rate, increasingly attenuates it: at a 48 kHz frame rate "
            "there is real, unspecified sensitivity out to ~20 kHz."
        ),
        "px_drift": (
            "No aging spec is published. Sensitivity is a factory-trimmed typical with "
            "min/max limits, not a calibration; expect a few dB of unit-to-unit spread, "
            "which sets the accuracy floor for any absolute dB(A) measurement built on this "
            "part. Long-term drift in the field is dominated by port contamination and "
            "moisture ingress rather than by silicon."
        ),
        "px_implies": (
            "Label: voice capture. Physically it is a 0.89 mPa-floor, 20 Pa-ceiling pressure "
            "transducer with a 60 Hz - 15 kHz window, and that window -- not the word "
            "'microphone' -- decides what it can infer. (1) Machine identification: every "
            "motor, pump, compressor and fan has a line spectrum at its shaft rate and "
            "blade-pass frequency, all comfortably inside the window, so one mic in a "
            "utility room reports which appliances are running and for how long, which is "
            "non-intrusive load monitoring without any electrical connection. (2) Water: "
            "laminar-to-turbulent transition in pipework radiates broadband 200 Hz - 5 kHz "
            "noise, so a mic clamped to a pipe (using the vibration cross-sensitivity, not "
            "the acoustic port) distinguishes a running tap from a toilet fill from a leak, "
            "and a leak's signature is a CONSTANT low-level hiss with no start/stop "
            "structure. (3) Compressed air and steam leaks radiate strongly from 20 to 60 "
            "kHz; the part rolls off there, but the audible 10-15 kHz tail of a leak still "
            "rises clearly above a quiet plant-room floor, so a cheap I2S mic is a "
            "first-pass leak locator. (4) Rain intensity from the impact rate on a resonant "
            "surface; road traffic counting from tyre noise envelopes; glass-break detection "
            "from the characteristic 5 kHz shatter transient. (5) What the part CANNOT do, "
            "and this is the design consequence: everything below 60 Hz is gone. Door "
            "pressure pulses, building stack effect, HVAC static pressure and infrasound "
            "from distant machinery are all attenuated to nothing by the vent. Recovering "
            "them requires pairing this mic with a barometer (S192) -- the two together span "
            "0 Hz to 15 kHz of the same physical quantity, and neither one alone does."
        ),
        "px_ref": (
            "INMP441 Omnidirectional Microphone with Bottom Port and I2S Digital Output, "
            "InvenSense (TDK), document DS-INMP441-00, Revision 1.1, 05/21/2014, "
            "https://product.tdk.com/system/files/dam/doc/product/sw_piezo/mic/mems-mic/data_"
            "sheet/inmp441.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S094": {
        "px_status": "partial",
        "px_measurand": (
            "Whether a spring-suspended conductive mass has momentarily broken contact -- "
            "i.e. whether the instantaneous specific force on the mass exceeded a threshold "
            "set by the spring's contact preload. It is a one-bit accelerometer with a "
            "mechanically fixed, undisclosed threshold, and because gravity contributes to "
            "the preload, that threshold DEPENDS ON ORIENTATION. The module's LM393 "
            "comparator and potentiometer do not change the mechanical threshold at all; "
            "they only set the electrical level at which the already-binary contact signal "
            "is declared a logic transition."
        ),
        "px_units": (
            "dimensionless (contact state); the underlying threshold is a specific force in "
            "m/s^2, set by spring stiffness / mass and by tilt, and is not specified by any "
            "manufacturer document"
        ),
        "px_effect": (
            "A helical spring surrounding a central pin (or a conductive mass in a plated "
            "barrel) held in contact by its own preload; inertial force from acceleration "
            "deflects the spring and momentarily opens or closes the contact. The result is "
            "a stochastic burst of make/break events whose RATE and duty cycle -- not any "
            "single event -- carry amplitude information. Downstream, an LM393 "
            "open-collector comparator squares this into a digital line."
        ),
        "px_chain": "Mechanical,Electrical",
        "px_cross": [
            "orientation-gravity", "acceleration", "vibration", "acoustic-noise", "temperature",
            "humidity", "contact-resistance", "aging-drift", "supply-voltage",
            "mechanical-stress", "dust-fouling",
        ],
        "px_cross_note": (
            "No manufacturer document specifies ANY of these numerically; the module is sold "
            "with a one-page reseller sheet giving only 3.3-5 V supply, an LM393 comparator, "
            "a normally-closed default state, a sensitivity potentiometer and a 3.2 x 1.4 cm "
            "board. The following are mechanism statements, not quoted figures. "
            "orientation-gravity: gravity acts on the same mass that acceleration acts on, "
            "so tilting the device changes the static preload on the contact and therefore "
            "its trigger threshold; a SW-420 lying flat and one standing on end are "
            "different sensors. A unit that begins chattering at rest is reporting a TILT "
            "change, not vibration. acceleration/vibration: the element is a mass on a "
            "spring and therefore has a mechanical resonance (a few tens to a couple of "
            "hundred hertz for this class of spring switch); its sensitivity peaks sharply "
            "there and falls off both sides, so the same 'vibration' at 20 Hz and 200 Hz "
            "produce wildly different event rates. It is a narrow-band detector pretending "
            "to be broadband. acoustic-noise: loud low-frequency sound couples into the "
            "spring through the board. supply-voltage: the LM393 threshold is set by a "
            "potentiometer divider off the rail, so rail droop moves the electrical trigger "
            "point (though not the mechanical one). "
            "contact-resistance/humidity/dust-fouling/aging-drift: bare sliding contacts "
            "oxidise and collect dust; the make resistance rises and the chattering "
            "statistics change over months, with no spec to bound it. temperature: spring "
            "modulus falls roughly 2-4% per 100 degC for common spring steels, so the "
            "threshold drifts slowly with temperature -- unquantified."
        ),
        "px_range": (
            "Binary output only. Supply 3.3-5 V. No acceleration threshold, no g-range, no "
            "frequency response, no bounce time and no temperature range is stated in any "
            "available document. Board 3.2 x 1.4 cm. Default contact state closed (module "
            "output low with the green LED on), opening on vibration."
        ),
        "px_resolution": (
            "One bit per event. There is no amplitude resolution in a single sample -- but "
            "there IS amplitude information in the aggregate: integrating the digital pin's "
            "open-duty over a 100 ms window converts the switch into a monotonic (not "
            "calibrated) vibration magnitude estimate, and the event RATE rises with "
            "excitation amplitude above threshold. This is the standard way to get more than "
            "one bit out of the part and it is nowhere in any documentation."
        ),
        "px_bandwidth": (
            "Not specified. Physically bounded above by the spring-mass resonance and below "
            "by the fact that a sub-threshold slow tilt produces no event at all -- there is "
            "no DC response and no low-frequency response. The LM393 stage on the module "
            "usually carries an RC that stretches each event, which sets the observed "
            "minimum pulse width rather than any property of the transducer."
        ),
        "px_drift": (
            "Unspecified. The mechanical threshold drifts with spring relaxation, contact "
            "wear and oxidation; the electrical threshold drifts with the potentiometer and "
            "the supply. Nothing in this part is calibrated or calibratable, and two units "
            "from the same reel commonly differ visibly in sensitivity."
        ),
        "px_implies": (
            "Label: a vibration alarm. Physically it is a free, zero-standby-power, "
            "orientation-dependent threshold accelerometer -- and its uselessness for "
            "measurement is exactly what makes it useful as a gate. (1) Wake-on-motion: the "
            "contact can pull an ESP32 out of deep sleep with no ADC, no bus and no "
            "quiescent current in the sensor itself, so a SW-420 in front of an MPU-6050 "
            "lets the expensive sensor sleep until something moves -- the pairing is worth "
            "far more than either part alone. (2) Appliance state from event rate: a washing "
            "machine, dryer, pump or compressor produces a characteristic burst density; a "
            "100 ms duty integration distinguishes 'off', 'running', and 'spin/unbalanced' "
            "without any spectral analysis. (3) Tamper and knock detection on doors, "
            "windows, meters and enclosures. (4) The orientation cross-sensitivity, normally "
            "a defect, is a second channel: a unit that changes its resting state has been "
            "tilted, so the same part is a coarse tilt/tip-over alarm for bins, gates and "
            "equipment. (5) The honest limitation, and why this entry is marked partial: "
            "nothing about the threshold, the resonance or the drift is documented by "
            "anyone, so a SW-420 can only ever produce a RELATIVE, self-referenced signal. "
            "Any absolute claim about it must be established by measurement against a "
            "calibrated accelerometer on the specific unit, in the specific orientation, on "
            "the specific mount."
        ),
        "px_ref": (
            "VERIFY: Vibration Sensor (SW-420 module), Rajguru Electronics, undated "
            "single-page reseller document, "
            "https://components101.com/sites/default/files/component_datasheet/Vibration-Sens"
            "or-Datasheet.pdf -- no manufacturer datasheet for the SW-420 switching element "
            "exists in the public record. Unverified and unavailable: acceleration trigger "
            "threshold in g, mechanical resonance, frequency response, contact bounce time, "
            "temperature coefficient, orientation dependence, operating temperature range, "
            "contact life. Every quantitative statement above is derived from the mechanism "
            "(mass-on-spring contact switch), not quoted from a document."
        ),
        "px_ref_kind": "datasheet",
    },

    "S097": {
        "px_status": "filled",
        "px_measurand": (
            "Charge generated by time-varying strain in a 28 um poled PVDF film -- i.e. the "
            "RATE of change of strain, not strain itself. The element is a charge source in "
            "parallel with its own 480 pF capacitance, so the voltage you measure is the "
            "strain high-pass-filtered by the RC formed with whatever the amplifier "
            "presents. It has exactly zero DC response: a permanently bent element outputs "
            "nothing after a few time constants, and a static load is invisible by "
            "construction."
        ),
        "px_units": (
            "C (charge) per unit strain; V across the 480 pF source capacitance; 50 mV/g = "
            "5.1 mV per m/s^2 in the cantilever configuration"
        ),
        "px_effect": (
            "Direct piezoelectric effect in beta-phase poled PVDF (polyvinylidene fluoride), "
            "a ferroelectric polymer. The film is laminated off the neutral axis of a "
            "polyester beam, so beam bending puts the film in tension/compression along the "
            "1-axis and the d31 coefficient (-33e-12 m/V) converts that strain to surface "
            "charge. The same material is strongly PYROELECTRIC (30e-6 C/m^2/K), which is "
            "not a separate part -- it is the same dipole alignment responding to "
            "temperature instead of strain."
        ),
        "px_chain": "Mechanical,Electrical",
        "px_cross": [
            "temperature", "thermal-gradient", "ir-radiation", "airflow", "acoustic-noise",
            "vibration", "cable-capacitance", "emi-rf", "body-capacitance", "humidity",
            "aging-drift", "mechanical-stress",
        ],
        "px_cross_note": (
            "temperature/thermal-gradient/ir-radiation: this is the big one. PVDF's "
            "pyroelectric coefficient is 30 uC/m^2/K, so a temperature change of the film "
            "produces charge indistinguishable from bending charge. A hand held near the "
            "element, a breath, a draught from an opening door, or sunlight falling on it "
            "produces a large, slow output in exactly the sub-10 Hz band where the piezo "
            "signal is weakest. TE's piezo film literature states outright that "
            "'pyroelectric response of piezo film can also become a noise source' and "
            "recommends common-mode rejection between two films to separate them. Sign: "
            "heating the film generates charge of one polarity, cooling the other, so the "
            "response to a passing warm body is bipolar. airflow: a draught is BOTH a "
            "convective cooling step (pyroelectric) and a mechanical force on the 25 mm "
            "cantilever (piezo) -- an unmassed LDT0 waves visibly in a breeze. "
            "acoustic-noise: the same cantilever is an efficient microphone above ~50 Hz; a "
            "bare element in a room picks up speech. cable-capacitance: the element's source "
            "capacitance is only 480 pF, so a 1 m coax at ~100 pF/m attenuates the signal by "
            "~17% and adds triboelectric noise when the cable moves; a short lead into a "
            "high-Z buffer is not optional. body-capacitance/emi-rf: a bare high-impedance "
            "piezo node is a superb E-field antenna; a hand approaching without touching "
            "swings the output volts, and mains hum couples in freely -- shield or lose the "
            "low-frequency band. humidity: surface conduction across the film edges lowers "
            "the effective load resistance and therefore RAISES the low-frequency corner, so "
            "the sensor's own bandwidth changes with the weather. mechanical-stress: bending "
            "to 90 degrees produces above 70 V, which will destroy an unprotected MCU input "
            "-- clamp diodes are part of the sensor, not an accessory. aging-drift: PVDF "
            "depoles progressively above ~80 degC; operating range is 0 to +85 degC and "
            "sensitivity falls permanently if that is exceeded."
        ),
        "px_range": (
            "Self-generating and effectively unbounded at the top: ~7 V open-circuit for 2 "
            "mm tip deflection, above 70 V bent to 90 degrees. As an accelerometer, 50 mV/g "
            "off resonance and 1.4 V/g at resonance with no added mass. Operating 0 to +85 "
            "degC, storage -40 to +85 degC. There is no low end other than the amplifier's "
            "noise -- the film itself generates charge for arbitrarily small strain."
        ),
        "px_resolution": (
            "No noise figure is published, because the element is a passive charge source: "
            "the noise floor is set entirely by the amplifier's current noise flowing in the "
            "bias resistor and by the Johnson noise of that resistor, both integrated across "
            "the 480 pF source capacitance. Practically, a FET-input buffer with a 10 Mohm "
            "bias resistor gives a thermal noise density of ~0.4 uV/sqrt(Hz) at the node, "
            "which against 50 mV/g is ~8 ug/sqrt(Hz) [derived] -- better than any consumer "
            "MEMS accelerometer, but only above the RC corner and with no DC reference at "
            "all."
        ),
        "px_bandwidth": (
            "Deliberately configurable and the most interesting property of the part. The "
            "low-frequency -3 dB corner is f = 1/(2*pi*R*C) with C = 480 pF: 1 Mohm gives "
            "332 Hz, 10 Mohm gives 33 Hz, 100 Mohm gives 3.3 Hz -- the datasheet's quoted "
            "3.3 Hz to 330 Hz range is exactly this, i.e. YOU choose the sensor's bandwidth "
            "by choosing a resistor. The cantilever's mechanical resonance is 180 Hz bare, "
            "90 Hz with 1 g of added tip mass, 60 Hz with 2 g and 40 Hz with 3 g, with a Q "
            "of about 28 (50 mV/g off resonance vs 1.4 V/g at resonance) [derived]. So added "
            "mass TUNES the part into a narrow, high-gain band. The PVDF material itself is "
            "usable from ~0.001 Hz to 10^9 Hz; the 180 Hz figure is the beam, not the film, "
            "and a film bonded flat to a structure responds well into the hundreds of kHz "
            "for acoustic emission."
        ),
        "px_drift": (
            "No DC response and therefore no zero to drift -- charge leaks away with the RC "
            "time constant (1.7 ms at 1 Mohm, 48 ms at 100 Mohm) [derived]. What does drift: "
            "sensitivity, through progressive depoling with time at temperature "
            "(accelerating above ~80 degC), and the low-frequency corner, through "
            "humidity-dependent surface leakage. Temperature also changes the film's elastic "
            "modulus and hence the beam's resonant frequency by a few percent across the "
            "operating range."
        ),
        "px_implies": (
            "Label: a knock/vibration switch. Physically it is a tunable-bandwidth dynamic "
            "strain sensor with an inherent high-pass and a strong thermal channel. (1) "
            "Because it has no DC response and enormous open-circuit gain, it is an "
            "excellent EVENT sensor and a useless level sensor: impacts, footsteps on a "
            "floor tile, a raindrop on a roof panel, water hammer in a pipe, a door knock, a "
            "machine's start transient. (2) The resonance is a design variable: gluing 2 g "
            "of mass on the tip converts a broadband element into a 60 Hz-selective "
            "vibration sensor with 28x gain, which is a cheap way to build a single-line "
            "vibration alarm for a 3600 rpm machine (60 Hz shaft rate) without any DSP at "
            "all. (3) Bonded flat to metal rather than used as a cantilever, PVDF is an "
            "acoustic-emission pickup usable into the hundreds of kHz -- crack growth, "
            "bearing spalling, and the ultrasonic hiss of a compressed-air or steam leak, "
            "none of which the 180 Hz cantilever spec suggests. (4) The pyroelectric "
            "cross-sensitivity is a second sensor hiding in the same part: with a high bias "
            "resistance and a slow amplifier, an LDT0 behind a window is a passive-infrared "
            "motion detector responding to a warm body's transit, and shielded from air "
            "currents it is a heat-flux gauge. Two elements differentially wired separate "
            "the two channels -- one gets both the mechanical and thermal signal, one only "
            "the thermal. (5) The trap: the same 3.3 Hz corner that gives you a clean impact "
            "edge also destroys any information about how long a load stayed applied. "
            "Weight, occupancy duration and static tilt are all invisible."
        ),
        "px_ref": (
            "LDT with Crimps Vibration Sensor/Switch -- LDT0-028K Piezo Vibration Sensor, TE "
            "Connectivity / Measurement Specialties, document 1002794-0 Rev 1, 10/13/2008, "
            "https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/LDT_Series.pdf ; material "
            "constants (pyroelectric coefficient 30e-6 C/m^2/K, d31 -33e-12 m/V, g31 216 "
            "Vm/N, 0.001 Hz-1 GHz usable range) from Piezo Film Sensors Technical Manual, "
            "Measurement Specialties / Images SI Sensor Products Division, "
            "https://www.imagesco.com/sensors/piezofilm.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S098": {
        "px_status": "filled",
        "px_measurand": (
            "Surface strain on an aluminium parallel-beam flexure, read as the ratio of "
            "bridge output to bridge excitation (V/V). Nothing in the signal chain measures "
            "force or mass: the gauges measure strain, the ADC measures a voltage RATIO (its "
            "reference is the excitation, so the measurement is inherently ratiometric), and "
            "force is a calibration constant applied afterwards. At full scale the strain is "
            "of order 500 microstrain and the bridge imbalance is 1 mV per volt of "
            "excitation."
        ),
        "px_units": "m/m (strain) at the gauge; V/V (mV/V) at the bridge; N after calibration",
        "px_effect": (
            "Strain-induced resistance change of bonded metal-foil gauges, dR/R = GF * "
            "epsilon with gauge factor ~2 (geometric change plus piezoresistance of the "
            "alloy), arranged as a four-active-arm Wheatstone bridge with two gauges in "
            "tension and two in compression on a parallel-beam flexure so that bending is "
            "summed and off-axis load, temperature and excitation drift are nominally "
            "common-mode. The HX711 is a chopper-stabilised PGA feeding a 24-bit sigma-delta "
            "whose reference is derived from the same excitation rail."
        ),
        "px_chain": "Mechanical,Electrical",
        "px_cross": [
            "temperature", "thermal-gradient", "self-heating", "creep", "hysteresis",
            "aging-drift", "mechanical-stress", "vibration", "orientation-gravity", "humidity",
            "contact-resistance", "supply-voltage", "ground-noise", "emi-rf", "clock-drift",
        ],
        "px_cross_note": (
            "Worked for a 10 kg TAL220-class cell at 5 V excitation, full-scale output 1.0 "
            "mV/V = 5 mV. temperature: the CELL, not the ADC, sets the floor. Cell "
            "temperature effect on zero is +/-0.05 %FS per 10 degC = 0.5 g/degC on a 10 kg "
            "cell; the HX711's own offset drift of +/-6 nV/degC is 1.2 ppm of FS per degC = "
            "0.012 g/degC -- 42x smaller [derived]. Cell temperature effect on span is also "
            "+/-0.05 %FS/10 degC; the HX711 gain drift of +/-5 ppm/degC is negligible beside "
            "it. A scale left in a shed swinging 20 degC day to night moves its zero by ~10 "
            "g with no load change at all. creep: +/-0.05 %FS per 3 minutes = 5 g on a 10 kg "
            "cell after a step load, recovering slowly after unload -- 50x the 0.1 g noise "
            "floor, and the reason a beehive or silo monitor must model load history rather "
            "than trusting a single reading. hysteresis: +/-0.05 %FS = 5 g; repeatability "
            "+/-0.03 %FS = 3 g; nonlinearity +/-0.05 %FS = 5 g. So: noise 0.1 g, systematics "
            "3-5 g. thermal-gradient: a gradient ALONG the beam defeats the bridge's "
            "common-mode rejection because the four gauges are no longer at the same "
            "temperature -- sunlight on one end of a cell is far worse than a uniform "
            "temperature change. self-heating: 5 V across ~1000 ohm is 25 mW dissipated in "
            "the bridge, which warms the flexure and produces a slow settling curve for "
            "minutes after power-up. mechanical-stress/orientation-gravity: the cell is only "
            "calibrated for its specified mounting; a twisted mounting plate, an "
            "over-torqued bolt or a tilted installation puts a permanent strain into the "
            "flexure and moves zero. vibration: the HX711 samples at 10 or 80 SPS with no "
            "analog anti-alias filter ahead of the sigma-delta's decimator, so machinery "
            "vibration and a swinging load fold down into a static offset rather than "
            "showing up as noise. humidity: moisture in the gauge adhesive and the "
            "strain-relief changes zero over days; sealed cells drift less. "
            "contact-resistance: a corroded or under-torqued bridge connection unbalances "
            "the bridge directly -- a 1 ohm change in a 1000 ohm arm is 1000 ppm, 200x full "
            "scale. supply-voltage/ground-noise: the measurement is ratiometric so "
            "excitation drift cancels, but only if the ADC reference and the bridge "
            "excitation are the same node; ground-return currents from a WiFi radio sharing "
            "the bridge ground do not cancel. clock-drift: the HX711's sinc filter puts "
            "notches at multiples of the output rate, so 10 SPS rejects 50 Hz mains well "
            "only if the clock is accurate; running on the internal RC oscillator moves the "
            "notches off mains and lets hum through as a slow beat. emi-rf: the bridge "
            "output is 5 mV full scale on a long unshielded cable -- it is an antenna, and "
            "rectified RF appears as a DC offset."
        ),
        "px_range": (
            "Cell: 3-50 kg (aluminium) or 80-200 kg (alloy steel) rated capacity, safe "
            "overload 120 %FS, rated output 1.0 +/-0.15 mV/V, excitation 5-10 Vdc, bridge "
            "1000 ohm. Front end: HX711 differential input +/-20 mV at gain 128 with a 5 V "
            "AVDD, so a 1 mV/V cell at 5 V excitation uses only 25% of the converter's span "
            "[derived]. Cell compensated -10 to +40 degC, operating -10 to +55 degC."
        ),
        "px_resolution": (
            "HX711 input-referred noise 50 nV rms at 10 SPS (gain 128) and 90 nV rms at 80 "
            "SPS. Against a 5 mV full-scale bridge output that is 1.0e-5 of FS at 10 SPS = "
            "0.1 g rms on a 10 kg cell, or 0.18 g rms at 80 SPS [derived]. Expressed as "
            "noise-free counts at 6.6 sigma peak-to-peak: ~15,000 counts (13.9 noise-free "
            "bits) at 10 SPS and ~8,400 counts (13.0 bits) at 80 SPS [derived] -- i.e. a "
            "24-bit converter delivers about 14 usable bits with this cell, and the "
            "remaining 10 bits are marketing. No spectral density is published; at 10 SPS "
            "the 50 nV rms in a ~5 Hz noise bandwidth is of order 22 nV/sqrt(Hz) [derived]."
        ),
        "px_bandwidth": (
            "Output data rate 10 SPS or 80 SPS, and this is an ODR not a bandwidth: the "
            "sigma-delta needs 4 conversions to settle after a channel or gain change, so a "
            "real step response is 400 ms at 10 SPS. The mechanical side is much faster -- a "
            "loaded beam's first resonance is typically tens of hertz -- so every mechanical "
            "transient above 5 Hz is aliased, not filtered. There is no analog anti-alias "
            "filter in the signal path."
        ),
        "px_drift": (
            "Cell: creep +/-0.05 %FS/3 min, zero temperature effect +/-0.05 %FS/10 degC, "
            "span temperature effect +/-0.05 %FS/10 degC, zero unbalance +/-0.1 %FS, "
            "hysteresis +/-0.05 %FS. Front end: offset drift +/-6 nV/degC (1.2 ppm FS/degC), "
            "gain drift +/-5 ppm/degC. The honest summary: the ADC is 40x quieter and 40x "
            "more stable than the transducer it is reading, so every improvement effort "
            "belongs on the mechanics, the mounting and the thermal environment, never on "
            "the ADC."
        ),
        "px_implies": (
            "Label: a kitchen/parcel scale. Physically it is a 0.1 g-resolution strain gauge "
            "with a 5 g systematic error budget, which sorts its off-label uses cleanly into "
            "'dynamic, excellent' and 'static, mediocre'. (1) Dynamic: 0.1 g = 1 mN of "
            "resolution is far below the ~0.1-1 N ballistic force of a heartbeat, so a beam "
            "cell under one leg of a bed or chair is a ballistocardiograph and respiration "
            "monitor -- heart rate, breathing rate, restlessness and bed-exit, none of them "
            "on the label and none of them affected by creep because they are AC. (2) Slow "
            "but differential: a beehive on a cell reports nectar inflow by day, evaporative "
            "water loss overnight (a clean sawtooth), and a swarm departure as a step of "
            "order 1 kg -- all well above the 5 g systematics. (3) The cell is a thermometer "
            "you did not ask for: at 0.5 g/degC on a 10 kg cell, an UNLOADED cell resolves "
            "~0.2 degC, so a spare cell in the same enclosure is a matched temperature "
            "reference for compensating the loaded one. (4) A strain gauge on a structure "
            "rather than a flexure reads structural load directly -- bolt preload, shelf "
            "sag, a gate's hinge force, tension in a guy wire. (5) The hard limit: any claim "
            "of 'weight change per day' finer than ~0.1 %FS is measuring the instrument, not "
            "the world, because creep and tempco alone occupy that band."
        ),
        "px_ref": (
            "HX711 24-Bit Analog-to-Digital Converter (ADC) for Weigh Scales, Avia "
            "Semiconductor (Xiamen), English edition (no revision printed), "
            "https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf ; "
            "transducer figures from Parallel Beam Load Cell TAL220, HTC-SENSOR (no revision "
            "printed), "
            "https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/TAL220M4M5Update.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S099": {
        "px_status": "filled",
        "px_measurand": (
            "The true microscopic contact area between a semiconductive polymer film and a "
            "set of interdigitated electrodes -- i.e. how many asperities on the two "
            "surfaces have been pressed into electrical contact. It is NOT a force sensor "
            "and it is NOT a pressure sensor. Force enters only through how it flattens "
            "surface roughness over the 12.7 mm active area, so the same force delivered "
            "through a soft pad, a rigid puck or a point gives three different readings. The "
            "device conductance, not its resistance, is the quantity that is roughly "
            "proportional to applied force."
        ),
        "px_units": (
            "S (siemens, conductance); resistance in ohms is the raw observable but is a "
            "reciprocal, not a linear, measure"
        ),
        "px_effect": (
            "Percolation and quantum-tunnelling conduction through a thin semiconductive "
            "polymer layer pressed against interdigitated electrodes: increasing load "
            "increases both the number of conducting asperity contacts and the area of each, "
            "so R falls as an approximate power law in force (1/R roughly linear over the "
            "useful decade), with a stand-off spacer holding the film clear below the "
            "actuation threshold."
        ),
        "px_chain": "Mechanical,Electrical",
        "px_cross": [
            "temperature", "humidity", "hysteresis", "creep", "aging-drift",
            "contact-resistance", "mechanical-stress", "vibration", "target-geometry",
            "supply-voltage",
        ],
        "px_cross_note": (
            "The most important thing about this part's cross-sensitivities is that the "
            "datasheet does not specify them at all -- there is no temperature coefficient, "
            "no linearity figure and no drift figure anywhere in Interlink's FSR 402 sheet, "
            "and that absence is the honest headline. What IS specified: part-to-part "
            "repeatability +/-6%, single-part repeatability +/-2%, hysteresis +10% ((RF+ - "
            "RF-)/RF+), recommended operating range -30 to +70 degC. target-geometry: the "
            "dominant real-world error and the one that is never in a spec sheet -- the "
            "polymer responds to contact area, so a 5 N load through a 3 mm ball and the "
            "same 5 N through a 12 mm rigid disc differ by a large factor; a compliant "
            "actuator that spreads with load makes the response steeper than the material's "
            "own law. Any FSR without a defined, rigid, area-matched puck is not "
            "reproducible even in principle. temperature: the polymer's conduction is "
            "thermally activated and its modulus falls with heat, so both the resistance at "
            "a given load and the load needed to actuate move with temperature; unquantified "
            "by the manufacturer, typically several percent per 10 degC in practice. "
            "humidity: the polymer and its substrate absorb moisture, changing modulus and "
            "surface conduction. hysteresis/creep: +10% hysteresis means the reading depends "
            "on whether you are loading or unloading; and under a sustained load the contact "
            "area keeps growing (polymer creep), so a static reading drifts downward in "
            "resistance for minutes -- again unquantified. mechanical-stress: the sensor is "
            "a flexible laminate, so BENDING the substrate changes the film/electrode gap "
            "and produces output with no load applied; mounting an FSR on anything that "
            "flexes gives you a bend sensor in series with your force sensor. "
            "contact-resistance: the tails are a crimped flexible circuit; a marginal ZIF or "
            "solder joint adds ohms in series with a device whose loaded resistance can be "
            "only a few kilohms. supply-voltage: in the usual voltage-divider circuit the "
            "output is ratiometric to the rail, so an ESP32 reading it against an internal "
            "reference sees rail droop as force."
        ),
        "px_range": (
            "Force sensitivity range 0.1 to 10.02 N (about 10 g to 1 kg of dead weight); "
            "actuation force 0.1 N; unactuated resistance greater than 10 Mohm (a true open, "
            "drawing essentially no current when idle). Recommended operating temperature "
            "-30 to +70 degC. Active area 12.7 mm diameter (FSR 402)."
        ),
        "px_resolution": (
            "No noise or resolution figure is published. The limit is not electrical -- an "
            "ESP32's 12-bit ADC across a divider resolves far finer than the sensor repeats "
            "-- it is the device's own +/-2% single-part repeatability, so the usable "
            "resolution is about 2% of reading, i.e. roughly 6 discriminable levels per "
            "decade of force over the ~2-decade usable span [derived]. Between parts, +/-6% "
            "means no two FSRs are interchangeable without individual calibration."
        ),
        "px_bandwidth": (
            "Device rise time under 3 microseconds (measured with a steel ball) -- "
            "extraordinarily fast, because the transduction is a contact-closure process "
            "with no mass-spring resonance in the sensing path at all. This is the part's "
            "most under-used property: its static accuracy is poor and its dynamic response "
            "is better than almost any load cell. There is no low-frequency limit and no "
            "high-pass, so unlike a piezo it responds to DC -- just not accurately."
        ),
        "px_drift": (
            "Hysteresis +10%; part-to-part repeatability +/-6%; single-part repeatability "
            "+/-2%. No creep, tempco or aging figure is given by the manufacturer. "
            "Empirically the polymer creeps under sustained load and the actuation threshold "
            "rises with cycle count as the stand-off and film wear."
        ),
        "px_implies": (
            "Label: a force sensor. Physically it is a fast, area-sensitive, DC-coupled "
            "contact switch with an analog middle. (1) The <3 us rise time makes it an "
            "impact TIMING instrument that no strain-gauge scale can match: drum and "
            "instrument triggers, ball-strike detection, the exact onset of a footfall, "
            "contact/no-contact transitions in a gripper -- all with microsecond timing "
            "resolution and 2% amplitude information. (2) The >10 Mohm unloaded resistance "
            "means an idle FSR draws zero current and can sit as a wake-on-touch input for "
            "years on a coin cell; as a binary occupancy sensor (chair, bed, mat, shelf) it "
            "is essentially perfect while being essentially useless as a scale. (3) Because "
            "it responds to contact AREA, an array of FSRs or a single FSR with a "
            "deliberately soft interface becomes a shape/area sensor: it distinguishes a "
            "palm from a fingertip, a foot from a paw, a full pallet from a corner-loaded "
            "one -- reading area, which is exactly the property that ruins it as a force "
            "gauge. (4) Its substrate-bending sensitivity, normally a mounting error, turns "
            "an FSR glued to a panel into a creak/flex detector for structures. (5) The "
            "design consequence: use it for WHEN and roughly HOW HARD, never for HOW MUCH; "
            "anything needing better than 10% absolute belongs on a strain gauge (S098), and "
            "the two are complementary rather than competing -- the FSR catches the "
            "transient the 10 SPS HX711 aliases away."
        ),
        "px_ref": (
            "FSR 400 Series Round Force Sensing Resistor -- FSR 402 Data Sheet, Interlink "
            "Electronics, P/N 94-00011 Rev. A, "
            "https://cdn.sparkfun.com/assets/8/a/1/2/0/2010-10-26-DataSheet-FSR402-Layout2.pd"
            "f"
        ),
        "px_ref_kind": "datasheet",
    },

    "S151": {
        "px_status": "filled",
        "px_measurand": (
            "The open/closed state of two mechanically offset sliding contacts as a "
            "patterned commutator disc rotates under them. The measurand is contact state "
            "versus shaft angle, not angle: there is no absolute reference, no zero, and no "
            "memory. Angle exists only as an accumulated count from an arbitrary origin, and "
            "every power cycle erases it. The quarter-cycle physical offset between the two "
            "tracks is what encodes direction -- the phase order of the two switch closures, "
            "not the closures themselves."
        ),
        "px_units": (
            "dimensionless (quadrature counts); rad after scaling -- 15 pulses/rev = 24 "
            "deg/pulse, 6 deg per quadrature edge"
        ),
        "px_effect": (
            "Mechanical make-and-break of sliding metal contacts on a patterned insulating "
            "disc (a commutator). Two contact fingers sit a quarter of a pattern period "
            "apart, so their switch waveforms are in quadrature; a detent spring and star "
            "wheel provide the tactile click and hold the disc at a stable point in the "
            "cycle. Conduction is ohmic contact, so the only 'signal' is a resistance that "
            "steps between ~100 mohm and open."
        ),
        "px_chain": "Mechanical,Electrical",
        "px_cross": [
            "contact-resistance", "vibration", "mechanical-stress", "temperature", "humidity",
            "condensation", "dust-fouling", "aging-drift", "emi-rf", "cable-capacitance",
            "ground-noise", "clock-drift",
        ],
        "px_cross_note": (
            "contact-resistance: 100 mohm initially, 200 mohm after rated rotational life. "
            "That is irrelevant against a 10 kohm pull-up, but the SAME wear that doubles "
            "the resistance also lengthens the chatter -- the two are the same physical "
            "process (contact film growth and asperity wear), so bounce duration is a wear "
            "telemetry channel. chattering/bounce: 2 ms max for EC11B/EC11E/EC11G (and 8 ms "
            "chatter / 5 ms bounce for the larger EC111/EC20A), and this is the dominant "
            "error source in every naive implementation: an interrupt on any edge sees a "
            "burst of transitions per detent and counts 3 where the user turned 1. It is not "
            "noise, it is the physics of a mechanical contact, and it is why an EC11 must be "
            "debounced in time (a >=5 ms filter) or in state (a quadrature state machine "
            "that only accepts legal transitions). vibration/mechanical-stress: a contact "
            "held at rest near a transition point will chatter under external vibration, so "
            "a panel-mounted encoder on a machine generates counts with nobody touching it "
            "-- a 'phantom rotation' that is really a vibration report. "
            "humidity/condensation/dust-fouling: sliding contacts are open to the air; "
            "moisture films and dust raise contact resistance and dramatically lengthen "
            "chatter, so an encoder's bounce statistics track the enclosure's humidity. "
            "temperature: -30 to +85 degC (EC11B) or -40 to +85 degC (EC11E/G/J); lubricant "
            "viscosity changes the rotational torque (10 +/- 7 mN.m nominal) so the feel and "
            "the achievable rotation rate change in the cold. aging-drift: rotational life "
            "ranges from 15,000 cycles (EC11B) to 100,000 (EC11E/EC11G) to 1,000,000 (EC11J) "
            "-- a factor of 67 between variants of the 'same' part, which is the single most "
            "consequential spec for anything that turns continuously rather than being "
            "knob-twiddled. cable-capacitance/ground-noise/emi-rf: the contacts are a bare "
            "switch on a high-impedance pull-up; a long cable turns each transition into a "
            "ringing edge and picks up mains and motor noise as false counts. clock-drift: "
            "irrelevant to position (counts are counts) but it scales any rate derived from "
            "them."
        ),
        "px_range": (
            "Unbounded rotation (continuous, no endstop) -- but only 15 pulses per "
            "revolution and 30 detents per revolution on the common EC11B/E/G, i.e. 24 deg "
            "per pulse, 12 deg per detent, 6 deg per quadrature edge [derived]. 18- and "
            "36-detent variants exist. Integrated push switch rated 3 A 16 V DC on most "
            "variants (0.5 A 12 V DC on EC11J). -40 to +85 degC (EC11E/G/J)."
        ),
        "px_resolution": (
            "6 degrees per quadrature edge (24 edges/rev) in principle, but only 12 degrees "
            "is trustworthy because the detent parks the disc mid-cycle, so the finest "
            "reliable quantum is one detent. There is no noise floor in the analog sense -- "
            "the output is binary -- but there IS an error floor: the +/-2 ms chatter means "
            "edges arriving closer than 2 ms apart cannot be distinguished from bounce, "
            "which is a hard limit on resolution at speed rather than at rest."
        ),
        "px_bandwidth": (
            "Set by the 2 ms bounce, not by any filter: usable edge rate is roughly 500/s, "
            "and since there are 60 quadrature edges per revolution at 15 ppr, that is about "
            "8 rev/s before the bounce windows of successive edges overlap and counts are "
            "lost. At a hand-spin of 5 rev/s the edges are only 3.3 ms apart [derived] -- "
            "barely 1.7x the bounce spec, which is precisely why fast spins under-count. "
            "Rotational torque 10 +/- 7 mN.m sets the mechanical time constant of anything "
            "driving it."
        ),
        "px_drift": (
            "No offset or gain to drift -- counts are exact. What degrades is contact "
            "quality (100 -> 200 mohm over life) and chatter duration, and what is lost is "
            "absolute position: at every power cycle the count restarts at whatever the "
            "software says, so an encoder alone can never report where something IS, only "
            "how much it has moved. Rotational life 15,000 to 1,000,000 cycles depending on "
            "variant."
        ),
        "px_implies": (
            "Label: a volume knob. Physically it is a bidirectional event counter with "
            "12-degree quanta and no absolute reference, which makes it a general-purpose "
            "rotation transducer for anything that spins or unwinds. (1) On a shaft it is a "
            "tachometer AND a direction sensor: a wind-cup rotor (rev rate -> wind speed), a "
            "water meter's register dial, a rain gauge's mechanism, a spool. (2) On a "
            "spring-loaded cable reel it becomes a draw-wire linear displacement sensor with "
            "unbounded range and 12-degree -> few-millimetre resolution, which the dataset "
            "already exploits separately -- a door position sensor, a tank float, a "
            "plant-growth or snow-depth gauge. (3) The bounce spec is a second, free sensor: "
            "contact chatter duration rises with wear, humidity and contamination, so "
            "logging the distribution of bounce lengths on a continuously-turned encoder "
            "predicts its own failure and reports enclosure condition. (4) Phantom counts "
            "with nobody touching the knob are a vibration report, not a bug -- a panel "
            "encoder is a crude machine-running detector. (5) The structural limit: because "
            "there is no absolute reference, an encoder must always be paired with something "
            "absolute (a limit switch, a hall sensor, a potentiometer, an accelerometer's "
            "gravity vector) to anchor its origin. And because it is a wear part with as few "
            "as 15,000 cycles in the cheapest variant, anything turning continuously -- a "
            "wind sensor at 1 rev/s is 86,400 cycles per day -- will destroy an EC11B in "
            "hours and needs a non-contact encoder instead. That failure mode is the "
            "strongest argument in the whole catalogue for a magnetic or optical alternative."
        ),
        "px_ref": (
            "EC11 Series Incremental Type 11mm Size Rotary Encoder, Alps Alpine "
            "(EC11B/EC11E/EC11G/EC11J specification pages; no revision printed), "
            "https://www.avnet.com/fsp/opasdata/d120001/medias/docus/196/Alps-Alpine-EC11-Ser"
            "ies-EN-Datasheet.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S192": {
        "px_status": "filled",
        "px_measurand": (
            "Absolute pressure: the net force per unit area on a micromachined silicon "
            "diaphragm, referenced to a sealed evacuated cavity beneath it. It is not an "
            "altimeter and not a weather sensor -- it is a differential force gauge against "
            "a vacuum, and every altitude or weather number is a downstream assumption about "
            "air density and about what the atmosphere was doing an hour ago."
        ),
        "px_units": "Pa",
        "px_effect": (
            "Piezoresistance in boron-doped silicon strain gauges diffused into a "
            "micromachined diaphragm and wired as a Wheatstone bridge; diaphragm deflection "
            "strains the gauges and unbalances the bridge in proportion to the pressure "
            "difference across it. A co-integrated bandgap temperature sensor supplies the "
            "compensation term."
        ),
        "px_chain": "Mechanical,Electrical",
        "px_cross": [
            "temperature", "thermal-gradient", "self-heating", "airflow", "wind",
            "acoustic-noise", "mechanical-stress", "condensation", "dust-fouling", "altitude",
            "aging-drift",
        ],
        "px_cross_note": (
            "temperature: temperature coefficient of offset +/-1.5 Pa/K, which the datasheet "
            "itself translates as 12.6 cm of apparent altitude per kelvin. This is the "
            "dominant error and it is 10x the RMS noise for a single degree of drift: an "
            "enclosure warmed 10 K by afternoon sun moves the reading ~15 Pa = 1.3 m of "
            "fictitious altitude, which is larger than most of the signals people build with "
            "this part. thermal-gradient: a gradient across the package strains the "
            "diaphragm asymmetrically, so heating one side (a nearby regulator, a sunlit "
            "wall) is worse than heating the whole part uniformly. self-heating: 2.7 uA at 1 "
            "Hz forced mode is negligible; continuous 182 Hz normal mode at ~700 uA is not, "
            "and it warms the die into its own TCO. airflow/wind: dynamic pressure q = "
            "0.5*rho*v^2, so with rho = 1.2 kg/m^3 a 5 m/s draught across an unbaffled port "
            "is 15 Pa and a 10 m/s gust is 60 Pa -- 46x the 1.3 Pa noise floor. An exposed "
            "port is an anemometer whether you wanted one or not. acoustic-noise: the port "
            "plus internal cavity is an acoustic low-pass, but a door slam in a closed room "
            "is a genuine tens-of-Pa pressure step, not acoustic noise, and shows up "
            "cleanly. mechanical-stress: the die is stress-sensitive; reflow, board flex and "
            "potting shift the offset by hectopascal-scale amounts, which is why Bosch "
            "specifies a mounting footprint and why absolute accuracy is +/-1.0 hPa while "
            "relative accuracy is +/-0.12 hPa (~1 m). condensation/dust-fouling: liquid or "
            "dust in the port changes the acoustic path and, if it bridges the port, "
            "decouples the diaphragm from ambient entirely -- the reading goes quiet and "
            "stable, which looks like good data. altitude: dP/dh = -rho*g = -12.0 Pa/m at "
            "sea level, so altitude and pressure are the same measurement and cannot be "
            "separated without a second reference. aging-drift: long-term stability +/-1.0 "
            "hPa over 12 months = 8.3 m of apparent altitude per year, which forbids "
            "absolute altimetry outright."
        ),
        "px_range": (
            "300 to 1100 hPa (30 to 110 kPa), equivalent to +9000 to -500 m relative to sea "
            "level. Temperature channel -40 to +85 degC, +/-1.0 degC accuracy over 0..+65 "
            "degC."
        ),
        "px_resolution": (
            "1.3 Pa RMS noise in ultra-high-resolution mode (x16 pressure oversampling), "
            "falling to 0.2 Pa with the lowest-bandwidth IIR filter setting. 1.3 Pa = 10.8 "
            "cm of altitude at sea level [derived at 12.0 Pa/m]; 0.2 Pa = 1.7 cm. The "
            "datasheet quotes RMS at a stated oversampling rather than a spectral density; "
            "at the ~26 Hz ultra-high-res output rate that 1.3 Pa rms in a ~13 Hz noise "
            "bandwidth is of order 0.36 Pa/sqrt(Hz) [derived, not a datasheet figure]."
        ),
        "px_bandwidth": (
            "No analog -3 dB figure is specified; the response is set by conversion time and "
            "the optional IIR filter. Fastest measurement cycle 5.5 ms typical "
            "(ultra-low-power), maximum output rate 182 Hz; ultra-high-resolution cycles "
            "take ~38 ms. The port and internal cavity form a mechanical low-pass ahead of "
            "all of that, so genuine kHz acoustics are attenuated while sub-hertz pressure "
            "changes pass unmolested -- the opposite of a microphone."
        ),
        "px_drift": (
            "Offset tempco +/-1.5 Pa/K (12.6 cm/K). Long-term stability +/-1.0 hPa per 12 "
            "months. Absolute accuracy +/-1.0 hPa over 300-1100 hPa, 0-65 degC; relative "
            "accuracy +/-0.12 hPa (+/-1 m) over 700-900 hPa at 25 degC. The gap between "
            "+/-1.0 hPa absolute and +/-0.12 hPa relative is the whole design brief: this "
            "part measures CHANGE well and LEVEL badly."
        ),
        "px_implies": (
            "Label: barometer / altimeter. Physically it is a 1.3 Pa-resolution absolute "
            "force gauge, and 1.3 Pa is 11 cm of air. (1) Vertical position indoors: "
            "floor-level localisation, counting lift travel, distinguishing stairs from a "
            "lift, detecting a fall as a 20-30 cm step in 200 ms. (2) Room state: opening a "
            "door between a sealed room and a corridor produces a transient of tens of Pa "
            "and a permanent offset of a few Pa; a barometer indoors is a door/window sensor "
            "with no line of sight and no moving parts. (3) HVAC: duct static pressure and "
            "filter loading are 50-250 Pa signals, right in the middle of this part's usable "
            "span. (4) A barometer in a SEALED enclosure stops measuring the weather and "
            "starts measuring the enclosure: P/T is constant for a fixed mass of gas, so "
            "pressure normalised by the on-chip temperature reports the enclosure's leak "
            "rate -- a free gasket-integrity monitor. (5) Two barometers differenced cancel "
            "the weather (which is common-mode over any building) and leave metre-level "
            "relative altitude that does not drift with the synoptic pattern. (6) Three-hour "
            "pressure tendency, not pressure, is the forecasting variable: a 3 hPa fall in 3 "
            "hours is a gale signature, and the +/-0.12 hPa relative accuracy is 25x better "
            "than that threshold while the +/-1.0 hPa absolute accuracy is useless for it. "
            "The failure mode to design against is thermal: at 1.5 Pa/K the sensor reports "
            "its own enclosure temperature roughly as loudly as it reports a person walking "
            "up one flight of stairs."
        ),
        "px_ref": (
            "BMP280 Digital Pressure Sensor Data Sheet, Bosch Sensortec, document "
            "BST-BMP280-DS001-26, revision 1.26, October 2021, "
            "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bm"
            "p280-ds001.pdf"
        ),
        "px_ref_kind": "datasheet",
    },


    # ========================================================================
    # Electrical, RF and bio — 10 sensors.
    # S067, S070, S081, S084, S104, S113, S129, S144, S146, S213
    # ========================================================================

    "S067": {
        "px_status": "filled",
        "px_measurand": (
            "Complex (amplitude and phase) reflectivity of the scene as a function of range, "
            "sampled in 0.75 m distance gates out to 6 m. The primitive is not 'presence' "
            "but per-gate reflected energy plus the *time evolution of phase* in each gate: "
            "a stationary human is detected because chest-wall motion of well under a "
            "millimetre changes the round-trip phase by a substantial fraction of a radian "
            "(dphi = 4*pi*dx/lambda, lambda = 12.5 mm, so 1 mm of displacement = ~1.0 rad)."
        ),
        "px_units": (
            "m (range, quantised to 0.75 m gates) and dimensionless per-gate energy 0-100; "
            "underlying physical quantity is sub-millimetre radial displacement"
        ),
        "px_effect": (
            "FMCW (frequency-modulated continuous-wave) radar: a 250 MHz linear sweep across "
            "24.00-24.25 GHz, with range from the beat frequency of the deramped echo and "
            "micro-motion from inter-sweep phase"
        ),
        "px_chain": "Electrical,Radiant,Mechanical,Radiant,Electrical",
        "px_cross": [
            "target-reflectivity", "target-geometry", "multipath", "airflow", "vibration",
            "precipitation", "humidity", "emi-rf", "temperature", "supply-voltage",
            "acoustic-noise",
        ],
        "px_cross_note": (
            "multipath: with a +/-60 degree field of view and no angular resolution in the "
            "LD2410B/C, every gate contains the coherent sum of everything at that range in "
            "a spherical shell -- including reflections that arrive via a wall or ceiling "
            "and therefore appear at a range longer than the true one. A room with metal "
            "furniture produces persistent ghost targets at fixed gates that look exactly "
            "like a stationary person. target-reflectivity + target-geometry: a human is "
            "detected via water content, so a person in a thick down jacket, or lying under "
            "a duvet, returns markedly less; a metal chair or a fan returns far more and "
            "will dominate the gate it occupies. airflow: a curtain, an oscillating fan, or "
            "a hanging plant produces genuine coherent micro-motion in the same 0.1-2 Hz "
            "band as respiration, and this is the number-one false-presence source. HVAC "
            "turning on and off correlates with false detections. vibration: because the "
            "module measures sub-mm displacement, vibration of the *mounting surface* -- a "
            "hollow plasterboard wall next to a door, a desk -- modulates every gate "
            "simultaneously; a whole-array common-mode signature is a structure-vibration "
            "measurement, not a target. precipitation + humidity: 24 GHz suffers little "
            "atmospheric attenuation indoors, but a wet outer housing or condensation on the "
            "radome detunes the antenna and reduces range; standing water on a surface is a "
            "strong specular reflector. emi-rf: the 24.00-24.25 GHz ISM band is shared with "
            "other 24 GHz presence radars, automotive blind-spot radars and motion-activated "
            "door openers; two LD2410s facing each other produce spurious sweeps. "
            "temperature: the VCO's sweep linearity and the antenna's match drift, which "
            "degrades range accuracy rather than presence detection. supply-voltage: 5 V "
            "(5-12 V accepted) at ~80 mA average, and the module's own switching draws "
            "current in step with the sweep, so a shared rail couples radar activity into "
            "other sensors. Logic on the UART and OUT pins is 3.3 V, but the *supply* is 5 V "
            "-- the module is not a 3.3 V-powered part."
        ),
        "px_range": (
            "0.75 m to 6 m, configurable, in eight or nine 0.75 m distance gates; field of "
            "view +/-60 degrees. Range resolution is bandwidth-limited to c/(2B) = 0.6 m for "
            "the 250 MHz sweep (derived), which is why the gates are 0.75 m and why sub-gate "
            "range numbers from this module are interpolation, not measurement."
        ),
        "px_resolution": (
            "0.75 m in range; per-gate energy quantised 0-100 with a user threshold. In "
            "phase, the module is sensitive to displacements far below a millimetre -- which "
            "is what 'stationary target' detection actually means. The engineering (debug) "
            "mode exposes per-gate moving and static energy arrays, which is the real data "
            "product; the OUT pin discards all of it."
        ),
        "px_bandwidth": (
            "Micro-motion band of interest 0.1-0.5 Hz (respiration) and 0.8-2 Hz "
            "(heartbeat-driven chest-wall motion); gross motion up to a few hertz. The "
            "reporting frame rate over UART (256000 baud default, ~10-20 frames/s) sets the "
            "practical ceiling, and the module's own presence/absence decision has a "
            "configurable multi-second hold that removes everything faster."
        ),
        "px_drift": (
            "No published tempco. The dominant slow error is scene drift: the module's "
            "background estimate adapts, so a piece of furniture moved once is absorbed over "
            "minutes, and a slowly-warming radiator or a settling curtain shows up as "
            "wandering static energy in fixed gates. Repeated re-calibration on a scene that "
            "contains a sleeping person will slowly learn that person as background."
        ),
        "px_implies": (
            "Sold as a 'human presence' switch, the physics delivers a sub-millimetre "
            "displacement profiler over range that works through plastic, drywall, wood and "
            "fabric and is stopped by metal and foil-backed insulation. The three inferences "
            "the label hides are: (1) per-gate static energy is a coarse range map of the "
            "room's dielectric contents, so it detects furniture rearrangement, an open "
            "versus closed door, and whether a bed is occupied -- through the mattress; (2) "
            "the 0.1-0.5 Hz component of a single gate's phase is a respiration-rate "
            "measurement, and its variability over a night is a sleep-stage proxy, obtained "
            "with no camera, no microphone and no contact; (3) the common-mode signal across "
            "all gates is not a target at all but the mounting structure's vibration, which "
            "makes the module an accidental building-motion and footfall sensor. PRIVACY: "
            "this is the important part. A 5 GBP module hidden inside a plastic enclosure "
            "measures the breathing rate of a person in the next room, through the wall, "
            "without their knowledge and without emitting anything a person can perceive. "
            "Deploying it in a shared or rented space is a surveillance decision, not a "
            "convenience decision, and it should be disclosed. It is also not a medical "
            "device: a respiration rate derived this way is an awareness signal, never a "
            "clinical measurement, and it fails silently on a target that is shielded, "
            "tangential or behind metal."
        ),
        "px_ref": (
            "HLK-LD2410 Human Presence Sensing Module User Manual, Shenzhen Hi-Link "
            "Electronic Co., Ltd, Version V1.02, 8 June 2022, "
            "https://www.sudo.is/docs/esphome/components/ld2410/HLK-LD2410_manual_v1.02.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S070": {
        "px_status": "partial",
        "px_measurand": (
            "Doppler beat frequency between a free-running ~3.18 GHz microwave oscillator "
            "and the echo returned from a moving reflector -- i.e. the target's radial "
            "velocity component, not its presence, position or size. The transistor "
            "oscillator is also the mixer (a self-oscillating mixer), so the module "
            "additionally responds to reactive near-field loading of its own antenna: a "
            "dielectric body close to the board pulls the oscillator frequency directly."
        ),
        "px_units": (
            "m/s radial velocity (transduced to Hz of beat frequency: f_d = 2v/lambda, "
            "lambda ~= 94 mm, so ~21 Hz per m/s -- derived); output is a single logic level"
        ),
        "px_effect": (
            "Doppler shift on a continuous-wave microwave carrier, detected by "
            "self-oscillating mixing; plus oscillator frequency pulling by near-field "
            "dielectric loading"
        ),
        "px_chain": "Electrical,Radiant,Mechanical,Radiant,Electrical",
        "px_cross": [
            "target-reflectivity", "target-geometry", "multipath", "airflow", "vibration",
            "precipitation", "emi-rf", "temperature", "supply-voltage", "ambient-light",
            "acoustic-noise",
        ],
        "px_cross_note": (
            "target-reflectivity: the module responds to radar cross-section, so it sees a "
            "moving metal object (a door, a car, a fan blade, a filing-cabinet drawer) far "
            "more strongly than a person, and sees a person through a wooden door or a "
            "drywall partition almost as well as in free air. It is essentially blind to "
            "anything that is not moving *toward or away from it*, however large. "
            "target-geometry: purely tangential motion produces zero Doppler shift, so "
            "someone walking across the beam at constant range is invisible while the same "
            "person walking toward it at 0.1 m/s (a ~2 Hz beat) trips it. multipath: with an "
            "omnidirectional PCB antenna and no range gate, reflections from behind and "
            "beside the board count equally; mounting it inside a metal box turns the box "
            "into a resonant cavity and the module into an extremely sensitive vibration "
            "detector for the box itself. airflow: moving curtains, plant leaves and even "
            "dense rising warm air with entrained dust produce genuine Doppler returns -- "
            "the classic false-trigger source that no sensitivity setting removes. "
            "vibration: because the oscillator and antenna are on the same FR4, mechanical "
            "vibration of the board modulates the carrier and produces a beat with no "
            "external target at all. precipitation: rain and snow are moving scatterers. "
            "emi-rf: there is no channel selectivity of any consequence; a second RCWL-0516 "
            "within a few metres beats against the first at the difference of their "
            "(uncontrolled) carrier frequencies, and 2.4 GHz WiFi/BLE transmitters and "
            "microwave ovens couple in. Two of these modules cannot coexist. temperature + "
            "supply-voltage: the carrier is a bare transistor oscillator on FR4 with no PLL; "
            "its frequency drifts with temperature and rail (documented shifts of up to ~1 "
            "MHz from a hand near the board alone), which changes the Doppler scale factor "
            "and the module-to-module beat frequency. ambient-light: only through the CDS "
            "pin, which disables detection when a light-dependent resistor pulls it below "
            "0.2*Vdd (the enable threshold is ~269 kOhm with no external resistor). "
            "acoustic-noise: loud low-frequency sound physically moves lightweight "
            "reflectors and the board itself, producing real returns."
        ),
        "px_range": (
            "5-7 m nominal detection distance for a person; adding a 1 MOhm resistor at R-GN "
            "reduces it to ~5 m. No range information whatsoever is produced -- the output "
            "is a single bit. Supply 4.0-24 V, 2.8 mA typical / 3 mA maximum, output 3.3 V "
            "at 30 mA drive."
        ),
        "px_resolution": (
            "One bit. The underlying analog beat has no published noise floor; the practical "
            "minimum detectable radial velocity is set by the ~2 s retrigger timer and the "
            "IC's fixed gain, roughly 3-5 cm/s for a human-sized target. The retrigger "
            "period follows T = (1/f) * 32768 set by the C-TM capacitor, 2 s by default."
        ),
        "px_bandwidth": (
            "Doppler beats of interest are ~0.2-20 Hz for human motion (0.01-1 m/s at 21 Hz "
            "per m/s). The RCWL-9196 signal chain is a PIR-style band-limited amplifier plus "
            "comparator with a multi-second output hold, so the output pin has an effective "
            "bandwidth of well under 1 Hz. The information is in the analog node, not the "
            "pin."
        ),
        "px_drift": (
            "No specification exists. The uncontrolled oscillator means the Doppler scale "
            "factor itself drifts with temperature and supply; the comparator threshold is "
            "fixed and untrimmed, so unit-to-unit sensitivity varies substantially. There is "
            "no self-test and no way to distinguish 'no motion' from 'oscillator dead'."
        ),
        "px_implies": (
            "The label says 'motion detected'; the physics says 'something with a radar "
            "cross-section moved radially at more than a few cm/s somewhere in a roughly "
            "spherical volume, possibly through a wall'. That difference is the whole story. "
            "It sees through drywall, wood, plastic and glass and is stopped by metal and by "
            "wet masonry, so an RCWL-0516 mounted inside a sealed weatherproof plastic box "
            "works perfectly -- and also watches the neighbouring room, which is a real "
            "privacy capability that no indicator LED discloses. It is blind to a person "
            "sitting still and blind to tangential walking, so it cannot be used for "
            "occupancy, only for transitions. Off-label, the useful signal is the analog "
            "node ahead of the comparator: tapped there, the beat frequency IS a calibrated "
            "speedometer (21 Hz per m/s), which makes it a vehicle-speed sensor, a fan/rotor "
            "tachometer (blade passing produces a comb of harmonics), a washing-machine "
            "cycle detector through a laundry-room wall, and -- for a static target -- a "
            "micro-Doppler sideband analyser whose 0.2-0.5 Hz component is a breathing rate. "
            "Its self-oscillating-mixer nature adds a second, quite different mode: a hand "
            "near the board pulls the carrier without any Doppler, so the module doubles as "
            "a short-range dielectric-proximity sensor. Because two modules interfere, an "
            "array is impossible; because the carrier is unlicensed-band and uncontrolled, "
            "regulatory compliance in a deployed product cannot be assumed from the module."
        ),
        "px_ref": (
            "VERIFY: no manufacturer datasheet with a revision or date exists for the "
            "RCWL-0516, and no datasheet at all is published for its RCWL-9196 "
            "signal-processing IC. Electrical figures from the vendor product sheet "
            "'RCWL-0516 microwave radar sensor module' (undated), "
            "https://www.mantech.co.za/datasheets/products/RCWL-0516.pdf ; the 3.181 GHz "
            "carrier, the ~1 MHz frequency pulling and the CDS threshold are SDR "
            "measurements reported in J. Desbonnet, RCWL-0516 reverse-engineering notes, "
            "https://github.com/jdesbonnet/RCWL-0516 . Carrier frequency is unit-to-unit "
            "variable and unspecified."
        ),
        "px_ref_kind": "measurement",
    },

    "S081": {
        "px_status": "filled",
        "px_measurand": (
            "Three orthogonal components of the total magnetic flux density at the die -- "
            "the vector sum of the Earth's field, every piece of ferrous metal within a few "
            "package-diameters, every current in the host PCB, and the magnetisation the AMR "
            "strips themselves are carrying. It measures the local field, never 'north'; "
            "heading is an inference that assumes the only field present is the Earth's."
        ),
        "px_units": (
            "T (registers are in gauss: 12000 LSB/G on the +/-2 G range, 3000 LSB/G on +/-8 "
            "G)"
        ),
        "px_effect": (
            "Anisotropic magnetoresistance (AMR) -- the resistance of a permalloy strip "
            "depends on the angle between its magnetisation and the current -- linearised by "
            "barber-pole biasing and periodically re-magnetised by an on-chip set/reset strap"
        ),
        "px_chain": "Magnetic,Electrical",
        "px_cross": [
            "temperature", "mechanical-stress", "supply-voltage", "emi-rf", "electric-field",
            "hysteresis", "aging-drift", "vibration", "orientation-gravity",
        ],
        "px_cross_note": (
            "temperature: sensitivity tempco +/-0.05 %/degC -- at Earth field (0.25-0.65 G) "
            "that is only ~0.2 mG/degC of gain error, but the *offset* term is far larger "
            "and is the reason a compass that was calibrated indoors is wrong outdoors. Base "
            "offset is +/-10 mG, i.e. ~2% of a 0.5 G horizontal component, worth ~1 degree "
            "of heading before any hard-iron correction. hysteresis: AMR strips retain "
            "magnetisation; a strong field (a phone speaker, a fridge magnet) flips domains "
            "and biases every subsequent reading until a set/reset pulse restores them. The "
            "set/reset is what makes AMR usable and is also a measurable disturbance -- it "
            "dumps a current pulse (2.6 mA peak) into the supply on every conversion. "
            "mechanical-stress: permalloy is magnetostrictive, so board bending and reflow "
            "stress change the sensitivity axis by a fraction of a percent, which is a "
            "permanent soft-iron-like error baked into the assembly. supply-voltage: "
            "2.16-3.6 V; the internal reference and the set/reset current both scale with "
            "rail, so a sagging LiPo shows up as a slow gain change over a discharge cycle. "
            "emi-rf / electric-field: the AMR bridge is a low-impedance resistive divider "
            "and is fairly immune to E-field, but any nearby switching current -- a WiFi TX "
            "burst on an ESP32 pulling hundreds of mA, a motor driver, a buck inductor -- "
            "makes a real magnetic field the sensor correctly reports as field. On an ESP32 "
            "board this is typically tens of mG, larger than the sensor's own noise. "
            "cross-axis: 0.1 %/G, negligible in Earth field, significant near a magnet. "
            "vibration + orientation-gravity: no direct sensitivity, but tilt converts "
            "vertical field (which is ~2/3 of the total field at mid latitudes) into the "
            "horizontal plane, so heading error from 5 degrees of un-compensated tilt is "
            "many degrees. aging-drift: hard-iron offsets drift as the host device's own "
            "steel screws and battery magnetise over time."
        ),
        "px_range": (
            "+/-2 G or +/-8 G selectable (+/-200 uT or +/-800 uT). Earth's total field is "
            "0.25-0.65 G, so the +/-8 G range exists for magnet tracking, not navigation."
        ),
        "px_resolution": (
            "2 mG (0.2 uT) field resolution, 1-sigma, from a 16-bit ADC. At a 0.5 G "
            "horizontal component that is ~0.23 degrees of heading -- so the sensor is never "
            "the limit on compass accuracy; the calibration is."
        ),
        "px_bandwidth": (
            "Set by the output data rate: 10, 50, 100 or 200 Hz. The analog chain settles "
            "much faster than a conversion, so effective bandwidth is ODR/2 at best; "
            "sampling a 200 Hz magnetic transient (a relay closing) needs the 200 Hz ODR and "
            "still aliases anything above 100 Hz."
        ),
        "px_drift": (
            "Offset +/-10 mG initial, sensitivity +/-0.05 %/degC. The set/reset strap "
            "suppresses the AMR bridge's flicker noise by chopping the magnetisation, so the "
            "1/f corner is pushed below the ODR -- long averages actually help, unlike an "
            "un-flipped bridge. Current 75-100 uA continuous at 10 Hz ODR."
        ),
        "px_implies": (
            "A 0.2 uT, 200 Hz, three-axis field logger sold as a compass is really an indoor "
            "positioning and machine-state sensor. Buildings have magnetic fingerprints -- "
            "steel rebar, lift shafts, ducting -- that are stable for years and vary by tens "
            "of uT over a metre, so the raw vector is a room-level location signal that "
            "needs no radio and cannot be jammed. A door with a steel frame, a passing car, "
            "a lift car moving in a shaft, and a filing cabinet drawer opening are all "
            "detectable ferrous-mass events at 1-3 m. Held near a mains cable it reads the "
            "50/60 Hz field -- but only if the ODR is 200 Hz, and even then it heavily "
            "aliases, which turns the aliased beat frequency into an unintended "
            "grid-frequency measurement. On a motor housing the field's harmonic content "
            "tracks rotor slip and, over months, rotor-bar degradation. The privacy "
            "corollary is real: because a magnetometer sees through walls and drywall, a "
            "QMC5883L on a desk logs when the lift arrives and when a steel door opens on "
            "the far side of a partition, without line of sight or any RF emission of its "
            "own. Practical caveat: the QMC5883L is a QST part commonly sold on boards "
            "silkscreened HMC5883L; the register maps differ entirely, so the first "
            "inference this part supports is 'which chip did I actually receive'."
        ),
        "px_ref": (
            "QMC5883L 3-Axis Magnetic Sensor, QST Corporation, Rev. A, 7/22/2016, "
            "https://qstcorp.com/upload/pdf/202202/13-52-04%20QMC5883L%20Datasheet%20Rev.%20A"
            "(1).pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S084": {
        "px_status": "filled",
        "px_measurand": (
            "Component of magnetic flux density normal to the package face at the Hall "
            "plate. The A3144 thresholds it (unipolar switch, south pole only); the SS49E "
            "reports it linearly and bipolar as a ratiometric voltage. Neither responds to a "
            "magnet's presence -- both respond to one vector component of B, which is why "
            "turning a magnet 90 degrees makes it vanish."
        ),
        "px_units": "T (datasheets use gauss; 1 G = 100 uT)",
        "px_effect": (
            "Hall effect in silicon; A3144 adds a Schmitt comparator with built-in "
            "hysteresis and temperature compensation, SS49E is an open linear amplifier"
        ),
        "px_chain": "Magnetic,Electrical",
        "px_cross": [
            "temperature", "magnetic-field", "supply-voltage", "mechanical-stress",
            "target-geometry", "orientation-gravity", "aging-drift", "hysteresis",
        ],
        "px_cross_note": (
            "temperature (of the magnet, not the sensor): NdFeB loses about -0.11 %/degC of "
            "remanence and ferrite about -0.20 %/degC, so a switch set with 20% margin at 25 "
            "degC can fail to trip at -20 degC or at +80 degC. This usually dominates any IC "
            "drift. temperature (of the IC): the A3144's Bop/Brp are temperature-compensated "
            "but still move over -40 to +150 degC; the SS49E has up to 0.185 %/degC "
            "sensitivity tempco and +/-0.10 %/degC null drift (worse, -0.15 to +0.05 %/degC, "
            "below 25 degC), so at 1.4 mV/G a 40 degC swing moves the SS49E's zero by up to "
            "10 mV = ~7 G of phantom field. magnetic-field: any field counts. A DC motor, a "
            "speaker magnet, a relay, or a nearby current-carrying wire (a wire at 5 mm "
            "carrying 10 A makes ~4 G) can hold a switch latched. supply-voltage: the SS49E "
            "null is Vcc/2 and its sensitivity is ratiometric, so supply ripple lands on the "
            "output at 0.5 V/V; the A3144's digital output is immune but its switch points "
            "shift slightly with supply. mechanical-stress and target-geometry: switch "
            "behaviour is set by air gap, and B from a small magnet falls roughly as 1/d^3 "
            "near-field, so a 1 mm change in gap at 5 mm is a ~50% change in field -- the "
            "switch is a very nonlinear displacement sensor. orientation-gravity: only "
            "through the mechanics (a pendulum, a float, a tilting magnet), but that is "
            "exactly how float switches and tilt sensors are built from it. hysteresis: the "
            "A3144 guarantees >20 G of Bhys, which is the whole reason it does not chatter "
            "-- and which makes it useless as a field meter, because the reported state "
            "depends on which way the field last moved. aging-drift: magnet remanence loss "
            "and package stress relaxation both shift the effective trip gap over years."
        ),
        "px_range": (
            "A3144 switch points: Bop 35-450 G (3.5-45 mT), Brp 25-430 G (2.5-43 mT), Bhys > "
            "20 G (> 2 mT) -- note the 13:1 unit-to-unit spread, so a single A3144 has no "
            "calibrated threshold at all. SS49E linear range +/-650 G min, +/-1000 G typ "
            "(+/-65 to +/-100 mT)."
        ),
        "px_resolution": (
            "A3144: one bit, and the guaranteed uncertainty band between 35 G and 450 G is "
            "the resolution. SS49E: analog and continuous, sensitivity 1.0/1.4/1.75 mV/G "
            "min/typ/max -- the 75% sensitivity spread means an uncalibrated SS49E gives "
            "field to no better than +/-25%; against a 12-bit ADC on 3.3 V (0.8 mV LSB) the "
            "quantisation floor is ~0.6 G."
        ),
        "px_bandwidth": (
            "SS49E response time 3 us (~100 kHz class); the A3144 is a comparator with "
            "comparable propagation, so both will follow a 100-pole rotor at tens of "
            "thousands of RPM without aliasing."
        ),
        "px_drift": (
            "SS49E null drift -0.10 to +0.10 %/degC above 25 degC and -0.15 to +0.05 %/degC "
            "below; sensitivity tempco 0.185 %/degC max. A3144 switch points drift over the "
            "-40 to +85 degC (E suffix) or -40 to +150 degC (L suffix) range despite on-chip "
            "compensation. Neither part is chopper-stabilised, so the SS49E carries real 1/f "
            "noise -- averaging below ~1 Hz buys you little."
        ),
        "px_implies": (
            "SAFETY: the A3144 requires 4.5-24 V supply -- it is NOT a 3.3 V part and must "
            "not be run from an ESP32 rail; its open-collector output can, separately, be "
            "pulled up to 3.3 V safely. The SS49E does run from 2.7-6.5 V and is 3.3 "
            "V-compatible, but then its output swings only around 1.65 V with 1.4 mV/G, "
            "halving the usable field range against a 3.3 V ADC. Off-label: because the "
            "SS49E is a calibrated-enough vector magnetometer with 3 us response and no "
            "digital housekeeping, it is the cheapest way to watch a magnetic field "
            "*waveform*. Clamped to a mains cable it reads the cable's stray field and "
            "becomes a non-contact, non-isolated load indicator; near a transformer it reads "
            "core saturation; near a stepper it reads microstep position. A pair of them at "
            "a known separation is a gradiometer that rejects the Earth's field and sees "
            "only local ferrous mass -- a vehicle detector that works through asphalt. And "
            "the A3144's terrible threshold spread is itself informative: any A3144 that "
            "trips reliably is telling you the field at its face exceeds 45 mT, which is a "
            "*lower bound* on magnet strength and air gap that no amount of software can "
            "tighten."
        ),
        "px_ref": (
            "A3141, A3142, A3143, and A3144 Sensitive Hall-Effect Switches for "
            "High-Temperature Operation, Allegro MicroSystems datasheet 27621.6B, "
            "https://www.allegromicro.com/~/media/Files/Datasheets/A3141-2-3-4-Datasheet.ashx"
            " ; linear variant: SS39ET/SS49E/SS59ET Series Linear Hall-effect Sensor ICs, "
            "Honeywell 005850-4-EN IL50, February 2015, "
            "https://prod-edam.honeywell.com/content/dam/honeywell-edam/sps/siot/ja/products/"
            "sensors/magnetic-sensors/linear-and-angle-sensor-ics/common/documents/sps-siot-s"
            "s39et-ss49e-ss59et-product-sheet-005850-3-en-ciid-50359.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S104": {
        "px_status": "filled",
        "px_measurand": (
            "Capacitance from each electrode to the device's own ground reference -- that "
            "is, the electrode's self-capacitance including everything its fringing field "
            "terminates on: the wire, the board, the enclosure, the human standing nearby, "
            "and the mains-referenced environment coupling back through the power supply. It "
            "does not measure touch; it measures a change in electrode capacitance against a "
            "continuously re-tracked baseline."
        ),
        "px_units": "F (10 pF to >2000 pF absolute; resolution quoted as 0.01 pF)",
        "px_effect": (
            "Constant-DC-current charge-transfer capacitance sensing: a programmable current "
            "(0-63 uA) is applied for a programmable time (0.5-32 us) and the resulting "
            "electrode voltage is digitised, so C = I*t/V"
        ),
        "px_chain": "Electrical",
        "px_cross": [
            "body-capacitance", "humidity", "condensation", "temperature", "cable-capacitance",
            "supply-voltage", "ground-noise", "emi-rf", "dust-fouling",
            "contamination-poisoning", "mechanical-stress", "aging-drift",
        ],
        "px_cross_note": (
            "body-capacitance: this IS the signal for touch (a fingertip adds roughly 0.1-1 "
            "pF through a few hundred microns of overlay) but it is also the largest "
            "confound, because a human body is ~100-200 pF to earth and couples the "
            "mains-referenced environment into every electrode at once. A person *near* but "
            "not touching shifts all 12 channels together -- which is exactly what the 13th "
            "'proximity' channel exploits by summing all electrodes. humidity + "
            "condensation: a water film is a conductor and bridges electrodes; at high RH a "
            "hygroscopic overlay (paper, wood, unsealed 3D print) gains surface conductivity "
            "and the baseline walks. This is the single commonest field failure. "
            "temperature: PCB FR4 permittivity and the parasitic capacitance of the trace "
            "move ~100s of ppm/degC; the auto-baseline tracker absorbs this only if it is "
            "slower than the tracker's filter, so a fast thermal transient (a hand hovering, "
            "sunlight on the panel) is indistinguishable from a slow touch. "
            "cable-capacitance: an electrode on a long wire adds tens to hundreds of pF of "
            "static capacitance, eating the dynamic range and diluting the 0.1-1 pF touch "
            "delta -- keep the run short or the auto-configuration will pick a charge "
            "current that leaves no headroom. supply-voltage + ground-noise: the measurement "
            "is a voltage read after a fixed charge, so rail noise is signal. A "
            "battery-powered board floating with respect to earth behaves completely "
            "differently from a USB-powered one, because the return path for the finger's "
            "displacement current changes. emi-rf: a nearby SMPS, a phone charger, an LED "
            "dimmer or a fluorescent ballast injects displacement current directly into the "
            "electrode; the charge-transfer scheme's fixed integration window (CDT 0.5-32 "
            "us) means noise near 1/CDT folds in, which is why the datasheet makes charge "
            "time programmable at all. dust-fouling and contamination-poisoning: conductive "
            "dust, grease and salt residue all add leakage paths. mechanical-stress: flexing "
            "the overlay changes the gap and therefore the capacitance -- an unintended but "
            "perfectly usable force signal. aging-drift: absorbed moisture in the overlay is "
            "slow and partly irreversible."
        ),
        "px_range": (
            "10 pF to over 2000 pF of electrode capacitance, 12 independent electrodes plus "
            "a 13th synthesised channel that sums all enabled electrodes into one large "
            "proximity plate. Charge current 0-63 uA in 1 uA steps, charge time 0.5-32 us; "
            "sample interval 1-128 ms."
        ),
        "px_resolution": (
            "0.01 pF, i.e. roughly 1 part in 1000 of a typical 10 pF pad and ~1-10% of a "
            "light fingertip touch. Auto-configuration picks charge current and time per "
            "electrode to place the working point in range, so real-world resolution depends "
            "on that choice rather than on a fixed LSB."
        ),
        "px_bandwidth": (
            "Programmable sample interval 1-128 ms sets it: at the 1 ms setting the "
            "effective bandwidth is a few hundred hertz and the part will resolve the "
            "approach velocity of a finger; at the 16 ms default (29 uA) it is a touch "
            "detector only. The baseline filter is a slow second loop -- anything slower "
            "than the baseline tracker is *removed* by design, which is why this part cannot "
            "report an absolute capacitance trend."
        ),
        "px_drift": (
            "The auto-baseline tracker is the drift specification: it deliberately servos "
            "out any slow environmental change (temperature, humidity, dirt) so that the "
            "reported 'touch' delta stays centred. Consequence -- a genuinely slow physical "
            "signal is erased. 29 uA typical at a 16 ms sample interval, 3 uA in stop mode; "
            "supply 1.71-3.6 V (3.3 V-native, and the datasheet's 3.6 V maximum means it "
            "must never see 5 V)."
        ),
        "px_implies": (
            "A 0.01 pF, 12-channel electrometer with per-channel baseline tracking is a "
            "distributed dielectric-imaging front end that happens to be sold as a button "
            "controller. Because it measures self-capacitance to ground rather than contact, "
            "electrodes behind a plastic wall report liquid level, foam, and whether a "
            "container is full, empty or has a hand around it. The relative timing across 12 "
            "pads gives direction and velocity of a swipe -- and, on a door frame or under a "
            "mat, direction of travel of a person who never touches anything. The 13th "
            "summed channel is a genuine proximity radar at tens of centimetres with no "
            "emission at all: it is entirely passive from the outside, so unlike PIR or "
            "mmWave it cannot be detected by a sweep. That is also its privacy edge -- a "
            "capacitive plate under a desk logs occupancy continuously and invisibly. "
            "Inverted, the humidity cross-term becomes the measurement: a bare electrode "
            "with a hygroscopic overlay and the baseline tracker disabled is a condensation "
            "and leaf-wetness sensor, and one on an unglazed pot wall is a soil-moisture "
            "sensor with no probe in the soil. Because a human body couples the "
            "mains-referenced environment into every pad simultaneously, the common-mode "
            "shift across all 12 channels is a 50/60 Hz-environment and body-earthing "
            "measurement -- it tells you whether the person is barefoot on concrete or in "
            "trainers on carpet."
        ),
        "px_ref": (
            "MPR121 Proximity Capacitive Touch Sensor Controller, Freescale/NXP, Document "
            "Number MPR121, Rev. 4, 02/2013, "
            "https://www.nxp.com/docs/en/data-sheet/MPR121.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S113": {
        "px_status": "filled",
        "px_measurand": (
            "Differential electric potential between two skin-surface electrodes -- the "
            "far-field projection onto the body surface of the summed ionic current dipoles "
            "of depolarising excitable tissue. The transduction from ionic to electronic "
            "current happens at the Ag/AgCl half-cell, not in the IC, so the amplifier's "
            "true input is an electrochemical interface with its own DC potential, impedance "
            "and noise."
        ),
        "px_units": (
            "V (differential, typically 0.5-5 mV for surface ECG, 50 uV-5 mV for surface "
            "EMG, amplified by a fixed instrumentation gain of 100 V/V)"
        ),
        "px_effect": (
            "Biopotential (electrophysiological volume conduction) sensed through an Ag/AgCl "
            "electrochemical half-cell, amplified by an instrumentation amplifier with "
            "driven-electrode (right-leg-drive) common-mode feedback and a two-pole "
            "integrated high-pass filter"
        ),
        "px_chain": "Chemical,Electrical",
        "px_cross": [
            "contact-resistance", "emi-rf", "electric-field", "body-capacitance",
            "mechanical-stress", "vibration", "acceleration", "humidity", "temperature",
            "supply-voltage", "ground-noise", "aging-drift",
        ],
        "px_cross_note": (
            "contact-resistance: the electrode-skin interface is 5 kOhm (freshly gelled) to "
            ">1 MOhm (dry, hairy, or a day-old pad), and a mismatch between the two "
            "electrodes converts common mode into differential mode, destroying the 80 dB "
            "(min) / 86 dB (typ) CMRR. Nearly every 'noisy ECG' is an impedance-mismatch "
            "problem, not an amplifier problem. The Ag/AgCl half-cell also contributes a DC "
            "offset the part tolerates up to +/-300 mV; beyond that the input saturates and "
            "the fast-restore circuit engages. emi-rf + electric-field + body-capacitance: a "
            "human body is a ~100-200 pF antenna coupling the mains-referenced environment; "
            "typical common-mode on a subject is 1-10 V at 50/60 Hz, so 86 dB CMRR still "
            "leaves 50-500 uV differential -- of the same order as a P wave. The "
            "driven-electrode amplifier (A2, 150 kOhm internal, external integrating "
            "capacitor) exists specifically to servo this down; with only two electrodes and "
            "no driven leg, the mains term wins. The residual 50/60 Hz amplitude is "
            "therefore a direct measurement of how well the subject is coupled to earth. "
            "mechanical-stress + vibration + acceleration: motion artefact is triboelectric "
            "and half-cell disturbance at the gel interface, and it is the dominant noise "
            "source in any ambulatory recording -- typically 10-100x the ECG amplitude, in "
            "the same 0.5-40 Hz band, so no filter separates it. humidity: gel dries, "
            "impedance rises, artefact grows over hours; sweat does the opposite and shorts "
            "electrodes. temperature: half-cell potentials are temperature-dependent at the "
            "millivolt level, which drives baseline wander. supply-voltage: 2.0-3.5 V only "
            "-- the AD8232 must NOT be run from a 5 V rail. Input common-mode range is 0.2 V "
            "to +Vs, so on a 3.0 V supply the electrodes must sit inside 0.2-3.0 V, which is "
            "what the on-chip mid-supply reference buffer is for. The internal RFI filter "
            "suppresses rectification of carriers (phone, WiFi) that would otherwise appear "
            "as a DC offset shift. aging-drift: the input bias current of 50-200 pA flowing "
            "into a 1 MOhm dried electrode develops 50-200 uV of offset that grows as the "
            "pad ages."
        ),
        "px_range": (
            "Instrumentation gain 100 V/V fixed, so the linear input range on a 3 V supply "
            "is roughly +/-14 mV differential about the reference -- ample for ECG (0.5-5 "
            "mV) and surface EMG, and easily saturated by motion artefact. Tolerates +/-300 "
            "mV of electrode half-cell offset before saturating."
        ),
        "px_resolution": (
            "Input-referred noise 14 uV p-p over 0.5-40 Hz (12 uV p-p over 0.1-10 Hz), 100 "
            "nV/rtHz at 1 kHz. Against a 1 mV R wave that is a noise floor ~70 dB down; "
            "against a 50 uV P wave it is only ~11 dB down, which is why P-wave morphology "
            "from a two-electrode wrist setup is not trustworthy."
        ),
        "px_bandwidth": (
            "Set entirely by external components. A two-pole high-pass is integrated into "
            "the instrumentation stage (typically 0.5 Hz for a monitoring configuration, "
            "0.05 Hz for diagnostic morphology) with an uncommitted op-amp available for a "
            "low-pass at ~40 Hz (heart-rate) or ~150 Hz (morphology) or ~500 Hz (EMG). The "
            "fast-restore circuit temporarily raises the high-pass corner after a "
            "rail-to-rail transient to shorten recovery -- which means the transfer function "
            "is not stationary and the seconds after an artefact are quantitatively "
            "unreliable."
        ),
        "px_drift": (
            "Baseline wander below 0.5 Hz is dominated by the electrode half-cell and by "
            "respiration-induced electrode motion, not by the amplifier; the amplifier "
            "itself contributes 50-200 pA of bias current and a 12 uV p-p 0.1-10 Hz noise "
            "floor. 170 uA quiescent current on a 2.0-3.5 V supply."
        ),
        "px_implies": (
            "SAFETY AND SCOPE FIRST: connecting any of this to a person makes an awareness "
            "aid, never a medical device. The AD8232 datasheet carries no diagnostic claim, "
            "there is no patient isolation in the part, and a mains-powered build must be "
            "battery-operated or use a certified medical isolation barrier -- never a USB "
            "supply tied to a mains-earthed PC while electrodes are on skin. Do not act on "
            "any waveform from it clinically. With that fixed, the physics is far broader "
            "than 'heart rate'. The same channel that reads ECG reads EMG if you move the "
            "electrodes to a muscle belly and open the low-pass to ~500 Hz -- the part is a "
            "general biopotential front end, and the *labelling* of the signal is done by "
            "electrode placement and filter choice, not by the chip. Three inferences hide "
            "in what the label calls noise: (1) the below-0.5 Hz baseline wander is "
            "respiration -- chest expansion moves the electrodes and modulates thoracic "
            "impedance, so respiration rate falls out of an ECG channel with no respiration "
            "sensor at all, and the R-R interval's respiratory modulation (sinus arrhythmia) "
            "is a second, independent estimate of the same rate plus an autonomic-tone "
            "signal; (2) the AC leads-off detection injects a small current and detects the "
            "resulting voltage, which is a direct electrode-skin impedance measurement -- "
            "usable as a contact-quality metric, a skin-hydration proxy, and the basis of a "
            "crude bioimpedance channel; (3) the residual 50/60 Hz common-mode that survives "
            "the driven electrode is a measurement of the subject's capacitive coupling to "
            "the mains environment, so it changes when they stand up, touch a radiator, or a "
            "nearby appliance switches on -- an accidental proximity and appliance-state "
            "sensor. PRIVACY: heart rate, respiration rate and their variability are health "
            "data; a device that logs them continuously is collecting health data regardless "
            "of what the enclosure is called."
        ),
        "px_ref": (
            "AD8232 Single-Lead, Heart Rate Monitor Front End Data Sheet, Analog Devices, "
            "Rev. D, "
            "https://www.analog.com/media/en/technical-documentation/data-sheets/ad8232.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S129": {
        "px_status": "partial",
        "px_measurand": (
            "Bulk apparent relative permittivity (dielectric constant) of the medium in the "
            "fringing field around a coated PCB electrode, integrated over roughly the first "
            "centimetre from the board face. Water dominates because liquid water has eps_r "
            "~ 80 against ~4 for mineral soil solids and 1 for air, but the reading is a "
            "permittivity, not a water content -- and at the board's low (roughly 1-2 MHz) "
            "excitation frequency the measured permittivity also absorbs a large "
            "conductive-loss term from dissolved salts."
        ),
        "px_units": (
            "dimensionless relative permittivity eps_r (reported as a raw ADC voltage, "
            "typically ~1.2-1.5 V wet to ~2.8-3.0 V dry on a 3.3 V board -- inverted)"
        ),
        "px_effect": (
            "Fringing-field capacitance loading an RC/relaxation oscillator; the "
            "oscillator's amplitude after rectification is read as a DC voltage. Related to "
            "water content through the Topp relation eps_b = 3.03 + 9.3*theta + 146*theta^2 "
            "- 76.7*theta^3."
        ),
        "px_chain": "Electrical",
        "px_cross": [
            "salinity-conductivity", "temperature", "soil-density", "target-geometry",
            "humidity", "condensation", "supply-voltage", "temperature-of-electronics",
            "aging-drift", "precipitation", "contamination-poisoning",
        ],
        "px_cross_note": (
            "salinity-conductivity: the headline cross-term and the reason these boards "
            "disagree with each other in the same pot. At an excitation of a few MHz the "
            "ionic conduction loss is not separable from the dielectric term, so fertiliser, "
            "road salt or a hard-water irrigation event raises the apparent permittivity and "
            "reads as 'wetter' with no change in water content. Laboratory-grade capacitance "
            "probes run at 70-100 MHz specifically to escape this; a 555-based board cannot. "
            "temperature: two opposed mechanisms. Free water's permittivity falls with "
            "temperature (~-0.36 %/degC near 20 degC), which reads drier; soil solution "
            "conductivity rises ~+2 %/degC, which reads wetter and usually wins in anything "
            "but washed sand. Net soil-dependent diurnal swing of order 1-3 %VWC over a "
            "day-night cycle with genuinely constant moisture. soil-density: the measurement "
            "is per unit volume, so compaction raises the solid fraction and the apparent "
            "permittivity for the same gravimetric water -- repotting or a heavy rain "
            "settling the surface shifts the calibration permanently. target-geometry: the "
            "fringing field is strongest within a few mm of the board, so an air gap along "
            "the insertion slot, a root touching the face, or a stone dominates the reading; "
            "insertion depth changes which fraction of the electrode is in soil at all and "
            "is a first-order gain term. humidity + condensation: dew or a water film on the "
            "exposed *upper* part of the board is read as soil water; so is condensation "
            "inside an unsealed board. precipitation: rainfall arrives as a step at the "
            "surface and propagates downward, so the shape of the wetting front is real "
            "information but the first minutes are surface film, not infiltration. "
            "supply-voltage + temperature-of-electronics: the 555-class oscillator's "
            "frequency and the rectifier's diode drop both move with rail and with the "
            "board's own temperature; a 100 mV rail sag can look like a moisture step, so "
            "these boards should be read ratiometrically or on a regulated rail. aging-drift "
            "+ contamination-poisoning: the solder mask is the only dielectric barrier; once "
            "it wicks water or is scratched, the electrode starts conducting and the board "
            "reads permanently wet. Salt and biofilm accumulate on the surface over a season."
        ),
        "px_range": (
            "eps_r roughly 1 (air) to ~80 (free water), useful soil span eps_r ~3 (oven-dry) "
            "to ~35 (saturated), which the Topp relation maps to volumetric water content 0 "
            "to ~0.55 m3/m3. Output is a monotonically *decreasing* analog voltage with "
            "wetness."
        ),
        "px_resolution": (
            "Not specified by any manufacturer. Practically the ADC and noise set it: on an "
            "ESP32's 12-bit ADC over a ~1.5 V usable span the step is ~0.4 mV, ~0.03 %VWC, "
            "which is far below the ~2-5 %VWC accuracy achievable after soil-specific "
            "calibration and meaningless without one."
        ),
        "px_bandwidth": (
            "Electrically fast (the oscillator settles in microseconds and the rectifier "
            "time constant is of order milliseconds), but the physically meaningful response "
            "is the soil's, not the board's: a wetting front takes minutes to hours to "
            "traverse the sensing volume, so anything faster than ~0.1 Hz is measuring "
            "surface film, temperature or noise, not soil water."
        ),
        "px_drift": (
            "No published tempco. Field experience and the literature on low-cost capacitive "
            "probes report calibration drift of several %VWC over a season, dominated by "
            "coating degradation and salt accumulation rather than electronics. There is no "
            "chopper and no reference, so 1/f and supply drift pass straight through."
        ),
        "px_implies": (
            "This is a dielectric probe, and every inference that follows from that is "
            "available off-label. Because it reads permittivity and not water, it is a "
            "salinity sensor whenever water content is independently known -- pair it with a "
            "gravimetric reference or a second probe at a different depth and the difference "
            "is an EC signal, which is how over-fertilisation and salt build-up in a pot "
            "become visible. Because the sensing volume is a centimetre-scale shell, a "
            "vertical stack of three probes measures the wetting front's descent velocity, "
            "which is a hydraulic-conductivity measurement of that specific soil. Because "
            "the diurnal temperature cross-term is deterministic, the daily oscillation "
            "amplitude in a *constant-moisture* probe is a soil-temperature proxy and, more "
            "usefully, a way to estimate thermal diffusivity by depth. Because it responds "
            "to any dielectric, the same board outside soil is a liquid-level, grain-fill, "
            "foam-detection and hand-proximity sensor; taped to a plastic tank it reads "
            "through the wall. And its most under-used output is the *absence* of a diurnal "
            "cycle: a probe that stops breathing with the day has either lost soil contact "
            "or flooded, a fault signal that no absolute reading gives you."
        ),
        "px_ref": (
            "VERIFY: no manufacturer datasheet with a revision exists for the generic "
            "'Capacitive Soil Moisture Sensor v1.2 / v2.0' board -- it is an unbranded clone "
            "and the oscillator frequency (commonly reported as ~1-2 MHz from an on-board "
            "555) is a community measurement, not a specification. Physics and "
            "cross-sensitivities sourced from: G. C. Topp, J. L. Davis and A. P. Annan, "
            "'Electromagnetic determination of soil water content: Measurements in coaxial "
            "transmission lines', Water Resources Research 16(3):574-582, 1980, "
            "https://doi.org/10.1029/WR016i003p00574 ; and S. Adla, N. K. Rai, S. H. "
            "Karumanchi, S. Tripathi, M. Disse and S. Pande, 'Laboratory Calibration and "
            "Performance Evaluation of Low-Cost Capacitive and Very Low-Cost Resistive Soil "
            "Moisture Sensors', Sensors 20(2):363, 2020, https://doi.org/10.3390/s20020363"
        ),
        "px_ref_kind": "paper",
    },

    "S144": {
        "px_status": "filled",
        "px_measurand": (
            "Differential voltage developed across an external metal-film shunt in series "
            "with the load (Ohm's-law drop, I*Rshunt), measured while riding on a bus "
            "common-mode potential that is separately digitised. The part is not a current "
            "sensor at all: it is a 26 V-common-mode microvoltmeter, and every current "
            "number it produces is arithmetic done against a resistor value the user "
            "asserts. It therefore actually responds to the shunt's resistance -- including "
            "that resistance's temperature coefficient and its solder-joint and trace "
            "resistance."
        ),
        "px_units": (
            "V (shunt: volts differential, 10 uV LSB; bus: volts, 4 mV LSB); reported as A "
            "and W only after multiplication by a user-supplied Rshunt in ohms"
        ),
        "px_effect": (
            "Ohmic (Joule) conduction in a four-terminal shunt, read by a chopper-stabilised "
            "(zero-drift) differential amplifier ahead of a delta-sigma ADC"
        ),
        "px_chain": "Electrical",
        "px_cross": [
            "temperature", "self-heating", "contact-resistance", "supply-voltage",
            "ground-noise", "reference-drift", "emi-rf", "aging-drift", "mechanical-stress",
        ],
        "px_cross_note": (
            "temperature + self-heating: the dominant error is not in the IC but in the "
            "shunt. A typical 0.1 ohm 1% board shunt is 50-100 ppm/degC, so a 40 degC rise "
            "reads as +0.2 to +0.4% of current, always in the direction of under-reporting "
            "current (R rises, so for a fixed I the drop rises -> over-reports; for a fixed "
            "V-source load the current genuinely falls). At 3.2 A through 0.1 ohm the shunt "
            "burns 1.0 W and self-heats tens of degC in seconds -- the reading therefore "
            "drifts with a thermal time constant of its own, which is itself a measurement "
            "of the shunt's thermal resistance to the board. temperature (IC): the chopper "
            "front end contributes only 0.1 uV/degC offset drift and 1 m%/degC gain drift, "
            "i.e. the silicon is ~500x more stable than the resistor in front of it. "
            "contact-resistance: a non-Kelvin layout puts solder-joint and trace resistance "
            "(1-10 mohm, and itself +3900 ppm/degC for copper) in series with a 100 mohm "
            "shunt -- a 1-10% gain error that grows as the board warms. supply-voltage / "
            "ground-noise: CMRR is 100 dB min / 120 dB typ, so 1 V of bus ripple injects "
            "1-10 uV RTI = 0.1-1 LSB; below that floor the part is genuinely immune to "
            "common mode over 0-26 V. reference-drift: bus and shunt channels share one "
            "reference, so ratiometric power (V*I) partially cancels reference error while "
            "either channel alone does not. emi-rf: there is no anti-alias filter ahead of "
            "the ~500 kHz (+/-30%) delta-sigma modulator; the conversion window (84 us at 9 "
            "bit to 68.10 ms at 12 bit x128 average) is a rectangular boxcar, so any tone "
            "not near a boxcar null folds into the reading. A PWM or SMPS switching at a "
            "frequency close to a multiple of 1/T_conv aliases down to a slow, spurious "
            "'load drift'. mechanical-stress: board flex changes the shunt's resistance by "
            "piezoresistivity at the 10s of ppm level -- negligible for power logging, "
            "measurable if the shunt is a bare 1 mohm strip. aging-drift: shunt resistors "
            "shift ~0.1-0.5% over years of thermal cycling; the IC does not."
        ),
        "px_range": (
            "Shunt +/-40 mV (PGA /1) to +/-320 mV (PGA /8); bus 0-16 V or 0-32 V, common "
            "mode 0-26 V. With the near-universal 0.1 ohm board shunt this is +/-400 mA to "
            "+/-3.2 A."
        ),
        "px_resolution": (
            "10 uV shunt LSB (= 100 uA with 0.1 ohm, 10 mA with 1 mohm); 4 mV bus LSB. "
            "Offset is the real floor: +/-50 uV RTI (INA219B) = +/-500 uA on a 0.1 ohm "
            "shunt, i.e. 5 LSB of dead reckoning you cannot average away."
        ),
        "px_bandwidth": (
            "No analog -3 dB input bandwidth is specified. The response is set by the boxcar "
            "conversion window: -3 dB at approximately 0.443/T_conv (derived), so ~5.3 kHz "
            "for the 84 us 9-bit window, ~830 Hz for the 532 us 12-bit window, and ~6.5 Hz "
            "for the 68.10 ms 128-average window. Choosing the conversion time IS choosing "
            "the analog bandwidth."
        ),
        "px_drift": (
            "Offset 0.1 uV/degC (chopper-stabilised, so no meaningful 1/f corner in-band -- "
            "the chopper moves flicker noise up to the chopping rate). Gain error +/-40 m% "
            "typ with 1 m%/degC tempco. Input bias 20 uA in active mode flows out of the "
            "sense pins and drops on the source impedance ahead of the shunt. All of this is "
            "dwarfed by the external shunt's 50-100 ppm/degC."
        ),
        "px_implies": (
            "A 10 uV / ~830 Hz voltmeter sitting across a load is a behaviour sensor, not an "
            "energy meter. Sampled continuously at the 84 us conversion time it resolves the "
            "individual current pulses of a switching regulator, so the ripple frequency IS "
            "a tachometer for the converter and a fingerprint for which device is plugged "
            "in; a shift in that ripple frequency is a measurement of the converter's "
            "feedback loop and, on a DC-DC, of its input voltage. On a battery rail, "
            "stepping the load and watching the bus channel's recovery measures the cell's "
            "internal impedance -- a state-of-health estimate from a part sold as a "
            "fuel-free ammeter. On a DC motor, the current waveform's commutation ripple "
            "counts rotations without an encoder, and the growth of the ripple's broadband "
            "floor is bearing wear. Because bus and shunt are digitised separately, sign of "
            "the shunt channel tells you power flow direction -- a solar/battery node's "
            "charge/discharge state. Conversely, a 'current drift' report is ambiguous by "
            "construction: it is equally consistent with the load changing, the shunt "
            "warming up, or a solder joint fatiguing, and only a second temperature channel "
            "separates them. Mains use is out of scope for this part: with a 0-26 V "
            "common-mode limit it can only be used on the low-voltage side, and any "
            "mains-referenced shunt requires galvanic isolation the INA219 does not provide."
        ),
        "px_ref": (
            "INA219 Zero-Drift, Bidirectional Current/Power Monitor With I2C Interface, "
            "Texas Instruments SBOS448G, original August 2008, latest revision December "
            "2015, https://www.ti.com/lit/ds/symlink/ina219.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

    "S146": {
        "px_status": "filled",
        "px_measurand": (
            "Magnetic flux density in the die's Hall plate, generated by current flowing in "
            "the 1.2 mohm copper lead frame that passes directly under it. The part responds "
            "to total field at that point -- it cannot distinguish the field made by 'its' "
            "conductor from the field of any other conductor, magnet or motor nearby."
        ),
        "px_units": (
            "T at the Hall plate (reported ratiometrically as V; 185 mV/A for the 05B, 100 "
            "mV/A for the 20A, 66 mV/A for the 30A variant)"
        ),
        "px_effect": (
            "Hall effect in a doped-silicon plate, with dynamic offset cancellation "
            "(spinning-current chopping) and a ratiometric Vcc/2 output pedestal"
        ),
        "px_chain": "Electrical,Magnetic,Electrical",
        "px_cross": [
            "magnetic-field", "temperature", "supply-voltage", "self-heating", "emi-rf",
            "mechanical-stress", "aging-drift", "target-geometry",
        ],
        "px_cross_note": (
            "magnetic-field: this is the big one and the datasheet does not quantify it. The "
            "Hall plate sees the vector sum of the lead-frame field and any external field. "
            "A small neodymium magnet a centimetre away, or the stray field of a "
            "transformer, relay coil or an adjacent current-carrying wire, adds a "
            "full-scale-class offset: at 185 mV/A the 05B needs only a few gauss of external "
            "field to read a spurious amp. Mount two ACS712s side by side on a busbar and "
            "each reads a blend of both currents. temperature: the output pedestal drifts "
            "-0.35 to -0.07 mV/degC and sensitivity drifts +0.054 to -0.008 mV/A/degC "
            "depending on variant and range; on the 05B a -0.35 mV/degC pedestal drift is "
            "-1.9 mA/degC of apparent current, so a 50 degC swing is ~95 mA of phantom "
            "current with nothing connected. self-heating: 1.2 mohm at 20 A dissipates 0.48 "
            "W into the same package as the Hall plate, so the die runs hot exactly when the "
            "current is high -- the offset drift is load-correlated, not random. "
            "supply-voltage: the zero-current output is Vcc*0.5 and sensitivity is "
            "ratiometric, so supply noise appears at the output with 0.5 V/V gain. An ADC "
            "referenced to the same 5 V rail cancels the gain term but not the pedestal term "
            "unless it is also measured ratiometrically. emi-rf: 80 kHz -3 dB bandwidth and "
            "3.5 us rise time mean the part passes SMPS switching transients and "
            "dV/dt-coupled noise straight through; the CF filter pin trades this bandwidth "
            "for noise. mechanical-stress: package stress from PCB flex or an over-torqued "
            "screw terminal shifts the Hall offset by the piezo-Hall effect -- an offset "
            "that appears at assembly and never comes back to zero. target-geometry: the "
            "sensitivity depends on how the conductor field couples to the plate; the "
            "internal path is fixed, but any external busbar or wire routed near the package "
            "adds coupling that calibration at build time will silently bake in."
        ),
        "px_range": (
            "+/-5 A (05B), +/-20 A (20A), +/-30 A (30A), bidirectional, AC or DC. 2.4 kVRMS "
            "basic isolation between the current path and the signal pins."
        ),
        "px_resolution": (
            "Noise-limited, not LSB-limited: 21 mV peak-to-peak output noise on the 05B, "
            "which at 185 mV/A is ~113 mA p-p (~19 mA RMS). Total output error +/-1.5% of "
            "full scale at 25 degC. Reading tens of milliamps with a 20 A part is not "
            "possible -- its noise floor alone is ~200 mA."
        ),
        "px_bandwidth": (
            "80 kHz -3 dB (all variants), rise time 3.5 us with the CF pin open. Adding a CF "
            "capacitor lowers both."
        ),
        "px_drift": (
            "Offset drift -0.35 to -0.07 mV/degC; sensitivity drift 0.054 to -0.008 "
            "mV/A/degC. Magnetic hysteresis is stated as 'nearly zero' -- unlike a "
            "ferrite-cored CT it does not remember past overloads. The spinning-current "
            "chopper suppresses the Hall plate's 1/f noise, so the residual drift is thermal "
            "and package-stress driven, not flicker driven."
        ),
        "px_implies": (
            "Because the transducer is a magnetometer, an ACS712 is a magnetically-isolated "
            "true-DC current probe -- the thing a CT clamp physically cannot do -- and the "
            "same property makes it a proximity and vibration sensor for anything ferrous or "
            "magnetised that moves near it. Point it at a rotating magnet and it is a "
            "tachometer. Its DC capability plus 80 kHz bandwidth mean the waveform, not the "
            "RMS, is the product: the shape of a motor's current ramp reveals load torque; "
            "the presence of even harmonics in a mains-side reading is a rectifier "
            "signature; the inrush transient's decay measures the load's L/R. The 2.4 kVRMS "
            "isolation is *basic*, not reinforced -- it means the sensing electronics "
            "survive being referenced to mains, not that the low-voltage side is safe to "
            "touch during a mains measurement; that still requires an enclosure, creepage "
            "and a separate isolated supply. In a multi-sensor build the cross-sensitivity "
            "is the feature: an ACS712 that reads current on an unpowered circuit is telling "
            "you a magnet or an energised coil is nearby, which turns it into a "
            "solenoid-state and door-magnet detector for free."
        ),
        "px_ref": (
            "Fully Integrated, Hall-Effect-Based Linear Current Sensor IC with 2.4 kVRMS "
            "Isolation and a Low-Resistance Current Conductor (ACS712), Allegro "
            "MicroSystems, Rev. 22, 13 February 2024, "
            "https://www.allegromicro.com/-/media/files/datasheets/acs712-datasheet.ashx"
        ),
        "px_ref_kind": "datasheet",
    },

    "S213": {
        "px_status": "filled",
        "px_measurand": (
            "Differential (or single-ended) voltage between two input pins, referred to an "
            "internal bandgap reference -- but what the part physically does is transfer "
            "charge from the source onto a switched sampling capacitor at ~1 MHz, so it "
            "actually responds to the *charge the source can deliver in a sampling "
            "aperture*. A high-impedance source is therefore attenuated, not merely loaded, "
            "and the attenuation depends on the PGA setting."
        ),
        "px_units": "V (LSB from 187.5 uV at +/-6.144 V FSR down to 7.8125 uV at +/-0.256 V FSR)",
        "px_effect": (
            "Delta-sigma (charge-balancing) modulation with a switched-capacitor PGA front "
            "end and a sinc digital filter; single-cycle-settled, so each conversion is an "
            "independent boxcar average"
        ),
        "px_chain": "Electrical",
        "px_cross": [
            "temperature-of-electronics", "reference-drift", "supply-voltage", "ground-noise",
            "emi-rf", "clock-drift", "cable-capacitance", "contact-resistance", "self-heating",
            "aging-drift",
        ],
        "px_cross_note": (
            "reference-drift: gain drift is 5-40 ppm/degC depending on FSR (7 ppm/degC at "
            "+/-0.256 V), and this is the accuracy ceiling for any absolute measurement. "
            "Ratiometric measurements (bridge, potentiometer, thermistor divider from the "
            "same rail) cancel it entirely -- but only if you use the external divider's "
            "supply as the effective reference, which the ADS1115 cannot do because its "
            "reference is internal and fixed. This is the single most misunderstood property "
            "of the part. temperature-of-electronics: offset drift is a remarkably small "
            "0.005 LSB/degC, so offset is essentially free; the error budget is all gain. "
            "cable-capacitance + contact-resistance: the differential input impedance is "
            "only 22 MOhm at +/-6.144 V FSR but falls to 710 kOhm at +/-0.512 V and +/-0.256 "
            "V. A 100 kOhm source into a 710 kOhm input is a 12% gain error that looks "
            "exactly like a calibration problem; a long cable's capacitance plus the source "
            "resistance forms an RC that will not settle inside the sampling aperture, "
            "producing gain error that changes with data rate. clock-drift: the internal ~1 "
            "MHz oscillator has no ppm specification, and it sets both the data rate and the "
            "position of the sinc filter's nulls. There is no mains notch: at 8 SPS the 125 "
            "ms boxcar attenuates 50 Hz by only ~29 dB and 60 Hz by ~28 dB (derived from the "
            "sinc1 response, |sinc(f/8)|), and at 860 SPS mains passes essentially "
            "unattenuated. emi-rf + ground-noise: with no input anti-alias filter, any tone "
            "above half the data rate folds down. A 50 Hz pickup sampled at 8 SPS aliases to "
            "2 Hz and looks like a real slow signal. supply-voltage: 2.0-5.5 V, CMRR ~90-105 "
            "dB, so the part itself rejects rail noise well -- the problem is almost always "
            "the sensor's rail, not the ADC's. self-heating: negligible at 150-200 uA. "
            "aging-drift: bandgap references age at roughly tens of ppm in the first year."
        ),
        "px_range": (
            "Programmable FSR +/-6.144 V, +/-4.096 V, +/-2.048 V, +/-1.024 V, +/-0.512 V, "
            "+/-0.256 V (ADS1114/1115). Note the +/-6.144 V setting does not permit inputs "
            "above the supply rail -- it only rescales the reference. Four single-ended or "
            "two differential channels; 16-bit ADS1115, 12-bit ADS1015."
        ),
        "px_resolution": (
            "16 bits, no missing codes; LSB 7.8125 uV at +/-0.256 V FSR. Datasheet noise is "
            "62.5 uVRMS at +/-2.048 V and 7.81 uVRMS at +/-0.256 V -- i.e. exactly 1 LSB, so "
            "the device is quantisation-limited at every data rate. Peak-to-peak noise grows "
            "with rate (7.81 uVpp at 8 SPS versus 35.83 uVpp at 860 SPS on the +/-0.256 V "
            "range). INL 1 LSB."
        ),
        "px_bandwidth": (
            "Set by the single-cycle-settled sinc1 filter: -3 dB at approximately 0.443 x "
            "data rate (derived), so ~3.5 Hz at 8 SPS and ~380 Hz at 860 SPS, with the first "
            "null at the data rate itself. Because each conversion is independent, there is "
            "no settling penalty when multiplexing channels -- unlike most delta-sigma ADCs."
        ),
        "px_drift": (
            "Offset drift 0.005 LSB/degC (negligible). Gain drift 5-40 ppm/degC. No chopper, "
            "so the modulator's 1/f contribution appears below ~1 Hz; averaging many 8 SPS "
            "conversions gives diminishing returns past a few seconds, and long-term "
            "stability is set by the reference, not the noise."
        ),
        "px_implies": (
            "The ADS1115's real role in a sensor build is as a *shared physical reference "
            "plane*: two sensors read through the same ADC share its gain error, so their "
            "difference is far more accurate than either absolute value -- which is what "
            "makes differential thermocouple, gradiometer and dual-probe soil setups work on "
            "a hobby budget. Its own imperfections are measurements: because there is no "
            "anti-alias filter and no mains notch, the residual 50/60 Hz that appears on a "
            "floating input is a real reading of the electric-field environment, and its "
            "amplitude is a proximity sensor for a human body or a live cable. Because the "
            "internal oscillator is uncalibrated, deliberately sampling a known mains tone "
            "and measuring the alias frequency calibrates the ADC's clock against the grid "
            "-- and, run the other way, calibrating the clock first turns the alias into a "
            "grid-frequency meter accurate to millihertz, which tracks continental "
            "generation/load balance. Because differential input impedance is a strong "
            "function of PGA setting, stepping the PGA on an unchanged source and watching "
            "the reading change measures the *source impedance* -- which converts the ADC "
            "into an electrode-contact-quality, water-conductivity or battery-impedance "
            "meter with no extra hardware. And the 860 SPS continuous mode is fast enough to "
            "catch the burst structure of an SMPS or a heartbeat's PPG waveform, both of "
            "which the part was never marketed for."
        ),
        "px_ref": (
            "ADS111x Ultra-Small, Low-Power, I2C-Compatible, 860-SPS, 16-Bit ADCs With "
            "Internal Reference, Oscillator, and Programmable Comparator, Texas Instruments "
            "SBAS444, original May 2009; noise, impedance and drift figures quoted from Rev. "
            "D (January 2018), latest revision E (December 2024), "
            "https://www.ti.com/lit/ds/symlink/ads1115.pdf"
        ),
        "px_ref_kind": "datasheet",
    },

}


# ---------------------------------------------------------------- fields

# The px_* fields, in schema order. Derived from schema.FIELDS so this module
# cannot drift out of step with the contract.
PX_FIELDS = [f for f in schema.FIELDS if f.startswith("px_")]

# What a record must carry, on top of a citation, to earn "filled".
PX_SUBSTANCE = ["px_measurand", "px_units", "px_effect", "px_range",
                "px_resolution", "px_bandwidth", "px_drift", "px_implies"]

# The default every sensor without an entry loads with.
UNFILLED = {"px_status": "unfilled"}


def overlay(pid):
    """The physics-layer overlay for one record id.

    Returns a fresh dict every call, so a caller mutating a loaded record can
    never write back into `PX`. Sensors with no authored physics load as
    unfilled — the "rest is marked unfilled" requirement is satisfied by
    construction, not by 405 hand-written stubs.
    """
    entry = PX.get(pid)
    if not entry:
        return dict(UNFILLED)
    out = dict(UNFILLED)
    out.update(entry)
    out.setdefault("px_status", "partial")
    return out


def missing_fields(entry):
    """Which substance fields (and citation) an entry lacks. [] means complete."""
    gaps = [f for f in PX_SUBSTANCE if not str(entry.get(f) or "").strip()]
    if not str(entry.get("px_ref") or "").strip():
        gaps.append("px_ref")
    if not str(entry.get("px_ref_kind") or "").strip():
        gaps.append("px_ref_kind")
    return gaps


def coverage(records):
    """Counts over loaded sensor records: by status, and filled by modality.

    Computed, never authored. `records` is the loaded catalog; anything whose
    `catalog` is not "sensor" is ignored, because the physics layer is only
    applied to sensors.
    """
    sensors = [r for r in records if r.get("catalog", "sensor") == "sensor"]
    by_status = {s: 0 for s in schema.PX_STATUS}
    by_modality = {}
    filled_by_modality = {}
    for r in sensors:
        st = r.get("px_status") or "unfilled"
        by_status[st] = by_status.get(st, 0) + 1
        mod = r.get("modality") or "—"
        by_modality[mod] = by_modality.get(mod, 0) + 1
        if st == "filled":
            filled_by_modality[mod] = filled_by_modality.get(mod, 0) + 1
    return {
        "total": len(sensors),
        "by_status": by_status,
        "by_modality": by_modality,
        "filled_by_modality": {m: filled_by_modality.get(m, 0) for m in by_modality},
    }
