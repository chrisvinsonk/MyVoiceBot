import streamlit as st
import time
from utils.speech_processing import record_audio, save_audio, transcribe_audio, synthesize_speech
from utils.chatbot import get_bot_response
import pygame
import threading
import os
from dotenv import load_dotenv

# Initialize pygame mixer for better audio playback
pygame.mixer.init()

# Set page configuration
st.set_page_config(
    page_title="My Voice Bot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS with improved styling
st.markdown("""
<style>
    /* Overall app styling */
    .main {
        background-color: #f8f9fa;
        padding: 20px;
    }
    
    /* Updated chat message styles with better text contrast */
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.8rem; 
        margin-bottom: 1rem; 
        display: flex;
        align-items: flex-start;
        animation: fadeIn 0.5s ease-in-out;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .chat-message.user {
        background-color: #e3f2fd;
        border-left: 5px solid #2979ff;
        color: #000000; /* Dark text for contrast */
    }
    .chat-message.bot {
        background-color: #f0f7fa;
        border-left: 5px solid #00796b;
        color: #000000; /* Dark text for contrast */
    }
    
    /* Avatar styling */
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        font-size: 20px;
        flex-shrink: 0;
    }
    .avatar.user {
        background-color: #2979ff;
        color: white;
    }
    .avatar.bot {
        background-color: #00796b;
        color: white;
    }
    
    /* Message content */
    .message-content {
        flex-grow: 1;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    /* Recording animation */
    .recording-animation {
        display: inline-block;
        width: 15px;
        height: 15px;
        background-color: #f44336;
        border-radius: 50%;
        margin-right: 10px;
        animation: pulse 1s infinite;
    }
    
    /* Speaking animation */
    .speaking-animation {
        display: inline-block;
        margin-left: 10px;
    }
    .speaking-animation span {
        display: inline-block;
        width: 5px;
        height: 5px;
        margin: 0 2px;
        background-color: #2979ff;
        border-radius: 50%;
        animation: soundwave 0.5s infinite alternate;
    }
    .speaking-animation span:nth-child(2) {
        animation-delay: 0.2s;
    }
    .speaking-animation span:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes soundwave {
        from { height: 5px; }
        to { height: 15px; }
    }
    
    /* Button styling */
    .speak-button button {
        background-color: #2979ff;
        color: white;
        border-radius: 30px;
        padding: 12px 24px;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 0 auto;
        display: block;
        font-size: 16px;
    }
    .speak-button button:hover {
        background-color: #1565c0;
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Center the button container */
    .button-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    
    /* Status messages */
    .status-message {
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* Text input styling */
    .text-input {
        border-radius: 8px;
        border: 1px solid #ddd;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Send button styling */
    .send-button button {
        background-color: #00796b;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .send-button button:hover {
        background-color: #00695c;
        transform: scale(1.05);
    }
    
    /* Header styling */
    .header {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #2979ff 0%, #00796b 100%);
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .header h1 {
        font-size: 2.5rem;
        margin-bottom: 10px;
        animation: fadeIn 1s ease-in-out;
    }
    .header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Make the chat container scrollable */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 10px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'audio_playing' not in st.session_state:
    st.session_state.audio_playing = False
if 'text_input_fallback' not in st.session_state:
    st.session_state.text_input_fallback = False

# Load environment variables
load_dotenv()

# Play audio in a separate thread to avoid blocking
def play_audio_file(file_path):
    if not file_path:
        return
        
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        st.session_state.audio_playing = True
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        st.session_state.audio_playing = False
        
        # Clean up temp file after playback
        try:
            os.remove(file_path)
        except:
            pass
    except Exception as e:
        print(f"Error playing audio: {str(e)}")

# Custom header with animation
st.markdown("""
<div class="header">
    <h1>🤖 My Voice Bot</h1>
    <p>Your interactive AI assistant - speak or type to chat</p>
</div>
""", unsafe_allow_html=True)

# Display chat messages in a scrollable container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message['role'] == 'user':
        st.markdown(f"""
        <div class='chat-message user'>
            <div class='avatar user'>👤</div>
            <div class='message-content'>
                <b>You:</b><br>{message['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='chat-message bot'>
            <div class='avatar bot'>🤖</div>
            <div class='message-content'>
                <b>Bot:</b><br>{message['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Add some space
st.write("")

# Add toggle for text input fallback in sidebar
st.sidebar.title("Settings")
use_text_input = st.sidebar.checkbox("Use text input mode", 
                                     value=st.session_state.text_input_fallback)
st.session_state.text_input_fallback = use_text_input

# Choose a better AI model
model_options = {
    "Standard": "google/flan-t5-small",
    "Advanced": "google/flan-t5-xl",
    "Multilingual": "google/mt5-large"
}
selected_model = st.sidebar.selectbox(
    "Choose AI model quality:",
    options=list(model_options.keys()),
    index=0
)

# Input section
if use_text_input:
    # Text input as fallback
    st.markdown("<div class='text-input'>", unsafe_allow_html=True)
    user_text = st.text_input("Type your message here", key="text_input")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Center the send button
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    st.markdown("<div class='send-button'>", unsafe_allow_html=True)
    send_button = st.button("Send Message")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if send_button and user_text.strip():
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_text})
        
        # Get bot response with the selected model
        bot_response = get_bot_response(user_text, model=model_options[selected_model])
        
        # Add bot response to chat
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        
        # Synthesize speech
        speech_file = synthesize_speech(bot_response)
        
        # Rerun to update the chat interface
        st.rerun()
else:
    # Voice input - center the button
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    st.markdown("<div class='speak-button'>", unsafe_allow_html=True)
    record_button = st.button("🎤 Press to speak")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Handle recording
if record_button and not use_text_input:
    # Show recording animation
    recording_status = st.empty()
    recording_status.markdown("""
    <div class='status-message' style='background-color: #ffebee;'>
        <div class='recording-animation'></div>
        Recording... Speak now
    </div>
    """, unsafe_allow_html=True)
    
    # Record audio
    audio_data, samplerate = record_audio(duration=5)
    
    # Update status
    recording_status.markdown("""
    <div class='status-message' style='background-color: #fff8e1;'>
        <div style='color: #ff9800;'>Processing your message...</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Process the audio
    audio_path = save_audio(audio_data, samplerate)
    user_input = transcribe_audio(audio_path)
    
    # Check if transcription was successful
    if user_input and user_input.strip():
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get bot response with the selected model
        bot_response = get_bot_response(user_input, model=model_options[selected_model])
        
        # Add bot response to chat
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        
        # Synthesize speech
        speech_file = synthesize_speech(bot_response)
        
        # Clear the recording status
        recording_status.empty()
        
        # Rerun to update the chat interface
        st.rerun()
    else:
        recording_status.markdown("""
        <div class='status-message' style='background-color: #ffebee;'>
            <div style='color: #f44336;'>
                Sorry, I couldn't hear you. Please try again or switch to text input mode.
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(3)
        recording_status.empty()

# Play the latest bot response automatically
if st.session_state.messages and st.session_state.messages[-1]['role'] == 'assistant' and not st.session_state.audio_playing:
    latest_message = st.session_state.messages[-1]['content']
    
    # Visual indicator that the bot is speaking
    speaking_status = st.empty()
    speaking_status.markdown("""
    <div class='status-message' style='background-color: #e3f2fd;'>
        Bot is speaking
        <div class='speaking-animation'>
            <span></span><span></span><span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate and play the audio
    speech_file = synthesize_speech(latest_message)
    if speech_file:
        # Start audio playback in a separate thread
        audio_thread = threading.Thread(target=play_audio_file, args=(speech_file,))
        audio_thread.start()
        
        # Wait briefly to ensure the thread starts
        time.sleep(0.5)
        
        # Check if audio is actually playing
        if st.session_state.audio_playing:
            # Keep the speaking animation while audio is playing
            while st.session_state.audio_playing:
                time.sleep(0.1)
                
        # Clear speaking status when done
        speaking_status.empty()

# Instructions or help
with st.expander("ℹ️ How to use"):
    st.markdown("""
    ### Using the Voice Bot
    
    **Voice Mode:**
    1. Click the **Press to speak** button
    2. Speak clearly into your microphone 
    3. Wait for the bot to respond both in text and voice
    4. Continue the conversation by pressing the button again
    
    **Text Mode:**
    1. Enable text mode in the sidebar settings
    2. Type your message in the text box
    3. Click "Send Message" to get a response
    
    **Tips:**
    - For better quality responses, select a more advanced AI model in the sidebar
    - If your microphone isn't working, switch to text input mode
    - Make sure your microphone is properly connected and browser permissions are granted
    """)