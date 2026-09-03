"""Authored ESP32 interface fields, keyed by stable part ID.

GENERATED FILE — do not hand-edit. `tools/gen_enrich_iface.py` builds it from
the authored `iface_data_*.json` files and rewrites it wholesale; anything typed
in here by hand is lost on the next run. Edit the JSON, then regenerate.

This is the fourth and last overlay the loader merges, so a value here beats
`enrich_core`, `enrich`, `enrich_manual` and every derivation in
`data/iface_derive.py`. Author only what you have checked against a datasheet or
a real driver; leave the rest out and let the derivation (or an explicit None)
stand. An explicit None here means "checked, could not verify".
"""

ENRICH_IFACE: dict[str, dict] = {}
