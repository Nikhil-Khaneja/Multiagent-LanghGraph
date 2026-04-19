# System Architecture

## Overview
This system is designed as a scalable microservice backend that exposes Multi-Agent LLM capabilities via REST/SSE endpoints. It separates concerns between the API layer, the Agentic workflow layer, and the Data/Retrieval layer.

## Component Layout
```
Client Request
    │
    ▼
[ FastAPI Gateway ] ── (Metrics / JSON Logger)
    │
    ▼
[ Agent Service (LangGraph) ]
    │
    ├── Supervisor Node (Orchestrator)
    ├── Retriever Node  ◄── [ FAISS Vector Store ]
    ├── Analyzer Node   
    ├── Guardrails Node (Validator)
    └── Responder Node
```

## RAG Layer (Retrieval-Augmented Generation)
We utilize a dense retrieval strategy using HuggingFace `all-MiniLM-L6-v2` embeddings stored in a FAISS index. 
- **Why FAISS?** It provides a highly efficient, local-first vector search that fits within a single container for this scale. 
- **Vector Dimensions:** The model outputs 384 dimensions. This lower dimensionality is significantly faster to search and uses less memory compared to OpenAI's 1536d embeddings, at a slight cost to semantic nuance.
- **Chunking:** Documents are ingested via `RecursiveCharacterTextSplitter` with 1000 char chunks and 200 char overlap to preserve context boundaries.

## Ingestion Architecture
We implemented an event-driven ingestion abstraction (`KafkaAdapter`).
In production, a Kafka topic `document-ingestion-events` receives messages. The consumer loop reads these, chunks the documents, embeds them, and upserts them to the Vector Database. This decouples write-heavy ingestion from the read-heavy Agent workflow.
