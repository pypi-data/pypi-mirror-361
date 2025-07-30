import pytest
import numpy as np
from mazegym.maze_gym_env import MazeEnvironment

@pytest.fixture
def custom_env():
    grid = np.ones((5, 5), dtype=np.int8)
    # Create a path from agent to goal
    grid[1:4, 2] = 0  # Vertical path
    grid[1, 1:3] = 0  # Connect agent
    grid[3, 2:4] = 0  # Connect goal
    # Place agent and goal
    grid[1, 1] = 2  # Agent
    grid[3, 3] = 3  # Goal

    return MazeEnvironment(grid=grid)

def test_user_input_grid():
    """Test that a user can provide a custom grid."""
    grid = np.ones((4, 4), dtype=np.int8)
    grid[1, 1:3] = 0
    grid[2, 1:3] = 0
    grid[1, 1] = 2  # Agent
    grid[2, 2] = 3  # Goal
    
    env = MazeEnvironment(grid=grid)
    
    obs, _ = env.reset()
    
    # Verify grid dimensions match
    assert obs.shape == (4, 4)
    # Verify agent position
    agent_pos = tuple(np.argwhere(obs == 2)[0])
    assert agent_pos == (1, 1)
    # Verify goal position
    goal_pos = tuple(np.argwhere(env._maze == 3)[0])
    assert goal_pos == (2, 2)

def test_random_generation():
    """Test that a random maze is generated when no grid is provided."""
    width, height = 7, 7
    env = MazeEnvironment(size=(width, height))
    
    obs, info = env.reset()
    
    assert obs.shape == (height, width)
    assert np.sum(obs == 2) == 1
    assert np.sum(env._maze == 3) == 1
    assert "valid_moves" in info
    assert len(info["valid_moves"]) > 0

def test_done_state():
    """Test that reaching the goal sets done to True."""
    grid = np.ones((3, 3), dtype=np.int8)
    grid[1, 0:3] = 0  # Horizontal path
    grid[1, 0] = 2  # Agent
    grid[1, 1] = 3  # Goal (adjacent to agent)
    env = MazeEnvironment(grid=grid)

    _, info = env.reset()
    valid_moves = info["valid_moves"]
    assert valid_moves == [1]
    
    # Execute the move
    obs, reward, done, truncated, _ = env.step(1)
    
    # Verify the done state
    print(obs)
    assert done is True
    assert reward == 100

def test_reset(custom_env):
    """Test that reset returns the environment to its initial state."""
    # Make a move
    obs, info = custom_env.reset()
    if "valid_moves" in info and len(info["valid_moves"]) > 0:
        action = info["valid_moves"][0]
        custom_env.step(action)
    
    # Reset and check it's back to initial state
    reset_maze, _ = custom_env.reset()
    
    # The reset maze should match the original grid with agent and goal
    agent_pos = np.argwhere(obs == 2)[0]
    goal_pos = np.argwhere(custom_env._maze == 3)[0]  # Check internal maze

    reset_agent_pos = np.argwhere(reset_maze == 2)[0]
    reset_goal_pos = np.argwhere(custom_env._maze == 3)[0]  # Check internal maze
    
    assert np.array_equal(reset_agent_pos, agent_pos)
    assert np.array_equal(reset_goal_pos, goal_pos)

def test_valid_move(custom_env):
    """Test taking a valid move."""
    _, info = custom_env.reset()
    
    assert "valid_moves" in info
    assert info["valid_moves"] == [1]

    next_maze, reward, done, truncated, next_info = custom_env.step(1)
    
    # Verify the step returns all expected values
    assert isinstance(next_maze, np.ndarray)
    assert isinstance(reward, (int, float))
    assert isinstance(done, bool)
    assert isinstance(truncated, bool)
    assert isinstance(next_info, dict)
    
    # Check that agent moved (should be exactly one agent)
    agent_position = np.argwhere(next_maze == 2).tolist()
    assert agent_position == [[1, 2]]

def test_invalid_move(custom_env):
    """Test that an invalid action returns -2 reward and doesn't change position."""
    _, _ = custom_env.reset()
    initial_agent_pos = custom_env._agent_pos
    
    # Test with invalid action index
    invalid_action = 10  # An action index that doesn't exist
    obs, reward, done, _, info = custom_env.step(invalid_action)
    
    # Should return -2 reward for invalid move
    assert reward == -2
    # Agent position should not change
    assert custom_env._agent_pos == initial_agent_pos
    # Episode should not be done
    assert done == False
    # Should still provide valid moves info
    assert "valid_moves" in info

def test_vision_system():
    """Test that the agent only sees in the direction they're facing (starts facing right)."""
    grid = np.ones((5, 5), dtype=np.int8)
    grid[1:4, 1:4] = 0  # Open area
    grid[2, 2] = 2  # Agent in center
    grid[3, 3] = 3  # Goal in corner
    
    env = MazeEnvironment(grid=grid, vision_range=2)
    obs, _ = env.reset()
    
    # Agent starts facing right, so can only see straight ahead (no diagonals)
    expected = np.array([
        [4, 4, 4, 4, 4],  # Nothing visible in this row
        [4, 4, 4, 4, 4],  # Nothing visible in this row
        [4, 4, 2, 0, 1],  # Agent and path straight ahead with wall
        [4, 4, 4, 4, 4],  # Nothing visible in this row
        [4, 4, 4, 4, 4]   # Nothing visible in this row
    ], dtype=np.int8)
    
    assert np.array_equal(obs, expected)

def test_visited_paths_remain_visible():
    """Test that previously visited paths remain visible and don't become fog of war."""
    grid = np.ones((5, 5), dtype=np.int8)
    grid[1:4, 1:4] = 0  # Open area
    grid[2, 2] = 2  # Agent in center
    grid[3, 3] = 3  # Goal in corner
    
    env = MazeEnvironment(grid=grid, vision_range=2)
    obs, _ = env.reset()
    
    # Initially agent at (2,2) facing right
    # Move right to (2,3)
    obs, _, _, _, _ = env.step(1)  # Move right
    
    # Now agent is at (2,3) facing right, but (2,2) should still be visible as visited
    expected_after_right = np.array([
        [4, 4, 4, 4, 4],  # Nothing visible in this direction
        [4, 4, 4, 4, 4],  # Nothing visible in this direction
        [4, 4, 0, 2, 1],  # Previous position (2,2) still visible, agent now at (2,3), wall ahead
        [4, 4, 4, 4, 4],  # Nothing visible in this direction
        [4, 4, 4, 4, 4]   # Nothing visible in this direction
    ], dtype=np.int8)
    
    assert np.array_equal(obs, expected_after_right)

def test_unlimited_vision():
    """Test that when vision_range=None, the agent can see everything."""
    grid = np.ones((5, 5), dtype=np.int8)
    grid[1:4, 1:4] = 0  # Open area
    grid[2, 2] = 2  # Agent in center
    grid[3, 3] = 3  # Goal in corner
    
    env = MazeEnvironment(grid=grid, vision_range=None)
    obs, _ = env.reset()
    
    # With unlimited vision, observation should match the internal maze exactly
    expected = np.array([
        [1, 1, 1, 1, 1],  # Full maze visible
        [1, 0, 0, 0, 1],  # Full maze visible
        [1, 0, 2, 0, 1],  # Agent and full maze visible
        [1, 0, 0, 3, 1],  # Goal and full maze visible
        [1, 1, 1, 1, 1]   # Full maze visible
    ], dtype=np.int8)
    
    assert np.array_equal(obs, expected)
    assert np.array_equal(obs, env._maze)  # Should be identical to internal maze