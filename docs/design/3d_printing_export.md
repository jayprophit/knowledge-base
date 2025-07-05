---
title: "3D Printing Export Guide"
description: "Comprehensive guide to exporting 3D models for 3D printing, including file formats, optimization, and troubleshooting"
type: "design"
category: "3D Printing"
related_resources:
  - name: "3D Model Generation"
    url: "/docs/design/3d_model_generation"
  - name: "Multi-material Design"
    url: "/docs/design/multi_material_design"
tags:
  - 3d-printing
  - cad
  - manufacturing
  - stl
  - fdm
  - sla
  - slicer
---

# 3D Printing Export Guide

This guide provides comprehensive information on preparing and exporting 3D models for 3D printing, covering various file formats, optimization techniques, and common issues.

## Table of Contents

1. [Introduction to 3D Printing Export](#introduction-to-3d-printing-export)
2. [Supported File Formats](#supported-file-formats)
3. [Export Settings by Software](#export-settings-by-software)
4. [Model Preparation](#model-preparation)
5. [Optimization Techniques](#optimization-techniques)
6. [Slicer Software](#slicer-software)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Topics](#advanced-topics)

## Introduction to 3D Printing Export

Exporting a 3D model for printing involves converting your digital design into a format that 3D printers can understand. This process requires careful attention to model integrity, scale, and printability.

### Key Considerations

- **Model Integrity**: Ensure your model is watertight and manifold
- **Scale**: Verify dimensions match your intended physical size
- **Wall Thickness**: Maintain minimum wall thickness for your printer
- **Orientation**: Optimize print orientation for strength and surface quality
- **Supports**: Plan for support structures where needed

## Supported File Formats

### 1. STL (Stereolithography)
- **Extensions**: `.stl`
- **Best for**: FDM, SLA, SLS printing
- **Pros**:
  - Industry standard
  - Widely supported
  - Simple structure
- **Cons**:
  - No color or material information
  - No units (assumes mm)

### 2. 3MF (3D Manufacturing Format)
- **Extensions**: `.3mf`
- **Best for**: Modern 3D printing workflows
- **Pros**:
  - Supports colors, materials, and metadata
  - Single file with all resources
  - Open standard
- **Cons**:
  - Newer format with varying support

### 3. OBJ (Wavefront)
- **Extensions**: `.obj`
- **Best for**: Multi-color or multi-material prints
- **Pros**:
  - Supports colors and textures
  - Widely supported
- **Cons**:
  - Multiple files (.obj + .mtl + textures)
  - Larger file size

### 4. AMF (Additive Manufacturing File Format)
- **Extensions**: `.amf`
- **Best for**: Advanced manufacturing
- **Pros**:
  - Supports colors, materials, and lattices
  - XML-based
- **Cons**:
  - Limited software support

## Export Settings by Software

### Blender
1. Select your object
2. File > Export > STL (.stl)
3. **Key Settings**:
   - Scale: 1.0 (or adjust as needed)
   - Apply Modifiers: Checked
   - Selection Only: If needed
   - Forward/Up: Y Forward, Z Up (common for 3D printing)

### Fusion 360
1. Right-click component > Save As Mesh
2. Select format (STL, 3MF, etc.)
3. **Key Settings**:
   - Refinement: High
   - Send to Print Utility: If direct printing
   - Units: Match your design units

### TinkerCAD
1. Click "Export"
2. Select format (STL, OBJ, etc.)
3. **Note**: Limited control over export settings

## Model Preparation

### 1. Check for Errors
- **Non-manifold edges**: Fix gaps or holes
- **Inverted normals**: Ensure all faces are oriented correctly
- **Self-intersections**: Resolve intersecting geometry

### 2. Scale and Units
- Verify dimensions match intended size
- Convert units if necessary (mm is standard)
- Check minimum feature size for your printer

### 3. Wall Thickness
- Minimum wall thickness: 0.8mm for FDM, 0.5mm for SLA
- Check thin walls that might not print properly

### 4. Watertight Mesh
- Ensure the model is a single, closed volume
- Remove any internal geometry not meant to be printed

## Optimization Techniques

### 1. Reducing Polygon Count
- Use decimation tools to reduce polycount while maintaining shape
- Target resolution: 0.1mm tolerance for most prints

### 2. Hollowing Models
- For SLA/SLS to save material
- Add drainage holes for uncured resin

### 3. Splitting Large Models
- For printers with small build volumes
- Add alignment features (dowels, pins)

### 4. Adding Tolerances
- For moving parts: 0.2-0.5mm clearance
- For press fits: -0.1 to -0.3mm interference

## Slicer Software

### Popular Options
1. **Ultimaker Cura**
   - Best for: FDM printing
   - Key features: Extensive material profiles, custom supports

2. **PrusaSlicer**
   - Best for: Prusa printers, but works with others
   - Key features: Variable layer height, paint-on supports

3. **Chitubox**
   - Best for: Resin (SLA/DLP/LCD) printing
   - Key features: Advanced support generation

4. **Simplify3D**
   - Best for: Advanced users
   - Key features: Customizable processes, dual extrusion

### Slicer Settings
- **Layer Height**: 0.1-0.3mm (lower = higher quality)
- **Infill**: 10-20% for most prints
- **Wall Thickness**: 0.8-1.2mm (2-3 perimeters)
- **Support**: Generate where needed (45° rule)
- **Brim/Raft**: For better bed adhesion

## Troubleshooting

### Common Issues and Solutions

1. **Won't Slice**
   - Check for non-manifold geometry
   - Run mesh repair tools
   - Try exporting with different settings

2. **Poor Print Quality**
   - Reduce layer height
   - Check extrusion multiplier
   - Calibrate printer

3. **Warping**
   - Use a heated bed
   - Apply adhesive (glue stick, hairspray)
   - Add a brim or raft

4. **Stringing**
   - Enable retraction
   - Adjust temperature
   - Check for moist filament

## Advanced Topics

### 1. Multi-material Printing
- Design considerations for multi-extruder setups
- Using PVA or HIPS for supports

### 2. Textures and Surface Finish
- Adding surface details
- Post-processing techniques

### 3. Custom Supports
- Designing breakaway supports
- Tree supports for complex geometries

### 4. Parametric Designs
- Creating customizable models
- Using OpenSCAD or Fusion 360 parameters

## Resources

### Learning
- [Prusa Knowledge Base](https://help.prusa3d.com/)
- [Simplify3D Print Quality Guide](https://www.simplify3d.com/support/print-quality-troubleshooting/)
- [MatterHackers 3D Printing Guide](https://www.matterhackers.com/3d-printing/guides)

### Tools
- [Netfabb Online Repair](https://www.autodesk.com/solutions/netfabb/overview)
- [3D Builder (Windows)](https://www.microsoft.com/en-us/p/3d-builder/9wzdncrfj3t6)
- [Meshmixer](http://www.meshmixer.com/)

### Communities
- [r/3Dprinting](https://www.reddit.com/r/3Dprinting/)
- [3D Printing Stack Exchange](https://3dprinting.stackexchange.com/)
- [Prusa Forums](https://forum.prusaprinters.org/)

## Next Steps

1. [Learn about 3D model generation →](/docs/design/3d_model_generation)
2. [Explore multi-material design →](/docs/design/multi_material_design)
3. [Understand CNC machining export →](/docs/design/cnc_machining_export)
