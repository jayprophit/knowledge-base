import paho.mqtt.client as mqtt
import json
import logging
import ssl
import time
from typing import Callable, Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class MQTTClient:
    """
    MQTT client implementation for IoT device communication.
    """
    def __init__(self, client_id: str, broker: str, port: int = 1883, use_ssl: bool = False):
        """
        Initialize MQTT client.
        
        Args:
            client_id: Unique client identifier
            broker: MQTT broker address
            port: MQTT broker port (default: 1883, SSL: 8883)
            use_ssl: Whether to use SSL/TLS
        """
        self.client_id = client_id
        self.broker = broker
        self.port = port
        self.use_ssl = use_ssl
        
        self.client = mqtt.Client(client_id)
        self.callbacks = {}
        self.connected = False
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Configure SSL if needed
        if use_ssl:
            self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    
    def connect(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Connect to the MQTT broker.
        
        Args:
            username: Optional username for authentication
            password: Optional password for authentication
            
        Returns:
            Success status
        """
        if username and password:
            self.client.username_pw_set(username, password)
            
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        
    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False) -> bool:
        """
        Publish message to a topic.
        
        Args:
            topic: MQTT topic
            payload: Message payload (will be converted to JSON)
            qos: Quality of Service (0, 1, or 2)
            retain: Whether message should be retained
            
        Returns:
            Success status
        """
        if not self.connected:
            logger.error("Cannot publish: not connected")
            return False
            
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload)
            
        result = self.client.publish(topic, payload, qos, retain)
        return result.rc == mqtt.MQTT_ERR_SUCCESS
        
    def subscribe(self, topic: str, callback: Callable[[str, Dict[str, Any]], None], qos: int = 0):
        """
        Subscribe to a topic.
        
        Args:
            topic: MQTT topic or pattern
            callback: Function to call when messages are received
            qos: Quality of Service (0, 1, or 2)
        """
        self.callbacks[topic] = callback
        self.client.subscribe(topic, qos)
        
    def _on_connect(self, client, userdata, flags, rc):
        """Internal callback for connection events."""
        if rc == 0:
            logger.info(f"Connected to MQTT broker {self.broker}")
            self.connected = True
            # Re-subscribe to topics
            for topic in self.callbacks:
                self.client.subscribe(topic)
        else:
            logger.error(f"Failed to connect to MQTT broker, error code: {rc}")
            
    def _on_message(self, client, userdata, msg):
        """Internal callback for message events."""
        try:
            payload = msg.payload.decode()
            try:
                # Try to parse as JSON
                payload = json.loads(payload)
            except:
                # Not JSON, use as is
                pass
                
            # Find matching callbacks
            for topic, callback in self.callbacks.items():
                if mqtt.topic_matches_sub(topic, msg.topic):
                    callback(msg.topic, payload)
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
            
    def _on_disconnect(self, client, userdata, rc):
        """Internal callback for disconnection events."""
        logger.warning(f"Disconnected from MQTT broker with code: {rc}")
        self.connected = False


class MQTTDeviceManager:
    """
    MQTT-based device management for IoT devices.
    Uses MQTT for device discovery, registration, and control.
    """
    def __init__(self, client_id: str, broker: str, port: int = 1883):
        """Initialize MQTT device manager."""
        self.mqtt_client = MQTTClient(client_id, broker, port)
        self.devices = {}
        self.device_status = {}
        
    def start(self, username: Optional[str] = None, password: Optional[str] = None):
        """Start the MQTT device manager."""
        # Connect to broker
        if not self.mqtt_client.connect(username, password):
            return False
            
        # Subscribe to device discovery and status topics
        self.mqtt_client.subscribe("devices/+/status", self._on_device_status)
        self.mqtt_client.subscribe("devices/discovery", self._on_device_discovery)
        self.mqtt_client.subscribe("devices/+/telemetry", self._on_device_telemetry)
        
        # Publish discovery request
        self.mqtt_client.publish("devices/discovery/request", {
            "requestId": f"discovery-{int(time.time())}",
            "manager": self.mqtt_client.client_id
        })
        
        return True
        
    def stop(self):
        """Stop the MQTT device manager."""
        self.mqtt_client.disconnect()
        
    def send_command(self, device_id: str, command: str, params: Dict[str, Any] = None):
        """Send command to a device."""
        payload = {
            "command": command,
            "timestamp": time.time()
        }
        
        if params:
            payload["params"] = params
            
        return self.mqtt_client.publish(f"devices/{device_id}/commands", payload, qos=1)
        
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get device status."""
        return self.device_status.get(device_id, {})
        
    def request_device_status(self, device_id: str):
        """Request status update from device."""
        return self.mqtt_client.publish(f"devices/{device_id}/status/request", {
            "requestId": f"status-{int(time.time())}",
            "manager": self.mqtt_client.client_id
        })
        
    def _on_device_status(self, topic, payload):
        """Handle device status messages."""
        try:
            device_id = topic.split('/')[1]
            self.device_status[device_id] = payload
            logger.info(f"Updated status for device {device_id}")
        except Exception as e:
            logger.error(f"Error processing device status: {e}")
            
    def _on_device_discovery(self, topic, payload):
        """Handle device discovery messages."""
        try:
            if "deviceId" in payload:
                device_id = payload["deviceId"]
                self.devices[device_id] = payload
                logger.info(f"Discovered device: {device_id}")
                
                # Request status for newly discovered device
                self.request_device_status(device_id)
        except Exception as e:
            logger.error(f"Error processing device discovery: {e}")
            
    def _on_device_telemetry(self, topic, payload):
        """Handle device telemetry messages."""
        try:
            device_id = topic.split('/')[1]
            if device_id not in self.devices:
                logger.warning(f"Received telemetry from unknown device: {device_id}")
                return
                
            # Process telemetry data
            logger.debug(f"Received telemetry from {device_id}: {payload}")
            # Additional telemetry processing would go here
        except Exception as e:
            logger.error(f"Error processing device telemetry: {e}")
