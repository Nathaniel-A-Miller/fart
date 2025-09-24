import streamlit as st
from gtts import gTTS
import os
import tempfile
import time # Added for a small delay to help with file operations

# Word list
my_list = [
    'spray', 'riddles', 'basil', 'petals', 'trains', 'subway',
    'brushes', 'camel', 'plain', 'shuffle', 'holidays', 'essay',
    'fables', 'paints', 'claim', 'stairs', 'fingernails', 'despair'
]

# Initialize session state
if 'word_index' not in st.session_state:
    st.session_state.word_index = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'show_next' not in st.session_state:
    st.session_state.show_next = False

st.title("Spelling Quiz")

def get_audio_path(word):
    """
    Generates audio for a word and saves it to a temporary MP3 file on disk,
    returning the file path. This is more reliable for deployment than using io.BytesIO.
    """
    temp_path = None
    try:
        tts = gTTS(text=word, lang='en')
        
        # Create a temporary file to save the MP3
        # delete=False ensures the file persists after the block so st.audio can access it
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tts.write_to_fp(tmp)
            temp_path = tmp.name
        
        return temp_path
    
    except Exception as e:
        # Print the actual error to the Streamlit Cloud logs for debugging
        print(f"DEBUG ERROR: gTTS failed for '{word}': {e}")
        st.error(f"❌ Could not generate audio for the word. Error: {e}")
        return None

def cleanup_file(filepath):
    """Safely deletes the temporary file."""
    if filepath and os.path.exists(filepath):
        try:
            # Add a small delay for good measure, to ensure the OS isn't using the file
            time.sleep(0.1) 
            os.unlink(filepath)
        except Exception as e:
            print(f"DEBUG: Failed to delete temp file {filepath}. Error: {e}")

if st.session_state.word_index < len(my_list):
    word = my_list[st.session_state.word_index]
    st.write("Listen to the word and type its spelling:")

    # State variable to hold the audio file path
    if 'current_audio_path' not in st.session_state:
        st.session_state.current_audio_path = None

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
        # The first thing we do after submit is clean up the audio file
        cleanup_file(st.session_state.current_audio_path)
        st.session_state.current_audio_path = None # Reset the state variable

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
            # Streamlit will automatically rerun the app from the top here
else:
    # Final cleanup when the quiz is complete
    cleanup_file(st.session_state.current_audio_path)
    st.success("🎉 Quiz complete! Well done!")
