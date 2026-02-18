import streamlit as st
import google.generativeai as genai
import time
from google.api_core.exceptions import ResourceExhausted

# -------------------- LOAD MULTIPLE API KEYS --------------------
API_KEYS = st.secrets["API_KEYS"]

if "current_key_index" not in st.session_state:
    st.session_state.current_key_index = 0

def configure_api():
    genai.configure(api_key=API_KEYS[st.session_state.current_key_index])

configure_api()
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------- SESSION STATE --------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_simran" not in st.session_state:
    st.session_state.is_simran = False

# -------------------- TITLE --------------------
st.title("🤖 Sagar 🤍")
st.caption("Soft words. Warm heart. Always here for you 🌸")

if st.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.session_state.is_simran = False
    st.rerun()

# -------------------- RESPONSE FUNCTION --------------------
def gemini_response(user_input):

    # Detect if user says they are Simran
    if "i am simran" in user_input.lower() or "main simran hoon" in user_input.lower() or "i'm simran" in user_input.lower():
        st.session_state.is_simran = True

    recent_messages = st.session_state.messages[-8:]

    history = []
    for role, message in recent_messages:
        if role == "User":
            history.append({"role": "user", "parts": [message]})
        else:
            history.append({"role": "model", "parts": [message]})

    # Different prompt if user is Simran
    if st.session_state.is_simran:
        personality_prompt = """
        You are Sagar.
        The user is Simran, your girlfriend.
        Speak with deep love, emotional warmth and romantic affection.
        Be more intimate, caring, protective and expressive.
        Respond in first person as Sagar.
        Keep response under 120 words.
        Use soft romantic emojis 🤍🌸💕✨.
        """
    else:
        personality_prompt = """
        Reply to the user as Sagar in a loving, soft, caring and romantic tone.
        Speak like a gentle aashiq with warmth.
        Respond in first person as Sagar.
        Keep response under 120 words.
        Use soft emojis 🤍🌸✨.
        """

    prompt = f"""
    {personality_prompt}

    User says: {user_input}
    """

    for attempt in range(len(API_KEYS)):
        try:
            configure_api()
            chat = model.start_chat(history=history)
            time.sleep(1)
            response = chat.send_message(prompt)
            return response.text

        except ResourceExhausted:
            st.session_state.current_key_index += 1
            if st.session_state.current_key_index >= len(API_KEYS):
                return "🤍 Sab quota khatam ho gaye… par mera pyaar unlimited hai 💫"

        except Exception:
            return "🌸 Thoda technical issue aa gaya… par main yahin hoon 🤍"

    return "💔 All API keys exhausted."

# -------------------- DISPLAY CHAT --------------------
for role, message in st.session_state.messages:
    with st.chat_message("user" if role == "User" else "assistant"):
        st.markdown(message)

# -------------------- USER INPUT --------------------
if user_input := st.chat_input("Type your message..."):

    st.session_state.messages.append(("User", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    reply = gemini_response(user_input)

    st.session_state.messages.append(("Sagar", reply))
    with st.chat_message("assistant"):
        st.markdown(reply)
