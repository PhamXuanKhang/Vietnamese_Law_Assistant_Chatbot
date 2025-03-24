import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Generator

from .NER import ner
from .retrieve import multi_retr

load_dotenv()

answerPrompt = PromptTemplate.from_template("""Bạn là một chuyên gia tư vấn luật tại Việt Nam, chỉ trả lời dựa trên thông tin pháp điển được cung cấp.
Câu hỏi của người dùng: {query}
Thông tin pháp điển để trả lời: {source_information}
Yêu cầu:
1. Trả lời ngắn gọn, rõ ràng, chỉ dùng thông tin pháp điển được cung cấp.
2. Nếu thông tin pháp điển được cung cấp không có dữ liệu liên quan, trả lời "Tôi không đủ dữ liệu tìm thấy căn cứ pháp lý cho trường hợp này".
3. Nếu có thông tin, kèm điều luật cụ thể từ thông tin pháp điển được cung cấp.
4. Không sử dụng kiến thức ngoài thông tin pháp điển được cung cấp.""")

answerModel = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("API_KEY", ""),
    temperature=0.3,
    max_output_tokens=1000
)

answerChain = answerPrompt | answerModel

def process_message_v2(message: str, context: List[Dict[str, str]]) -> Generator[str, None, None]:    
    tokens, predictions, ner_entities = ner.infer(
        query=message,
        model_path="./chatbot_v2/Code/NER/bilstm_ner.pt"
    )
    results = multi_retr.retrieve_entity(message, ner_entities if ner_entities else None)
    top3 = results[:5]

    if not top3:
        # Chỉ yield câu trả lời khi không tìm thấy thông tin
        yield "Không tìm thấy căn cứ pháp lý phù hợp.\n"
        return
    
    source_info = ""
    for e in top3:
        source_info += f"- {e['label']} ({e['name']}): {e['value']}\n"

    response = answerChain.invoke({
        "query": message,
        "source_information": source_info
    })

    # Stream câu trả lời từ LLM
    response_text = response if isinstance(response, str) else response.content
    chunk_size = 100 
    for i in range(0, len(response_text), chunk_size):
        yield response_text[i:i + chunk_size]
    yield "\n"