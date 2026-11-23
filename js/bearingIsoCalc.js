'use strict';

/**
 * ISO Industrial Bearing Engineering Reference Calculations (JavaScript / Node.js, zero dependencies)
 * Maintained by ZQM Bearings Technical Team (https://www.zqmbearings.com/tools/)
 *
 * Implements standard ISO engineering reference formulas:
 *  - ISO 281 Basic Rating Life (L10, L10h) & reverse required dynamic rating C_req
 *  - ISO 15 series-locked tapered bore ratio check (1:12 K vs. 1:30 K30)
 *  - Relubrication grease quantity (0.005*D*B / 0.002*D*B) & speed factor (n*dm)
 *  - Steel shaft axial thermal expansion (dL = alpha * L * dT)
 */

const STEEL_ALPHA_PER_C = 11.5e-6;
const RELIABILITY_A1 = { '90': 1.0, '95': 0.64, '96': 0.55, '97': 0.47, '98': 0.37, '99': 0.25 };

function computeIso281Life({
  family,
  crKn,
  frKn,
  rpm,
  faKn = 0,
  c0Kn = 0,
  e = 0.30,
  y1 = 2.0,
  y2 = 3.0,
  y0 = 2.0,
  reliability = '90',
  dMm = 0,
  odMm = 0,
  widthMm = 0,
}) {
  if (!(crKn > 0) || !(rpm > 0)) throw new Error('crKn and rpm must be positive');
  if (frKn < 0 || faKn < 0) throw new Error('Loads cannot be negative');

  const fam = String(family || '').toLowerCase().trim();
  const warnings = [];
  const isBall = ['dgbb', 'acbb', 'qjf', 'sabb', 'tbb'].includes(fam);
  const exponentP = isBall ? 3.0 : 10.0 / 3.0;

  let P = 0;
  let P0 = 0;
  const ratio = frKn > 0 ? faKn / frKn : Infinity;

  if (fam === 'srb') {
    P = ratio <= e ? frKn + y1 * faKn : 0.67 * frKn + y2 * faKn;
    P0 = frKn + y0 * faKn;
  } else if (fam === 'trb') {
    P = ratio <= e ? frKn : 0.4 * frKn + y2 * faKn;
    P0 = Math.max(frKn, 0.5 * frKn + y0 * faKn);
  } else if (fam === 'crb') {
    P = frKn;
    P0 = frKn;
    if (frKn > 0 && faKn > 0.1 * frKn) warnings.push('crb_axial_limit');
  } else if (fam === 'ts') {
    if (!(faKn > 0)) throw new Error('Thrust SRB requires positive faKn');
    P = faKn + 1.2 * frKn;
    P0 = faKn + 2.7 * frKn;
    if (frKn > 0.55 * faKn) warnings.push('ts_radial_limit');
    warnings.push('ts_oil_bath');
  } else if (fam === 'acbb') {
    P = ratio <= e ? frKn : 0.35 * frKn + y2 * faKn;
    P0 = Math.max(frKn, 0.5 * frKn + y0 * faKn);
  } else if (fam === 'dgbb') {
    P = ratio <= e ? frKn : 0.56 * frKn + y2 * faKn;
    P0 = Math.max(frKn, 0.6 * frKn + 0.5 * faKn);
  } else {
    throw new Error(`Unsupported family: ${family}`);
  }

  const l10Millions = Math.pow(crKn / P, exponentP);
  const l10hHours = (l10Millions * 1e6) / (60 * rpm);
  const a1 = RELIABILITY_A1[String(reliability)] || 1.0;
  const dmMm = dMm > 0 && odMm > dMm ? (dMm + odMm) / 2 : 0;
  const ndm = rpm * dmMm;
  const greaseCenterG = fam !== 'ts' && odMm > 0 && widthMm > 0 ? 0.005 * odMm * widthMm : 0;
  const greaseSideG = fam !== 'ts' && odMm > 0 && widthMm > 0 ? 0.002 * odMm * widthMm : 0;

  return {
    family: fam,
    equivalentLoadKn: P,
    exponentP,
    l10Millions,
    l10hHours,
    lnaHours: l10hHours * a1,
    staticSafetyS0: c0Kn > 0 && P0 > 0 ? c0Kn / P0 : null,
    cReq20khKn: P * Math.pow((20000 * 60 * rpm) / 1e6, 1 / exponentP),
    dmMm,
    ndm,
    greaseCenterG,
    greaseSideG,
    warnings,
  };
}

function detectIso15Taper(designation) {
  const clean = String(designation || '').replace(/\s+/g, '').toUpperCase();
  const m = clean.match(/^(222|223|230|231|232|239|240|241)/);
  if (!m) return { series: 'other', taperRatio: 'cylindrical_or_drawing' };
  const series = m[1];
  const isWide = series === '240' || series === '241';
  if (isWide) {
    if (clean.includes('K30')) return { series, taperRatio: '1:30', suffix: 'K30' };
    if (/K(?!30)/.test(clean)) return { series, taperRatio: 'INVALID_K_ON_240_241', suffix: 'K' };
    return { series, taperRatio: 'cylindrical', suffix: '' };
  }
  if (clean.includes('K30')) return { series, taperRatio: 'INVALID_K30_ON_1_12', suffix: 'K30' };
  if (clean.includes('K')) return { series, taperRatio: '1:12', suffix: 'K' };
  return { series, taperRatio: 'cylindrical', suffix: '' };
}

function computeShaftThermalExpansion(spanMm, deltaTC, alpha = STEEL_ALPHA_PER_C) {
  if (spanMm < 0) throw new Error('spanMm cannot be negative');
  const deltaLMm = alpha * spanMm * deltaTC;
  return { spanMm, deltaTC, alphaPerC: alpha, deltaLMm, deltaLUm: deltaLMm * 1000 };
}

module.exports = {
  STEEL_ALPHA_PER_C,
  computeIso281Life,
  detectIso15Taper,
  computeShaftThermalExpansion,
};
