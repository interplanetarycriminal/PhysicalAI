"""Combinatorics — ranking SENSOR COMBINATIONS, not sensors.

Everything upstream of this file scores parts one at a time. `outcome_solver`
picks a KIT, but it picks it greedily to cover a target set: it never asks
"which two of these 405 parts are interesting *together*, and why?". 81,810
pairs exist. This file scores every one of them, and shows its working.

Five things are computed, each returned with the evidence that produced it so a
number can always be argued with:

  1. INTERFERENTS — `fools` is free prose (median 898 characters of it), which
     means the thing every sensor is most honest about is the thing nothing can
     query. `INTERFERENTS` below is a DERIVED lexicon: ~39 concepts, each with
     regex patterns and the PHENOMENON keys that observe it. It is code, not
     data — the repo's first rule is that derived values are computed, never
     authored, and an interferent list authored onto 405 records would drift out
     of sync with the prose it came from the first time anyone edited a `fools`
     string. Every extraction returns the matched snippet, so every downstream
     claim quotes its source.

  2. TIME CONSTANTS — parsed from the free-text `rate` and `warmup`. Two sensors
     that respond on the same timescale can be subtracted; two that differ by
     three decades can discipline each other. Returns None, loudly, when nothing
     parses. It never guesses.

  3. ESP32 SINGLE-BOARD FIT — a DOCUMENTED HEURISTIC, and it must be read as
     one. The schema has no field for "how many I2C buses", "how many ADC1
     channels" or "which peripheral instance"; `iface` is an enumlist, `pins` is
     one integer, `i2c_addr` is prose with hex literals in it. So this models
     bus sharing from `iface`, the pin budget from `pins`, and address conflicts
     by parsing hex out of `i2c_addr`. It is good enough to say "these two
     obviously collide at 0x76" and NOT good enough to say "this will boot".
     Where it repeats a hardware fact (ADC2 dying under Wi-Fi) it quotes the
     boards' own `fools` text rather than asserting it here.

  4. THE SCORE — six components, each normalised and weighted by the visible
     `WEIGHTS` dict, never by a magic number buried in a function.

  5. ENUMERATION — all C(405,2) pairs exhaustively; triples by candidate
     generation, because C(405,3) = 11,042,570 is not tractable at ~0.5 ms a
     combination. `rank_triples` is explicitly a heuristic search and says so.

Pure stdlib. Imports the repo's own primitives (`fusion.covers`,
`outcome_solver.closure`) rather than reimplementing them, so this file cannot
disagree with the workbook about what a sensor covers.

A NOTE ON ONE DEVIATION FROM THE OBVIOUS FORMULA. `closure()` returns
`fired_keys`, which are *edge* keys ("condensation-watch"), while EMERGENT is
keyed by what an edge *provides* ("condensation-risk"). Synergy is therefore
computed over the PROVIDED keys — `covers(r) | {e["provides"] for e in fired}` —
because that is the set that can be split into emergent outcomes and new routes.
The fired edge keys are still reported separately, as `edges_fired_jointly`.
"""
import math
import re
from collections import Counter
from itertools import combinations

import fusion
import outcome_solver as osv
import vocab


# ===========================================================================
# 1 · INTERFERENTS — a derived lexicon over the `fools` prose
# ===========================================================================
# Each entry:
#   label       — human phrasing for reports
#   patterns    — case-insensitive regexes; a record matches the concept if ANY
#                 pattern hits its `fools` (plus `spec`, where present)
#   measured_by — PHENOMENON keys that OBSERVE this interferent, i.e. a second
#                 part carrying one of these can tell you how much to correct
#                 the first. [] means "nothing in the vocabulary measures this",
#                 which is a real and common answer — dust, ageing and creep are
#                 not compensable by another sensor, only by maintenance.
# Every measured_by key is checked against vocab.PHENOMENON at import time.
#
# Some patterns use Python's local flag syntax `(?-i:...)` to force a
# case-SENSITIVE sub-match. That is not decoration: `\bCO\b` under /i matches
# "co-located", which appears in six records and means the opposite of a carbon
# monoxide cross-sensitivity.

