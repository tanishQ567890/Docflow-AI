#  DocFlow AI

**An Intelligent Knowledge Engine powered by LangGraph, Google Gemini, FAISS, and Streamlit.**

DocFlow AI is an agentic Retrieval-Augmented Generation (RAG) chatbot that reads your PDFs and answers questions about them — while also being smart enough to know when a question needs a tool (math, current time) or just general knowledge, instead of the document. It's built as a **stateful LangGraph agent** with conversational memory, dynamic routing, and a clean Streamlit chat UI.

---

##  Features

- ** PDF Knowledge Base** — Upload any PDF and it gets chunked, embedded, and indexed into a FAISS vector store in seconds.
- ** Smart Query Router** — An LLM-based router classifies every question as `RAG`, `TOOL`, or `DIRECT` and sends it down the right path of the graph.
- ** Retrieval-Augmented Generation** — Relevant chunks are retrieved from FAISS and injected into the LLM's context before answering.
- ** Built-in Tools** — The agent can call a calculator or fetch the current system time when the question calls for it, instead of hallucinating an answer.
- ** Persistent Conversation Memory** — Powered by LangGraph's `MemorySaver` checkpointer, so each chat thread remembers prior turns.
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

This design means DocFlow AI never blindly forces every question through the PDF — general chit-chat goes straight to the LLM, math/time questions get an actual tool call, and only document-related questions pay the cost of a vector search.

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | [LangGraph](https://www.langchain.com/langgraph) (stateful agent graph + memory checkpointing) |
| LLM | [Google Gemini](https://ai.google.dev/) (`gemini-2.5-flash`) via `langchain-google-genai` |
| Embeddings | Google `gemini-embedding-001` |
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
├── requirement.txt      # Minimal list of core dependencies
└── requirements.txt     # Full pinned environment dependency freeze
```

---

##  Getting Started

### Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com/) API key (for Gemini + embeddings)


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

## 📄 License

This project does not currently specify a license. Add a `LICENSE` file to clarify usage terms.
