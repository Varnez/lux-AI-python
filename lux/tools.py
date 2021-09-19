from .game_map import GameMap
from .constants import Constants
from .game_objects import City, Player, Unit


def is_resource_left(map: GameMap, resource: Constants.RESOURCE_TYPES) -> bool:
    width, height = map.width, map.height

    for y in range(height):
        for x in range(width):
            cell = map.get_cell(x, y)

            if cell.resource == resource:
                return True

    return False


def get_current_fuel_cost(city: City) -> int:
    current_cost = 0

    for city_tile in city.citytiles:
        city_tile_cost = 23

        for other_city_tiles in city.citytiles:
            if city_tile.pos.distance_to(other_city_tiles.pos) == 1:
                city_tile_cost -= 5

        current_cost += city_tile_cost

    return current_cost


def count_player_city_tiles(player: Player):
    city_tiles_count = 0

    for city in player.cities.values():
        for _ in city.citytiles:
            city_tiles_count += 1

    return city_tiles_count