INTERFERENTS = {

    "self-heating": dict(
        label="Self-heating of the sensor or its own board",
        patterns=[r"self[- ]heat", r"heats? itself", r"its own heat",
                  r"own die temperature", r"warm(?:s|ed|ing) (?:itself|the sensor|its own)",
                  r"heat from the (?:board|regulator|LED|MCU|ESP32|display)",
                  r"internal heater", r"the heater (?:warms|raises|adds)",
                  r"co-located with an ESP32"],
        measured_by=["temperature-contact"]),

    "temperature-drift": dict(
        label="Ambient temperature drift / temperature coefficient",
        patterns=[r"tempco", r"temperature coefficient", r"temperature[- ]depend",
                  r"drifts? with temperature", r"\bwith temperature\b", r"temperature drift",
                  r"thermal drift", r"temperature compensat", r"per (?:°|deg)\s?C\b",
                  r"changes? with (?:the )?temperature", r"temperature swing",
                  r"temperature is the largest"],
        measured_by=["temperature-contact", "temperature-remote"]),

    "humidity": dict(
        label="Ambient humidity and condensation",
        patterns=[r"\bhumid", r"relative humidity", r"\bRH\b", r"\bcondens",
                  r"\bdew\b", r"moisture in the air", r"damp air"],
        measured_by=["humidity-relative", "dew-point"]),

    "sunlight-ir": dict(
        label="Sunlight and ambient infrared",
        patterns=[r"\bsunlight\b", r"\bsunlit\b", r"direct sun\b", r"\bin (?:the )?sun\b",
                  r"solar gain", r"infrared from", r"\bIR from\b", r"\bhalogen\b",
                  r"\bincandescent\b", r"\bsun\b", r"solar radiation", r"radiant heat",
                  r"sun cross(?:es|ing)"],
        measured_by=["solar-irradiance", "irradiance", "ir-near", "temperature-remote"]),

    "ambient-light": dict(
        label="Ambient or stray visible light",
        patterns=[r"ambient light", r"stray light", r"room light", r"light leak",
                  r"\bdaylight\b", r"bright light", r"under (?:office |fluorescent )?lighting"],
        measured_by=["illuminance"]),

    "ambient-rf": dict(
        label="Ambient RF — Wi-Fi, BLE and radio traffic",
        patterns=[r"\bWi-?Fi\b", r"\bBluetooth\b", r"\bBLE\b", r"RF interference",
                  r"radio interference", r"\b2\.4\s?GHz\b", r"other radios",
                  r"radio traffic", r"antenna coupling", r"\bRF noise\b"],
        measured_by=["rf-power", "rf-channel-state"]),

    "mains-hum": dict(
        label="Mains hum, 50/60 Hz pickup and supply ripple",
        patterns=[r"mains hum", r"\b50\s?Hz\b", r"\b60\s?Hz\b",
                  r"mains (?:pickup|noise|frequency)", r"\bhum\b", r"\bripple\b",
                  r"line frequency"],
        measured_by=["electric-field", "voltage", "current-ac"]),

    "switching-emi": dict(
        label="EMI from switching supplies, motors and PWM",
        patterns=[r"switching (?:supply|supplies|regulator|noise|converter)", r"\bSMPS\b",
                  r"buck converter", r"PWM (?:noise|LED)", r"switch[- ]mode", r"\bEMI\b",
                  r"electromagnetic interference", r"motor noise", r"brush noise"],
        measured_by=["electric-field", "magnetic-field"]),

    "magnetic-hard-iron": dict(
        label="Hard/soft iron, magnets, motors and nearby steel",
        patterns=[r"hard[- ]iron", r"soft[- ]iron", r"\bmagnets?\b", r"\bferrous\b",
                  r"nearby (?:steel|metal|iron)", r"steel (?:beam|frame|desk|rebar)",
                  r"speaker magnet", r"magnetic field of", r"stray (?:magnetic )?field",
                  r"magnetic memory"],
        measured_by=["magnetic-field"]),

    "vibration-shock": dict(
        label="Vibration and mechanical shock",
        patterns=[r"\bvibrat", r"mechanical shock", r"\bknock", r"\bbang", r"\bthump",
                  r"\bfootstep", r"\bslam", r"\bjolt", r"\bshock\b", r"being dropped"],
        measured_by=["vibration", "acceleration", "shock-impact", "ground-motion"]),

    "air-currents": dict(
        label="Air currents, draughts and forced airflow",
        patterns=[r"\bdraught", r"\bdraft\b", r"air current", r"\bbreeze\b",
                  r"\b(?:ceiling|desk|extractor|pedestal|room|cooling) fan\b",
                  r"\bfan (?:blade|blowing|draught)", r"forced air", r"\bairflow\b",
                  r"\bmoving air\b", r"HVAC vent"],
        measured_by=["air-velocity", "wind-speed"]),

    "dust-fouling": dict(
        label="Dust, dirt, fouling and soiling",
        patterns=[r"\bdust", r"\bdirt", r"\bfoul", r"\bsoiling\b", r"\bgrime\b",
                  r"\bcobweb", r"\bspider", r"\bclog", r"\blint\b", r"\bgrease\b",
                  r"dirty (?:lens|window|optic)"],
        measured_by=[]),

    "emissivity-albedo": dict(
        label="Surface emissivity, colour and albedo",
        patterns=[r"\bemissivit", r"\bshiny\b", r"\bpolished\b", r"\breflective\b",
                  r"\bmatt\b", r"\balbedo\b", r"bare metal",
                  r"colour of the (?:target|surface|object)",
                  r"dark (?:surface|object|target)", r"\bwhite surface"],
        measured_by=["colour", "spectral-power"]),

    "ethanol-voc": dict(
        label="Ethanol, solvents and general VOCs",
        patterns=[r"\bethanol\b", r"\balcohol\b", r"\bVOC", r"\bsolvent", r"\bperfume",
                  r"\baerosol", r"cleaning (?:spray|product|fluid)",
                  r"hand (?:gel|sanitiser|sanitizer)", r"\bacetone\b", r"\bisopropyl",
                  r"\bmarker pen\b"],
        measured_by=["voc-index", "gas-concentration"]),

    "hydrogen": dict(
        label="Hydrogen cross-response",
        patterns=[r"\bhydrogen\b", r"(?-i:\bH2\b)", r"\bH₂\b"],
        measured_by=["gas-concentration"]),

    "gas-cross-sensitivity": dict(
        label="Cross-sensitivity to other gases",
        patterns=[r"cross[- ]sensitiv", r"cross[- ]respon", r"\bmethane\b",
                  r"carbon monoxide", r"(?-i:\bCO\b)(?![ -]?2)", r"(?-i:\bNO2\b)",
                  r"\bozone\b", r"(?-i:\bH2S\b)", r"\bammonia\b", r"interfering gas",
                  r"other gases", r"\bLPG\b", r"\bpropane\b", r"\bchlorine\b"],
        measured_by=["gas-concentration"]),

    "barometric-pressure": dict(
        label="Barometric pressure and altitude change",
        patterns=[r"\bbarometric\b", r"weather (?:system|front|pressure)", r"\bhPa\b",
                  r"atmospheric pressure", r"pressure changes?", r"\baltitude\b",
                  r"sea[- ]level pressure"],
        measured_by=["pressure-absolute", "altitude-barometric"]),

    "supply-voltage": dict(
        label="Supply-voltage sag, rail noise and regulator quality",
        patterns=[r"supply voltage", r"(?:supply|power|same|its own|shared|5V|3\.3V|1\.8V) rail\b",
                  r"\bregulator\b", r"ratiometric", r"\bbrown[- ]?out", r"\bVCC\b", r"\bVDD\b",
                  r"battery voltage", r"\bUSB power\b", r"noisy supply", r"decoupl"],
        measured_by=["voltage"]),

    "ageing-drift": dict(
        label="Ageing, baseline drift and burn-in",
        patterns=[r"\bageing\b", r"\baging\b", r"baseline (?:drift|creep|wander|shift)",
                  r"\bburn[- ]in\b", r"\bdrifts? (?:over|up|down|away|permanently|seconds|minutes)",
                  r"degrades? over", r"long[- ]term drift", r"\bzero drift\b",
                  r"\brecalibrat", r"loses? (?:sensitivity|calibration)",
                  r"\bdrift[- ]compensat", r"the baseline (?:creeps|walks|moves|drifts)"],
        measured_by=[]),

    "warmup-settling": dict(
        label="Warm-up and settling before the reading is valid",
        patterns=[r"warm[- ]?up", r"\bsettl(?:e|es|ing)\b", r"stabilis|stabiliz",
                  r"first (?:few )?(?:seconds|minutes|hours)", r"after power[- ]up",
                  r"cold start", r"time to (?:a )?(?:valid|stable)"],
        measured_by=[]),

    "subject-stillness": dict(
        label="A still subject — motionless people, static scenes",
        patterns=[r"\bmotionless\b", r"\bstationary\b", r"stops? moving", r"does not move",
                  r"\b(?:sitting|sat|lying|lies|standing|holds?|stays?|remains?|perfectly|completely|absolutely)\s+(?:very\s+)?still\b",
                  r"\bstill (?:person|subject|occupant|human|body|target|sleeper)\b",
                  r"\bno (?:movement|motion)\b", r"\bstillness\b"],
        measured_by=["occupancy-signal"]),

    "subject-motion": dict(
        label="Motion of the subject — motion artefacts",
        patterns=[r"motion arte?[fi]act", r"movement arte?[fi]act",
                  r"if (?:the )?(?:subject|wearer|patient|user|they) moves?",
                  r"the wearer moves", r"\bmoves during\b",
                  r"\bhand (?:moves|movement|tremor)\b",
                  r"movement of the (?:subject|wearer|hand|wrist|arm)",
                  r"\bmoving (?:subject|target|person|wrist)\b", r"\bwhile (?:walking|moving)\b"],
        measured_by=["acceleration", "vibration"]),

    "glass-opacity": dict(
        label="Glass and material opacity in the wrong band",
        patterns=[r"\bglass\b(?!\s*(?:bead|electrode|fibre|fiber))", r"\bwindow pane\b",
                  r"\bpolycarbonate\b", r"\bacrylic\b", r"\bperspex\b",
                  r"\bplastic (?:window|cover|lens|enclosure)\b", r"opaque to",
                  r"does not (?:pass|see) through", r"blocks? (?:IR|infrared|the beam|the band)"],
        measured_by=[]),

    "multipath": dict(
        label="Multipath, reflections and ghost returns",
        patterns=[r"\bmultipath\b", r"\breflect(?:ion|ions|ed|s|ing)\b",
                  r"\breflective (?:surface|tape|target|object|wrap)",
                  r"ghost (?:echo|target|return)", r"\bbounces? off\b", r"corner reflect",
                  r"\bspecular\b", r"secondary echo", r"\bretroreflect"],
        measured_by=[]),

    "reverberation": dict(
        label="Acoustic reverberation and background noise",
        patterns=[r"\breverber", r"\bechoe?s?\b", r"room acoustics", r"background noise",
                  r"ambient noise", r"\bnoisy room\b", r"acoustic (?:noise|clutter)"],
        measured_by=["sound-pressure"]),

    "crosstalk": dict(
        label="Crosstalk between units of the same kind",
        patterns=[r"cross[- ]?talk", r"interfere with (?:each other|one another)",
                  r"two of these", r"\bhear each other\b", r"see each other",
                  r"multiple units", r"adjacent (?:units|sensors|modules)",
                  r"two .{0,20}probes? in the same"],
        measured_by=[]),

    "target-geometry": dict(
        label="Target distance, angle, size and field of view",
        patterns=[r"field of view", r"\bFoV\b", r"angle of incidence", r"\boff[- ]axis\b",
                  r"\bperpendicular\b", r"spot size", r"distance[- ]to[- ]spot", r"\baiming\b",
                  r"\bmisaligned?\b", r"\balignment\b", r"\bat an angle\b",
                  r"target (?:size|distance|geometry)", r"acceptance cone",
                  r"\bsteeply angled\b"],
        measured_by=["distance-point", "distance-field"]),

    "water-immersion": dict(
        label="Water immersion, splash and wetting",
        patterns=[r"\bimmers", r"\bsubmerg", r"\bsplash", r"water ingress", r"\bgets? wet\b",
                  r"\bwater wicks?\b", r"\bflood", r"standing water", r"\brain(?:water)? on\b",
                  r"\bwetting\b", r"\bwater film\b", r"\bwater droplets?\b"],
        measured_by=["surface-wetness", "liquid-level", "moisture-material"]),

    "salinity-ionic": dict(
        label="Salinity, ionic strength and dissolved solids",
        patterns=[r"\bsalinit", r"\bionic\b", r"\bsalt", r"dissolved solids", r"\bTDS\b",
                  r"\bconductivity of\b", r"(?-i:\bEC\b)", r"\bfertilis|fertiliz",
                  r"\bdS/m\b"],
        measured_by=["conductivity-liquid"]),

    "ph": dict(
        label="pH of the medium",
        patterns=[r"(?-i:\bpH\b)", r"\bacidic\b", r"\balkaline\b", r"\bacidity\b"],
        measured_by=["ph"]),

    "optical-transparency": dict(
        label="Optical transparency or blackness of the target",
        patterns=[r"\btransparent\b", r"\bclear (?:plastic|liquid|water|glass|surface)\b",
                  r"\bmatte? black\b", r"\bblack (?:surface|object|target|fabric|foam)\b",
                  r"\babsorbs? (?:the )?(?:light|IR|infrared|laser|beam|pulse)",
                  r"\bglossy\b", r"\bwater surface\b", r"\bsoft or steeply\b"],
        measured_by=[]),

    "clock-drift": dict(
        label="Clock and timing drift",
        patterns=[r"\bclock drift\b", r"timing drift", r"\bRTC\b", r"\boscillator",
                  r"\bjitter\b", r"\btime base\b", r"drifts? (?:seconds|minutes) per",
                  r"crystal (?:drift|tolerance|ageing|ppm)", r"\bXTAL\b",
                  r"\bsample[- ]clock\b"],
        measured_by=["radio-time", "position-global"]),

    "orientation-tilt": dict(
        label="Mounting orientation and tilt",
        patterns=[r"\btilt", r"\bmounting (?:angle|orientation)\b", r"\borientation\b",
                  r"\bupside[- ]down\b", r"\bgravity vector\b", r"\bnot level\b",
                  r"\bmount(?:ed)? (?:vertical|horizontal|flat)", r"\blevelling\b",
                  r"\bspirit level\b"],
        measured_by=["tilt", "orientation-fused", "acceleration"]),

    "part-tolerance": dict(
        label="Part-to-part tolerance and per-unit calibration",
        patterns=[r"part[- ]to[- ]part", r"unit[- ]to[- ]unit", r"\btolerance\b",
                  r"each (?:unit|part|sensor|module) (?:differs|is different|needs)",
                  r"per[- ]unit calibration", r"\bcounterfeit", r"\brelabelled\b",
                  r"\bclones?\b", r"varies? between (?:units|parts|batches)",
                  r"\bbatch to batch\b", r"\bsample to sample\b"],
        measured_by=[]),

    "hysteresis-creep": dict(
        label="Hysteresis, creep and memory effect",
        patterns=[r"\bhysteres", r"\bcreep\b", r"memory effect", r"does not return to zero",
                  r"zero (?:shift|offset) after", r"\bstiction\b", r"\brelaxation\b"],
        measured_by=[]),

    "saturation": dict(
        label="Saturation, over-range and clipping",
        patterns=[r"\bsaturat", r"\bover[- ]range\b", r"\bclipping\b", r"hard[- ]?clips?\b",
                  r"\bclips? (?:at|above|below)\b", r"\bfull[- ]scale\b", r"\bout of range\b",
                  r"\bpegs?\b", r"\bpinned?\b", r"\boverload", r"\bblinded\b",
                  r"\bflat rail\b", r"\beither rail\b"],
        measured_by=[]),

    "light-colour-temperature": dict(
        label="Colour temperature / spectrum of the illuminant",
        patterns=[r"colou?r temperature", r"\billuminant\b",
                  r"spectrum of the (?:light|lamp|LED|source)", r"\bLED spectrum\b",
                  r"\bIR content\b", r"\bfluorescent\b", r"\bwhite LED\b",
                  r"light source'?s spectrum", r"\bwarm white\b", r"\blow-e\b"],
        measured_by=["spectral-power", "colour"]),

    "wind-rain": dict(
        label="Wind, rain and outdoor weather exposure",
        patterns=[r"\bwind\b", r"\brain\b", r"\brainfall\b", r"\bprecipitation\b",
                  r"\bstorm\b", r"\bsnow\b", r"\bgust", r"\bweather[- ]exposed\b",
                  r"\bhail\b"],
        measured_by=["wind-speed", "rainfall", "surface-wetness"]),

    "biofouling": dict(
        label="Biofouling — biofilm, algae and slime",
        patterns=[r"\bbiofoul", r"\bbiofilm\b", r"\balgae\b", r"\bslime\b",
                  r"\bbacterial growth\b", r"\bmould\b", r"\bmold\b", r"\bmoss\b"],
        measured_by=["turbidity"]),
}


