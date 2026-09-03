"""Deterministic derivation of the structured ESP32 interface fields.

Nothing here is a new claim. Every value is a re-reading of text that is already
in the record and already reviewed — `v`, `rate`, `pwr`, `iface`, `i2c_addr`,
`logic_3v3`, `hazard` — turned into a form you can filter and compute on.

Three rules, in order of importance:

  1. Ambiguity yields None. These parsers match well-formed patterns and refuse
     everything else. A missing number is a gap; a guessed number is a lie, and
     the whole point of the field set is that an explicit None means "nobody has
     checked this yet".
  2. Authored wins. `data/enrich_iface.py` is merged by the loader before any of
     this runs, and a derivation never overwrites a value that came from there.
  3. Only the safe half is derivable. `level_shift` is never derived as
     "Divider" or "Analog-front-end" and `addr_mode` is never derived for a bus
     whose addressing the record does not state — those are authored only.

Run `python3 data/iface_derive.py` for a coverage self-check over the catalog.
"""
import re

# --------------------------------------------------------------------------- volts

_NUM = r"\d+(?:\.\d+)?"
_VUNIT = r"V(?:DC)?"

# A whole-string match, deliberately. "3.3-5V (board)", "5V cycled" and
# "3.3/5V versions" all name two different things and are left to an author.
_V_RANGE = re.compile(
    rf"^({_NUM})\s*(?:{_VUNIT})?\s*(?:-|–|to|or)\s*({_NUM})\s*{_VUNIT}$", re.I)
_V_ONE = re.compile(rf"^({_NUM})\s*{_VUNIT}$", re.I)
_V_3V3 = re.compile(r"^(\d)V(\d)$", re.I)          # 3V3, 1V8 — the EE shorthand

V_LOW, V_HIGH = 0.5, 250.0                          # sanity fence, both ends


def _v_ok(a, b):
    return V_LOW <= a <= b <= V_HIGH


def parse_volts(v_text):
    """`v` -> (v_min, v_max) in volts, or (None, None) if it is not a clean range.

    Handles "3.0-5.5V", "1.7-3.6V", "3.3V", "2.5 to 3.6 V", "3.3V or 5V", "3V3".
    Refuses anything carrying prose ("any (divider)", "mains", "5V cycled") and
    anything slash-separated ("3.3/5V versions"), which names two products.
    """
    t = (v_text or "").strip()
    if not t or "/" in t:
        return (None, None)
    m = _V_RANGE.match(t)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        return (a, b) if _v_ok(a, b) else (None, None)
    m = _V_ONE.match(t)
    if m:
        a = float(m.group(1))
        return (a, a) if _v_ok(a, a) else (None, None)
    m = _V_3V3.match(t)
    if m:
        a = float(f"{m.group(1)}.{m.group(2)}")
        return (a, a) if _v_ok(a, a) else (None, None)
    return (None, None)


# --------------------------------------------------------------------------- rate

# Leading and trailing qualifiers that do not change the number's meaning.
_LEAD = r"(?:up\s+to|max\.?|maximum|about|ODR)?\s*[~≈]?\s*"
_TRAIL = r"(?:\s+ODR)?"
_HZ = r"(k)?Hz"
_SPS = r"(k)?(?:SPS|sps|samples?/s|sample\s+per\s+second|readings?/s|fps|frames?/s)"

_R_RANGE = re.compile(
    rf"^{_LEAD}{_NUM}\s*(?:k)?(?:Hz)?\s*(?:-|–|to)\s*[~≈]?\s*({_NUM})\s*{_HZ}{_TRAIL}$", re.I)
_R_ONE = re.compile(rf"^{_LEAD}({_NUM})\s*{_HZ}{_TRAIL}$", re.I)
_R_SPS_RANGE = re.compile(
    rf"^{_LEAD}{_NUM}\s*(?:k)?(?:SPS|sps|fps)?\s*(?:-|–|to)\s*[~≈]?\s*({_NUM})\s*{_SPS}$")
_R_SPS_ONE = re.compile(rf"^{_LEAD}({_NUM})\s*{_SPS}$")
# "1 reading / 5 s", "one reading every 2s", "1 sample/s"
_R_EVERY = re.compile(
    rf"^(?:one|1)\s+(?:reading|sample|measurement|conversion)\s*"
    rf"(?:/|per|every)\s*({_NUM})?\s*(s|sec|secs|second|seconds|min|minute|minutes)$", re.I)

