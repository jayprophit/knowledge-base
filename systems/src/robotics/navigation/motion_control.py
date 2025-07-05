import numpy as np
from typing import Dict, Any, List, Tuple

class MotionController:
    """
    Base motion controller for robot navigation.
    """
    def __init__(self):
        self.max_linear_velocity = 1.0  # m/s
        self.max_angular_velocity = 0.5  # rad/s
        
    def set_velocity_limits(self, linear: float, angular: float):
        """Set maximum velocity limits."""
        self.max_linear_velocity = linear
        self.max_angular_velocity = angular
        
    def compute_control(self, state: Dict[str, Any], goal: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute control commands to reach goal state.
        
        Args:
            state: Current robot state with position, orientation
            goal: Goal state with desired position
            
        Returns:
            Control commands (linear_velocity, angular_velocity)
        """
        raise NotImplementedError("Subclasses must implement compute_control()")


class PIDController(MotionController):
    """
    PID controller for robot motion control.
    """
    def __init__(self):
        super().__init__()
        # PID gains for linear velocity
        self.kp_linear = 0.5
        self.ki_linear = 0.0
        self.kd_linear = 0.1
        
        # PID gains for angular velocity
        self.kp_angular = 1.0
        self.ki_angular = 0.0
        self.kd_angular = 0.2
        
        # Error integrals
        self.linear_error_integral = 0.0
        self.angular_error_integral = 0.0
        
        # Previous errors
        self.prev_linear_error = 0.0
        self.prev_angular_error = 0.0
        
        # Time step
        self.dt = 0.1  # seconds
        
    def set_gains(self, kp_linear: float, ki_linear: float, kd_linear: float,
                 kp_angular: float, ki_angular: float, kd_angular: float):
        """Set PID controller gains."""
        self.kp_linear = kp_linear
        self.ki_linear = ki_linear
        self.kd_linear = kd_linear
        
        self.kp_angular = kp_angular
        self.ki_angular = ki_angular
        self.kd_angular = kd_angular
        
    def reset(self):
        """Reset controller state."""
        self.linear_error_integral = 0.0
        self.angular_error_integral = 0.0
        self.prev_linear_error = 0.0
        self.prev_angular_error = 0.0
        
    def compute_control(self, state: Dict[str, Any], goal: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute PID control commands.
        
        Args:
            state: Current robot state with position, orientation
            goal: Goal state with desired position
            
        Returns:
            Control commands (linear_velocity, angular_velocity)
        """
        # Extract positions
        robot_pos = state['position'][:2]  # x, y
        goal_pos = goal['position'][:2]    # x, y
        
        # Compute distance error
        distance_error = np.linalg.norm(goal_pos - robot_pos)
        
        # Compute heading error
        desired_heading = np.arctan2(goal_pos[1] - robot_pos[1], 
                                    goal_pos[0] - robot_pos[0])
        
        # Extract current orientation (assuming yaw is available)
        if 'yaw' in state:
            current_heading = state['yaw']
        else:
            # Extract yaw from rotation matrix
            rotation_matrix = state['orientation']
            current_heading = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
            
        # Normalize heading error to [-pi, pi]
        heading_error = desired_heading - current_heading
        while heading_error > np.pi:
            heading_error -= 2 * np.pi
        while heading_error < -np.pi:
            heading_error += 2 * np.pi
            
        # Update error integrals
        self.linear_error_integral += distance_error * self.dt
        self.angular_error_integral += heading_error * self.dt
        
        # Compute error derivatives
        linear_error_derivative = (distance_error - self.prev_linear_error) / self.dt
        angular_error_derivative = (heading_error - self.prev_angular_error) / self.dt
        
        # Update previous errors
        self.prev_linear_error = distance_error
        self.prev_angular_error = heading_error
        
        # Compute PID control
        linear_velocity = (
            self.kp_linear * distance_error +
            self.ki_linear * self.linear_error_integral +
            self.kd_linear * linear_error_derivative
        )
        
        angular_velocity = (
            self.kp_angular * heading_error +
            self.ki_angular * self.angular_error_integral +
            self.kd_angular * angular_error_derivative
        )
        
        # Apply velocity limits
        linear_velocity = max(-self.max_linear_velocity, 
                             min(self.max_linear_velocity, linear_velocity))
        angular_velocity = max(-self.max_angular_velocity,
                              min(self.max_angular_velocity, angular_velocity))
        
        # Slow down linear velocity when angular error is large
        linear_velocity *= max(0.1, 1 - abs(heading_error) / np.pi)
        
        # Stop when close to goal
        if distance_error < 0.1:  # 10 cm threshold
            linear_velocity = 0.0
            angular_velocity = 0.0
            
        return {
            'linear_velocity': linear_velocity,
            'angular_velocity': angular_velocity
        }


class DWAController(MotionController):
    """
    Dynamic Window Approach controller.
    Simulates multiple trajectories and selects the best one.
    """
    def __init__(self):
        super().__init__()
        self.obstacle_weight = 0.5
        self.goal_weight = 0.8
        self.heading_weight = 0.3
        self.clearance_weight = 0.1
        self.velocity_weight = 0.2
        
        self.velocity_resolution = 0.05  # m/s
        self.angular_velocity_resolution = 0.1  # rad/s
        self.simulation_time = 3.0  # seconds
        self.time_step = 0.1  # seconds
        
    def set_weights(self, obstacle_weight: float, goal_weight: float, 
                   heading_weight: float, clearance_weight: float,
                   velocity_weight: float):
        """Set weights for trajectory evaluation."""
        self.obstacle_weight = obstacle_weight
        self.goal_weight = goal_weight
        self.heading_weight = heading_weight
        self.clearance_weight = clearance_weight
        self.velocity_weight = velocity_weight
        
    def _simulate_trajectory(self, x: float, y: float, theta: float, 
                           v: float, w: float, obstacles: List[Tuple[float, float]]):
        """
        Simulate a trajectory with constant velocity and angular velocity.
        
        Args:
            x, y, theta: Initial state
            v, w: Linear and angular velocities
            obstacles: List of obstacle positions
            
        Returns:
            trajectory, min_obstacle_distance
        """
        trajectory = [(x, y)]
        min_distance = float('inf')
        
        for t in np.arange(0, self.simulation_time, self.time_step):
            # Update state with motion model
            theta += w * self.time_step
            x += v * np.cos(theta) * self.time_step
            y += v * np.sin(theta) * self.time_step
            
            # Add to trajectory
            trajectory.append((x, y))
            
            # Check minimum distance to obstacles
            for ox, oy in obstacles:
                distance = np.sqrt((x - ox) ** 2 + (y - oy) ** 2)
                min_distance = min(min_distance, distance)
                
        return trajectory, min_distance
        
    def _evaluate_trajectory(self, trajectory: List[Tuple[float, float]], 
                           min_obstacle_distance: float,
                           goal: Tuple[float, float], v: float, w: float):
        """Evaluate trajectory based on multiple criteria."""
        # Goal distance cost
        last_x, last_y = trajectory[-1]
        goal_x, goal_y = goal
        goal_distance = np.sqrt((goal_x - last_x) ** 2 + (goal_y - last_y) ** 2)
        goal_cost = goal_distance
        
        # Heading cost
        dx = goal_x - trajectory[0][0]
        dy = goal_y - trajectory[0][1]
        goal_heading = np.arctan2(dy, dx)
        trajectory_heading = np.arctan2(trajectory[-1][1] - trajectory[0][1],
                                       trajectory[-1][0] - trajectory[0][0])
        heading_cost = abs(goal_heading - trajectory_heading)
        
        # Obstacle cost
        if min_obstacle_distance == 0:
            obstacle_cost = float('inf')
        else:
            obstacle_cost = 1.0 / min_obstacle_distance
            
        # Clearance cost
        clearance_cost = 1.0 / (min_obstacle_distance + 0.001)
        
        # Velocity cost - prefer higher velocities
        velocity_cost = self.max_linear_velocity - v
        
        # Total cost with weights
        total_cost = (
            self.goal_weight * goal_cost +
            self.heading_weight * heading_cost +
            self.obstacle_weight * obstacle_cost +
            self.clearance_weight * clearance_cost +
            self.velocity_weight * velocity_cost
        )
        
        return total_cost
        
    def compute_control(self, state: Dict[str, Any], goal: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute control using Dynamic Window Approach.
        
        Args:
            state: Current robot state
            goal: Goal state
            
        Returns:
            Control commands (linear_velocity, angular_velocity)
        """
        # Extract current state
        x, y = state['position'][:2]
        
        if 'yaw' in state:
            theta = state['yaw']
        else:
            rotation_matrix = state['orientation']
            theta = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
            
        # Extract current velocities if available
        v_current = state.get('linear_velocity', 0.0)
        w_current = state.get('angular_velocity', 0.0)
        
        # Extract obstacles
        obstacles = state.get('obstacles', [])
        
        # Extract goal position
        goal_x, goal_y = goal['position'][:2]
        
        # Define dynamic window based on current velocities
        v_min = max(0, v_current - 0.2)
        v_max = min(self.max_linear_velocity, v_current + 0.2)
        w_min = max(-self.max_angular_velocity, w_current - 0.4)
        w_max = min(self.max_angular_velocity, w_current + 0.4)
        
        # Discretize velocity space
        v_samples = np.arange(v_min, v_max, self.velocity_resolution)
        w_samples = np.arange(w_min, w_max, self.angular_velocity_resolution)
        
        best_cost = float('inf')
        best_v = 0.0
        best_w = 0.0
        
        # Evaluate all possible velocity combinations
        for v in v_samples:
            for w in w_samples:
                trajectory, min_obstacle_distance = self._simulate_trajectory(
                    x, y, theta, v, w, obstacles)
                
                # Skip if collision
                if min_obstacle_distance < 0.2:  # 20cm safety margin
                    continue
                    
                cost = self._evaluate_trajectory(
                    trajectory, min_obstacle_distance, (goal_x, goal_y), v, w)
                
                if cost < best_cost:
                    best_cost = cost
                    best_v = v
                    best_w = w
        
        # If no valid trajectory found, slow down or turn in place
        if best_cost == float('inf'):
            if v_current > 0:
                best_v = v_current / 2.0
            else:
                best_v = 0.0
                
            # Turn toward goal
            goal_heading = np.arctan2(goal_y - y, goal_x - x)
            heading_diff = goal_heading - theta
            while heading_diff > np.pi:
                heading_diff -= 2 * np.pi
            while heading_diff < -np.pi:
                heading_diff += 2 * np.pi
                
            best_w = np.sign(heading_diff) * 0.3
        
        return {
            'linear_velocity': best_v,
            'angular_velocity': best_w
        }
