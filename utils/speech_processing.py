import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import requests
import os
import time
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

STT_URL = "https://api-inference.huggingface.co/models/openai/whisper-tiny"
TTS_URL = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"

def record_audio(duration=5, samplerate=16000):
    """Record audio from the microphone."""
    try:
        # Print device info for debugging
        print("Available audio devices:")
        print(sd.query_devices())
        
        # Use default device
        print(f"Recording {duration} seconds of audio...")
        audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype=np.int16)
        sd.wait()
        
        # Check if audio was actually recorded
        if np.max(np.abs(audio)) < 50:  # Very low volume threshold
            print("Warning: Audio level is very low, might be microphone issue")
        
        return audio, samplerate
    except Exception as e:
        print(f"Error recording audio: {str(e)}")
        # Return some dummy audio data so the app doesn't crash
        return np.zeros((samplerate * duration,), dtype=np.int16), samplerate

def save_audio(audio, samplerate):
    """Save the recorded audio to a temporary file."""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        wav.write(temp_file.name, samplerate, audio)
        print(f"Audio saved to: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        print(f"Error saving audio: {str(e)}")
        return None

def transcribe_audio(audio_path):
    """Send audio to Hugging Face API for transcription."""
    if not audio_path:
        return ""
        
    try:
        print(f"Sending audio file {audio_path} for transcription...")
        
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        # First try with multipart/form-data
        with open(audio_path, "rb") as f:
            response = requests.post(
                STT_URL, 
                headers=HEADERS, 
                files={"file": f}
            )
        
        # If first attempt fails, try with raw bytes
        if response.status_code != 200:
            print(f"First transcription attempt failed: {response.status_code} - {response.text}")
            print("Trying alternative transcription method...")
            
            response = requests.post(
                STT_URL,
                headers={**HEADERS, "Content-Type": "audio/wav"},
                data=audio_data
            )
        
        if response.status_code == 200:
            result = response.json()
            transcribed_text = result.get("text", "")
            print(f"Transcription successful: '{transcribed_text}'")
            return transcribed_text
        else:
            print(f"Transcription failed: {response.status_code} - {response.text}")
            return ""
            
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        return ""

def synthesize_speech(text):
    """Convert text to speech using a valid Hugging Face API model."""
    try:
        print(f"Synthesizing speech for text: '{text}'")
        response = requests.post(TTS_URL, headers=HEADERS, json={"inputs": text})

        if response.status_code != 200:
            st.error(f"TTS API Error: {response.status_code} - {response.text}")
            print(f"TTS API Error: {response.status_code} - {response.text}")
            return None

        # Save audio file correctly
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with open(temp_file.name, "wb") as f:
            f.write(response.content)  # Write raw audio bytes
        
        print(f"Speech synthesized and saved to: {temp_file.name}")
        return temp_file.name  # Return saved file path

    except requests.exceptions.RequestException as e:
        st.error(f"TTS request failed: {str(e)}")
        print(f"TTS request failed: {str(e)}")
        return None