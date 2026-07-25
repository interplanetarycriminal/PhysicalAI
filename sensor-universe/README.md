# ESP32 Sensor Universe — v6, *The Invention Atlas*

A reference and invention instrument for building with sensors on the ESP32.

Lineage: **v4** mapped what the ESP32 *chip* can do (73 platform capabilities).
**v5** mapped what the *world* can sense (238 sensors). **v6** adds the layer that
turns a catalog into an instrument.

## The idea

A sensor never measures what you actually want to know. It measures a physical
**proxy**. The invention lives in the mapping:

| The part measures | The invention infers |
|---|---|
| A load cell measures grams | *the beehive is about to swarm* |
| A barometer measures hPa | *a door opened on the third floor* |
| A CT clamp measures amps | *Grandma made tea this morning — she's OK* |

v5 had the left column. v6 makes the right column structured, searchable data —
because two facts about it are generative:

- **One inference has many routes.** "Is someone in the room?" → PIR, mmWave,
  thermal array, ToF, CO2 rise, Wi-Fi CSI, floor vibration, or a 50c reed switch.
  They differ in cost, privacy, power and what fools them. *Choosing the route is
  the design act.*
- **One sensor serves many inferences.** One accelerometer yields tilt, impact,
  vibration spectra, step count, sleep movement, machine load, seismic events and
  knock signatures. *Seeing all of them is the creative act.*

## Build

```bash
pip install -r requirements.txt
python3 validate.py            # hard gate — must pass
python3 build_workbook.py      # writes esp32_sensor_universe_v6.xlsx
```

`validate.py --strict` additionally requires the semantic fields (modality,
phenomena, contact, privacy) on every record. That is the release gate.

## Layout

| Path | Contents |
|---|---|
| `data/schema.py` | **The contract.** 36 fields, 11 enums, difficulty rubric, derived-value helpers |
| `data/vocab.py` | Categories, themes, phenomena, inferences, constraints, fusion patterns |
| `data/part*.py` | Sensor records |
| `data/actuators.py`, `glue.py`, `boards.py` | The other three catalogs |
| `data/enrich.py` | Overlay of schema-v2 fields keyed by stable ID |
| `data/seeds.py` | Invention seeds, linked to catalog IDs so BOMs compute |
| `data/archetypes.py`, `inference_notes.py` | Authored analytical content |
| `data/ids.json` | **Stable IDs.** Assigned once, never renumbered |
| `data/loader.py` | Load → migrate → assign IDs → enrich → derive |
| `sheet_lib.py` | Shared visual system for every sheet |
| `ingest.py` | Validates and merges authored fragments into data modules |
| `WRITING_GUIDE.md` | The authoring contract |

## Rules

1. **Derived values are never authored.** Price tier, power class and BOM totals
   are computed, so they cannot drift out of sync with their source.
2. **IDs are frozen.** v5 generated them from sort order at build time, so adding
   one sensor renumbered everything downstream and nothing could cite them.
3. **Anything filterable is an enum.** v5 had 165 distinct free-text power strings
   and 101 interface strings across 238 records, which made both "show me every
   I²C sensor" and "compute a battery budget" impossible to answer.
4. **`hazard` is mandatory where the prose implies one.** The validator greps for
   mains, high voltage, heated elements, lasers, UV-C and flammable gas, and fails
   the build if the field is empty. This check exists because v5 recommended
   siting a heated gas sensor inside an LPG locker.
5. **Never invent a SKU.** v5 cited an Adafruit product number for a breakout that
   does not exist. If it can't be confirmed, describe the board generically.

## Accuracy

Prices are **tiers, not quotes**, and they drift. Every record carries a
`confidence` flag (`Verified` / `High` / `Estimate`) and an `as_of` date. Specs
come from datasheets and community experience, not from our bench. The
`Provenance` sheet states all of this in the workbook itself.

For anything life-safety — combustible gas, carbon monoxide, fire, medical — a
certified device is the answer and a hobby sensor is at best a supplement to it.
