# Interview Prep: Multi-Agent LLM Backend

**Your Profile Framing:**
"As a Data Engineer with 4 years of experience, I wanted to expand into AI Infrastructure. I built this Multi-Agent LLM backend to demonstrate how I apply data engineering rigor (pipelines, observability, schema contracts) to GenAI workflows."

---

### 1. Describe the end-to-end agentic workflow designed, built, and deployed
"I built a state-machine architecture using LangGraph wrapped in a FastAPI backend. When a request comes in, a **Supervisor Agent** initializes the state and routes the query to a **Retriever Agent** which performs vector search against a local FAISS index. The retrieved context is passed to an **Analyzer Agent** which acts as the reasoning engine, extracting technical points and outputting structured JSON. A deterministic **Guardrail Node** validates this JSON. If it passes, the **Responder Agent** drafts the final reply; if it fails, the router loops it back for correction. The entire state is preserved for auditability."

### 2. Key success metrics
"I instrumented the application with a `MetricsCollector`. The core metrics I tracked were:
1. **Success Rate**: The percentage of workflows that completed without unhandled exceptions or infinite loops.
2. **Average Latency**: End-to-end processing time, which is critical since agent workflows chain multiple LLM calls.
3. **Ingestion Volume**: Tracking the throughput of documents embedded into the FAISS index."

### 3. How accuracy/effectiveness was measured
"Rather than just eyeballing outputs, I relied on structured JSON extraction from the Analyzer agent. By forcing the LLM to output a `confidence_score` and an `is_sufficient_context` boolean, I could programmatically measure effectiveness. If the system frequently hit fallback loops, it indicated poor retrieval effectiveness or poorly tuned prompts."

### 4. Software stack and tools used
- **Backend**: FastAPI (Python), Uvicorn for async server.
- **Orchestration**: LangGraph and LangChain.
- **RAG/Vector**: FAISS (local, fast CPU retrieval), `sentence-transformers` for embeddings.
- **Infrastructure**: Docker for containerization, Kubernetes (Manifests) for deployment, and a mock Kafka adapter for event-driven ingestion.

### 5. How guardrails were implemented
"I treated agent handoffs like microservice API contracts. Instead of the Analyzer agent passing raw text to the Responder, it had to output a specific JSON schema. I built a Python guardrail function that parsed this output using `json.loads` and verified the presence of required keys (`key_points`, `confidence_score`). If the LLM hallucinated the schema or returned a confidence score below `0.3`, the guardrail threw a validation error, and my LangGraph router intercepted it to force a retry."

### 6. How skill definitions/prompts were iterated for reliability
"Initially, agents were too chatty and would break the JSON parser. I iterated the prompts to be highly restrictive, explicitly stating 'Return ONLY a valid JSON object'. I also split the 'thinking' (Analyzer) from the 'talking' (Responder). This separation of concerns made the prompts much easier to tune, as the Analyzer didn't have to worry about tone, and the Responder didn't have to worry about complex reasoning."

### 7. How misleading or wrong outputs were handled
"I implemented a strict thresholding strategy. If the context retrieved from FAISS wasn't relevant, the Analyzer was prompted to set `is_sufficient_context: false`. The Responder was then instructed to explicitly state 'I do not have enough information' rather than hallucinating. Additionally, a hard loop limit (`MAX_TURNS=5`) prevented the system from getting stuck in an infinite retry cycle, ensuring it failed gracefully instead of hanging."

### 8. How repeatability and observability were ensured
"I approached this with a data engineering mindset. I wrote a custom `StructuredJSONFormatter` for Python's logging module. Every incoming request to FastAPI was assigned a UUID `trace_id`. This ID was attached to every log emitted by the LangGraph nodes. In a real environment like Datadog, this means I can filter by `trace_id` and instantly see the exact path the graph took—Supervisor -> Retriever -> Analyzer -> Responder—along with latency at each hop."
