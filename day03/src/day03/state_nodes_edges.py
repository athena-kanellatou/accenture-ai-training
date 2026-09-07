import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph

load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)


class State(TypedDict):
    question: str
    answer: str | None


def normalize(state: State) -> dict:
    """Normalize the question without using an LLM."""
    return {"question": state["question"].strip().rstrip("?") + "?"}


def generate_answer(state: State) -> dict:
    """Use the LLM to answer the normalized question."""
    response = llm.invoke(state["question"])
    return {"answer": response.content}


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
            "question": "  what is the speed of light  ",
            "answer": None,
        }
    )

    print("Question:", result["question"])
    print("Answer:", result["answer"])

    mermaid = app.get_graph().draw_mermaid()

    with open("graph.md", "w", encoding="utf-8") as file:
        file.write("# Day 3 LangGraph\n\n")
        file.write("```mermaid\n")
        file.write(mermaid)
        file.write("\n```\n")

    print("Graph diagram saved to graph.md")


if __name__ == "__main__":
    main()