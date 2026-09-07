import asyncio
import operator
import time
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    question: str
    results: Annotated[list[str], operator.add]
    final_answer: str


async def research_node(state: State) -> dict:
    print("Research started")
    await asyncio.sleep(2)

    print("Research completed")
    return {
        "results": [
            "Research: Encryption protects patient data."
        ]
    }


async def safety_node(state: State) -> dict:
    print("Safety analysis started")
    await asyncio.sleep(3)

    print("Safety analysis completed")
    return {
        "results": [
            "Safety: Access must follow least privilege."
        ]
    }


async def compliance_node(state: State) -> dict:
    print("Compliance review started")
    await asyncio.sleep(1)

    print("Compliance review completed")
    return {
        "results": [
            "Compliance: All access should be auditable."
        ]
    }


async def synthesis_node(state: State) -> dict:
    print("\nSynthesis started")

    combined_results = "\n".join(state["results"])

    final_answer = (
        "Healthcare AI safety recommendations:\n"
        f"{combined_results}"
    )

    return {"final_answer": final_answer}


builder = StateGraph(State)

builder.add_node("research", research_node)
builder.add_node("safety", safety_node)
builder.add_node("compliance", compliance_node)
builder.add_node("synthesis", synthesis_node)

# Οι τρεις nodes ξεκινούν παράλληλα.
builder.add_edge(START, "research")
builder.add_edge(START, "safety")
builder.add_edge(START, "compliance")

# Το synthesis περιμένει να ολοκληρωθούν και οι τρεις.
builder.add_edge(
    ["research", "safety", "compliance"],
    "synthesis",
)

builder.add_edge("synthesis", END)

graph = builder.compile()


async def main() -> None:
    initial_state: State = {
        "question": (
            "How can healthcare AI handle patient data safely?"
        ),
        "results": [],
        "final_answer": "",
    }

    start_time = time.perf_counter()

    result = await graph.ainvoke(initial_state)

    elapsed_time = time.perf_counter() - start_time

    print("\n" + "=" * 60)
    print(result["final_answer"])
    print("=" * 60)
    print(f"Total execution time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())