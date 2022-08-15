import random
import numpy as np
import math

EMPTY = 0
ANT = 1
DEAD_ANT = 2
FOOD = 3

ACTIONS = {0: 'n',
           1: 'e',
           2: 's',
           3: 'w',
           4: 'r'}

MOVE_VEC = {'n': (-1, 0),
            'e': (0, 1),
            's': (1, 0),
            'w': (0, -1),
            'r': (0, 0)}

ADJACENT = ((-1, 0), (0, 1), (1, 0), (0, -1))

VISIBLE_SIZE = 16
VISIBLE_RADIUS = 7


INCUBATION_PERIOD = 10
MATURATION_PERIOD = 10

random.seed(2)

class Queen:
    def __init__(self):

        self.hunger = 1.0

    def eat(self, food):
        food -= 5
        self.hunger = 1.0

    def lay_egg(self, name):
        return Egg(name=name)


class Ant:
    def __init__(self, state, name, loc, group, in_colony=True):

        # ant location
        self.loc = loc

        # visible area
        self.visible = self.get_visible(state)

        # hunger level
        self.hunger = 1.0

        # alive
        self.alive = True

        # name, integer
        self.name = name

        # in colony
        self.in_colony = in_colony

        # group name
        self.group = group

    def get_visible(self, state):

        visible = np.full((2 * VISIBLE_RADIUS + 1, 2 * VISIBLE_RADIUS + 1), -1)

        visible[VISIBLE_RADIUS, VISIBLE_RADIUS] = 1

        for row in range(2 * VISIBLE_RADIUS + 1):
            for col in range(2 * VISIBLE_RADIUS + 1):
                map_row, map_col = self.map_convert((row, col))

                if (0 <= map_row < state.shape[0]) and (0 <= map_col < state.shape[1]):
                    visible[row, col] = state[map_row, map_col]

        return visible

    def map_convert(self, ant_coord):

        ant_row, ant_col = ant_coord
        row, col = self.loc
        map_coord = ant_row + row, ant_col + col

        return map_coord


    def make_decision(self):
        decision = ACTIONS[random.randint(0, 4)]
        return decision

    def attempt_move(self):
        decision = self.make_decision()

        # get new direction
        row, col = self.loc
        d_row, d_col = MOVE_VEC[decision]
        new_loc = (row + d_row, col + d_col)

        return new_loc

    def ant_state_update(self, new_loc, state):
        self.loc = new_loc

        found, food_loc = self.found_food(new_loc, state)
        if found:
            state = self.eat(state, food_loc)
            self.hunger = 1.0

        self.hunger -= 0.01

        if self.hunger <= 0:
            self.alive = False

        return state

    def found_food(self, new_loc, state):
        new_row, new_col = new_loc
        rows = state.shape[0]
        cols = state.shape[1]

        adj_locs = []
        for row, col in ADJACENT:
            adj_locs.append(((new_row + row), (new_col + col)))

        for adj_row, adj_col in adj_locs:
            if 0 <= adj_row < rows and 0 <= adj_col < cols:
                if state[adj_row, adj_col] == FOOD:
                    return True, (adj_row, adj_col)

        return False, None

    def eat(self, state, food_loc):
        row, col = food_loc
        assert state[row, col] == FOOD
        state[row, col] = EMPTY
        return state

    # TODO attack


class Larva:
    def __init__(self, egg):

        # name
        self.name = egg.name

        # hunger
        self.hunger = egg.hunger

        # maturation
        self.maturation = 0.0

    def eat(self, food):
        food -= 1
        return food

    def mature(self):
        self.maturation += 1.0 / MATURATION_PERIOD

    def become_ant(self):
        # TODO
        pass


class Egg:
    def __init__(self, name):

        # name
        self.name = name

        # hunger
        self.hunger = 1.0

        # maturation
        self.maturation = 0.0

        # alive
        self.alive = True

    def mature(self):
        self.maturation += 1.0 / INCUBATION_PERIOD

    def hatched(self):
        if self.maturation >= 1.0:
            return True


        #TODO large food
        # TODO communication through trails

