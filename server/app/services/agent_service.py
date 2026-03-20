import time
import uuid
from typing import Dict, Any, AsyncGenerator
from langchain_openai import ChatOpenAI
from agentflow.graph.builder import build_agent_graph
from agentflow.state.workflow_state import create_initial_state
from server.app.observability.logger import logger
from server.app.observability.metrics import metrics_collector
import os

class AgentService:
    def __init__(self):
        # We assume OPENAI_API_KEY is set in environment for this example
        # Alternatively we could use ChatGroq if GROQ_API_KEY is provided
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.graph = build_agent_graph(llm)

    async def execute_query(self, query: str) -> Dict[str, Any]:
        """Executes the workflow graph synchronously and returns the final state."""
        session_id = str(uuid.uuid4())
        logger.info(f"Starting workflow for query: {query}", extra={"trace_id": session_id})
        
        state = create_initial_state(query, session_id)
        start_time = time.time()
        success = False
        
        try:
            # Run the graph
            final_state = self.graph.invoke(state)
            success = True
            
            latency = (time.time() - start_time) * 1000
            metrics_collector.record_request(success=True, latency_ms=latency)
            
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}", extra={"trace_id": session_id})
            latency = (time.time() - start_time) * 1000
            metrics_collector.record_request(success=False, latency_ms=latency)
            raise e

    async def stream_query(self, query: str) -> AsyncGenerator[str, None]:
        """Streams state updates from the workflow graph as JSON strings."""
        session_id = str(uuid.uuid4())
        logger.info(f"Starting stream workflow for query: {query}", extra={"trace_id": session_id})
        
        state = create_initial_state(query, session_id)
        start_time = time.time()
        
        try:
            # Stream the graph execution events
            # For langgraph, .astream() yields tuples or dicts representing node updates
            for event in self.graph.stream(state):
                # event is typically a dict mapping node_name -> state_update
                import json
                yield f"data: {json.dumps(event)}\n\n"
                
            latency = (time.time() - start_time) * 1000
            metrics_collector.record_request(success=True, latency_ms=latency)
            
        except Exception as e:
            logger.error(f"Stream workflow failed: {str(e)}", extra={"trace_id": session_id})
            latency = (time.time() - start_time) * 1000
            metrics_collector.record_request(success=False, latency_ms=latency)
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

agent_service = AgentService()
