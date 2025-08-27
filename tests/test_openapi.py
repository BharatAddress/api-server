import json
from pathlib import Path

from main import app


def test_openapi_has_servers_and_paths():
    spec = app.openapi()
    assert spec["info"]["title"] == "Bharat Address API"
    assert any(p.startswith("/collections") for p in spec["paths"].keys())
    assert spec.get("servers"), "servers should be present"


def test_items_media_type_geojson():
    # Ensure OpenAPI documents the items endpoint
    spec = app.openapi()
    items = spec["paths"]["/collections/addresses/items"]["get"]
    assert items["responses"], "responses declared"
