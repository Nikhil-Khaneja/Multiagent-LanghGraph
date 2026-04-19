# Project Code Walkthrough

This document provides a guided tour of the codebase, ideal for presenting the project in a technical interview.

## 📂 1. Folder Structure Overview

- **`agentflow/`**: The core AI logic. Isolated from the web server.
  - `state/`: Contains `WorkflowState`, the TypedDict that acts as the single source of truth.
  - `nodes/`: Individual agent functions (Retriever, Analyzer, Responder, Supervisor).
  - `routing/`: `router.py` holds the conditional logic that directs the graph.
  - `guardrails/`: Deterministic validation logic.
  - `memory/`: FAISS vector store manager and text ingestion pipeline.
  - `graph/`: `builder.py` compiles the LangGraph state machine.
- **`server/`**: The FastAPI application.
  - `api/`: REST endpoints (`/query`, `/ingest`, `/metrics`).
  - `services/`: Wrappers like `agent_service.py` to trigger the LangGraph.
  - `observability/`: Custom JSON logger and metrics collector.
  - `ingestion/`: Kafka mock adapter and event schemas.
- **`webapp/`**: Static frontend dashboard.
- **`infra/`**: Docker, K8s, and bash deployment scripts.

---

## 🧠 2. The Agentic State Design (`agentflow/state/workflow_state.py`)
In LangGraph, state is passed between nodes. Instead of passing massive objects, we use a structured `TypedDict`.
- **Input**: `query`, `session_id`.
- **RAG**: `retrieved_context` (List of dicts).
- **Agent Outputs**: `analysis_findings` (JSON), `final_response` (String).
- **Control**: `current_node`, `turn_count`, `is_valid`.

*Interview Talking Point:* "Using a strict TypedDict prevents random state mutations and provides a clear contract for what data is available at any point in the graph."

---

## 🧭 3. Routing Logic (`agentflow/routing/router.py`)
The `route_from_supervisor` function dictates the flow. It acts as the brain:
1. Checks for infinite loops (`turn_count >= MAX_TURNS`).
2. Checks if context is missing -> routes to `retriever`.
3. Checks if analysis is missing -> routes to `analyzer`.
4. **Guardrail Check**: If `is_valid` is False, it loops *back* to the `analyzer`.
5. Finally, routes to `responder` to finish.

---

## 🛡️ 4. Validation Flow (`agentflow/guardrails/validators.py`)
The Analyzer LLM outputs JSON. The `apply_guardrails` node intercepts this before it goes anywhere else.
It checks for `key_points` and ensures `confidence_score` > 0.3. If it fails, it sets `is_valid = False`, triggering the router's retry logic.

*Interview Talking Point:* "This is where I applied data engineering principles. You wouldn't trust an unvalidated JSON payload in a data pipeline, and you shouldn't trust an unvalidated LLM output in an agent workflow."

---

## 📚 5. Retrieval Flow (`agentflow/memory/`)
1. **Ingestion**: `ingestion.py` uses LangChain's `RecursiveCharacterTextSplitter`.
2. **Storage**: `vector_store.py` manages a local `FAISS` index.
3. **Retrieval**: The `retriever_node` calls `vector_store_manager.retrieve()` with a score threshold to drop irrelevant chunks.

---

## 📡 6. API Request Lifecycle (`server/app/api/router.py`)
1. Client POSTs to `/api/v1/query`.
2. The FastAPI router calls `agent_service.execute_query()`.
3. A `trace_id` (UUID) is generated for logging.
4. The LangGraph executes synchronously.
5. Metrics (latency, success) are recorded via `metrics_collector`.
6. `QueryResponse` is returned to the client.

---

## 📈 7. Logging & Metrics (`server/app/observability/`)
`logger.py` overrides the standard Python logger to output pure JSON. This means tools like Datadog can ingest it perfectly. `metrics.py` holds in-memory counters for latency and success rates, which are exposed via the `/api/v1/metrics` endpoint.

---

## 🐳 8. Local Deployment & Testing (`infra/`)
The `infra/scripts/run_local.sh` script bootstraps the Python environment. The `Dockerfile` packages the FAISS dependencies (which require C++ build tools) securely. 

*Interview Talking Point:* "I structured the repo so that it's easy for another engineer to spin up locally using Docker Compose, while keeping the architecture close to what it would look like on Kubernetes."
