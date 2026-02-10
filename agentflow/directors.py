from .memory import FlowState

MAX_TURNS = 6

def decide_next(state: FlowState) -> str:
    # stop condition
    if state.get("turn", 0) >= MAX_TURNS:
        return "STOP"

    # if no plan yet -> plan first
    if not state.get("plan"):
        return "PLAN"

    # if no review yet -> review
    if not state.get("review"):
        return "REVIEW"

    # if reviewer says issues -> go back to plan
    if state["review"].get("has_issues"):
        state["review"] = {}
        return "PLAN"

    return "STOP"
