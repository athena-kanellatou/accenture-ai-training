"""
Observe a LangGraph workflow with Langfuse.
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


class TicketState(TypedDict):
    ticket: str
    category: str | None
    reply: str | None


def classify(state: TicketState) -> dict:
    """Classify the customer-support ticket."""

    response = llm.invoke(
        "Classify this customer-support ticket as billing, technical, "
        f"or general. Return one category only.\n\nTicket: {state['ticket']}"
    )

    return {
        "category": response.content.strip()
    }


def reply(state: TicketState) -> dict:
    """Create a helpful response."""

    response = llm.invoke(
        "Write a short and helpful response to this customer-support ticket.\n\n"
        f"Category: {state['category']}\n"
        f"Ticket: {state['ticket']}"
    )

    return {
        "reply": response.content.strip()
    }


graph = StateGraph(TicketState)

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