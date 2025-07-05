import logging
import time
import uuid
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class IoTDevice:
    """Base class for IoT devices in the system."""
    
    def __init__(self, device_id: Optional[str] = None, name: str = "", device_type: str = "generic"):
        self.device_id = device_id or str(uuid.uuid4())
        self.name = name
        self.device_type = device_type
        self.connected = False
        self.last_seen = None
        self.properties = {}
        self.sensors = {}
        self.actuators = {}
        
    def connect(self) -> bool:
        """Connect to the device."""
        # Implementation for connection logic
        self.connected = True
        self.last_seen = time.time()
        logger.info(f"Device {self.device_id} connected")
        return self.connected
        
    def disconnect(self) -> bool:
        """Disconnect from the device."""
        if not self.connected:
            return True
            
        # Implementation for disconnection logic
        self.connected = False
        logger.info(f"Device {self.device_id} disconnected")
        return not self.connected
        
    def update_status(self) -> Dict[str, Any]:
        """Update and return device status."""
        if self.connected:
            self.last_seen = time.time()
            
        return {
            'device_id': self.device_id,
            'name': self.name,
            'type': self.device_type,
            'connected': self.connected,
            'last_seen': self.last_seen,
            'properties': self.properties
        }
        
    def get_sensor_data(self, sensor_id: str = None) -> Dict[str, Any]:
        """Get data from device sensors."""
        if not self.connected:
            logger.warning(f"Cannot get sensor data: device {self.device_id} not connected")
            return {}
            
        if sensor_id and sensor_id in self.sensors:
            return {sensor_id: self.sensors[sensor_id].read()}
        else:
            return {sid: sensor.read() for sid, sensor in self.sensors.items()}
            
    def set_actuator(self, actuator_id: str, value: Any) -> bool:
        """Set actuator to specified value."""
        if not self.connected:
            logger.warning(f"Cannot set actuator: device {self.device_id} not connected")
            return False
            
        if actuator_id in self.actuators:
            self.actuators[actuator_id].write(value)
            return True
        else:
            logger.warning(f"Actuator {actuator_id} not found on device {self.device_id}")
            return False


class DeviceManager:
    """Manager for IoT devices in the system."""
    
    def __init__(self):
        self.devices: Dict[str, IoTDevice] = {}
        self.device_types: Dict[str, type] = {}
        self.discovery_active = False
        
    def register_device_type(self, device_type: str, device_class: type):
        """Register a new device type."""
        if device_type in self.device_types:
            logger.warning(f"Device type {device_type} already registered, overwriting")
            
        self.device_types[device_type] = device_class
        logger.info(f"Registered device type: {device_type}")
        
    def register_device(self, device: IoTDevice) -> bool:
        """Register a device with the manager."""
        if device.device_id in self.devices:
            logger.warning(f"Device with ID {device.device_id} already registered")
            return False
            
        self.devices[device.device_id] = device
        logger.info(f"Registered device: {device.device_id} ({device.name})")
        return True
        
    def unregister_device(self, device_id: str) -> bool:
        """Unregister a device from the manager."""
        if device_id not in self.devices:
            logger.warning(f"Device with ID {device_id} not found")
            return False
            
        # Disconnect device if connected
        if self.devices[device_id].connected:
            self.devices[device_id].disconnect()
            
        # Remove device
        del self.devices[device_id]
        logger.info(f"Unregistered device: {device_id}")
        return True
        
    def get_device(self, device_id: str) -> Optional[IoTDevice]:
        """Get device by ID."""
        return self.devices.get(device_id)
        
    def get_devices(self, device_type: Optional[str] = None) -> List[IoTDevice]:
        """Get all devices, optionally filtered by type."""
        if device_type:
            return [d for d in self.devices.values() if d.device_type == device_type]
        else:
            return list(self.devices.values())
            
    def connect_device(self, device_id: str) -> bool:
        """Connect to a specific device."""
        device = self.get_device(device_id)
        if not device:
            logger.warning(f"Device with ID {device_id} not found")
            return False
            
        return device.connect()
        
    def disconnect_device(self, device_id: str) -> bool:
        """Disconnect from a specific device."""
        device = self.get_device(device_id)
        if not device:
            logger.warning(f"Device with ID {device_id} not found")
            return False
            
        return device.disconnect()
        
    def start_discovery(self) -> bool:
        """Start device discovery process."""
        if self.discovery_active:
            logger.warning("Device discovery already active")
            return False
            
        self.discovery_active = True
        logger.info("Started device discovery")
        # Implementation for device discovery
        # This would typically involve network scanning, broadcast listeners, etc.
        return True
        
    def stop_discovery(self) -> bool:
        """Stop device discovery process."""
        if not self.discovery_active:
            return True
            
        self.discovery_active = False
        logger.info("Stopped device discovery")
        return True
        
    def get_all_sensor_data(self) -> Dict[str, Dict[str, Any]]:
        """Get sensor data from all connected devices."""
        data = {}
        for device_id, device in self.devices.items():
            if device.connected:
                sensor_data = device.get_sensor_data()
                if sensor_data:
                    data[device_id] = sensor_data
                    
        return data
        
    def update_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Update and return status of all devices."""
        return {device_id: device.update_status() 
                for device_id, device in self.devices.items()}
                
    def create_device(self, device_type: str, name: str = "", 
                     properties: Optional[Dict[str, Any]] = None) -> Optional[IoTDevice]:
        """Create a new device of specified type."""
        if device_type not in self.device_types:
            logger.warning(f"Unknown device type: {device_type}")
            return None
            
        # Create device instance
        device_class = self.device_types[device_type]
        device = device_class(name=name, device_type=device_type)
        
        # Set properties if provided
        if properties:
            device.properties.update(properties)
            
        # Register device
        self.register_device(device)
        return device
