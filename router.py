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
WEB
CODE
DIRECT

Rules:

Return TOOL if the user is asking for:
- calculations
- current time
- date
- mathematical expressions
- summarizing a PDF
- explaining diagrams or figures in a PDF

Return RAG if the answer should come from the uploaded PDF
(e.g., explain a chapter, find information in the document).

Return WEB if user asks about:
- latest news or today's news
- recent events
- search online / internet
- latest version or release
- weather
- stock market or cryptocurrency
- sports scores
- current affairs
- recent AI models

Return CODE if user asks to:
- write code or generate code
- explain code
- debug code
- optimize code
- convert code between languages
- programming questions
- algorithm or DSA problems
- SQL queries
- build something with Flask, React, Django, etc.
- anything involving Python, Java, C++, JavaScript, etc.

Return DIRECT if the question is general knowledge or conversation.

Only return one word.

Examples:

User: What is 25 * 4?
TOOL

User: Summarize the PDF
TOOL

User: Explain the diagram in the PDF
TOOL

User: What is Chapter 3 about?
RAG

User: Latest LangGraph version
WEB

User: Current Bitcoin price
WEB

User: Today's IPL points table
WEB

User: Write BFS in C++
CODE

User: Optimize this SQL query
CODE

User: Explain this Python code
CODE

User: Write REST API in Flask
CODE

User: What is machine learning?
DIRECT

User: Hello
DIRECT
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
    if route not in ["RAG", "TOOL", "WEB", "CODE", "DIRECT"]:
        route = "DIRECT"

    return {

        "question": question,

        "route": route

    }