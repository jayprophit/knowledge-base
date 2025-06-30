#!/usr/bin/env python3
"""
Multi-Modal Recognition System Tutorial

This tutorial demonstrates how to use the unified multi-modal recognition system
to process and analyze audio and visual data together.
"""

import os
import sys
import time
import argparse
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our multi-modal recognition system
from src.multimodal.recognition_api import MultiModalRecognitionSystem, MultiModalResult


def analyze_video_file(video_path, confidence_threshold=0.5, frame_interval=10):
    """Analyze a video file with multi-modal recognition."""
    print(f"\n{'=' * 50}")
    print(f"Analyzing video: {video_path}")
    print(f"{'=' * 50}\n")
    
    # Initialize our recognition system
    system = MultiModalRecognitionSystem()
    
    # Process the video file
    start_time = time.time()
    
    print("Processing video with audio and visual recognition...")
    results = system.process_video(
        video_path=video_path,
        extract_audio=True,
        frame_interval=frame_interval,
        confidence_threshold=confidence_threshold
    )
    
    elapsed_time = time.time() - start_time
    print(f"Processing completed in {elapsed_time:.2f} seconds\n")
    
    # Print basic results summary
    print(f"Video analysis summary:")
    print(f"- Frames analyzed: {results['video_analysis']['frames_analyzed']}")
    print(f"- Unique objects detected: {len(results['video_analysis']['objects_detected'])}")
    
    # Print object detection details
    print("\nDetected objects:")
    for obj in results['video_analysis']['objects_detected']:
        print(f"- {obj['class_name']} ({obj['confidence']:.2f})")
    
    # Print audio analysis if available
    if results['audio_analysis']:
        print("\nAudio analysis:")
        
        if 'speech_recognition' in results['audio_analysis'] and results['audio_analysis']['speech_recognition'].get('text'):
            print(f"- Transcript: {results['audio_analysis']['speech_recognition']['text']}")
        
        if 'sound_classification' in results['audio_analysis'] and results['audio_analysis']['sound_classification'].get('label'):
            print(f"- Sound classification: {results['audio_analysis']['sound_classification']['label']} "
                  f"({results['audio_analysis']['sound_classification'].get('confidence', 0):.2f})")
        
        if 'music_analysis' in results['audio_analysis'] and results['audio_analysis']['music_analysis'].get('genre'):
            print(f"- Music genre: {results['audio_analysis']['music_analysis']['genre']}")
    
    # Print context understanding
    if 'context' in results:
        print("\nContext understanding:")
        if results['context'].get('scene_description'):
            print(f"- Scene: {', '.join(results['context']['scene_description'])}")
        if results['context'].get('audio_context'):
            print(f"- Audio context: {', '.join(results['context']['audio_context'])}")
    
    return results


def analyze_image_and_audio(image_path, audio_path, confidence_threshold=0.5):
    """Analyze separate image and audio files together."""
    print(f"\n{'=' * 50}")
    print(f"Analyzing image: {image_path}")
    print(f"Analyzing audio: {audio_path}")
    print(f"{'=' * 50}\n")
    
    # Initialize our recognition system
    system = MultiModalRecognitionSystem()
    
    # Process the files
    start_time = time.time()
    
    print("Processing image and audio with multi-modal recognition...")
    result = system.process_image_and_audio(
        image_path=image_path,
        audio_path=audio_path,
        confidence_threshold=confidence_threshold
    )
    
    elapsed_time = time.time() - start_time
    print(f"Processing completed in {elapsed_time:.2f} seconds\n")
    
    # Print object detection results
    if result.objects_detected:
        print("Detected objects:")
        for obj in result.objects_detected:
            print(f"- {obj['class_name']} ({obj['confidence']:.2f})")
    
    # Print speech recognition results
    if result.speech_recognition and result.speech_recognition.get('text'):
        print(f"\nSpeech transcript: {result.speech_recognition['text']}")
    
    # Print voice analysis results
    if result.voice_analysis:
        print("\nVoice analysis:")
        for key, value in result.voice_analysis.items():
            print(f"- {key}: {value}")
    
    # Print sound classification results
    if result.sound_classification and result.sound_classification.get('label'):
        print(f"\nSound classification: {result.sound_classification['label']} "
              f"({result.sound_classification.get('confidence', 0):.2f})")
    
    # Print context understanding
    if result.context:
        print("\nContext understanding:")
        if result.context.get('scene_description'):
            print(f"- Scene: {', '.join(result.context['scene_description'])}")
        if result.context.get('audio_context'):
            print(f"- Audio context: {', '.join(result.context['audio_context'])}")
    
    return result


