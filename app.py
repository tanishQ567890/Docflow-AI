import streamlit as st
from html import escape
import os
import uuid
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from utils import format_sources
import time

load_dotenv(Path(__file__).resolve().parent / ".env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    from chat import chat, upload_pdf

st.set_page_config(
    page_title="DocFlow AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --ink: #202332;
        --muted: #74798b;
        --violet: #7568d9;
        --line: #e9e9f1;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 78% 0%, rgba(222, 217, 255, .42), transparent 34rem),
            #f7f7fb;
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1040px;
        padding: 2rem 2.5rem 5rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(255, 255, 255, .07);
        background: #171823;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #b5b7c6;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f5f4fb;
        font-family: 'Manrope', sans-serif;
        letter-spacing: -.035em;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        border: 1px dashed rgba(197, 187, 255, .38);
        border-radius: 14px;
        background: rgba(255, 255, 255, .035);
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] section:hover {
        border-color: #a99bf4;
        background: rgba(255, 255, 255, .06);
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        border: 1px solid rgba(197, 187, 255, .35);
        border-radius: 8px;
        background: rgba(141, 124, 231, .15);
        color: #eeeaff;
    }

    [data-testid="stSidebar"] .stButton > button {
        min-height: 42px;
        border: 1px solid rgba(255, 255, 255, .11);
        border-radius: 10px;
        background: rgba(255, 255, 255, .055);
        color: #e7e6ef;
        font-weight: 600;
        transition: background .18s ease, border-color .18s ease;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: rgba(197, 187, 255, .4);
        background: rgba(141, 124, 231, .17);
        color: #fff;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: .35rem 0 1.7rem;
    }

    .brand-mark {
        display: grid;
        width: 42px;
        height: 42px;
        place-items: center;
        border: 1px solid rgba(191, 179, 255, .26);
        border-radius: 13px;
        background: linear-gradient(145deg, #8573e8, #554e9f);
        box-shadow: 0 8px 24px rgba(96, 78, 195, .3);
        color: white;
        font-size: 20px;
    }

    .brand-name {
        margin: 0;
        color: #f5f4fb;
        font: 800 17px 'Manrope', sans-serif;
        letter-spacing: -.045em;
    }

    .brand-caption {
        margin: 3px 0 0;
        color: #8f91a2;
        font-size: 11px;
    }

    .sidebar-label {
        margin: 1rem 0 .45rem;
        color: #f0eff8;
        font: 700 12px 'Manrope', sans-serif;
        letter-spacing: .02em;
    }

    .sidebar-hint {
        margin: -.25rem 0 .85rem;
        color: #8f91a2;
        font-size: 11px;
        line-height: 1.6;
    }

    .document-card {
        margin: .85rem 0 1rem;
        padding: 12px;
        border: 1px solid rgba(130, 221, 196, .2);
        border-radius: 11px;
        background: rgba(93, 185, 155, .08);
        color: #c9f1e4;
        font-size: 12px;
        line-height: 1.55;
        overflow-wrap: anywhere;
    }

    .document-card strong {
        display: block;
        margin-bottom: 3px;
        color: #ecfff8;
        font-size: 11px;
    }

    .main-heading {
        margin: .15rem 0 .3rem;
        color: #222435;
        font: 800 clamp(30px, 4vw, 42px)/1.15 'Manrope', sans-serif;
        letter-spacing: -.065em;
    }

    .main-subheading {
        margin: 0;
        color: #777b8d;
        font-size: 14px;
        line-height: 1.65;
    }

    .topline {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 9px;
        color: #7368c9;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
    }

    .topline-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #65b99e;
        box-shadow: 0 0 0 3px rgba(101, 185, 158, .14);
    }

    .welcome-card {
        margin: 2rem 0 1rem;
        padding: clamp(22px, 4vw, 38px);
        border: 1px solid #e8e6f4;
        border-radius: 20px;
        background: rgba(255, 255, 255, .82);
        box-shadow: 0 16px 50px rgba(49, 43, 92, .055);
    }

    .welcome-icon {
        display: grid;
        width: 48px;
        height: 48px;
        margin-bottom: 16px;
        place-items: center;
        border: 1px solid #e7e1ff;
        border-radius: 15px;
        background: #f2efff;
        color: #7568d9;
        font-size: 23px;
    }

    .welcome-card h2 {
        margin: 0;
        color: #242638;
        font: 700 clamp(22px, 3vw, 28px)/1.25 'Manrope', sans-serif;
        letter-spacing: -.045em;
    }

    .welcome-card p {
        max-width: 600px;
        margin: 9px 0 0;
        color: #777b8d;
        font-size: 13px;
        line-height: 1.7;
    }

    [data-testid="stChatMessage"] {
        margin: .8rem 0;
        padding: 1.1rem 1.25rem;
        border: 1px solid #e9e9f1;
        border-radius: 16px;
        background: rgba(255, 255, 255, .86);
        box-shadow: 0 7px 20px rgba(40, 39, 65, .035);
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        color: #303244;
        font-size: 14px;
        line-height: 1.75;
    }

    [data-testid="stChatInput"] {
        border: 1px solid #e2e1eb;
        border-radius: 15px;
        background: white;
        box-shadow: 0 9px 30px rgba(46, 42, 76, .075);
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #9d91e5;
        box-shadow: 0 0 0 3px rgba(117, 104, 217, .1), 0 9px 30px rgba(46, 42, 76, .075);
    }

    [data-testid="stChatInput"] textarea {
        color: #292b3d;
        font-size: 14px;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #999bad;
    }

    .source-heading {
        margin: .4rem 0 .45rem;
        color: #7368c9;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .06em;
        text-transform: uppercase;
    }

    div[data-testid="stButton"] > button[kind="secondary"] {
        border: 1px solid #e6e4ef;
        border-radius: 12px;
        background: rgba(255, 255, 255, .78);
        color: #46485b;
        font-size: 12px;
        text-align: left;
        transition: transform .16s ease, border-color .16s ease, background .16s ease;
    }

    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        transform: translateY(-2px);
        border-color: #c7bef4;
        background: white;
        color: #5c50b6;
    }

    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] {
            padding: 1.4rem 1rem 5rem;
        }

        [data-testid="stChatMessage"] {
            padding: .9rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
            <div class="brand-mark">✳</div>
            <div>
                <p class="brand-name">DocFlow AI</p>
                <p class="brand-caption">Your document intelligence studio</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "docx", "txt", "csv", "pptx"]
    )
    if uploaded_file and st.session_state.get("last_uploaded") == hashlib.sha256(uploaded_file.getvalue()).hexdigest():
        st.markdown(
            f'<div class="document-card"><strong>✓ Document ready</strong>{escape(uploaded_file.name)}<br>'
            f'{st.session_state.get("indexed_chunks", 0)} searchable chunks</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p class="sidebar-hint">PDF · DOCX · TXT · CSV · PPTX</p>',
        unsafe_allow_html=True,
    )
    if st.button("＋  Start a new conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    if uploaded_file and GOOGLE_API_KEY:
        upload_hash = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
        if st.session_state.get("last_uploaded") != upload_hash:
            with st.spinner("Indexing document..."):
                success, message = upload_pdf(uploaded_file)
            if success:
                st.session_state.last_uploaded = upload_hash
                st.session_state.indexed_chunks = message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Your document is ready with {message} searchable chunks. Ask me anything about it."
                })
                st.toast(f"Indexed {message} chunks successfully!")
                st.rerun()
            else:
                st.error(message)
    elif uploaded_file:
        st.warning("Document indexing is unavailable right now.")

