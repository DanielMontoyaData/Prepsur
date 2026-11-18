import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_gis_catalog_is_scoped_and_https():
    data=json.loads((ROOT/'gis/sources/sources.json').read_text())
    assert len(data['sources']) >= 5
    municipalities={x['municipality'] for x in data['sources']}
    for name in ['Envigado','Itagüí','Sabaneta','La Estrella','Caldas']:
        assert name in municipalities
    for source in data['sources']:
        assert source['service'].startswith('https://')
        assert source.get('scope_note')
        assert source['layers']
        assert all(isinstance(layer['id'],int) for layer in source['layers'])
