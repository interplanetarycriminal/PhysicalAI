# ESP32 Sensor Universe (v5)

The successor to `esp32_capability_map_v4_world`. v4 mapped what the ESP32 **chip** can do
(73 platform capabilities). v5 maps what the **world around it** can sense:

- **238 sensors** across **32 categories** — each with what it measures, how it works in
  plain English, interface, voltage, typical price, difficulty, power draw, key specs &
  gotchas, where to buy, popular boards, library support, common uses, an invention spark,
  pairing suggestions and theme tags.
- **16 invention themes** — creative territories framed as questions.
- **12×12 synergy matrix** — which sensing worlds combine explosively, with worked examples.
- **41 invention seeds** — fully-specified project concepts with BOM costs and markets.
- **Buying guide** — 24 vendors with regions and honest notes, plus shopping wisdom.
- The original v4 ESP32 capability map, cleaned (mojibake fixed) and preserved.

## Build

```bash
pip install openpyxl
python3 build_workbook.py            # writes esp32_sensor_universe_v5.xlsx
```

## Editing / extending

All content lives in `data/`:

| File | Contents |
|---|---|
| `part1…part10_*.py` | Sensor entries (Python dicts — see field key in part1) |
| `meta.py` | Vendors, themes, category guide, synergy groups & ratings |
| `seeds.py` | Invention seed projects |
| `esp32_capabilities.json` | The v4 capability map (extracted & cleaned) |

Add a sensor by appending a dict to any part file (or a new `part11_*.py` registered in
`build_workbook.py`). The builder validates category names, theme tags and vendor codes,
sorts everything, assigns IDs and rebuilds all derived sheets (counts, dashboard, themes)
automatically.

Prices are typical hobby-breakout street prices and drift over time; treat them as tiers,
not quotes.
