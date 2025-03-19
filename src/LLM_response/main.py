from semantic_router import sRoute
from reflection import LawReflection
from LLM_generator import answerModel, answerChain
from retriever import Retriever

context = []

print("Chatbot đã sẵn sàng! Gõ 'exit' để kết thúc")

while True:
    user_input = input("\nYou: ")
    
    if user_input.lower() == 'exit':
        print("Tạm biệt!")
        break
        
    # Thêm message vào context
    context.append({"role": "user", "content": user_input})
    
    route = sRoute.guide(user_input)[0][1]
    print(f"ROUTE: {route}")
    
    if route == 'law':
        print("[ROUTE TO LAW]")

        # Xử lý tin nhắn
        law_relector = LawReflection(answerModel)
        refined_query = law_relector(context)
        print(f"\nREFINED: {refined_query}")

        # Lấy thông tin từ retriever
        retriever = Retriever()
        relevant_docs = retriever(refined_query)
        sources = "\n".join([f"{doc['noidung']} - {doc['vbqppl']} - Link : #{doc['vbqppl_link']}" for doc in relevant_docs])
        retriever.close()
        
        # Tạo response
        response = []
        print("Bot: ", end="", flush=True)
        for chunk in answerChain.stream({
            "query": refined_query,
            "source_information": sources
        }):
            print(chunk.content, end="", flush=True)
            response.append(chunk.content)
            
    else:
        print("[ROUTE TO CHAT]")
        response = []
        print("Bot: ", end="", flush=True)
        for chunk in answerModel.stream(user_input):
            print(chunk.content, end="", flush=True)
            response.append(chunk.content)
    
    # Thêm phản hồi vào context
    context.append({"role": "assistant", "content": "".join(response)})
    print()