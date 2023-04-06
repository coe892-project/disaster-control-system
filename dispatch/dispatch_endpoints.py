from typing import Tuple

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from dispatch import Dispatch

app = FastAPI()
dispatch: Dispatch = None


class MapResponse(BaseModel):
    world_map: list[list[int]]
    station_coordinates: list[Tuple[int, int]]


class MapRequest(BaseModel):
    map_size: Tuple[int, int]


@app.get("/map")
def get_world_map():
    global dispatch
    if dispatch is None:
        raise HTTPException(status_code=404,
                            detail="Dispatch service has not been initialized yet. "
                                   "Call '/map/generate' before continuing.")
    world_map = [[tile.value for tile in row] for row in dispatch.world_map]
    return {"world_map": world_map, "station_coordinates": dispatch.station_coordinates}


@app.post("/map/generate")
def generate_world_map(map_parameters: MapRequest):
    global dispatch
    dispatch = Dispatch(map_parameters.map_size)
    dispatch.generate_map()
    world_map = [[tile.value for tile in row] for row in dispatch.world_map]
    return {"world_map": world_map, "station_coordinates": dispatch.station_coordinates}


@app.post("/map/generate/stations/{num_of_stations}")
def generate_stations(num_of_stations: int):
    global dispatch
    if dispatch is None:
        raise HTTPException(status_code=404,
                            detail="Dispatch service has not been initialized yet. "
                                   "Call '/map/generate' before continuing.")
    dispatch.generate_stations(num_of_stations)
    world_map = [[tile.value for tile in row] for row in dispatch.world_map]
    return {"world_map": world_map, "station_coordinates": dispatch.station_coordinates}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
