"""
Langfuse tracing with LangGraph and Azure OpenAI.
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langfuse.langchain import CallbackHandler
from langgraph.graph import END, START, StateGraph


# Load variables from the .env file
load_dotenv()


# Azure OpenAI model
llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)


# State shared between the graph nodes
class TicketState(TypedDict):
    ticket: str
    category: str | None
    reply: str | None


def classify_ticket(state: TicketState) -> dict:
    """Classify the support ticket."""

    response = llm.invoke(
        "Classify the following support ticket into exactly one category: "
        "billing, technical, or general.\n\n"
        f"Ticket: {state['ticket']}"
    )

    return {
        "category": response.content.strip()
    }


def create_reply(state: TicketState) -> dict:
    """Create a short response to the support ticket."""

    response = llm.invoke(
        "Write a short and helpful customer-support response.\n\n"
        f"Category: {state['category']}\n"
        f"Ticket: {state['ticket']}"
    )

    return {
        "reply": response.content.strip()
    }


# Build the LangGraph workflow
graph = StateGraph(TicketState)

graph.add_node("classify", classify_ticket)
graph.add_node("reply", create_reply)

graph.add_edge(START, "classify")
graph.add_edge("classify", "reply")
graph.add_edge("reply", END)

app = graph.compile()


# Create the Langfuse callback handler
langfuse_handler = CallbackHandler()


# Run the graph and send the trace to Langfuse
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


# Display the final result
print("Category:", result["category"])
print("Reply:", result["reply"])