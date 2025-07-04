import unittest
import numpy as np
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from robotics.navigation.sensor_fusion import SensorFusion
from robotics.navigation.path_planning import AStarPlanner, RRTPlanner
from robotics.navigation.motion_control import PIDController, DWAController


class TestSensorFusion(unittest.TestCase):
    """Test cases for the SensorFusion module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sensor fusion with typical noise parameters
        self.fusion = SensorFusion()
        
    def test_initialization(self):
        """Test proper initialization of the SensorFusion class."""
        self.assertIsNotNone(self.fusion.state)
        self.assertIsNotNone(self.fusion.covariance)
        self.assertEqual(self.fusion.state.shape, (6, 1))
        self.assertEqual(self.fusion.covariance.shape, (6, 6))
        
    def test_predict_state(self):
        """Test state prediction with control inputs."""
        # Set initial state: [x, y, θ, v_x, v_y, ω]
        initial_state = np.array([[0], [0], [0], [0], [0], [0]])
        self.fusion.state = initial_state.copy()
        
        # Create control input: [v, ω]
        control = np.array([[1.0], [0.2]])
        dt = 0.1  # Time step
        
        # Predict next state
        self.fusion.predict(control, dt)
        
        # After prediction with v=1.0, ω=0.2 for dt=0.1:
        # x should increase by approximately v*dt*cos(θ)
        # y should increase by approximately v*dt*sin(θ)
        # θ should increase by approximately ω*dt
        # v_x should be approximately v*cos(θ)
        # v_y should be approximately v*sin(θ)
        # ω should be approximately equal to control[1]
        
        self.assertAlmostEqual(self.fusion.state[0, 0], 0.1, delta=0.01)  # x ≈ 0.1
        self.assertAlmostEqual(self.fusion.state[1, 0], 0.0, delta=0.01)  # y ≈ 0
        self.assertAlmostEqual(self.fusion.state[2, 0], 0.02, delta=0.01)  # θ ≈ 0.02
        self.assertAlmostEqual(self.fusion.state[3, 0], 1.0, delta=0.01)  # v_x ≈ 1.0
        self.assertAlmostEqual(self.fusion.state[4, 0], 0.0, delta=0.01)  # v_y ≈ 0
        self.assertAlmostEqual(self.fusion.state[5, 0], 0.2, delta=0.01)  # ω ≈ 0.2
        
    def test_update_with_gps(self):
        """Test updating state with GPS measurement."""
        # Set initial state with some uncertainty
        self.fusion.state = np.array([[1.0], [2.0], [0.1], [0.5], [0.0], [0.1]])
        
        # GPS measurement: [x, y]
        gps_measurement = np.array([[1.2], [2.1]])
        gps_covariance = np.array([[0.01, 0], [0, 0.01]])  # Low uncertainty in GPS
        
        # Update with GPS
        self.fusion.update_position(gps_measurement, gps_covariance)
        
        # State should be updated to be closer to the GPS measurement
        self.assertGreater(self.fusion.state[0, 0], 1.0)  # x should increase
        self.assertGreater(self.fusion.state[1, 0], 2.0)  # y should increase
        
    def test_update_with_imu(self):
        """Test updating state with IMU measurement."""
        # Set initial state
        self.fusion.state = np.array([[1.0], [2.0], [0.1], [0.5], [0.0], [0.1]])
        
        # IMU measurement: [θ, ω]
        imu_measurement = np.array([[0.15], [0.12]])
        imu_covariance = np.array([[0.001, 0], [0, 0.001]])  # Low uncertainty in IMU
        
        # Update with IMU
        self.fusion.update_orientation(imu_measurement, imu_covariance)
        
        # Orientation should be updated to be closer to the IMU measurement
        self.assertGreater(self.fusion.state[2, 0], 0.1)  # θ should increase
        self.assertNotEqual(self.fusion.state[5, 0], 0.1)  # ω should be updated
        

class TestPathPlanning(unittest.TestCase):
    """Test cases for path planning algorithms."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple grid for testing
        # 0 = free, 1 = obstacle
        self.grid = np.array([
            [0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0]
        ])
        self.grid_resolution = 1.0
        
    def test_astar_path_exists(self):
        """Test A* planning when a path exists."""
        planner = AStarPlanner(grid_map=self.grid, resolution=self.grid_resolution)
        start = (0, 0)  # Start at top-left
        goal = (4, 4)   # Goal at bottom-right
        
        path = planner.plan(start, goal)
        
        # Path should exist and be a list of waypoints
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 0)
        
        # First point should be start
        self.assertEqual(path[0], start)
        
        # Last point should be goal
        self.assertEqual(path[-1], goal)
        
    def test_astar_path_blocked(self):
        """Test A* planning when path is completely blocked."""
        # Create a grid with a wall separating start and goal
        blocked_grid = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ])
        
        planner = AStarPlanner(grid_map=blocked_grid, resolution=self.grid_resolution)
        start = (0, 0)  # Start at top-left
        goal = (4, 4)   # Goal at bottom-right
        
        path = planner.plan(start, goal)
        
        # Path should not exist
        self.assertIsNone(path)
        
    def test_rrt_planning(self):
        """Test RRT planning in open space."""
        planner = RRTPlanner(
            bounds=[(0, 4), (0, 4)],  # Match grid size
            obstacle_func=lambda x, y: self.grid[int(y), int(x)] == 1 if 0 <= int(y) < 5 and 0 <= int(x) < 5 else True
        )
        
        start = (0, 0)  # Start at top-left
        goal = (4, 4)   # Goal at bottom-right
        
        # Set a seed for reproducibility
        np.random.seed(42)
        
        path = planner.plan(start, goal, max_iterations=1000, goal_sample_rate=0.2)
        
        # Path should exist
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 0)
        
        # First point should be start
        self.assertAlmostEqual(path[0][0], start[0], delta=0.1)
        self.assertAlmostEqual(path[0][1], start[1], delta=0.1)
        
        # Last point should be near goal (RRT doesn't guarantee exact goal)
        self.assertAlmostEqual(path[-1][0], goal[0], delta=0.5)
        self.assertAlmostEqual(path[-1][1], goal[1], delta=0.5)
        

