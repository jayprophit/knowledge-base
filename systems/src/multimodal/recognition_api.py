"""
Unified Multi-Modal Recognition API

This module provides a unified API for multi-modal recognition across audio and visual data,
integrating specialized recognition systems into a cohesive framework.
"""

import os
import numpy as np
import cv2
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field

# Import audio recognition components
from ..audio.audio_recognition import AudioRecognitionSystem
from ..audio.speech_recognition import RecognitionResult
from ..audio.sound_classification import SoundClassificationResult

# Import vision recognition components
from ..vision.object_detection import ObjectDetector, DetectionResult, get_detector, ObjectCategory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MultiModalResult:
    """Data class to store multi-modal recognition results."""
    source: str  # Path or description of the source
    timestamp: Optional[float] = None  # For synchronized audio-visual data
    
    # Audio results
    audio_type: Optional[str] = None
    speech_recognition: Optional[Dict] = None
    voice_analysis: Optional[Dict] = None
    music_analysis: Optional[Dict] = None
    sound_classification: Optional[Dict] = None
    
    # Vision results
    objects_detected: Optional[List[Dict]] = None
    scene_classification: Optional[Dict] = None
    
    # Merged analysis
    context: Optional[Dict] = None  # Combined scene understanding
    annotations: Optional[Dict] = None  # Any additional metadata


