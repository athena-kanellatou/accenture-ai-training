from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph


load_dotenv()

llm = AzureChatOpenAI(model="gpt-4.1-mini")


class State(TypedDict):
    question: str
    answer: str | None


def normalize(state: State) -> dict:
    """Normalize the question without requiring answer to exist."""

    if state.get("answer") is not None:
        print(
            "[normalize] already answered, "
            "skipping re-normalization tweaks"
        )

    return {
        "question": state["question"].strip().rstrip("?") + "?"
    }


def generate_answer(state: State) -> dict:
    """Use the LLM to answer the normalized question."""

    response = llm.invoke(state["question"])

    return {
        "answer": response.content
    }


graph = StateGraph(State)

graph.add_node("normalize", normalize)
graph.add_node("answer", generate_answer)

graph.add_edge(START, "normalize")
graph.add_edge("normalize", "answer")
graph.add_edge("answer", END)       

app = graph.compile()


def main() -> None:
    result = app.invoke(
        {
            "question": "  what is the speed of light  "
        }
    )

    print(result)

    mermaid = app.get_graph().draw_mermaid()

    with open("graph.md", "w", encoding="utf-8") as file:
        file.write("# Unit 10 — LangGraph\n\n")
        file.write("```mermaid\n")
        file.write(mermaid)
        file.write("\n```\n")


if __name__ == "__main__":
    main()

