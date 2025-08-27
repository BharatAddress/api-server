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


class FeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = Field(default="FeatureCollection")
    features: List[Feature]


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
def items(limit: int = Query(100, ge=1, le=10000, description="Max number of features")):
    data = FEATURES.model_copy(deep=True)
    data.features = data.features[:limit]
    return JSONResponse(data.model_dump(), media_type="application/geo+json")


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
