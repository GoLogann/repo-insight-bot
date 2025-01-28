from typing import List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class DocumentRetriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve_relevant_documents(self, repo_url: str, query_embedding: List[float], top_k: int = 4):
        documents = self.vector_store.get_all(repo_url)

        embeddings = []
        texts = []

        for doc in documents:
            if doc.embedding:
                embeddings.append(doc.embedding)
                texts.append(doc.text)
            else:
                embeddings.append([0] * len(query_embedding))
                texts.append(doc.text)

        embeddings = np.array(embeddings)

        if embeddings.shape[1] == 0:
            raise ValueError("Embeddings have no features, cannot perform cosine similarity.")

        query_embedding = np.array(query_embedding).reshape(1, -1)
        similarities = cosine_similarity(query_embedding, embeddings)[0]

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [texts[i] for i in top_indices]

