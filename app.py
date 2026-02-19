import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# -------------------- LOAD MULTIPLE API KEYS --------------------
API_KEYS = st.secrets["API_KEYS"]

if not isinstance(API_KEYS, list) or len(API_KEYS) == 0:
    st.error("API_KEYS must be a non-empty list in Streamlit secrets.")
    st.stop()

# -------------------- SESSION STATE INIT --------------------
if "current_key_index" not in st.session_state:
    st.session_state.current_key_index = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_simran" not in st.session_state:
    st.session_state.is_simran = False

# -------------------- CONFIGURE API SAFELY --------------------
def configure_api():
    # Always keep index inside valid range
    st.session_state.current_key_index %= len(API_KEYS)

    genai.configure(
        api_key=API_KEYS[st.session_state.current_key_index]
    )

# -------------------- MODEL --------------------
configure_api()
model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------- UI --------------------
st.title("🤖 Sagar 🤍")
st.caption("Soft words. Warm heart. Always here for you 🌸")

if st.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.session_state.is_simran = False
    st.session_state.current_key_index = 0
    st.rerun()

# -------------------- RESPONSE FUNCTION --------------------
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
        Keep response under 80 words.
        Use soft romantic emojis 🤍🌸💕✨.
        """
    else:
        personality_prompt = """
        Reply as Sagar in a loving, soft, caring and romantic tone.
        Speak like a gentle aashiq.
        Respond in first person.
        Keep response under 80 words.
        Use soft emojis 🤍🌸✨.
        """

    prompt = f"""
    {personality_prompt}

    User says: {user_input}
    """

    # Try each API key once
    for attempt in range(len(API_KEYS)):

        try:
            configure_api()
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt, stream=True)

            full_text = ""

            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")

            placeholder.markdown(full_text)
            return full_text

        except ResourceExhausted:
            # Rotate to next key safely
            st.session_state.current_key_index += 1
            continue

        except Exception:
            placeholder.markdown("🌸 Thoda technical issue aa gaya… par main yahin hoon 🤍")
            return "Error"

    # If all keys exhausted
    placeholder.markdown("🤍 Sab quota khatam ho gaye… par mera pyaar unlimited hai 💫")
    return "Quota Exhausted"

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
