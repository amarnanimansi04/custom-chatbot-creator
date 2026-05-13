from sentence_transformers import SentenceTransformer
from typing import List


class Embedder:
    # ✅ Removed singleton pattern — it's unsafe with Celery's process forking.
    #    Each worker process creates its own fresh instance after the fork.

    def __init__(self):
        print("⏳ Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Embedding model loaded!")

    def embed(self, text: str) -> List[float]:
        """Convert a single text to a vector"""
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_many(self, texts: List[str]) -> List[List[float]]:
        """Convert multiple texts to vectors efficiently (batch processing)"""
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=True
        ).tolist()