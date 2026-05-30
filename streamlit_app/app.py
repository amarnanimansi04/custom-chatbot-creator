import streamlit as st
import requests

# ── Config ──────────────────────────────────────────────
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Custom Chatbot Creator", page_icon="🤖")

# ── Session state (keeps login alive while app is open) ──
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# ── If already logged in, go to dashboard ───────────────
if st.session_state.token:
    st.switch_page("pages/dashboard.py")

# ── Login / Register UI ──────────────────────────────────
st.title("🤖 Custom Chatbot Creator")
st.subheader("Login or Register to continue")

tab1, tab2 = st.tabs(["Login", "Register"])

# LOGIN TAB
with tab1:
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        res = requests.post(f"{API_URL}/api/login", json={
            "email": email,
            "password": password
        })
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.session_state.user_email = email
            st.success("Logged in!")
            st.switch_page("pages/dashboard.py")
        else:
            st.error("Invalid email or password")

# REGISTER TAB
with tab2:
    reg_email = st.text_input("Email", key="reg_email")
    reg_password = st.text_input("Password", type="password", key="reg_password")

    if st.button("Register"):
        res = requests.post(f"{API_URL}/api/register", json={
            "email": reg_email,
            "password": reg_password
        })
        if res.status_code == 200:
            st.success("Account created! Please login.")
        else:
            try:
                st.error(f"Error: {res.json().get('detail', 'Something went wrong')}")
            except Exception:
                st.error(f"Error {res.status_code}: {res.text or 'No response from server'}")