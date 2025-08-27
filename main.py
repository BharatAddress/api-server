from typing import List, Literal, Optional, Dict, Any

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from fastapi.openapi.utils import get_openapi


class Geometry(BaseModel):
    type: Literal["Point"] = Field(default="Point")
    coordinates: List[float] = Field(min_length=2, max_length=3)


class AddressProperties(BaseModel):
    ulb_lgd: str
    street_name: str
    house_number: str
    locality: str
    city: str
    state: str
    pin: str
    primary_digipin: str
    secondary_digipin: Optional[str] = None
    ulpin: Optional[str] = None
    entrance_point_source: Optional[str] = Field(default=None, description="survey|imagery|crowd|post")
    quality: Optional[str] = Field(default=None, description="MunicipalityVerified|GeoVerified|CrowdPending")


class Feature(BaseModel):
    type: Literal["Feature"] = Field(default="Feature")
    properties: AddressProperties
    geometry: Geometry


class Link(BaseModel):
    rel: str
    href: str
    type: Optional[str] = None


class FeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = Field(default="FeatureCollection")
    features: List[Feature]
    links: Optional[List[Link]] = None
    numberMatched: Optional[int] = None
    numberReturned: Optional[int] = None


class CollectionsResponse(BaseModel):
    collections: List[dict]


app = FastAPI(
    title="Bharat Address API",
    version="0.1.0",
    description="Reference OGC API Features-like read API for address features.",
    docs_url="/docs",
    redoc_url="/redoc",
)


FEATURES: FeatureCollection = FeatureCollection(
    features=[
        Feature(
            properties=AddressProperties(
                ulb_lgd="294690",
                street_name="Indira Nagar 12th Main",
                house_number="16B",
                locality="HAL 3rd Stage",
                city="Bengaluru",
                state="Karnataka",
                pin="560008",
                primary_digipin="ABC-DEF-1234",
                quality="MunicipalityVerified",
            ),
            geometry=Geometry(coordinates=[77.651, 12.963]),
        )
    ]
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get(
    "/collections",
    response_model=CollectionsResponse,
    summary="List collections",
    tags=["OGC API - Features"],
)
def collections():
    return {
        "collections": [
            {
                "id": "addresses",
                "title": "Addresses",
                "links": [
                    {"rel": "self", "type": "application/json", "href": "/collections/addresses"},
                    {"rel": "items", "type": "application/geo+json", "href": "/collections/addresses/items"},
                ],
            }
        ]
    }


@app.get(
    "/collections/addresses/items",
    response_model=FeatureCollection,
    summary="List address features",
    tags=["OGC API - Features"],
)
def items(
    limit: int = Query(100, ge=1, le=10000, description="Max number of features"),
    offset: int = Query(0, ge=0, description="Start index for pagination"),
    bbox: Optional[str] = Query(
        None,
        description="minLon,minLat,maxLon,maxLat (comma-separated) to filter by bounding box",
        examples={"blr": {"summary": "Bengaluru bbox", "value": "77.4,12.8,77.8,13.1"}},
    ),
):
    # Filter by bbox if provided
    feats = FEATURES.features
    if bbox:
        try:
            parts = [float(x) for x in bbox.split(",")]
            if len(parts) != 4:
                raise ValueError
            minx, miny, maxx, maxy = parts
        except Exception:
            return JSONResponse({"error": "Invalid bbox. Expected 'minLon,minLat,maxLon,maxLat'"}, status_code=400)
        feats = [
            f for f in feats
            if (minx <= f.geometry.coordinates[0] <= maxx) and (miny <= f.geometry.coordinates[1] <= maxy)
        ]

    total = len(feats)
    page = feats[offset: offset + limit]

    base = "/collections/addresses/items"
    params = []
    if bbox:
        params.append(f"bbox={bbox}")
    params.append(f"limit={limit}")
    params.append(f"offset={offset}")
    self_href = base + ("?" + "&".join(params) if params else "")

    links: List[Link] = [Link(rel="self", href=self_href, type="application/geo+json")]
    if offset + limit < total:
        next_offset = offset + limit
        next_params = [p for p in params if not p.startswith("offset=")] + [f"offset={next_offset}"]
        links.append(Link(rel="next", href=base + "?" + "&".join(next_params), type="application/geo+json"))
    if offset > 0:
        prev_offset = max(0, offset - limit)
        prev_params = [p for p in params if not p.startswith("offset=")] + [f"offset={prev_offset}"]
        links.append(Link(rel="prev", href=base + "?" + "&".join(prev_params), type="application/geo+json"))

    coll = FeatureCollection(features=page, links=links, numberMatched=total, numberReturned=len(page))
    return JSONResponse(coll.model_dump(), media_type="application/geo+json")


@app.get(
    "/collections/addresses",
    summary="Describe the addresses collection",
    tags=["OGC API - Features"],
)
def describe_addresses() -> Dict[str, Any]:
    return {
        "id": "addresses",
        "title": "Addresses",
        "extent": {
            "spatial": {"bbox": [[68.0, 6.0, 97.5, 37.5]]},
        },
        "itemType": "feature",
        "links": [
            {"rel": "self", "type": "application/json", "href": "/collections/addresses"},
            {"rel": "items", "type": "application/geo+json", "href": "/collections/addresses/items"},
        ],
    }


@app.get(
    "/conformance",
    summary="List conformance classes",
    tags=["OGC API - Features"],
)
def conformance() -> Dict[str, Any]:
    return {
        "conformsTo": [
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
        ]
    }


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["servers"] = [{"url": "http://localhost:8000"}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore
