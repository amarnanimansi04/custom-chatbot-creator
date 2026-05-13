import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

if not st.session_state.get("token"):
    st.switch_page("app.py")
if not st.session_state.get("selected_bot"):
    st.switch_page("pages/dashboard.py")

bot = st.session_state.selected_bot
token = st.session_state.token
headers = {"Authorization": f"Bearer {token}"}

st.title(f"⚙️ Configure: {bot['name']}")
if st.button("← Back to Dashboard"):
    st.switch_page("pages/dashboard.py")

st.divider()

# ── Settings ──────────────────────────────────────────────
st.subheader("🎨 Customize")
welcome_msg = st.text_input("Welcome Message",
    value=bot.get("welcome_message") or "Hi! How can I help you?")
widget_color = st.color_picker("Widget Color",
    value=bot.get("widget_color") or "#007bff")

if st.button("💾 Save Settings"):
    res = requests.put(f"{API_URL}/api/chatbots/{bot['id']}",
        headers=headers,
        json={"welcome_message": welcome_msg, "widget_color": widget_color}
    )
    if res.status_code == 200:
        st.session_state.selected_bot = res.json()
        st.success("Saved!")
    else:
        st.error("Failed to save")

st.divider()

# ── Embed Code ────────────────────────────────────────────
st.subheader("📋 Your Embed Code")
st.write("Copy and paste this into any website's HTML:")

script_tag = f"""<script
  src="https://your-cdn.com/widget.js"
  data-chatbot-id="{bot['id']}"
  data-color="{widget_color}"
  data-welcome="{welcome_msg}">
</script>"""

st.code(script_tag, language="html")
st.info("After deployment, replace 'your-cdn.com' with your actual hosted URL")

st.divider()

# ── Quick Actions ─────────────────────────────────────────
st.subheader("🧪 Quick Actions")
if st.button("💬 Test Chat"):
    st.switch_page("pages/chat.py")