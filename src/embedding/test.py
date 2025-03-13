from sentence_transformers import SentenceTransformer
import weaviate
import weaviate.classes.query as wq
import json

# Kết nối Weaviate
client = weaviate.connect_to_local(
    host="localhost",
    port=8080
)

# Load mô hình SentenceTransformer
model = SentenceTransformer('dangvantuan/vietnamese-embedding')

# Hybrid search
query_text = "Thông tư này quy định chi tiết và hướng dẫn thi hành về nơi cư trú của công dân; đăng ký thường trú; đăng ký tạm trú; thông báo lưu trú; khai báo tạm vắng và trách nhiệm quản lý cư trú."
query_vector = model.encode(query_text).tolist()

# Truy vấn hybrid
collection = client.collections.get("Chunk")
response = collection.query.hybrid(
    query=query_text,
    vector=query_vector,
    alpha=0.5,
    return_properties=["noidung", "mapc", "chunk_index", "ten"],
    return_metadata=wq.MetadataQuery(score=True),
    limit=3
)

# In kết quả
for obj in response.objects:
    print(json.dumps(obj.properties, indent=2, ensure_ascii=False))
    print(f"Hybrid score: {obj.metadata.score:.3f}\n")

client.close()