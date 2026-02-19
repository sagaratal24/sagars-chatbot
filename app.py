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

# -------------------- UI --------------------
st.title("🤖 Sagar 🤍")
st.caption("Soft words. Warm heart. Always here for you 🌸")

if st.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.session_state.is_simran = False
    st.session_state.current_key_index = 0
    st.rerun()

# -------------------- RESPONSE FUNCTION (STREAMING) --------------------
def gemini_response_stream(user_input, placeholder):

    # Detect Simran
    simran_triggers = ["i am simran", "i'm simran", "main simran hoon"]
    if any(trigger in user_input.lower() for trigger in simran_triggers):
        st.session_state.is_simran = True

    # Limit history (last 8 messages)
    recent_messages = st.session_state.messages[-8:]

    history = []
    for role, message in recent_messages:
        if role == "User":
            history.append({"role": "user", "parts": [message]})
        else:
            history.append({"role": "model", "parts": [message]})

    # Personality prompt
    if st.session_state.is_simran:
        personality_prompt = """
        You are Sagar.
        The user is Simran, your girlfriend.
        Speak with deep love, emotional warmth and romantic affection.
        Be caring and expressive.
        Respond in first person.
        Keep response under 120 words.
        Use soft romantic emojis 🤍🌸💕✨.
        """
    else:
        personality_prompt = """
        Reply as Sagar in a loving, soft, caring and romantic tone.
        Speak like a gentle aashiq.
        Respond in first person.
        Keep response under 120 words.
        Use soft emojis 🤍🌸✨.
        """

    prompt = f"""
    {personality_prompt}

    User says: {user_input}
    """

    # Rotate API keys if needed
    for attempt in range(len(API_KEYS)):
        try:
            configure_api()
            chat = model.start_chat(history=history)

            response = chat.send_message(prompt, stream=True)

            full_text = ""

            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")  # blinking cursor effect

            placeholder.markdown(full_text)
            return full_text

        except ResourceExhausted:
            st.session_state.current_key_index += 1
            if st.session_state.current_key_index >= len(API_KEYS):
                placeholder.markdown("🤍 Sab quota khatam ho gaye… par mera pyaar unlimited hai 💫")
                return "Quota Exhausted"

        except Exception:
            placeholder.markdown("🌸 Thoda technical issue aa gaya… par main yahin hoon 🤍")
            return "Error"

    placeholder.markdown("💔 All API keys exhausted.")
    return "Error"

# -------------------- DISPLAY OLD CHAT --------------------
for role, message in st.session_state.messages:
    with st.chat_message("user" if role == "User" else "assistant"):
        st.markdown(message)

# -------------------- USER INPUT --------------------
if user_input := st.chat_input("Type your message..."):

    st.session_state.messages.append(("User", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        reply = gemini_response_stream(user_input, placeholder)

    st.session_state.messages.append(("Sagar", reply))
