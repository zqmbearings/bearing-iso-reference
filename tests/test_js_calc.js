'use strict';

const assert = require('assert');
const {
  computeIso281Life,
  detectIso15Taper,
  computeShaftThermalExpansion,
  computeIso286Fit,
} = require('../js/bearingIsoCalc');

// 1. 23064 CA/W33 SRB ISO 281 + Grease + n*dm
const srb = computeIso281Life({
  family: 'srb', crKn: 1960, c0Kn: 3850, frKn: 200, faKn: 20, rpm: 400,
  e: 0.23, y1: 2.9, y2: 4.4, y0: 2.8, dMm: 320, odMm: 480, widthMm: 121,
});
assert(Math.abs(srb.equivalentLoadKn - 258.0) < 1e-6);
assert(Math.abs(srb.greaseCenterG - 290.4) < 0.01);
assert.strictEqual(srb.ndm, 160000);

// 2. 29434 Thrust SRB excludes W33 grease & flags radial limit
const ts = computeIso281Life({
  family: 'ts', crKn: 1680, c0Kn: 5800, frKn: 200, faKn: 300, rpm: 400,
  dMm: 170, odMm: 340, widthMm: 103,
});
assert.strictEqual(ts.greaseCenterG, 0);
assert(ts.warnings.includes('ts_radial_limit'));
assert(ts.warnings.includes('ts_oil_bath'));

// 3. 7330BM 40-deg ACBB ball exponent p=3
const ac = computeIso281Life({
  family: 'acbb', crKn: 289, c0Kn: 340, frKn: 20, faKn: 40, rpm: 1500,
  e: 1.14, y2: 0.57, y0: 0.26, dMm: 150, odMm: 320, widthMm: 65,
});
assert.strictEqual(ac.exponentP, 3);
assert(Math.abs(ac.equivalentLoadKn - (0.35 * 20 + 0.57 * 40)) < 1e-6);

// 4. ISO 15 Taper separation
assert.strictEqual(detectIso15Taper('23064 CAK/W33').taperRatio, '1:12');
assert.strictEqual(detectIso15Taper('24164 CAK30/W33').taperRatio, '1:30');
assert.strictEqual(detectIso15Taper('24164 CAK/W33').taperRatio, 'INVALID_K_ON_240_241');
assert.strictEqual(detectIso15Taper('23244 CAK30/W33').taperRatio, 'INVALID_K30_ON_1_12');

// 5. Steel shaft axial thermal expansion
const te = computeShaftThermalExpansion(4500, 55);
assert(Math.abs(te.deltaLMm - 2.84625) < 1e-5);

// 6. ISO 286 shaft & housing bore tolerances
const fitM6 = computeIso286Fit(150, 'm6');
assert.strictEqual(fitM6.upperDevUm, 40);
assert.strictEqual(fitM6.lowerDevUm, 15);
assert.strictEqual(fitM6.maxMm, 150.04);
const fitK7 = computeIso286Fit(390, 'K7');
assert.strictEqual(fitK7.upperDevUm, 17);
assert.strictEqual(fitK7.lowerDevUm, -40);

console.log('ALL_JS_ISO_TESTS_PASSED: 6/6');