_PERIOD_S = {"s": 1.0, "sec": 1.0, "secs": 1.0, "second": 1.0, "seconds": 1.0,
             "min": 60.0, "minute": 60.0, "minutes": 60.0}
RATE_MAX = 1e7                                       # above this it is a clock, not a rate
# A bare Hz/kHz figure this large is a bus clock or a carrier, never an update
# rate — "Up to 400kHz" on an I2C mux is the SCL speed. An explicit sampling
# unit (SPS, fps) or an "ODR" qualifier lifts the ceiling.
BARE_HZ_CEILING = 100_000.0


def _rate_ok(hz):
    return hz is not None and 0 < hz < RATE_MAX


def parse_rate_hz(rate_text):
    """`rate` -> the maximum sample/update rate in Hz, or None.

    Handles "125Hz", "1 kHz", "up to 200 Hz", "Max 8kHz", "1 sample/s",
    "one reading every 2s" (0.5), "8-860 SPS" (860), "12.5Hz to 800Hz ODR".
    A range yields its maximum. Everything with prose attached ("Continuous;
    ~1s package time constant"), everything unitless, "Varies" and MHz clock
    speeds are refused — MHz because a CPU clock is not a sample rate, and a
    bare figure at or above BARE_HZ_CEILING for the same reason.
    """
    t = (rate_text or "").strip()
    if not t:
        return None
    for rx, bare in ((_R_RANGE, True), (_R_ONE, True),
                     (_R_SPS_RANGE, False), (_R_SPS_ONE, False)):
        m = rx.match(t)
        if m:
            hz = float(m.group(1)) * (1000.0 if m.group(2) else 1.0)
            if bare and hz >= BARE_HZ_CEILING and "ODR" not in t:
                return None
            return hz if _rate_ok(hz) else None
    m = _R_EVERY.match(t)
    if m:
        period = float(m.group(1) or 1.0) * _PERIOD_S[m.group(2).lower()]
        hz = 1.0 / period if period > 0 else None
        return hz if _rate_ok(hz) else None
    return None


# --------------------------------------------------------------------------- peak current

_IUNIT = {"na": 0.001, "ua": 1.0, "µa": 1.0, "ma": 1000.0, "a": 1_000_000.0}
_I = rf"([~≈<]?\s*{_NUM})\s*(nA|µA|uA|mA|A)\b"
_SLEEPY = re.compile(r"sleep|standby|shutdown|quiescent|idle", re.I)

# keyword first: "peaks over 300mA", "burst of 40mA"
_P_AFTER = re.compile(
    rf"(?:peak|burst|surge|inrush|max(?:imum)?)s?((?:\s+[A-Za-z-]+){{0,2}})\s+{_I}", re.I)
# value first: "100mA peak", "~250mA Wi-Fi peaks". "max" is excluded here on
# purpose — "5µA maximum in shutdown" is a floor, not a peak.
_P_BEFORE = re.compile(
    rf"{_I}((?:\s+[A-Za-z-]+){{0,2}})\s+(?:peak|burst|surge|inrush)s?", re.I)


def _ua(num, unit):
    return float(re.sub(r"[~≈<\s]", "", num)) * _IUNIT[unit.lower()]


def parse_peak_ua(pwr_text):
    """`pwr` -> an explicitly stated peak/burst draw in µA, or None.

    Only fires when the text marks the figure peak/burst/surge/inrush/max.
    "1mA active, 750µA conv" has no peak and returns None; "20mA peak" is
    20000.0. Figures qualified by sleep/standby/idle are rejected — a maximum
    shutdown current is not a peak.
    """
    t = (pwr_text or "").strip()
    if not t:
        return None
    m = _P_AFTER.search(t)
    if m and not _SLEEPY.search(m.group(1)):
        return _ua(m.group(2), m.group(3))
    m = _P_BEFORE.search(t)
    if m and not _SLEEPY.search(m.group(3)):
        return _ua(m.group(1), m.group(2))
    return None


# --------------------------------------------------------------------------- bus shape

# When a part offers several buses, this is the order you would actually wire it
# in: shareable and addressable first, point-to-point and exotic last.
IFACE_PRECEDENCE = ["I2C", "SPI", "UART", "1-Wire", "I2S", "RS-485", "CAN",
                    "Analog", "Pulse", "Digital", "PWM", "4-20mA", "Camera",
                    "Radio", "USB", "Builtin"]

# Buses whose device count is not set by a per-device select line.
_NO_CS = {"I2C", "1-Wire", "UART", "RS-485", "CAN", "Analog", "Pulse",
          "Digital", "PWM", "4-20mA", "Builtin"}

