import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('extract_arcgis_v14', ROOT/'backend/scripts/extract_arcgis.py')
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)

class ArcGISPaginationV14Tests(unittest.TestCase):
    def test_pagination_obeys_exceeded_transfer_limit_even_short_page(self):
        responses = [
            {'features': [{'id': 1}], 'exceededTransferLimit': True},
            {'features': [{'id': 2}], 'exceededTransferLimit': False},
        ]
        with patch.object(extractor, 'get_json', side_effect=responses) as mocked:
            result = extractor.fetch_features('https://example.test/query', [], 2, 0, 'OBJECTID')
        self.assertEqual([x['id'] for x in result], [1, 2])
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(mocked.call_args_list[1].args[1]['resultOffset'], 2)

    def test_max_feature_limit_is_enforced(self):
        ids = list(range(10))
        with patch.object(extractor, 'get_json', return_value={'features': [{'id': i} for i in range(4)]}):
            result = extractor.fetch_features('https://example.test/query', ids, 4, 3, 'OBJECTID')
        self.assertEqual(len(result), 3)

    def test_sha256_is_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'sample.geojson'
            p.write_text('{"type":"FeatureCollection","features":[]}', encoding='utf-8')
            self.assertEqual(extractor.sha256_file(p), extractor.sha256_file(p))

if __name__ == '__main__':
    unittest.main()
