from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from enum import Enum
import random
import numpy as np
import pickle
import pika

app = FastAPI()


class Vehicle_Type(Enum):
    ambulance = 1
    firetruck = 2
    police_car = 3
    #tow_truck = 4

##Just for reference
class Tile_Type(Enum):
    Disaster = 0
    Free = 1
    Blocked = 2 ##Not sure if we need this

class Station:
    def __init__(self, number, vehicles, coordinates):
        self.number = number
        self.serial = vehicles
        self.coordinates = coordinates

class Vehicle:
    def __init__(self, id, vehicle, coordinates, available):
        self.id = id
        self.vehicle = vehicle
        self.coordinates = coordinates
        self.available = available

##Instantiate Vehicles For Stations
def generate_vehicles(number_of_vehicles, station_coords):
    vehicles = []
    for i in range(number_of_vehicles):
        vehicle = Vehicle(random.randint(100, 999),  random.choice(list(Vehicle_Type)), station_coords, True)
        vehicles.append(vehicle)
    return vehicles

##Instantiate Stations
def build_stations(number_of_stations, coordinates, station_num):
    stations = []
    for i in range(number_of_stations):
        station = Station(station_num[i], generate_vehicles(5, coordinates[i]))
        stations.append(station)
    return stations



##Generate Vehicle Path
def generate_path(maze, source, destination, visited, path, paths, rows, columns):
  if source == destination:
    paths.append(path[:])  
    return
  if len(paths) != 0:
      return paths
  
  x, y = source
  visited[x][y] = True
  if x >= 0 and y >= 0 and x < rows and y < columns and maze[x][y]:
    neighbors = [(1,0),(-1,0),(0,-1),(0,1)]
    for index, neighbor in enumerate(neighbors):
        next_xsquare = x + neighbor[0]
        next_ysquare = y + neighbor[1]
        if (next_xsquare < columns and next_xsquare >= 0 and next_ysquare < rows and next_ysquare >= 0 and (not visited[next_xsquare][next_ysquare])):
                path.append((next_xsquare, next_ysquare))
                new_source = (next_xsquare, next_ysquare)
                generate_path(maze, new_source, destination, visited, path, paths, rows, columns)
                path.pop()
  visited[x][y] = False
  return paths

def get_path(maze, source, destination, rows, columns):
  visited = [[False]*rows for _ in range(columns)] #may be inversed
  path = [source]
  paths = []
  return generate_path(maze, source, destination, visited, path, paths, rows, columns)

##Testing
def test_path():
    map = [[1, 1, 1, 0, 1], [1, 1, 0, 0, 1], [0, 1, 0, 1, 1], [1, 1, 0, 0, 0],  [1, 1, 1, 1, 1]]
    rows = len(map)
    columns = len(map[0])
    print(rows)
    print(columns)
    print(np.matrix(map))
    start = (0,0)
    end = (4,4)
    path = get_path(map, start, end, rows, columns)
    print("Path is: ")
    print(path)

test_path()

##Receive Dispatch Request
def handle_dispatch_request():
    ##Instatiation Code
    ##Reuires Some More Work
    while True:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='Dispatch-Queue')

        def callback(ch, method, properties, body):
            request = pickle.loads(body)
            print("Received %r" % request)
            connection.close()

        tag = channel.basic_consume(queue='Dispatch-Queue', on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

## Sends resposne to dispatch regarding status
def send_dispatch_response(station_num, status):
    station_response = {
        "station": station_num,
        "status": status
    }
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='Station-Response')
    channel.basic_publish(exchange='', routing_key='Station-Response', body=pickle.dumps(station_response))
    connection.close()
    


if __name__ == "__station__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    #handle_dispatch_request()