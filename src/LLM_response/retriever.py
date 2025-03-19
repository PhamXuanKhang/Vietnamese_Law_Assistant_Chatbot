from sentence_transformers import SentenceTransformer
import weaviate
import weaviate.classes.query as wq

class Retriever:
    def __init__(self):
        self.model = SentenceTransformer('dangvantuan/vietnamese-embedding')
        self.client = weaviate.connect_to_local(host="localhost", port=8080)
        self.collection = self.client.collections.get("Chunk")

    def __call__(self, query):
        query_vector = self.model.encode(query).tolist()
        
        response = self.collection.query.hybrid(
            query=query,
            vector=query_vector,
            alpha=0.5,
            return_properties=["mapc", "vbqppl", "noidung", "vbqppl_link"],
            return_metadata=wq.MetadataQuery(score=True),
            limit=10
        )
        
        context_1 = []
        context_2 = []
        context = []
        
        for obj in response.objects:
            score = obj.metadata.score
            result = {
                "noidung": obj.properties.get("noidung", ""),
                "vbqppl": obj.properties.get("vbqppl", ""),
                "mapc": obj.properties.get("mapc", ""),
                "vbqppl_link": obj.properties.get("vbqppl_link", ""),
                "score": score
            }
            
            if score >= 0.8:
                context_1.append(result)
            elif score >= 0.5:
                context_2.append(result)
        
        if len(context_1) > 0:
            return context_1
        elif len(context_2) > 0:
            return context_2
        else:
            print('No relevant context')
            return None

    def close(self):
        if self.client and self.client.is_connected():
            self.client.close()

retriever = Retriever()
query = "Công dân được sử dụng CMND của mình làm giấy tờ tuỳ thân trong việc đi lại và thực hiện các giao dịch. Mọi công dân phải có trách nhiệm mang theo CMND và xuất trình khi người có thẩm quyền yêu cầu kiểm tra, kiểm soát."
result = retriever(query)
print(result)
retriever.close()