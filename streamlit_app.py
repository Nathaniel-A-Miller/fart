import streamlit as st

st.title("💭 Writing Check")

# Radio with no default selection on page load
answer = st.radio(
    "Are you thinking about how bad your writing is?",
    ["Yes", "No"],
    index=None
)

if answer == "No":
    st.success("Keep up the good work. 🎉")

elif answer == "Yes":
    # Direct link with dl=1 to get the raw mp3
    url = "https://www.dropbox.com/scl/fi/3xhllqzptq2wadc163r9q/proud-fart-288263.mp3?rlkey=9eksxolgj1vrdqvmp2d9qrx6e&st=680xm7tv&dl=1"
    
    # Inject HTML audio tag with autoplay
    st.markdown(
        f"""
        <audio autoplay>
            <source src="{url}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        """,
        unsafe_allow_html=True
    )
