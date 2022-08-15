import cv2
import numpy as np
from ant import Ant
from colony import Colony
import random
import collections
import os

# directories

# files

EMPTY = 0
ANT = 1
DEAD_ANT = 2
FOOD = 3
COLONY = 4
WATER = 5


COLORS = {EMPTY: np.array([0, 0, 0]),
          ANT: np.array([0, 0, 255]),
          DEAD_ANT: np.array([19, 69, 139]),
          FOOD: np.array([0, 255, 0]),
          COLONY: np.array([255, 255, 255]),
          WATER: np.array([139, 0, 0])}

GRID_SIZE = 10


class Game:
    def __init__(self, world_map, num_groups=2, num_ants=10, num_food=30, food_rate=1, max_turns=1000):
        # world map
        self.world_map = world_map
        self.rows, self.cols = world_map.shape

        # set state
        self.state = np.zeros(self.world_map.shape)

        # colony
        # TODO different colony, different group
        self.colonies = []
        for _ in range(num_groups):
            row, col = self.random_loc()
            self.colonies.append(Colony(self.state, (row, col)))
            self.state[row, col] = COLONY

        # food
        for _ in range(num_food):
            self.place_food()

        # ants
        self.ants = []

        # place ant at random places
        for i in range(num_ants):
            # create ant
            ant = Ant(self.state, name=i, group=0, loc=self.random_loc())

            # update state
            self.state[ant.loc[0], ant.loc[1]] = ANT

            # append ant
            self.ants.append(ant)

        # maximum number of turns
        self.max_turns = max_turns

        # rate of new food
        self.food_rate = food_rate

        # turn number
        self.turn = 0

        # video frame
        self.video_frame = np.zeros((GRID_SIZE * self.rows, GRID_SIZE * self.cols, 3))

    def random_loc(self):
        # return random free location
        row, col = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
        while self.state[row, col] != EMPTY:
            row, col = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
        return (row, col)

    def place_food(self):
        row, col = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))

        while self.state[row, col] != EMPTY:
            row, col = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))

        self.state[row, col] = FOOD

    def update_state(self):


        # update the current state

        #TODO step on dead ant
        #TODO ant teleports
        attempt_list = []

        # get attempted movements

        for ant in self.ants:
            if ant.alive:
                attempt_list.append(ant.attempt_move())
            else:
                attempt_list.append(None)

        # check if more than one ants are heading to the same location
        same_loc = [loc for loc, count in collections.Counter(attempt_list).items() if count > 1]

        # apply movements
        # erase first
        for i, ant in enumerate(self.ants):
            if ant.alive:
                if attempt_list[i] not in same_loc and not self.out_of_bound(attempt_list[i]):
                    # erase
                    row, col = ant.loc
                    self.state[row, col] = EMPTY

        # move the ants
        for i, ant in enumerate(self.ants):
            if ant.alive:
                if attempt_list[i] not in same_loc and not self.out_of_bound(attempt_list[i]):
                    # move
                    new_row, new_col = attempt_list[i]
                    self.state[new_row, new_col] = ANT

                    # tell the ant
                    self.state = ant.ant_state_update((new_row, new_col), self.state)

        # dead ants
        for ant in self.ants:
            if not ant.alive:
                row, col = ant.loc
                self.state[row, col] = DEAD_ANT

        # place more food
        for _ in range(self.food_rate):
            self.place_food()

        # TODO get rid of dead ant after a while



        self.turn += 1


    def out_of_bound(self, new_loc):
        new_row, new_col = new_loc

        if new_row < 0 or new_row >= self.rows or new_col < 0 or new_col >= self.cols:
            return True
        else:
            return False

    def visualise(self):
        # convert state to video frame
        self.video_frame[:, :, :] = 0
        for row in range(self.rows):
            for col in range(self.cols):
                # colony
                if self.state[row, col] == COLONY:
                    for i in range(3):
                        self.video_frame[row * GRID_SIZE: row * GRID_SIZE + GRID_SIZE,
                        col * GRID_SIZE: col * GRID_SIZE + GRID_SIZE, i] = COLORS[COLONY][i] / 255

                # my ant
                if self.state[row, col] == ANT:
                    for i in range(3):
                        self.video_frame[row * GRID_SIZE: row * GRID_SIZE + GRID_SIZE,
                        col * GRID_SIZE: col * GRID_SIZE + GRID_SIZE, i] = COLORS[ANT][i] / 255

                # dead ant
                if self.state[row, col] == DEAD_ANT:
                    for i in range(3):
                        self.video_frame[row * GRID_SIZE: row * GRID_SIZE + GRID_SIZE,
                        col * GRID_SIZE: col * GRID_SIZE + GRID_SIZE, i] = COLORS[DEAD_ANT][i] / 255

                # food
                if self.state[row, col] == FOOD:
                    for i in range(3):
                        self.video_frame[row * GRID_SIZE: row * GRID_SIZE + GRID_SIZE,
                        col * GRID_SIZE: col * GRID_SIZE + GRID_SIZE, i] = COLORS[FOOD][i] / 255

                # water
                if self.state[row, col] == WATER:
                    for i in range(3):
                        self.video_frame[row * GRID_SIZE: row * GRID_SIZE + GRID_SIZE,
                        col * GRID_SIZE: col * GRID_SIZE + GRID_SIZE, i] = COLORS[WATER][i] / 255

        # visualise
        cv2.namedWindow('Ant World')
        cv2.moveWindow('Ant World', 20, 20)
        cv2.imshow('Ant World', self.video_frame[:, :, :])


    def check_terminate(self):
        # TODO if all dead, terminate
        # TODO if all queens are dead, terminate
        # terminate if q is pressed
        if cv2.waitKey(300) & 0xFF == ord('q'):
            return True
        elif self.max_turns < self.turn:
            return True
        else:
            return False

    def terminate(self):
        # terminate
        cv2.destroyAllWindows()


def main():

    # initialise the game
    world_map = np.zeros((50, 100))
    for _ in range(100):
        world_map[random.randint(0, 49), random.randint(0, 99)] = WATER #TODO, this is not working
    game = Game(world_map)


    # run game
    while True:

        # update state
        game.update_state()

        # visualise
        game.visualise()

        # check for terminate
        if game.check_terminate():
            break


    # terminate game
    game.terminate()


if __name__ == '__main__':
    main()