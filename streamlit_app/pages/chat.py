import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

# ── Guard ────────────────────────────────────────────────
if not st.session_state.get("token"):
    st.switch_page("app.py")

if not st.session_state.get("selected_bot"):
    st.switch_page("pages/dashboard.py")

bot = st.session_state.selected_bot
token = st.session_state.token
headers = {"Authorization": f"Bearer {token}"}
bot_id = bot["id"]

# ── Header ───────────────────────────────────────────────
st.title(f"💬 {bot['name']}")
st.caption(f"Trained on: {bot['website_url']}")

if st.button("← Back to Dashboard"):
    st.switch_page("pages/dashboard.py")

st.divider()

# ── Chat history per bot ─────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = {}

if bot_id not in st.session_state.messages:
    st.session_state.messages[bot_id] = []

# Show previous messages
for msg in st.session_state.messages[bot_id]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Chat input ───────────────────────────────────────────
if prompt := st.chat_input("Ask something about this website..."):

    st.session_state.messages[bot_id].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            res = requests.post(f"{API_URL}/api/chat",
                headers=headers,
                json={
                    "chatbot_id": bot_id,
                    "session_id": bot_id,
                    "message": prompt
                }
            )
            if res.status_code == 200:
                answer = res.json().get("answer", "No response")
            else:
                answer = f"Error: {res.text}"

        st.write(answer)
        st.session_state.messages[bot_id].append({"role": "assistant", "content": answer})