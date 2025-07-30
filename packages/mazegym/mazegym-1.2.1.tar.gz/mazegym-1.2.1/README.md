# MazeGym

[![codecov](https://codecov.io/gh/EvalVis/MazeGym/branch/main/graph/badge.svg)](https://codecov.io/gh/EvalVis/MazeGym)
[![PyPI version](https://badge.fury.io/py/mazegym.svg)](https://pypi.org/project/mazegym/)

A Gymnasium env for training reinforcement learning agents to navigate mazes.

Library used: [![GitHub](https://img.shields.io/badge/GitHub-john--science%2Fmazelib-black?style=flat&logo=github)](https://github.com/john-science/mazelib).

# 9x9 maze

Random moves are used for this demo.

![Maze9x9](images/maze_9_9.gif)

# 21x21 maze

Random moves are used for this demo.

![Maze21x21](images/maze_21_21.gif)

# 35x15 maze

Random moves are used for this demo.

![Maze35x15](images/maze_35_15.gif)

## Usage

### Initiating the env via gym

```python
import gymnasium as gym
import mazegym

env_9x9_random = gym.make('Maze9x9Random-v0')
env_35x15_random = gym.make('Maze35x15Random-v0')

env_5x5_fixed = gym.make('Maze5x5Fixed-v0')
env_3x7_fixed = gym.make('Maze3x7Fixed-v0')
```

### Initiating the env directly

```python
from mazegym import MazeEnvironment

#Random env
env_random = MazeEnvironment(width=10, height=5)

# Fixed env
fixed_grid = np.ones((3, 7), dtype=np.int8)
fixed_grid[1, :] = 0
fixed_grid[1, 0] = 2
fixed_grid[1, 6] = 3
env_fixed = MazeEnvironment(grid=grid)
```

### Making moves

```python
import gymnasium as gym

env_35x15_random = gym.make('Maze35x15Random-v0')

# Reset the environment
observation, info = env_35x15_random.reset()

# Make a random valid move

valid_moves = info.get("valid_moves")
move = random.choice(valid_moves)
observation, reward, done, truncated, info = env_35x15_random.step(move)

# Render the environment. The only render mode is 'human' which renders visual output.
env_35x15_random.render()

# Close the environment
env_35x15_random.close()
```

## Configurable parameters:
- **width**: width of maze.
- **height**: height of maze.
- **grid**: User for custom mazes.
- **vision_range**: Range of tiles your agent can see forward. Agent only sees forward and remembers previously visited tiles. If vision_range is not specified all map is visible.
-- **wall_path_swap**: Tuple accepting two elements. Allows environment randomness making a wall become a path and a path become a wall. First value is the transformation chance. The second value is the frequency of transformations. No effects if tuple value is None. 

Either width and height or grid is required. Width ang height are used for random mazes while grid is used for custom mazes.

## Environment Details

- **Action Space**: Discrete(4) - Four possible actions: `0` (up), `1` (right), `2` (down), `3` (left). Invalid moves (moving into walls) results in an error.
- **Observation Space**: `Box(0, 3, (height, width), int8)`.
Contains values: `0` for empty paths, `1` for walls, `2` for the agent, `3` for the goal.
- **Reward**: `100` if the goal is reached, `-1` for each step taken.
- **Done**: `True` if the agent reaches the goal, `False` otherwise.
- **Truncated**: `True` if maximum steps `(3 × width × height)` are exceeded, `False` otherwise.