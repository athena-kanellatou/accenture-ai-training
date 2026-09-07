import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph


DATABASE_URL = "postgresql://day04:day04_local_only@localhost:5433/day04"


class State(TypedDict):
    events: Annotated[list[str], operator.add]


def record_event(state: State) -> dict:
    return {"events": ["workflow step completed"]}


graph = StateGraph(State)
graph.add_node("record_event", record_event)
graph.add_edge(START, "record_event")
graph.add_edge("record_event", END)


def main() -> None:
    with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        checkpointer.setup()

        app = graph.compile(checkpointer=checkpointer)

        config = {"configurable": {"thread_id": "demo-ticket-001"}}

        first_run = app.invoke({"events": ["ticket created"]}, config)
        print("First run:", first_run["events"])

        second_run = app.invoke({"events": ["customer replied"]}, config)
        print("Second run:", second_run["events"])


if __name__ == "__main__":
    main()