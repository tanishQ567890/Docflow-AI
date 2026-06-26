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

    system_prompt = f"""

You are a helpful AI assistant.

Answer using the provided context.

If the answer is not in the context,

you may answer from your own knowledge.

Context:

{context}

"""

    messages = [

        SystemMessage(content=system_prompt)

    ] + state["messages"]

    response = llm_with_tools.invoke(messages)

    logger.info("LLM generated response.")

    return {

        "messages":[response]

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

    docs = retrieve_documents(question)

    logger.info(f"Retrieved {len(docs)} documents.")

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    return {
        "context": context,
        "retrieved_docs": docs
    }

tool_node = ToolNode(TOOLS)