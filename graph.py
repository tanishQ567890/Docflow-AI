from langgraph.graph import StateGraph
from langgraph.graph import START
from langgraph.prebuilt import tools_condition
from state import AgentState
from router import route_question
from node import chatbot
from node import retrieve
from node import tool_node
from memory import memory
# Routing function (must be defined before use)
def decide_next_node(state):

    route = state["route"]

    if route == "RAG":
        return "retrieve"

    elif route == "TOOL":
        return "chatbot"

    elif route == "WEB":
        return "chatbot"

    elif route == "CODE":
        return "chatbot"

    else:
        return "chatbot"

# Build graph
builder = StateGraph(AgentState)
builder.add_node("router", route_question)
builder.add_node("retrieve", retrieve)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", tool_node)

builder.add_edge(START, "router")

builder.add_conditional_edges("router", decide_next_node)

builder.add_edge("retrieve", "chatbot")

builder.add_conditional_edges("chatbot", tools_condition)

builder.add_edge("tools", "chatbot")

graph = builder.compile(checkpointer=memory)
