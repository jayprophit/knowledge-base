"""
Mock TensorFlow Module
======================

This is a minimal mock implementation of TensorFlow to satisfy import requirements
without needing the full TensorFlow installation. This is particularly useful in
environments where TensorFlow cannot be installed (such as certain Windows configurations).

Usage:
    import sys
    sys.path.insert(0, 'path/to/mock_modules')
    import tensorflow as tf
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_tensorflow")
logger.info("Using mock TensorFlow module")

class MockTensor:
    def __init__(self, value=None, shape=None, dtype=None):
        self.value = value
        self.shape = shape or ()
        self.dtype = dtype or 'float32'
    
    def __repr__(self):
        return f"MockTensor(value={self.value}, shape={self.shape}, dtype={self.dtype})"
    
    def numpy(self):
        return self.value

# Mock TensorFlow modules and classes
class keras:
    class layers:
        class Dense:
            def __init__(self, units, activation=None, **kwargs):
                self.units = units
                self.activation = activation
                self.kwargs = kwargs
        
        class Conv2D:
            def __init__(self, filters, kernel_size, activation=None, **kwargs):
                self.filters = filters
                self.kernel_size = kernel_size
                self.activation = activation
                self.kwargs = kwargs
        
        class LSTM:
            def __init__(self, units, return_sequences=False, **kwargs):
                self.units = units
                self.return_sequences = return_sequences
                self.kwargs = kwargs
        
        class Dropout:
            def __init__(self, rate, **kwargs):
                self.rate = rate
                self.kwargs = kwargs
        
        class Flatten:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
    
    class models:
        class Model:
            def __init__(self, inputs, outputs):
                self.inputs = inputs
                self.outputs = outputs
            
            def compile(self, optimizer, loss, metrics=None):
                pass
            
            def fit(self, x, y, epochs=1, batch_size=32, validation_data=None, **kwargs):
                return MockHistory()
            
            def predict(self, x):
                return [MockTensor(0.0)]
            
            def save(self, filepath):
                logger.info(f"Mock save model to {filepath}")
                return True
    
    class optimizers:
        class Adam:
            def __init__(self, learning_rate=0.001):
                self.learning_rate = learning_rate
    
    class losses:
        categorical_crossentropy = "mock_categorical_crossentropy"
        binary_crossentropy = "mock_binary_crossentropy"
        mse = "mock_mse"
    
    class utils:
        class to_categorical:
            def __init__(self, y, num_classes=None):
                self.y = y
                self.num_classes = num_classes

class MockHistory:
    def __init__(self):
        self.history = {
            'loss': [0.5, 0.4, 0.3],
            'accuracy': [0.5, 0.6, 0.7],
            'val_loss': [0.6, 0.5, 0.4],
            'val_accuracy': [0.4, 0.5, 0.6]
        }

# Expose modules
__version__ = "2.12.0-mock"

# Create common attributes and functions
def constant(value, dtype=None, shape=None):
    return MockTensor(value, shape, dtype)

def Variable(initial_value, dtype=None, name=None):
    return MockTensor(initial_value, None, dtype)

def placeholder(dtype, shape=None, name=None):
    return MockTensor(None, shape, dtype)

def Session():
    class MockSession:
        def __init__(self):
            pass
        
        def run(self, fetches, feed_dict=None):
            return 0
        
        def close(self):
            pass
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()
    
    return MockSession()

# Expose common attributes
float32 = "float32"
float64 = "float64"
int32 = "int32"
int64 = "int64"
string = "string"
bool = "bool"

# Log usage
logger.info("Mock TensorFlow module initialized")
