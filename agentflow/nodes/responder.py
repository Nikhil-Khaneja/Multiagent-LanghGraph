from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from agentflow.state.workflow_state import WorkflowState
import logging

logger = logging.getLogger(__name__)

def get_responder_prompt(query: str, findings: dict) -> str:
    return f"""
    You are an expert technical responder agent.
    Synthesize the analytical findings into a clear, concise final response for the user.
    
    User Query: {query}
    
    Analytical Findings:
    - Key Points: {findings.get('key_points', [])}
    - Sufficient Context: {findings.get('is_sufficient_context', False)}
    - Missing Info: {findings.get('missing_information', 'None')}
    
    Draft a final response that directly answers the user's query. If context is insufficient, state that clearly.
    """

def responder_node(state: WorkflowState, llm: BaseChatModel) -> Dict[str, Any]:
    """
    Synthesizes the final output using the analysis findings.
    """
    logger.info("NODE: RESPONDER")
    
    try:
        findings = state.get("analysis_findings", {})
        prompt = get_responder_prompt(state["query"], findings)
        
        response = llm.invoke(prompt)
        
        return {
            "final_response": response.content,
            "current_node": "responder",
            "turn_count": state["turn_count"] + 1
        }
        
    except Exception as e:
        logger.error(f"Error in responder node: {str(e)}")
        return {
            "error": str(e),
            "current_node": "responder",
            "turn_count": state["turn_count"] + 1
        }
