import json
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from enum import Enum
import random
import numpy as np
import pickle
import pika
import math 
from collections import deque

app = FastAPI()
class Vehicle_Type(Enum):
    ambulance = 1
    firetruck = 2
    police_car = 3
    #tow_truck = 4

##Just for reference
class Tile_Type(Enum):
    DISASTER = 0
    FREE = 1
    STATION = 2
    TERRAIN = 3

map = [[1, 1, 1, 0, 1, 1, 1, 1, 1, 1], [1, 1, 0, 0, 1, 1, 1, 1, 1, 1], [0, 1, 0, 1, 1, 1, 1, 1, 1, 1], [1, 1, 0, 0, 0, 1, 1, 1, 1, 1],  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
stations = []

# Dispatch notify all stations (level + coordinates)
# Dispatch choose based on the response and list (shortest distance) and dispatch sends a
# message designating which stations to send
class Station:
    """
    Station Object
    number -> id of the station
    vehicles -> list of vehicle objects per station
    coordinates -> coords of station
    """
    def __init__(self, number, vehicles, coordinates):
        self.number = number
        self.vehicles = vehicles
        self.coordinates = coordinates
        self.channel = None

    def bind_to_dispatch_exchange(self):
        print('binding to dispatch exchange')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange='dispatch_exchange', exchange_type='fanout')

        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange='dispatch_exchange', queue=queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=handle_dispatch_request, auto_ack=True)

    def start_consuming(self):
        print(f'Station {self.number} is now consuming messages...')
        self.channel.start_consuming()
        



#Unused
class Vehicle:
    """
    Station Object
    id -> id of the vehicle
    available -> availability of vehicle
    coordinates -> coords of vehicle
    """
    def __init__(self, id, vehicle, coordinates, available):
        self.id = id
        self.vehicle = vehicle
        self.coordinates = coordinates
        self.available = available

#Unused
def generate_vehicles(number_of_vehicles, station_coords):
    """
    Generates vehicles with a random vehicle type 
    """
    vehicles = []
    for i in range(number_of_vehicles):
        vehicle = Vehicle(random.randint(100, 999),  random.choice(list(Vehicle_Type)), station_coords, True)
        vehicles.append(vehicle)
    return vehicles





def build_stations(number_of_stations, coordinates, station_num):
    """
    Generates stations with 5 vehicles per station at the specified coordinates
    """
    for i in range(number_of_stations):
        station = Station(station_num[i], random.randint(1, 7), coordinates[i])
        stations.append(station)
        station.bind_to_dispatch_exchange()

    return stations

def generate_path(maze, start, end):
    visited = set()
    queue = deque([start])
    path = {start: None}

    while queue:
        source = queue.popleft()
        if source == end:
            shortest_path = [end]
            while shortest_path[-1] != start:
                shortest_path.append(path[shortest_path[-1]])
            shortest_path.reverse()
            return shortest_path

        row, col = source
        for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (row + x, col + y)
            if neighbor in visited:
                continue
            if 0 <= neighbor[0] < len(maze) and 0 <= neighbor[1] < len(maze[0]) and maze[neighbor[0]][neighbor[1]] == 1:
                visited.add(neighbor)
                queue.append(neighbor)
                path[neighbor] = source

    # If we have explored the entire maze without finding the end location, return None
    return None

def get_paths(maze, source, destination):
    """
    Actual function that should be called to generate the path for a vehicle
    """
    path = [source]
    x, y = source
    maze[x][y] = 1
    #print(np.matrix(maze))
    path = generate_path(maze, source, destination)
    print(path)
    return path


def assign_station(destination, disaster_level):
    """
    Assigns the nearest station with the appropriate resources
    """
    ##Mapping of 
    if disaster_level == 1:
        resources = 1
    elif disaster_level == 2:
        resources = 3
    elif disaster_level == 3:
        resources = 5

    min_distance = 100
    assigned_station = stations[0]
    for station in stations:
        coords = station.coordinates
        dist = math.dist(coords, destination)
        if (dist < min_distance and station.vehicles >= resources):
            assigned_station = station
            break
    return assigned_station

