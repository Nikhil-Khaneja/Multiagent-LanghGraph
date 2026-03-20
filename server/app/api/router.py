from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import uuid
import time
from server.app.schemas.api_models import QueryRequest, QueryResponse, IngestRequest
from server.app.services.agent_service import agent_service
from server.app.observability.metrics import metrics_collector
from server.app.ingestion.events import IngestionEvent
from server.app.ingestion.kafka_adapter import kafka_adapter

api_router = APIRouter()

@api_router.post("/query")
async def query_agent(request: QueryRequest):
    """
    Executes the multi-agent workflow. Supports both standard and streaming responses.
    """
    if request.stream:
        return StreamingResponse(
            agent_service.stream_query(request.query),
            media_type="text/event-stream"
        )
    
    try:
        final_state = await agent_service.execute_query(request.query)
        
        return QueryResponse(
            response=final_state.get("final_response", "No response generated"),
            trace_id=final_state.get("session_id", "unknown"),
            confidence_score=final_state.get("confidence_score", 0.0),
            turn_count=final_state.get("turn_count", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/ingest")
async def ingest_document(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Publishes an ingestion event to the Kafka adapter.
    """
    event = IngestionEvent(
        event_id=str(uuid.uuid4()),
        source_id=request.source_id,
        content=request.content,
        author=request.author,
        timestamp=time.time()
    )
    
    # We produce to Kafka (adapter) in the background
    background_tasks.add_task(kafka_adapter.produce, event)
    
    return {"status": "accepted", "event_id": event.event_id}

@api_router.get("/metrics")
def get_metrics():
    """Returns observability metrics."""
    return metrics_collector.get_summary()

@api_router.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
