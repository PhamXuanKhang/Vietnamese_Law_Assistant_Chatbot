from sentence_transformers import SentenceTransformer

# load model vào cache folder
cache_dir = "./chatbot_v1/models"
model1 = SentenceTransformer('dangvantuan/vietnamese-embedding', cache_folder=cache_dir)
model2 = SentenceTransformer("AITeamVN/Vietnamese_Embedding", cache_folder=cache_dir)