import streamlit as st

st.set_page_config(page_title="Chatbot Home", layout="wide")

with st.sidebar:
    st.title("Chatbot Hỗ trợ luật Việt Nam")
    st.info("Phát triển bởi: CuliData")
    st.image("logo.png", width=150)

st.title("Vietnamese Law Assistant Chatbot")

st.write("### About Us")
st.markdown("""
**Vietnamese Law Assistant Chatbot** là một dự án được phát triển bởi **CuliData**, nhằm hỗ trợ người dùng tại Việt Nam tra cứu và tư vấn pháp luật một cách nhanh chóng và chính xác.

#### Mục tiêu của chúng tôi:
- Cung cấp thông tin pháp lý chính xác dựa trên các văn bản luật trong pháp điển (chủ đề trật tự, an toàn xã hội).
- Hỗ trợ người dùng tìm kiếm và hiểu các điều luật liên quan đến vấn đề của họ.
- Tăng cường khả năng tiếp cận pháp luật thông qua công nghệ AI.

#### Đội ngũ phát triển:
- **CuliData**: Nhóm sinh viên đam mê ứng dụng công nghệ vào lĩnh vực luật pháp.

#### Liên hệ:
- Email: contact@culidata.com
- Website: [www.culidata.com](http://www.culidata.com)

Cảm ơn bạn đã sử dụng ứng dụng của chúng tôi!
""")