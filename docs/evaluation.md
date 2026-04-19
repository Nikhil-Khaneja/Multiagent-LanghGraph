# Evaluation & Observability

## Metrics Collected
The `MetricsCollector` in `server/app/observability/metrics.py` captures:
- **Total Requests**: Throughput volume.
- **Success Rate**: % of workflows that complete without unhandled exceptions.
- **Average Latency**: End-to-end execution time (ms).
- **Ingestion Volume**: Number of documents processed via the Kafka adapter.

## Logging Strategy
We use `StructuredJSONFormatter` to ensure all logs are output as parseable JSON.
Each workflow request is assigned a UUID `trace_id` at the FastAPI boundary. This ID is injected into the logger's `extra` dictionary, ensuring that every node's log statements can be correlated back to the original request in Datadog/Splunk.

## Evaluation Limitations
- We currently do not run automated "LLM-as-a-judge" evaluations.
- Retrieval precision/recall is not benchmarked against a golden dataset in this repository.
- To implement true continuous evaluation, we would need to capture user thumbs-up/thumbs-down signals in the frontend and write them to an eval database.
