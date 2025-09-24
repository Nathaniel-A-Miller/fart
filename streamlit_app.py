import streamlit as st
from gtts import gTTS
import io

# --- Streamlit App Initialization ---
st.set_page_config(page_title="Spelling Quiz")
st.title("Spelling Quiz")
st.markdown("Listen to the word and spell it in the box below.")

# --- Session State Management ---
# The word list is stored in session state so it's only created once.
if 'word_list' not in st.session_state:
    st.session_state.word_list = [
        'spray', 'riddles', 'basil', 'petals', 'trains', 'subway',
        'brushes', 'camel', 'plain', 'shuffle', 'holidays', 'essay',
        'fables', 'paints', 'claim', 'stairs', 'fingernails', 'despair'
    ]
    st.session_state.current_word_index = 0
    st.session_state.message = ""

# --- Function to generate audio and display it ---
def play_word_audio(word):
    """Generates and plays the audio for the given word."""
    try:
        # Check for potential library issues by wrapping in a try-except block
        tts = gTTS(text=word, lang='en')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        st.audio(audio_buffer, format="audio/mp3", autoplay=True)
    except Exception as e:
        # Catch any errors during the TTS process and show a message
        st.error(f"Error generating audio: {e}")
        st.write("Please check your internet connection and try again.")
        # Return an empty buffer to prevent further errors
        return io.BytesIO()

# --- Main App Logic ---
# Get the current word to be spelled
if st.session_state.current_word_index < len(st.session_state.word_list):
    current_word = st.session_state.word_list[st.session_state.current_word_index]
    
    # Display the quiz prompt
    st.header(f"Word {st.session_state.current_word_index + 1}/{len(st.session_state.word_list)}")
    st.write("Listen to the word:")
    play_word_audio(current_word)
    
    # Get user input
    user_input = st.text_input("Your spelling:", key="user_input")
    
    # Check button logic
    if st.button("Check Spelling"):
        if user_input.strip().lower() == current_word.lower():
            st.session_state.message = f"✅ Correct! The word was **{current_word}**."
            st.session_state.current_word_index += 1
        else:
            st.session_state.message = f"❌ Incorrect. The correct spelling is: **{current_word}**."
        
        # This forces the app to re-run and show the next word or result
        st.experimental_rerun()
        
    # Display the result message
    st.info(st.session_state.message)

else:
    # Quiz is finished
    st.success("🎉 You have completed the spelling quiz!")
    st.balloons()
    if st.button("Start Over"):
        st.session_state.current_word_index = 0
        st.session_state.message = ""
        st.experimental_rerun()
