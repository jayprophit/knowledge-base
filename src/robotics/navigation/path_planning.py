from typing import List, Tuple, Dict, Optional, Any
import numpy as np
import heapq

Point = Tuple[int, int]
Grid = List[List[int]]

class PathPlanner:
    """
    Base class for path planning algorithms.
    """
    def __init__(self):
        self.obstacles = []
        self.grid_resolution = 0.1  # meters per grid cell
        
    def set_obstacles(self, obstacles: List[Dict[str, Any]]):
        """Set obstacle list for planning."""
        self.obstacles = obstacles
        
    def plan(self, start: Point, goal: Point, grid: Optional[Grid] = None) -> List[Point]:
        """
        Plan a path from start to goal.
        
        Args:
            start: Start position (x, y)
            goal: Goal position (x, y)
            grid: Optional occupancy grid (0 = free, 1 = occupied)
            
        Returns:
            List of waypoints from start to goal
        """
        raise NotImplementedError("Subclasses must implement plan()")


class AStarPlanner(PathPlanner):
    """
    A* path planning implementation.
    """
    def __init__(self):
        super().__init__()
        
    def heuristic(self, a: Point, b: Point) -> float:
        """Calculate heuristic (Euclidean distance)."""
        return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
        
    def get_neighbors(self, current: Point, grid: Grid) -> List[Point]:
        """Get valid neighboring cells."""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), 
                       (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            x, y = current[0] + dx, current[1] + dy
            if (0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == 0):
                neighbors.append((x, y))
        return neighbors
        
    def plan(self, start: Point, goal: Point, grid: Grid) -> List[Point]:
        """
        A* path planning on a grid.
        
        Args:
            start: Start position (x, y)
            goal: Goal position (x, y)
            grid: Occupancy grid (0 = free, 1 = occupied)
            
        Returns:
            List of waypoints from start to goal
        """
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path
                
            for neighbor in self.get_neighbors(current, grid):
                # Distance from current to neighbor is 1 for orthogonal, sqrt(2) for diagonal
                distance = 1 if (neighbor[0] == current[0] or neighbor[1] == current[1]) else 1.414
                tentative_g = g_score[current] + distance
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # No path found


class RRTPlanner(PathPlanner):
    """
    Rapidly-exploring Random Tree (RRT) path planning implementation.
    """
    def __init__(self, max_iterations=1000, step_size=1.0):
        super().__init__()
        self.max_iterations = max_iterations
        self.step_size = step_size
        
    def _random_point(self, grid: Grid) -> Point:
        """Generate a random point in the grid."""
        x = np.random.randint(0, len(grid))
        y = np.random.randint(0, len(grid[0]))
        return (x, y)
        
    def _nearest_node(self, nodes: List[Point], point: Point) -> Point:
        """Find the nearest node in the tree to the given point."""
        distances = [np.sqrt((n[0] - point[0])**2 + (n[1] - point[1])**2) for n in nodes]
        return nodes[np.argmin(distances)]
        
    def _steer(self, from_point: Point, to_point: Point) -> Point:
        """Steer from one point toward another with limited step size."""
        dx = to_point[0] - from_point[0]
        dy = to_point[1] - from_point[1]
        
        dist = np.sqrt(dx**2 + dy**2)
        
        if dist <= self.step_size:
            return to_point
            
        # Normalize and scale
        dx = dx / dist * self.step_size
        dy = dy / dist * self.step_size
        
        return (int(from_point[0] + dx), int(from_point[1] + dy))
        
    def _is_collision_free(self, p1: Point, p2: Point, grid: Grid) -> bool:
        """Check if the line between p1 and p2 is collision free."""
        # Simple Bresenham line algorithm
        x0, y0 = p1
        x1, y1 = p2
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while x0 != x1 or y0 != y1:
            if 0 <= x0 < len(grid) and 0 <= y0 < len(grid[0]):
                if grid[x0][y0] == 1:  # Obstacle
                    return False
            else:
                return False  # Out of bounds
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
                
        return True
        
    def plan(self, start: Point, goal: Point, grid: Grid) -> List[Point]:
        """
        RRT path planning on a grid.
        
        Args:
            start: Start position (x, y)
            goal: Goal position (x, y)
            grid: Occupancy grid (0 = free, 1 = occupied)
            
        Returns:
            List of waypoints from start to goal
        """
        nodes = [start]
        parent = {start: None}
        
        for _ in range(self.max_iterations):
            # With probability 0.05, sample the goal directly
            if np.random.random() < 0.05:
                rand_point = goal
            else:
                rand_point = self._random_point(grid)
                
            # Skip if random point is in obstacle
            if grid[rand_point[0]][rand_point[1]] == 1:
                continue
                
            # Find nearest node in the tree
            nearest = self._nearest_node(nodes, rand_point)
            
            # Steer towards random point
            new_node = self._steer(nearest, rand_point)
            
            # Check if path is collision free
            if self._is_collision_free(nearest, new_node, grid):
                nodes.append(new_node)
                parent[new_node] = nearest
                
                # Check if we can connect to goal
                if self.heuristic(new_node, goal) < self.step_size and self._is_collision_free(new_node, goal, grid):
                    nodes.append(goal)
                    parent[goal] = new_node
                    
                    # Reconstruct path
                    path = [goal]
                    node = goal
                    while parent[node] is not None:
                        node = parent[node]
                        path.append(node)
                    path.reverse()
                    return path
                    
        return []  # No path found
        
    def heuristic(self, a: Point, b: Point) -> float:
        """Calculate heuristic (Euclidean distance)."""
        return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)
