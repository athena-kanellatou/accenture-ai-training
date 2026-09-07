"""
Example 21: Langfuse tracing
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langfuse.langchain import CallbackHandler
from langgraph.graph import END, START, StateGraph


load_dotenv()


llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)


class State(TypedDict):
    ticket: str
    category: str | None
    reply: str | None


def classify(state: State) -> dict:
    """Classify the ticket by category."""

    response = llm.invoke(
        f"One word category (billing/bug/general): {state['ticket']!r}"
    )

    return {"category": response.content.strip()}


def reply(state: State) -> dict:
    """Draft a reply based on the category."""

    prompt = (
        f"Write a short reply to this {state['category']} ticket: "
        f"{state['ticket']!r}"
    )

    response = llm.invoke(prompt)

    return {"reply": response.content}


graph = StateGraph(State)

graph.add_node("classify", classify)
graph.add_node("reply", reply)

graph.add_edge(START, "classify")
graph.add_edge("classify", "reply")
graph.add_edge("reply", END)

app = graph.compile()


langfuse_handler = CallbackHandler()

result = app.invoke(
    {
        "ticket": "Payment failed twice",
        "category": None,
        "reply": None,
    },
    config={
        "callbacks": [langfuse_handler],
        "run_name": "customer-support-ticket",
    },
)

print("Category:", result["category"])
print("Reply:", result["reply"])