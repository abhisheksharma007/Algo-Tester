import os

import streamlit as st
import requests
import dotenv
dotenv.load_dotenv()

# Set up Groq API key and endpoint
GROQ_API_KEY = os.environ['GROQ_API_KEY']  # Replace with your Groq API key
GROQ_API_ENDPOINT = "https://api.groq.ai/v1/chat"  # Replace with your Groq API endpoint

# Set up Streamlit app
st.title("🗨️ Simple Chatbot with Groq & Streamlit")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]

# Function to get response from Groq
def get_groq_response(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": "groq-model",  # Replace with your model name if needed
        "messages": messages,
    }
    
    response = requests.post(GROQ_API_ENDPOINT, json=data, headers=headers)
    response_data = response.json()
    return response_data['choices'][0]['message']['content']

# Sidebar for user input
st.sidebar.title("Chat with the Assistant")
user_input = st.sidebar.text_input("You:", key="input", placeholder="Type your message here...")

# Display chat history
for msg in st.session_state.messages:
    role = "User" if msg["role"] == "user" else "Assistant"
    st.chat_message(role).write(msg["content"])

# Handle user input
if st.sidebar.button("Send") and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    assistant_response = get_groq_response(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    st.sidebar.text_input("You:", key="input", placeholder="Type your message here...", value="")
    st.experimental_rerun()
