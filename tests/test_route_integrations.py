import json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class RouteIntegrationTests(unittest.TestCase):
    def test_provider_catalog_has_no_fake_api_claims(self):
        data = json.loads((ROOT / "integrations/route-providers.json").read_text(encoding="utf-8"))
        by_id = {x["id"]: x for x in data["providers"]}
        self.assertEqual(by_id["wikiloc"]["mode"], "search_link_and_user_gpx")
        self.assertIn("No public developer API", by_id["wikiloc"]["notes"])
        self.assertEqual(by_id["komoot"]["mode"], "share_link_and_user_gpx")
    def test_osm_trail_downloader_marks_not_verified(self):
        script = (ROOT / "backend/scripts/download_osm_trails.py").read_text(encoding="utf-8")
        self.assertIn("not_field_verified", script)
        self.assertIn("ODbL", script)
        self.assertIn("Overpass", script)
if __name__ == "__main__":
    unittest.main()
