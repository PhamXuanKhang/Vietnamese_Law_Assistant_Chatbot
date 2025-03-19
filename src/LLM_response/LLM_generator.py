import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv(".env")
api_key = os.getenv("API_KEY")

# Initialize the prompt template
answerPrompt = PromptTemplate.from_template("""Hãy trở thành chuyên gia tư vấn luật tại Việt Nam.
Câu hỏi của người dùng: {query}
Trả lời dựa vào thông tin sau: {source_information}
Yêu cầu:
1. Trả lời ngắn gọn, rõ ràng
2. Nếu không có thông tin, trả lời "Tôi không tìm thấy căn cứ pháp lý cho trường hợp này" sau đó gợi ý cách tìm kiếm ở các nguồn khác
3. Kèm điều luật liên quan""")

# Initialize the Gemini model with LangChain integration
answerModel = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # Thử với gemini-2.0-flash
    google_api_key=api_key,
    temperature=0.3,
    max_output_tokens=500
)

# Create the execution chain
answerChain = answerPrompt | answerModel