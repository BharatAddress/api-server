# Bharat Address API Server (Reference)

Minimal OGC API Features-like read API using FastAPI. Serves an `addresses` collection from memory now; swap to PostGIS later.

Quickstart:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Open http://localhost:8000/collections and /collections/addresses/items
```

Docker:

```bash
docker build -t ghcr.io/bharataddress/api-server:dev .
docker run -p 8000:8000 ghcr.io/bharataddress/api-server:dev
```
