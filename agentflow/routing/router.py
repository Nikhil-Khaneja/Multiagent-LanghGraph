import logging
from agentflow.state.workflow_state import WorkflowState

logger = logging.getLogger(__name__)

MAX_TURNS = 5

def route_from_supervisor(state: WorkflowState) -> str:
    """
    Decides the next node from the supervisor's perspective.
    """
    logger.info("ROUTING from Supervisor...")
    
    turn_count = state.get("turn_count", 0)
    
    if turn_count >= MAX_TURNS:
        logger.warning(f"Max turns ({MAX_TURNS}) reached. Ending graph.")
        return "end"
        
    if state.get("error"):
        logger.error(f"Error detected in state: {state['error']}. Ending graph.")
        return "end"
        
    # If we haven't retrieved context yet
    if not state.get("retrieved_context"):
        return "retriever"
        
    # If we retrieved context, but haven't analyzed it
    if not state.get("analysis_findings"):
        return "analyzer"
        
    # If we analyzed, but validation failed (guardrails)
    if not state.get("is_valid", True):
        logger.warning("Validation failed. Routing back to Analyzer for retry.")
        return "analyzer"
        
    # If analysis is valid and we haven't responded
    if not state.get("final_response"):
        return "responder"
        
    return "end"
