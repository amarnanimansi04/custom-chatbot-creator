# 🤖 Custom Chatbot Creator

> Turn any website into a smart, embeddable AI chatbot in minutes.

Custom Chatbot Creator is a full-stack SaaS platform where businesses paste a URL and get a fully trained AI chatbot that understands their website content — ready to embed on any webpage with a single script tag.

---

## 🎯 What It Does

1. **Paste a URL** → the platform scrapes the entire website automatically
2. **AI trains on the content** → chunks, embeds, and stores in a vector database
3. **Ask anything** → the chatbot answers questions using only that website's content
4. **Embed anywhere** → one script tag, any website, instant chatbot

---

## ✨ Features

- 🌐 **Intelligent Web Scraping** — crawls the given URL and all linked pages on the same domain (up to 10 pages)
- 🧠 **Custom RAG Pipeline** — built from scratch without LangChain: chunking, embedding, vector search, and LLM chaining all custom implemented
- ⚡ **Async Processing** — scraping and embedding runs in the background via Celery + Upstash Redis
- 💬 **Embeddable Widget** — lightweight vanilla JS chat bubble, paste one script tag into any website
- 🎨 **Customizable** — businesses set their own welcome message and brand color
- 📊 **Multi-chatbot Dashboard** — manage multiple chatbots, each trained on a different website
- 🔐 **JWT Authentication** — secure login and registration

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend API | FastAPI (Python) | REST API, auth, business logic |
| Task Queue | Celery + Upstash Redis | Async background scraping and embedding |
| Vector Database | ChromaDB | Storing and querying embeddings |
| LLM | Groq (LLaMA 3.1 8B Instant) | Generating answers |
| Embeddings | HuggingFace (sentence-transformers) | Converting text to vectors |
| Database | Supabase (PostgreSQL) | Users, chatbots, messages |
| Frontend | Streamlit | Dashboard and chat UI |
| Widget | Vanilla JavaScript | Embeddable chat bubble |

---

## 🏗️ Architecture

1. User pastes URL → FastAPI saves chatbot to Supabase
2. Celery worker picks up task asynchronously via Upstash Redis
3. WebScraper crawls URL and all linked pages on same domain
4. TextChunker splits content into overlapping chunks
5. HuggingFace Embedder converts chunks to vectors
6. ChromaDB stores vectors with metadata
7. Status updated to "done" in Supabase
8. User asks a question → question gets embedded
9. ChromaDB queried → top 5 most relevant chunks retrieved
10. Groq LLaMA 3.1 generates a grounded answer from chunks
11. Answer returned to user via dashboard or embedded widget

---

## 📁 Project Structure

    custom-chatbot-creator/
    ├── backend/
    │   ├── rag/
    │   │   ├── scraper.py        # Multi-page web scraper with session handling
    │   │   ├── chunker.py        # Text chunking with overlap
    │   │   ├── embedder.py       # HuggingFace sentence-transformers
    │   │   ├── vectorstore.py    # ChromaDB operations
    │   │   └── chain.py          # Custom RAG chain with Groq LLM
    │   ├── routes/
    │   │   ├── auth.py           # Login, register, JWT tokens
    │   │   ├── chatbots.py       # CRUD for chatbots
    │   │   ├── chat.py           # Chat endpoint
    │   │   └── analytics.py      # Usage analytics
    │   ├── tasks/
    │   │   └── scrape_task.py    # Celery background task
    │   ├── main.py               # FastAPI app entry point
    │   ├── models.py             # SQLAlchemy database models
    │   ├── database.py           # Supabase PostgreSQL connection
    │   └── celery_app.py         # Celery + Upstash Redis config
    ├── streamlit_app/
    │   ├── app.py                # Login / Register page
    │   └── pages/
    │       ├── dashboard.py      # Chatbot management dashboard
    │       ├── chat.py           # Chat interface with history
    │       └── config.py         # Widget customization + embed code
    ├── widget/
    │   └── widget.js             # Embeddable vanilla JS chat widget
    ├── test.html                 # Local widget testing page
    ├── .gitignore
    └── README.md

---

## ⚙️ Environment Variables

Create a `.env` file inside `backend/`:

    DATABASE_URL=your_supabase_postgresql_connection_string
    UPSTASH_REDIS_REST_URL=your_upstash_redis_url
    UPSTASH_REDIS_REST_TOKEN=your_upstash_redis_token
    GROQ_API_KEY=your_groq_api_key
    SECRET_KEY=your_jwt_secret_key

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Supabase account
- Groq API key (free at console.groq.com)
- Upstash Redis account (free at upstash.com)

### 1. Clone the repo

    git clone https://github.com/amarnanimansi04/custom-chatbot-creator.git
    cd custom-chatbot-creator

### 2. Set up backend

    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

### 3. Add your .env file inside backend/

    DATABASE_URL=...
    UPSTASH_REDIS_REST_URL=...
    UPSTASH_REDIS_REST_TOKEN=...
    GROQ_API_KEY=...
    SECRET_KEY=...

### 4. Run all 3 services

**Terminal 1 — Backend:**

    cd backend && source venv/bin/activate && uvicorn main:app --reload

**Terminal 2 — Celery Worker:**

    cd backend && source venv/bin/activate && celery -A celery_app worker --loglevel=info --pool=solo

**Terminal 3 — Streamlit:**

    cd streamlit_app && source ../backend/venv/bin/activate && streamlit run app.py

Visit http://localhost:8501 in your browser.

---

## 🔌 Embedding the Widget

After creating a chatbot, go to the Config page and copy your embed code:

    <script
      src="https://your-cdn.com/widget.js"
      data-chatbot-id="your-chatbot-id"
      data-color="#007bff"
      data-welcome="Hi! How can I help you?"
      data-api-url="https://your-backend.railway.app">
    </script>

Paste into any website's HTML — a floating chat bubble appears instantly.

---

## 👩‍💻 About

Built by **Mansi Amarnani** — exploring full-stack AI application development through custom RAG pipelines, async task queues, vector databases, and embeddable widgets.

---

## 📄 License

MIT License