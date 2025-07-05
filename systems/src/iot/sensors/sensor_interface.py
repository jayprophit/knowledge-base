from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import time
import uuid
import logging

logger = logging.getLogger(__name__)

class Sensor(ABC):
    """
    Abstract base class for all sensor types.
    """
    def __init__(self, sensor_id: Optional[str] = None, name: str = "", sensor_type: str = "generic"):
        """
        Initialize sensor with unique ID and metadata.
        
        Args:
            sensor_id: Optional unique identifier (auto-generated if not provided)
            name: Human-readable name
            sensor_type: Type of sensor
        """
        self.sensor_id = sensor_id or str(uuid.uuid4())
        self.name = name
        self.sensor_type = sensor_type
        self.properties = {}
        self.last_reading = None
        self.last_read_time = None
        self.read_count = 0
        
    @abstractmethod
    def read(self) -> Any:
        """
        Read current sensor value.
        
        Returns:
            The sensor reading in appropriate type for the sensor.
        """
        pass
        
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get sensor metadata.
        
        Returns:
            Dictionary containing sensor metadata.
        """
        return {
            "sensor_id": self.sensor_id,
            "name": self.name,
            "type": self.sensor_type,
            "properties": self.properties,
            "last_read_time": self.last_read_time,
            "read_count": self.read_count
        }
        
    def update_properties(self, properties: Dict[str, Any]) -> bool:
        """
        Update sensor properties.
        
        Args:
            properties: Dictionary of properties to update
            
        Returns:
            Success status
        """
        self.properties.update(properties)
        return True


class TemperatureSensor(Sensor):
    """
    Temperature sensor implementation.
    """
    def __init__(self, sensor_id: Optional[str] = None, name: str = "Temperature Sensor",
                units: str = "celsius", min_temp: float = -40.0, max_temp: float = 125.0):
        """
        Initialize temperature sensor.
        
        Args:
            sensor_id: Optional unique identifier
            name: Sensor name
            units: Temperature units (celsius, fahrenheit, kelvin)
            min_temp: Minimum readable temperature
            max_temp: Maximum readable temperature
        """
        super().__init__(sensor_id, name, "temperature")
        self.properties["units"] = units
        self.properties["min_temp"] = min_temp
        self.properties["max_temp"] = max_temp
        self._simulated_value = 22.0  # Default room temperature
        
    def read(self) -> float:
        """
        Read current temperature.
        
        Returns:
            Current temperature in configured units
        """
        # In a real implementation, this would access hardware
        # For this example, we'll simulate a reading
        self._simulate_reading()
        
        self.last_reading = self._simulated_value
        self.last_read_time = time.time()
        self.read_count += 1
        
        return self.last_reading
        
    def _simulate_reading(self):
        """Simulate a sensor reading with slight variations."""
        # Add small random variation to simulate real sensor
        import random
        variation = random.uniform(-0.5, 0.5)
        self._simulated_value += variation
        
        # Ensure within valid range
        min_temp = self.properties["min_temp"]
        max_temp = self.properties["max_temp"]
        self._simulated_value = max(min_temp, min(max_temp, self._simulated_value))


class HumiditySensor(Sensor):
    """
    Humidity sensor implementation.
    """
    def __init__(self, sensor_id: Optional[str] = None, name: str = "Humidity Sensor"):
        """Initialize humidity sensor."""
        super().__init__(sensor_id, name, "humidity")
        self._simulated_value = 45.0  # Default humidity percentage
        
    def read(self) -> float:
        """
        Read current humidity percentage.
        
        Returns:
            Current humidity (0-100%)
        """
        # In a real implementation, this would access hardware
        # For this example, we'll simulate a reading
        self._simulate_reading()
        
        self.last_reading = self._simulated_value
        self.last_read_time = time.time()
        self.read_count += 1
        
        return self.last_reading
        
    def _simulate_reading(self):
        """Simulate a sensor reading with slight variations."""
        import random
        variation = random.uniform(-2.0, 2.0)
        self._simulated_value += variation
        
        # Ensure within valid range
        self._simulated_value = max(0.0, min(100.0, self._simulated_value))


class MotionSensor(Sensor):
    """
    Motion sensor implementation (PIR).
    """
    def __init__(self, sensor_id: Optional[str] = None, name: str = "Motion Sensor"):
        """Initialize motion sensor."""
        super().__init__(sensor_id, name, "motion")
        self._simulated_value = False
        self._last_motion = 0
        
    def read(self) -> bool:
        """
        Read current motion status.
        
        Returns:
            True if motion detected, False otherwise
        """
        # In a real implementation, this would access hardware
        # For this example, we'll simulate a reading
        self._simulate_reading()
        
        self.last_reading = self._simulated_value
        self.last_read_time = time.time()
        self.read_count += 1
        
        return self.last_reading
        
    def _simulate_reading(self):
        """Simulate a motion detection."""
        import random
        
        # Simulate occasional motion detection
        if not self._simulated_value:
            # No motion currently, small chance of detecting motion
            if random.random() < 0.1:
                self._simulated_value = True
                self._last_motion = time.time()
        else:
            # Motion already detected, should timeout after a while
            if time.time() - self._last_motion > 5.0:
                self._simulated_value = False


class LightSensor(Sensor):
    """
    Light sensor implementation (ambient light).
    """
    def __init__(self, sensor_id: Optional[str] = None, name: str = "Light Sensor"):
        """Initialize light sensor."""
        super().__init__(sensor_id, name, "light")
        self.properties["units"] = "lux"
        self._simulated_value = 500.0  # Default room lighting
        
    def read(self) -> float:
        """
        Read current light level.
        
        Returns:
            Current light level in lux
        """
        # In a real implementation, this would access hardware
        # For this example, we'll simulate a reading
        self._simulate_reading()
        
        self.last_reading = self._simulated_value
        self.last_read_time = time.time()
        self.read_count += 1
        
        return self.last_reading
        
    def _simulate_reading(self):
        """Simulate a light reading with variations."""
        import random
        variation = random.uniform(-50.0, 50.0)
        self._simulated_value += variation
        
        # Ensure within valid range (0 - 100000 lux)
        self._simulated_value = max(0.0, min(100000.0, self._simulated_value))


class SensorArray:
    """
    Container for multiple sensors with combined reading.
    """
    def __init__(self, name: str = "Sensor Array"):
        """Initialize sensor array."""
        self.name = name
        self.sensors: Dict[str, Sensor] = {}
        
    def add_sensor(self, sensor: Sensor) -> bool:
        """
        Add sensor to array.
        
        Args:
            sensor: Sensor object to add
            
        Returns:
            Success status
        """
        self.sensors[sensor.sensor_id] = sensor
        return True
        
    def remove_sensor(self, sensor_id: str) -> bool:
        """
        Remove sensor from array.
        
        Args:
            sensor_id: ID of sensor to remove
            
        Returns:
            Success status
        """
        if sensor_id in self.sensors:
            del self.sensors[sensor_id]
            return True
        return False
        
    def read_all(self) -> Dict[str, Any]:
        """
        Read all sensors in the array.
        
        Returns:
            Dictionary mapping sensor IDs to readings
        """
        readings = {}
        
        for sensor_id, sensor in self.sensors.items():
            try:
                readings[sensor_id] = sensor.read()
            except Exception as e:
                logger.error(f"Error reading sensor {sensor_id}: {e}")
                readings[sensor_id] = None
                
        return readings
        
    def get_by_type(self, sensor_type: str) -> List[Sensor]:
        """
        Get all sensors of a specific type.
        
        Args:
            sensor_type: Type of sensors to retrieve
            
        Returns:
            List of matching sensors
        """
        return [s for s in self.sensors.values() if s.sensor_type == sensor_type]