def _validate_interferents():
    """Import-time contract: every measured_by key must be a real PHENOMENON.
    A typo here would silently invent compensation channels that do not exist,
    which is the single most damaging failure this module could have."""
    bad = [(k, p) for k, v in INTERFERENTS.items()
           for p in v["measured_by"] if p not in vocab.PHENOMENON]
    if bad:
        raise ValueError(
            "combinatorics.INTERFERENTS: measured_by keys not in vocab.PHENOMENON: "
            + ", ".join(f"{k} -> {p!r}" for k, p in bad))
    for k, v in INTERFERENTS.items():
        for p in v["patterns"]:
            try:
                re.compile(p)
            except re.error as exc:                       # pragma: no cover
                raise ValueError(f"INTERFERENTS[{k!r}] bad pattern {p!r}: {exc}") from exc


_validate_interferents()

_COMPILED = {k: [re.compile(p, re.I) for p in v["patterns"]]
             for k, v in INTERFERENTS.items()}

SNIPPET_CONTEXT = 90       # characters either side of the match, per the audit rule


def interferent_text(record):
    """The prose an interferent may be extracted from: `fools` always, `spec`
    where it exists (58% of sensors). Nothing else — `how` and `use` are
    marketing-adjacent, `fools` is the field that exists to be pessimistic."""
    parts = [record.get("fools") or ""]
    if record.get("spec"):
        parts.append(record["spec"])
    return "  ".join(p for p in parts if p)


def extract_interferents(record):
    """-> {interferent_key: matched snippet}. The snippet is +/-90 characters of
    context around the first match, so every claim downstream can quote the
    sentence it came from instead of asserting it."""
    text = interferent_text(record)
    if not text:
        return {}
    out = {}
    for key, pats in _COMPILED.items():
        for p in pats:
            m = p.search(text)
            if m:
                a = max(0, m.start() - SNIPPET_CONTEXT)
                b = min(len(text), m.end() + SNIPPET_CONTEXT)
                snip = " ".join(text[a:b].split())
                out[key] = ("…" if a else "") + snip + ("…" if b < len(text) else "")
                break
    return out


# ===========================================================================
# 2 · TIME CONSTANTS — parsed out of the free-text `rate` and `warmup`
# ===========================================================================
# `rate` is populated on 396/405 sensors and `warmup` on 329, both as prose
# written for a human ("8.2ms conversion", "~4s to reach 63%", "several
# minutes", "1 Hz - 5.376 kHz ODR"). A time constant is the single number that
# decides whether two sensors can be SUBTRACTED (they must respond alike) or
# whether one can DISCIPLINE the other (they must differ). So it is worth
# parsing, and worth refusing to invent: ~a quarter of the catalog yields
# nothing, and estimate_tau returns None for every one of them.
#
# Precedence, and why:
#   1. an explicit response/settling time in `warmup`  — a 63% or t90 figure is
#      literally a time constant, and it is the physical one
#   2. an explicit response time inside `rate`         — same thing, other field
#   3. a conversion / integration time in `rate`       — the instrument's own
#      per-reading latency: an upper bound on how fast it can possibly be
#   4. a frequency in `rate`                           — 1/f_max. This only
#      BOUNDS tau FROM BELOW (a 1.6 kHz ODR accelerometer is not a 0.6 ms
#      instrument, it is an instrument you may sample that fast), hence
#      confidence "low"
#   5. a bare duration in `rate`, then in `warmup`
# Nothing else. No defaults, no category priors, no "thermal parts are slow".

_NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"
_UNITS = [
    (r"milliseconds?", 1e-3), (r"microseconds?", 1e-6), (r"minutes?", 60.0),
    (r"seconds?", 1.0), (r"hours?", 3600.0), (r"days?", 86400.0),
    (r"weeks?", 604800.0), (r"mins?", 60.0), (r"hrs?", 3600.0), (r"secs?", 1.0),
    (r"ms", 1e-3), (r"µs", 1e-6), (r"us", 1e-6), (r"s", 1.0), (r"h", 3600.0),
]
_UNIT_ALT = "|".join(u for u, _s in _UNITS)
_UNIT_SCALE = [(re.compile(rf"^(?:{u})$", re.I), s) for u, s in _UNITS]

_RANGE_RE = re.compile(
    rf"({_NUM})\s*(?:{_UNIT_ALT})?\s*(?:-|–|—|\s+to\s+)\s*[~≈<]?\s*({_NUM})\s*"
    rf"({_UNIT_ALT})(?![A-Za-z])", re.I)
_SINGLE_RE = re.compile(
    rf"(?:[<≤~]|under\s+|within\s+|about\s+|approx\.?\s*|roughly\s+|up\s+to\s+|every\s+)?"
    rf"({_NUM})\s*({_UNIT_ALT})(?![A-Za-z])", re.I)
_VAGUE_RE = re.compile(
    r"(several|a few|a couple of|tens of|dozens of|hundreds of)\s+"
    r"(milliseconds?|seconds?|minutes?|hours?|days?)", re.I)
_VAGUE_MULT = {"several": 3, "a few": 3, "a couple of": 2, "tens of": 30,
               "dozens of": 24, "hundreds of": 300}
_SUB_RE = re.compile(r"sub-?(millisecond|second|minute)", re.I)
_SUB_VAL = {"millisecond": 5e-4, "second": 0.5, "minute": 30.0}

