import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8001"

if not st.session_state.get("token"):
    st.switch_page("app.py")

token = st.session_state.token
headers = {"Authorization": f"Bearer {token}"}

def get_chatbots():
    res = requests.get(f"{API_URL}/api/chatbots", headers=headers)
    if res.status_code == 200:
        return res.json()
    return []

def delete_chatbot(bot_id):
    res = requests.delete(f"{API_URL}/api/chatbots/{bot_id}", headers=headers)
    return res.status_code == 200

col1, col2 = st.columns([4, 1])
with col1:
    st.title("📊 My Chatbots")
with col2:
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.user_email = None
        st.switch_page("app.py")

st.divider()

with st.expander("➕ Create New Chatbot"):
    name = st.text_input("Chatbot Name", placeholder="e.g. Support Bot")
    url  = st.text_input("Website URL",  placeholder="https://yoursite.com")

    if st.button("Create & Start Scraping", disabled=st.session_state.get("creating", False)):
        st.session_state.creating = True
        if not name or not url:
            st.warning("Please fill in both fields.")
        else:
            res = requests.post(f"{API_URL}/api/chatbots",
                headers=headers,
                json={"name": name, "website_url": url}
            )
            if res.status_code == 200:
                st.success("Chatbot created! Scraping started...")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Error: {res.json().get('detail', 'Something went wrong')}")

st.divider()

chatbots = get_chatbots()

if not chatbots:
    st.info("No chatbots yet. Create one above!")
else:
    for bot in chatbots:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            st.subheader(bot["name"])
            st.caption(bot["website_url"])

        with col2:
            status = bot["scrape_status"]
            if status == "done":
                st.success(status)
            elif status == "processing":
                st.warning(status)
            elif status == "failed":
                st.error(status)
            else:
                st.info(status)

        with col3:
            if st.button("💬 Chat", key=f"chat_{bot['id']}"):
                st.session_state.selected_bot = bot
                st.switch_page("pages/chat.py")
            if st.button("⚙️ Config", key=f"config_{bot['id']}"):
                st.session_state.selected_bot = bot
                st.switch_page("pages/config.py")

        with col4:
            if not st.session_state.get(f"confirm_delete_{bot['id']}"):
                if st.button("🗑️ Delete", key=f"delete_{bot['id']}"):
                    st.session_state[f"confirm_delete_{bot['id']}"] = True
                    st.rerun()

        if st.session_state.get(f"confirm_delete_{bot['id']}"):
            c1, c2, c3 = st.columns([4, 1, 1])
            with c1:
                st.warning("Are you sure you want to delete this chatbot?")
            with c2:
                if st.button("Yes", key=f"yes_{bot['id']}"):
                    if delete_chatbot(bot["id"]):
                        st.session_state[f"confirm_delete_{bot['id']}"] = False
                        st.rerun()
                    else:
                        st.toast("Failed to delete.", icon="❌")
            with c3:
                if st.button(" No", key=f"no_{bot['id']}"):
                    st.session_state[f"confirm_delete_{bot['id']}"] = False
                    st.rerun()

        st.divider()

statuses = [b["scrape_status"] for b in chatbots]
if "processing" in statuses or "pending" in statuses:
    st.caption("⏳ Scraping in progress — auto refreshing every 3 seconds...")
    time.sleep(3)
    st.rerun()