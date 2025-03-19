from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

class LawReflection:
    def __init__(self, llm):
        self.llm = llm

    def __call__(self, chat_history, last_items_considered=5):
        if len(chat_history) >= last_items_considered:
            chat_history = chat_history[len(chat_history)-last_items_considered:]

        history_string = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in chat_history[:-1]]
        )

        # Prompt template chuyên về pháp luật
        legal_prompt = PromptTemplate.from_template(
            """Hãy cải tiến câu hỏi pháp lý sau đây dựa trên lịch sử trò chuyện, 
            tạo thành câu hỏi độc lập và rõ ràng bằng tiếng Việt. Chỉ cải tiến nếu cần thiết.

            Lịch sử trò chuyện:
            {history_string}

            Câu hỏi hiện tại:
            {current_question}

            Yêu cầu:
            - Giữ nguyên ngôn ngữ tiếng Việt
            - Tập trung vào yếu tố pháp lý
            - Làm rõ các thuật ngữ pháp lý
            - Không thêm thông tin không có trong câu hỏi
            - Định dạng: Câu hỏi ngắn gọn, rõ ràng"""
        )

        chain = legal_prompt | self.llm
        response = chain.invoke({
            "current_question": chat_history[-1]["content"],
            "history_string": history_string
        })

        return response.content