import numpy as np

from .game import Game
from .game_map import Position
from .game_objects import Player, Unit
from .constants import Constants

from .tools import get_unit_id_number

from typing import List

class CollisionMap:
    def __init__(self, height: int, width: int):
        self.state = np.zeros((width, height))


    def check_colision(self, position: Position) -> bool:
        x, y = position.x, position.y

        if self.state[x][y] == 0:
            return True
        else:
            return False


    def update_colision(self, position: Position, unit: Unit):
        x, y = position.x, position.y

        self.state[x][y] = get_unit_id_number(unit)


    def undo_movement(self, player: Player, actions: list, pos: Position, new_pos_id: int=0):
        id_num = int(self.state[pos.x][pos.y])
        colliding_id = 'u_{}'.format(id_num)

        for action in actions:
            if colliding_id in action:
                actions.remove(action)

        for unit in player.units:
            if unit.id == colliding_id:
                if self.state[unit.pos.x][unit.pos.y] != 0:
                    self.undo_movement(player, actions, unit.pos, int(unit.id[2:]))

        self.update_colision(new_pos_id.pos, new_pos_id)

    def reset(self):
        self.state = np.zeros_like(self.state)

    def move_unit(game_state: Game, player: Player, actions: List[str], unit: Unit, direction_to_move: Constants.DIRECTIONS, un):
        position_to_move = unit.pos.translate(direction_to_move, 1)

        if game_state.colision_map.check_colision(position_to_move):
            game_state.colision_map.update_colision(position_to_move, unit)
            action = unit.move(direction_to_move)
            actions.append(action)

        else:
            if game_state.map.get_cell(unit.pos.x, unit.pos.y).citytile:
                pass
            else:
                if game_state.colision_map.check_colision[unit.pos.x][unit.pos.y] == 0:
                    game_state.colision_map.update_colision(unit.pos, unit)
                else:
                    game_state.colision_map.undo_movement(player, actions, game_state.colision_map, unit.pos, get_unit_id_number(unit))