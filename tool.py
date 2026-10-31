from langchain_core.tools import tool
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from rag import load_pdf
from vision import extract_images
from tavily import TavilyClient
from config import MODEL_NAME, TAVILY_API_KEY
import base64
import ast
import operator

llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.3)
@tool
def current_time():
    """
    Returns current system time.
    """
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


@tool
def calculator(expression: str):

    """
    Evaluate a mathematical expression.
    """
    # Safe evaluator using AST — avoids the security risks of eval()
    _OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }

    def _safe_eval(node):
        if isinstance(node, ast.Constant):  # numbers
            return node.value
        elif isinstance(node, ast.BinOp):
            op = _OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(_safe_eval(node.left), _safe_eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op = _OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(_safe_eval(node.operand))
        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool
def summarize_pdf(summary_type: str = "short summary") -> str:
    """
    Summarizes the uploaded PDF.

    Examples:
    - short summary
    - 5 lines
    - 10 bullet points
    - executive summary
    - technical summary
    """
    try:
        docs = load_pdf()
    except FileNotFoundError:
        return "No document has been uploaded yet. Please upload a PDF or document first."
    except Exception as e:
        return f"Failed to load the document: {e}"

    document = "\n\n".join(
        doc.page_content for doc in docs
    )

    prompt = f"""
You are an expert document summarizer.

Below is the complete document.

{document}

Generate a:
{summary_type}

Make the summary concise, accurate and well formatted.
"""

    response = llm.invoke(prompt)

    return response.content

@tool
def explain_diagram(question: str) -> str:
    """
    Explains diagrams, figures, charts, graphs,
    architecture diagrams and flowcharts present
    in uploaded PDFs.
    """
    try:
        images = extract_images()
    except Exception as e:
        return f"Failed to extract images from the document: {e}"

    if len(images) == 0:
        return (
            "This PDF does not contain any embedded "
            "figures, diagrams, charts or images."
        )

    # Build multimodal content with all images
    content = []

    for img_path in images:
        with open(img_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Detect MIME type from extension
        ext = str(img_path).rsplit(".", 1)[-1].lower()
        mime_map = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/png")

        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{image_data}"}
        })

    prompt_text = f"""
You are an expert in understanding technical diagrams.

The uploaded images may contain:

• Software architecture
• Flowchart
• UML diagram
• Neural Network
• Research Paper Figure
• Graph
• Chart
• ER Diagram

User Question:

{question}

Instructions:

1. Explain every component.

2. Explain labels.

3. Explain arrows and connections.

4. Explain the overall workflow.

5. If it is a graph,
explain X-axis,
Y-axis,
trend,
and conclusion.

6. If it is an architecture,
describe every module.

7. Finally provide an overall summary.
"""

    content.append({"type": "text", "text": prompt_text})

    response = llm.invoke(
        [HumanMessage(content=content)]
    )

    return response.content

@tool
def web_search(query: str) -> str:
    """
    Search the internet for the latest information.
    """
    if not TAVILY_API_KEY:
        return "Web search is not configured. Set TAVILY_API_KEY in the project .env file."

    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    search_result = tavily.search(

        query=query,

        search_depth="advanced",

        max_results=5

    )

    results = ""

    for item in search_result["results"]:

        results += f"""
Title:
{item['title']}

Content:
{item['content']}

URL:
{item['url']}

-----------------------------------
"""

    prompt = f"""
You are an AI research assistant.

Answer the user's question using ONLY the web search results.

Question:

{query}

Search Results:

{results}

Instructions:

• Give a professional answer.

• Merge duplicate information.

• Mention important facts.

• Don't mention raw URLs unless necessary.

• If multiple sources disagree,
mention that.

• Keep answer concise.
"""

    response = llm.invoke(prompt)

    return response.content

@tool
def code_generator(request: str) -> str:
    """
    Generates, explains, debugs, or optimizes code
    based on the user's programming request.
    """
    prompt = f"""
You are an expert Senior Software Engineer.

User Request:

{request}

Follow these rules:

1. Understand the request.

2. If user asks for code,
generate complete code.

3. Explain every important step.

4. Mention Time Complexity.

5. Mention Space Complexity.

6. Mention Edge Cases.

7. Mention possible improvements.

8. Mention common mistakes.

9. Use Markdown.

10. If user asks to debug,

identify the issue,

fix it,

explain why.

11. If user asks optimization,

compare old vs new.

12. If DSA,

also explain intuition.

13. Never produce incomplete code.
"""
    response = llm.invoke(prompt)

    return response.content

TOOLS = [
    calculator,
    current_time,
    summarize_pdf,
    explain_diagram,
    web_search,
    code_generator
]