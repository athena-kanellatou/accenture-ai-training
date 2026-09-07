"""
LangGraph and routing
"""

import os
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)


class State(TypedDict):
    ticket: str
    category: str | None
    reply: str | None


def classify(
    state: State,
) -> Command[Literal["billing", "bug", "general"]]:
    """Classify a support ticket and route it to the right handler."""

    category = (
        llm.invoke(
            "Classify this support ticket as exactly one word: "
            f"billing, bug, or general.\n\nTicket: {state['ticket']!r}"
        )
        .content.strip()
        .lower()
    )

    category = (
        category
        if category in ("billing", "bug", "general")
        else "general"
    )

    return Command(
        goto=category,
        update={"category": category},
    )


def billing(state: State) -> dict:
    """Handle billing-related support tickets."""

    response = llm.invoke(
        f"Write a short billing-support reply to: {state['ticket']!r}"
    )

    return {"reply": response.content}


def bug(state: State) -> dict:
    """Handle bug-report support tickets."""

    response = llm.invoke(
        f"Write a short reply acknowledging this bug report: "
        f"{state['ticket']!r}"
    )

    return {"reply": response.content}


def general(state: State) -> dict:
    """Handle general support tickets."""

    response = llm.invoke(
        f"Write a short general support reply to: {state['ticket']!r}"
    )

    return {"reply": response.content}


graph = StateGraph(State)

graph.add_node("classify", classify)
graph.add_node("billing", billing)
graph.add_node("bug", bug)
graph.add_node("general", general)

graph.add_edge(START, "classify")
graph.add_edge("billing", END)
graph.add_edge("bug", END)
graph.add_edge("general", END)

app = graph.compile()


def main() -> None:
    result = app.invoke(
        {
            "ticket": "I was charged twice this month",
        }
    )

    print(result)

    app.get_graph().draw_mermaid_png(output_file_path="graph.png")


if __name__ == "__main__":
    main()