"""
Swarm Robotics System Module for Advanced Robotics
-------------------------------------------------
Implements decentralized, scalable, robust, and emergent swarm behaviors
for multi-robot systems, including communication, consensus, and task allocation.
"""

import numpy as np
import random
from typing import List, Tuple, Optional

class SwarmRobot:
    """
    Represents a single robot in the swarm with simple local rules.
    """
    def __init__(self, robot_id: int, position: np.ndarray):
        self.id = robot_id
        self.position = position
        self.goal = None
        self.neighbors: List['SwarmRobot'] = []
        self.status = "idle"
    def sense_neighbors(self, swarm: List['SwarmRobot'], radius: float = 1.0):
        self.neighbors = [r for r in swarm if r is not self and np.linalg.norm(self.position - r.position) <= radius]
    def move_towards(self, target: np.ndarray, speed: float = 0.1):
        direction = target - self.position
        if np.linalg.norm(direction) > 1e-6:
            direction = direction / np.linalg.norm(direction)
            self.position += speed * direction
    def avoid_collisions(self, min_dist: float = 0.5):
        for other in self.neighbors:
            dist = np.linalg.norm(self.position - other.position)
            if dist < min_dist:
                self.position -= 0.05 * (self.position - other.position)
    def update(self, swarm: List['SwarmRobot'], goal: Optional[np.ndarray] = None):
        self.sense_neighbors(swarm)
        if goal is not None:
            self.move_towards(goal)
        self.avoid_collisions()
    def __repr__(self):
        return f"SwarmRobot(id={self.id}, pos={self.position}, status={self.status})"

class SwarmController:
    """
    Controls the entire swarm, manages communication, consensus, and task allocation.
    """
    def __init__(self, num_robots: int, space_dim: int = 2):
        self.robots = [SwarmRobot(i, np.random.rand(space_dim)) for i in range(num_robots)]
        self.goal = np.ones(space_dim)
        self.history: List[List[float]] = []
    def broadcast_goal(self, goal: np.ndarray):
        self.goal = goal
        for robot in self.robots:
            robot.goal = goal
    def consensus(self):
        # Simple average consensus on goal position
        avg_goal = np.mean([r.goal for r in self.robots if r.goal is not None], axis=0)
        self.broadcast_goal(avg_goal)
    def task_allocation(self, tasks: List[np.ndarray]):
        # Assign each robot to the nearest task
        for robot in self.robots:
            closest_task = min(tasks, key=lambda t: np.linalg.norm(robot.position - t))
            robot.goal = closest_task
    def step(self):
        for robot in self.robots:
            robot.update(self.robots, robot.goal)
        self.history.append([r.position.copy() for r in self.robots])
    def run(self, steps: int = 50):
        for _ in range(steps):
            self.step()
    def get_positions(self) -> List[np.ndarray]:
        return [r.position for r in self.robots]
    def __repr__(self):
        return f"SwarmController(num_robots={len(self.robots)})"

if __name__ == "__main__":
    # Example usage: 10 robots, 2D space, move to goal at (1,1)
    swarm = SwarmController(num_robots=10, space_dim=2)
    swarm.broadcast_goal(np.array([1.0, 1.0]))
    swarm.run(steps=30)
    for idx, robot in enumerate(swarm.robots):
        print(f"Robot {idx}: Position {robot.position}")
