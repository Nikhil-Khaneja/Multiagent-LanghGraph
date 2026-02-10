"""
Run the stateful agent graph (Supervisor pattern) for Part 3.

This script wires together the nodes in `agent_nodes.py` and the
`AgentState` in `agent_state.py` and provides a simple runner that
executes until the router returns "end" or the max turns are reached.

Usage:
    python run_graph.py

If you have an OpenAI key in your environment, the script will attempt
to use `langchain.chat_models.ChatOpenAI`. Otherwise it will use a
`DummyLLM` for local testing.
"""
import os
import json
from typing import Any, Dict
from dotenv import load_dotenv

# Local imports
from agent_state import create_initial_state, AgentState
from agent_nodes import planner_node, reviewer_node, supervisor_node, router_logic

# Try to import a real LLM from langchain if available; otherwise fallback
try:
    from langchain.chat_models import ChatOpenAI
    REAL_LLM_AVAILABLE = True
except Exception:
    REAL_LLM_AVAILABLE = False


class DummyResponse:
    def __init__(self, content: str):
        self.content = content


class DummyLLM:
    """Simple deterministic LLM stub for offline testing."""
    def invoke(self, prompt: str) -> DummyResponse:
        # Heuristic replies for planner vs reviewer based on prompt contents
        if "book planner" in prompt.lower():
            response = json.dumps({
                "title": "(Planner) Improved Title",
                "content": "(Planner) Improved content summary...",
                "suggestions": ["Make pacing clearer", "Add stronger opening"],
                "strengths": ["Good themes", "Strong voice"],
                "areas_for_improvement": ["Pacing", "Clarity"]
            })
        elif "book reviewer" in prompt.lower():
            response = json.dumps({
                "issues": [],
                "suggestions": ["Looks solid"],
                "approved": True,
                "confidence_score": 0.95,
                "detailed_feedback": "This proposal looks publishable with minor edits."
            })
        else:
            response = json.dumps({"message": "Default stub response"})
        return DummyResponse(response)


def get_llm():
    load_dotenv()
    if REAL_LLM_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        print("Using real ChatOpenAI model from langchain")
        return ChatOpenAI(model_name="gpt-4")
    else:
        print("OPENAI_API_KEY not found or langchain unavailable — using DummyLLM")
        return DummyLLM()


def merge_state(state: AgentState, updates: Dict[str, Any]):
    """Merge updates into the AgentState object (in-place).

    For simplicity we assume AgentState is a TypedDict and is also a
    normal dict-like object (the create_initial_state returns a dict).
    """
    for k, v in updates.items():
        state[k] = v


def run_graph(state: AgentState):
    """Run the graph loop until router returns 'end'."""
    print("\\nStarting stateful agent graph run...\\n")

    while True:
        # 1) Supervisor state update node
        sup_updates = supervisor_node(state)
        if isinstance(sup_updates, dict):
            merge_state(state, sup_updates)

        # 2) Router decides next node
        next_node = router_logic(state)

        if next_node == "planner":
            updates = planner_node(state)
            merge_state(state, updates)
        elif next_node == "reviewer":
            updates = reviewer_node(state)
            merge_state(state, updates)
        elif next_node == "end":
            print("\\nGraph signaled END — finishing execution.")
            break
        else:
            print(f"\\nUnknown node returned by router: {next_node} — ending.")
            break

        print("\\n--- State after step ---")
        print(json.dumps(state, indent=2, default=str)[:2000])

    print("\\nFinal state:")
    print(json.dumps(state, indent=2, default=str)[:2000])


if __name__ == "__main__":
    llm = get_llm()

    # Initial example inputs — adjust as needed
    initial_state = create_initial_state(
        title="The Great Gatsby",
        content="A novel about the American Dream and the Roaring Twenties...",
        email="student@example.com",
        strict=False,
        task="Create and review a proposal for improving this book description",
        llm=llm,
    )

    run_graph(initial_state)
