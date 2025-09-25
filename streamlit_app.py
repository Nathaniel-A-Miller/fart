import streamlit as st
import requests

st.title("💭 Writing Check")

# Ask the question
answer = st.radio("Are you thinking about how bad your writing is?", ["Yes", "No"])

if answer == "No":
    st.success("Keep up the good work. 🎉")
else:
    # Download the mp3 file
    url = "https://www.dropbox.com/scl/fi/3xhllqzptq2wadc163r9q/proud-fart-288263.mp3?rlkey=9eksxolgj1vrdqvmp2d9qrx6e&st=680xm7tv&dl=1"
    response = requests.get(url)

    if response.status_code == 200:
        st.audio(response.content, format="audio/mp3")
    else:
        st.error("Couldn't load the audio file. 🚫")