# Buses that carry logic levels an ESP32 GPIO either can or cannot touch.
DIGITAL_BUSES = {"I2C", "SPI", "UART", "1-Wire", "I2S", "Digital", "Pulse", "PWM"}
ISOLATED_BUSES = {"RS-485", "CAN", "4-20mA"}
UNADDRESSED_BUSES = {"Analog", "Pulse", "PWM", "Digital", "4-20mA"}


def derive_iface_primary(iface_list):
    """The one bus you wire. Single entry wins; several fall to IFACE_PRECEDENCE."""
    ifs = [i for i in (iface_list or []) if i in IFACE_PRECEDENCE]
    if not ifs:
        return None
    if len(ifs) == 1:
        return ifs[0]
    return min(ifs, key=IFACE_PRECEDENCE.index)


def derive_cs_pins(iface_primary):
    """Select lines beyond the shared bus. None where it genuinely varies."""
    if iface_primary in _NO_CS:
        return 0
    if iface_primary == "SPI":
        return 1
    return None                       # I2S, Camera, Radio, USB — depends on the part


# --------------------------------------------------------------------------- addressing

_ADDR_HEX = re.compile(r"0x([0-9A-Fa-f]{2})")
_ADDR_RANGE = re.compile(r"0x([0-9A-Fa-f]{2})\s*[-–]\s*0x([0-9A-Fa-f]{2})")
_STRAP = re.compile(
    r"\bADDR\b|\bAD0\b|\bSA0\b|\bSDO\b|\bCSB\b|\bASEL\b|\bA0\b|\bA1\b|\bA2\b"
    r"|jumper|solder|strap|address resistor|pin-selectable|address pins?"
    r"|\bpins?\b|\btied\b", re.I)
_STRAP_DENIED = re.compile(
    r"\bno\s+address[-\s](?:select\s+)?pins?\b|\bnot\s+strappable\b"
    r"|\bnot\s+changeable\b|\bno\s+address\s+pins?\b", re.I)
_PROGRAMMABLE = re.compile(
    r"reprogrammable|re-addressable|software-settable|software-changeable"
    r"|software.settable|changeable|configurable|settable|by command|at runtime"
    r"|in the module firmware", re.I)
# 2-4 addresses only count as alternatives when the text presents them as such.
_ALTERNATIVES = re.compile(r"/|\bor\b|default|[-–]", re.I)


def _i2c_addresses(text):
    """Every distinct 7-bit address the text names, ranges expanded."""
    found = {int(h, 16) for h in _ADDR_HEX.findall(text)}
    for lo, hi in _ADDR_RANGE.findall(text):
        a, b = int(lo, 16), int(hi, 16)
        if a <= b:
            found |= set(range(a, b + 1))
    return found


def derive_addr_mode(record):
    """How the device is selected on its bus. None wherever the record is silent."""
    primary = record.get("iface_primary") or derive_iface_primary(record.get("iface"))
    if primary == "1-Wire":
        return "ROM-unique"
    if primary == "SPI":
        return "ChipSelect"
    if primary in UNADDRESSED_BUSES:
        return "NotAddressed"
    if primary != "I2C":
        return None                   # UART, I2S, Camera, Radio, CAN, RS-485, USB
    t = (record.get("i2c_addr") or "").strip()
    if not t:
        return None
    addrs = _i2c_addresses(t)
    denied = bool(_STRAP_DENIED.search(t))
    if not denied and _STRAP.search(t):
        return "Strappable"
    if not denied and 2 <= len(addrs) <= 4 and _ALTERNATIVES.search(t):
        return "Strappable"
    if _PROGRAMMABLE.search(t) or len(addrs) >= 5:
        return "Programmable"
    if len(addrs) == 1:
        return "Fixed"
    return None


# --------------------------------------------------------------------------- levels

def derive_level_shift(record):
    """What goes between the part and a GPIO. Never derives Divider or
    Analog-front-end — deciding those needs the signal, not the bus."""
    primary = record.get("iface_primary") or derive_iface_primary(record.get("iface"))
    if primary in ISOLATED_BUSES or "Mains" in (record.get("hazard") or []):
        return "Isolator"
    safe = record.get("logic_3v3")
    if safe is None or primary not in DIGITAL_BUSES:
        return None
    return "Direct" if safe is True else "Shifter"


