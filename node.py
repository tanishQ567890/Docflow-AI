from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from tool import TOOLS
from config import MODEL_NAME
from rag import retrieve_documents
from langchain_core.messages import HumanMessage
from logger import logger
llm = ChatGoogleGenerativeAI(model=MODEL_NAME,temperature=0.3,streaming=True)
#Tool binding
llm_with_tools = llm.bind_tools(TOOLS)
# Chatbot node
def chatbot(state):

    context = state.get("context", "")
    route = state.get("route", "DIRECT")

    # Build route-specific system instructions
    if route == "RAG":
        system_prompt = f"""You are a helpful AI assistant that answers questions about uploaded documents.

The user has uploaded a document. Use the context below to answer their question accurately and in detail.
If the context doesn't contain enough information, say so clearly.

Document Context:
{context}
"""

    elif route == "TOOL":
        system_prompt = """You are a helpful AI assistant with access to tools.

You MUST use the appropriate tool to answer the user's question. Do NOT answer directly without calling a tool.

Available tools:
- calculator: for math expressions and calculations
- current_time: for current date and time
- summarize_pdf: to summarize the uploaded document (use for questions like "what is this file about", "summarize this", "give overview")
- explain_diagram: to explain charts, figures, diagrams in the PDF
- web_search: for real-time web information
- code_generator: for writing, debugging or explaining code

Always call the most relevant tool based on the user's request.
"""

    elif route == "WEB":
        system_prompt = """You are a helpful AI research assistant.

You MUST use the web_search tool to find current, up-to-date information for the user.
Do NOT answer from memory — always search the web first.
"""

    elif route == "CODE":
        system_prompt = """You are an expert software engineer assistant.

You MUST use the code_generator tool to handle the user's coding request.
The tool will generate, explain, debug or optimize code as needed.
"""

    else:  # DIRECT
        system_prompt = """You are a helpful, knowledgeable AI assistant.

Answer the user's question clearly and in detail using your own knowledge.
Be conversational, accurate and thorough.
"""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]

    response = llm_with_tools.invoke(messages)

    logger.info(f"LLM generated response for route: {route}")

    return {
        "messages": [response]
    }

def stream_response(messages):
    """
    Stream the final LLM response token by token.
    """

    for chunk in llm.stream(messages):
        yield chunk


def retrieve(state):

    if state.get("route") != "RAG":
        return {}

    question = state.get("question", "")
    if not question:
        # Fallback: extract from last message
        question = state["messages"][-1].content
        if isinstance(question, list):
            question = " ".join(
                block.get("text", "") for block in question if isinstance(block, dict)
            )

    try:
        docs = retrieve_documents(question)
        logger.info(f"Retrieved {len(docs)} documents.")
        context = "\n\n".join(doc.page_content for doc in docs)
        return {
            "context": context,
            "retrieved_docs": docs
        }
    except Exception as e:
        logger.warning(f"Retrieval failed (no index yet?): {e}")
        return {
            "context": "No document has been uploaded and indexed yet. Please upload a document first.",
            "retrieved_docs": []
        }

tool_node = ToolNode(TOOLS)