# a duration is a RESPONSE time only if one of these sits beside it
_RESPONSE = re.compile(
    r"respon|t\s?90|t\s?63|63\s?%|90\s?%|time constant|settl|to reach|recover|"
    r"rise\b|decay|converge|equilibr|relax|thermal (?:mass|time)|"
    r"to (?:a )?(?:usable|valid|stable|plausible|specified)|to valid|"
    r"to first (?:output|reading|value|frame)|damped|valid data", re.I)
# ...and NOT a burn-in, which is a different physical thing entirely
_BURNIN = re.compile(
    r"burn[- ]in|soak|overnight|shipping|before first use|per season|"
    r"one full (?:wet|dry|cycle)|survey|re-?equilibrat|baseline stops|"
    r"fully settle|to (?:a )?settled baseline|build a usable baseline|"
    r"model to settle|continuous operation|conditioning|preheat|"
    r"powered before|learning cycle|fresh out of the box|before the first|"
    r"baseline (?:algorithm|to converge)|install|stored unpowered|"
    r"before (?:burying|trusting|judging)|first (?:used|installed)", re.I)
_CONVERSION = re.compile(
    r"conversion|integration|per (?:reading|sample|measurement)|"
    r"one conversion|acquisition", re.I)

_FREQ_RE = re.compile(
    rf"({_NUM})\s*(k|M)?\s*(Hz|SPS|sps|fps|Sa/s)(?![A-Za-z])", re.I)
_PER_SEC_RE = re.compile(
    rf"({_NUM})\s*(?:readings?|samples?|ranges?|points?|reports?|frames?|"
    rf"measurements?|conversions?|updates?)\s*(?:/|\s+per\s+)\s*s(?:ec(?:ond)?)?"
    r"(?![A-Za-z])", re.I)
_EVERY_RE = re.compile(
    rf"(?:1|one|a)\s*(?:reading|sample|report|measurement|update)\s*"
    rf"(?:/|\s+per\s+|\s+every\s+)\s*({_NUM})\s*({_UNIT_ALT})(?![A-Za-z])", re.I)
_CONTEXT = 55          # how far a response marker may sit from its duration
_VETO_CONTEXT = 30     # deliberately tighter: a burn-in phrase one clause away
                       # must not veto the response time in the clause before it


def _scale(unit):
    for rx, s in _UNIT_SCALE:
        if rx.match(unit):
            return s
    return None                                            # pragma: no cover


def _f(txt):
    return float(txt.replace(",", ""))


def _durations(text):
    """Every duration in `text`, as (seconds, span, literal). Ranges take the
    UPPER bound — the spec's rule, and the conservative one: a part quoted at
    '30-60s' is a 60 s part when you are deciding whether it can be subtracted
    from something else."""
    out, taken = [], []

    def overlaps(a, b):
        return any(not (b <= s or a >= e) for s, e in taken)

    for m in _RANGE_RE.finditer(text):
        sc = _scale(m.group(3))
        if sc:
            out.append((_f(m.group(2)) * sc, m.span(), m.group(0)))
            taken.append(m.span())
    for m in _SINGLE_RE.finditer(text):
        if overlaps(*m.span()):
            continue
        sc = _scale(m.group(2))
        if sc:
            out.append((_f(m.group(1)) * sc, m.span(), m.group(0)))
            taken.append(m.span())
    for m in _VAGUE_RE.finditer(text):
        if overlaps(*m.span()):
            continue
        sc = _scale(m.group(2))
        if sc:
            out.append((_VAGUE_MULT[m.group(1).lower()] * sc, m.span(), m.group(0)))
    for m in _SUB_RE.finditer(text):
        if not overlaps(*m.span()):
            out.append((_SUB_VAL[m.group(1).lower()], m.span(), m.group(0)))
    out.sort(key=lambda t: t[1][0])
    return out


def _window(text, span, ctx=_CONTEXT):
    return text[max(0, span[0] - ctx): span[1] + ctx]


def _first_marked(text, marker, veto=_BURNIN):
    """The duration in `text` sitting CLOSEST to a `marker` word, skipping any
    whose neighbourhood also matches `veto`.

    Nearest, not first, because these strings routinely carry two durations of
    different kinds in one clause — "1ms per conversion; ~1s RH response
    through the die's port" — and the response time is the one the word
    "response" is next to. Ties go to the earlier duration."""
    marks = [m.span() for m in marker.finditer(text)]
    if not marks:
        return None
    best = None
    for val, span, lit in _durations(text):
        if veto and veto.search(_window(text, span, _VETO_CONTEXT)):
            continue
        win = _window(text, span)
        d = min(max(ms - span[1], span[0] - me, 0) for ms, me in marks)
        if d > _CONTEXT:
            continue
        if best is None or d < best[0]:
            best = (d, val, lit, " ".join(win.split()))
    if best is None:
        return None
    return best[1], best[2], best[3]


def _max_frequency(text):
    """The highest frequency stated, as Hz. Highest, because 1/f_max is the
    LOWER bound on tau that a sample rate can honestly support."""
    best = None
    for m in _FREQ_RE.finditer(text):
        mult = {"k": 1e3, "m": 1e6}.get((m.group(2) or "").lower(), 1.0)
        f = _f(m.group(1)) * mult
        if f > 0:
            best = f if best is None else max(best, f)
    for m in _PER_SEC_RE.finditer(text):
        f = _f(m.group(1))
        if f > 0:
            best = f if best is None else max(best, f)
    return best


def estimate_tau(record):
    """-> (tau_seconds | None, basis, confidence in high|medium|low|none).

    `basis` names the field, the literal that matched and the rule that fired,
    so any tau in an export can be traced back to the sentence it came from."""
    warm = record.get("warmup") or ""
    rate = record.get("rate") or ""

    for field, txt in (("warmup", warm), ("rate", rate)):
        hit = _first_marked(txt, _RESPONSE)
        if hit:
            val, lit, win = hit
            return val, f"{field}:response-time · matched {lit!r} in “{win}”", "high"

    hit = _first_marked(rate, _CONVERSION, veto=None)
    if hit:
        val, lit, win = hit
        return val, f"rate:conversion-time · matched {lit!r} in “{win}”", "medium"

    m = _EVERY_RE.search(rate)
    if m:
        sc = _scale(m.group(2))
        if sc:
            return (_f(m.group(1)) * sc,
                    f"rate:update-period · matched {m.group(0)!r}", "medium")

    f = _max_frequency(rate)
    if f:
        return (1.0 / f,
                f"rate:max-frequency {f:g} Hz · 1/f is a LOWER bound on tau, "
                f"not a measured response", "low")

    ds = _durations(rate)
    if ds:
        return ds[0][0], f"rate:bare-duration · matched {ds[0][2]!r}", "medium"

    for val, span, lit in _durations(warm):
        win = _window(warm, span)
        if not _BURNIN.search(win):
            return val, f"warmup:bare-duration · matched {lit!r} in “{' '.join(win.split())}”", "low"

    return None, "no parsable response time in `rate` or `warmup`", "none"


def tau_decades(a, b):
    """|log10(tau_a) - log10(tau_b)|, or None if either is unknown. Decades,
    not a ratio, because the interesting question is order of magnitude: is one
    of these a thousand times slower than the other, or the same speed?"""
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return abs(math.log10(a) - math.log10(b))


# ===========================================================================
# 3 · ESP32 SINGLE-BOARD FIT — a heuristic over iface / pins / i2c_addr
# ===========================================================================
# Read the module docstring first. Restating the important half: the schema has
# no structured field for bus instances or ADC channels, so nothing below is a
# guarantee. What it CAN do reliably is catch the two failures that actually
# stop a two-sensor build — an I2C address collision and a UART shortage — and
# compute an honest pin budget to compare against each board's `pins`.
#
# Where this file repeats a hardware fact about the ESP32 itself, it quotes the
# boards' own `fools` text (see ADC_SOURCE below) rather than asserting it, so
# the claim has a citation inside this repository.

# Which bus a part will actually be wired to, best case, when it offers several.
# I2C first because it is the only one that costs nothing to add a second part
# to; the industrial buses last because they are the ones needing a transceiver.
IFACE_PREFERENCE = ["I2C", "1-Wire", "I2S", "SPI", "UART", "Pulse", "PWM",
                    "Digital", "Analog", "Builtin", "Radio", "Camera",
                    "USB", "RS-485", "CAN", "4-20mA"]

# Interfaces that need a part the ESP32 does not contain. `Radio` and `Builtin`
# are deliberately NOT here: in this schema `Radio` means "sensing performed by
# the radio itself (CSI, RSSI, backscatter)" — the ESP32's own radio IS the
# sensor (S228 Wi-Fi CSI, S275 BLE beacon), so it needs no transceiver at all.
GLUE_NEEDED = {
    "RS-485": "an RS-485 transceiver (MAX485/SP3485 class) and a Modbus RTU master",
    "CAN":    "a CAN transceiver (SN65HVD230 class) on the TWAI peripheral",
    "4-20mA": "a current-loop receiver — a precision shunt into an external ADC, "
              "or an RCV420-class loop receiver, plus a 24V loop supply",
    "USB":    "a USB host stack; only the S2/S3/P4 expose USB-OTG at all, and "
              "most USB-only sensors expect a full PC-class host",
}

