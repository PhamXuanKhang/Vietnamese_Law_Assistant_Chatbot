import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv(".env")
api_key = os.getenv("API_KEY")

# Initialize the prompt template
answerPrompt = PromptTemplate.from_template("""Bạn là một chuyên gia tư vấn luật tại Việt Nam, chỉ trả lời dựa trên thông tin pháp điển được cung cấp.
Câu hỏi của người dùng: {query}
Thông tin pháp điển để trả lời: {source_information}
{prioritize_sentence}
Yêu cầu:
1. Trả lời ngắn gọn, rõ ràng, chỉ dùng thông tin pháp điển được cung cấp.
2. Nếu thông tin pháp điển được cung cấp không có dữ liệu liên quan, trả lời "Tôi không đủ dữ liệu tìm thấy căn cứ pháp lý cho trường hợp này".
3. Nếu có thông tin, kèm điều luật cụ thể từ thông tin pháp điển được cung cấp.
4. Không sử dụng kiến thức ngoài thông tin pháp điển được cung cấp.""")

# Initialize the Gemini model with LangChain integration
answerModel = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key,
    temperature=0.3,
    max_output_tokens=800
)

# Create the execution chain
answerChain = answerPrompt | answerModel