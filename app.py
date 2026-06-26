import streamlit as st
from chat import chat, upload_pdf
import uuid
from utils import format_sources
import time
st.set_page_config(

    page_title="DocFlow AI",

    page_icon="🤖",

    layout="wide"

)

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages=[]

st.title("🤖DocFlow AI")
with st.sidebar:
    st.header("Settings")
    uploaded_pdf = st.file_uploader("Upload PDF",type="pdf")
    st.divider()
    if st.button("🗑 Clear Chat"):
        st.session_state.messages=[]
        st.rerun()
    if uploaded_pdf:
        if st.session_state.get("last_uploaded") != uploaded_pdf.name:
            with st.spinner("Indexing PDF..."):
                success, message = upload_pdf(uploaded_pdf)
            if success:
                st.session_state.last_uploaded = uploaded_pdf.name
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f" **System:** Successfully indexed `{uploaded_pdf.name}` ({message} chunks)."
                })
                st.toast(f" Indexed {message} chunks successfully!")
                st.rerun()
            else:
                st.error(message)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt=st.chat_input("Ask me anything...")

if prompt:
    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        }
    )
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            start = time.time()
            placeholder = st.empty()

            result = chat(prompt,thread_id=st.session_state.thread_id)
            answer=result["answer"]
            sources=result["sources"]
            
            for i in range(0, len(answer), 4):
                placeholder.markdown(answer[:i+4] + "▌")
                time.sleep(0.01)
            placeholder.markdown(answer)
            if sources:
                st.divider()
                st.caption("📚 Sources")
                st.code(format_sources(sources))
    st.session_state.messages.append(

        {

            "role":"assistant",

            "content":answer

        }

    )