UART_INSTANCES = 3          # the ESP32 family exposes three UART controllers
I2C_PINS, ONEWIRE_PINS, SPI_BUS_PINS, SPI_CS_PINS, UART_PINS = 2, 1, 3, 1, 2
ANALOG_CHANNEL_CAVEAT_AT = 6

# The ADC caveat, cited rather than asserted. Source: data/boards.py, B001
# ESP32 classic (WROOM-32E), `fools`.
ADC_SOURCE = ("boards.py B001 `fools`: “ADC2 stops working the moment Wi-Fi is "
              "active — a silent failure that produces frozen or garbage analog "
              "readings… Put every analog sensor on ADC1 (GPIO32-39). The ADC "
              "itself is non-linear and noisy even on ADC1.”")

_HEX = re.compile(r"0x([0-9A-Fa-f]{2})")
_HEX_RANGE = re.compile(r"0x([0-9A-Fa-f]{2})\s*(?:-|–|—|to)\s*0x([0-9A-Fa-f]{2})")


def i2c_addresses(record):
    """Every 7-bit address a part can occupy, parsed out of the `i2c_addr`
    prose. Ranges ('0x28-0x2D', '0x44-0x47 selectable on the ADDR pin') expand.
    Returns None — not an empty set — when the field is absent, because "we do
    not know this part's address" and "this part has no addresses" are different
    answers and only one of them is a reason to worry."""
    txt = record.get("i2c_addr")
    if not txt:
        return None
    addrs = set()
    for m in _HEX_RANGE.finditer(txt):
        lo, hi = int(m.group(1), 16), int(m.group(2), 16)
        if lo <= hi and hi - lo <= 32:
            addrs.update(range(lo, hi + 1))
    addrs.update(int(m.group(1), 16) for m in _HEX.finditer(txt))
    return addrs or None


def chosen_iface(record):
    """The bus this part would actually be wired to, best case."""
    have = record.get("iface") or []
    for want in IFACE_PREFERENCE:
        if want in have:
            return want
    return have[0] if have else None


def esp32_fit(recs, boards):
    """Can this combination hang off one ESP32 board, and which ones?

    -> dict(verdict, boards_that_fit, pin_budget, caveats, blockers, detail)
    verdict ∈ single-board | single-board-with-caveats | needs-glue | not-single-board
    """
    caveats, blockers, unknowns, notes = [], [], [], []
    buses = Counter()
    pins = 0
    detail = []

    for r in recs:
        ifc = chosen_iface(r)
        own = r.get("pins") if isinstance(r.get("pins"), int) else 1
        buses[ifc] += 1
        detail.append(dict(id=r["id"], name=r["n"], iface=ifc,
                           iface_options=list(r.get("iface") or []), pins_field=r.get("pins")))
        if ifc in GLUE_NEEDED:
            blockers_glue = f"{r['n']} is {ifc}-only — needs {GLUE_NEEDED[ifc]}"
            notes.append(("glue", blockers_glue))
        elif ifc in ("I2C", "1-Wire", "SPI", "UART"):
            pass                                   # accounted for below, as a bus
        else:
            pins += own                            # Analog/Digital/Pulse/PWM/I2S/Camera/Builtin

    if buses["I2C"]:
        pins += I2C_PINS
    if buses["1-Wire"]:
        pins += ONEWIRE_PINS
    if buses["SPI"]:
        pins += SPI_BUS_PINS + SPI_CS_PINS * buses["SPI"]
    if buses["UART"]:
        pins += UART_PINS * buses["UART"]
        if buses["UART"] > UART_INSTANCES:
            blockers.append(f"{buses['UART']} UART parts but the ESP32 has "
                            f"{UART_INSTANCES} UART controllers — one of these needs a "
                            f"software serial port or an external UART bridge")

    # ---- I2C address conflicts ------------------------------------------
    i2c_parts = [r for r in recs if chosen_iface(r) == "I2C"]
    for a, b in combinations(i2c_parts, 2):
        sa, sb = i2c_addresses(a), i2c_addresses(b)
        if sa is None or sb is None:
            missing = a if sa is None else b
            unknowns.append(f"{missing['n']} is an I2C part with no `i2c_addr` recorded — "
                            f"its address against {(b if sa is None else a)['n']} is UNKNOWN, "
                            f"not clear")
            continue
        overlap = sa & sb
        if not overlap:
            continue
        if len(sa) == 1 and len(sb) == 1:
            addr = next(iter(overlap))
            escape = ("; one of them also offers SPI, which is the other way out"
                      if "SPI" in (a.get("iface") or []) or "SPI" in (b.get("iface") or [])
                      else "")
            blockers.append(f"I2C address collision at 0x{addr:02X} between {a['n']} and "
                            f"{b['n']} — both are fixed-address, so this needs a TCA9548A "
                            f"mux or a second I2C bus{escape}")
        else:
            movable = a["n"] if len(sa) > 1 else b["n"]
            caveats.append(f"{a['n']} and {b['n']} overlap at "
                           f"{', '.join('0x%02X' % x for x in sorted(overlap))} — strap "
                           f"{movable} to its alternate address")

    # ---- levels ----------------------------------------------------------
    for r in recs:
        v = r.get("v") or ""
        if r.get("logic_3v3") is False:
            caveats.append(f"{r['n']} does not present 3.3V-safe logic ({v or 'see `v`'}) — "
                           f"needs level shifting")
        elif (r.get("logic_3v3") is None
              and re.search(r"\b5(?:\.0)?\s*V", v)
              and not re.search(r"3\.3|3\.0|1\.8", v)):
            caveats.append(f"{r['n']} is a 5V part ({v}) with no `logic_3v3` recorded — "
                           f"assume level shifting until checked")

    # ---- analog channels -------------------------------------------------
    n_analog = buses["Analog"]
    if n_analog > ANALOG_CHANNEL_CAVEAT_AT:
        caveats.append(f"{n_analog} parts want their own ADC pin. The usable analog "
                       f"channels are the ADC1 ones, because — {ADC_SOURCE}")

    # ---- boards ----------------------------------------------------------
    needs_camera = any(chosen_iface(r) == "Camera" for r in recs)
    hosts = [b for b in boards if "Builtin" in (b.get("iface") or [])]
    fit = []
    for b in hosts:
        if needs_camera and "Camera" not in (b.get("iface") or []):
            continue
        if (b.get("pins") or 0) >= pins:
            fit.append(b)
    if needs_camera:
        notes.append(("camera", "a Camera-iface part only fits the boards whose own "
                                "`iface` includes Camera"))
    if not fit:
        blockers.append(f"pin budget of {pins} fits none of the "
                        f"{len(hosts)} ESP32 host boards"
                        + (" that carry a camera bus" if needs_camera else ""))

    glue = [m for kind, m in notes if kind == "glue"]
    if blockers:
        verdict = "not-single-board"
    elif glue:
        verdict = "needs-glue"
    elif caveats or unknowns:
        verdict = "single-board-with-caveats"
    else:
        verdict = "single-board"

    return dict(
        verdict=verdict,
        boards_that_fit=[dict(id=b["id"], name=b["n"], pins=b.get("pins")) for b in fit],
        pin_budget=pins,
        buses=dict(buses),
        caveats=caveats + glue,
        blockers=blockers,
        unknowns=unknowns,
        notes=[m for _k, m in notes if _k != "glue"],
        detail=detail)


# ===========================================================================
# 4 · THE SCORE
# ===========================================================================
# Every weight and every normalisation constant lives here, in the open, with
# the reason it has the value it has. Nothing below this block contains a bare
# number that changes a ranking.
#
# Normalisation is a fixed saturating map, raw -> min(raw/CAP, 1), not a
# percentile over the run. That is deliberate: a percentile normaliser means a
# pair's score changes when you filter the catalog, and two exports stop being
# comparable. Fixed caps mean a score means the same thing every time.

