# Versioning & Changelog

This document maintains the historical evolution of the Multi-Agent LLM Backend project for backtracking and auditing purposes.

## [v2.0.0] - 2026-04-06
### Added
- **Multi-Agent Orchestration**: Complete rewrite of the agent workflow using LangGraph state machines (`agentflow/`). Includes Retriever, Analyzer, Responder, and Supervisor nodes.
- **RAG Subsystem**: Implemented a local FAISS vector store with HuggingFace `all-MiniLM-L6-v2` embeddings and document ingestion/chunking logic.
- **Guardrails**: Added strict JSON schema validation and confidence thresholding for agent outputs to prevent hallucinations and infinite loops.
- **FastAPI Gateway**: Migrated from simple CRUD endpoints to async streaming and query endpoints (`server/app/api/`).
- **Kafka Adapter**: Introduced `LocalKafkaAdapter` for simulating event-driven context ingestion in the background.
- **Observability**: Added structured JSON logging and custom metric tracking (throughput, latency, success rates).
- **Modern Dashboard**: Replaced the legacy book CRUD UI with a real-time streaming agent trace interface (`webapp/`).
- **Infrastructure**: Added `Dockerfile`, `docker-compose.yml`, and `deployment.yaml` for Kubernetes.
- **Automated UAT**: Added `run_uat.py` to test system health, ingestion, and agent routing logic.

### Changed
- Refactored project structure into distinct `agentflow/`, `server/`, `webapp/`, `infra/`, and `docs/` directories.
- Relaxed Pydantic and FastAPI requirements in `requirements.txt` to resolve dependency conflicts with LangChain.

### Deprecated & Archived
- The legacy Book Management API (`main.py`, `models.py`, `server/api.py`, `server/schemas.py`, `server/storage.py`) has been archived.
- The standalone LangGraph prototype scripts (`agent_nodes.py`, `agent_state.py`, `run_graph.py`, `run_graph_stream.py`, `run_langgraph.py`) have been archived.
- *Note: These files have been removed from Git tracking but are retained locally in the `.gitignore`d `legacy_code/` directory for backtracking.*

---

## [v1.0.0] - Legacy Prototype
### Added
- Basic FastAPI server demonstrating CRUD operations (Create, Read, Update, Delete) for a static in-memory book list.
- Vanilla HTML/JS frontend to interact with the CRUD API.
- Introductory LangGraph tutorial script featuring a Planner and Reviewer agent working on a "Book Proposal" domain.
- Basic Supervisor pattern for routing.
