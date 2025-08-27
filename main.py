from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

app = FastAPI(title="Bharat Address API")

FEATURES = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "ulb_lgd": "294690",
                "street_name": "Indira Nagar 12th Main",
                "house_number": "16B",
                "locality": "HAL 3rd Stage",
                "city": "Bengaluru",
                "state": "Karnataka",
                "pin": "560008",
                "primary_digipin": "ABC-DEF-1234",
                "quality": "MunicipalityVerified",
            },
            "geometry": {"type": "Point", "coordinates": [77.651, 12.963]},
        }
    ],
}


@app.get("/collections")
def collections():
    return {"collections": [{"id": "addresses", "title": "Addresses"}]}


@app.get("/collections/addresses/items")
def items(limit: int = Query(100, ge=1, le=10000)):
    data = dict(FEATURES)
    data["features"] = FEATURES["features"][:limit]
    return JSONResponse(data)