class TestMotionControl(unittest.TestCase):
    """Test cases for motion control algorithms."""
    
    def test_pid_controller(self):
        """Test PID controller for path following."""
        controller = PIDController(kp=1.0, ki=0.1, kd=0.05)
        
        # Test with zero error
        vel_cmd = controller.compute(0.0, 0.1)
        self.assertAlmostEqual(vel_cmd, 0.0)
        
        # Test with positive error
        vel_cmd = controller.compute(2.0, 0.1)
        self.assertGreater(vel_cmd, 0.0)
        
        # Test with negative error
        vel_cmd = controller.compute(-2.0, 0.1)
        self.assertLess(vel_cmd, 0.0)
        
        # Test integration over time
        vel_cmd1 = controller.compute(1.0, 0.1)
        vel_cmd2 = controller.compute(1.0, 0.1)  # Same error
        self.assertGreater(vel_cmd2, vel_cmd1)  # Output should increase due to I term
        
    def test_dwa_controller(self):
        """Test Dynamic Window Approach controller."""
        # Create a controller with simple constraints
        controller = DWAController(
            max_speed=1.0,
            min_speed=-0.5,
            max_yaw_rate=1.0,
            max_accel=1.0,
            max_delta_yaw_rate=1.0,
            v_resolution=0.1,
            yaw_rate_resolution=0.1
        )
        
        # Current state: [x, y, θ, v, ω]
        curr_state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        
        # Goal position
        goal = np.array([5.0, 5.0])
        
        # Simple obstacle list: [(x, y, radius), ...]
        obstacles = [(2.0, 2.0, 1.0)]
        
        # Calculate control input
        v, w = controller.compute(curr_state, goal, obstacles)
        
        # Should return valid velocity commands
        self.assertIsNotNone(v)
        self.assertIsNotNone(w)
        self.assertLessEqual(abs(v), 1.0)  # Within max speed
        self.assertLessEqual(abs(w), 1.0)  # Within max yaw rate
        
        # With goal ahead, v should be positive
        self.assertGreater(v, 0.0)


if __name__ == '__main__':
    unittest.main()
