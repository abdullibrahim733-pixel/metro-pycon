"""12-line LangGraph warm-up: no API key required."""
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    request: str
    result: str


def inspect(state: State):
    return {"result": "I received: " + state["request"]}


graph = StateGraph(State)
graph.add_node("inspect", inspect)
graph.add_edge(START, "inspect")
graph.add_edge("inspect", END)
app = graph.compile()
print(app.invoke({"request": "Check a sample payment"}))
