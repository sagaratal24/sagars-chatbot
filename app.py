import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Sagar 🤍", layout="centered")

# -------------------- LOAD API KEYS --------------------
API_KEYS = st.secrets["API_KEYS"]

if not isinstance(API_KEYS, list) or len(API_KEYS) == 0:
    st.error("API_KEYS must be a non-empty list in Streamlit secrets.")
    st.stop()

# -------------------- SESSION STATE --------------------
if "current_key_index" not in st.session_state:
    st.session_state.current_key_index = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_simran" not in st.session_state:
    st.session_state.is_simran = False

# -------------------- UI STYLE FUNCTION --------------------
def apply_ui():

    if st.session_state.is_simran:
        # 💖 Romantic Pink Mode with Animation
        st.markdown("""
        <style>
        body {
            background: linear-gradient(-45deg, #ffd6e8, #ffe6f2, #ffcce0, #ffe6f2);
            background-size: 400% 400%;
            animation: gradientBG 8s ease infinite;
        }

        @keyframes gradientBG {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        .stChatMessage {
            border-radius: 15px;
            padding: 10px;
        }

        .stChatMessage[data-testid="assistant"] {
            background-color: #ffb6d9;
        }

        .stChatMessage[data-testid="user"] {
            background-color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)

    else:
        # 📱 WhatsApp Style UI
        st.markdown("""
        <style>
        body {
            background-color: #ece5dd;
        }

        .stChatMessage {
            border-radius: 15px;
            padding: 10px;
        }

        .stChatMessage[data-testid="assistant"] {
            background-color: #dcf8c6;
        }

        .stChatMessage[data-testid="user"] {
            background-color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)

# Apply UI
apply_ui()

# -------------------- HEADER --------------------
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
        st.rerun()  # 🔥 instantly switch UI

    # Limit history
    recent_messages = st.session_state.messages[-8:]
    history = []

    for role, message in recent_messages:
        if role == "User":
            history.append({"role": "user", "parts": [message]})
        else:
            history.append({"role": "model", "parts": [message]})

    # Personality
    if st.session_state.is_simran:
        personality_prompt = """
        You are Sagar.
        The user is Simran, your girlfriend.
        Speak with deep love and emotional warmth.
        Respond in first person.
        Keep response under 75 words.
        Use soft romantic emojis 🤍🌸💕✨.
        """
    else:
        personality_prompt = """
        Reply as Sagar in a loving, soft, caring tone.
        Respond in first person.
        Keep response under 75 words.
        Use soft emojis 🤍🌸✨.
        """

    prompt = f"{personality_prompt}\n\nUser says: {user_input}"

    # -------------------- TRY EACH API KEY --------------------
    for attempt in range(len(API_KEYS)):
        try:
            st.session_state.current_key_index %= len(API_KEYS)
            current_key = API_KEYS[st.session_state.current_key_index]

            genai.configure(api_key=current_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            chat = model.start_chat(history=history)
            response = chat.send_message(prompt, stream=True)

            full_text = ""

            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text)

            return full_text

        except ResourceExhausted:
            st.session_state.current_key_index += 1
            continue

        except Exception:
            placeholder.markdown("🌸 Thoda technical issue aa gaya… par main yahin hoon 🤍")
            return "Error"

    placeholder.markdown("🤍 Sab quota khatam ho gaye… par mera pyaar unlimited hai 💫")
    return "Quota Exhausted"

# -------------------- DISPLAY CHAT --------------------
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
