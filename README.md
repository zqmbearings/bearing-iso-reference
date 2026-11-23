# ZQM Bearing ISO Engineering Reference (`zqm-bearing-iso-reference`)

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Zero-dependency **Python 3** and **JavaScript (Node.js)** reference implementations of standard ISO industrial rolling-bearing calculations, paired with a catalog-verified heavy-duty bearing JSON dataset.

Maintained by the **[ZQM Bearings](https://www.zqmbearings.com/)** Technical Team.

## What's Included

1. **ISO 281 Basic Rating Life (`L10`, `L10h`, `Lna`) & Reverse `C_req`**
   - Supports Spherical Roller (`srb`), Tapered Roller (`trb`), Cylindrical Roller (`crb`), Spherical Roller Thrust (`ts`, enforcing `P = Fa + 1.2 Fr` and flagging `Fr > 0.55 Fa`), 40°/25°/15° Angular Contact Ball (`acbb`), and Deep Groove Ball (`dgbb`) bearings.
2. **ISO 15 Series-Locked Tapered Bore Validator (`1:12 K` vs. `1:30 K30`)**
   - Automatically distinguishes `222/223/230/231/232/239` (`1:12 K`) from wide `240/241` (`1:30 K30`) and flags invalid taper suffix combinations.
3. **Relubrication Grease Quantity & Speed Factor (`n·dm`) Estimator**
   - Computes center/groove (`G = 0.005 · D · B`) and side (`G = 0.002 · D · B`) relubrication baselines while explicitly flagging oil-bath / circulating oil for `292/293/294` thrust spherical roller bearings and excluding spherical plain (`GE`) bearings.
4. **Steel Shaft Axial Thermal Expansion (`ΔL = α · L · ΔT`)**
   - Verifies axial float margins (`α = 11.5 × 10⁻⁶ /°C`) for non-locating bearings on hot steam dryers, industrial gearboxes, and process pumps.
5. **Verified Heavy-Industry Sample Dataset (`data/verified-heavy-bearings.json`)**
   - 16 catalog-verified large-bore and heavy-duty designations (`23064/23164/24164 CA/W33`, `240/500 CAF3/W33`, `29426/29434`, `7326BM/7330BM`, `NU2330EM`, `6330M`, `32244`, `QJF1064X1MB` `-0.5 mm` special OD, and four-row `FCDP3248195/YA3`).

---

## Quick Start

### Python 3

```python
from python.bearing_iso_calc import (
    compute_iso281_life,
    compute_shaft_thermal_expansion,
    detect_iso15_taper,
)

# 23064 CA/W33 paper drying cylinder spherical roller bearing
res = compute_iso281_life(
    family="srb", cr_kn=1960, c0_kn=3850, fr_kn=200, fa_kn=20, rpm=400,
    e=0.23, y1=2.9, y2=4.4, y0=2.8, d_mm=320, od_mm=480, width_mm=121,
)
print(f"L10h = {res.l10h_hours:,.0f} h | W33 Grease ≈ {res.grease_center_g:.0f} g | n·dm = {res.ndm:,.0f}")

# ISO 15 taper check & 4,500 mm dryer axial thermal expansion at ΔT = 55 °C
print(detect_iso15_taper("24164 CAK30/W33"))
print(compute_shaft_thermal_expansion(span_mm=4500, delta_t_c=55))
```

### Node.js

```js
const { computeIso281Life, detectIso15Taper, computeShaftThermalExpansion } = require('./js/bearingIsoCalc');

const life = computeIso281Life({
  family: 'acbb', crKn: 289, c0Kn: 340, frKn: 20, faKn: 40, rpm: 1500,
  e: 1.14, y2: 0.57, y0: 0.26, dMm: 150, odMm: 320, widthMm: 65,
});
console.log({ L10h: Math.round(life.l10hHours), ndm: life.ndm });
console.log(detectIso15Taper('23064 CAK/W33'));
console.log(computeShaftThermalExpansion(4500, 55));
```

### Run Unit Tests

```bash
python -m unittest discover -s tests -v
node tests/test_js_calc.js
```

---

## Free Online Interactive Bearing Tools & Catalog

Prefer an interactive browser interface with built-in catalog presets, ISO 5753 clearance tables, and suffix decoding?

- **All Engineering Tools**: [ZQM Bearing Tools](https://www.zqmbearings.com/tools/)
- **ISO 281 Life & Relubrication Calculator** (43 verified presets): [Bearing Life Calculator](https://www.zqmbearings.com/tools/bearing-life-calculator/)
- **Tapered Bore (`1:12 K` / `1:30 K30`) & Shaft Thermal Growth Calculator**: [Tapered Bore Clearance Calculator](https://www.zqmbearings.com/tools/tapered-bore-clearance-calculator/)
- **Bearing Suffix Decoder** (130+ linked specifications): [Bearing Suffix Decoder](https://www.zqmbearings.com/tools/bearing-suffix-decoder/)
- **Online Bearing Catalog** (6,377+ verified designations, `d = 20–1,700 mm`): [ZQM Bearing Catalog](https://www.zqmbearings.com/catalog/)
- **Illustrated 2D Engineering Guides**:
  - [Paper Mill Drying Cylinder Bearings: C4 Clearance, Thermal Growth & 230/241 Selection](https://www.zqmbearings.com/blog/paper-mill-dryer-c4-bearings/)
  - [Petrochemical Process Pump Bearings: 40° DB Paired Thrust & Radial End Guide](https://www.zqmbearings.com/blog/petrochemical-pump-db-df-bearings/)
  - [Heavy-Industry Application Hubs](https://www.zqmbearings.com/industries/)

## Engineering Disclaimer

Formulas and sample catalog values are provided for engineering reference under the MIT License. Nominal ISO dimensions do not imply direct brand interchangeability; always verify internal radial/axial clearance, shaft and housing tolerances, cage execution, and lubrication requirements against OEM equipment drawings.
