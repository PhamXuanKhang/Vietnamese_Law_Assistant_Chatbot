import streamlit as st
import requests
import uuid
st.set_page_config(layout="wide") 


# Set up the Streamlit interface
page = st.title("Chatbot Version 1.0")
# page = st.markdown("""
#     API endpoint: /v1/chat
# """)

st.session_state.fastapi_url1 = "http://localhost:8000/chat"  # Set your FastAPI URL here

# Generate a random session ID
session_id = str(uuid.uuid4())

# Initialize chat history in session state
if "chat_history_v1" not in st.session_state:
    st.session_state.chat_history_v1 = []

# Display the chat history using chat UI
for message in st.session_state.chat_history_v1:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input(key="chat", placeholder="What are you looking for?"):
    # Add user message to chat history
    st.session_state.chat_history_v1.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare the payload for the request
    payload = {
        "message": prompt,
        "context": st.session_state.chat_history_v1,
        "sessionId": session_id,
        "stream": True  # Enable streaming
    }

    # Stream the response from the Flask API
    with st.chat_message("assistant"):
        streamed_content = ""  # Initialize an empty string to concatenate chunks
        response = requests.post(st.session_state.fastapi_url1, json=payload, stream=True)

        # Create a placeholder to update the markdown
        response_placeholder = st.empty()

        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()  # Get the JSON response
            # Only display the message part of the response
            response_placeholder.markdown(result)

            # Once complete, add the full response to the chat history
            st.session_state.chat_history_v1.append({"role": "assistant", "content": result})
        else:
            st.error(f"Error: {response.status_code}")


