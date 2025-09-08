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
    # Params include limit, offset, bbox
    names = [p["name"] for p in items.get("parameters", [])]
    assert "limit" in names and "offset" in names and "bbox" in names
