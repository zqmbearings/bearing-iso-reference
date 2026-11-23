# ISO 281 Bearing Life, Tapered Bore (K vs K30) & Lubrication Calculator — ZQM Bearings Reference Library

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3](https://img.shields.io/badge/Python-3.8%2B-3776ab.svg)](python/bearing_iso_calc.py)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933.svg)](js/bearingIsoCalc.js)

Zero-dependency **Python 3** and **JavaScript (Node.js)** engineering reference implementations for **ISO 281 bearing life calculation (`L10` / `L10h` / `C_req`)**, **ISO 15 tapered bore ratio validation (`1:12 K` vs. `1:30 K30`)**, **bearing relubrication grease quantity (`G = 0.005·D·B` / `0.002·D·B`) & speed factor (`n·dm`)**, and **steel shaft axial thermal expansion (`ΔL = α · L · ΔT`)** — maintained by the **[ZQM Bearings](https://www.zqmbearings.com/)** Technical Team.

> **Prefer a free interactive browser calculator (no login required)?**  
> Launch **[ZQM Bearing Tools](https://www.zqmbearings.com/tools/)** or browse **6,377+ verified designations (`d = 20–1,700 mm`)** in the **[ZQM Online Bearing Catalog](https://www.zqmbearings.com/catalog/)**.

---

## Core Engineering Capabilities

1. **ISO 281 Basic Rating Life Calculator (`L10`, `L10h`, `Lna`, Reverse `C_req`)**
   - Supports **Spherical Roller (`srb`)**, **Tapered Roller (`trb`)**, **Cylindrical Roller (`crb`)**, **Spherical Roller Thrust (`293/294 ts`, enforcing `P = Fa + 1.2 Fr` & flagging `Fr > 0.55 Fa`)**, **40° / 25° / 15° Angular Contact Ball (`acbb`)**, and **Deep Groove Ball (`dgbb`)** bearings.
2. **ISO 15 Tapered Bore Validator (`1:12 K` vs. `1:30 K30`)**
   - Prevents costly overhaul mismatches by enforcing ISO 15 series-locked taper geometry: `222 / 223 / 230 / 231 / 232 / 239` → **`1:12 (K)`**, whereas wide heavy-duty `240 / 241` → **`1:30 (K30)`**.
3. **Bearing Relubrication Grease Formula (`0.005·D·B` / `0.002·D·B`) & Speed Factor (`n·dm`)**
   - Computes center/groove (`0.005 × D × B`) and side (`0.002 × D × B`) relubrication baselines while explicitly flagging **oil-bath / circulating oil** for `292/293/294` thrust spherical roller bearings and excluding sliding spherical plain (`GE`) bearings.
4. **Steel Shaft Axial Thermal Expansion (`ΔL = α · L · ΔT`)**
   - Calculates shaft elongation (`α = 11.5 × 10⁻⁶ /°C`) to verify non-locating end float on steam-heated paper mill drying cylinders, hot gearboxes, and petrochemical pumps.
5. **Catalog-Verified Heavy Industrial Bearing Dataset (`data/verified-heavy-bearings.json`)**
   - Machine-readable JSON dataset covering 16 flagship heavy-duty designations: `23064 CA/W33`, `23164 CA/W33`, `24056 CA/W33`, `24164 CA/W33`, `23244 CA/W33`, `23264 CA/W33`, `240/500 CAF3/W33`, `29426`, `29434`, `7326BM`, `7330BM`, `NU2330EM`, `6330M`, `32244`, special `-0.5 mm` OD `QJF1064X1MB` (`479.5 mm`), and four-row rolling mill `FCDP3248195/YA3`.

---

## Quick Start

### Python 3 (Zero Dependencies)

```python
from python.bearing_iso_calc import (
    compute_iso281_life,
    compute_shaft_thermal_expansion,
    detect_iso15_taper,
)

# Paper mill drying cylinder 23064 CA/W33 (320 x 480 x 121 mm, Cr = 1960 kN)
res = compute_iso281_life(
    family="srb", cr_kn=1960, c0_kn=3850, fr_kn=200, fa_kn=20, rpm=400,
    e=0.23, y1=2.9, y2=4.4, y0=2.8, d_mm=320, od_mm=480, width_mm=121,
)
print(f"L10h = {res.l10h_hours:,.0f} h | Grease (0.005*D*B) = {res.grease_center_g:.0f} g | n*dm = {res.ndm:,.0f}")

# Verify ISO 15 taper (241 series = 1:30 K30) & 4,500 mm dryer axial growth at ΔT = 55 °C
print(detect_iso15_taper("24164 CAK30/W33"))
print(compute_shaft_thermal_expansion(span_mm=4500, delta_t_c=55))
```

### JavaScript / Node.js (Zero Dependencies)

```js
const { computeIso281Life, detectIso15Taper, computeShaftThermalExpansion } = require('./js/bearingIsoCalc');

// Petrochemical process pump 7330BM (40° angular contact, e = 1.14)
const life = computeIso281Life({
  family: 'acbb', crKn: 289, c0Kn: 340, frKn: 20, faKn: 40, rpm: 1500,
  e: 1.14, y2: 0.57, y0: 0.26, dMm: 150, odMm: 320, widthMm: 65,
});
console.log({ L10h: Math.round(life.l10hHours), ndm: life.ndm });
console.log(detectIso15Taper('23064 CAK/W33'));
console.log(computeShaftThermalExpansion(4500, 55));
```

### Run Automated Unit Tests

```bash
python -m unittest discover -s tests -v
node tests/test_js_calc.js
```

---

## Free Interactive Online Tools, Catalog & Technical Guides

| Resource | What It Covers | Direct Link |
| :--- | :--- | :--- |
| **ISO 281 Life & Relubrication Calculator** | 43 verified presets, L10h, reverse C_req, `0.005·D·B` grease & `n·dm` | [Launch Calculator](https://www.zqmbearings.com/tools/bearing-life-calculator/) |
| **Tapered Bore & Thermal Growth Tool** | `1:12 K` vs `1:30 K30`, ISO 5753 C3/C4, hollow shaft, `ΔL = α·L·ΔT` | [Launch Calculator](https://www.zqmbearings.com/tools/tapered-bore-clearance-calculator/) |
| **Bearing Suffix Decoder** | `CA/W33`, `W20`, `2RSH/LLU/DDU`, `ECJ`, `VL0241`, `-0.5 mm` QJF, 130+ links | [Launch Decoder](https://www.zqmbearings.com/tools/bearing-suffix-decoder/) |
| **Online Bearing Catalog** | 6,377+ verified designations (`d = 20–1,700 mm`), metric/imperial & BOM matcher | [Browse Catalog](https://www.zqmbearings.com/catalog/) |
| **Paper Mill Dryer Bearing Guide** | Steam-heated C4 thermal clearance budget, `ΔL` float & 2D CAD schematic | [Read Guide](https://www.zqmbearings.com/blog/paper-mill-dryer-c4-bearings/) |
| **Process Pump 40° DB Bearing Guide** | Paired `7326BM/7330BM` DB vs DF thrust & `NU2330EM` radial-end guide | [Read Guide](https://www.zqmbearings.com/blog/petrochemical-pump-db-df-bearings/) |
| **Heavy-Industry Bearing Solutions** | 9 core heavy-duty sectors (mining, steel mills, cement, paper, petrochemical) | [Explore Industries](https://www.zqmbearings.com/industries/) |

---

## Engineering Disclaimer

Formulas and sample catalog parameters are published under the MIT License for engineering reference only. Nominal ISO boundary dimensions do not guarantee direct brand interchangeability; always confirm bore taper, internal clearance (`CN/C3/C4`), shaft/housing fits, cage execution, and lubrication requirements against OEM drawings prior to procurement. For technical verification or factory-direct quotes, visit [ZQM Bearings Contact](https://www.zqmbearings.com/contact/).
