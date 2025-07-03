import numpy as np
import time
from typing import Dict, Any

class SensorFusion:
    """
    Sensor fusion implementation for robot localization.
    Combines data from multiple sensors (IMU, GPS, odometry) to estimate robot state.
    """
    def __init__(self):
        self.state = {
            'position': np.zeros(3),  # x, y, z
            'orientation': np.identity(3),  # Rotation matrix
            'velocity': np.zeros(3),
            'angular_velocity': np.zeros(3)
        }
        self.covariance = np.eye(15)  # State covariance
        self.last_update = time.time()
        
    def update(self, sensors: Dict[str, Any]):
        """
        Update the state estimate with new sensor data.
        
        Args:
            sensors: Dictionary containing sensor data
                - 'imu': IMU data with accelerations and angular velocities
                - 'odom': Odometry data with wheel encoder readings
                - 'gps': GPS data with position and accuracy
        
        Returns:
            Updated state dictionary
        """
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Predict state based on previous state and time elapsed
        if dt > 0 and dt < 1.0:  # Reasonable time step
            self._predict_state(dt)
            
        # Update with IMU data
        if 'imu' in sensors:
            self._update_imu(sensors['imu'], dt)
            
        # Update with odometry data
        if 'odom' in sensors:
            self._update_odometry(sensors['odom'])
            
        # Update with GPS data
        if 'gps' in sensors and sensors['gps'].get('valid', False):
            self._update_gps(sensors['gps'])
            
        return self.state
        
    def _predict_state(self, dt):
        """Predict next state based on motion model."""
        # Simple linear motion model
        self.state['position'] += self.state['velocity'] * dt
        
        # Update covariance based on process noise
        # (simplified - in practice would use proper noise model)
        process_noise = np.eye(15) * 0.01
        self.covariance += process_noise * dt
        
    def _update_imu(self, imu_data, dt):
        """Update state with IMU data."""
        if 'acceleration' in imu_data:
            # Remove gravity component (assuming orientation is known)
            gravity = np.array([0, 0, 9.81])  # In body frame when level
            accel = imu_data['acceleration'] - gravity
            
            # Update velocity using acceleration
            self.state['velocity'] += accel * dt
            
        if 'gyro' in imu_data:
            # Update orientation using angular velocity
            self.state['angular_velocity'] = imu_data['gyro']
            
            # Simple orientation update (would use quaternions in practice)
            skew_matrix = np.array([
                [0, -imu_data['gyro'][2], imu_data['gyro'][1]],
                [imu_data['gyro'][2], 0, -imu_data['gyro'][0]],
                [-imu_data['gyro'][1], imu_data['gyro'][0], 0]
            ])
            
            self.state['orientation'] += skew_matrix.dot(self.state['orientation']) * dt
            
            # Orthonormalize rotation matrix
            u, _, vh = np.linalg.svd(self.state['orientation'])
            self.state['orientation'] = u.dot(vh)
            
    def _update_odometry(self, odom_data):
        """Update state with odometry data."""
        if 'position' in odom_data:
            # Simple weighted average of position estimates
            weight = 0.3  # Weight for odometry position
            self.state['position'] = (1 - weight) * self.state['position'] + weight * odom_data['position']
            
        if 'velocity' in odom_data:
            # Simple weighted average of velocity estimates
            weight = 0.5  # Weight for odometry velocity
            self.state['velocity'] = (1 - weight) * self.state['velocity'] + weight * odom_data['velocity']
            
    def _update_gps(self, gps_data):
        """Update state with GPS data."""
        if 'position' in gps_data:
            # Kalman filter-like update based on accuracy
            accuracy = gps_data.get('accuracy', 5.0)  # Default 5m accuracy
            
            # Compute Kalman gain based on relative uncertainties
            # Higher accuracy (lower value) means more weight to GPS
            k = 1.0 / (1.0 + accuracy)
            
            # Update position
            self.state['position'] = (1 - k) * self.state['position'] + k * gps_data['position']
            
            # Reduce covariance for position states
            pos_indices = [0, 1, 2]  # X, Y, Z position indices
            for idx in pos_indices:
                self.covariance[idx, idx] *= (1 - k)
