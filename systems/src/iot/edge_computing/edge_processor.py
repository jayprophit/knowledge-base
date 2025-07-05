import numpy as np
import time
import logging
import threading
import queue
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DataType(Enum):
    """Data types supported by the edge processor."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    JSON = "json"
    BINARY = "binary"


@dataclass
class DataPoint:
    """
    Represents a single data point from a sensor or input.
    """
    source_id: str  # ID of the data source (e.g., sensor ID, device ID)
    timestamp: float  # Unix timestamp
    data_type: DataType  # Type of data
    value: Any  # The actual data value
    metadata: Dict[str, Any] = None  # Optional metadata about the data point
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
        if "unit" not in self.metadata and self.data_type == DataType.NUMERIC:
            self.metadata["unit"] = "unknown"


class ProcessingTask:
    """
    Represents a data processing task to be executed on the edge.
    """
    def __init__(self, task_id: str, processor: Callable[[List[DataPoint]], Any],
                 data_sources: List[str], batch_size: int = 1, interval: Optional[float] = None):
        """
        Initialize a processing task.
        
        Args:
            task_id: Unique identifier for the task
            processor: Function that processes data points
            data_sources: List of data source IDs to collect data from
            batch_size: Number of data points to collect before processing
            interval: If set, process data at fixed intervals regardless of batch size
        """
        self.task_id = task_id
        self.processor = processor
        self.data_sources = data_sources
        self.batch_size = batch_size
        self.interval = interval
        self.last_run = 0
        self.data_buffer = []
        
    def should_process(self, current_time: float) -> bool:
        """
        Determine if the task should be processed now.
        
        Args:
            current_time: Current time as Unix timestamp
            
        Returns:
            True if task should be processed, False otherwise
        """
        # Check if we have enough data points
        if len(self.data_buffer) >= self.batch_size:
            return True
            
        # Check if interval-based processing is due
        if self.interval and (current_time - self.last_run) >= self.interval:
            return len(self.data_buffer) > 0
            
        return False
        
    def add_data(self, data_point: DataPoint) -> bool:
        """
        Add a data point to the task's buffer.
        
        Args:
            data_point: Data point to add
            
        Returns:
            True if added, False otherwise
        """
        if data_point.source_id in self.data_sources:
            self.data_buffer.append(data_point)
            return True
        return False
        
    def process(self) -> Any:
        """
        Process the buffered data and clear the buffer.
        
        Returns:
            Result of the processor function
        """
        if not self.data_buffer:
            return None
            
        try:
            result = self.processor(self.data_buffer)
            self.last_run = time.time()
            self.data_buffer = []
            return result
        except Exception as e:
            logger.error(f"Error processing task {self.task_id}: {e}")
            return None


class EdgeProcessor:
    """
    Edge computing processor that runs data processing tasks locally.
    """
    def __init__(self, device_id: str, max_queue_size: int = 1000):
        """
        Initialize the edge processor.
        
        Args:
            device_id: ID of the device running this processor
            max_queue_size: Maximum size of the data queue
        """
        self.device_id = device_id
        self.tasks: Dict[str, ProcessingTask] = {}
        self.data_queue = queue.Queue(maxsize=max_queue_size)
        self.running = False
        self.processing_thread = None
        self.output_handlers: List[Callable[[str, Any], None]] = []
        
    def register_task(self, task: ProcessingTask) -> bool:
        """
        Register a new processing task.
        
        Args:
            task: Processing task to register
            
        Returns:
            Success status
        """
        if task.task_id in self.tasks:
            logger.warning(f"Task {task.task_id} already registered")
            return False
            
        self.tasks[task.task_id] = task
        logger.info(f"Registered task {task.task_id} for data sources {task.data_sources}")
        return True
        
    def unregister_task(self, task_id: str) -> bool:
        """
        Unregister a processing task.
        
        Args:
            task_id: ID of task to unregister
            
        Returns:
            Success status
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Unregistered task {task_id}")
            return True
        return False
        
    def add_data(self, data_point: DataPoint) -> bool:
        """
        Add a data point to be processed.
        
        Args:
            data_point: Data point to add
            
        Returns:
            Success status
        """
        try:
            self.data_queue.put_nowait(data_point)
            return True
        except queue.Full:
            logger.warning("Data queue is full, dropping data point")
            return False
            
    def add_output_handler(self, handler: Callable[[str, Any], None]):
        """
        Add handler for processing results.
        
        Args:
            handler: Function that handles task output (task_id, result)
        """
        self.output_handlers.append(handler)
        
    def _handle_output(self, task_id: str, result: Any):
        """
        Handle task processing result.
        
        Args:
            task_id: ID of the task that produced the result
            result: Processing result
        """
        for handler in self.output_handlers:
            try:
                handler(task_id, result)
            except Exception as e:
                logger.error(f"Error in output handler: {e}")
                
    def _process_loop(self):
        """Internal processing loop run in a separate thread."""
        while self.running:
            try:
                # Process all data in the queue
                while not self.data_queue.empty():
                    data_point = self.data_queue.get_nowait()
                    
                    # Distribute data point to relevant tasks
                    for task in self.tasks.values():
                        task.add_data(data_point)
                    
                    self.data_queue.task_done()
                    
                # Check if any tasks need processing
                current_time = time.time()
                for task_id, task in self.tasks.items():
                    if task.should_process(current_time):
                        result = task.process()
                        if result is not None:
                            self._handle_output(task_id, result)
                            
                # Sleep briefly to avoid excessive CPU usage
                time.sleep(0.01)
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                
    def start(self):
        """Start the edge processor."""
        if self.running:
            logger.warning("Edge processor already running")
            return
            
        self.running = True
        self.processing_thread = threading.Thread(
            target=self._process_loop, name="EdgeProcessorThread")
        self.processing_thread.daemon = True
        self.processing_thread.start()
        logger.info(f"Started edge processor for device {self.device_id}")
        
    def stop(self):
        """Stop the edge processor."""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
        logger.info(f"Stopped edge processor for device {self.device_id}")


