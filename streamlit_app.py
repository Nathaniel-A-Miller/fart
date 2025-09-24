import streamlit as st
import os
import tempfile
import time
# --- NEW IMPORTS ---
from google.cloud import texttospeech 
# -------------------

# --- Securely get API Key ---
try:
    # Key should be set in Streamlit Secrets as [api] google_tts_key = "YOUR_KEY"
    GOOGLE_API_KEY = st.secrets["api"]["google_tts_key"]
except KeyError:
    # Display error if secret is missing (prevents crash)
    st.error("🚨 API key not found. Please add [api] google_tts_key to your Streamlit secrets.")
    GOOGLE_API_KEY = None

# Word list (unchanged)
my_list = [
    'spray', 'riddles', 'basil', 'petals', 'trains', 'subway',
    'brushes', 'camel', 'plain', 'shuffle', 'holidays', 'essay',
    'fables', 'paints', 'claim', 'stairs', 'fingernails', 'despair'
]

# Initialize session state (unchanged)
if 'word_index' not in st.session_state:
    st.session_state.word_index = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'show_next' not in st.session_state:
    st.session_state.show_next = False
if 'current_audio_path' not in st.session_state:
    st.session_state.current_audio_path = None # Track file to delete later

st.title("Spelling Quiz (Google Cloud TTS)")

def cleanup_file(filepath):
    """Safely deletes the temporary file."""
    if filepath and os.path.exists(filepath):
        try:
            time.sleep(0.1) 
            os.unlink(filepath)
        except Exception as e:
            print(f"DEBUG: Failed to delete temp file {filepath}. Error: {e}")

def get_audio_path(word):
    """Generates audio using Google Cloud TTS and saves it to a temporary file."""
    if not GOOGLE_API_KEY:
        # Stop here if the API key wasn't loaded from secrets
        return None
        
    # Initialize the client using the API key
    client = texttospeech.TextToSpeechClient(api_key=GOOGLE_API_KEY)
    synthesis_input = texttospeech.SynthesisInput(text=word)

    # Configure the voice and audio settings
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", 
        name="en-US-Standard-C" # A reliable US English voice
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
        print(f"DEBUG ERROR: Google Cloud TTS failed for '{word}': {e}")
        # The st.error message is more visible to the user than the print()
        st.error(f"❌ Could not generate audio. API Error: {type(e).__name__}")
        cleanup_file(temp_path)
        return None

# ----------------- MAIN APP LOGIC -----------------

if st.session_state.word_index < len(my_list):
    word = my_list[st.session_state.word_index]
    st.write("Listen to the word and type its spelling:")

    # State variable is already initialized above

    # Play button
    if st.button("🔊 Play Word"):
        # Cleanup the old file before creating a new one
        cleanup_file(st.session_state.current_audio_path) 
        
        # Generate the new audio and get its path
        st.session_state.current_audio_path = get_audio_path(word)
        
        # Display the audio player using the file path
        if st.session_state.current_audio_path:
            st.audio(st.session_state.current_audio_path, format='audio/mp3')
        # If get_audio_path failed, it already displayed an st.error

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
