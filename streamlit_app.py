import streamlit as st
from gtts import gTTS
import io

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

def get_audio(word):
    try:
        tts = gTTS(text=word, lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp.read()
    except Exception as e:
        # Ensure this is visible in the Streamlit Cloud logs
        print(f"DEBUG: Error generating audio for '{word}': {e}") 
        return None

if st.session_state.word_index < len(my_list):
    word = my_list[st.session_state.word_index]
    st.write("Listen to the word and type its spelling:")

    # Play button
    if st.button("🔊 Play Word"):
        audio_bytes = get_audio(word)
        if audio_bytes:
            st.audio(audio_bytes, format='audio/mp3')
        else:
            # THIS WILL SHOW THE ERROR MESSAGE INSTEAD OF THE SILENT FAILURE
            st.error("❌ Failed to generate audio. Check the Streamlit logs!")

    user_input = st.text_input("Your spelling:", key=f"input_{st.session_state.word_index}")

    if st.button("Submit"):
        if user_input.lower() == word.lower():
            st.session_state.feedback = "✅ Correct!"
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
    st.success("🎉 Quiz complete! Well done!")
