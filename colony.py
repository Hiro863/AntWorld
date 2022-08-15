import random
from ant import Ant, Larva, Egg, Queen

EMPTY = 0
MY_ANT = 1
ENEMY_ANT = 2
DEAD_ANT = 3
FOOD = 4
COLONY = 5


class Colony:
    def __init__(self, state, loc, num_ants=3, num_larvae=0, num_eggs=0, num_foods=100, group=0):

        # colony location
        self.hill_row = loc[0]
        self.hill_col = loc[1]

        # queen
        self.queen = Queen()

        # names
        self.names = list(range(num_ants))

        # number of ants in the colony
        self.num_ants = num_ants
        self.ants = []
        for i in range(num_ants):
            self.ants.append(Ant(state, name=i, loc=(self.hill_row, self.hill_col), group=group))

        # number of larvae in the colony
        self.num_larvae = num_larvae

        # larvae
        self.larvae = []

        # number of eggs in the colony
        self.num_eggs = num_eggs

        # eggs
        self.eggs = []

        # number of foods
        self.foods = num_foods

        # group name
        self.group = group


    def let_ant_in(self, ants):
        # append to list of ants in the colony
        name = 0
        for ant in ants:
            if ant.loc == (self.hill_row, self.hill_col):
                self.ants.append(ant)
                name = ant.name
                break
        for ant in ants:
            if ant.name == name:
                del ant

        # update number of ants
        self.num_ants += 1
        return ants

    def let_ant_out(self, ants):

        if self.ants:
        # append to list in game
            ants.append(self.ants[0])

            # remove from colony list
            self.ants.pop(0)

            # update number of ants
            self.num_ants -= 1
        return ants

    def decide_entry(self, state):
        return bool(random.getrandbits(1))

    def decide_exit(self, state):
        if state[self.hill_row, self.hill_col] != MY_ANT:
            return bool(random.getrandbits(1))
        else:
            return False

    def feed_larvae(self, larva):
        self.foods -= 1
        larva.hunger = 1.0

    def hatch_egg(self, egg_index):
        # turn egg into larva
        egg = self.eggs[egg_index]
        self.larvae.append(Larva(egg))
        del self.eggs[egg_index]

    def update_state(self, state, ants):
        ant_out = False

        # let ant in
        if state[self.hill_row, self.hill_col] == MY_ANT and self.decide_entry(state):
            ants = self.let_ant_in(ants)


        # let ant out
        elif self.decide_exit(state):
            ants = self.let_ant_out(ants)
            ant_out = True

        # feed queen
        self.queen.eat(self.foods)

        # feed larvae
        for i in range(min(self.num_ants, self.foods, len(self.larvae))):
            self.feed_larvae(self.larvae[i])

        # lay eggs
        egg = self.queen.lay_egg(self.names[-1] + 1)
        self.eggs.append(egg)

        # check if hatched
        hatched = []
        for i, egg in enumerate(self.eggs):
            if egg.hatched():
                hatched.append(i)

        for i in hatched:
            self.hatch_egg(i)

        return state, ants, ant_out



