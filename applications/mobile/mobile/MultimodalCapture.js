import React, { useState } from 'react';
import { View, Text, TouchableOpacity, Image, ActivityIndicator, StyleSheet, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';
import { Audio } from 'expo-av';

/**
 * MultimodalCapture - React Native component for capturing images, audio, and selecting files
 * Features:
 * - Capture photo/video from camera
 * - Record audio
 * - Pick image/audio/document from device
 * - Upload to backend for analysis
 */
const API_BASE = 'http://192.168.1.100:8000'; // Change to your backend URL

export default function MultimodalCapture({ onResult }) {
  const [image, setImage] = useState(null);
  const [audio, setAudio] = useState(null);
  const [recording, setRecording] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Capture photo from camera
  const handleCapturePhoto = async () => {
    setError(null);
    let permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      setError('Camera permission denied');
      return;
    }
    let result = await ImagePicker.launchCameraAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images });
    if (!result.canceled && result.assets && result.assets[0].uri) {
      setImage(result.assets[0].uri);
      setAudio(null);
    }
  };

  // Pick image or audio from device
  const handlePickFile = async () => {
    setError(null);
    let result = await DocumentPicker.getDocumentAsync({ type: ['image/*', 'audio/*'] });
    if (result.type === 'success') {
      if (result.mimeType && result.mimeType.startsWith('image')) {
        setImage(result.uri);
        setAudio(null);
      } else if (result.mimeType && result.mimeType.startsWith('audio')) {
        setAudio(result.uri);
        setImage(null);
      }
    }
  };

  // Record audio
  const handleRecordAudio = async () => {
    setError(null);
    if (recording) {
      // Stop recording
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setAudio(uri);
      setRecording(null);
    } else {
      // Start recording
      const permission = await Audio.requestPermissionsAsync();
      if (!permission.granted) {
        setError('Audio recording permission denied');
        return;
      }
      try {
        await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
        const { recording } = await Audio.Recording.createAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
        setRecording(recording);
      } catch (err) {
        setError('Failed to start recording');
      }
    }
  };

  // Upload file to backend for analysis
  const handleAnalyze = async () => {
    setError(null);
    setIsLoading(true);
    setResult(null);
    try {
      let uri = image || audio;
      let type = image ? 'image' : 'audio';
      let filename = uri.split('/').pop();
      let formData = new FormData();
      formData.append('file', { uri, name: filename, type: type + '/*' });
      formData.append('type', type);
      let res = await fetch(`${API_BASE}/analyze_multimodal`, {
        method: 'POST',
        headers: { 'Content-Type': 'multipart/form-data' },
        body: formData,
      });
      let data = await res.json();
      setResult(data);
      if (onResult) onResult(data);
    } catch (err) {
      setError('Failed to analyze file');
    }
    setIsLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Multimodal Capture</Text>
      <View style={styles.buttonRow}>
        <TouchableOpacity style={styles.button} onPress={handleCapturePhoto}>
          <Text>📷 Camera</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={handlePickFile}>
          <Text>📁 Pick File</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={handleRecordAudio}>
          <Text>{recording ? '⏹️ Stop' : '🎤 Record'}</Text>
        </TouchableOpacity>
      </View>
      {image && (
        <View style={styles.previewContainer}>
          <Image source={{ uri: image }} style={styles.previewImage} />
        </View>
      )}
      {audio && !recording && (
        <Text style={styles.audioText}>Audio ready for analysis: {audio.split('/').pop()}</Text>
      )}
      {isLoading && <ActivityIndicator size="large" color="#1a73e8" />}
      {error && <Text style={styles.error}>{error}</Text>}
      <TouchableOpacity
        style={[styles.analyzeButton, !(image || audio) && styles.disabledButton]}
        onPress={handleAnalyze}
        disabled={!(image || audio) || isLoading}
      >
        <Text style={styles.analyzeButtonText}>Analyze</Text>
      </TouchableOpacity>
      {result && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>Analysis Result:</Text>
          <Text style={styles.resultText}>{JSON.stringify(result, null, 2)}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    margin: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#1a73e8',
    textAlign: 'center',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  button: {
    backgroundColor: '#f1f3f4',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 4,
  },
  previewContainer: {
    alignItems: 'center',
    marginVertical: 12,
  },
  previewImage: {
    width: 200,
    height: 200,
    borderRadius: 8,
    resizeMode: 'contain',
  },
  audioText: {
    textAlign: 'center',
    color: '#333',
    marginVertical: 8,
  },
  analyzeButton: {
    backgroundColor: '#1a73e8',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginVertical: 12,
  },
  analyzeButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  disabledButton: {
    backgroundColor: '#b3c7e6',
  },
  error: {
    color: 'red',
    textAlign: 'center',
    marginVertical: 8,
  },
  resultContainer: {
    backgroundColor: '#f1f3f4',
    borderRadius: 8,
    padding: 12,
    marginTop: 16,
  },
  resultTitle: {
    fontWeight: 'bold',
    color: '#1a73e8',
    marginBottom: 4,
  },
  resultText: {
    color: '#333',
    fontSize: 14,
  },
});
