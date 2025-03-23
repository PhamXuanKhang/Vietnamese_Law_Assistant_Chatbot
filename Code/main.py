import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from NER import ner
from retrive import multi_retr

load_dotenv()

answerPrompt = PromptTemplate.from_template(
    """Hãy trở thành chuyên gia tư vấn luật tại Việt Nam.
Câu hỏi của người dùng: {query}
Trả lời dựa vào thông tin sau:
{source_information}
Yêu cầu:
1. Trả lời ngắn gọn, rõ ràng
2. Nếu không có thông tin, trả lời "Tôi không tìm thấy căn cứ pháp lý cho trường hợp này" và gợi ý cách tìm kiếm ở nguồn khác
3. Kèm điều luật liên quan"""
)

answerModel = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY", ""),
    temperature=0.3,
    max_output_tokens=500
)

answerChain = answerPrompt | answerModel

def main():
    query = input("Nhập query của bạn: ").strip()
    
    tokens, predictions, ner_entities = ner.infer(
        query,
        model_path="/home/maianhtruong/Law_bot/Law_Chatbot/Code/NER/bilstm_ner.pt"
    )
    print("\nThực thể được NER nhận diện:", ner_entities)

    if not ner_entities:
        print("\nKhông nhận diện được thực thể nào. Truy vấn toàn câu:")

    results = multi_retr.retrieve_entity(query, ner_entities if ner_entities else None)
    
    top3 = results[:5]
    source_info = ""
    for e in top3:
        source_info += f"- {e['label']} ({e['name']}): {e['value']}\n"

    if not top3:
        print("Không tìm thấy căn cứ pháp lý phù hợp.")
        return

    response = answerChain.invoke({
        "query": query,
        "source_information": source_info
    })

    print("\n=== Câu trả lời từ LLM ===")
    print(response)

if __name__ == "__main__":
    main()
