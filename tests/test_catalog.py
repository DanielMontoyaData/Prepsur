import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads((ROOT / "gis/sources/sources.json").read_text(encoding="utf-8"))

    def test_six_municipalities_have_sources(self):
        names = {x["municipality"] for x in self.cfg["sources"]}
        for expected in ["Envigado", "Itagüí", "Sabaneta", "La Estrella", "Caldas", "Medellín (sur prioritario)"]:
            self.assertIn(expected, names)

    def test_all_layers_have_valid_ids(self):
        for source in self.cfg["sources"]:
            self.assertTrue(source["service"].startswith("https://"))
            self.assertTrue(source["layers"])
            for layer in source["layers"]:
                self.assertIsInstance(layer["id"], int)
                self.assertIn("theme", layer)

    def test_known_official_layer_ids(self):
        by_id = {x["id"]: {int(y["id"]) for y in x["layers"]} for x in self.cfg["sources"]}
        self.assertEqual(by_id["envigado_pot"], {2, 5, 6, 7})
        self.assertEqual(by_id["itagui_pot"], {7, 8, 9})
        self.assertEqual(by_id["sabaneta_pot"], {5, 7, 8})
        self.assertEqual(by_id["la_estrella_pot"], {4, 5, 6, 7})
        self.assertEqual(by_id["caldas_pot"], {1, 2, 3})
        self.assertEqual(by_id["medellin_dagrd"], {0, 1, 2, 8, 9, 10, 11, 12, 13})

    def test_mixed_hazards_are_not_reclassified(self):
        for source in self.cfg["sources"]:
            for layer in source["layers"]:
                if layer["theme"] == "mixed_hazard":
                    self.assertIn("combinada", layer.get("note", ""))

    def test_meeting_points_and_routes_are_medellin_only(self):
        for source in self.cfg["sources"]:
            for layer in source["layers"]:
                if layer["theme"] in {"meeting_points", "evacuation_routes"}:
                    self.assertEqual(source["id"], "medellin_dagrd")

if __name__ == "__main__":
    unittest.main()
