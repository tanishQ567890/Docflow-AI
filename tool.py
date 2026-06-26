from langchain_core.tools import tool
from datetime import datetime
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
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return str(e)

TOOLS = [
    calculator,
    current_time
]