import math
import numpy as np

from .game import Game
from .constants import Constants
from .game_objects import Player
from .game_map import Cell, Position

from .game_tools import is_resource_left

from typing import List

def find_resources(game_state: Game) -> List[Cell]:
    resource_tiles: list[Cell] = []
    width, height = game_state.map_width, game_state.map_height

    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)

            if cell.has_resource():
                resource_tiles.append(cell)

    return resource_tiles


def find_empty_tiles(game_state: Game) -> List[Cell]:
    empty_tiles: list[Cell] = []
    width, height = game_state.map_width, game_state.map_height

    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)

            if not cell.has_resource() and not cell.citytile:
                empty_tiles.append(cell)

    return empty_tiles


def find_closest_resources(game_state: Game, pos: Position, player: Player, resource_tiles: List[Cell],
                           min_distance: int=0) -> Cell:
    closest_dist = math.inf
    closest_resource_tile = None

    for resource_tile in resource_tiles:
        if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM:
            if not player.researched_uranium():
                pass
            else:
                dist = resource_tile.pos.distance_to(pos)

                if dist < closest_dist and dist >= min_distance:
                    closest_dist = dist
                    closest_resource_tile = resource_tile

        elif resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL:
            if not player.researched_coal():
                pass
            else:
                dist = resource_tile.pos.distance_to(pos)

                if dist < closest_dist and dist >= min_distance:
                    closest_dist = dist
                    closest_resource_tile = resource_tile

        else:  # Constants.RESOURCE_TYPES.WOOD
            dist = resource_tile.pos.distance_to(pos)
            if dist < closest_dist and dist >= min_distance:
                closest_dist = dist
                closest_resource_tile = resource_tile

    return closest_resource_tile


def find_closest_unnocupied_resources(game_state: Game, pos: Position, player: Player, resource_tiles: List[Cell],
                                      unit_map: np.ndarry,  min_distance: int=0) -> Cell:
    closest_dist = math.inf
    closest_resource_tile = None

    for resource_tile in resource_tiles:
        if unit_map[resource_tile.pos.x][resource_tile.pos.y] != 0:
            pass
        elif resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM:
            if not player.researched_uranium():
                pass
            else:
                dist = resource_tile.pos.distance_to(pos)

                if dist < closest_dist and dist >= min_distance:
                    closest_dist = dist
                    closest_resource_tile = resource_tile

        elif resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL:
            if not player.researched_coal():
                pass
            else:
                dist = resource_tile.pos.distance_to(pos)

                if dist < closest_dist and dist >= min_distance:
                    closest_dist = dist
                    closest_resource_tile = resource_tile

        else:  # Constants.RESOURCE_TYPES.WOOD
            dist = resource_tile.pos.distance_to(pos)
            if dist < closest_dist:
                closest_dist = dist
                closest_resource_tile = resource_tile

    return closest_resource_tile


def find_closest_empty_tile(pos: Position, player: Player, empty_tiles: List[Cell]) -> Cell:
    closest_dist = math.inf
    closest_empty_tile = None

    for empty_tile in empty_tiles:
        dist = empty_tile.pos.distance_to(pos)

        if dist < closest_dist:
            closest_dist = dist
            closest_empty_tile = empty_tile

    return closest_empty_tile


def find_closest_city(pos: Position, player: Player) -> Cell:
    closest_city = None

    if len(player.cities) > 0:
        closest_dist = math.inf

        # the cities are stored as a dictionary mapping city id to the city object, which has a citytiles field that
        # contains the information of all citytiles in that city

        for k, city in player.cities.items():
            for city_tile in city.citytiles:
                dist = city_tile.pos.distance_to(pos)

                if dist < closest_dist:
                    closest_dist = dist
                    closest_city = city

    return closest_city

def find_closest_city_tile(pos: Position, player: Player):
    closest_city_tile = None

    if len(player.cities) > 0:
        closest_dist = math.inf

        # the cities are stored as a dictionary mapping city id to the city object, which has a citytiles field that
        # contains the information of all citytiles in that city

        for k, city in player.cities.items():
            for city_tile in city.citytiles:
                dist = city_tile.pos.distance_to(pos)

                if dist < closest_dist:
                    closest_dist = dist
                    closest_city_tile = city_tile

    return closest_city_tile