class MultiModalRecognitionSystem:
    """Unified system for multi-modal recognition across audio and visual data."""
    
    def __init__(self, 
                speech_model_path: Optional[str] = None,
                sound_model_path: Optional[str] = None,
                vision_model_type: str = "yolo",
                vision_model_path: Optional[str] = None,
                device: Optional[str] = None):
        """Initialize the multi-modal recognition system.
        
        Args:
            speech_model_path: Path to speech recognition model
            sound_model_path: Path to sound classification model
            vision_model_type: Type of vision model ('yolo', 'face', etc.)
            vision_model_path: Path to vision model
            device: Device for model inference ('cuda', 'cpu')
        """
        # Initialize audio recognition system
        self.audio_system = AudioRecognitionSystem(
            speech_model_path=speech_model_path,
            sound_model_path=sound_model_path
        )
        
        # Initialize vision recognition system
        self.vision_system = get_detector(
            model_type=vision_model_type,
            model_path=vision_model_path,
            device=device
        )
        
        logger.info("Multi-Modal Recognition System initialized")
    
    def process_video(self, video_path: str, 
                     extract_audio: bool = True,
                     frame_interval: int = 10,
                     confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """Process video file with both audio and visual analysis.
        
        Args:
            video_path: Path to video file
            extract_audio: Whether to extract and process audio
            frame_interval: Process every nth frame (for efficiency)
            confidence_threshold: Minimum confidence for object detection
            
        Returns:
            Dictionary with combined audio-visual analysis results
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        results = {
            'source': video_path,
            'video_analysis': {
                'frames_analyzed': 0,
                'objects_detected': [],
                'object_timeline': []
            },
            'audio_analysis': None
        }
        
        # Extract audio if requested
        if extract_audio:
            try:
                # Extract audio using ffmpeg (temporary file)
                audio_path = video_path + '.temp_audio.wav'
                os.system(f'ffmpeg -i "{video_path}" -q:a 0 -map a "{audio_path}" -y')
                
                if os.path.exists(audio_path):
                    # Process the extracted audio
                    audio_results = self.audio_system.process_audio(audio_path)
                    results['audio_analysis'] = audio_results
                    
                    # Clean up temporary file
                    os.remove(audio_path)
                else:
                    logger.warning(f"Failed to extract audio from {video_path}")
            
            except Exception as e:
                logger.error(f"Audio extraction error: {e}")
        
        # Process video frames
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Process every nth frame
                if frame_count % frame_interval == 0:
                    # Get current timestamp
                    timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    
                    # Detect objects in frame
                    detections = self.vision_system.detect(
                        frame, 
                        confidence_threshold=confidence_threshold
                    )
                    
                    # Convert DetectionResult objects to dictionaries
                    frame_objects = []
                    for det in detections:
                        obj = {
                            'category': det.category.value,
                            'class_name': det.class_name,
                            'confidence': det.confidence,
                            'bbox': det.bbox
                        }
                        if det.attributes:
                            obj['attributes'] = det.attributes
                        
                        frame_objects.append(obj)
                    
                    # Add to timeline
                    results['video_analysis']['object_timeline'].append({
                        'timestamp': timestamp,
                        'frame_number': frame_count,
                        'objects': frame_objects
                    })
                    
                    # Add unique objects to overall list
                    for obj in frame_objects:
                        if obj not in results['video_analysis']['objects_detected']:
                            results['video_analysis']['objects_detected'].append(obj)
                    
                    results['video_analysis']['frames_analyzed'] += 1
                
                frame_count += 1
            
            cap.release()
            
        except Exception as e:
            logger.error(f"Video processing error: {e}")
        
        # Generate combined analysis
        self._generate_context(results)
        
        return results
    
    def process_image_and_audio(self, image_path: str, audio_path: str,
                              confidence_threshold: float = 0.5) -> MultiModalResult:
        """Process separate image and audio files with combined analysis.
        
        Args:
            image_path: Path to image file
            audio_path: Path to audio file
            confidence_threshold: Minimum confidence for object detection
            
        Returns:
            MultiModalResult with combined analysis
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Process image
        image_detections = self.vision_system.detect(
            image_path, 
            confidence_threshold=confidence_threshold
        )
        
        # Process audio
        audio_results = self.audio_system.process_audio(audio_path)
        
        # Convert vision results to dictionary format
        vision_results = []
        for det in image_detections:
            obj = {
                'category': det.category.value,
                'class_name': det.class_name,
                'confidence': det.confidence,
                'bbox': det.bbox
            }
            if det.attributes:
                obj['attributes'] = det.attributes
            
            vision_results.append(obj)
        
        # Create combined result
        result = MultiModalResult(
            source=f"Image: {image_path}, Audio: {audio_path}",
            audio_type=audio_results.get('audio_type'),
            speech_recognition=audio_results.get('speech_recognition'),
            voice_analysis=audio_results.get('voice_analysis'),
            music_analysis=audio_results.get('music_analysis'),
            sound_classification=audio_results.get('sound_classification'),
            objects_detected=vision_results
        )
        
        # Generate context from combined results
        self._generate_context_for_result(result)
        
        return result
    
    def process_live_feed(self, camera_id: int = 0, duration: int = 10,
                        confidence_threshold: float = 0.5) -> MultiModalResult:
        """Process live camera feed with audio for real-time recognition.
        
        Args:
            camera_id: Camera device ID
            duration: Recording duration in seconds
            confidence_threshold: Minimum confidence for object detection
            
        Returns:
            MultiModalResult with combined analysis
        """
        # Capture video frame from camera
        cap = cv2.VideoCapture(camera_id)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise RuntimeError(f"Failed to capture frame from camera {camera_id}")
        
        # Record audio from microphone
        audio_results = self.audio_system.recognize_from_microphone(duration=duration)
        
        # Process the captured frame
        image_detections = self.vision_system.detect(
            frame, 
            confidence_threshold=confidence_threshold
        )
        
        # Convert vision results to dictionary format
        vision_results = []
        for det in image_detections:
            obj = {
                'category': det.category.value,
                'class_name': det.class_name,
                'confidence': det.confidence,
                'bbox': det.bbox
            }
            if det.attributes:
                obj['attributes'] = det.attributes
            
            vision_results.append(obj)
        
        # Create combined result
        result = MultiModalResult(
            source="Live camera and microphone feed",
            timestamp=0.0,  # Current frame
            audio_type="microphone_recording",
            speech_recognition=audio_results.get('speech_recognition'),
            objects_detected=vision_results
        )
        
        # Generate context from combined results
        self._generate_context_for_result(result)
        
        return result
    
    def _generate_context(self, results: Dict) -> None:
        """Generate contextual understanding from combined audio-visual results.
        
        Args:
            results: Dictionary with audio and visual analysis results
        """
        context = {
            'scene_description': [],
            'audio_context': [],
            'detected_activities': [],
            'confidence_level': 'medium'
        }
        
        # Extract audio context
        if results.get('audio_analysis'):
            audio = results['audio_analysis']
            
            if audio.get('speech_recognition') and audio['speech_recognition'].get('text'):
                context['audio_context'].append(f"Speech: {audio['speech_recognition']['text']}")
            
            if audio.get('sound_classification') and audio['sound_classification'].get('label'):
                context['audio_context'].append(
                    f"Sound: {audio['sound_classification']['label']}"
                )
                
            if audio.get('music_analysis') and audio['music_analysis'].get('genre'):
                context['audio_context'].append(
                    f"Music: {audio['music_analysis']['genre']}"
                )
        
        # Extract visual context
        if results.get('video_analysis') and results['video_analysis'].get('objects_detected'):
            objects = results['video_analysis']['objects_detected']
            
            # Group objects by category
            categories = {}
            for obj in objects:
                cat = obj['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(obj['class_name'])
            
            # Generate scene description
            for cat, items in categories.items():
                # Get unique items with counts
                item_counts = {}
                for item in items:
                    if item not in item_counts:
                        item_counts[item] = 0
                    item_counts[item] += 1
                
                # Create description
                for item, count in item_counts.items():
                    if count > 1:
                        context['scene_description'].append(f"{count} {item}s")
                    else:
                        context['scene_description'].append(item)
        
        # Add context to results
        results['context'] = context
    
    def _generate_context_for_result(self, result: MultiModalResult) -> None:
        """Generate contextual understanding for a MultiModalResult.
        
        Args:
            result: MultiModalResult object to update with context
        """
        context = {
            'scene_description': [],
            'audio_context': [],
            'detected_activities': [],
            'confidence_level': 'medium'
        }
        
        # Extract audio context
        if result.speech_recognition and result.speech_recognition.get('text'):
            context['audio_context'].append(f"Speech: {result.speech_recognition['text']}")
        
        if result.sound_classification and result.sound_classification.get('label'):
            context['audio_context'].append(
                f"Sound: {result.sound_classification['label']}"
            )
            
        if result.music_analysis and result.music_analysis.get('genre'):
            context['audio_context'].append(
                f"Music: {result.music_analysis['genre']}"
            )
        
        # Extract visual context
        if result.objects_detected:
            # Group objects by category
            categories = {}
            for obj in result.objects_detected:
                cat = obj['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(obj['class_name'])
            
            # Generate scene description
            for cat, items in categories.items():
                # Get unique items with counts
                item_counts = {}
                for item in items:
                    if item not in item_counts:
                        item_counts[item] = 0
                    item_counts[item] += 1
                
                # Create description
                for item, count in item_counts.items():
                    if count > 1:
                        context['scene_description'].append(f"{count} {item}s")
                    else:
                        context['scene_description'].append(item)
        
        # Update result with context
        result.context = context


# Example usage
if __name__ == "__main__":
    # Initialize multi-modal system
    system = MultiModalRecognitionSystem()
    
    # Example: Process video with audio and visual analysis
    # results = system.process_video("path/to/video.mp4")
    # print(f"Video analysis: {len(results['video_analysis']['object_timeline'])} frames analyzed")
    # if results['audio_analysis']:
    #     print(f"Audio type: {results['audio_analysis']['audio_type']}")
    #     if results['audio_analysis'].get('speech_recognition'):
    #         print(f"Speech: {results['audio_analysis']['speech_recognition']['text']}")
    
    print("Multi-Modal Recognition System loaded successfully")
