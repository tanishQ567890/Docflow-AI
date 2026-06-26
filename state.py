from typing import Annotated, Literal
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.documents import Document


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

    question: str

    route: Literal["RAG", "TOOL", "DIRECT"]

    context: str

    retrieved_docs: list[Document]

    tool_output: str