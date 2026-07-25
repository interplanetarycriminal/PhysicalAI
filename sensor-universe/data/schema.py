"""Schema v2 — the single source of truth for the Sensor Universe data model.

Everything downstream (validator, builder, every derived sheet) reads from here.
If a field or vocabulary term is not defined in this file, it does not exist.

Design rules learned from v5's failures:
  * Free-text where an enum belongs makes data unqueryable. v5 had 165 distinct
    `pwr` strings and 101 distinct `iface` strings across 238 sensors, which made
    "show me every I2C sensor" and "compute a battery budget" both impossible.
    Anything that will ever be filtered, sorted or computed on is an enum here.
  * Derived values are NEVER authored. Price tier, power class and pin count are
    computed, so they cannot drift out of sync with their source field.
  * IDs are assigned once and frozen (see ids.py). v5 generated them from sort
    order at build time, so adding one sensor renumbered everything downstream.
"""

# --------------------------------------------------------------------------- enums

MODALITY = {
    "Thermal":    "Heat, infrared emission, thermal conduction",
    "Optical":    "Visible, UV, IR light — intensity, spectrum, time-of-flight",
    "Acoustic":   "Pressure waves in air, liquid or solids (incl. ultrasound)",
    "Mechanical": "Force, strain, displacement, acceleration, rotation, flow",
    "Electrical": "Voltage, current, resistance, capacitance, impedance",
    "Chemical":   "Gas/ion concentration, redox, chemical reaction products",
    "Magnetic":   "Magnetic field strength and direction",
    "RF":         "Radio-frequency propagation, backscatter, channel state",
    "Nuclear":    "Ionising radiation — alpha, beta, gamma, cosmic",
    "Biological": "Biopotentials and physiological signals from living tissue",
}

# How close must the sensor be to the thing it measures? Drives most design decisions.
CONTACT = {
    "Contact":        "Must physically touch the subject",
    "Immersed":       "Must be submerged in / buried in the medium",
    "Through-barrier": "Reads through a wall, container or clothing without touching the subject",
    "Standoff":       "Works across a room (cm to ~10m)",
    "Remote":         "Works at long range (>10m) or without any local install",
}

# What personal data does deploying this create? The modern make-or-break constraint.
PRIVACY = {
    "None":         "Captures nothing attributable to a person",
    "Aggregate":    "Reveals that people are present / how many, but not who",
    "Identifiable": "Can distinguish or identify specific individuals",
    "Raw-imagery":  "Captures images or audio a human could review directly",
}

# Coarse power class. Computed from `pwr_ua` — never authored directly.
POWER_CLASS = {
    "Zero":     "Generates its own signal or draws nothing (passive)",
    "Nanoamp":  "<1µA — coin cell for years",
    "Microamp": "1µA-1mA — small LiPo for months, always-on viable",
    "Milliamp": "1-50mA — must duty-cycle for battery use",
    "Hungry":   ">50mA — mains, large battery, or brief bursts only",
}

ENVIRONMENT = {
    "Indoor":     "Clean, dry, room temperature",
    "Outdoor":    "Weather-exposed with suitable housing",
    "Submersible": "Rated for continuous immersion",
    "Harsh":      "Industrial: dust, vibration, chemicals, temperature extremes",
}

CALIBRATION = {
    "None":       "Factory-calibrated, use as-is",
    "One-point":  "Single offset/zero against a known reference",
    "Two-point":  "Span calibration against two references",
    "Periodic":   "Drifts; needs recalibrating on a schedule",
    "Reference":  "Needs lab standards or calibration gas to mean anything",
}

LIFECYCLE = {
    "Active":     "Current production, safe to design in",
    "Mature":     "Widely available but superseded by a newer part",
    "NRND":       "Not recommended for new designs",
    "EOL":        "End of life — stock only",
    "Clone-risk": "Available, but counterfeits/mislabelled parts are common",
}

# Safety. Absent = no special hazard. The validator REQUIRES one of these on any
# entry whose text implies mains, high voltage, heat, lasers or explosive gas.
HAZARD = {
    "Mains":       "Connects to or measures mains AC — isolation and competence required",
    "HighVoltage": "Generates or requires >48V (e.g. Geiger tube supplies, SiPM bias)",
    "HotSurface":  "Runs hot enough to burn or ignite (heated gas sensors, heaters)",
    "Laser":       "Emits laser radiation — eye safety class matters",
    "UV":          "Emits UV — skin/eye hazard, especially UV-C",
    "Ignition":    "Is an ignition source; must NOT enter a flammable atmosphere",
    "Asphyxiant":  "Involves gases that displace oxygen (CO2, N2, argon)",
    "Toxic":       "Involves toxic gas or chemicals",
    "HighCurrent": "Draws amps — needs its own supply and wiring",
    "Radiation":   "Involves radioactive sources or ionising radiation",
    "Mechanical":  "Moving parts, pinch or cut risk",
}

