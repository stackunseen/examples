from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph


class State(TypedDict):
    question: str
    context: list[str]
    answer: str
    next: Literal["retrieve", "answer", "done"]


def supervisor(state: State) -> State:
    nxt = "retrieve" if not state["context"] else "answer"
    return {**state, "next": nxt}


def retrieve(state: State) -> State:
    # Replace with hybrid retrieval over your corpus.
    return {**state, "context": ["Chunk the corpus by structure, not size."]}


def answer(state: State) -> State:
    return {**state, "answer": " ".join(state["context"]), "next": "done"}


graph = StateGraph(State)
graph.add_node("supervisor", supervisor)
graph.add_node("retrieve", retrieve)
graph.add_node("answer", answer)
graph.set_entry_point("supervisor")
graph.add_conditional_edges(
    "supervisor", lambda s: s["next"], {"retrieve": "retrieve", "answer": "answer"}
)
graph.add_edge("retrieve", "supervisor")
graph.add_edge("answer", END)

app = graph.compile()
print(app.invoke({"question": "How should I chunk documents?", "context": [], "answer": "", "next": "retrieve"}))
