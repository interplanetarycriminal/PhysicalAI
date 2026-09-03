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

STATUS: the table below is intentionally EMPTY. The plumbing (schema fields,
PHYSQTY vocabulary, loader hook, `px_report.py` quality gate) lands in this
commit; the physics data lands in a later commit, authored by the workers
researching the datasheets. Add entries to `PX` and nothing else changes.

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
# id -> {px_* field: value}. Empty by design; the physics data lands in a later
# commit. See the module docstring for the exact shape of one entry.
PX: dict[str, dict] = {}


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
