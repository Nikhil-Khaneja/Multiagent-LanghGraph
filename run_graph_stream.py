"""
Streaming runner for the stateful agent graph.

This script exposes a `GraphRunner` with a `.stream()` generator method that
yields events after each node executes. It uses the same node functions as
`run_graph.py`. Use the `FORCE_REJECT=1` environment variable to force the
reviewer to always produce an issue for testing the correction loop.

Usage:

# Run in normal mode (uses DummyLLM if no OPENAI_API_KEY):
python run_graph_stream.py

# Run with forced rejection to test loop:
FORCE_REJECT=1 python run_graph_stream.py
"""
import os
import json
from typing import Any, Dict, Generator
from dotenv import load_dotenv

from agent_state import create_initial_state, AgentState
from agent_nodes import planner_node, reviewer_node, supervisor_node, router_logic

# Reuse LLM chooser from run_graph
try:
    from run_graph import get_llm
except Exception:
    # Fallback: simple dummy LLM if run_graph not importable
    class DummyResponse:
        def __init__(self, content: str):
            self.content = content
    class DummyLLM:
        def invoke(self, prompt: str):
            return DummyResponse(json.dumps({"message": "dummy"}))
    def get_llm():
        return DummyLLM()


class GraphRunner:
    def __init__(self, state: AgentState):
        self.state = state

    def stream(self) -> Generator[Dict[str, Any], None, None]:
        """Generator that yields step events as the graph runs.

        Each yielded dict contains:
        - step: int (step count)
        - node: str (which node ran)
        - updates: Dict[str, Any] (state updates from node)
        - state: snapshot of state after merge
        """
        step = 0
        while True:
            # Supervisor updates
            updates = supervisor_node(self.state)
            if updates:
                # merge
                for k, v in updates.items():
                    self.state[k] = v
            step += 1
            yield {"step": step, "node": "supervisor", "updates": updates, "state": dict(self.state)}

            # Router decides
            next_node = router_logic(self.state)
            yield {"step": step, "node": "router_decision", "updates": {}, "state": dict(self.state), "next": next_node}

            if next_node == "planner":
                updates = planner_node(self.state)
                for k, v in updates.items():
                    self.state[k] = v
                step += 1
                yield {"step": step, "node": "planner", "updates": updates, "state": dict(self.state)}

            elif next_node == "reviewer":
                updates = reviewer_node(self.state)
                for k, v in updates.items():
                    self.state[k] = v
                step += 1
                yield {"step": step, "node": "reviewer", "updates": updates, "state": dict(self.state)}

            elif next_node == "end":
                yield {"step": step, "node": "end", "updates": {}, "state": dict(self.state)}
                break

            else:
                yield {"step": step, "node": "unknown", "updates": {}, "state": dict(self.state), "error": f"Unknown next node: {next_node}"}
                break


def main():
    load_dotenv()
    llm = get_llm()
    initial_state = create_initial_state(
        title="The Great Gatsby",
        content="A novel about the American Dream and the Roaring Twenties...",
        email="student@example.com",
        strict=False,
        task="Create and review a proposal for improving this book description",
        llm=llm,
    )

    runner = GraphRunner(initial_state)
    print("")
    print("Streaming graph run (press Ctrl+C to stop):")
    print("")
    for event in runner.stream():
        # Nicely print each event
        node = event.get("node")
        step = event.get("step")
        print(f"[Step {step}] Node: {node}")
        if node == "router_decision":
            print(f"  → Next: {event.get('next')}")
        if event.get("updates"):
            print(f"  Updates: {json.dumps(event['updates'], indent=2)}")
        # Print limited state for readability (exclude non-serializable llm)
        state_copy = {k: v for k, v in event['state'].items() if k != 'llm'}
        print(f"  State snapshot: {json.dumps(state_copy, indent=2, default=str)[:800]}")
        print("\n---\n")

    print("Graph stream finished.")


if __name__ == "__main__":
    main()
