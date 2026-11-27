import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from bearing_iso_calc import (
    compute_iso281_life,
    compute_relubrication_grease,
    compute_shaft_thermal_expansion,
    compute_iso286_fit,
    detect_iso15_taper,
)


class TestBearingIsoCalc(unittest.TestCase):
    def test_srb_23064_life_and_grease(self):
        r = compute_iso281_life(
            family="srb", cr_kn=1960, c0_kn=3850, fr_kn=200, fa_kn=20, rpm=400,
            e=0.23, y1=2.9, y2=4.4, y0=2.8, d_mm=320, od_mm=480, width_mm=121,
        )
        self.assertAlmostEqual(r.equivalent_load_kn, 258.0, places=3)
        self.assertAlmostEqual(r.exponent_p, 10.0 / 3.0, places=6)
        self.assertAlmostEqual(r.grease_center_g, 290.4, places=1)
        self.assertAlmostEqual(r.grease_side_g, 116.16, places=2)
        self.assertEqual(r.ndm, 160000.0)

    def test_thrust_srb_29434_oil_bath_and_radial_guardrail(self):
        r = compute_iso281_life(
            family="ts", cr_kn=1680, c0_kn=5800, fr_kn=200, fa_kn=300, rpm=400,
            d_mm=170, od_mm=340, width_mm=103,
        )
        self.assertAlmostEqual(r.equivalent_load_kn, 540.0, places=3)
        self.assertEqual(r.grease_center_g, 0.0)
        self.assertTrue(any("ts_radial_limit" in w for w in r.warnings))
        self.assertTrue(any("ts_oil_bath" in w for w in r.warnings))

    def test_acbb_40deg_ball_exponent(self):
        r = compute_iso281_life(
            family="acbb", cr_kn=289, c0_kn=340, fr_kn=20, fa_kn=40, rpm=1500,
            e=1.14, y2=0.57, y0=0.26, d_mm=150, od_mm=320, width_mm=65,
        )
        self.assertEqual(r.exponent_p, 3.0)
        self.assertAlmostEqual(r.equivalent_load_kn, 0.35 * 20 + 0.57 * 40, places=4)

    def test_iso15_taper_separation(self):
        self.assertEqual(detect_iso15_taper("23064 CAK/W33")["taper_ratio"], "1:12")
        self.assertEqual(detect_iso15_taper("24164 CAK30/W33")["taper_ratio"], "1:30")
        self.assertEqual(detect_iso15_taper("24164 CAK/W33")["taper_ratio"], "INVALID_K_ON_240_241")
        self.assertEqual(detect_iso15_taper("23244 CAK30/W33")["taper_ratio"], "INVALID_K30_ON_1_12")

    def test_shaft_thermal_expansion_paper_dryer(self):
        res = compute_shaft_thermal_expansion(4500, 55)
        self.assertAlmostEqual(res["delta_l_mm"], 2.84625, places=4)

    def test_relubrication_exclusions(self):
        self.assertFalse(compute_relubrication_grease(75, 35, "GE50ES-2RS")["applicable"])
        self.assertFalse(compute_relubrication_grease(340, 103, "29434")["applicable"])
        g = compute_relubrication_grease(400, 144, "23244 CA/W33")
        self.assertTrue(g["applicable"])
        self.assertEqual(g["center_groove_g"], 288.0)

    def test_verified_dataset_schema(self):
        data = json.loads((ROOT / "data" / "verified-heavy-bearings.json").read_text("utf-8"))
        self.assertEqual(len(data["models"]), 16)
        qjf = next(m for m in data["models"] if m["designation"] == "QJF1064X1MB")
        self.assertEqual(qjf["D_mm"], 479.5)


    def test_iso286_shaft_and_housing_fits(self):
        s_m6 = compute_iso286_fit(150, "m6")
        self.assertEqual((s_m6["upper_dev_um"], s_m6["lower_dev_um"]), (40, 15))
        self.assertEqual((s_m6["max_mm"], s_m6["min_mm"]), (150.04, 150.015))
        s_n6 = compute_iso286_fit(320, "n6")
        self.assertEqual((s_n6["upper_dev_um"], s_n6["lower_dev_um"]), (73, 37))
        h_h7 = compute_iso286_fit(280, "H7")
        self.assertEqual((h_h7["upper_dev_um"], h_h7["lower_dev_um"]), (52, 0))
        h_k7 = compute_iso286_fit(390, "K7")
        self.assertEqual((h_k7["upper_dev_um"], h_k7["lower_dev_um"]), (17, -40))


if __name__ == "__main__":
    unittest.main()
