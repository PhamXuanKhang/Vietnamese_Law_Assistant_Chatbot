from typing import List
import numpy as np
from route_sample import chatSamples, lawSamples
from sentence_transformers import SentenceTransformer

class Route():
    def __init__(self, name, samples:List = []):
        self.name = name
        self.samples = samples

class SemanticRouter():
    def __init__(self, embedding, routes):
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
        return scores

chatRoute = Route("chat", chatSamples)
lawRoute = Route("law", lawSamples)

embedding_model = SentenceTransformer('dangvantuan/vietnamese-embedding')
sRoute = SemanticRouter(embedding=embedding_model, routes=[chatRoute, lawRoute])