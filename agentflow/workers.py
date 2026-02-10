import os
from typing import Dict, Any
from .memory import FlowState

def planner_worker(state: FlowState) -> Dict[str, Any]:
    print("---NODE: planner_worker---")
    state["turn"] = state.get("turn", 0) + 1

    proposal = {
        "summary": f"Plan for: {state.get('task', '')}",
        "title": state.get("title", ""),
        "notes": "Draft proposal generated."
    }
    return {"plan": proposal, "turn": state["turn"]}

def reviewer_worker(state: FlowState) -> Dict[str, Any]:
    print("---NODE: reviewer_worker---")
    state["turn"] = state.get("turn", 0) + 1

    force_reject = os.getenv("FORCE_REJECT") == "1"
    has_issues = force_reject or not state.get("plan")

    feedback = {
        "has_issues": has_issues,
        "comments": "Please improve clarity." if has_issues else "Looks good."
    }
    return {"review": feedback, "turn": state["turn"]}

def supervisor_worker(state: FlowState) -> Dict[str, Any]:
    print("---NODE: supervisor_worker---")
    return {}
