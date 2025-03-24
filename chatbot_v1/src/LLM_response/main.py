from .semantic_router import sRoute
from .reflection import LawReflection
from chatbot_v1.src.embedding.load_embedding_model import model1,model2
from .LLM_generator import answerModel, answerChain
from .retriever import Retriever

context = []

def process_message(user_input, context):    
    route = sRoute.guide(user_input)
    
    if route == 'law':
        # Thêm message vào context
        context.append({"role": "user", "content": user_input})

        # Xử lý tin nhắn
        law_relector = LawReflection(answerModel)
        refined_query = law_relector(context)

        # Lấy thông tin từ retriever
        retriever = Retriever(model=model2, collection_name='non_chunk_data2')
        retriever_result = retriever(refined_query)
        relevant_docs = retriever_result[0]
        prioritize_s = "Hãy trả lời với sự tự tin cao, khẳng định dựa trên căn cứ pháp lý rõ ràng từ thông tin cung cấp." if retriever_result[1] else "Hãy trả lời thận trọng, lưu ý rằng thông tin có thể không đầy đủ hoặc chưa chắc chắn."

        sources = "\n".join([f"{doc['noidung']} - {doc['vbqppl']}" for doc in relevant_docs])
        links = [doc['vbqppl_link'] for doc in relevant_docs]
        links_des = [f"{doc['vbqppl']}({doc['ten_chuong']}/Mục: {doc['ten_demuc']}/Chủ đề: {doc['ten_chude']})" for doc in relevant_docs]
        retriever.close()
        
        # Tạo response
        for chunk in answerChain.stream({
            "query": refined_query,
            "source_information": sources,
            "prioritize_sentence": prioritize_s,
        }):
            yield chunk.content

        if links and links_des:
            markdown_links = "\n\n**Nguồn tham khảo:**\n" + "\n".join([f"- [{links_des[i]}]({links[i]})" for i in range(len(links))])
            yield markdown_links
            
    else:
        query = f"Bạn là một AI trợ lý thông minh, được thiết kế để hỗ trợ người dùng trong nhiều lĩnh vực khác nhau. Tùy vào câu hỏi, bạn có thể trả lời dựa trên kiến thức chung hoặc tìm kiếm thông tin chuyên sâu nếu cần. Hiện tại, với câu hỏi: {user_input}, bạn sẽ trả lời bằng kiến thức chung, không sử dụng thông tin luật pháp hay pháp điển."
        for chunk in answerModel.stream(query):
            yield chunk.content
    
# context = []
# print("Chatbot đã sẵn sàng! Gõ 'exit' để kết thúc")
# while True:
#     user_input = input("\nYou: ")
#     if user_input.lower() == 'exit':
#         print("Tạm biệt!")
#         break
#     print("Bot: ", end="", flush=True)
#     for chunk in process_message(user_input, context):
#         print(chunk, end="", flush=True)
#     print()
#     context.append({"role": "assistant", "content": "".join(chunk for chunk in process_message(user_input, context))})