![CI](https://github.com/BharatAddress/api-server/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/BharatAddress/api-server/actions/workflows/codeql.yml/badge.svg)

# Bharat Address API Server (Reference)

Minimal OGC API Features-like read API using FastAPI. Serves an `addresses` collection from memory now; swap to PostGIS later.

Quickstart:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Open http://localhost:8000/collections, /collections/addresses, /collections/addresses/items, /conformance
# API docs: Swagger UI at /docs, ReDoc at /redoc, OpenAPI JSON at /openapi.json
```

OpenAPI export:

```bash
python export_openapi.py  # writes openapi.json in repo root
```

Query parameters (items endpoint):
- `limit` (default 100): maximum features returned
- `offset` (default 0): pagination index; response includes `self`/`next`/`prev` links
- `bbox`: `minLon,minLat,maxLon,maxLat` filter

Docker:

```bash
docker build -t ghcr.io/bharataddress/api-server:dev .
docker run -p 8000:8000 ghcr.io/bharataddress/api-server:dev
```
