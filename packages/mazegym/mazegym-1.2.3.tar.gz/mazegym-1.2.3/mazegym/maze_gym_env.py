from mazelib import Maze
from mazelib.generate.Prims import Prims
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import matplotlib.pyplot as plt
from matplotlib import colors

class MazeEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}
    def __init__(self, size=None, grid=None, vision_range=None, wall_path_swap=None, max_steps=None):
        super().__init__()
        if size is not None:
            self._width, self._height = size
        else:
            self._width = None
            self._height = None
        self._maze = None
        self._agent_pos = None
        self._goal_pos = None
        self._steps_taken = 0
        self._max_steps = max_steps
        self._vision_range = vision_range if vision_range is not None else float('inf')
        self._facing_direction = 1  # 0: up, 1: right, 2: down, 3: left (starts looking right)
        self._visited_positions = set()  # Track visited positions to prevent fog of war
        
        # Dynamic wall/path swapping parameters (chance, cooldown)
        if wall_path_swap is not None:
            self._wall_path_swap_change, self._wall_path_swap_cooldown = wall_path_swap
        else:
            self._wall_path_swap_change = None
            self._wall_path_swap_cooldown = None
        
        self._initial_maze = None
        self._initial_agent_pos = None
        self._initial_goal_pos = None
        self._initial_facing_direction = None
        
        self.action_space = None
        self.observation_space = None
        self.fig = None
        self.ax = None
        
        plt.ion()

        if size is not None:
            width, height = size
            if width < 7 or height < 7:
                raise ValueError("Maze cannot be smaller than 7x7.")
            if width % 2 == 0 or height % 2 == 0:
                raise ValueError("Dimensions must be odd numbers.")

        if ((size is not None and grid is not None)
                or (size is None and grid is None)):
            raise ValueError("Please enter either size or a grid")
        
        if grid is not None:
            self._setup_from_grid(grid)
        else:
            self._generate_maze()

    def _setup_from_grid(self, grid):
        """Set up the environment from a provided grid."""
        if not isinstance(grid, np.ndarray):
            raise ValueError("Grid must be a numpy array")
        
        if grid.dtype != np.int8:
            raise ValueError("Grid must be of dtype np.int8")
            
        if not np.all(np.isin(grid, [0, 1, 2, 3])):
            raise ValueError("Grid must contain only values 0, 1, 2, 3")
        
        agent_positions = np.argwhere(grid == 2)
        if len(agent_positions) != 1:
            raise ValueError("Grid must contain exactly one agent (value 2)")
        self._agent_pos = (int(agent_positions[0][0]), int(agent_positions[0][1]))
        
        goal_positions = np.argwhere(grid == 3)
        if len(goal_positions) != 1:
            raise ValueError("Grid must contain exactly one goal (value 3)")
        self._goal_pos = (int(goal_positions[0][0]), int(goal_positions[0][1]))
        
        self._height, self._width = grid.shape
        self._maze = grid.copy()
        
        self._update_spaces()
        self._store_initial_state()
        
    def _generate_maze(self):
        """Generate a random maze."""
        maze = Maze()
        
        maze_width = (self._width - 1) // 2
        maze_height = (self._height - 1) // 2
        
        maze_width = max(1, maze_width)
        maze_height = max(1, maze_height)
        
        maze.generator = Prims(maze_width, maze_height)
        maze.generate()
        
        grid = np.array(maze.grid, dtype=np.int8)
        path_positions = np.argwhere(grid == 0)
        if path_positions.size == 0:
            raise ValueError("No path found in the maze")
        
        self._agent_pos = (int(path_positions[0][0]), int(path_positions[0][1]))
        grid[self._agent_pos] = 2
        
        self._goal_pos = (int(path_positions[-1][0]), int(path_positions[-1][1]))
        grid[self._goal_pos] = 3
        
        self._maze = grid.copy()
        
        self._update_spaces()
        self._store_initial_state()
    
    def _update_spaces(self):
        """Set up action and observation spaces based on current dimensions."""
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0, high=4, shape=(self._height, self._width), dtype=np.int8
        )
    
    def _store_initial_state(self):
        """Store the initial state for reset."""
        self._initial_maze = self._maze.copy()
        self._initial_agent_pos = self._agent_pos
        self._initial_goal_pos = self._goal_pos
        self._initial_facing_direction = self._facing_direction
        self._steps_taken = 0
        self._max_steps = self._max_steps if self._max_steps is not None else 3 * self._width * self._height
    
    def _get_valid_moves(self, position):
        row, col = position
        moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        valid_moves = []
        
        for i, (dr, dc) in enumerate(moves):
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self._height and 0 <= new_col < self._width and self._maze[new_row, new_col] != 1:
                valid_moves.append(i)
                
        return valid_moves
    
    def _cast_ray(self, start_pos, direction, max_distance):
        """Cast a ray from start_pos in given direction and return visible cells."""
        visible_cells = []
        row, col = start_pos
        dr, dc = direction
        
        for distance in range(1, max_distance + 1):
            new_row = row + dr * distance
            new_col = col + dc * distance
            
            if not (0 <= new_row < self._height and 0 <= new_col < self._width):
                break
            
            visible_cells.append((new_row, new_col))
            
            if self._maze[new_row, new_col] == 1:
                break
                
        return visible_cells
    
    def _get_line_of_sight(self, agent_pos):
        """Get all cells visible from agent's position in the facing direction only."""
        visible_cells = set()
        visible_cells.add(agent_pos)
        
        # Direction vectors: 0: up, 1: right, 2: down, 3: left
        main_directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        # Get the main facing direction
        main_direction = main_directions[self._facing_direction]
        
        # Cast ray only in the main facing direction (no diagonals)
        ray_cells = self._cast_ray(agent_pos, main_direction, self._vision_range)
        visible_cells.update(ray_cells)
        
        return visible_cells
    
    def _apply_wall_path_swapping(self):
        """Apply dynamic wall/path swapping based on parameters."""
        if (self._wall_path_swap_change is None or 
            self._wall_path_swap_cooldown is None or
            self._steps_taken % self._wall_path_swap_cooldown != 0):
            return
        
        # Create a copy to modify
        new_maze = self._maze.copy()
        
        # Apply swapping to each cell
        for row in range(self._height):
            for col in range(self._width):
                # Skip agent and goal positions
                if (row, col) == self._agent_pos or (row, col) == self._goal_pos:
                    continue
                
                cell_value = self._maze[row, col]
                
                # Only swap walls (1) and empty paths (0)
                if cell_value in [0, 1]:
                    if np.random.random() < self._wall_path_swap_change:
                        # Swap: wall becomes path, path becomes wall
                        new_maze[row, col] = 1 - cell_value
        
        self._maze = new_maze
    
    def _apply_vision_mask(self):
        """Apply vision mask to the maze, obscuring areas outside line of sight."""
        # If vision range is infinite (None), show everything
        if self._vision_range == float('inf'):
            return self._maze.copy()
        
        visible_cells = self._get_line_of_sight(self._agent_pos)
        
        masked_maze = np.full((self._height, self._width), 4, dtype=np.int8)
        
        # Copy visible cells from the real maze
        for row, col in visible_cells:
            masked_maze[row, col] = self._maze[row, col]
        
        # Copy visited positions from the real maze (they remain visible)
        for row, col in self._visited_positions:
            masked_maze[row, col] = self._maze[row, col]
        
        return masked_maze

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self._maze = self._initial_maze.copy()
        self._agent_pos = self._initial_agent_pos
        self._goal_pos = self._initial_goal_pos
        self._facing_direction = self._initial_facing_direction
        self._steps_taken = 0
        self._visited_positions = set()
        self._visited_positions.add(self._agent_pos)  # Mark initial position as visited

        info = {"valid_moves": self._get_valid_moves(self._agent_pos)}
        return self._apply_vision_mask(), info
    
    def step(self, action):
        if self._steps_taken >= self._max_steps:
            raise ValueError("Episode has already finished.")
            
        self._steps_taken += 1
        truncated = self._steps_taken >= self._max_steps

        # Apply dynamic wall/path swapping if configured
        self._apply_wall_path_swapping()

        current_row, current_col = self._agent_pos
        
        valid_moves = self._get_valid_moves(self._agent_pos)
        
        if action not in valid_moves:
            info = {"valid_moves": valid_moves}
            return self._apply_vision_mask(), -2, False, truncated, info
            
        moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # 0: up, 1: right, 2: down, 3: left
        dr, dc = moves[action]
        
        new_row, new_col = current_row + dr, current_col + dc
        
        # Update facing direction based on movement
        self._facing_direction = action
        
        self._maze[current_row, current_col] = 0
        self._maze[new_row, new_col] = 2
        self._agent_pos = (new_row, new_col)
        self._visited_positions.add(self._agent_pos)  # Mark new position as visited
              
        if self._agent_pos == self._goal_pos:
            return self._apply_vision_mask(), 100, True, truncated, {}
 
        info = {"valid_moves": self._get_valid_moves(self._agent_pos)}
        return self._apply_vision_mask(), -1, False, truncated, info
    
    def render(self): # pragma: no cover
        custom_cmap = colors.ListedColormap(['white', 'black', 'blue', 'red', 'gray'])
        
        if self.fig is None or not plt.fignum_exists(self.fig.number):
            self.fig, self.ax = plt.subplots(figsize=(10, 5))
            self.ax.set_title(f"Maze ({self._width}x{self._height}) - Agent Vision")
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.im = self.ax.imshow(self._apply_vision_mask(), cmap=custom_cmap, interpolation='nearest')
        else:
            self.im.set_data(self._apply_vision_mask())
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
        return self._apply_vision_mask()
    
    def close(self): # pragma: no cover
        if self.fig is not None:
            plt.close(self.fig)
    