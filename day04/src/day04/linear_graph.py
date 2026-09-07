from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    raw_text: str
    cleaned_text: str


def validate(state: State) -> dict:
    text = state["raw_text"].strip()

    if not text:
        raise ValueError("empty ticket text")

    return {"cleaned_text": text}


def summarize(state: State) -> dict:
    return {
        "cleaned_text": f"Ticket received: {state['cleaned_text']}"
    }


graph = StateGraph(State)

graph.add_node("validate", validate)
graph.add_node("summarize", summarize)

graph.add_edge(START, "validate")
graph.add_edge("validate", "summarize")
graph.add_edge("summarize", END)

app = graph.compile()


def main() -> None:
    result = app.invoke({"raw_text": "  I was charged twice  "})
    print(result["cleaned_text"])


if __name__ == "__main__":
    main()