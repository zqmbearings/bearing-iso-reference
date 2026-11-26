"""ISO Industrial Bearing Engineering Reference Calculations (Python 3, zero dependencies).

Maintained by ZQM Bearings Technical Team (https://www.zqmbearings.com/tools/).
Implements standard reference formulas for:
  - ISO 281 Basic Rating Life (L10, L10h) and reverse required dynamic rating C_req
  - ISO 15 series-locked tapered bore ratio check (1:12 K vs. 1:30 K30)
  - Relubrication grease quantity (0.005*D*B / 0.002*D*B) and speed factor (n*dm)
  - Steel shaft axial thermal expansion (dL = alpha * L * dT)

Disclaimer: Engineering reference calculations only. Always verify shaft/housing fits,
internal clearance groups, lubrication, and tolerances against OEM drawings.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

STEEL_ALPHA_PER_C = 11.5e-6  # ISO carbon/bearing steel linear thermal expansion (/degC)

RELIABILITY_A1: Dict[str, float] = {
    "90": 1.00,
    "95": 0.64,
    "96": 0.55,
    "97": 0.47,
    "98": 0.37,
    "99": 0.25,
}

K30_SERIES = ("240", "241")
K12_SERIES = ("222", "223", "230", "231", "232", "239")


@dataclass(frozen=True)
class LifeResult:
    family: str
    equivalent_load_kn: float
    exponent_p: float
    l10_millions: float
    l10h_hours: float
    lna_hours: float
    static_safety_s0: Optional[float]
    c_req_20kh_kn: Optional[float]
    dm_mm: float
    ndm: float
    grease_center_g: float
    grease_side_g: float
    warnings: List[str]


def compute_iso281_life(
    family: str,
    cr_kn: float,
    fr_kn: float,
    rpm: float,
    fa_kn: float = 0.0,
    c0_kn: float = 0.0,
    e: float = 0.30,
    y1: float = 2.0,
    y2: float = 3.0,
    y0: float = 2.0,
    reliability: str = "90",
    d_mm: float = 0.0,
    od_mm: float = 0.0,
    width_mm: float = 0.0,
) -> LifeResult:
    """Compute ISO 281 basic rating life L10 / L10h, static safety s0, and lubrication cues."""
    if cr_kn <= 0 or rpm <= 0:
        raise ValueError("cr_kn and rpm must be positive")
    if fr_kn < 0 or fa_kn < 0:
        raise ValueError("loads cannot be negative")

    fam = family.lower().strip()
    warnings: List[str] = []
    is_ball = fam in {"dgbb", "acbb", "qjf", "sabb", "tbb"}
    p_exp = 3.0 if is_ball else (10.0 / 3.0)

    if fam == "srb":
        ratio = (fa_kn / fr_kn) if fr_kn > 0 else float("inf")
        p_kn = (fr_kn + y1 * fa_kn) if ratio <= e else (0.67 * fr_kn + y2 * fa_kn)
        p0_kn = fr_kn + y0 * fa_kn
    elif fam == "trb":
        ratio = (fa_kn / fr_kn) if fr_kn > 0 else float("inf")
        p_kn = fr_kn if ratio <= e else (0.4 * fr_kn + y2 * fa_kn)
        p0_kn = max(fr_kn, 0.5 * fr_kn + y0 * fa_kn)
    elif fam == "crb":
        p_kn = fr_kn
        p0_kn = fr_kn
        if fr_kn > 0 and fa_kn > 0.1 * fr_kn:
            warnings.append("crb_axial_limit: Verify rib/locating design (NJ/NUP) for axial load > 0.1*Fr.")
    elif fam == "ts":
        if fa_kn <= 0:
            raise ValueError("Thrust spherical roller bearing (ts) requires positive axial load fa_kn")
        p_kn = fa_kn + 1.2 * fr_kn
        p0_kn = fa_kn + 2.7 * fr_kn
        if fr_kn > 0.55 * fa_kn:
            warnings.append("ts_radial_limit: Fr exceeds 0.55*Fa limit for spherical roller thrust bearings.")
    elif fam == "acbb":
        ratio = (fa_kn / fr_kn) if fr_kn > 0 else float("inf")
        p_kn = fr_kn if ratio <= e else (0.35 * fr_kn + y2 * fa_kn)
        p0_kn = max(fr_kn, 0.5 * fr_kn + y0 * fa_kn)
    elif fam == "dgbb":
        ratio = (fa_kn / fr_kn) if fr_kn > 0 else float("inf")
        p_kn = fr_kn if ratio <= e else (0.56 * fr_kn + y2 * fa_kn)
        p0_kn = max(fr_kn, 0.6 * fr_kn + 0.5 * fa_kn)
    else:
        raise ValueError(f"Unsupported bearing family: {family}")

    if p_kn <= 0:
        raise ValueError("Equivalent dynamic load P must be positive")

    l10_m = math.pow(cr_kn / p_kn, p_exp)
    l10h = (l10_m * 1_000_000.0) / (60.0 * rpm)
    a1 = RELIABILITY_A1.get(str(reliability), 1.0)
    lna = l10h * a1
    s0 = (c0_kn / p0_kn) if (c0_kn > 0 and p0_kn > 0) else None
    c_req_20k = p_kn * math.pow((20_000.0 * 60.0 * rpm) / 1_000_000.0, 1.0 / p_exp)

    dm = ((d_mm + od_mm) / 2.0) if (d_mm > 0 and od_mm > d_mm) else 0.0
    ndm = rpm * dm
    if fam == "ts":
        grease_center = 0.0
        grease_side = 0.0
        warnings.append("ts_oil_bath: 292/293/294 thrust SRBs normally use oil-bath or circulating oil (no W33 groove).")
    elif od_mm > 0 and width_mm > 0:
        grease_center = 0.005 * od_mm * width_mm
        grease_side = 0.002 * od_mm * width_mm
    else:
        grease_center = 0.0
        grease_side = 0.0

    return LifeResult(
        family=fam,
        equivalent_load_kn=p_kn,
        exponent_p=p_exp,
        l10_millions=l10_m,
        l10h_hours=l10h,
        lna_hours=lna,
        static_safety_s0=s0,
        c_req_20kh_kn=c_req_20k,
        dm_mm=dm,
        ndm=ndm,
        grease_center_g=grease_center,
        grease_side_g=grease_side,
        warnings=warnings,
    )


def detect_iso15_taper(designation: str) -> Dict[str, str]:
    """Identify ISO 15 series-locked tapered bore ratio (1:12 K vs. 1:30 K30) or cylindrical bore."""
    clean = re.sub(r"\s+", "", designation.upper())
    m = re.match(r"^(222|223|230|231|232|239|240|241)", clean)
    if not m:
        return {"series": "other", "taper_ratio": "cylindrical_or_drawing", "note": "Check OEM drawing for bore geometry."}
    series = m.group(1)
    if series in K30_SERIES:
        if "K30" in clean:
            return {"series": series, "taper_ratio": "1:30", "suffix": "K30", "note": "ISO 15 1:30 tapered bore (wide 240/241 series)."}
        if re.search(r"K(?!30)", clean):
            return {"series": series, "taper_ratio": "INVALID_K_ON_240_241", "suffix": "K", "note": "Warning: 240/241 standard tapered bore is 1:30 (K30), not 1:12 (K)."}
        return {"series": series, "taper_ratio": "cylindrical", "suffix": "", "note": "Cylindrical bore (tapered variant uses 1:30 K30)."}
    if "K30" in clean:
        return {"series": series, "taper_ratio": "INVALID_K30_ON_1_12", "suffix": "K30", "note": f"Warning: {series} series standard tapered bore is 1:12 (K), not 1:30 (K30)."}
    if "K" in clean:
        return {"series": series, "taper_ratio": "1:12", "suffix": "K", "note": f"ISO 15 1:12 tapered bore ({series} series)."}
    return {"series": series, "taper_ratio": "cylindrical", "suffix": "", "note": "Cylindrical bore (tapered variant uses 1:12 K)."}


def compute_shaft_thermal_expansion(span_mm: float, delta_t_c: float, alpha: float = STEEL_ALPHA_PER_C) -> Dict[str, float]:
    """Calculate steel shaft axial thermal growth dL = alpha * L * dT."""
    if span_mm < 0:
        raise ValueError("span_mm cannot be negative")
    dl_mm = alpha * span_mm * delta_t_c
    return {
        "span_mm": float(span_mm),
        "delta_t_c": float(delta_t_c),
        "alpha_per_c": float(alpha),
        "delta_l_mm": dl_mm,
        "delta_l_um": dl_mm * 1000.0,
    }


def compute_relubrication_grease(od_mm: float, width_mm: float, designation: str = "") -> Dict[str, object]:
    """Calculate reference relubrication grease quantity (0.005*D*B center/groove, 0.002*D*B side).

    Excludes spherical plain (GE) bearings and flags oil-bath for 292/293/294 thrust SRBs.
    """
    code = designation.upper().strip()
    if code.startswith("GE"):
        return {"applicable": False, "reason": "Spherical plain bearing (GE) — follow sliding-contact relubrication rules."}
    if re.match(r"^29[234]", code):
        return {"applicable": False, "reason": "Spherical roller thrust bearing (292/293/294) — oil-bath or circulating oil recommended (no outer-ring W33 groove)."}
    if od_mm <= 0 or width_mm <= 0:
        raise ValueError("od_mm and width_mm must be positive")
    return {
        "applicable": True,
        "center_groove_g": round(0.005 * od_mm * width_mm, 1),
        "side_relub_g": round(0.002 * od_mm * width_mm, 1),
    }


# ISO 286-2:2010 standard tolerances (IT5/IT6/IT7 in um) and shaft/housing deviations (um)
_ISO286_RANGES = (
    (30.0, 50.0),
    (50.0, 80.0),
    (80.0, 120.0),
    (120.0, 180.0),
    (180.0, 250.0),
    (250.0, 315.0),
    (315.0, 400.0),
    (400.0, 500.0),
)

_ISO286_SHAFTS_UM: Dict[str, tuple] = {
    "k5": ((13, 2), (15, 2), (18, 3), (21, 3), (24, 4), (27, 4), (29, 4), (32, 5)),
    "k6": ((18, 2), (21, 2), (25, 3), (28, 3), (33, 4), (36, 4), (40, 4), (45, 5)),
    "m5": ((20, 9), (24, 11), (28, 13), (33, 15), (37, 17), (43, 20), (46, 21), (50, 23)),
    "m6": ((25, 9), (30, 11), (35, 13), (40, 15), (46, 17), (52, 20), (57, 21), (63, 23)),
    "n6": ((33, 17), (39, 20), (45, 23), (52, 27), (60, 31), (66, 34), (73, 37), (80, 40)),
    "p6": ((42, 26), (49, 30), (57, 35), (65, 40), (75, 46), (82, 50), (93, 57), (103, 63)),
}

_ISO286_HOLES_UM: Dict[str, tuple] = {
    "G7": ((34, 9), (40, 10), (47, 12), (54, 14), (75, 29), (84, 32), (93, 36), (103, 40)),
    "H7": ((25, 0), (30, 0), (35, 0), (40, 0), (46, 0), (52, 0), (57, 0), (63, 0)),
    "J7": ((11, -14), (12, -18), (15, -20), (17, -23), (26, -20), (30, -22), (32, -25), (36, -27)),
    "K7": ((17, -8), (20, -10), (23, -12), (27, -13), (13, -33), (16, -36), (17, -40), (18, -45)),
}


def compute_iso286_fit(nominal_mm: float, tolerance_class: str) -> Dict[str, object]:
    """Compute ISO 286-2 upper/lower limit deviations (um) and limits of size (mm) for 30 < D <= 500 mm.

    Supports bearing shaft fits (k5, k6, m5, m6, n6, p6) and housing bore fits (G7, H7, J7, K7).
    """
    if not (30.0 < nominal_mm <= 500.0):
        raise ValueError("nominal_mm must be in (30, 500] mm for ISO 286 heavy bearing fit lookup")
    cls = tolerance_class.strip()
    is_shaft = cls in _ISO286_SHAFTS_UM
    is_hole = cls in _ISO286_HOLES_UM
    if not (is_shaft or is_hole):
        raise ValueError(f"Unsupported ISO 286 tolerance_class: {tolerance_class}")

    idx = next(i for i, (lo, hi) in enumerate(_ISO286_RANGES) if lo < nominal_mm <= hi)
    upper_um, lower_um = (_ISO286_SHAFTS_UM[cls] if is_shaft else _ISO286_HOLES_UM[cls])[idx]
    lo_r, hi_r = _ISO286_RANGES[idx]
    return {
        "nominal_mm": float(nominal_mm),
        "tolerance_class": cls,
        "feature_type": "shaft" if is_shaft else "housing_bore",
        "range_mm": f">{int(lo_r)}..{int(hi_r)}",
        "upper_dev_um": int(upper_um),
        "lower_dev_um": int(lower_um),
        "max_mm": round(nominal_mm + upper_um / 1000.0, 4),
        "min_mm": round(nominal_mm + lower_um / 1000.0, 4),
        "fit_zone_um": int(upper_um - lower_um),
    }
