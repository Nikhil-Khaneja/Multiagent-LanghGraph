from typing import Dict, Any
from agentflow.state.workflow_state import WorkflowState
import logging

logger = logging.getLogger(__name__)

def supervisor_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Supervisor Node: Updates the state and logs the current flow.
    The routing decision is made in the router logic.
    """
    logger.info("NODE: SUPERVISOR")
    
    turn_count = state.get("turn_count", 0)
    logger.info(f"Current Turn Count: {turn_count}")
    
    # Just update the current node. The Router will decide next steps.
    return {
        "current_node": "supervisor",
        "turn_count": turn_count + 1
    }
