from typing import TypedDict, Dict, Any, List, Optional
import operator
from typing import Annotated

class WorkflowState(TypedDict):
    """
    Shared state for the multi-agent workflow.
    This structure flows through the LangGraph execution.
    """
    
    # Input
    query: str
    session_id: str
    
    # RAG Context
    retrieved_context: List[Dict[str, Any]]
    
    # Agent Outputs
    analysis_findings: Dict[str, Any]
    final_response: str
    
    # Guardrails & Validation
    is_valid: bool
    validation_errors: List[str]
    confidence_score: float
    
    # Workflow Control
    current_node: str
    turn_count: int
    error: Optional[str]
    
def create_initial_state(query: str, session_id: str) -> WorkflowState:
    """Helper to initialize the state."""
    return WorkflowState(
        query=query,
        session_id=session_id,
        retrieved_context=[],
        analysis_findings={},
        final_response="",
        is_valid=True,
        validation_errors=[],
        confidence_score=1.0,
        current_node="supervisor",
        turn_count=0,
        error=None
    )
