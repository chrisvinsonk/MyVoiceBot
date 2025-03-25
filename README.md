# MyVoiceBot 🤖

A sophisticated voice-enabled AI assistant that can interact through both speech and text. Built with Streamlit and Hugging Face's AI models.

[MyVoiceBot Demo](https://myvoicebot.streamlit.app/)

## Features

- **Voice Interaction**: Speak to the bot and hear its responses
- **Text Input Option**: Type messages when voice input isn't available
- **Multiple AI Models**: Choose from different quality levels for responses
- **Responsive UI**: Modern and interactive user interface
- **Real-time Feedback**: Visual indicators for recording and speaking states

## Technologies Used

- **Streamlit**: For the web interface
- **Hugging Face API**: For AI model inference
  - Text generation (flan-t5 models)
  - Speech-to-Text (Whisper)
  - Text-to-Speech (Facebook MMS-TTS)
- **Pygame**: For audio playback
- **SoundDevice**: For microphone recording

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/chrisvinsonk/MyVoiceBot.git
   cd MyVoiceBot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   HF_API_KEY=your_huggingface_api_key
   ```

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Open your browser at `http://localhost:8501`

3. Use the interface to:
   - Click "Press to speak" to talk to the bot
   - Or enable text input mode in the sidebar
   - Select different AI models for varied response quality

## Project Structure

```
MyVoiceBot/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (API keys)
├── README.md 
└── resume/   
    ├── resume.py            
└── utils/                  # Utility modules
    ├── chatbot.py          # AI response generation
    ├── speech_processing.py # Audio recording and TTS
    └── resume_parser.py    # Resume processing utilities
```

## Configuration

You can customize the bot's behavior through the sidebar settings:

- **Input Mode**: Switch between voice and text input
- **AI Model Quality**:
  - Standard: Faster but simpler responses
  - Advanced: Higher quality but slower
  - Multilingual: Better for non-English queries

## Troubleshooting

### Common Issues

- **Microphone not working**: 
  - Check browser permissions
  - Ensure your microphone is properly connected
  - Try using text input mode as a fallback

- **Response quality issues**:
  - Try selecting a more advanced AI model in the sidebar
  - Ask more specific questions
  - For complex queries, use text input for better accuracy

## Future Improvements

- Add support for more languages
- Implement conversation memory
- Add voice customization options
- Create a mobile-friendly version

## License

[MIT License](LICENSE)

## Acknowledgments

- Hugging Face for providing the AI models and inference API
- Streamlit for the great web framework
- All the open-source packages that made this project possible

---

Created by [Chris Vinson Kunnankada]