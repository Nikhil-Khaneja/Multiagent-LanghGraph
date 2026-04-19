import json
from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from agentflow.state.workflow_state import WorkflowState
import logging

logger = logging.getLogger(__name__)

def get_analyzer_prompt(query: str, context: list) -> str:
    context_str = "\n".join([f"Source ({c['metadata'].get('source_id', 'unknown')}): {c['content']}" for c in context])
    return f"""
    You are an expert technical analysis agent.
    Analyze the following user query based on the retrieved context.
    
    Query: {query}
    
    Retrieved Context:
    {context_str if context else "No context found."}
    
    Extract key technical findings and structured information.
    Return ONLY a valid JSON object with the following schema:
    {{
        "key_points": ["point 1", "point 2"],
        "is_sufficient_context": true/false,
        "missing_information": "description of what is missing, if any",
        "confidence_score": 0.0-1.0
    }}
    """

def analyzer_node(state: WorkflowState, llm: BaseChatModel) -> Dict[str, Any]:
    """
    Analyzes the query and retrieved context to produce structured findings.
    """
    logger.info("NODE: ANALYZER")
    
    try:
        prompt = get_analyzer_prompt(state["query"], state.get("retrieved_context", []))
        response = llm.invoke(prompt)
        
        # Parse JSON
        import re
        content = response.content
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        
        if json_match:
            findings = json.loads(json_match.group())
        else:
            findings = {
                "key_points": ["Failed to parse findings"],
                "is_sufficient_context": False,
                "missing_information": "JSON parsing failed",
                "confidence_score": 0.0
            }
            
        return {
            "analysis_findings": findings,
            "confidence_score": findings.get("confidence_score", 0.0),
            "current_node": "analyzer",
            "turn_count": state["turn_count"] + 1
        }
        
    except Exception as e:
        logger.error(f"Error in analyzer node: {str(e)}")
        return {
            "error": str(e),
            "current_node": "analyzer",
            "turn_count": state["turn_count"] + 1
        }