#Sample Skeleton Code Not Actually Implemented
def sample():
    init_stations() #replace with actual stations from dispatch
    display_stations()
    while (True):
        #Receive Disaster From Dispatch
        global map
        map = new_map #Update Map
        station = assign_station(destination, disaster_level) #Get closest station
        path = get_paths(map, station.coordinates, destination)  #get path from station to disaster
        ##Response To Dispatch With Path


def show_path(map, path):
    if path is None:
        return None
    for coord in path:
        map[coord[1]][coord[0]] = 7
    print(np.matrix(map))


    
def handle_dispatch_request(ch, method, properties, body): ##Would need to pass the station's coordinates
    print('handling dispatch request')
    disaster = json.loads(body)
    disaster_coordinates = disaster["disaster_location"]
    disaster_level = disaster["disaster_level"]
    map = disaster["map"]
    closest_station = assign_station(disaster_coordinates, disaster_level) ##Don't need this if each station is getting its own path
    print("Station coords: " + str(closest_station.coordinates)) ## Currently is just the closeset station's coords
    print("Disaster coords: " + str(disaster_coordinates))
    closest_path = get_paths(map, closest_station.coordinates, tuple(disaster_coordinates)) #Expects Coordinates to Be Tuples
    show_path(map, closest_path)

    # call send_dispatch_response()
    print('sending dispatch desponse')
    send_dispatch_response(closest_station.number, closest_path)

# Sends response to dispatch regarding status


def send_dispatch_response(station_num, path):
    # Send a message to dispatch stating its num and path to the disaster
    station_response = {
        "station": station_num,
        "path": path
    }
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='Station-Response')
    channel.basic_publish(exchange='', routing_key='Station-Response', body=pickle.dumps(station_response))
    connection.close()

##Testing
def test_path():
    map = [[1, 1, 1, 3, 1], [1, 1, 3, 3, 1], [3, 1, 3, 1, 1], [1, 1, 3, 3, 2],  [1, 1, 1, 1, 1]]
    map = [[1, 2, 1, 3, 1, 1, 1, 1, 1, 1], [1, 1, 1, 3, 1, 1, 1, 1, 1, 1], [1, 3, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 2, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 2, 1, 1, 1, 1], [1, 1, 0, 1, 1, 1, 1, 2, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 3, 1, 1, 1, 1, 1]]
    print(np.matrix(map))
    start = (8,3)
    end = (2,7)
    path = get_paths(map, start, end)
    print(len(path))
    print("Path is: ")
    print(path)

#test_path()

##Testing
def create_get_test_path():
    start = (0,0)
    end = (4,4)
    path = get_paths(map, start, end)
    return path


# Initializes Hard Coded Stations (Not Used if Dispatch Sends the Starting Locations)
def init_stations():
    station_coords = []
    station1 = (3,5)
    station2 = (6,2)
    station3 = (9,9)
    station4 = (8,1)
    station_coords.append(station1)
    station_coords.append(station2)
    station_coords.append(station3)
    station_coords.append(station4)

    station_number = []
    station1_num = 1234
    station2_num = 3612
    station3_num = 7624
    station4_num = 5135
    station_number.append(station1_num)
    station_number.append(station2_num)
    station_number.append(station3_num)
    station_number.append(station4_num)
    return build_stations(4, station_coords, station_number)

#Displaying Initial Stations
def display_stations():
    for station in stations:
        print("Station: ")
        print(station.number)
        print(station.coordinates)
        print("Vehicles: ")
        for vehicle in station.vehicles:
            print(vehicle.id)
            print(vehicle.vehicle)
            print(vehicle.coordinates)
            print(vehicle.available)
        print("------------")



if __name__ == "__station__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
   