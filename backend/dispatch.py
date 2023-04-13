import random
from enum import Enum
import threading
from typing import Tuple
import json
from fastapi import FastAPI
import numpy as np
import pika

from station import build_stations


class TileType(Enum):
    DISASTER = 0
    FREE = 1
    STATION = 2
    TERRAIN = 3

class Dispatch:
    """
    Manages map and service station information, relaying real-time information to a frontend map display.
    """

    def __init__(self, map_size: Tuple[int, int]):
        """
        Initializes the dispatch service with a blank map of the given map_size tuple.
        :param map_size: Tuple of X,Y dimensions.
        """
        self.world_map: list[list[TileType]] = [[TileType.FREE for _ in range(map_size[0])] for _ in
                                                range(map_size[1])]
        self.station_coordinates: list[Tuple[int, int]] = []

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_purge(queue="DisasterResponse")
        self.channel.exchange_declare(exchange='dispatch_exchange', exchange_type='fanout')
   

    def generate_map(self):
        """
        Generates a random map with terrain tiles, free of disasters.
        Terrain tiles have a pre-set probability of spawning anywhere, and have an increased probability to spawn should
        a neighbouring tile be a terrain tile.
        :param map_size: Tuple of X,Y dimensions
        :return: 2D array representing the generated map.
        """
        terrain_chance = 0.1
        for y in range(len(self.world_map[1])):
            for x in range(len(self.world_map[0])):
                if random.random() < terrain_chance:
                    self.set_tile(x, y, TileType.TERRAIN)
                # If the terrain could not spawn on its base chance, check neighbours to see if there are any terrain
                # tiles in the vicinity, and apply an increased spawn chance
                elif self.check_neighbours((x, y), TileType.TERRAIN) \
                        and random.random() * 1.5 < terrain_chance:
                    self.set_tile(x, y, TileType.TERRAIN)

    def generate_stations(self, num_stations: int):
        """
        Generates a given amount of stations and places them randomly on the map.
        :param num_stations: Number of stations to be generated.
        :return:
        """
        #Added to clear stations
        if len(self.station_coordinates) != 0:
            for station in self.station_coordinates:
                self.set_tile(station[0], station[1], TileType.FREE) #Not sure if this is redundant
            self.station_coordinates.clear()
            
        max_x, max_y = len(self.world_map[0]) - 1, len(self.world_map) - 1
        for _ in range(num_stations):
            valid_spot = False
            while not valid_spot:
                x, y = random.randint(0, max_x), random.randint(0, max_y)
                if self.get_tile(x, y) == TileType.FREE and not self.check_neighbours((x, y), TileType.STATION) and \
                        not self.check_neighbours((x, y), TileType.TERRAIN):
                    self.set_tile(x, y, TileType.STATION)
                    self.station_coordinates.append((x, y))
                    valid_spot = True

        station_numbers = []
        for _ in range(num_stations):
            station_numbers.append(random.randint(1000, 9999))
        
        stations = build_stations(num_stations, self.station_coordinates, station_numbers)
        
        # have each station start consuming on a separate thread so that it's non-blocking
        for station in stations:
            t = threading.Thread(target=station.start_consuming)
            t.start()

    def check_neighbours(self, position: Tuple[int, int], tile: TileType) -> bool:
        """
        Check neighbours of a tile at an index for another tile type, returning true if a tile is found.
        :param position: X,Y coordinates to check for neighbours.
        :param tile: Tile type enum to check for.
        :return: Boolean indicating if the given map position has a neighbour of the given tile type.
        """
        x, y = position
        if len(self.world_map) < 0 and len(self.world_map[y]) < 0:
            return False
        if x > 0 and y > 0:
            if self.get_tile(x - 1, y - 1) == tile or self.get_tile(x - 1, y) == tile or self.get_tile(x,
                                                                                                       y - 1) == tile:
                return True
        if x < len(self.world_map[y]) - 1 and y < len(self.world_map) - 1:
            if self.get_tile(x + 1, y + 1) == tile or self.get_tile(x + 1, y) == tile or self.get_tile(x,
                                                                                                       y + 1) == tile:
                return True
        if x > 0:
            if self.get_tile(x - 1, y) == tile:
                return True
        if y > 0:
            if self.get_tile(x, y - 1) == tile:
                return True
        if x < len(self.world_map[y]) - 1:
            if self.get_tile(x + 1, y) == tile:
                return True
        if y < len(self.world_map) - 1:
            if self.get_tile(x, y + 1) == tile:
                return True
        return False

    def get_tile(self, x: int, y: int) -> TileType:
        """
        Returns the tile at the given coordinate.
        :param x: X coordinate of the tile.
        :param y: Y coordinate of the tile.
        :return: Tile at coordinates.
        """
        if (x > 0 and y > 0) or (x < len(self.world_map[0]) and y < len(self.world_map)):
            return self.world_map[y][x]
        else:
            raise IndexError

    def set_tile(self, x: int, y: int, tile: TileType):
        """
        Sets the tile at the given coordinate.
        :param x: X coordinate of the tile.
        :param y: Y coordinate of the tile.
        :param tile: Tile enum to be used.
        """
        if (x > 0 and y > 0) or (x < len(self.world_map[0]) and y < len(self.world_map)):
            self.world_map[y][x] = tile
        else:
            raise IndexError

    def __str__(self) -> str:
        map_str = ""
        for y in range(len(self.world_map)):
            for x in range(len(self.world_map[y])):
                map_str += str(self.get_tile(x, y).value)
            map_str += "\n"
        return map_str

    def send_dispatch_request(self, location, level):
        """
        Publish to station queue to notify stations about a disaster's location and threat level
        :param location: cooordinates of the disaster
        :param level: threat level of the disaster
        :return: 
        """

        map = [[item.value for item in sublist] for sublist in self.world_map]

        request = {
            "disaster_location": location,
            "disaster_level": level,
            "map": map
        }

        self.channel.basic_publish(exchange='dispatch_exchange', routing_key='', body=json.dumps(request))

    def generate_disaster(self, location, level):
        """
        Generates a disaster with info provided by front-end which includes level of intensity
        and location.
        :param 
        :return: 
        """
        # code to generate disaster
        x = location[0]
        y = location[1]

        if self.get_tile(x, y) == TileType.FREE:
            self.set_tile(x, y, TileType.DISASTER)
            self.send_dispatch_request(location, level)
        else:
            print('Space occupied. Disaster could not be created')
            return 0

        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        channel = connection.channel()
        channel.queue_delete(queue="DisasterResponse")
        channel.queue_declare(queue="DisasterResponse")
        
        def callback(ch, method, properties, body):
            response = body.decode('utf-8')
            global station_response
            station_response = response.split(" ", 1)
            self.set_tile(x, y, TileType.FREE)
            channel.stop_consuming()
            
        channel.basic_consume(queue="DisasterResponse", on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

        if station_response[0] is not None and station_response[1] is not None:
            return station_response
        else:    
            return 1 # if path is empty, have api return error
        

        
        