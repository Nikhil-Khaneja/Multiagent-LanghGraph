# Agent Workflow

The core intelligence of the system is managed by a LangGraph StateMachine.

## State Representation
All nodes read from and write to a centralized `WorkflowState` TypedDict. This prevents passing large nested objects between functions and maintains a clear audit trail.

## Nodes
1. **Supervisor**: Determines if the graph should continue, stop, or error out based on `turn_count` and state completeness.
2. **Retriever**: Executes semantic search against the FAISS index using the user's query.
3. **Analyzer**: Instructed to extract structured findings and assess if the context is sufficient.
4. **Guardrails**: (Non-LLM node) Runs deterministic schema validation on the Analyzer's output.
5. **Responder**: Synthesizes the final human-readable response based *only* on the Analyzer's structured output.

## Routing Logic
The `router.py` handles conditional edges:
- If `turn_count > MAX_TURNS` -> END
- If validation fails -> Loop back to Analyzer
- If successful -> Responder -> END
