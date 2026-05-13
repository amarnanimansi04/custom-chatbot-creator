from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        chunk_size    = max tokens per chunk (~500 words)
        chunk_overlap = how much chunks overlap (avoids cutting sentences)
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def chunk_text(self, text: str, metadata: dict = {}) -> List[dict]:
        """Split text into chunks and attach metadata to each"""
        if not text or len(text.strip()) < 50:
            return []

        chunks = self.splitter.split_text(text)

        # Attach metadata to every chunk (source URL, title etc.)
        return [
            {
                "text": chunk,
                "metadata": {**metadata, "chunk_index": i}
            }
            for i, chunk in enumerate(chunks)
            if len(chunk.strip()) > 20  # Skip tiny chunks
        ]

    def chunk_scraped_pages(self, pages: list) -> List[dict]:
        """Process multiple scraped pages into chunks"""
        all_chunks = []
        for page in pages:
            if not page.get("success") or not page.get("text"):
                continue
            metadata = {
                "source_url": page["url"],
                "page_title": page["title"]
            }
            chunks = self.chunk_text(page["text"], metadata)
            all_chunks.extend(chunks)
        return all_chunks