CONFIDENCE = {
    "Verified": "Checked against a manufacturer or first-party vendor page",
    "High":     "Well-established, widely documented; not individually re-checked",
    "Estimate": "Approximate — treat the number as a tier, not a quote",
}

MATURITY = {
    "Excellent": "First-class library, great docs, huge community",
    "Good":      "Solid library support and plenty of examples",
    "Workable":  "A library exists but expect to read the datasheet",
    "Raw":       "You will be writing the driver",
}

# Bus/interface — an enum so "every I2C part" is one filter, not ten string matches.
INTERFACE = {
    "I2C":     "2-wire addressable bus — the default, shareable",
    "SPI":     "4-wire fast bus, one chip-select per device",
    "UART":    "Async serial, 2 pins per device",
    "1-Wire":  "Many devices on a single data pin",
    "I2S":     "Digital audio stream",
    "Analog":  "Raw voltage into an ADC",
    "Digital": "Simple high/low output or dry contact",
    "Pulse":   "Frequency/count output (use the PCNT peripheral)",
    "PWM":     "Duty-cycle encoded output",
    "RS-485":  "Differential industrial bus, usually Modbus RTU",
    "CAN":     "CAN / TWAI bus",
    "4-20mA":  "Industrial current loop",
    "USB":     "USB device or host",
    "Camera":  "Parallel DVP or MIPI-CSI image bus",
    "Radio":   "Sensing performed by the radio itself (CSI, RSSI, backscatter)",
    "Builtin": "Internal to the SoC — no external wiring",
}

CATALOG = {
    "sensor":   "Something that measures the world",
    "actuator": "Something that changes the world",
    "glue":     "Signal conditioning, conversion, power and interconnect",
    "board":    "Compute — ESP32 family members and carriers",
}

# --------------------------------------------------------------------------- fields

# name -> (required?, kind, note)
#   kind: str | text | float | int | enum:NAME | enumlist:NAME | csv | vocab:NAME
FIELDS = {
    # identity
    "id":        (True,  "str",   "Stable, frozen at first assignment. Never reused."),
    "catalog":   (True,  "enum:CATALOG", "Which catalog this part belongs to"),
    "n":         (True,  "str",   "Human name"),
    "pn":        (True,  "str",   "Manufacturer part number(s)"),
    "cat":       (True,  "vocab:CATEGORY", "Category"),
    "sub":       (True,  "str",   "Subcategory"),

    # what it does
    "meas":      (True,  "str",   "What it measures, in one line"),
    "how":       (True,  "text",  "How it works, plain English"),
    "modality":  (True,  "enum:MODALITY", "Physical principle family"),
    "phenomena": (True,  "vocablist:PHENOMENON", "Physical quantities it transduces"),
    "inferences":(False, "vocablist:INFERENCE", "What it lets you know about the world"),

    # structured performance (was buried in prose in v5)
    "range":     (False, "str",   "Measurement range with units"),
    "accuracy":  (False, "str",   "Accuracy — distinct from resolution"),
    "resolution":(False, "str",   "Smallest resolvable step"),
    "rate":      (False, "str",   "Max sample/update rate"),
    "warmup":    (False, "str",   "Warm-up, settling or burn-in time before data is valid"),

    # interfacing
    "iface":     (True,  "enumlist:INTERFACE", "Bus/interface options"),
    "v":         (True,  "str",   "Supply voltage"),
    "logic_3v3": (False, "bool",  "Is the signal line safe to connect to a 3.3V GPIO?"),
    "i2c_addr":  (False, "str",   "I2C address(es); feeds the conflict map"),
    "pins":      (False, "int",   "GPIO/wires consumed beyond power"),
    "esp32_compat": (False, "str", "Variant caveats (touch/DAC/PSRAM/camera needs)"),

    # constraints
    "contact":   (True,  "enum:CONTACT", "Proximity required to the subject"),
    "privacy":   (True,  "enum:PRIVACY", "Personal-data profile"),
    "environment": (False, "enumlist:ENVIRONMENT", "Where it can survive"),
    "ip":        (False, "str",   "IP rating if any"),

    # power
    "pwr":       (True,  "str",   "Human-readable power draw"),
    "pwr_ua":    (False, "float", "Typical active draw in µA — the computable one"),
    "pwr_sleep_ua": (False, "float", "Sleep/standby draw in µA"),

    # money & sourcing
    "usd":       (True,  "float", "Typical breakout street price, USD"),
    "buy":       (True,  "csv",   "Vendor codes"),
    "brd":       (True,  "str",   "Popular breakouts/modules"),
    "lib":       (True,  "str",   "Library/driver support"),
    "link":      (False, "str",   "Manufacturer or first-party vendor URL"),
    "lifecycle": (False, "enum:LIFECYCLE", "Availability status"),
    "maturity":  (False, "enum:MATURITY", "Ecosystem quality"),

    # the expert-reviewer fields
    "fools":     (False, "text",  "What fools it: false positives, drift, blind spots"),
    "hazard":    (False, "enumlist:HAZARD", "Safety hazards"),
    "calibration": (False, "enum:CALIBRATION", "Calibration burden"),
    "consumable":(False, "str",   "Consumables and service life"),
    "requires":  (False, "str",   "HARD dependencies — parts without which it will not work"),
    "substitutes": (False, "str", "Cheaper / better / no-contact alternatives"),

    # creative
    "diff":      (True,  "int",   "Difficulty 1-5 (see DIFFICULTY_RUBRIC)"),
    "use":       (True,  "text",  "Common uses"),
    "spark":     (True,  "text",  "Invention spark"),
    "pair":      (False, "str",   "Creative pairings (soft — see `requires` for hard deps)"),
    "tags":      (True,  "vocablist:THEME", "Theme tags"),

    # provenance
    "confidence":(False, "enum:CONFIDENCE", "How much to trust the price/specs"),
    "as_of":     (False, "str",   "Date the price/spec was last checked"),
    "note":      (False, "text",  "Anything else worth knowing"),
}

