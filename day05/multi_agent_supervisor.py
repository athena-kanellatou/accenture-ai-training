import os
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)


class RouteDecision(BaseModel):
    next_agent: Literal[
        "research_agent",
        "safety_agent",
        "writer_agent",
        "FINISH",
    ] = Field(description="The agent that should work next")


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: str


router_llm = llm.with_structured_output(RouteDecision)


def supervisor(state: State) -> dict:
    """Select the next specialist or finish the workflow."""

    history = "\n\n".join(
        f"{message.type}: {message.content}"
        for message in state["messages"]
    )

    decision = router_llm.invoke(
        f"""
        You are the supervisor of a team of AI specialists.

        Available agents:

        research_agent:
        Finds the important technical information.

        safety_agent:
        Identifies safety risks and necessary safeguards.

        writer_agent:
        Produces the final concise answer using the previous findings.

        Choose only one next agent.

        Rules:
        1. First use the research_agent.
        2. Then use the safety_agent.
        3. Then use the writer_agent.
        4. After the writer_agent produces a final answer, choose FINISH.
        5. Never call the same agent twice.

        Conversation history:
        {history}
        """
    )

    print(f"\nSUPERVISOR ROUTE: {decision.next_agent}")

    return {"next_agent": decision.next_agent}


def research_agent(state: State) -> dict:
    """Research the technical part of the question."""

    question = state["messages"][0].content

    response = llm.invoke(
        f"""
        You are the research specialist.

        User question:
        {question}

        Identify three technically important points.
        Be concise and factual.
        """
    )

    print("\nRESEARCH AGENT COMPLETED")

    return {
        "messages": [
            AIMessage(
                content=response.content,
                name="research_agent",
            )
        ]
    }


def safety_agent(state: State) -> dict:
    """Analyze risks and safeguards."""

    history = "\n\n".join(
        str(message.content)
        for message in state["messages"]
    )

    response = llm.invoke(
        f"""
        You are the AI safety specialist.

        Review the question and the research below:

        {history}

        Identify the main risks and appropriate safeguards.
        Be concise and practical.
        """
    )

    print("\nSAFETY AGENT COMPLETED")

    return {
        "messages": [
            AIMessage(
                content=response.content,
                name="safety_agent",
            )
        ]
    }


def writer_agent(state: State) -> dict:
    """Create the final answer."""

    history = "\n\n".join(
        f"{message.name or message.type}: {message.content}"
        for message in state["messages"]
    )

    response = llm.invoke(
        f"""
        You are the final writer.

        Use the work completed by the other agents:

        {history}

        Produce one clear, concise final answer.
        Do not mention the internal multi-agent workflow.
        """
    )

    print("\nWRITER AGENT COMPLETED")

    return {
        "messages": [
            AIMessage(
                content=response.content,
                name="writer_agent",
            )
        ]
    }


def route_from_supervisor(
    state: State,
) -> Literal[
    "research_agent",
    "safety_agent",
    "writer_agent",
    "FINISH",
]:
    """Return the supervisor's routing decision."""

    return state["next_agent"]


builder = StateGraph(State)

builder.add_node("supervisor", supervisor)
builder.add_node("research_agent", research_agent)
builder.add_node("safety_agent", safety_agent)
builder.add_node("writer_agent", writer_agent)

builder.add_edge(START, "supervisor")

builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "research_agent": "research_agent",
        "safety_agent": "safety_agent",
        "writer_agent": "writer_agent",
        "FINISH": END,
    },
)

builder.add_edge("research_agent", "supervisor")
builder.add_edge("safety_agent", "supervisor")
builder.add_edge("writer_agent", "supervisor")

graph = builder.compile()


def main() -> None:
    initial_state: State = {
        "messages": [
            HumanMessage(
                content=(
                    "How can a healthcare AI agent be made safer "
                    "when handling patient information?"
                )
            )
        ],
        "next_agent": "",
    }

    result = graph.invoke(
        initial_state,
        config={"recursion_limit": 12},
    )

    final_message = result["messages"][-1]

    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(final_message.content)


if __name__ == "__main__":
    main()