st.markdown(
    """
    <h1 class="main-heading">Ask your documents<br>better questions.</h1>
    <p class="main-subheading">A calmer, smarter way to find the details that matter in your files.</p>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-card">
            <div class="welcome-icon">✧</div>
            <h2>Your next insight starts here.</h2>
            <p>Upload a document in the sidebar, then ask a question in plain language.
            DocFlow can also help with general questions, calculations, and more.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    suggestions = [
        "Summarize the key points",
        "What are the main takeaways?",
        "Find important dates or figures",
    ]
    suggestion_columns = st.columns(len(suggestions))
    for column, suggestion in zip(suggestion_columns, suggestions):
        if column.button(suggestion, use_container_width=True, disabled=not GOOGLE_API_KEY):
            st.session_state.suggested_prompt = suggestion
            st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"📚 Sources · {len(set(format_sources(message['sources']).splitlines()))}"):
                st.markdown('<p class="source-heading">Document references</p>', unsafe_allow_html=True)
                for source in format_sources(message["sources"]).splitlines():
                    st.caption(f"↳ {source}")

prompt = st.chat_input("Ask a question or explore a document...")
if st.session_state.get("suggested_prompt"):
    prompt = st.session_state.pop("suggested_prompt")

if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    with st.chat_message("user"):
        st.markdown(prompt)
    if GOOGLE_API_KEY:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                placeholder = st.empty()

                result = chat(prompt, thread_id=st.session_state.thread_id)
                answer = result.get("answer") or "Sorry, I encountered an error. Please try again."
                sources = result.get("sources", [])

                for i in range(0, len(answer), 4):
                    placeholder.markdown(answer[:i+4] + "▌")
                    time.sleep(0.01)
                placeholder.markdown(answer)
    else:
        answer = "The assistant is temporarily unavailable. Please try again later."
        sources = []
        with st.chat_message("assistant"):
            st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )