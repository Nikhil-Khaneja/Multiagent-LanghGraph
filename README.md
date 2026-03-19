# Multi-Agent LLM Backend 🤖

A scalable, production-style backend system combining **Retrieval-Augmented Generation (RAG)** with a **Multi-Agent Workflow** using LangGraph, FastAPI, and FAISS.

This project demonstrates how to structure an LLM backend for scale, reliability, and observability, focusing on data engineering and systems design principles.

## 🌟 Key Features
- **Multi-Agent Orchestration**: LangGraph-based workflow routing between Retriever, Analyzer, and Responder agents.
- **RAG Subsystem**: FAISS local vector store with recursive chunking for context injection.
- **Guardrails & Reliability**: Strict JSON schema validation for agent handoffs and confidence-based retry routing.
- **Kafka-Style Ingestion**: Async event-based document ingestion abstraction.
- **Observability**: Structured JSON logging and metrics collection (latency, success rates).
- **FastAPI Gateway**: Sync and Async streaming endpoints.
- **Docker & K8s Ready**: Includes Compose and K8s deployment manifests.

## 🚀 Quick Start (Local)

1. **Clone & Setup Environment**
   ```bash
   git clone <repo-url>
   cd Multiagent-LangGraph
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run the Backend**
   ```bash
   ./infra/scripts/run_local.sh
   ```
   *The Web UI will be available at [http://localhost:8000/](http://localhost:8000/)*
   *API Docs available at [http://localhost:8000/docs](http://localhost:8000/docs)*

## 📚 Documentation
Detailed documentation is split into focused guides:
- [Architecture Overview](docs/architecture.md)
- [Workflow & Agents](docs/workflow.md)
- [Guardrails & Safety](docs/guardrails.md)
- [Evaluation Strategy](docs/evaluation.md)

## 🏗️ Architecture Summary
Client requests hit the FastAPI gateway, which instantiates a LangGraph workflow. The Supervisor agent delegates to a Retriever (which queries FAISS). The retrieved context goes to the Analyzer for technical extraction. A Guardrail node validates the Analyzer's JSON output (rejecting/looping if confidence is low). Finally, the Responder synthesizes the final answer.

## ⚠️ Known Limitations & Future Work
- **Local FAISS**: Currently uses a local FAISS index. For production, this should be swapped for Pinecone/Milvus.
- **Mock Kafka**: Real-time ingestion currently uses an in-memory queue adapter simulating Kafka.
- **Scale Claims**: No load tests have been run yet. Latency is heavily dependent on the chosen LLM provider (e.g., OpenAI vs Groq).
