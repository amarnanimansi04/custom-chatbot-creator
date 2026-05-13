import os
import requests
from typing import List
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

class RAGChain:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = "llama-3.1-8b-instant"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def build_prompt(self, question: str, chunks: List[dict]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks):
            source = chunk["metadata"].get("source_url", "")
            context_parts.append(f"[Source {i+1}] ({source}):\n{chunk['text']}")
        context = "\n\n".join(context_parts)

        return f"""You are a knowledgeable and conversational assistant trained on specific website content.

Your job is to answer questions in a helpful, detailed, and friendly way using the context provided below.

Guidelines:
- Give thorough, well-structured answers using the context
- Use bullet points or numbered lists when listing multiple things
- If the context has partial information, use it and say what you found
- Only say you don't know if the context has absolutely nothing relevant
- Never say "contact support" unless the context itself mentions it
- Be conversational and engaging, not robotic

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    def answer(self, question: str, chunks: List[dict], welcome_message: str = "") -> dict:
        if not chunks:
            return {
                "answer": "I couldn't find relevant information about that. Try rephrasing your question!",
                "sources": [],
                "chunks_used": 0
            }

        prompt = self.build_prompt(question, chunks)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 1024
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()

        answer_text = response.json()["choices"][0]["message"]["content"].strip()

        sources = list(set([
            chunk["metadata"].get("source_url", "")
            for chunk in chunks
            if chunk["metadata"].get("source_url")
        ]))

        return {
            "answer": answer_text,
            "sources": sources,
            "chunks_used": len(chunks)
        }