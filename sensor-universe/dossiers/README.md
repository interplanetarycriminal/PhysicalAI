# Device-reinvention dossiers

Ten everyday devices whose design has not been seriously rethought since their inventor, taken
apart and rebuilt against the atlas. The method is the same in each: separate what the device
*claims* to detect from the physical quantity it *actually* transduces, take "what fools it"
from the atlas's own `fools` fields rather than from opinion, and then rebuild the function from
catalogued parts that measure the underlying phenomenon instead of a proxy for it. Every part id,
part number, price, quoted field and fusion expression below is checked against `data/loader.py`
and `data/fusion.py`; where a dossier proposes a fusion edge the atlas does not have, it is
labelled `new edge — not in fusion.py`.

## The ten

| # | Incumbent | What it actually measures | Headline thing that fools it | Build | Writer's rating |
| --- | --- | --- | --- | --- | --- |
| [01](01-ionisation-smoke-alarm.md) | Ionisation smoke alarm | Ion-recombination rate in ~1 cm³ of air | Steam and burnt toast — aerosol without combustion | $152 | Strong on diagnosis, weak as a replacement |
| [02](02-bimetal-thermostat.md) | Bimetal room thermostat | Air temperature at one point, inside its own case | Radiant asymmetry: a cold window it cannot see | $125.50 | Strong |
| [03](03-resistive-soil-moisture-probe.md) | Two-nail soil moisture probe | Bulk DC conductivity — salinity × wetness | Fertiliser: a fertigation event makes dry soil read wet | $70 | Strong |
| [04](04-pir-occupancy-sensor.md) | PIR occupancy sensor | The *time derivative* of far-infrared flux | A person sitting still | $105 | Strong |
| [05](05-float-water-meter.md) | Domestic water meter | Cumulative revolutions of one disc, above its dead band | Flow below the disc's starting torque — a running toilet | $121 | Strong on leaks, moderate on metering |
| [06](06-pulse-oximeter.md) | Finger-clip pulse oximeter | A ratio of modulation depths at two wavelengths | Carboxyhaemoglobin — a poisoned patient reads 98 % | $124 | Moderate |
| [07](07-reed-switch-door-sensor.md) | Reed-switch door contact | Magnetic flux through one glass capsule | A magnet held against the reed — the classic bypass | $52.50/door | Strong on security, moderate on door state |
| [08](08-cds-photocell-dusk-to-dawn.md) | CdS dusk-to-dawn head | Photoconductivity of a CdS film vs one resistor | Spectrum, and its own lamp's reflection | $63 | Strong on the sun term, moderate overall |
| [09](09-irrigation-rain-sensor.md) | Cork-disc rain sensor | Linear expansion of a stack of cork discs | Its own drying rate, set by the cup's vents not the soil | $175.50 | Strong on physics, moderate on build |
| [10](10-resistive-leak-detector.md) | Under-sink leak puck | DC conductivity across a 20 mm gap | Water that lands anywhere but those 20 mm | $84 | Strong |

Costs are the dossier's own "Build" figure — sensors plus board plus any actuator — re-added from
the dataset's `usd` fields. Several dossiers also cost a cut-down version: `03` is $70 for the core
four and $142 with the ET₀ tier; `04` names a $43 two-physics minimum.

## The three strongest

Strongest here means the largest gap between what the incumbent can *physically* do and what the
replacement does, weighted by cost and buildability, and discounted where the dossier admits the
win is unproven.

1. **[04 — PIR occupancy sensor](04-pir-occupancy-sensor.md).** The incumbent's central failure is
   not a tuning problem: a pyroelectric element responds to temperature *change*, so a motionless
   person is indistinguishable from an empty room by construction. `S067` LD2410 mmWave, at $5,
   sees chest-wall motion instead and removes the blind spot outright; `S071` Grid-EYE adds an
   absolute thermal channel so the two physics can be required to agree (`presence-two-physics`).
   The decisive part costs $5 and the dossier discounts its own claim least.
2. **[10 — Under-sink leak puck](10-resistive-leak-detector.md).** The puck can only detect water
   that has already arrived at one 20 mm gap on the cabinet floor. Measuring the leak where it
   leaves the system instead — `S138` turbine flow at $5, gated on `S067` presence at $5 — covers
   the whole installation for $10 of parts, and `leak-by-context` is already an edge in the
   dataset. Discounted for the acoustic correlator, which the dossier itself rates low confidence,
   and for needing access to the incoming main.
3. **[03 — Two-nail soil moisture probe](03-resistive-soil-moisture-probe.md).** The only entry
   that replaces the measured *quantity* rather than improving its accuracy: the incumbent reads
   salinity × wetness on DC and electrolyses its own electrodes, while plants respond to matric
   potential. `S186` Watermark ($45) plus a same-depth `S132` ($5) measures the right variable, and
   `et0-station` closes the water balance. Discounted because the Watermark is blind above about
   −10 kPa and takes hours to equilibrate.

## Gaps in the dataset this exercise exposed

Parts the dossiers needed and the atlas does not carry, plus one record defect. Each was checked
against the loaded dataset before being listed here.

- **No smoke-chamber part of either kind.** Neither an ionisation chamber nor a photoelectric
  chamber is catalogued. The nearest physics is laser scattering (`S040`, `S041`, `S294`) and the
  chemiresistive `S026` MQ-2. Dossier 01 is built entirely around that absence.
- **No potentiostat glue record.** `S033` hard-`requires` "A potentiostat front-end (LMP91000, or
  the vendor's ULPSM board)…"; none of the 33 `G0xx` glue records is one. Every electrochemical
  cell in the atlas inherits this hole.
- **No room-scale low-velocity anemometer.** `S177` FS3000 states that "Below about 0.5 m/s,
  natural convection off its own heater dominates and the reading is mush"; `S121`'s cups do
  "nothing at all below the ~0.5-1.4 m/s starting threshold". Indoor draught — a first-order
  comfort term in dossier 02 — is therefore not measurable with any part here.
- **No record for the two-nail resistive probe itself.** `S129` is capacitive and its own `how`
  field defines itself *against* "cheap resistive forks"; the resistive fork has no record, so
  dossier 03 had to reconstruct the incumbent from the gypsum-block and Watermark electrode physics.
- **No cheap potable-water line-pressure sensor.** Domestic mains sits at 40–80 PSI. `S021` MPRLS
  is "0-25 PSI absolute"; the only catalogued part covering the range is `S254`, a $150 4-20 mA
  loop transmitter. Dossier 05 drops its pressure channel for this reason.
- **No optical rain sensor as a record.** The Hydreon RG-15 class appears only inside `S123`'s
  `substitutes` prose. `S123`'s tipping bucket "always under-reads, never over", and dossier 09 has
  no alternative to offer.
- **No outdoor-rated presence sensor.** All 16 records in the `Presence & Occupancy` category are
  `environment: ['Indoor']`. Dossier 08 proposes an outdoor streetlight controller and has to
  concede that the housing is the builder's problem.
- **No pickup for an existing utility meter.** `S138`'s `substitutes` recommends exactly this —
  "an optical or magnetometer pickup on the utility meter's existing spinning disc is free and does
  not touch the plumbing" — and no such record exists to build it from.
- **`S128` is a merged record, by its own admission.** Its `note`: "This record merges a ~$60
  silicon-cell Gravity unit with a ~$225 Apogee SP-110, which are different instruments with
  different accuracy classes and different interfaces." Dossiers 03 and 09 both price the $60 part
  and inherit the ambiguity.
