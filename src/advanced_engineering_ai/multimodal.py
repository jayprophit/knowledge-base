"""
Multi-modal Capabilities: Speech, Image, Video Processing
"""
import speech_recognition as sr
import pyttsx3
import cv2

class Multimodal:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts = pyttsx3.init()

    def recognize_speech(self):
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)
            return self.recognizer.recognize_google(audio)

    def speak(self, text):
        self.tts.say(text)
        self.tts.runAndWait()

    def process_image(self, image_path):
        image = cv2.imread(image_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray_image
