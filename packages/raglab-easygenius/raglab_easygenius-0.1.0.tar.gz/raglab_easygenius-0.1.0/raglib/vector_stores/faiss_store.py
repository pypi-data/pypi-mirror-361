import numpy as np
import faiss

class FaissVectorStore:
    def __init__(self, dim=384):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)  # Cosine similarity
        self.texts = []
        self.embeddings = None

    def add_embeddings(self, texts, embeddings):
        # Normalize embeddings for cosine similarity
        embeddings = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings)
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
        self.index.add(embeddings)
        self.texts.extend(texts)

    def query(self, query_vector, top_k=5):
        query_vector = np.array(query_vector).astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_vector)
        D, I = self.index.search(query_vector, top_k)
        return [self.texts[i] for i in I[0] if i < len(self.texts)] 