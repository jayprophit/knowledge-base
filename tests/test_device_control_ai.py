"""
Test suite for Device Control AI Component
"""
import unittest
import time
import json
import paho.mqtt.client as mqtt
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from device_control import (
    DeviceType, 
    DeviceState, 
    MQTTClient, 
    AIDeviceController,
    RuleEngine
)

class TestDeviceState(unittest.TestCase):
    """Test cases for DeviceState class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.device = DeviceState(
            device_id="qpu1",
            device_type=DeviceType.QUANTUM_PROCESSOR,
            status="online",
            parameters={"temperature": 0.05, "fidelity": 0.99}
        )
    
    def test_initial_state(self):
        """Test initial device state."""
        self.assertEqual(self.device.device_id, "qpu1")
        self.assertEqual(self.device.device_type, DeviceType.QUANTUM_PROCESSOR)
        self.assertEqual(self.device.status, "online")
        self.assertEqual(self.device.parameters["temperature"], 0.05)
        self.assertGreater(self.device.last_updated, 0)
    
    def test_update_state(self):
        """Test updating device state."""
        update_time = self.device.last_updated
        time.sleep(0.01)  # Ensure timestamp changes
        
        self.device.update({
            "status": "calibrating",
            "parameters": {"temperature": 0.06}
        })
        
        self.assertEqual(self.device.status, "calibrating")
        self.assertEqual(self.device.parameters["temperature"], 0.06)
        self.assertEqual(self.device.parameters["fidelity"], 0.99)  # Should be preserved
        self.assertGreater(self.device.last_updated, update_time)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        device_dict = self.device.to_dict()
        self.assertEqual(device_dict["device_id"], "qpu1")
        self.assertEqual(device_dict["device_type"], "quantum_processor")
        self.assertEqual(device_dict["status"], "online")
        self.assertIn("last_updated", device_dict)


class TestMQTTClient(unittest.TestCase):
    """Test cases for MQTTClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = MQTTClient("test-client", "localhost")
        self.client.client = Mock()  # Mock the MQTT client
    
    def test_connect(self):
        """Test connecting to MQTT broker."""
        self.client.connect()
        self.client.client.connect.assert_called_once_with("localhost", 1883, 60)
        self.client.client.loop_start.assert_called_once()
    
    def test_publish(self):
        """Test publishing messages."""
        self.client.connected = True
        test_payload = {"key": "value"}
        
        # Mock successful publish
        mock_message = Mock()
        mock_message.rc = mqtt.MQTT_ERR_SUCCESS
        self.client.client.publish.return_value = mock_message
        
        result = self.client.publish("test/topic", test_payload)
        
        self.assertTrue(result)
        self.client.client.publish.assert_called_once_with(
            "test/topic",
            json.dumps(test_payload),
            qos=1,
            retain=True
        )
    
    def test_subscribe(self):
        """Test subscribing to topics."""
        self.client.connected = True
        callback = Mock()
        
        result = self.client.subscribe("test/topic", callback)
        
        self.assertTrue(result)
        self.client.client.subscribe.assert_called_once_with("test/topic", qos=1)
        self.assertIn("test/topic", self.client.subscriptions)
        self.assertEqual(self.client.subscriptions["test/topic"], callback)


class TestAIDeviceController(unittest.TestCase):
    """Test cases for AIDeviceController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('device_control.MQTTClient') as mock_mqtt:
            self.controller = AIDeviceController("test-controller")
            self.mock_mqtt = mock_mqtt.return_value
    
    def test_add_device(self):
        """Test adding a new device."""
        device_id = "qpu1"
        device_type = DeviceType.QUANTUM_PROCESSOR
        
        self.controller.add_device(device_id, device_type)
        
        self.assertIn(device_id, self.controller.devices)
        self.assertEqual(self.controller.devices[device_id].device_type, device_type)
    
    def test_send_command(self):
        """Test sending commands to devices."""
        device_id = "qpu1"
        command = {"action": "calibrate", "params": {"duration": 60}}
        
        # Add a device first
        self.controller.add_device(device_id, DeviceType.QUANTUM_PROCESSOR)
        
        # Test successful command
        self.mock_mqtt.publish.return_value = True
        result = self.controller.send_command(device_id, command)
        
        self.assertTrue(result)
        self.mock_mqtt.publish.assert_called_once()
        
        # Test command to non-existent device
        result = self.controller.send_command("nonexistent", command)
        self.assertFalse(result)
    
    def test_handle_device_update(self):
        """Test handling device status updates."""
        device_id = "qpu1"
        self.controller.add_device(device_id, DeviceType.QUANTUM_PROCESSOR)
        
        # Create a test update
        update = {
            "status": "calibrating",
            "parameters": {"temperature": 0.05}
        }
        
        # Simulate MQTT message
        self.controller._handle_device_update(
            f"devices/{device_id}/status",
            update
        )
        
        # Verify device was updated
        self.assertEqual(self.controller.devices[device_id].status, "calibrating")
        self.assertEqual(self.controller.devices[device_id].parameters["temperature"], 0.05)


class TestRuleEngine(unittest.TestCase):
    """Test cases for RuleEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rule_engine = RuleEngine()
        self.mock_controller = Mock()
        
        # Sample device state
        self.device_state = DeviceState(
            device_id="qpu1",
            device_type=DeviceType.QUANTUM_PROCESSOR,
            status="online",
            parameters={"temperature": 0.05}
        )
    
    def test_add_rule(self):
        """Test adding a new rule."""
        rule = {
            "name": "high_temp_alert",
            "condition": "device.parameters.get('temperature', 0) > 0.1",
            "action": "controller.send_command(device.device_id, {'action': 'cool_down'})"
        }
        
        self.rule_engine.add_rule(rule)
        self.assertEqual(len(self.rule_engine.rules), 1)
        self.assertEqual(self.rule_engine.rules[0]["name"], "high_temp_alert")
    
    def test_evaluate_rules(self):
        """Test evaluating rules against device state."""
        # Add a rule that triggers when temperature > 0.1
        self.rule_engine.add_rule({
            "name": "high_temp_alert",
            "condition": "device.parameters.get('temperature', 0) > 0.1",
            "action": "controller.send_command(device.device_id, {'action': 'cool_down'})"
        })
        
        # Test with temperature below threshold
        self.device_state.parameters["temperature"] = 0.05
        self.rule_engine.evaluate_rules(self.mock_controller, self.device_state)
        self.mock_controller.send_command.assert_not_called()
        
        # Test with temperature above threshold
        self.device_state.parameters["temperature"] = 0.15
        self.rule_engine.evaluate_rules(self.mock_controller, self.device_state)
        self.mock_controller.send_command.assert_called_once()


if __name__ == "__main__":
    unittest.main()
