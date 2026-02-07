"""
Speech Service - Voice Input/Output
"""
import os
import time
import speech_recognition as sr
import pyttsx3
from config import Config

class SpeechService:
    """Handle speech recognition and text-to-speech"""
    
    def __init__(self, ai_service):
        """
        Initialize speech service.
        
        Args:
            ai_service (AIService): AI service for Whisper transcription
        """
        self.ai_service = ai_service
        
        # Initialize TTS
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', Config.TTS_RATE)
        self.tts_engine.setProperty('volume', Config.TTS_VOLUME)
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        
        print("✅ Speech service initialized")
    
    def speak(self, text):
        """
        Speak text using TTS.
        
        Args:
            text (str): Text to speak
        """
        print(f"🤖 Assistant: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        """
        Listen to microphone and transcribe using Groq Whisper.
        
        Returns:
            str: Transcribed text or None
        """
        with sr.Microphone() as source:
            print("\n🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # Record audio
                audio = self.recognizer.listen(
                    source,
                    timeout=Config.SPEECH_TIMEOUT,
                    phrase_time_limit=Config.SPEECH_PHRASE_LIMIT
                )
                
                print("🔄 Processing speech...")
                
                # Save to temp file
                temp_file = "temp_audio.wav"
                with open(temp_file, "wb") as f:
                    f.write(audio.get_wav_data())
                
                # Transcribe using Groq Whisper
                text = self.ai_service.transcribe_audio(temp_file)
                
                # Cleanup
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                if text:
                    print(f"👤 You said: {text}")
                    return text.lower()
                else:
                    return None
                
            except sr.WaitTimeoutError:
                print("⏱️  No speech detected")
                return None
            except Exception as e:
                print(f"❌ Listen error: {e}")
                return None
