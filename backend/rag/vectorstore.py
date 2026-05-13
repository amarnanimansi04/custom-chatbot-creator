import chromadb
from chromadb.config import Settings
from typing import List
import os

class VectorStore:
    def __init__(self):
        # Persist to disk so data survives restarts
        persist_dir = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
        self.client = chromadb.PersistentClient(path=persist_dir)

    def get_or_create_collection(self, chatbot_id: str):
        """Each chatbot gets its own isolated collection"""
        return self.client.get_or_create_collection(
            name=f"chatbot_{chatbot_id}",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

    def add_chunks(self, chatbot_id: str, chunks: List[dict], embeddings: List[List[float]]):
        """Store chunks + their embeddings in ChromaDB"""
        collection = self.get_or_create_collection(chatbot_id)

        ids = [f"{chatbot_id}_chunk_{i}" for i in range(len(chunks))]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        # Add in batches of 100 to avoid memory issues
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            collection.add(
                ids=ids[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                documents=texts[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )

        return len(ids)

    def query(self, chatbot_id: str, question_embedding: List[float], n_results: int = 5) -> List[dict]:
        """Find the most relevant chunks for a question"""
        collection = self.get_or_create_collection(chatbot_id)

        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        # Format results cleanly
        chunks = []
        for i, doc in enumerate(results["documents"][0]):
            chunks.append({
                "text": doc,
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i]  # Convert distance to similarity score
            })

        return chunks

    def delete_collection(self, chatbot_id: str):
        """Delete all data for a chatbot (when user deletes it)"""
        try:
            self.client.delete_collection(f"chatbot_{chatbot_id}")
        except Exception:
            pass

    def collection_exists(self, chatbot_id: str) -> bool:
        """Check if a chatbot has been indexed"""
        try:
            collections = self.client.list_collections()
            return any(c.name == f"chatbot_{chatbot_id}" for c in collections)
        except Exception:
            return False