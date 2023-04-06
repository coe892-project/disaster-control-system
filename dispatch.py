import random
from enum import Enum
from typing import Tuple


class TileType(Enum):
    DISASTER = 0
    FREE = 1
    BLOCKED = 2


class Dispatch:
    """
    Manages map and service station information, relaying real-time information to a frontend map display.
    """

    def __init__(self, map_size: Tuple[int, int]):
        """
        Initializes the dispatch service with a blank map of the given map_size tuple.
        :param map_size: Tuple of X,Y dimensions
        """
        self.world_map: list[list[TileType]] = [[TileType.FREE for _ in range(map_size[0])] for _ in
                                                range(map_size[1])]

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
                    self.set_tile(x, y, TileType.BLOCKED)
                # If the terrain could not spawn on its base chance, check neighbours to see if there are any terrain
                # tiles in the vicinity, and apply an increased spawn chance
                elif self.check_neighbours((x, y), TileType.BLOCKED) \
                        and random.random() * 1.5 < terrain_chance:
                    self.set_tile(x, y, TileType.BLOCKED)

    def check_neighbours(self, position: Tuple[int, int], tile: TileType) -> bool:
        """
        Check neighbours of a tile at an index for another tile type, returning true if a tile is found.
        :param map_state:
        :param position: X,Y coordinates to check for neighbours
        :param tile: Tile type enum to check for
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
        Returns the tile at the given coordinate
        :param x: X coordinate of the tile
        :param y: Y coordinate of the tile
        :return: Tile
        """
        if (x > 0 and y > 0) or (x < len(self.world_map[0]) and y < len(self.world_map)):
            return self.world_map[y][x]
        else:
            raise IndexError

    def set_tile(self, x: int, y: int, tile: TileType):
        """
        Sets the tile at the given coordinate
        :param x: X coordinate of the tile
        :param y: Y coordinate of the tile
        :param tile: Tile enum to be used
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


d = Dispatch((10, 10))
d.generate_map()
print(d)
