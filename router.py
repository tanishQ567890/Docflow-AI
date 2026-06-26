from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from config import MODEL_NAME
from logger import logger
router_llm = ChatGoogleGenerativeAI(model=MODEL_NAME,temperature=0)

ROUTER_PROMPT = """
You are a routing agent.

Your job is to classify the user's question.

Return ONLY one word.

RAG
TOOL
DIRECT

Rules:

Return TOOL if the user is asking for

- calculations
- current time
- date
- mathematical expressions

Return RAG if the answer should come from the uploaded PDF.

Return DIRECT if the question is general knowledge or conversation.

Only return one word.
"""

def extract_text(content):
    """Extract plain text from Gemini response content (handles both str and list of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") for block in content if isinstance(block, dict)
        )
    return str(content)

def route_question(state):

    question = state["messages"][-1].content
    if isinstance(question, list):
        question = extract_text(question)

    response = router_llm.invoke(

        [

            HumanMessage(

                content=ROUTER_PROMPT + "\n\nQuestion:\n" + question

            )

        ]

    )

    route = extract_text(response.content).strip().upper()
    logger.info(f"Route Selected : {route}")
    if route not in ["RAG", "TOOL", "DIRECT"]:
        route = "DIRECT"

    return {

        "question": question,

        "route": route

    }