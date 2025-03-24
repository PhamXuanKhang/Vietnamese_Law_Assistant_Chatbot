import numpy as np
from sentence_transformers import SentenceTransformer

def delete_old_embeddings(session):
    query = """
    MATCH (n)
    REMOVE n.embedding
    """
    session.run(query)
    print("Đã xóa tất cả các embedding trong db")

def get_entities_from_neo4j(session):
    query = "MATCH (n) RETURN n.ten AS ten, n.Value AS value, labels(n) AS labels"
    result = session.run(query)
    return [(record["ten"], record["value"], record["labels"]) for record in result]

def create_embeddings(texts, device):
    model = SentenceTransformer('keepitreal/vietnamese-sbert')
    model.to(device)
    embeddings = model.encode(texts, device=device)
    return embeddings

def save_embeddings_to_neo4j(session, entities, embeddings):
    for (entity_name, _, labels), embedding in zip(entities, embeddings):
        query = """
        MATCH (n) WHERE n.ten = $entity_name AND ANY(label IN labels(n) WHERE label IN $labels)
        SET n.embedding = $embedding
        """
        session.run(query, entity_name=entity_name, labels=labels, embedding=embedding.tolist())
    print("Đã lưu embedding vào db")