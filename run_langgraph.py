import os
from dotenv import load_dotenv
from typing import Dict

from langgraph.graph import StateGraph, END

from agent_state import create_initial_state, AgentState
from agent_nodes import planner_node, reviewer_node, supervisor_node, router_logic

# Reuse your LLM chooser (already exists in run_graph.py)
from run_graph import get_llm


def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("planner", planner_node)
    graph.add_node("reviewer", reviewer_node)

    # Entry point
    graph.set_entry_point("supervisor")

    # After planner/reviewer, go back to supervisor (supervisor pattern loop)
    graph.add_edge("planner", "supervisor")
    graph.add_edge("reviewer", "supervisor")

    # Conditional routing from supervisor
    # router_logic returns: "planner" / "reviewer" / "end" (your current behavior)
    def route_from_supervisor(state: AgentState) -> str:
        nxt = router_logic(state)
        return END if nxt == "end" else nxt

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "planner": "planner",
            "reviewer": "reviewer",
            END: END,
        },
    )

    return graph.compile()


def main():
    load_dotenv()
    llm = get_llm()

    state = create_initial_state(
        title="The Great Gatsby",
        content="A novel about the American Dream and the Roaring Twenties...",
        email="nikhil@sjsu.com",
        strict=False,
        task="Create and review a proposal for improving this book description",
        llm=llm,
    )

    app = build_graph()

    print("\nStreaming LangGraph execution:\n")
    # .stream() yields events; mode varies by langgraph version
    for event in app.stream(state):
        print(event)


if __name__ == "__main__":
    main()
