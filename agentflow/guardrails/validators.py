from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

def validate_analyzer_output(findings: Dict[str, Any]) -> Tuple[bool, list]:
    """
    Validates that the analyzer output matches the required JSON schema
    and contains sufficient confidence.
    """
    errors = []
    is_valid = True
    
    if not isinstance(findings, dict):
        return False, ["Output is not a valid JSON dictionary."]
        
    required_keys = ["key_points", "is_sufficient_context", "missing_information", "confidence_score"]
    
    for key in required_keys:
        if key not in findings:
            errors.append(f"Missing required key: {key}")
            is_valid = False
            
    # Check confidence threshold if it exists
    if is_valid:
        score = findings.get("confidence_score", 0.0)
        try:
            score = float(score)
            if score < 0.3: # Arbitrary strictness threshold
                errors.append(f"Confidence score {score} is below threshold 0.3")
                is_valid = False
        except ValueError:
            errors.append("confidence_score must be a float")
            is_valid = False
            
    return is_valid, errors

def apply_guardrails(state: dict) -> dict:
    """
    Applies guardrails to the current state.
    Designed to run as a node right after Analyzer.
    """
    logger.info("Applying Guardrails...")
    findings = state.get("analysis_findings", {})
    
    is_valid, errors = validate_analyzer_output(findings)
    
    if not is_valid:
        logger.warning(f"Guardrail validation failed: {errors}")
        
    return {
        "is_valid": is_valid,
        "validation_errors": errors
    }