REQUIRED = [k for k, v in FIELDS.items() if v[0]]

# v5 had no rubric: a $45 NPU camera was rated 1 and a 400V Geiger kit was rated 2.
DIFFICULTY_RUBRIC = {
    1: "Plug and play — Qwiic/STEMMA cable or 3 wires, library example works first time",
    2: "Easy — breadboard wiring, a well-documented library, no analog thought needed",
    3: "Some skill — calibration, level shifting, timing, or datasheet reading required",
    4: "Advanced — analog front-ends, protocol work, mechanical integration, or real safety",
    5: "Expert — you are doing research; expect to write drivers and validate your own results",
}

# --------------------------------------------------------------------------- derived

def price_tier(usd):
    if usd is None:      return "?"
    if usd == 0:         return "free"
    if usd < 5:          return "$"
    if usd < 15:         return "$$"
    if usd < 50:         return "$$$"
    return "$$$$"

PRICE_TIER_LABEL = {
    "free": "no cost — built in or repurposed",
    "$":    "under $5",
    "$$":   "$5–15",
    "$$$":  "$15–50",
    "$$$$": "$50+",
    "?":    "price unknown",
}

def power_class(pwr_ua, pwr_text=""):
    """Coarse class from the computable µA figure, falling back to text hints."""
    if pwr_ua is None:
        t = (pwr_text or "").lower()
        if t.startswith("0") or "passive" in t or "generates" in t:
            return "Zero"
        return "Milliamp"
    if pwr_ua <= 0:      return "Zero"
    if pwr_ua < 1:       return "Nanoamp"
    if pwr_ua < 1_000:   return "Microamp"
    if pwr_ua < 50_000:  return "Milliamp"
    return "Hungry"

# Semantic colour: hue carries meaning. One colour per modality, not 32 random pastels.
MODALITY_COLOR = {
    "Thermal":    "F4C7A1",
    "Optical":    "FFE9A8",
    "Acoustic":   "C9DFF0",
    "Mechanical": "CFE3CF",
    "Electrical": "F7D4D4",
    "Chemical":   "DCCFE8",
    "Magnetic":   "C6E6E2",
    "RF":         "E2D7C3",
    "Nuclear":    "E8CBD6",
    "Biological": "F2D9C4",
}

CATALOG_COLOR = {
    "sensor": "1F2A44", "actuator": "8C3B2E", "glue": "4A5878", "board": "2F5D50",
}
