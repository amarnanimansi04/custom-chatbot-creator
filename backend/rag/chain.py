import os
import time
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

        return f"""You are a helpful assistant for a business website. Answer questions using ONLY the context below.

Rules:
- Always look carefully through ALL context sources for specific facts (phone numbers, emails, prices, dates, names)
- If you find a phone number, email, address or any contact detail in the context, always include it exactly as written
- Use bullet points when listing multiple items
- If context has partial info, share what you found and be honest about gaps
- Never make up information — only use what's in the context
- Be friendly and concise

CONTEXT:
{context}

QUESTION: {question}

ANSWER (use specific details from the context above):"""

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
            "max_tokens": 600
        }

        response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)

        if response.status_code == 429:
            return {
                "answer": "I'm receiving too many requests right now. Please wait a few seconds and try again.",
                "sources": [],
                "chunks_used": 0
            }

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