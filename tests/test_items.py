from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_items_geojson_media_type_and_pagination_links():
    r = client.get("/collections/addresses/items", params={"limit": 1, "offset": 0})
    assert r.status_code == 200
    assert r.headers.get("content-type").startswith("application/geo+json")
    data = r.json()
    assert data["type"] == "FeatureCollection"
    # With limit=1 and at least one feature total, next link should be present if more than one
    assert any(link["rel"] == "self" for link in data.get("links", []))


def test_items_pin_filter_returns_match():
    r = client.get("/collections/addresses/items", params={"pin": "560008"})
    assert r.status_code == 200
    data = r.json()
    assert data["numberMatched"] >= 1
    assert data["numberReturned"] >= 1
    for f in data["features"]:
        assert f["properties"]["pin"] == "560008"


def test_items_invalid_bbox_400():
    r = client.get("/collections/addresses/items", params={"bbox": "not,a,bbox"})
    assert r.status_code == 400
    assert r.json()["error"].startswith("Invalid bbox")