class DataPreprocessor:
    """
    Provides common data preprocessing functions for edge computing.
    """
    @staticmethod
    def moving_average(data_points: List[DataPoint], window_size: int = 5) -> List[float]:
        """
        Calculate moving average for numeric data points.
        
        Args:
            data_points: List of numeric data points
            window_size: Size of the moving average window
            
        Returns:
            List of moving averages
        """
        values = [dp.value for dp in data_points 
                 if dp.data_type == DataType.NUMERIC]
        
        if not values:
            return []
            
        results = []
        for i in range(len(values)):
            window = values[max(0, i - window_size + 1):i + 1]
            results.append(sum(window) / len(window))
            
        return results
        
    @staticmethod
    def threshold_detection(data_points: List[DataPoint], 
                           threshold: float, 
                           comparison: str = "greater") -> List[Tuple[DataPoint, bool]]:
        """
        Detect when values cross a threshold.
        
        Args:
            data_points: List of numeric data points
            threshold: Threshold value
            comparison: Type of comparison ("greater", "less", "equal")
            
        Returns:
            List of (data_point, threshold_crossed) tuples
        """
        results = []
        
        for dp in data_points:
            if dp.data_type != DataType.NUMERIC:
                continue
                
            threshold_crossed = False
            if comparison == "greater":
                threshold_crossed = dp.value > threshold
            elif comparison == "less":
                threshold_crossed = dp.value < threshold
            elif comparison == "equal":
                threshold_crossed = abs(dp.value - threshold) < 1e-6
                
            results.append((dp, threshold_crossed))
            
        return results
        
    @staticmethod
    def normalize(data_points: List[DataPoint]) -> List[float]:
        """
        Normalize numeric data to range [0, 1].
        
        Args:
            data_points: List of numeric data points
            
        Returns:
            List of normalized values
        """
        values = [dp.value for dp in data_points 
                 if dp.data_type == DataType.NUMERIC]
        
        if not values:
            return []
            
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            return [0.5] * len(values)
            
        return [(v - min_val) / (max_val - min_val) for v in values]
