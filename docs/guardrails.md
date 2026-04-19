# Guardrails and Reliability

LLMs are non-deterministic. For a backend to be production-ready, it must enforce strict contracts.

## Validation Strategy
We treat agent handoffs exactly like API boundaries. When the `Analyzer` agent completes its work, it does not hand text directly to the `Responder`. Instead, it outputs a JSON string.

The `Guardrails` node parses this JSON and validates:
1. **Schema Compliance**: Are `key_points`, `is_sufficient_context`, and `confidence_score` present?
2. **Type Checking**: Is confidence a float?
3. **Thresholding**: Is the confidence > 0.3?

## Failure Modes & Fallbacks
- **Parsing Failure**: If the LLM returns invalid JSON, the system defaults to a structured error state, and the router forces a retry (up to `MAX_TURNS`).
- **Low Confidence**: If the agent explicitly states confidence is low, the router triggers a fallback loop to re-analyze or prompt the user for clarification.
- **Infinite Loops**: A hard `MAX_TURNS=5` check in the Supervisor prevents runaway LLM execution, failing gracefully.
