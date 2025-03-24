from typing import List
import numpy as np
from .route_sample import chatSamples, lawSamples
from chatbot_v1.src.embedding.load_embedding_model import model1, model2

class Route():
    def __init__(self, name, samples:List = []):
        self.name = name
        self.samples = samples

# Class Router để phân loại ngữ nghĩa
class SemanticRouter():
    def __init__(self, embedding, routes, k=5):
        self.routes = routes
        self.embedding = embedding
        self.routesEmbedding = {}

        for route in self.routes:
            self.routesEmbedding[route.name] = self.embedding.encode(route.samples)

    def get_routes(self):
        return self.routes

    def guide(self, query):
        queryEmbedding = self.embedding.encode([query])

        queryEmbedding = queryEmbedding / np.linalg.norm(queryEmbedding)
        scores = []

        # Calculate the cosine similarity of the query embedding with the sample embeddings of the router.
        for route in self.routes:
            routesEmbedding = self.routesEmbedding[route.name] / np.linalg.norm(self.routesEmbedding[route.name])
            score = np.mean(np.dot(routesEmbedding, queryEmbedding.T).flatten())
            scores.append((score, route.name))

        scores.sort(reverse=True)
        top_5 = scores[:5]

        route_counts = {}
        for _, route_name in top_5:
            route_counts[route_name] = route_counts.get(route_name, 0) + 1

        selected_route = max(route_counts.items(), key=lambda x: x[1])[0]
        return selected_route

chatRoute = Route("chat", chatSamples)
lawRoute = Route("law", lawSamples)

sRoute = SemanticRouter(embedding=model2, routes=[chatRoute, lawRoute])

# while True:
#     query = input("YOU: ")
#     print(sRoute.guide(query))