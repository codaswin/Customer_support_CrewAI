import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
import crew  # noqa: E402  (after load_dotenv so the API key is set)
from tools import LOG_FILE  # noqa: E402

st.title("BrewHaven Support")
# Gap Log holds other customers' queries: admin-only, hidden unless ADMIN_PASSWORD is set and entered.
admin_pw = os.getenv("ADMIN_PASSWORD")
if admin_pw:
    with st.sidebar:
        st.header("Admin")
        if st.text_input("Admin password", type="password") == admin_pw:
            st.code(LOG_FILE.read_text() if LOG_FILE.exists() else "(empty)")

if "msgs" not in st.session_state:
    st.session_state.msgs = []
for role, text in st.session_state.msgs:
    st.chat_message(role).write(text)

if q := st.chat_input("Ask a question"):
    st.chat_message("user").write(q)
    with st.spinner("Thinking..."):
        text, source = crew.answer(q)
    text = f"{text}\n\n*Source: {source}*"
    st.chat_message("assistant").write(text)
    st.session_state.msgs += [("user", q), ("assistant", text)]
    if source != "Knowledge Base":
        st.rerun()  # refresh sidebar log
