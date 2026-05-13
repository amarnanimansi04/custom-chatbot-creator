from rag.scraper import WebScraper
from rag.chunker import TextChunker
from rag.embedder import Embedder
from rag.vectorstore import VectorStore
from rag.chain import RAGChain

print("\n🧪 Testing RAG Pipeline...\n")

# Step 1 — Scrape
print("Step 1: Scraping URL...")
scraper = WebScraper()
result = scraper.scrape_url("https://en.wikipedia.org/wiki/Artificial_intelligence")
print(f"✅ Scraped: {result['title']}")
print(f"   Text length: {len(result['text'])} characters\n")

# Step 2 — Chunk
print("Step 2: Chunking text...")
chunker = TextChunker()
chunks = chunker.chunk_scraped_pages([result])
print(f"✅ Created {len(chunks)} chunks\n")

# Step 3 — Embed
print("Step 3: Embedding chunks...")
embedder = Embedder()
texts = [chunk["text"] for chunk in chunks]
embeddings = embedder.embed_many(texts)
print(f"✅ Created {len(embeddings)} embeddings\n")

# Step 4 — Store
print("Step 4: Storing in ChromaDB...")
vectorstore = VectorStore()
test_chatbot_id = "test-123"
vectorstore.delete_collection(test_chatbot_id)  # Clean slate
count = vectorstore.add_chunks(test_chatbot_id, chunks, embeddings)
print(f"✅ Stored {count} chunks in ChromaDB\n")

# Step 5 — Query + Answer
print("Step 5: Testing question answering...")
question = "What is artificial intelligence?"
question_embedding = embedder.embed(question)
relevant_chunks = vectorstore.query(test_chatbot_id, question_embedding, n_results=3)
print(f"✅ Found {len(relevant_chunks)} relevant chunks\n")

print("Step 6: Asking Groq LLM...")
chain = RAGChain()
response = chain.answer(question, relevant_chunks)
print(f"✅ Answer received!\n")
print(f"{'='*50}")
print(f"Q: {question}")
print(f"A: {response['answer']}")
print(f"Sources: {response['sources']}")
print(f"{'='*50}\n")

# Cleanup
vectorstore.delete_collection(test_chatbot_id)
print("🧹 Test collection cleaned up")
print("\n🎉 ALL PIPELINE STEPS PASSED!\n")