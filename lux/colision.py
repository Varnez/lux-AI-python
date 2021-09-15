import numpy as np

from .game_map import Position
from .game_objects import Player, Unit

from ..tools import get_unit_id_number


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