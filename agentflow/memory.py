from typing import TypedDict, Dict, Any, Optional

class FlowState(TypedDict, total=False):
    title: str
    content: str
    task: str
    strict: bool
    llm: Any

    plan: Dict[str, Any]
    review: Dict[str, Any]
    turn: int
    done: bool

def seed_state(*, title: str, content: str, task: str, strict: bool, llm: Any) -> FlowState:
    return {
        "title": title,
        "content": content,
        "task": task,
        "strict": strict,
        "llm": llm,
        "plan": {},
        "review": {},
        "turn": 0,
        "done": False,
    }
