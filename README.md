<img width="1883" height="885" alt="Screenshot 2026-07-30 232620" src="https://github.com/user-attachments/assets/5b7b4971-c824-431a-b0b8-18d1a7c850be" />
#  DocFlow AI

**An Intelligent Knowledge Engine powered by LangGraph, Google Gemini, FAISS, and Streamlit.**

DocFlow AI is an agentic Retrieval-Augmented Generation (RAG) chatbot that reads your PDFs and answers questions about them — while also being smart enough to know when a question needs a tool (math, current time) or just general knowledge, instead of the document. It's built as a **stateful LangGraph agent** with conversational memory, dynamic routing, and a clean Streamlit chat UI.

---

##  Features

- **Document Knowledge Base** — Upload a PDF, DOCX, TXT, CSV, or PPTX file to chunk, embed, and index its contents in a FAISS vector store.
- **Smart Query Router** — An LLM-based router classifies questions as `RAG`, `TOOL`, `WEB`, `CODE`, or `DIRECT`.
- ** Retrieval-Augmented Generation** — Relevant chunks are retrieved from FAISS and injected into the LLM's context before answering.
- ** Built-in Tools** — The agent can call a calculator or fetch the current system time when the question calls for it, instead of hallucinating an answer.
- **Conversation Memory** — LangGraph's in-memory checkpointer keeps each chat thread's recent turns while the app is running.
- ** Source Citations** — Every RAG-backed answer shows which document/page the information came from.
- ** Streamlit Chat UI** — Upload a PDF, chat, clear history, and watch responses stream in, all from the browser.
- ** CLI Mode** — A simple terminal chat loop (`test_graph.py`) for quickly testing the graph without the UI.
- ** Logging** — All routing decisions, retrievals, and errors are logged to file for debugging.

---

##  Architecture

DocFlow AI's brain is a **LangGraph state machine**. Every incoming message flows through the graph below:


**How it works, step by step:**

1. **`router`** (`router.py`) — Sends the question to Gemini with a routing prompt and gets back one of `RAG`, `TOOL`, or `DIRECT`.
2. **`retrieve`** (`node.py` / `rag.py`) — If routed to `RAG`, the question is embedded and the top-k similar chunks are pulled from the FAISS index. These become the `context` for the next step.
3. **`chatbot`** (`node.py`) — The core LLM node. It receives the conversation history plus any retrieved context, and decides whether to answer directly or call a tool.
4. **`tools`** (`tool.py`) — If the chatbot's response requests a tool call (e.g. `calculator`, `current_time`), LangGraph's `ToolNode` executes it and routes the result back to `chatbot` for a final answer.
5. **Memory** (`memory.py`) — Every step is checkpointed against a `thread_id`, so the same conversation can be resumed with full history.

This design means DocFlow AI routes document questions through retrieval, math/time questions through tools, current-information questions through web search, coding questions through the code tool, and general conversation directly to the LLM.

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | [LangGraph](https://www.langchain.com/langgraph) (stateful agent graph + memory checkpointing) |
| LLM | [Google Gemini](https://ai.google.dev/) (`gemini-2.5-flash`) via `langchain-google-genai` |
| Embeddings | Google `gemini-embedding-2` |
| Vector Store | [FAISS](https://github.com/facebookresearch/faiss) (local, in-process similarity search) |
| Document Loading | `langchain-community` (`PyPDFLoader`) + `RecursiveCharacterTextSplitter` |
| Frontend | [Streamlit](https://streamlit.io/) |
| Tooling | LangChain `@tool` decorators (calculator, current time) |

---

##  Project Structure

```
Docflow-AI/
├── app.py              # Streamlit UI — chat window, PDF upload, sidebar controls
├── chat.py             # High-level chat/upload functions that wrap the LangGraph graph
├── config.py           # Loads env vars, model name, folder paths
├── graph.py            # Builds and compiles the LangGraph StateGraph
├── logger.py           # Logging setup (writes to Logs/agentic_rag.log)
├── memory.py           # MemorySaver checkpointer for conversation persistence
├── node.py             # Graph nodes: chatbot, retrieve, tool_node, stream_response
├── rag.py              # PDF loading, chunking, embedding, FAISS index build/query
├── router.py           # LLM-based query router (RAG / TOOL / DIRECT) + text helpers
├── state.py             # AgentState TypedDict — the shared graph state schema
├── test_graph.py        # CLI chat loop for testing the graph without Streamlit
├── tool.py              # Tool definitions (calculator, current_time)
├── utils.py             # Shared helpers (extract_text, format_sources)
└── requirements.txt     # Runtime dependencies
```

---

##  Getting Started

### Prerequisites

- Python 3.10 or newer
- A [Google AI Studio](https://aistudio.google.com/) API key for Gemini and embeddings
- A [Tavily API key](https://tavily.com/) only if you want to use web search

### Install

From the project directory, create a `.env` file:

```dotenv
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

`TAVILY_API_KEY` is optional. Without it, chat, document retrieval, and other tools still work; web search returns a configuration message.

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start the Streamlit app from the project directory:

```bash
streamlit run app.py
```

The project loads `.env` and stores uploads, the FAISS index, logs, and extracted images relative to the project directory, even when launched from another working directory.

### Notes

- Chat history is held in memory and is cleared when the app process restarts. The **Clear Chat** button starts a fresh conversation thread.
- The FAISS index represents the most recently indexed document. Uploading another document replaces the searchable index.
- A document must contain extractable text to be indexed. Image-only PDFs do not provide text for RAG.
---

##  Roadmap

- [ ] Support for multiple simultaneous PDFs with per-document filtering
- [ ] Swap FAISS for a persistent/managed vector DB (e.g. Chroma, Pinecone) for multi-user deployments
- [ ] Streamed token-by-token responses straight from the graph (currently simulated in the UI)
- [ ] Additional tools (web search, code execution)
- [ ] Dockerfile for one-command deployment

---

##  Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.
## Note:
The live demo may occasionally be unavailable because it relies on the Google Gemini API under the free-tier quota. If the API quota is exhausted or the API key has been disabled, the deployed application will not generate responses.
You can run the project locally by adding your own GOOGLE_API_KEY to a .env file and following the setup instructions.
##  License
Link: https://docflow-ai-1-xuoc.onrender.com
