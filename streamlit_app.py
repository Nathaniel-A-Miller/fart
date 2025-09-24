import streamlit as st
from gtts import gTTS
import os
# List of words for the quiz
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
def play_audio(word):
    tts = gTTS(text=word, lang='en')
    filename = f"{word}.mp3"
    tts.save(filename)
    audio_file = open(filename, 'rb')
    st.audio(audio_file.read(), format='audio/mp3')
    audio_file.close()
    os.remove(filename)
st.title("Spelling Quiz")
if st.session_state.word_index < len(my_list):
    word = my_list[st.session_state.word_index]
    st.write("Listen to the word and type its spelling:")
    # Play audio
    play_audio(word)
    # Input box for spelling
    user_input = st.text_input("Your spelling:", key=f"input_{st.session_state.word_index}")
    # Check answer
    if st.button("Submit"):
        if user_input.lower() == word.lower():
            st.session_state.feedback = "Correct!"
        else:
            st.session_state.feedback = f"Incorrect. The correct spelling is: {word}"
        st.session_state.show_next = True
    # Show feedback
    if st.session_state.feedback:
        st.write(st.session_state.feedback)
    # Next button
    if st.session_state.show_next:
        if st.button("Next Word"):
            st.session_state.word_index += 1
            st.session_state.feedback = ""
            st.session_state.show_next = False
else:
    st.write("Quiz complete! 🎉")
