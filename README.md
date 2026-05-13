---

## ⚙️ Environment Variables

Create a `.env` file inside `backend/`:

```env
DATABASE_URL=your_supabase_postgresql_connection_string
UPSTASH_REDIS_REST_URL=your_upstash_redis_url
UPSTASH_REDIS_REST_TOKEN=your_upstash_redis_token
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_jwt_secret_key
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Supabase account
- Groq API key (free at console.groq.com)
- Upstash Redis account (free at upstash.com)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/custom-chatbot-creator.git
cd custom-chatbot-creator
```

### 2. Set up backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add your `.env` file
```env
DATABASE_URL=...
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
GROQ_API_KEY=...
SECRET_KEY=...
```

### 4. Run all 3 services

**Terminal 1 — Backend:**
```bash
cd backend && source venv/bin/activate && uvicorn main:app --reload
```

**Terminal 2 — Celery Worker:**
```bash
cd backend && source venv/bin/activate && celery -A celery_app worker --loglevel=info --pool=solo
```

**Terminal 3 — Streamlit:**
```bash
cd streamlit_app && source ../backend/venv/bin/activate && streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

---

## 🔌 Embedding the Widget

After creating a chatbot, go to the **Config** page and copy your embed code:

```html
<script
  src="https://your-cdn.com/widget.js"
  data-chatbot-id="your-chatbot-id"
  data-color="#007bff"
  data-welcome="Hi! How can I help you?"
  data-api-url="https://your-backend.railway.app">
</script>
```

Paste into any website's HTML — a floating chat bubble appears instantly.

---

## 🗺️ Roadmap

- [ ] Deploy backend on Railway
- [ ] Deploy Streamlit on Streamlit Cloud
- [ ] Host widget.js on GitHub Pages / Cloudflare
- [ ] PDF and document upload support
- [ ] Analytics dashboard with charts
- [ ] Multi-language support

---

## 👩‍💻 About

Built by **Mansi** as an internship project exploring full-stack AI application development — custom RAG pipelines, async task queues, vector databases, and embeddable widgets.

---

## 📄 License

MIT License