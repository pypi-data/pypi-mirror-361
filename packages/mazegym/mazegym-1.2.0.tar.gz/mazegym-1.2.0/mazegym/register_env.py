from gymnasium.envs.registration import register
import numpy as np

register(
    id='Maze9x9Random-v0',
    entry_point='mazegym.maze_gym_env:MazeEnvironment',
    kwargs={
        'width': 9,
        'height': 9
    }
)

register(
    id='Maze21x21Random-v0',
    entry_point='mazegym.maze_gym_env:MazeEnvironment',
    kwargs={
        'width': 21,
        'height': 21
    }
)

register(
    id='Maze35x15Random-v0',
    entry_point='mazegym.maze_gym_env:MazeEnvironment',
    kwargs={
        'width': 35,
        'height': 15
    }
)

def create_custom_grid():
    grid = np.ones((5, 5), dtype=np.int8)
    grid[1:4, 2] = 0
    grid[1, 1:3] = 0
    grid[3, 2:4] = 0
    grid[1, 1] = 2
    grid[3, 3] = 3
    return grid

register(
    id='Maze5x5Fixed-v0',
    entry_point='mazegym.maze_gym_env:MazeEnvironment',
    kwargs={
        'grid': create_custom_grid()
    }
)

def create_corridor():
    grid = np.ones((3, 7), dtype=np.int8)
    grid[1, :] = 0
    grid[1, 0] = 2
    grid[1, 6] = 3
    return grid

register(
    id='Maze3x7Fixed-v0',
    entry_point='mazegym.maze_gym_env:MazeEnvironment',
    kwargs={
        'grid': create_corridor()
    }
)