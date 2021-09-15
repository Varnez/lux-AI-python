from lux.game import Game
from lux.constants import Constants
from lux.game_map import Cell, Position
from lux.game_objects import Player, Unit
from lux.constants import Constants

from tools import get_unit_id_number

from typing import List

def move_unit(game_state: Game, player: Player, actions: List[str], unit: Unit, position_to_move: Position, direction_to_move: Constants.DIRECTIONS):
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
