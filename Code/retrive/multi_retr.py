import numpy as np
import torch
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase

class Retrive:
    def __init__(self, 
                 neo4j_uri="bolt://localhost:7687", 
                 neo4j_user="neo4j", 
                 neo4j_password="Maianhtruong1112@",
                 top_k=5,
                 lambda_val=0.5,
                 num_iterations=1,
                 device=None):
        self.device = device if device is not None else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Đang sử dụng device: {self.device}")
        
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        self.model = SentenceTransformer('keepitreal/vietnamese-sbert')
        self.model.to(self.device)
        
        self.top_k = top_k
        self.lambda_val = lambda_val
        self.num_iterations = num_iterations
        
        with self.driver.session() as session:
            self.entities = self.get_entities_from_neo4j(session)
        if not self.entities:
            print("Không tìm thấy entity nào có đủ embedding trong Neo4j.")
        else:
            print(f"Đã lấy được {len(self.entities)} entity từ Neo4j.")
        
        self.bm25_model = self.create_bm25_model(self.entities)
    
    def get_entities_from_neo4j(self, session):
        query = """
        MATCH (n)
        WHERE n.ten IS NOT NULL
          AND n.embedding IS NOT NULL AND n.graph_embedding IS NOT NULL
        RETURN n.ten AS name, n.Value AS value, n.embedding AS embedding, n.graph_embedding AS graph_embedding, n.Label AS label
        """
        result = session.run(query)
        entities = []
        for record in result:
            name = record["name"]
            value = record["value"]
            content_emb = record["embedding"]
            graph_emb = record["graph_embedding"]
            label = record["label"]
            if content_emb is not None and graph_emb is not None:
                entities.append({
                    "name": name,
                    "value": value,
                    "content_embedding": np.array(content_emb),
                    "graph_embedding": np.array(graph_emb),
                    "label": label
                })
        return entities

    def create_bm25_model(self, entities):
        texts = [f"{e['name']} {e['value']}" for e in entities]
        tokenized_texts = [text.split() for text in texts]
        return BM25Okapi(tokenized_texts)

    def create_embeddings(self, texts):
        embeddings = self.model.encode(texts, device=self.device)
        return embeddings

    def cosine_sim(self, vec1, vec2):
        eps = 1e-10
        return np.dot(vec1, vec2) / ((np.linalg.norm(vec1) * np.linalg.norm(vec2)) + eps)

    def normalize_scores(self, scores):
        scores = list(scores)
        if len(scores) == 0:
            return []
        min_s = min(scores)
        max_s = max(scores)
        if abs(max_s - min_s) < 1e-9:
            return [1.0] * len(scores)
        return [(s - min_s) / (max_s - min_s) for s in scores]

    def combined_search(self, bm25_query, vector_query):
        tokenized = bm25_query.split()
        bm25_scores = self.bm25_model.get_scores(tokenized)
        query_embedding = self.create_embeddings([vector_query])[0]
        cos_sims = [self.cosine_sim(query_embedding, e["content_embedding"]) for e in self.entities]

        bm25_norm = self.normalize_scores(bm25_scores)
        cosine_norm = self.normalize_scores([(sim + 1.0) / 2.0 for sim in cos_sims])
        
        results = []
        for i, e in enumerate(self.entities):
            combined_score = bm25_norm[i] + cosine_norm[i]
            item = {
                "name": e["name"],
                "value": e["value"],
                "label": e["label"],  
                "content_embedding": e["content_embedding"],
                "graph_embedding": e["graph_embedding"],
                "bm25": bm25_norm[i],
                "cosine": cosine_norm[i],
                "combined_score": combined_score
            }
            results.append(item)
        results.sort(key=lambda x: x["combined_score"], reverse=True)
        return results[:self.top_k]

    def iterative_rerank(self, candidates):
        if not candidates:
            return []
        for iteration in range(self.num_iterations):
            current_topk = candidates[:self.top_k]
            raw_graph_sums = []
            for c in candidates:
                gsum = 0.0
                for top_c in current_topk:
                    sim = self.cosine_sim(c["graph_embedding"], top_c["graph_embedding"])
                    sim_01 = (sim + 1.0) / 2.0
                    gsum += sim_01
                raw_graph_sums.append(gsum)
            norm_graph_sums = self.normalize_scores(raw_graph_sums)
            for i, c in enumerate(candidates):
                c["graph_sum"] = norm_graph_sums[i]
                c["final_score"] = c["combined_score"] + self.lambda_val * c["graph_sum"]
            candidates.sort(key=lambda x: x["final_score"], reverse=True)
        return candidates[:self.top_k]

    def advanced_retrieve(self, query_text, ner_entities):
        print(f"\nXử lý truy vấn: '{query_text}'")
        if not ner_entities:
            cands = self.combined_search(query_text, query_text)
            final_top = self.iterative_rerank(cands)
            return final_top

        all_candidates = {}
        for e in ner_entities:
            partial_top5 = self.combined_search(e, query_text)
            for item in partial_top5:
                key = item["name"]
                if key not in all_candidates or item["combined_score"] > all_candidates[key]["combined_score"]:
                    all_candidates[key] = item
        merged_candidates = list(all_candidates.values())
        final_top = self.iterative_rerank(merged_candidates)
        return final_top

def retrieve_entity(query_text, ner_entities=None):
    retriever = Retrive()
    results = retriever.advanced_retrieve(query_text, ner_entities)
    
    print(f"\nKết quả xếp hạng cuối cùng (Top {retriever.top_k}):")
    for idx, entity in enumerate(results, 1):
        print(f"{idx}. Node: {entity['name']} -- BM25 Score: {entity['bm25']:.4f}, "
              f"Cosine Score: {entity['cosine']:.4f}, Graph Sum: {entity['graph_sum']:.4f}, "
              f"Final Score: {entity['final_score']:.4f}")
    print('Nội dung truy vấn cuối cùng:')
    for idx, entity in enumerate(results, 1):
        print(f"{idx}. {entity['name']} - {entity['value']} (Label: {entity['label']}) - (Score: {entity['final_score']:.4f})")
    return results
