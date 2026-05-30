from celery_app import celery_app
from rag.scraper import WebScraper
from rag.chunker import TextChunker
from rag.embedder import Embedder
from rag.vectorstore import VectorStore
from database import SessionLocal
import models

scraper = WebScraper(max_pages=500)  # no practical cap
chunker = TextChunker()
vectorstore = VectorStore()
# ✅ Removed top-level: embedder = Embedder()
#    Singleton + Celery forking = SIGSEGV. Instantiate inside the task instead.

@celery_app.task(bind=True, max_retries=3)
def process_url(self, chatbot_id: str, url: str):
    db = SessionLocal()
    embedder = Embedder()  # ✅ Create INSIDE the task, after fork
    try:
        chatbot = db.query(models.Chatbot).filter(
            models.Chatbot.id == chatbot_id
        ).first()
        if not chatbot:
            return {"status": "failed", "error": "Chatbot not found"}

        chatbot.scrape_status = "processing"
        db.commit()

        # ── Scrape entire site (follows links) ──
        # Seed with key business pages first
        from urllib.parse import urlparse
        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        seed_urls = [
            url,
            f"{base}/premium-packages",
            f"{base}/destinations",
            f"{base}/day-trips",
            f"{base}/visa",
            f"{base}/terms",
            f"{base}/about",
        ]
        pages = scraper.scrape_site(url, seed_urls=seed_urls)
        successful_pages = [p for p in pages if p["success"]]

        if not successful_pages:
            chatbot.scrape_status = "failed"
            db.commit()
            return {"status": "failed", "error": "Could not scrape URL"}

        # ── Chunk ──
        chunks = chunker.chunk_scraped_pages(successful_pages)
        if not chunks:
            chatbot.scrape_status = "failed"
            db.commit()
            return {"status": "failed", "error": "No content found"}

        # ── Embed ──
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedder.embed_many(texts)

        # ── Store ──
        vectorstore.delete_collection(chatbot_id)
        count = vectorstore.add_chunks(chatbot_id, chunks, embeddings)

        chatbot.scrape_status = "done"
        db.commit()

        return {
            "status": "done",
            "chunks_stored": count,
            "pages_scraped": len(successful_pages)
        }

    except Exception as e:
        try:
            chatbot = db.query(models.Chatbot).filter(
                models.Chatbot.id == chatbot_id
            ).first()
            if chatbot:
                chatbot.scrape_status = "failed"
                db.commit()
        except:
            pass
        raise self.retry(exc=e, countdown=5)
    finally:
        db.close()