def visualize_results(result, output_path=None):
    """Visualize the results of multi-modal recognition."""
    # For video analysis, create a timeline visualization
    if isinstance(result, dict) and 'video_analysis' in result:
        # Create figure for timeline visualization
        plt.figure(figsize=(15, 8))
        
        # Extract timeline data
        timeline = result['video_analysis']['object_timeline']
        timestamps = [entry['timestamp'] for entry in timeline]
        frame_numbers = [entry['frame_number'] for entry in timeline]
        
        # Count objects per frame
        object_counts = [len(entry['objects']) for entry in timeline]
        
        # Plot object counts over time
        plt.subplot(2, 1, 1)
        plt.plot(timestamps, object_counts, 'b-', linewidth=2)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Objects Detected')
        plt.title('Object Detection Timeline')
        plt.grid(True)
        
        # Get unique object classes across all frames
        unique_classes = set()
        for entry in timeline:
            for obj in entry['objects']:
                unique_classes.add(obj['class_name'])
        
        # Plot object class distribution
        plt.subplot(2, 1, 2)
        class_counts = {}
        for cls in unique_classes:
            class_counts[cls] = 0
            for entry in timeline:
                for obj in entry['objects']:
                    if obj['class_name'] == cls:
                        class_counts[cls] += 1
        
        plt.bar(class_counts.keys(), class_counts.values())
        plt.xlabel('Object Class')
        plt.ylabel('Count')
        plt.title('Object Class Distribution')
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
    # For image/audio analysis, show the image with detections
    elif isinstance(result, MultiModalResult) and result.objects_detected:
        if os.path.exists(result.source.split("Image: ")[1].split(",")[0]):
            image_path = result.source.split("Image: ")[1].split(",")[0]
            image = cv2.imread(image_path)
            if image is not None:
                # Convert to RGB for plotting
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Create figure for image visualization
                plt.figure(figsize=(10, 8))
                plt.imshow(image)
                
                # Draw bounding boxes for detected objects
                for obj in result.objects_detected:
                    if 'bbox' in obj:
                        x, y, w, h = obj['bbox']
                        confidence = obj['confidence']
                        class_name = obj['class_name']
                        
                        # Draw rectangle
                        rect = plt.Rectangle((x, y), w, h, fill=False, edgecolor='red', linewidth=2)
                        plt.gca().add_patch(rect)
                        
                        # Add label
                        plt.text(x, y-10, f"{class_name} {confidence:.2f}", 
                                color='white', fontsize=12, backgroundcolor='red')
                
                plt.title('Object Detection Results')
                plt.axis('off')
                
    # Save or show the visualization
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {output_path}")
    else:
        plt.show()


def main():
    """Main function to run the tutorial."""
    parser = argparse.ArgumentParser(description='Multi-Modal Recognition Tutorial')
    parser.add_argument('--mode', choices=['video', 'image_audio'], default='video',
                      help='Mode of analysis: video or image_audio')
    parser.add_argument('--video', type=str, help='Path to video file')
    parser.add_argument('--image', type=str, help='Path to image file')
    parser.add_argument('--audio', type=str, help='Path to audio file')
    parser.add_argument('--confidence', type=float, default=0.5,
                      help='Confidence threshold for object detection')
    parser.add_argument('--output', type=str, help='Path to save visualization')
    
    args = parser.parse_args()
    
    if args.mode == 'video':
        if not args.video:
            print("Error: Video path is required for video mode")
            return
        
        if not os.path.exists(args.video):
            print(f"Error: Video file not found: {args.video}")
            return
        
        results = analyze_video_file(
            args.video, 
            confidence_threshold=args.confidence
        )
        visualize_results(results, args.output)
        
    elif args.mode == 'image_audio':
        if not args.image or not args.audio:
            print("Error: Both image and audio paths are required for image_audio mode")
            return
        
        if not os.path.exists(args.image):
            print(f"Error: Image file not found: {args.image}")
            return
            
        if not os.path.exists(args.audio):
            print(f"Error: Audio file not found: {args.audio}")
            return
        
        result = analyze_image_and_audio(
            args.image, 
            args.audio,
            confidence_threshold=args.confidence
        )
        visualize_results(result, args.output)


if __name__ == "__main__":
    # Print banner
    print("\n" + "=" * 70)
    print(" MULTI-MODAL RECOGNITION SYSTEM TUTORIAL ".center(70, "="))
    print("=" * 70 + "\n")
    
    main()
