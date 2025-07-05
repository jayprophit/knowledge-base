---
title: "OpenSCAD Automation Guide"
description: "Comprehensive guide to automating 3D modeling with OpenSCAD using scripts and programming"
type: "design"
category: "3D Modeling"
related_resources:
  - name: "3D Model Generation"
    url: "/docs/design/3d_model_generation"
  - name: "3D Printing Export"
    url: "/docs/design/3d_printing_export"
  - name: "Generative Design"
    url: "/docs/design/generative_design"
tags:
  - openscad
  - 3d-modeling
  - cad
  - automation
  - scripting
  - parametric-design
---

# OpenSCAD Automation Guide

This guide provides comprehensive information on automating 3D modeling workflows using OpenSCAD, a script-based 3D CAD modeling tool. Learn how to create parametric designs, automate model generation, and integrate OpenSCAD with other tools.

## Table of Contents

1. [Introduction to OpenSCAD Automation](#introduction-to-openscad-automation)
2. [Getting Started with OpenSCAD Scripting](#getting-started-with-openscad-scripting)
3. [Advanced OpenSCAD Techniques](#advanced-openscad-techniques)
4. [Command-Line Automation](#command-line-automation)
5. [Integrating with Python](#integrating-with-python)
6. [Batch Processing and Parameter Studies](#batch-processing-and-parameter-studies)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Examples and Templates](#examples-and-templates)
10. [Resources](#resources)

## Introduction to OpenSCAD Automation

OpenSCAD is a powerful open-source 3D modeling tool that uses a scripting language to create precise 3D models. Unlike traditional CAD software, OpenSCAD is programmatic, making it ideal for:

- Parametric designs
- Customizable 3D models
- Batch generation of variants
- Automated testing of designs
- Integration with other tools and workflows

### Why Automate OpenSCAD?

1. **Reproducibility**: Scripts ensure consistent results
2. **Parameterization**: Easily adjust dimensions and features
3. **Version Control**: Track changes in your designs
4. **Automation**: Generate multiple variants automatically
5. **Integration**: Connect with other tools and workflows

## Getting Started with OpenSCAD Scripting

### Basic OpenSCAD Syntax

OpenSCAD uses a C-like syntax with functions for creating and modifying 3D objects:

```openscad
// Basic shapes
cube([10, 20, 30]);
sphere(r=10);
cylinder(h=20, r=5);

// Transformations
translate([10, 0, 0]) cube(10);
rotate([0, 0, 45]) cube(10);
scale([1, 1, 2]) sphere(5);

// Boolean operations
union() {
    cube(10, center=true);
    sphere(r=7);
}

difference() {
    cube(15, center=true);
    sphere(r=10);
}

intersection() {
    cube(12, center=true);
    sphere(r=8);
}
```

### Variables and Parameters

```openscad
// Define parameters
width = 20;
height = 30;
depth = 15;
wall_thickness = 2;

// Use variables in shapes
difference() {
    // Outer box
    cube([width, depth, height]);
    
    // Inner cutout
    translate([wall_thickness, wall_thickness, wall_thickness]) 
        cube([width - 2*wall_thickness, 
              depth - 2*wall_thickness, 
              height - wall_thickness]);
}
```

### Modules for Reusable Components

```openscad
// Define a module
module rounded_cube(size, radius=2) {
    // Implementation of a cube with rounded corners
    // (simplified example)
    hull() {
        for(x = [radius, size[0]-radius]) {
            for(y = [radius, size[1]-radius]) {
                for(z = [radius, size[2]-radius]) {
                    translate([x, y, z]) sphere(r=radius);
                }
            }
        }
    }
}

// Use the module
rounded_cube([30, 20, 10], radius=3);
```

## Advanced OpenSCAD Techniques

### List Comprehensions

```openscad
// Generate a grid of cylinders
points = [ for(x=[0:10:50], y=[0:10:50]) [x, y] ];
for(p = points) {
    translate(p) cylinder(h=5, r=2);
}
```

### Functions and Mathematical Operations

```openscad
// Define a function
function fibonacci(n) = 
    n <= 1 ? n : fibonacci(n-1) + fibonacci(n-2);

// Create a Fibonacci spiral
for(i = [0:10]) {
    r = fibonacci(i);
    rotate(i * 137.5)  // Golden angle
    translate([r, 0, 0])
    sphere(r=sqrt(r));
}
```

### 2D to 3D Operations

```openscad
// Create a 2D shape
module star(num_points=5, outer_radius=10, inner_radius=5) {
    points = [
        for(i = [0:2*num_points-1])
        let (
            radius = i % 2 == 0 ? outer_radius : inner_radius,
            angle = i * 180/num_points
        )
        [radius * cos(angle), radius * sin(angle)]
    ];
    polygon(points);
}

// Extrude to 3D
linear_extrude(height=5) star(num_points=7);
```

## Command-Line Automation

OpenSCAD can be controlled from the command line, enabling automation and batch processing:

### Basic Command-Line Usage

```bash
# Render and export an STL file
openscad -o output.stl input.scad

# Render a specific output format (STL, OFF, AMF, 3MF, DXF, SVG, PDF, PNG)
openscad -o output.png --render --autocenter --viewall --imgsize=800,600 input.scad

# Set variables from the command line
openscad -o output.stl -D 'width=20; height=30' input.scad
```

### Common Command-Line Options

- `-o, --output` - Output file
- `-D, --define` - Define variables
- `-p, --preview` - Preview mode (faster rendering)
- `-m, --implicit` - Implicitly call `render()`
- `--export-format` - Specify output format (e.g., 'stl', 'amf', '3mf')
- `--camera` - Set camera position (e.g., '0,0,0,55,0,25,0')
- `--colorscheme` - Set color scheme (e.g., 'Cornfield', 'Starnight')
- `--render` - Force full geometry rendering

## Integrating with Python

Python can be used to generate OpenSCAD code, automate rendering, and process the results:

### Basic Python Integration

```python
import subprocess
import os

def render_openscad(template_file, output_file, parameters=None):
    """Render an OpenSCAD file with the given parameters."""
    cmd = ['openscad', '-o', output_file]
    
    # Add parameter definitions
    if parameters:
        params = ';'.join(f'{k}={v}' for k, v in parameters.items())
        cmd.extend(['-D', params])
    
    # Add input file
    cmd.append(template_file)
    
    # Run OpenSCAD
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error rendering {template_file}:")
        print(result.stderr)
        return False
    
    print(f"Rendered {output_file}")
    return True

# Example usage
render_openscad(
    'box.scad',
    'output.stl',
    parameters={'width': 30, 'height': 20, 'depth': 10}
)
```

### Generating OpenSCAD Code with Python

```python
def generate_parametric_box(width, height, depth, wall_thickness, output_file):
    """Generate an OpenSCAD file for a parametric box."""
    scad_code = f"""
    // Parametric Box
    // Generated by Python
    
    // Parameters
    width = {width};
    height = {height};
    depth = {depth};
    wall_thickness = {wall_thickness};
    
    // Main box
    difference() {{
        // Outer shape
        cube([width, depth, height]);
        
        // Inner cutout
        translate([wall_thickness, wall_thickness, wall_thickness])
            cube([width - 2*wall_thickness, 
                  depth - 2*wall_thickness, 
                  height - wall_thickness]);
    }}
    """
    
    with open(output_file, 'w') as f:
        f.write(scad_code)
    
    print(f"Generated {output_file}")

# Generate a box
generate_parametric_box(
    width=50,
    height=30,
    depth=40,
    wall_thickness=2,
    output_file='parametric_box.scad'
)
```

## Batch Processing and Parameter Studies

### Batch Rendering Multiple Variants

```python
import itertools

def batch_render_parameters(template_file, output_dir, parameter_sets):
    """Render multiple variants of a model with different parameters."""
    os.makedirs(output_dir, exist_ok=True)
    
    for i, params in enumerate(parameter_sets, 1):
        output_file = os.path.join(output_dir, f'variant_{i:03d}.stl')
        render_openscad(template_file, output_file, params)

# Example: Generate boxes with different dimensions
box_sizes = [
    {'width': 30, 'height': 20, 'depth': 15},
    {'width': 40, 'height': 30, 'depth': 20},
    {'width': 50, 'height': 40, 'depth': 25},
]

batch_render_parameters('box.scad', 'output_variants', box_sizes)
```

### Parameter Sweeps

```python
def parameter_sweep(template_file, output_dir, base_params, sweep_params):
    """Perform a parameter sweep over multiple dimensions."""
    # Generate all combinations of parameters
    param_names = list(sweep_params.keys())
    param_values = list(sweep_params.values())
    
    for i, combo in enumerate(itertools.product(*param_values), 1):
        # Create parameter dictionary
        params = base_params.copy()
        params.update(dict(zip(param_names, combo)))
        
        # Create descriptive filename
        filename = '_'.join(f"{k}{v}" for k, v in zip(param_names, combo))
        output_file = os.path.join(output_dir, f"sweep_{i:03d}_{filename}.stl")
        
        # Render
        render_openscad(template_file, output_file, params)

# Example usage
parameter_sweep(
    template_file='parametric_box.scad',
    output_dir='parameter_study',
    base_params={'wall_thickness': 2},
    sweep_params={
        'width': [20, 30, 40],
        'height': [10, 15, 20],
        'depth': [15, 25, 35]
    }
)
```

## Best Practices

### Code Organization

1. **Use modules** to organize related functionality
2. **Name parameters descriptively** (e.g., `outer_diameter` instead of `od`)
3. **Add comments** to explain complex operations
4. **Group related parameters** together at the top of the file
5. **Use functions** for calculations that might be reused

### Performance Optimization

1. **Use `$fn` wisely** - Lower values for faster rendering
2. **Avoid excessive recursion** - Can cause stack overflows
3. **Use `hull()` and `minkowski()` sparingly** - They're computationally expensive
4. **Precompile common operations** into modules
5. **Use `children()`** for flexible module composition

### Version Control

1. **Include a header** with author, date, and description
2. **Use meaningful commit messages**
3. **Tag releases** for important versions
4. **Document dependencies** between files

## Troubleshooting

### Common Issues and Solutions

1. **Model takes too long to render**
   - Reduce `$fn` values
   - Simplify complex operations
   - Use `%` to hide helper geometry during development

2. **Model has holes or is not manifold**
   - Check for coincident faces
   - Use `hull()` or `minkowski()` to ensure watertight models
   - Try `render(convexity=10)` for complex models

3. **OpenSCAD crashes**
   - Check for infinite loops
   - Reduce model complexity
   - Update to the latest version
   - Check system resources

4. **Export issues**
   - Ensure output directory exists
   - Check file permissions
   - Try a different output format

## Examples and Templates

### Parametric Gear Generator

```openscad
// Parametric Gear Generator
// Inspired by http://www.thingiverse.com/thing:3575

// Parameters
number_of_teeth = 20;  // Number of teeth
circular_pitch = 200;  // Pitch diameter / number of teeth
pressure_angle = 20;   // Standard pressure angle
gear_thickness = 5;    // Thickness of the gear
hub_diameter = 15;     // Diameter of the center hole
hub_thickness = 8;     // Thickness of the hub

// Derived values
pitch_radius = number_of_teeth * circular_pitch / 360;
base_radius = pitch_radius * cos(pressure_angle);

// Generate the gear
difference() {
    // Main gear shape
    linear_extrude(height=gear_thickness)
        gear_shape();
    
    // Center hole
    translate([0, 0, -1])
        cylinder(h=hub_thickness+2, d=hub_diameter, $fn=32);
}

// Hub
translate([0, 0, gear_thickness])
    cylinder(h=hub_thickness-gear_thickness, d=hub_diameter+5, $fn=32);

// Gear profile module
module gear_shape() {
    // Simplified gear profile (actual implementation would be more complex)
    difference() {
        circle(r=pitch_radius + 2, $fn=100);
        
        for (i = [0:number_of_teeth-1]) {
            rotate([0, 0, i * 360/number_of_teeth])
                translate([pitch_radius, 0, 0])
                    square([circular_pitch/2, circular_pitch/10], center=true);
        }
    }
}
```

## Resources

### Official Documentation
- [OpenSCAD User Manual](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual)
- [OpenSCAD Cheat Sheet](https://www.openscad.org/cheatsheet/)
- [OpenSCAD Language Reference](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/The_OpenSCAD_Language)

### Tutorials and Learning Resources
- [OpenSCAD Tutorial for Beginners](https://www.openscad.org/tutorials.html)
- [Learn OpenSCAD in Y Minutes](https://learnxinyminutes.com/docs/openscad/)
- [OpenSCAD Workbench (FreeCAD)](https://wiki.freecadweb.org/OpenSCAD_Workbench)

### Libraries and Extensions
- [MCAD Library](https://github.com/openscad/MCAD) - Standard parts library
- [BOSL2](https://github.com/revarbat/BOSL2) - The Belfry OpenSCAD Library v2
- [NopSCADlib](https://github.com/nophead/NopSCADlib) - Library of parts for 3D printing

### Tools
- [OpenSCAD Workbench for FreeCAD](https://wiki.freecadweb.org/OpenSCAD_Workbench)
- [Customizer](https://www.thingiverse.com/apps/customizer/run?thing=44004) - Web-based OpenSCAD customizer
- [OpenJSCAD](https://openjscad.org/) - JavaScript port of OpenSCAD

## Next Steps

1. [Explore 3D Model Generation →](/docs/design/3d_model_generation)
2. [Learn about 3D Printing Export →](/docs/design/3d_printing_export)
3. [Discover Generative Design →](/docs/design/generative_design)
