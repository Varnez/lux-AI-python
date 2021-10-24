import math
import numpy as np

from .game_objects import Unit, Player
from .constants import Constants
from .position import Position

from typing import List


DIRECTIONS = Constants.DIRECTIONS
RESOURCE_TYPES = Constants.RESOURCE_TYPES



class Resource:
    def __init__(self, r_type: str, amount: int):
        self.type = r_type
        self.amount = amount



class Cell:
    def __init__(self, x, y):
        self.pos = Position(x, y)
        self.resource: Resource = None
        self.citytile = None
        self.road = 0
        self.cluster = None

    def has_resource(self):
        return self.resource is not None and self.resource.amount > 0

    def mark_included_in_cluster(self, cluster):
        self.cluster = cluster



class GameMap:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.map: List[List[Cell]] = [None] * height
        for y in range(0, self.height):
            self.map[y] = [None] * width
            for x in range(0, self.width):
                self.map[y][x] = Cell(x, y)

    def get_cell_by_pos(self, pos) -> Cell:
        return self.map[pos.y][pos.x]

    def get_cell(self, x, y) -> Cell:
        return self.map[y][x]

    def _setResource(self, r_type, x, y, amount):
        """
        do not use this function, this is for internal tracking of state
        """
        cell = self.get_cell(x, y)
        cell.resource = Resource(r_type, amount)



class ResourceCluster:
    def __init__(self, first_cell: Cell, map: GameMap):
        self.cells = [first_cell]
        self.resource_type = first_cell.resource.type
        self.assigned_units = []

        first_cell.cluster = self
        self._add_adjacent_cells(first_cell)


    def _add_adjacent_cells(self, cell: Cell, map: GameMap):
        for direction in DIRECTIONS:
            adjacent_cell = map.get_cell_by_pos(cell.pos.translate(direction, 1))

            if adjacent_cell in self.cells or not adjacent_cell.has_resource:
                pass

            elif adjacent_cell.resource == self.resource_type:
                self.cells.append(adjacent_cell)
                self._add_adjacent_cells(adjacent_cell)

                adjacent_cell.cluster = self


    def cell_amount(self) -> int:
        return len(self.cells)


    def closest_reource_tile(self, position: Position) -> Cell:
        least_distance = math.inf
        closest_tile = None

        for cell in self.cells:
            distance = cell.pos.distance_to(position)

            if distance < least_distance:
                least_distance = distance
                closest_tile = cell

        return closest_tile


    def check_number_of_units(self, unit_map: np.ndarray):
        number_of_units = 0

        for cell in self.cells:
            if unit_map[cell.pos.x][cell.pos.y] != 0:
                number_of_units += 1

        return number_of_units



class CollisionMap(GameMap):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.colision_map = np.zeros((width, height))
        self.player_unit_placement_map = np.zeros((width, height))
        self.enemy_unit_placement_map = np.zeros((width, height))
        self.resource_clusters = []
        self.resource_clusters_population = None

        for x, y in zip(range(width), range(height)):
            cell = self.get_cell(x, y)

            if cell.has_resource() and not cell.in_cluster:
                self.resource_clusters.append(ResourceCluster(cell, self))

        self.update_resource_cluster_population()


    def check_colision(self, pos: Position) -> bool:
        if self.colision_map[pos.x][pos.y] == 0:
            return True
        else:
            return False


    def update_colision(self, pos: Position, unit: Unit):
        if not self.get_cell(pos.x, pos.y).citytile:
            self.colision_map[pos.x][pos.y] = unit.id_value


    def undo_movement(self, player: Player, actions: list, pos: Position, undoer_unit: Unit):
        id_num = int(self.colision_map[pos.x][pos.y])
        colliding_id = 'u_{}'.format(id_num)

        for action in actions:
            if colliding_id in action:
                actions.remove(action)

        for unit in player.units:
            if unit.id == colliding_id:
                if self.colision_map[unit.pos.x][unit.pos.y] != 0:
                    self.undo_movement(player, actions, unit.pos, unit)

        self.update_colision(undoer_unit.pos, undoer_unit)


    def reset_colision(self):
        self.colision_map = np.zeros_like(self.colision_map)


    def move_unit(self, player: Player, actions: List[str], unit: Unit, direction_to_move: Constants.DIRECTIONS):
        position_to_move = unit.pos.translate(direction_to_move, 1)

        if self.check_colision(position_to_move):
            self.update_colision(position_to_move, unit)
            action = unit.move(direction_to_move)
            actions.append(action)

        else:
            if self.get_cell(unit.pos.x, unit.pos.y).citytile:
                pass
            else:
                if self.check_colision(unit.pos) == 0:
                    self.update_colision(unit.pos, unit)
                else:
                    self.undo_movement(player, actions, unit.pos, unit)


    def update_player_unit_placement_map(self, units):
        self._update_unit_map(self.player_unit_placement_map, units)


    def update_enemy_unit_placement_map(self, units):
        self._update_unit_map(self.enemy_unit_placement_map, units)


    def _update_unit_map(self, map: np.ndarray, units: List[Unit]):
        for unit in units:
            map[unit.pos.x][unit.pos.y] = unit.id_value


    def update_resource_cluster_population(self):
        populations = []

        for cluster in self.resource_clusters:
            population = cluster.check_number_of_units(self.player_unit_placement_map)
            population += cluster.check_number_of_units(self.enemy_unit_placement_map)

            populations.append(population)

        self.resource_clusters_population = np.array(populations)

    def get_closest_available_cluster(self, pos: Position, max_occupancy: float=1.0) -> Cell:
        """In order not to be greedy on processing time, I will only calculate the distance to the original cell.
        This might be subject to revision in the future, that's why I'm leaving it written down here."""
        least_distance = math.inf
        closest_cluster = None

        for idx, cluster in enumerate(self.resource_clusters):
            if (self.cluster_population[idx] / cluster.cell_amount()) > max_occupancy:
                continue

            distance = pos.distance_to(cluster.cells[0].pos)

            if distance < least_distance:
                least_distance = distance
                closest_cluster = cluster

        return closest_cluster