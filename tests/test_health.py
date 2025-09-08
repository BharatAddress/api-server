from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_healthz_ok():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_cors_header_on_request_with_origin():
    # When Origin header present, CORS middleware should include ACAO
    r = client.get("/collections", headers={"Origin": "http://example.com"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "*"


def test_cors_preflight_options():
    r = client.options(
        "/collections",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code in (200, 204)
    # Starlette may return 200 with allow headers
    assert r.headers.get("access-control-allow-origin") == "*"
    allow_methods = r.headers.get("access-control-allow-methods", "")
    assert "GET" in allow_methods or allow_methods == "*"


def test_readyz_ok():
    r = client.get("/readyz")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}
