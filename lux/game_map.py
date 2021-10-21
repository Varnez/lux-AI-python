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
        self.in_cluster = False

    def has_resource(self):
        return self.resource is not None and self.resource.amount > 0

    def mark_included_in_cluster(self):
        self.in_cluster = True


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

        self._add_adjacent_cells(first_cell)

    def _add_adjacent_cells(self, cell: Cell, map: GameMap):
        for direction in DIRECTIONS:
            adjacent_cell = map.get_cell_by_pos(cell.pos.translate(direction, 1))

            if adjacent_cell in self.cells or not adjacent_cell.has_resource:
                pass

            elif adjacent_cell.resource == self.resource_type:
                self.cells.append(adjacent_cell)
                self._add_adjacent_cells(adjacent_cell)

                adjacent_cell.mark_included_in_cluster()


class CollisionMap(GameMap):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.colision_map = np.zeros((width, height))
        self.resource_clusters = []

        for x, y in zip(range(width), range(height)):
            cell = self.get_cell(x, y)

            if cell.has_resource() and not cell.in_cluster:
                self.resource_clusters.append(ResourceCluster(cell, self))

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
