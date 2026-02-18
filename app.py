import streamlit as st
import google.generativeai as genai
import os

GOOGLE_APIKEY = st.secrets['API_KEYS']
genai.configure(api_key=GOOGLE_APIKEY)

model = genai.GenerativeModel(model_name="gemini-2.5-flash")  

if "messages" not in st.session_state:
    st.session_state.messages = []

def gemini_response(user_message):
    prompt = f"""Reply to the user as Sagar in a funny, humorous, confident and friendly tone. 
    Respond like you ARE Sagar (first person). 
    Add emojis to make the response more fun.
    User: {user_message}"""
    
    response = model.generate_content(prompt)
    return response.text

st.title(f"🤖 Sagar's Bot 🤝")
st.markdown("Sagar here 😎🔥 Convo 💬✨? Crushed it 🤜🏻💥.")

with st.form("chat_input", clear_on_submit=True):
    user = st.text_input("You:", "")
    submit = st.form_submit_button("Send")

if submit and user:
    st.session_state.messages.append(("user", user))
    reply = gemini_response(user)
    st.session_state.messages.append(("Sagar", reply))

for role, messages in st.session_state.messages:
    if role == "user":
        st.markdown(f"**🧑 You:** {messages}")
    else:
        st.markdown(f"**🤖 Sagar's Bot:** {messages}")
