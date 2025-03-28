import streamlit as st
import requests
import uuid

st.set_page_config(layout="wide", page_title="Chatbot Version 2.0")

with st.sidebar:
    st.title("Chatbot Hỗ trợ luật Việt Nam")
    st.info("Phát triển bởi: CuliData")
    st.image("logo.png", width=150)
    
# Thiết lập giao diện Streamlit
st.title("Chatbot Version 2.0 - Law Assistant Using Knowledge Graph")

st.session_state.fastapi_url2 = "http://localhost:8000/v2/chat"  # URL FastAPI

# Tạo session ID duy nhất
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Khởi tạo lịch sử chat
if "chat_history_v2" not in st.session_state:
    st.session_state.chat_history_v2 = []

# Hiển thị lịch sử chat
for message in st.session_state.chat_history_v2:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nhận đầu vào từ người dùng
if prompt := st.chat_input(key="chat_v2", placeholder="Hỏi tôi bất cứ điều gì về luật - chủ đề trật tự, an toàn xã hội!"):
    # Thêm tin nhắn người dùng vào lịch sử và hiển thị
    st.session_state.chat_history_v2.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chuẩn bị payload cho yêu cầu
    payload = {
        "message": prompt,
        "context": st.session_state.chat_history_v2,
        "sessionId": st.session_state.session_id,
        "stream": True
    }

    # Stream phản hồi từ FastAPI
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        streamed_content = ""
        
        # Gửi yêu cầu POST với streaming
        response = requests.post(st.session_state.fastapi_url2, json=payload, stream=True)
        
        if response.status_code == 200:
            # Đọc từng chunk từ luồng phản hồi
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    streamed_content += chunk
                    response_placeholder.markdown(streamed_content)
            # Sau khi stream xong, thêm vào lịch sử
            st.session_state.chat_history_v2.append({"role": "assistant", "content": streamed_content})
        else:
            st.error(f"Error: {response.status_code}")