def derive_logic_v(record):
    """The signal-line logic level, but only in the two unarguable cases."""
    safe = record.get("logic_3v3")
    if safe is None:
        return None
    lo, hi = record.get("v_min"), record.get("v_max")
    if lo is None or hi is None:
        lo, hi = parse_volts(record.get("v"))
    if lo is None or hi is None:
        return None
    if safe is True and lo <= 3.3 <= hi:
        return "3.3V"
    if safe is False and lo == hi == 5.0:
        return "5V TTL"
    return None


# --------------------------------------------------------------------------- self-check

DERIVED_FIELDS = ["iface_primary", "v_min", "v_max", "logic_v", "level_shift",
                  "addr_mode", "cs_pins", "i_peak_ua", "rate_hz"]

# The whole field set the loader guarantees is present on every record. The last
# two have no derivation at all — they are authored in data/enrich_iface.py or
# they are None.
AUTHORED_ONLY_FIELDS = ["esp32_driver", "driver_status"]
IFACE_FIELDS = DERIVED_FIELDS + AUTHORED_ONLY_FIELDS


def derive_all(record):
    """Every derivable field for one record, as a dict. Order matters: the bus
    and the supply range are derived first, then the things that depend on them."""
    out = {}
    out["iface_primary"] = derive_iface_primary(record.get("iface"))
    out["v_min"], out["v_max"] = parse_volts(record.get("v"))
    out["cs_pins"] = derive_cs_pins(out["iface_primary"])
    out["i_peak_ua"] = parse_peak_ua(record.get("pwr"))
    out["rate_hz"] = parse_rate_hz(record.get("rate"))
    seen = dict(record)
    seen.update({k: v for k, v in out.items() if v is not None})
    out["addr_mode"] = derive_addr_mode(seen)
    out["level_shift"] = derive_level_shift(seen)
    out["logic_v"] = derive_logic_v(seen)
    return out


def _self_check():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    import loader

    records, _ = loader.load_all(persist_ids=False)
    n = len(records)
    print(f"iface_derive self-check over {n} records\n")
    counts = {f: 0 for f in DERIVED_FIELDS}
    for r in records:
        for f, v in derive_all(r).items():
            if v is not None:
                counts[f] += 1
    for f in DERIVED_FIELDS:
        print(f"  {f:<14} {counts[f]:>4}/{n}")

    print("\n  sanity — volts")
    bad = [(r["id"], r.get("v"), parse_volts(r.get("v")))
           for r in records
           if parse_volts(r.get("v"))[0] is not None
           and not (V_LOW <= parse_volts(r.get("v"))[0]
                    <= parse_volts(r.get("v"))[1] <= V_HIGH)]
    print(f"    {len(bad)} out-of-range voltages {bad[:3]}")
    print("\n  sanity — rate")
    bad = [(r["id"], r.get("rate"), parse_rate_hz(r.get("rate")))
           for r in records
           if parse_rate_hz(r.get("rate")) is not None
           and not (0 < parse_rate_hz(r.get("rate")) < RATE_MAX)]
    print(f"    {len(bad)} out-of-range rates {bad[:3]}")

    print("\n  spot-checks (real strings from the catalog)")
    for text in ["3.3-5V", "3.3V", "1.7-3.6V", "5-24V", "2.7-5.5V", "3V3",
                 "2.5 to 3.6 V", "3.3V or 5V", "any (divider)", "3.3/5V versions",
                 "Mains", "24VDC", "±15V dual supply", "5V cycled",
                 "Dry contact — switch 3.3V through it, nothing more",
                 "1.71-3.6V VDD, 1.08-3.6V VDDIO"]:
        print(f"    v     {text!r:<52} -> {parse_volts(text)}")
    for text in ["125Hz", "1 kHz", "up to 200 Hz", "Max 8kHz", "1 sample/s",
                 "one reading every 2s", "1 reading / 5 s", "8-860 SPS",
                 "12.5Hz to 800Hz ODR", "Up to 400Hz ODR", "0.5-64Hz",
                 "240MHz dual-core", "Varies", "Continuous", "~1 Hz",
                 "Up to 6.66 kHz ODR on accel and gyro; 9kB FIFO",
                 "Instant - but debounce it", "20 Hz"]:
        print(f"    rate  {text!r:<52} -> {parse_rate_hz(text)}")
    for text in ["1mA active, 750µA conv", "20mA peak", "<60mA peak",
                 "640µA typical in continuous conversion, 5µA maximum in shutdown",
                 "~180mA streaming, peaks over 300mA",
                 "14.5µA at maximum performance; 160nA sleep"]:
        print(f"    peak  {text!r:<52} -> {parse_peak_ua(text)}")


if __name__ == "__main__":
    _self_check()