WEIGHTS = {
    # The headline claim: outcomes the pair reaches that neither reaches alone.
    # Highest weight because it is the only component that answers "what does
    # this combination KNOW that its parts do not", which is the question.
    "synergy": 0.30,

    # The most defensible signal in the model, and weighted to say so: part A's
    # `fools` prose names an interferent, and part B physically measures that
    # interferent. That is not a metaphor about complementarity — it is a
    # correction term you can write down. Every instance quotes its prose.
    "compensation": 0.28,

    # Two parts measuring the same phenomenon through DIFFERENT physics. The
    # disagreement is the measurement (dew point vs surface temperature, radar
    # vs PIR). Weighted below compensation because same-phenomenon pairs are
    # also how you build an expensive way to measure one thing twice.
    "shared_measurand": 0.18,

    # Do they fail together? Jaccard distance over the extracted interferent
    # sets, plus differing modality and contact class. Lower weight because it
    # is a property of the prose's thoroughness as much as of the physics — a
    # tersely-documented sensor looks independent of everything.
    "failure_independence": 0.12,

    # Matched time constants make subtraction valid; separated ones let a slow
    # reference discipline a fast channel. Which rule applies depends on what
    # the pair claims, so this is signed by claim type, and scores 0 — never a
    # bonus — when either tau is unknown.
    "time_separation": 0.08,

    # A tiebreaker, not a driver. The project's goal is combinations nobody has
    # tried, but "nobody wrote it down in this catalog" is weak evidence about
    # the world, so it is worth 4% and a CLI filter, not more.
    "novelty": 0.04,
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "WEIGHTS must sum to 1"

# Cost is deliberately ABSENT from WEIGHTS. `outcome_solver` already ranks parts
# per pound and its own finding is that cost-optimising reaches for the cheapest
# dumbest transducers; dividing this score by price would rediscover that and
# fill the top of the table with 50p pairs. Cost is reported (`usd`,
# `per_dollar`) and filtered (`--max-usd`), not scored.

SYNERGY_EMERGENT_KEY = 3.0     # an EMERGENT key is an outcome with no catalog row
SYNERGY_ROUTE_KEY = 1.0        # a new route reaches an outcome that already exists
SAME_MODALITY_REDUNDANCY = 0.15  # same phenomenon, same physics = a spare, not a pair

# Thirteen of the 52 fusion edges require ONE capability at multiplicity >= 2:
# psychrometric-wetbulb, soil-heat-pulse and house-thermal-constant all read
# `[("temperature-contact", 2)]`. 59 catalog parts carry temperature-contact —
# every IMU, barometer and pulse oximeter with a die-temperature register — so
# all 1,711 of those pairs fire the same three edges and, uncorrected, they own
# the entire top of the table.
#
# The reason to discount them is not that they are false, it is that they say
# NOTHING ABOUT THE PAIR. fusion.py's own FUSION_FINDINGS makes the argument:
# "two copies of one £2 probe satisfy a ×2 edge in practice". If one part bought
# twice satisfies the edge, then the edge is not evidence that these two
# DIFFERENT parts belong together. What two different parts do add over two
# identical ones is independent error — real, but a fraction of the claim.
SYNERGY_MULTIPLICITY_ONLY = 0.25

NORM = {
    # Calibrated on the full 81,810-PAIR run; a combination at the cap scores 1.0
    # and anything beyond is equally excellent, which is the honest shape — the
    # difference between 9 and 14 gained outcomes is not worth ranking on.
    # Because the caps are pair-calibrated, TRIPLE totals saturate more
    # components and must NOT be compared numerically against pair totals. Rank
    # within a k, never across it.
    "synergy": 9.0,         # p99.95 of the full 81,810-pair run, after the
                            # multiplicity discount below (raw p99 = 3.75, max 11.75)
    "compensation": 3.0,    # p99.9 of the run; only 15,804 of 81,810 pairs have
                            # any channel at all, and the maximum found is 5
    "shared_measurand": 2.0,  # p99.9; one cross-modality overlap scores 0.5
}

# failure_independence composition
FI_JACCARD, FI_MODALITY, FI_CONTACT = 0.75, 0.15, 0.10

PRIVACY_ORDER = ["None", "Aggregate", "Identifiable", "Raw-imagery"]


# --------------------------------------------------------------- preparation

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*")


def part_tokens(record):
    """Distinctive strings that identify this part inside someone else's prose.
    A token must contain a digit and be at least four characters, or be an
    all-caps word of five or more — otherwise 'Grove GSR' and 'DIY leaf clip'
    would match half the catalog and every pair would read as already-explored."""
    toks = set()
    for field in ("pn", "n"):
        for chunk in re.split(r"[/,()]", record.get(field) or ""):
            for t in _TOKEN_RE.findall(chunk):
                if len(t) >= 4 and any(c.isdigit() for c in t):
                    toks.add(t.lower())
                elif len(t) >= 5 and t.isupper():
                    toks.add(t.lower())
    return toks


def prepare(records):
    """Per-record derived facts, computed once. 81,810 pairs times a regex sweep
    of 39 interferents over 900 characters of prose is not something to do
    inside the inner loop."""
    prep = {}
    for r in records:
        cov = fusion.covers(r)
        solo = osv.closure([r])
        tau, basis, conf = estimate_tau(r)
        prep[r["id"]] = dict(
            rec=r,
            covers=cov,
            phenomena={p for p in r.get("phenomena") or [] if p in vocab.PHENOMENON},
            reach=cov | {e["provides"] for e in solo["fired"]},
            solo_fired=set(solo["fired_keys"]),
            interferents=extract_interferents(r),
            tau=tau, tau_basis=basis, tau_confidence=conf,
            tokens=part_tokens(r),
            prose=((r.get("pair") or "") + "  " + (r.get("spark") or "")).lower(),
            i2c=i2c_addresses(r),
        )
    return prep


_EDGE_EXAMPLES = [(e["key"], (e.get("example") or "").lower()) for e in fusion.FUSION_EDGES]

# Edges satisfied by N copies of ONE capability — see SYNERGY_MULTIPLICITY_ONLY.
MULTIPLICITY_ONLY_EDGES = {
    e["key"] for e in fusion.FUSION_EDGES
    if len({c for c, _m in e["requires"]}) == 1
    and max(m for _c, m in e["requires"]) >= 2}

# Edges that ALSO lean on an N-copies atom but combine it with a second, genuinely
# different capability (`building-ua` = energy-accumulated + temperature-contact×2,
# `loop-heat-meter` = flow-liquid + temperature-contact×2). These are NOT discounted
# — the second capability is real synergy — but they are flagged in the output,
# because part of the claim still rides on the same die-temperature halo and a
# reader deserves to see which half is which.
MULTIPLICITY_ASSISTED_EDGES = {
    e["key"] for e in fusion.FUSION_EDGES
    if e["key"] not in MULTIPLICITY_ONLY_EDGES
    and max(m for _c, m in e["requires"]) >= 2}


# ------------------------------------------------------------------- scoring

def _novelty(members):
    """`known` if the catalog already pairs these parts in prose, else
    `unexplored`. Evidence is always returned, including the evidence of
    absence (a part with no distinctive token cannot be found in prose, and
    that is a limitation of the check, not proof of novelty)."""
    ev = []
    for a, b in combinations(members, 2):
        for x, y in ((a, b), (b, a)):
            hit = sorted(t for t in x["tokens"] if t in y["prose"])
            if hit:
                ev.append(f"{x['rec']['n']} named as {hit[0]!r} in {y['rec']['n']}'s "
                          f"pair/spark prose")
    toks = [m["tokens"] for m in members]
    for key, ex in _EDGE_EXAMPLES:
        if all(any(t in ex for t in ts) for ts in toks if ts):
            if all(ts for ts in toks):
                ev.append(f"both appear in fusion edge {key!r}'s worked example")
    weak = [m["rec"]["n"] for m in members if not m["tokens"]]
    if ev:
        return "known", ev
    note = ([f"no distinctive part token for {', '.join(weak)} — the prose check "
             f"cannot see it, so 'unexplored' is weaker here"] if weak else [])
    return "unexplored", note


def _time_score(mode, d):
    """Signed by claim type. `matched` wants tau_a ~ tau_b so the two channels
    can be subtracted; `separated` wants a slow reference disciplining a fast
    one. Returns 0.0 for unknown — never a bonus for missing data."""
    if d is None:
        return 0.0
    if mode == "matched":
        if d <= 0.5:
            return 1.0
        if d >= 2.0:
            return 0.0
        return (2.0 - d) / 1.5
    if mode == "separated":
        if 1.0 <= d <= 4.0:
            return 1.0
        if d < 1.0:
            return d
        if d >= 6.0:
            return 0.0
        return (6.0 - d) / 2.0
    return 0.0


def score_combo(recs, prep=None, boards=None, with_esp32=True):
    """Score one combination. Returns every component with the evidence that
    produced it — the point of this function is that a rank can be argued with,
    not that it produces a number."""
    prep = prep if prep is not None else prepare(recs)
    members = [prep[r["id"]] for r in recs]
    ids = [r["id"] for r in recs]
    names = [r["n"] for r in recs]

    # ---- synergy ---------------------------------------------------------
    cl = osv.closure(recs)
    joint = set().union(*(m["covers"] for m in members)) | {e["provides"] for e in cl["fired"]}
    alone = set().union(*(m["reach"] for m in members))
    synergy_keys = sorted(joint - alone)
    emergent_keys = [k for k in synergy_keys if k in fusion.EMERGENT]
    new_route_keys = [k for k in synergy_keys if k in vocab.INFERENCE]
    solo_fired = set().union(*(m["solo_fired"] for m in members))
    edges_fired_jointly = sorted(set(cl["fired_keys"]) - solo_fired)
    fired_by_key = {e["key"]: e for e in cl["fired"]}
    # a synergy key is "multiplicity-only" when EVERY newly-fired edge that
    # provides it is one of the N-copies-of-one-capability edges
    mult_only, mult_assisted = set(), set()
    for k in synergy_keys:
        srcs = [ek for ek in edges_fired_jointly if fired_by_key[ek]["provides"] == k]
        if srcs and all(ek in MULTIPLICITY_ONLY_EDGES for ek in srcs):
            mult_only.add(k)
        elif any(ek in MULTIPLICITY_ASSISTED_EDGES for ek in srcs):
            mult_assisted.add(k)
    synergy_raw = 0.0
    for k in synergy_keys:
        base = SYNERGY_EMERGENT_KEY if k in fusion.EMERGENT else SYNERGY_ROUTE_KEY
        synergy_raw += base * (SYNERGY_MULTIPLICITY_ONLY if k in mult_only else 1.0)

    # ---- shared measurand, weighted by modality disagreement -------------
    shared = []
    shared_raw = 0.0
    for a, b in combinations(members, 2):
        for p in sorted(a["phenomena"] & b["phenomena"]):
            ma, mb = a["rec"].get("modality"), b["rec"].get("modality")
            differ = ma != mb
            w = 1.0 if differ else SAME_MODALITY_REDUNDANCY
            shared_raw += w
            shared.append(dict(phenomenon=p, a=a["rec"]["n"], b=b["rec"]["n"],
                               modality_a=ma, modality_b=mb,
                               kind="differential" if differ else "redundant",
                               weight=w))

    # ---- compensation ----------------------------------------------------
    # One CHANNEL is one (fooled part, interferent, correcting part) triple. An
    # IMU observing `orientation-tilt` through tilt AND orientation-fused AND
    # acceleration is one correction, not three, so the observing phenomena are
    # collected onto the channel rather than counted as separate evidence.
    compensation = []
    self_compensated = 0
    seen_channels = {}
    for a, b in combinations(members, 2):
        for fooled, corrector in ((a, b), (b, a)):
            for key, snippet in sorted(fooled["interferents"].items()):
                for phen in INTERFERENTS[key]["measured_by"]:
                    if phen not in corrector["phenomena"]:
                        continue
                    if phen in fooled["phenomena"]:
                        self_compensated += 1
                        continue          # it already measures its own confounder
                    sig = (fooled["rec"]["id"], key, corrector["rec"]["id"])
                    if sig in seen_channels:
                        seen_channels[sig]["phenomena"].append(phen)
                        continue
                    ch = dict(
                        fooled_id=fooled["rec"]["id"], fooled=fooled["rec"]["n"],
                        interferent=key, interferent_label=INTERFERENTS[key]["label"],
                        corrector_id=corrector["rec"]["id"], corrector=corrector["rec"]["n"],
                        phenomenon=phen, phenomena=[phen], evidence=snippet)
                    seen_channels[sig] = ch
                    compensation.append(ch)
    comp_raw = float(len(compensation))

    # ---- failure independence -------------------------------------------
    fi_pairs, fi_shared = [], set()
    for a, b in combinations(members, 2):
        ia, ib = set(a["interferents"]), set(b["interferents"])
        union = ia | ib
        fi_shared |= (ia & ib)
        jac = None if not union else 1.0 - len(ia & ib) / len(union)
        modality_differ = a["rec"].get("modality") != b["rec"].get("modality")
        contact_differ = a["rec"].get("contact") != b["rec"].get("contact")
        val = (0.0 if jac is None else FI_JACCARD * jac) \
            + FI_MODALITY * modality_differ + FI_CONTACT * contact_differ
        fi_pairs.append(dict(a=a["rec"]["n"], b=b["rec"]["n"],
                             jaccard_distance=None if jac is None else round(jac, 3),
                             shared_interferents=sorted(ia & ib),
                             modality_differ=modality_differ, contact_differ=contact_differ,
                             value=round(val, 3)))
    failure_independence = min(sum(p["value"] for p in fi_pairs) / len(fi_pairs), 1.0)
    fi_unknown = any(p["jaccard_distance"] is None for p in fi_pairs)

    # ---- time separation -------------------------------------------------
    taus = [m["tau"] for m in members]
    ds = [tau_decades(a, b) for a, b in combinations(taus, 2)]
    d = None if any(x is None for x in ds) else max(ds)
    shared_norm = min(shared_raw / NORM["shared_measurand"], 1.0)
    comp_norm = min(comp_raw / NORM["compensation"], 1.0)
    if d is None:
        time_mode = "unknown"
        time_note = ("at least one member has no parsable time constant — "
                     + "; ".join(f"{m['rec']['n']}: {m['tau_basis']}"
                                 for m in members if m["tau"] is None))
    elif shared_raw > 0 and shared_norm >= comp_norm:
        time_mode = "matched"
        time_note = ("the claim is differential/cross-validating (shared measurand "
                     "dominates), so matched time constants are what make the "
                     "subtraction valid")
    elif comp_raw > 0:
        time_mode = "separated"
        time_note = ("the claim is compensation — one channel corrects the other — so "
                     "1-4 decades of separation is the useful shape: a slow reference "
                     "disciplining a fast signal")
    else:
        time_mode = "unknown"
        time_note = ("neither a shared measurand nor a compensation channel, so no "
                     "rule about time constants applies")
    time_score = _time_score(time_mode, d)

    # ---- novelty ---------------------------------------------------------
    novelty, novelty_evidence = _novelty(members)

    # ---- practicals ------------------------------------------------------
    usd = [r.get("usd") for r in recs]
    cost = sum(u for u in usd if isinstance(u, (int, float)))
    hazards = sorted({h for r in recs for h in (r.get("hazard") or [])})
    privacy = max((r.get("privacy") for r in recs),
                  key=lambda p: PRIVACY_ORDER.index(p) if p in PRIVACY_ORDER else -1)
    pwr = sum(r.get("pwr_ua") or 0 for r in recs)
    max_diff = max((r.get("diff") or 0) for r in recs)

    # ---- total -----------------------------------------------------------
    components = dict(
        synergy=min(synergy_raw / NORM["synergy"], 1.0),
        compensation=comp_norm,
        shared_measurand=shared_norm,
        failure_independence=failure_independence,
        time_separation=time_score,
        novelty=1.0 if novelty == "unexplored" else 0.0)
    total = sum(WEIGHTS[k] * v for k, v in components.items())

    out = dict(
        ids=ids, names=names, joint_reach=sorted(joint),
        total=round(total, 5), components={k: round(v, 4) for k, v in components.items()},
        synergy=dict(score=round(components["synergy"], 4), raw=round(synergy_raw, 3),
                     keys=synergy_keys, emergent_keys=emergent_keys,
                     new_route_keys=new_route_keys,
                     multiplicity_only_keys=sorted(mult_only),
                     multiplicity_assisted_keys=sorted(mult_assisted),
                     edges_fired_jointly=edges_fired_jointly,
                     edges_fired_total=cl["fired_keys"]),
        shared_measurand=dict(score=round(shared_norm, 4), raw=round(shared_raw, 3),
                              shared=shared,
                              keys=sorted({s["phenomenon"] for s in shared})),
        compensation=dict(score=round(comp_norm, 4), raw=comp_raw,
                          channels=compensation, self_compensated=self_compensated),
        failure_independence=dict(score=round(failure_independence, 4), pairs=fi_pairs,
                                  shared_interferents=sorted(fi_shared),
                                  unknown=fi_unknown),
        time=dict(score=round(time_score, 4), mode=time_mode, decades=d, note=time_note,
                  taus=[dict(id=m["rec"]["id"], tau=m["tau"], confidence=m["tau_confidence"],
                             basis=m["tau_basis"]) for m in members]),
        novelty=novelty, novelty_evidence=novelty_evidence,
        usd=round(cost, 2), per_dollar=round(total / max(cost, 0.5), 4),
        max_diff=max_diff, hazard=hazards, privacy=privacy, pwr_ua=round(pwr, 1),
    )
    out["reasoning"] = _reasoning(out, members)
    out["confound"] = _confound(out, cl)
    if with_esp32 and boards is not None:
        f = esp32_fit(recs, boards)
        out["esp32"] = f
        out["esp32_verdict"] = f["verdict"]
        out["boards_that_fit"] = [b["id"] for b in f["boards_that_fit"]]
    return out


def _reasoning(s, members):
    """A sentence built only out of things that were actually matched. If a
    component found nothing, it contributes nothing — no 'these sensors
    complement each other' filler."""
    bits = []
    names = s["names"]
    if s["compensation"]["channels"]:
        c = s["compensation"]["channels"][0]
        bits.append(f"{c['corrector']} measures `{c['phenomenon']}`, which is exactly what "
                    f"fools {c['fooled']} ({INTERFERENTS[c['interferent']]['label'].lower()})"
                    + (f", plus {len(s['compensation']['channels']) - 1} further correction "
                       f"channel(s)" if len(s["compensation"]["channels"]) > 1 else ""))
    diffs = [x for x in s["shared_measurand"]["shared"] if x["kind"] == "differential"]
    if diffs:
        x = diffs[0]
        bits.append(f"both read `{x['phenomenon']}` but through different physics "
                    f"({x['modality_a']} vs {x['modality_b']}), so the disagreement between "
                    f"them is itself the measurement")
    elif s["shared_measurand"]["shared"]:
        x = s["shared_measurand"]["shared"][0]
        bits.append(f"they share `{x['phenomenon']}` through the same {x['modality_a']} "
                    f"physics, which is redundancy rather than a differential pair")
    if s["synergy"]["emergent_keys"]:
        mo = set(s["synergy"]["multiplicity_only_keys"])
        strong = [k for k in s["synergy"]["emergent_keys"] if k not in mo]
        weak = [k for k in s["synergy"]["emergent_keys"] if k in mo]
        if strong:
            bits.append("together they reach " + ", ".join(f"`{k}`" for k in strong[:4])
                        + ", which no member reaches alone")
        if weak:
            bits.append(", ".join(f"`{k}`" for k in weak[:3]) + " also fire, but only "
                        "because two parts happen to carry the same capability — two "
                        "copies of one part would do the same, so that is discounted")
    elif s["synergy"]["new_route_keys"]:
        bits.append("together they open a new route to " + ", ".join(
            f"`{k}`" for k in s["synergy"]["new_route_keys"][:4]))
    _WHY = {"matched": "matched constants are what make the subtraction valid",
            "separated": "a slow reference disciplining a fast channel",
            "unknown": "no timing rule applies to this claim"}
    if s["time"]["decades"] is not None:
        bits.append(f"their time constants differ by {s['time']['decades']:.1f} decades, "
                    f"scored as `{s['time']['mode']}` ({_WHY[s['time']['mode']]})")
    else:
        bits.append(f"time constants are `unknown` for at least one member, so nothing is "
                    f"claimed about their timing")
    if not bits:
        return (f"Nothing was matched between {names[0]} and {names[1] if len(names) > 1 else ''}"
                f" — no shared measurand, no compensation channel, no joint fusion edge.")
    head = " + ".join(names)
    return head + ": " + "; ".join(bits) + "."


def _confound(s, closure_result):
    """The repo's own rule is that a claim without a stated confound is
    marketing. This states one from the members' overlapping interferents and
    from the `confound` field of any fusion edge that fired — or says plainly
    that it cannot."""
    parts = []
    shared = s["failure_independence"]["shared_interferents"]
    if shared:
        parts.append("Both members are fooled by the same thing ("
                     + ", ".join(INTERFERENTS[k]["label"].lower() for k in shared[:3])
                     + "), so agreement between them is NOT independent confirmation")
    fired_joint = set(s["synergy"]["edges_fired_jointly"])
    for e in closure_result["fired"]:
        if e["key"] in fired_joint and e.get("confound"):
            parts.append(f"{e['name']}: {e['confound'].rstrip('.')}")
            break
    if s["compensation"]["channels"]:
        c = s["compensation"]["channels"][0]
        parts.append(f"the correction is only as good as the co-location — "
                     f"{c['corrector']} must sit in the same air/on the same surface as "
                     f"{c['fooled']} or it is correcting a different place")
    if s["time"]["mode"] == "unknown":
        parts.append("and at least one time constant is unknown, so the two channels may "
                     "not even be comparable in time")
    if not parts:
        return "unstated — check members' fools text"
    return ". ".join(x[0].upper() + x[1:] for x in parts) + "."


def slim(s):
    """The same score with the bulky evidence removed. 81,810 pairs each
    carrying a 180-character prose snippet per compensation channel is a
    quarter of a gigabyte; the ranking only needs the numbers, and the CLI
    re-scores the handful of rows it is going to print."""
    out = dict(s)
    out["compensation"] = dict(
        score=s["compensation"]["score"], raw=s["compensation"]["raw"],
        n=len(s["compensation"]["channels"]),
        channels=[dict(fooled_id=c["fooled_id"], interferent=c["interferent"],
                       corrector_id=c["corrector_id"], phenomenon=c["phenomenon"])
                  for c in s["compensation"]["channels"]],
        self_compensated=s["compensation"]["self_compensated"])
    out["failure_independence"] = dict(
        score=s["failure_independence"]["score"],
        shared_interferents=s["failure_independence"]["shared_interferents"],
        unknown=s["failure_independence"]["unknown"])
    out["time"] = dict(score=s["time"]["score"], mode=s["time"]["mode"],
                       decades=s["time"]["decades"])
    out["shared_measurand"] = dict(score=s["shared_measurand"]["score"],
                                   raw=s["shared_measurand"]["raw"],
                                   keys=s["shared_measurand"]["keys"])
    out["synergy"] = dict(score=s["synergy"]["score"], raw=s["synergy"]["raw"],
                          emergent_keys=s["synergy"]["emergent_keys"],
                          new_route_keys=s["synergy"]["new_route_keys"],
                          multiplicity_only_keys=s["synergy"]["multiplicity_only_keys"],
                          multiplicity_assisted_keys=s["synergy"]["multiplicity_assisted_keys"],
                          edges_fired_jointly=s["synergy"]["edges_fired_jointly"])
    out.pop("joint_reach", None)
    out.pop("novelty_evidence", None)
    out.pop("reasoning", None)
    out.pop("confound", None)
    out.pop("esp32", None)
    return out


# ===========================================================================
# 5 · ENUMERATION
# ===========================================================================

def rank_pairs(sensors, prep=None, boards=None, predicate=None, postfilter=None,
               keep=None):
    """Every C(n,2) pair — for the full catalog that is 81,810, and it is
    EXHAUSTIVE. No sampling, no beam, no cap: at ~0.6 ms a pair the whole space
    costs under a minute, so there is no excuse for a heuristic here.

    `predicate(a, b) -> bool` filters candidates before scoring.
    `postfilter(score) -> bool` filters on the scored result — the only way to
    ask a question about the closure, which does not exist until scoring runs.
    `keep` bounds the returned list to the top N by total (memory, not search).
    """
    prep = prep if prep is not None else prepare(sensors)
    rows = []
    for a, b in combinations(sensors, 2):
        if predicate and not predicate(a, b):
            continue
        s = score_combo([a, b], prep, boards, with_esp32=boards is not None)
        if postfilter and not postfilter(s):
            continue
        rows.append(slim(s))
    rows.sort(key=lambda r: (-r["total"], r["ids"]))
    return rows[:keep] if keep else rows


TRIPLE_STRATEGY = """\
C(405,3) = 11,042,570 combinations. At the measured ~0.7 ms each that is over
two hours, and the great majority are three unrelated parts, so triples are
found by CANDIDATE GENERATION, not by search:

  1. the top `top_pairs` scoring pairs, each extended by every other sensor —
     the assumption being that a strong triple almost always contains a strong
     pair. That assumption is the heuristic, and it is falsifiable: a triple
     whose value only appears at three parts (three temperature points, three
     ranging heads) is invisible to it;
  2. every triple drawn from the parts at or under `extra_pool_max_usd`, in
     full — this is the pool where three-part inventions are actually
     affordable, and it is small enough to enumerate exhaustively;
  3. dedupe by frozenset, then apply `cap`.

THE RESULT IS NOT A GLOBAL OPTIMUM AND MUST NOT BE PRESENTED AS ONE. It is the
best triple found inside a searched neighbourhood, and the neighbourhood is
stated above so the claim can be checked."""


def rank_triples(sensors, pairs, prep=None, boards=None, top_pairs=400,
                 extra_pool_max_usd=3.0, cap=250_000, predicate=None,
                 postfilter=None, keep=None):
    """Candidate-generated triples. See TRIPLE_STRATEGY — it is a heuristic."""
    prep = prep if prep is not None else prepare(sensors)
    by_id = {r["id"]: r for r in sensors}
    cands, seen = [], set()

    def add(ids):
        f = frozenset(ids)
        if len(f) == 3 and f not in seen:
            seen.add(f)
            cands.append(tuple(sorted(f)))

    for row in pairs[:top_pairs]:
        for s in sensors:
            add(row["ids"] + [s["id"]])
    pool = sorted((r for r in sensors
                   if isinstance(r.get("usd"), (int, float))
                   and r["usd"] <= extra_pool_max_usd),
                  key=lambda r: r["id"])
    for c in combinations((r["id"] for r in pool), 3):
        if len(cands) >= cap:
            break
        add(c)
    cands = cands[:cap]

    rows = []
    for ids in cands:
        recs = [by_id[i] for i in ids]
        if predicate and not predicate(*recs):
            continue
        s = score_combo(recs, prep, boards, with_esp32=boards is not None)
        if postfilter and not postfilter(s):
            continue
        rows.append(slim(s))
    rows.sort(key=lambda r: (-r["total"], r["ids"]))
    return dict(rows=rows[:keep] if keep else rows,
                n_candidates=len(cands),
                n_scored=len(rows),
                strategy=TRIPLE_STRATEGY,
                params=dict(top_pairs=top_pairs, extra_pool_max_usd=extra_pool_max_usd,
                            cap=cap, cheap_pool=len(pool)))
