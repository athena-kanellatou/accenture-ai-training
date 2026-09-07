import operator
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


load_dotenv()

llm = AzureChatOpenAI(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)


class Plan(BaseModel):
    steps: list[str] = Field(
        description="Ordered, concrete steps needed to answer the question"
    )


class Replan(BaseModel):
    done: bool = Field(
        description="True when enough information is available"
    )
    remaining_steps: list[str] = Field(
        description="Steps that still need to be completed"
    )
    final_response: str | None = Field(
        default=None,
        description="Final answer when done is True",
    )


class State(TypedDict):
    question: str
    plan: list[str]
    past_steps: Annotated[list[str], operator.add]
    response: str | None


planner_llm = llm.with_structured_output(Plan)
replanner_llm = llm.with_structured_output(Replan)


def planner(state: State) -> dict:
    """Create the initial plan."""

    result = planner_llm.invoke(
        f"""
        Create a short plan with 2-4 concrete steps.

        Question:
        {state["question"]}
        """
    )

    return {"plan": result.steps}


def executor(state: State) -> dict:
    """Execute the first remaining step."""

    current_step = state["plan"][0]

    result = llm.invoke(
        f"""
        Original question:
        {state["question"]}

        Current step:
        {current_step}

        Complete only this step and return a concise result.
        """
    )

    completed_step = (
        f"STEP: {current_step}\n"
        f"RESULT: {result.content}"
    )

    return {
        "past_steps": [completed_step],
        "plan": state["plan"][1:],
    }


def replanner(state: State) -> dict:
    """Decide whether to finish or update the plan."""

    result = replanner_llm.invoke(
        f"""
        Original question:
        {state["question"]}

        Completed work:
        {state["past_steps"]}

        Remaining plan:
        {state["plan"]}

        Decide whether the question can now be answered.

        If done is True:
        - return an empty remaining_steps list
        - provide the final_response

        If done is False:
        - provide the updated remaining_steps
        - final_response must be null
        """
    )

    if result.done:
        return {
            "plan": [],
            "response": result.final_response,
        }

    return {
        "plan": result.remaining_steps,
        "response": None,
    }


def should_continue(state: State) -> str:
    """Route either to another execution or to END."""

    if state["response"] is not None:
        return "end"

    return "continue"


graph_builder = StateGraph(State)

graph_builder.add_node("planner", planner)
graph_builder.add_node("executor", executor)
graph_builder.add_node("replanner", replanner)

graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "executor")
graph_builder.add_edge("executor", "replanner")

graph_builder.add_conditional_edges(
    "replanner",
    should_continue,
    {
        "continue": "executor",
        "end": END,
    },
)

graph = graph_builder.compile()


def main() -> None:
    question = (
        "Explain three practical ways an AI agent can be made safer."
    )

    initial_state: State = {
        "question": question,
        "plan": [],
        "past_steps": [],
        "response": None,
    }

    result = graph.invoke(
        initial_state,
        config={"recursion_limit": 15},
    )

    print("\nFINAL PLAN:")
    for step in result["past_steps"]:
        print(step)
        print("-" * 60)

    print("\nFINAL RESPONSE:")
    print(result["response"])


if __name__ == "__main__":
    main()