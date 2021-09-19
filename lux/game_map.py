import math
import numpy as np

from .constants import Constants

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
    def has_resource(self):
        return self.resource is not None and self.resource.amount > 0


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, pos) -> int:
        return abs(pos.x - self.x) + abs(pos.y - self.y)

    def distance_to(self, pos):
        """
        Returns Manhattan (L1/grid) distance to pos
        """
        return self - pos

    def is_adjacent(self, pos):
        return (self - pos) <= 1

    def __eq__(self, pos) -> bool:
        return self.x == pos.x and self.y == pos.y

    def equals(self, pos):
        return self == pos

    def translate(self, direction, units) -> 'Position':
        if direction == DIRECTIONS.NORTH:
            return Position(self.x, self.y - units)
        elif direction == DIRECTIONS.EAST:
            return Position(self.x + units, self.y)
        elif direction == DIRECTIONS.SOUTH:
            return Position(self.x, self.y + units)
        elif direction == DIRECTIONS.WEST:
            return Position(self.x - units, self.y)
        elif direction == DIRECTIONS.CENTER:
            return Position(self.x, self.y)

    def direction_to(self, target_pos: 'Position') -> DIRECTIONS:
        """
        Return closest position to target_pos from this position
        """
        check_dirs = [
            DIRECTIONS.NORTH,
            DIRECTIONS.EAST,
            DIRECTIONS.SOUTH,
            DIRECTIONS.WEST,
        ]
        closest_dist = self.distance_to(target_pos)
        closest_dir = DIRECTIONS.CENTER
        for direction in check_dirs:
            newpos = self.translate(direction, 1)
            dist = target_pos.distance_to(newpos)
            if dist < closest_dist:
                closest_dir = direction
                closest_dist = dist
        return closest_dir

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


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


class CollisionMap(GameMap):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.state = np.zeros((width, height))

    def check_colision(self, pos: Position) -> bool:
        if self.state[pos.x][pos.y] == 0:
            return True
        else:
            return False

    def update_colision(self, pos: Position, unit: 'Unit'):
        if self.get_cell(unit.pos.x, unit.pos.y).citytile:
            self.state[pos.x][pos.y] = unit.id_value

    def undo_movement(self, player: 'Player', actions: list, pos: Position, new_pos_id: int=0):
        id_num = int(self.state[pos.x][pos.y])
        colliding_id = 'u_{}'.format(id_num)

        for action in actions:
            if colliding_id in action:
                actions.remove(action)

        for unit in player.units:
            if unit.id == colliding_id:
                if self.state[unit.pos.x][unit.pos.y] != 0:
                    self.undo_movement(player, actions, unit.pos)

        self.update_colision(unit.pos, new_pos_id)

    def reset(self):
        self.state = np.zeros_like(self.state)

    def move_unit(self, player: 'Player', actions: List[str], unit: 'Unit', direction_to_move: Constants.DIRECTIONS):
        position_to_move = unit.pos.translate(direction_to_move, 1)

        if self.check_colision(position_to_move):
            self.update_colision(position_to_move, unit)
            action = unit.move(direction_to_move)
            actions.append(action)

        else:
            if self.get_cell(unit.pos.x, unit.pos.y).citytile:
                pass
            else:
                if self.check_colision(unit.pos.x, unit.pos.y) == 0:
                    self.update_colision(unit.pos, unit)
                else:
                    self.undo_movement(player, actions, unit.pos, unit.id_value)
