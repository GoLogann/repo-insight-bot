import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class DocumentRetriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve_relevant_documents(self, query_embedding, top_k=4):
        embeddings, documents = self.vector_store.get_all()

        embeddings = np.array(embeddings)
        query_embedding = np.array(query_embedding).reshape(1, -1)

        similarities = cosine_similarity(query_embedding, embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [documents[i] for i in top_indices]
