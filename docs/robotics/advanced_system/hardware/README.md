# Hardware Specifications

This document details the hardware components and specifications for the advanced robotic system.

## Core Components

### 1. Processing Units

| Component | Specification | Purpose |
|-----------|---------------|---------|
| Main Computer | NVIDIA Jetson AGX Orin | Primary AI/ML processing |
| Microcontroller | STM32H743 | Low-level motor control |
| FPGA | Xilinx Zynq UltraScale+ | Real-time sensor processing |

### 2. Sensors

#### Vision
- **Stereo Cameras**: Intel RealSense D455
  - Resolution: 1280×720 @ 30fps
  - Field of View: 86°×57°
  - Depth Range: 0.4m - 6m

- **3D LIDAR**: Ouster OS1-64
  - Channels: 64
  - Range: 120m
  - Field of View: 360°×45°
  - Accuracy: ±3cm

#### Environmental
- **IMU**: BMI088
  - Accelerometer: ±3g to ±24g
  - Gyroscope: ±125 to ±2000°/s
  - Update Rate: 1kHz

- **Gas Sensors**
  - MQ-2: Combustible gases
  - MQ-135: Air quality
  - SCD30: CO₂, temperature, humidity

### 3. Actuators

#### Locomotion
- **Drive Motors**: Maxon EC 45 Flat 100W
  - Nominal Voltage: 24V
  - Nominal Speed: 4,500 rpm
  - Torque: 38 mNm
  - Encoder: 500 CPR

#### Manipulation
- **Robotic Arm**: 6-DOF with parallel gripper
  - Payload: 1kg
  - Reach: 600mm
  - Repeatability: ±0.1mm

### 4. Power System

| Component | Specification |
|-----------|---------------|
| Main Battery | LiPo 6S 10,000mAh |
| Backup Battery | LiFePO4 3.2V 2,000mAh |
| Power Management | Custom BMS with fuel gauge |
| Solar Panel | 60W foldable with MPPT |
| Power Efficiency | >90% DC-DC conversion |

## Mechanical Specifications

### 1. Chassis
- **Material**: Carbon fiber and aluminum alloy
- **Dimensions**: 500mm × 400mm × 300mm (L×W×H)
- **Weight**: 12kg (without payload)
- **IP Rating**: IP54 (splash and dust resistant)

### 2. Mobility
- **Drive System**: 4-wheel Mecanum drive
- **Max Speed**: 2 m/s
- **Obstacle Clearance**: 50mm
- **Slope Climbing**: 15°

## Electrical Specifications

### 1. Power Requirements
- **Operating Voltage**: 12V - 36V DC
- **Peak Power**: 200W
- **Idle Power**: 15W
- **Charging**: 24V 3A fast charging

### 2. Communication Interfaces
- **Wireless**:
  - WiFi 6 (802.11ax)
  - Bluetooth 5.2
  - 5G/LTE (optional)
- **Wired**:
  - Gigabit Ethernet
  - USB 3.2 Gen 2 (10Gbps)
  - CAN 2.0B

## Environmental Specifications

| Parameter | Operating Range | Storage Range |
|-----------|----------------|----------------|
| Temperature | -10°C to 50°C | -20°C to 60°C |
| Humidity | 10% to 90% RH (non-condensing) | 5% to 95% RH |
| Altitude | 0 to 4,000m | 0 to 10,000m |

## Compliance and Certifications

- **Safety**: UL 60950-1, IEC 62061
- **EMC**: FCC Part 15, CE RED, EN 301 489
- **Wireless**: FCC ID, CE, IC, MIC
- **Environmental**: RoHS, REACH

## Maintenance Schedule

| Component | Maintenance Interval | Actions |
|-----------|----------------------|---------|
| Batteries | 6 months | Capacity test, balance charge |
| Motors | 12 months | Bearing check, encoder calibration |
| Sensors | 6 months | Calibration, cleaning |
| Chassis | 3 months | Bolt tightening, inspection |
| Software | Monthly | Security updates, bug fixes |

## Troubleshooting

### Common Issues
1. **Battery Not Charging**
   - Check power adapter connection
   - Verify battery temperature
   - Test with known-good battery

2. **WiFi Connectivity Issues**
   - Check antenna connections
   - Verify network credentials
   - Test with different frequency bands

3. **Motor Overheating**
   - Reduce payload
   - Check for mechanical binding
   - Verify motor driver configuration

## Ordering Information

| Part Number | Description | Lead Time |
|-------------|-------------|------------|
| RB-AS-001 | Main Processing Unit | 2 weeks |
| RB-AS-002 | Sensor Package | 1 week |
| RB-AS-003 | Power System | 1 week |
| RB-AS-004 | Chassis Kit | 3 weeks |

## Support

For technical support, please contact:
- Email: support@robotics-ai.com
- Phone: +1 (555) 123-4567
- Online: https://support.robotics-ai.com

---
*Last updated: 2025-07-01*
*Version: 1.0.0*
