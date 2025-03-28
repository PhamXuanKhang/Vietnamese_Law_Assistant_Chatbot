from chatbot_v1.src.embedding.load_embedding_model import model1, model2
import weaviate
import weaviate.classes.query as wq
from dotenv import load_dotenv
import os

load_dotenv()
host = os.getenv("VECTOR_DB_HOST")
port = os.getenv("VECTOR_DB_PORT")

# Class truy vấn từ db
class Retriever:
    def __init__(self, model, collection_name):
        self.model = model
        self.client = weaviate.connect_to_local(host=host, port=port)
        self.collection = self.client.collections.get(collection_name)

    def __call__(self, query):
        query_vector = self.model.encode(query).tolist()
        
        response = self.collection.query.hybrid(
            query=query,
            vector=query_vector,
            alpha=0.5,
            query_properties=["vbqppl", "noidung", "ten_demuc", "ten_chuong"],
            return_properties=["mapc", "vbqppl", "noidung", "vbqppl_link", "ten_demuc", "ten_chuong", "ten_chude"],
            return_metadata=wq.MetadataQuery(score=True),
            limit=10
        )
        
        context_1 = []
        context_2 = []
        
        for obj in response.objects:
            score = obj.metadata.score
            result = {
                "noidung": obj.properties.get("noidung", ""),
                "vbqppl": obj.properties.get("vbqppl", ""),
                "mapc": obj.properties.get("mapc", ""),
                "vbqppl_link": obj.properties.get("vbqppl_link", ""),
                "ten_demuc": obj.properties.get("ten_demuc", ""),
                "ten_chuong": obj.properties.get("ten_chuong", ""),
                "ten_chude": obj.properties.get("ten_chude", ""),
                "score": score
            }
            
            if score >= 0.6:
                context_1.append(result)
            elif score >= 0.1:
                context_2.append(result)
        
        if len(context_1) > 0:
            context_1 = sorted(context_1, key=lambda x: x["score"], reverse=True)
            context_1 = context_1[:3]
            return context_1, True
        elif len(context_2) > 0:
            context_2 = sorted(context_2, key=lambda x: x["score"], reverse=True)
            context_2 = context_2[:3]
            return context_2, False
        else:
            return "Không có thông tin liên quan nào được đề cập.", False

    def close(self):
        if self.client and self.client.is_connected():
            self.client.close()

# retriever = Retriever(model2, "non_chunk_data2")
# query = "Điều 35 Nghị định số 105/2021/NĐ-CP có nội dung gì?"
# result = retriever(query)
# if result[1]:
#     print("Prioritize!")
# else:
#     print("No Prioritize!")
# print(result[0])
# retriever.close()