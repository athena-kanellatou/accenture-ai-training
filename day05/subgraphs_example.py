from typing import TypedDict

from langgraph.graph import END, START, StateGraph


# -----------------------------
# SUBGRAPH
# -----------------------------

class ResearchState(TypedDict):
    topic: str
    draft: str
    verified_result: str


def analyze_topic(state: ResearchState) -> dict:
    print("SUBGRAPH: Analyzing topic")

    draft = (
        f"Initial analysis of '{state['topic']}': "
        "encryption, access control and audit logging "
        "are important safeguards."
    )

    return {"draft": draft}


def verify_analysis(state: ResearchState) -> dict:
    print("SUBGRAPH: Verifying analysis")

    verified_result = (
        f"{state['draft']} "
        "The analysis was reviewed and approved."
    )

    return {"verified_result": verified_result}


research_builder = StateGraph(ResearchState)

research_builder.add_node("analyze", analyze_topic)
research_builder.add_node("verify", verify_analysis)

research_builder.add_edge(START, "analyze")
research_builder.add_edge("analyze", "verify")
research_builder.add_edge("verify", END)

research_subgraph = research_builder.compile()


# -----------------------------
# PARENT GRAPH
# -----------------------------

class ParentState(TypedDict):
    question: str
    research_output: str
    final_answer: str


def run_research_subgraph(state: ParentState) -> dict:
    print("\nPARENT: Calling research subgraph")

    # State mapping:
    # parent question → subgraph topic
    subgraph_input: ResearchState = {
        "topic": state["question"],
        "draft": "",
        "verified_result": "",
    }

    subgraph_result = research_subgraph.invoke(
        subgraph_input
    )

    # State mapping:
    # subgraph verified_result → parent research_output
    return {
        "research_output": subgraph_result[
            "verified_result"
        ]
    }


def create_final_answer(state: ParentState) -> dict:
    print("PARENT: Creating final answer")

    final_answer = (
        "Final healthcare AI recommendation:\n"
        f"{state['research_output']}"
    )

    return {"final_answer": final_answer}


parent_builder = StateGraph(ParentState)

parent_builder.add_node(
    "research_module",
    run_research_subgraph,
)
parent_builder.add_node(
    "final_answer",
    create_final_answer,
)

parent_builder.add_edge(START, "research_module")
parent_builder.add_edge(
    "research_module",
    "final_answer",
)
parent_builder.add_edge("final_answer", END)

parent_graph = parent_builder.compile()


def main() -> None:
    initial_state: ParentState = {
        "question": (
            "How should a healthcare AI agent "
            "protect patient information?"
        ),
        "research_output": "",
        "final_answer": "",
    }

    result = parent_graph.invoke(initial_state)

    print("\n" + "=" * 60)
    print(result["final_answer"])
    print("=" * 60)


if __name__ == "__main__":
    main()