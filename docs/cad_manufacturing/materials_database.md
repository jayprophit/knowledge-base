---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Materials Database for cad_manufacturing/materials_database.md
title: Materials Database
updated_at: '2025-07-04'
version: 1.0.0
---

# Material Properties & Database

This document outlines the material database system used for CAD modeling, physics simulation, and manufacturing. The database stores material properties essential for accurate simulations and manufacturing processes.

## Table of Contents
- [1. Material Properties](#1-material-properties)
- [2. Material Database Structure](#2-material-database-structure)
- [3. Python Implementation](#3-python-implementation)
- [4. Material Selection](#4-material-selection)
- [5. Custom Materials](#5-custom-materials)
- [6. Integration with CAD](#6-integration-with-cad)
- [7. Example Materials](#7-example-materials)

## 1. Material Properties

### Mechanical Properties
- **Density (ρ)**: Mass per unit volume (kg/m³)
- **Young's Modulus (E)**: Stiffness/elasticity (Pa)
- **Poisson's Ratio (ν)**: Transverse strain response
- **Yield Strength (σ_y)**: Stress at which deformation becomes plastic (Pa)
- **Ultimate Tensile Strength (σ_u)**: Maximum stress before failure (Pa)
- **Shear Modulus (G)**: Resistance to shear deformation (Pa)
- **Hardness**: Resistance to deformation (various scales)

### Thermal Properties
- **Thermal Conductivity (k)**: Heat transfer rate (W/m·K)
- **Specific Heat (c)**: Heat capacity (J/kg·K)
- **Thermal Expansion (α)**: Dimensional change with temperature (1/K)
- **Melting Point**: Temperature at which material melts (°C)

### Electrical Properties
- **Electrical Conductivity (σ)**: Ability to conduct electricity (S/m)
- **Resistivity (ρ)**: Opposition to current flow (Ω·m)
- **Dielectric Constant (ε)**: Electric permittivity relative to vacuum

## 2. Material Database Structure

The material database is implemented as a Python module with the following structure:

```python
material_database = {
    'steel_aisi_1018': {
        'name': 'AISI 1018 Steel',
        'category': 'metal',
        'mechanical': {
            'density': 7870,  # kg/m?
            'youngs_modulus': 205e9,  # Pa
            'poisson_ratio': 0.29,
            'yield_strength': 370e6,  # Pa
            'tensile_strength': 440e6,  # Pa
            'shear_modulus': 80e9,  # Pa
            'hardness_brinell': 126
        },
        'thermal': {
            'conductivity': 51.9,  # W/m?K
            'specific_heat': 486,  # J/kg?K
            'expansion': 12e-6,  # 1/K
            'melting_point': 1520  # ?C
        },
        'electrical': {
            'resistivity': 1.43e-7,  # ??m
            'conductivity': 6.99e6  # S/m
        },
        'manufacturing': {
            'machinability': 0.65,  # Relative to AISI 1212 steel
            'weldability': 'Good',
            'formability': 'Good'
        },
        'cost': 0.8,  # Relative cost factor
        'source': 'ASM Handbook Vol. 1',
        'notes': 'Low carbon steel, good for general purpose applications'
    },
    # More materials...
}
```

## 3. Python Implementation

### Material Class
```python
class Material:
    def __init__(self, material_id, database=None):
        """Initialize material from database."""
        self.database = database or material_database
        if material_id not in self.database:
            raise ValueError(f"Material '{material_id}' not found in database")
        
        self.id = material_id
        self.properties = self.database[material_id]
    
    def __getattr__(self, name):
        """Access properties using dot notation."""
        # Check top-level properties
        if name in self.properties:
            return self.properties[name]
        
        # Check nested properties (e.g., mechanical.density)
        parts = name.split('_', 1)
        if len(parts) > 1 and parts[0] in self.properties:
            return self.properties[parts[0]].get(parts[1])
            
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def get_property(self, path, default=None):
        """Get nested property using dot notation."""
        parts = path.split('.')
        value = self.properties
        
        try:
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def calculate_mass(self, volume):
        """Calculate mass from volume."""
        return self.mechanical_density * volume if hasattr(self, 'mechanical_density') else None
    
    def calculate_stress(self, force, area):
        """Calculate stress from force and area."""
        return force / area if area > 0 else 0
    
    def calculate_strain(self, stress):
        """Calculate strain from stress using Hooke's Law."""
        if hasattr(self, 'mechanical_youngs_modulus') and self.mechanical_youngs_modulus > 0:
            return stress / self.mechanical_youngs_modulus
        return None

# Example usage
steel = Material('steel_aisi_1018')
print(f"Density: {steel.mechanical_density} kg/m?")
print(f"Young's Modulus: {steel.mechanical_youngs_modulus/1e9:.1f} GPa")
```

## 4. Material Selection

### Filtering Materials
```python
def filter_materials(database, **criteria):
    """Filter materials based on criteria."""
    results = []
    
    for mat_id, props in database.items():
        match = True
        
        for key, value in criteria.items():
            # Handle nested properties (e.g., 'mechanical.density')
            if '.' in key:
                parts = key.split('.')
                prop = props
                try:
                    for part in parts:
                        prop = prop[part]
                    if prop < value[0] or prop > value[1]:
                        match = False
                        break
                except (KeyError, TypeError):
                    match = False
                    break
            # Handle top-level properties
            elif key not in props or props[key] < value[0] or props[key] > value[1]:
                match = False
                break
                
        if match:
            results.append((mat_id, props['name']))
            
    return results

# Example: Find materials with density between 2000-3000 kg/m? and yield strength > 200 MPa
results = filter_materials(
    material_database,
    **{
        'mechanical.density': (2000, 3000),
        'mechanical.yield_strength': (200e6, float('inf'))
    }
)
```

### Material Selection by Application
```python
def recommend_material(application, constraints):
    """Recommend materials based on application requirements."""
    # Define application profiles with weightings
    profiles = {
        'structural': {
            'mechanical.yield_strength': 0.4,
            'mechanical.density': 0.3,
            'cost': 0.2,
            'manufacturing.machinability': 0.1
        },
        'thermal': {
            'thermal.conductivity': 0.5,
            'thermal.expansion': 0.3,
            'cost': 0.2
        },
        'lightweight': {
            'mechanical.density': 0.6,
            'mechanical.yield_strength': 0.3,
            'cost': 0.1
        }
    }
    
    if application not in profiles:
        raise ValueError(f"Unknown application profile: {application}")
    
    profile = profiles[application]
    scores = []
    
    for mat_id, props in material_database.items():
        score = 0
        valid = True
        
        # Apply constraints (hard requirements)
        for key, (min_val, max_val) in constraints.items():
            try:
                value = props
                for part in key.split('.'):
                    value = value[part]
                if not (min_val <= value <= max_val):
                    valid = False
                    break
            except (KeyError, TypeError):
                valid = False
                break
                
        if not valid:
            continue
            
        # Calculate score based on profile
        for key, weight in profile.items():
            try:
                value = props
                for part in key.split('.'):
                    value = value[part]
                # Normalize value (assuming higher is better for all properties)
                # In a real implementation, you'd want to handle different properties differently
                score += value * weight
            except (KeyError, TypeError):
                pass
                
        if score > 0:
            scores.append((mat_id, props['name'], score))
    
    # Sort by score in descending order
    return sorted(scores, key=lambda x: x[2], reverse=True)

# Example: Find best structural material with yield strength > 200 MPa
recommendations = recommend_material(
    'structural',
    {'mechanical.yield_strength': (200e6, float('inf'))}
)
```

## 5. Custom Materials

### Adding Custom Materials
```python
def add_custom_material(database, material_id, properties):
    """Add a custom material to the database."""
    if material_id in database:
        raise ValueError(f"Material ID '{material_id}' already exists")
    
    # Validate required properties
    required = ['name', 'category', 'mechanical']
    for prop in required:
        if prop not in properties:
            raise ValueError(f"Missing required property: {prop}")
    
    database[material_id] = properties
    return database

# Example: Add a custom aluminum alloy
custom_aluminum = {
    'name': 'Custom 7075 Aluminum',
    'category': 'metal',
    'mechanical': {
        'density': 2810,
        'youngs_modulus': 71.7e9,
        'poisson_ratio': 0.33,
        'yield_strength': 503e6,
        'tensile_strength': 572e6,
        'shear_modulus': 26.9e9,
        'hardness_brinell': 150
    },
    'thermal': {
        'conductivity': 130,
        'specific_heat': 960,
        'expansion': 23.6e-6,
        'melting_point': 635
    },
    'notes': 'High-strength aluminum alloy'
}

material_database = add_custom_material(
    material_database,
    'aluminum_custom_7075',
    custom_aluminum
)
```

## 6. Integration with CAD

### FreeCAD Integration
```python
import FreeCAD

class FreeCADMaterial:
    def __init__(self, material):
        """Initialize with a Material object."""
        self.material = material
    
    def apply_to_object(self, obj):
        """Apply material properties to a FreeCAD object."""
        if not hasattr(obj, 'Material'):
            print("Warning: Object does not support materials")
            return
            
        obj.Material = {
            'Name': self.material.name,
            'Density': f"{self.material.mechanical_density} kg/m^3",
            'YoungsModulus': f"{self.material.mechanical_youngs_modulus} Pa",
            'PoissonRatio': str(self.material.mechanical_poisson_ratio),
            'YieldStrength': f"{self.material.mechanical_yield_strength} Pa"
        }
        
        # Set visual properties if available
        if hasattr(obj, 'ViewObject') and hasattr(obj.ViewObject, 'ShapeColor'):
            # Set color based on material category
            colors = {
                'metal': (0.8, 0.8, 0.8),      # Light gray for metals
                'plastic': (0.9, 0.9, 0.5),    # Light yellow for plastics
                'ceramic': (0.7, 0.7, 0.9),    # Light blue for ceramics
                'composite': (0.8, 0.5, 0.5)   # Light red for composites
            }
            
            color = colors.get(
                self.material.category.lower(), 
                (0.8, 0.8, 0.8)  # Default to gray
            )
            obj.ViewObject.ShapeColor = color

# Example usage
steel = Material('steel_aisi_1018')
fc_material = FreeCADMaterial(steel)

# Assuming 'box' is a FreeCAD object
# fc_material.apply_to_object(box)
```

## 7. Example Materials

### Common Engineering Materials

#### Metals
- **Steel (AISI 1018)**: General purpose low carbon steel
- **Aluminum 6061**: Lightweight, corrosion-resistant alloy
- **Titanium Grade 5**: High strength-to-weight ratio
- **Brass C360**: Excellent machinability, good corrosion resistance

#### Plastics
- **ABS**: Tough, impact-resistant thermoplastic
- **Nylon (PA6)**: Good wear resistance, self-lubricating
- **Polycarbonate**: High impact strength, transparent
- **PTFE (Teflon)**: Excellent chemical resistance, low friction

#### Composites
- **Carbon Fiber/Epoxy**: High strength-to-weight ratio
- **Fiberglass**: Good strength, corrosion resistant
- **Kevlar/Epoxy**: High impact resistance

#### Ceramics
- **Alumina (Al₂O₃)**: High hardness, electrical insulator
- **Silicon Carbide (SiC)**: Excellent wear resistance
- **Zirconia (ZrO₂)**: High fracture toughness

## Next Steps
- [Physics Simulation](physics_simulation.md)
- [FEA Analysis](temp_reorg/docs/cad_manufacturing/fea_analysis.md)
- [Manufacturing Export](temp_reorg/docs/manufacturing/3d_printing_export.md)

---
*Last updated: June 30, 2025*
