# Physics Simulation for CAD Models

This document covers the implementation of physics simulations for CAD models, including rigid body dynamics, material interactions, and stress analysis.

## Table of Contents
- [1. Rigid Body Dynamics](#1-rigid-body-dynamics)
- [2. Stress-Strain Analysis](#2-stress-strain-analysis)
- [3. Thermal Analysis](#3-thermal-analysis)
- [4. Impact Simulation](#4-impact-simulation)
- [5. Integration with CAD](#5-integration-with-cad)
- [6. Advanced Simulations](#6-advanced-simulations)

## 1. Rigid Body Dynamics

### Basic Motion Simulation
```python
import numpy as np
from scipy.integrate import solve_ivp

class RigidBody:
    def __init__(self, mass, position, velocity, orientation=(0, 0, 0, 1)):
        self.mass = mass  # kg
        self.position = np.array(position, dtype=float)  # [x, y, z] in meters
        self.velocity = np.array(velocity, dtype=float)  # [vx, vy, vz] in m/s
        self.orientation = np.array(orientation, dtype=float)  # Quaternion [x, y, z, w]
        self.angular_velocity = np.zeros(3)  # [ωx, ωy, ωz] in rad/s
        self.forces = []
        self.torques = []
    
    def apply_force(self, force, point=None):
        """Apply a force at a specific point (in world coordinates)."""
        self.forces.append(np.array(force, dtype=float))
        if point is not None:
            r = np.array(point, dtype=float) - self.position
            self.torques.append(np.cross(r, force))
    
    def apply_torque(self, torque):
        """Apply a pure torque."""
        self.torques.append(np.array(torque, dtype=float))
    
    def reset_forces(self):
        """Clear all forces and torques."""
        self.forces = []
        self.torques = []
    
    def step(self, dt):
        """Advance simulation by time step dt."""
        # Sum all forces and torques
        total_force = sum(self.forces, np.zeros(3))
        total_torque = sum(self.torques, np.zeros(3))
        
        # Linear motion (F = ma)
        acceleration = total_force / self.mass
        self.velocity += acceleration * dt
        self.position += self.velocity * dt
        
        # Angular motion (τ = Iα, simplified)
        # Note: This is a simplified version assuming spherical inertia
        moment_of_inertia = (2/5) * self.mass * 0.1**2  # For a sphere
        angular_acceleration = total_torque / moment_of_inertia
        self.angular_velocity += angular_acceleration * dt
        
        # Update orientation (simplified)
        # In a real implementation, you'd use quaternion integration
        self.reset_forces()

def simulate_physics(bodies, duration, dt=0.01):
    """Simulate physics for multiple bodies."""
    time_steps = np.arange(0, duration, dt)
    
    for t in time_steps:
        # Apply forces (e.g., gravity)
        for body in bodies:
            body.apply_force([0, 0, -9.81 * body.mass])  # Gravity
        
        # Step simulation
        for body in bodies:
            body.step(dt)
    
    return bodies
```

### Example: Projectile Motion
```python
# Create a projectile
projectile = RigidBody(
    mass=1.0,  # kg
    position=[0, 0, 0],  # m
    velocity=[10, 0, 10]  # m/s
)

# Simulate for 2 seconds with 0.1s time steps
simulate_physics([projectile], duration=2.0, dt=0.1)
print(f"Final position: {projectile.position}")
print(f"Final velocity: {projectile.velocity}")
```

## 2. Stress-Strain Analysis

### Basic Stress Calculation
```python
def calculate_stress(force, area, angle=0):
    """
    Calculate normal and shear stress.
    
    Args:
        force: Applied force vector [Fx, Fy, Fz] in N
        area: Cross-sectional area in m²
        angle: Angle between force and surface normal in radians
    
    Returns:
        tuple: (normal_stress, shear_stress) in Pa
    """
    force_magnitude = np.linalg.norm(force)
    normal_force = force_magnitude * np.cos(angle)
    shear_force = force_magnitude * np.sin(angle)
    
    normal_stress = normal_force / area if area > 0 else 0
    shear_stress = shear_force / area if area > 0 else 0
    
    return normal_stress, shear_stress

def calculate_strain(stress, youngs_modulus):
    """Calculate strain using Hooke's Law."""
    return stress / youngs_modulus if youngs_modulus > 0 else 0

def von_mises_stress(principal_stresses):
    """Calculate von Mises stress from principal stresses."""
    s1, s2, s3 = principal_stresses
    return np.sqrt(0.5 * ((s1-s2)**2 + (s2-s3)**2 + (s3-s1)**2))
```

### Example: Beam Bending
```python
class Beam:
    def __init__(self, length, width, height, material):
        self.length = length  # m
        self.width = width    # m
        self.height = height  # m
        self.material = material  # Material object
        
        # Calculate cross-sectional properties
        self.area = width * height
        self.I = (width * height**3) / 12  # Second moment of area
    
    def bending_stress(self, bending_moment, y):
        """Calculate bending stress at distance y from neutral axis."""
        return (bending_moment * y) / self.I
    
    def max_bending_stress(self, bending_moment):
        """Calculate maximum bending stress (at extreme fiber)."""
        return self.bending_stress(bending_moment, self.height/2)
    
    def deflection(self, load, x, support='cantilever'):
        """Calculate deflection at distance x from support."""
        E = self.material.mechanical_youngs_modulus
        I = self.I
        
        if support == 'cantilever':
            if x > self.length:
                return 0
            # For a point load at the free end
            return (load * x**2) * (3*self.length - x) / (6 * E * I)
        elif support == 'simply_supported':
            if x < 0 or x > self.length:
                return 0
            # For a point load at the center
            if x <= self.length/2:
                return (load * x * (3*self.length**2 - 4*x**2)) / (48 * E * I)
            else:
                return self.deflection(load, self.length - x, 'simply_supported')
        else:
            raise ValueError(f"Unsupported beam type: {support}")

# Example usage
from materials_database import Material

# Create a steel beam
steel = Material('steel_aisi_1018')
beam = Beam(length=2.0, width=0.05, height=0.1, material=steel)

# Calculate maximum stress under a bending moment
moment = 1000  # N·m
max_stress = beam.max_bending_stress(moment)
print(f"Maximum bending stress: {max_stress/1e6:.2f} MPa")

# Check against yield strength
safety_factor = steel.mechanical_yield_strength / max_stress
print(f"Safety factor: {safety_factor:.2f}")
```

## 3. Thermal Analysis

### Heat Transfer Simulation
```python
class ThermalSimulation:
    def __init__(self, nodes, conductivity, specific_heat, density):
        """
        Initialize thermal simulation.
        
        Args:
            nodes: List of node positions [[x1,y1,z1], [x2,y2,z2], ...]
            conductivity: Thermal conductivity (W/m·K)
            specific_heat: Specific heat capacity (J/kg·K)
            density: Material density (kg/m³)
        """
        self.nodes = np.array(nodes)
        self.temperatures = np.zeros(len(nodes))
        self.conductivity = conductivity
        self.specific_heat = specific_heat
        self.density = density
        
        # Precompute distances between nodes
        self.distances = np.zeros((len(nodes), len(nodes)))
        for i in range(len(nodes)):
            for j in range(i+1, len(nodes)):
                dist = np.linalg.norm(nodes[i] - nodes[j])
                self.distances[i,j] = dist
                self.distances[j,i] = dist
    
    def set_initial_temperature(self, temp):
        """Set initial temperature for all nodes."""
        self.temperatures = np.full(len(self.nodes), temp)
    
    def set_boundary_condition(self, node_indices, temp):
        """Set fixed temperature boundary conditions."""
        self.temperatures[node_indices] = temp
    
    def step(self, dt, heat_sources=None):
        """Advance thermal simulation by time step dt."""
        if heat_sources is None:
            heat_sources = np.zeros(len(self.nodes))
            
        new_temps = np.copy(self.temperatures)
        
        for i in range(len(self.nodes)):
            # Skip boundary nodes
            if self.temperatures[i] != new_temps[i]:
                continue
                
            # Heat diffusion (simplified)
            heat_flux = 0
            for j in range(len(self.nodes)):
                if i != j and self.distances[i,j] > 0:
                    temp_diff = self.temperatures[j] - self.temperatures[i]
                    heat_flux += self.conductivity * temp_diff / self.distances[i,j]**2
            
            # Update temperature
            new_temps[i] += (heat_flux + heat_sources[i]) * dt / (self.specific_heat * self.density)
        
        self.temperatures = new_temps
        return self.temperatures

def simulate_thermal_analysis():
    # Create a simple 1D rod with 10 nodes
    nodes = np.linspace(0, 1, 10).reshape(-1, 1)
    
    # Material properties for steel
    sim = ThermalSimulation(
        nodes=nodes,
        conductivity=50,  # W/m·K
        specific_heat=500,  # J/kg·K
        density=7800  # kg/m³
    )
    
    # Initial temperature: 20°C
    sim.set_initial_temperature(20)
    
    # Boundary conditions: fixed temperature at ends
    sim.set_boundary_condition([0], 100)  # 100°C at left end
    sim.set_boundary_condition([-1], 0)   # 0°C at right end
    
    # Simulate for 100 time steps
    for _ in range(100):
        sim.step(dt=0.1)
    
    return sim.temperatures
```

## 4. Impact Simulation

### Simple Impact Model
```python
def calculate_impact(mass, velocity, stiffness, damping=0.1):
    """
    Calculate impact force using a spring-damper model.
    
    Args:
        mass: Mass of impacting object (kg)
        velocity: Impact velocity (m/s)
        stiffness: Contact stiffness (N/m)
        damping: Damping ratio (dimensionless)
    
    Returns:
        dict: Impact results including max force, duration, etc.
    """
    # Natural frequency (rad/s)
    omega_n = np.sqrt(stiffness / mass)
    
    # Damped natural frequency
    omega_d = omega_n * np.sqrt(1 - damping**2)
    
    # Time of maximum compression
    t_max = np.pi / omega_d
    
    # Maximum force (simplified)
    max_force = velocity * np.sqrt(mass * stiffness) * np.exp(-damping * omega_n * t_max / 2)
    
    return {
        'max_force': max_force,
        'contact_time': 2 * t_max,
        'natural_frequency': omega_n,
        'damped_frequency': omega_d
    }
```

## 5. Integration with CAD

### FreeCAD Integration
```python
import FreeCAD
import Part

def create_stress_visualization(displacements, scale_factor=1000):
    """Create a visualization of stress/displacement in FreeCAD."""
    doc = FreeCAD.ActiveDocument
    
    # Create a copy of the original shape
    original = doc.ActiveObject
    if not original or not hasattr(original, 'Shape'):
        raise ValueError("No valid object selected")
    
    # Create displaced shape
    displaced = original.Shape.copy()
    vertices = displaced.Vertexes
    
    # Apply displacements
    for i, vertex in enumerate(vertices):
        if i < len(displacements):
            disp = np.array(displacements[i]) * scale_factor
            vertex.Point.x += disp[0]
            vertex.Point.y += disp[1]
            vertex.Point.z += disp[2]
    
    # Create new object with displaced shape
    displaced_obj = doc.addObject("Part::Feature", "DisplacedShape")
    displaced_obj.Shape = displaced
    displaced_obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)  # Red
    
    # Show original in wireframe
    original.ViewObject.DisplayMode = "Wireframe"
    
    doc.recompute()
    return displaced_obj
```

## 6. Advanced Simulations

### Multi-physics Simulation
```python
class MultiPhysicsSimulation:
    def __init__(self, thermal_sim, structural_sim):
        """Initialize coupled thermal-structural simulation."""
        self.thermal = thermal_sim
        self.structural = structural_sim
        self.thermal_expansion = 12e-6  # Thermal expansion coefficient (1/K)
    
    def step(self, dt):
        # Step thermal simulation
        thermal_result = self.thermal.step(dt)
        
        # Calculate thermal strains
        delta_T = thermal_result - 20  # Temperature change from reference (20°C)
        thermal_strain = self.thermal_expansion * delta_T
        
        # Apply thermal loads to structural model
        for i, node in enumerate(self.structural.nodes):
            self.structural.apply_thermal_strain(i, thermal_strain[i])
        
        # Step structural simulation
        structural_result = self.structural.step(dt)
        
        return {
            'temperatures': thermal_result,
            'displacements': structural_result
        }
```

## Next Steps
- [FEA Analysis](fea_analysis.md)
- [Material Properties](materials_database.md)
- [Manufacturing Integration](../manufacturing/3d_printing_export.md)

---
*Last updated: June 30, 2025*
