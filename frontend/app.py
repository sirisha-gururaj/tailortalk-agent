import streamlit as st
import requests
import os

# The URL where your FastAPI backend is running
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/chat")

# Set up the page layout and title
st.set_page_config(page_title="TailorTalk Drive Agent", page_icon="📁")
st.title("T) TailorTalk")
st.markdown("I can help you search, filter, and discover files in your Google Drive. What are you looking for?")

# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me to find a file..."):
    # 1. Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # 2. Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 3. Send the message to our FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Searching Google Drive..."):
            try:
                # Make the POST request to the backend
                response = requests.post(BACKEND_URL, json={"message": prompt})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # NEW: Check if our FastAPI backend caught an error
                    if "error" in data:
                        bot_reply = f"🚨 **Error from Backend:** {data['error']}"
                    else:
                        bot_reply = data.get("response", f"Unexpected data received: {data}")
                        
                    st.markdown(bot_reply)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                else:
                    st.error(f"Backend HTTP error: {response.status_code}")
            except Exception as e:
                st.error(f"Failed to connect to backend. Is the FastAPI server running? Error: {e}")