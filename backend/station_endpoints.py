from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import station

app = FastAPI()

#Path Testing
@app.post("/paths")
def test_path():
    return station.create_get_test_path()


@app.get("/paths")
def get_path():
    return station.get_path()

@app.get("/stations")
def get_stations():
    return station.get_stations()

@app.get("/stations/{station_id}")
def get_station_vehicles(station_id: int):
    return station.get_station_vehicles(station_id)

if __name__ == "__station_endpoints__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    #handle_dispatch_request()