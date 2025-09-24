import streamlit as st
import os
import tempfile
import time
from google.cloud import texttospeech 
from google.auth.credentials import BaseCredentials # <-- Added for robust authentication

# --- Global Configuration and Authentication ---

# Define a custom credentials class to pass the API key in the headers
class ApiKeyCredentials(BaseCredentials):
    """Custom credentials class to pass the API key in the required header."""
    def __init__(self, api_key):
        self.api_key = api_key

    def apply(self, headers, **kwargs):
        # This header is required by Google for API Key authentication
        headers['X-Goog-Api-Key'] = self.api_key

# Securely get API Key from Streamlit Secrets
try:
    GOOGLE_API_KEY = st.secrets["api"]["google_tts_key"]
except KeyError:
    st.error("🚨 API key not found. Please add [api] google_tts_key to your Streamlit secrets.")
    GOOGLE_API_KEY = None 
    
# Word list
my_list = [
    'spray', 'riddles', 'basil', 'petals', 'trains', 'subway',
    'brushes', 'camel', 'plain', 'shuffle', 'holidays', 'essay',
    'fables', 'paints', 'claim', 'stairs', 'fingernails', 'despair'
]

# --- Session State Initialization ---

if 'word_index' not in st.session_state:
    st.session_state.word_index = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'show_next' not in st.session_state:
    st.session_state.show_next = False
if 'current_audio_path' not in st.session_state:
    st.session_state.current_audio_path = None # Track file to delete later

st.title("Spelling Quiz (Google Cloud TTS)")

# --- Utility Functions ---

def cleanup_file(filepath):
    """Safely deletes the temporary file."""
    if filepath and os.path.exists(filepath):
        try:
            # Short delay to ensure the file handle is released
            time.sleep(0.1) 
            os.unlink(filepath)
        except Exception as e:
            print(f"DEBUG: Failed to delete temp file {filepath}. Error: {e}")

@st.cache_data
def get_audio_path(word):
    """Generates audio using Google Cloud TTS, saves it to a file, and returns the path."""
    if not GOOGLE_API_KEY:
        st.warning("Cannot generate audio: API Key is missing.")
        return None
        
    # 1. Initialize client using the custom credentials object (FIX for TypeError)
    credentials = ApiKeyCredentials(GOOGLE_API_KEY)
    
    try:
        client = texttospeech.TextToSpeechClient(credentials=credentials)
    except Exception as e:
        print(f"DEBUG ERROR: Client Init Failed: {e}")
        st.error(f"❌ Failed to initialize TTS Client: {type(e).__name__}")
        return None

    synthesis_input = texttospeech.SynthesisInput(text=word)

    # Configure the voice and audio settings
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", 
        name="en-US-Standard-C"
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    temp_path = None
    try:
        # Perform the API request
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Save the audio content (bytes) to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(response.audio_content)
            temp_path = tmp.name
        
        return temp_path
            
    except Exception as e:
        print(f"DEBUG ERROR: Google Cloud TTS API Call failed for '{word}': {e}")
        st.error(f"❌ Could not generate audio. API Call Error: {type(e).__name__}. Check key validity/restrictions.")
        cleanup_file(temp_path)
        return None

# ----------------- MAIN APP LOGIC -----------------

if st.session_state.word_index < len(my_list):
    word = my_list[st.session_state.word_index]
    st.write("Listen to the word and type its spelling:")

    # Play button
    if st.button("🔊 Play Word"):
        # Cleanup the old file before creating a new one
        cleanup_file(st.session_state.current_audio_path) 
        
        # Generate the new audio and get its path
        st.session_state.current_audio_path = get_audio_path(word)
        
        # Display the audio player using the file path
        if st.session_state.current_audio_path:
            st.audio(st.session_state.current_audio_path, format='audio/mp3')

    user_input = st.text_input("Your spelling:", key=f"input_{st.session_state.word_index}")

    if st.button("Submit"):
        # Clean up the audio file after submit
        cleanup_file(st.session_state.current_audio_path)
        st.session_state.current_audio_path = None

        if user_input.lower() == word.lower():
            st.session_state.feedback = "✅ Correct! Well done."
        else:
            st.session_state.feedback = f"❌ Incorrect. The correct spelling is: **{word}**"
        st.session_state.show_next = True

    if st.session_state.feedback:
        st.write(st.session_state.feedback)

    if st.session_state.show_next:
        if st.button("Next Word"):
            st.session_state.word_index += 1
            st.session_state.feedback = ""
            st.session_state.show_next = False
else:
    # Final cleanup when the quiz is complete
    cleanup_file(st.session_state.current_audio_path)
    st.success("🎉 Quiz complete! Well done!")
