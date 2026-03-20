from typing import Dict, Any
from agentflow.state.workflow_state import WorkflowState
from agentflow.memory.vector_store import vector_store_manager
import logging

logger = logging.getLogger(__name__)

def retriever_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Queries the vector store based on the user's input query.
    Returns the top matching context chunks.
    """
    logger.info(f"NODE: RETRIEVER | Query: {state['query']}")
    
    try:
        # Retrieve documents from FAISS
        results = vector_store_manager.retrieve(state["query"], top_k=3, score_threshold=1.5)
        
        return {
            "retrieved_context": results,
            "current_node": "retriever",
            "turn_count": state["turn_count"] + 1
        }
    except Exception as e:
        logger.error(f"Error in retriever node: {str(e)}")
        return {
            "error": str(e),
            "current_node": "retriever",
            "turn_count": state["turn_count"] + 1
        }
