from langgraph.graph import StateGraph, END
from .memory import FlowState
from .workers import planner_worker, reviewer_worker, supervisor_worker
from .directors import decide_next

def build_pipeline():
    g = StateGraph(FlowState)

    g.add_node("boss", supervisor_worker)
    g.add_node("planner", planner_worker)
    g.add_node("reviewer", reviewer_worker)

    g.set_entry_point("boss")

    g.add_edge("planner", "boss")
    g.add_edge("reviewer", "boss")

    def route(state: FlowState):
        action = decide_next(state)
        if action == "PLAN":
            return "planner"
        if action == "REVIEW":
            return "reviewer"
        return END

    g.add_conditional_edges("boss", route, {"planner": "planner", "reviewer": "reviewer", END: END})

    return g.compile()
