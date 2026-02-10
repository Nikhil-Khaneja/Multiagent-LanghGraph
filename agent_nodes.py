# ========================================
# PART 3: AGENT NODES
# Node functions for LangGraph execution
# ========================================

from typing import Dict, Any
from agent_state import AgentState
import os
import json

# ========================================
# NODE 1: PLANNER NODE
# ========================================

def planner_node(state: AgentState) -> Dict[str, Any]:
    """
    Planner Node: Creates a proposal for the book.
    
    This node:
    1. Reads the initial book title and content from state
    2. Calls the LLM to generate a structured proposal
    3. Increments turn counter
    4. Returns only the fields it wants to update
    
    Args:
        state: Current AgentState (read-only in this context)
    
    Returns:
        Dict with keys to update: planner_proposal, turn_count
    """
    print("\n" + "="*50)
    print("📋 NODE: PLANNER")
    print("="*50)
    
    # Get input from state
    title = state.get("title", "")
    content = state.get("content", "")
    task = state.get("task", "")
    llm = state.get("llm")
    
    print(f"Input Title: {title}")
    print(f"Input Content: {content[:100]}...")  # First 100 chars
    print(f"Task: {task}")
    
    # ========================================
    # PLANNER LOGIC
    # ========================================
    
    # Create prompt for the planner
    planner_prompt = f"""
You are an expert book planner and editor. Your task is to create a proposal for improving a book.

Current Book Details:
- Title: {title}
- Content: {content}
- Task: {task}

Please analyze this book and create a structured proposal. Return a JSON object with the following structure:
{{
    "title": "improved title if needed",
    "content": "improved content summary",
    "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
    "strengths": ["strength 1", "strength 2"],
    "areas_for_improvement": ["area 1", "area 2"]
}}

Ensure your response is valid JSON that can be parsed.
"""
    
    print("\n🤖 Calling LLM for planning...")
    
    try:
        # Call the LLM
        response = llm.invoke(planner_prompt)
        response_text = response.content
        
        print(f"LLM Response: {response_text[:200]}...")
        
        # Parse JSON from response
        # Extract JSON from response (in case LLM includes extra text)
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            proposal = json.loads(json_match.group())
        else:
            # Fallback if JSON not found
            proposal = {
                "title": title,
                "content": content,
                "suggestions": ["Unable to parse LLM response"],
                "strengths": [],
                "areas_for_improvement": []
            }
        
        print("✅ Planner proposal created successfully")
        
    except Exception as e:
        print(f"❌ Error in planner: {str(e)}")
        proposal = {
            "title": title,
            "content": content,
            "suggestions": [f"Error: {str(e)}"],
            "strengths": [],
            "areas_for_improvement": []
        }
    
    # ========================================
    # RETURN UPDATED STATE
    # ========================================
    
    return {
        "planner_proposal": proposal,
        "turn_count": state.get("turn_count", 0) + 1
    }


# ========================================
# NODE 2: REVIEWER NODE
# ========================================

def reviewer_node(state: AgentState) -> Dict[str, Any]:
    """
    Reviewer Node: Reviews the planner's proposal and provides feedback.
    
    This node:
    1. Reads the planner_proposal from state
    2. Calls the LLM to review and provide detailed feedback
    3. Determines if the proposal is approved or needs revision
    4. Increments turn counter
    5. Returns only the fields it wants to update
    
    Args:
        state: Current AgentState (contains planner_proposal)
    
    Returns:
        Dict with keys to update: reviewer_feedback, turn_count
    """
    print("\n" + "="*50)
    print("👁️ NODE: REVIEWER")
    print("="*50)
    
    # Get inputs from state
    title = state.get("title", "")
    planner_proposal = state.get("planner_proposal", {})
    strict = state.get("strict", False)
    email = state.get("email", "")
    llm = state.get("llm")
    
    print(f"Reviewing proposal for: {title}")
    print(f"Strict Mode: {strict}")
    print(f"User Email: {email}")
    
    # ========================================
    # REVIEWER LOGIC
    # ========================================
    
    # Create prompt for the reviewer
    strictness_instruction = (
        "Be very strict and critical. Require high quality standards."
        if strict
        else "Be balanced and constructive. Accept good proposals."
    )
    
    reviewer_prompt = f"""
You are an expert book reviewer. Your task is to review a book proposal and provide detailed feedback.

Original Title: {title}
Planner's Proposal:
{json.dumps(planner_proposal, indent=2)}

Reviewer Instructions:
{strictness_instruction}

Please analyze this proposal and provide feedback. Return a JSON object with the following structure:
{{
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["suggestion 1", "suggestion 2"],
    "approved": true/false,
    "confidence_score": 0.0-1.0,
    "detailed_feedback": "comprehensive feedback"
}}

Ensure your response is valid JSON that can be parsed.
- "approved" should be true only if the proposal is of high quality
- "confidence_score" indicates how confident you are in your assessment
"""
    
    print("\n🤖 Calling LLM for review...")
    
    # For testing: allow forcing reviewer to always reject via environment variable
    force_reject = os.getenv("FORCE_REJECT", "false").lower() in ("1", "true", "yes")

    if force_reject:
        # Deterministic rejection for testing correction loop
        print("⚠️ FORCE_REJECT is enabled — reviewer will always return an issue for testing.")
        feedback = {
            "issues": ["Test-mode: forced rejection - requires revision"],
            "suggestions": ["Improve opening paragraph", "Clarify character motivations"],
            "approved": False,
            "confidence_score": 0.01,
            "detailed_feedback": "Forced rejection mode enabled. This feedback is synthetic for testing."
        }
        print("❌ Review complete - Approved: False (forced)")
    else:
        try:
            # Call the LLM
            response = llm.invoke(reviewer_prompt)
            response_text = response.content
            
            print(f"LLM Response: {response_text[:200]}...")
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                feedback = json.loads(json_match.group())
            else:
                # Fallback if JSON not found
                feedback = {
                    "issues": ["Unable to parse LLM response"],
                    "suggestions": [],
                    "approved": False,
                    "confidence_score": 0.0,
                    "detailed_feedback": "Could not parse feedback"
                }
            
            approved = feedback.get("approved", False)
            print(f"✅ Review complete - Approved: {approved}")
            
        except Exception as e:
            print(f"❌ Error in reviewer: {str(e)}")
            feedback = {
                "issues": [f"Error: {str(e)}"],
                "suggestions": [],
                "approved": False,
                "confidence_score": 0.0,
                "detailed_feedback": f"Error during review: {str(e)}"
            }
    
    # ========================================
    # RETURN UPDATED STATE
    # ========================================
    
    return {
        "reviewer_feedback": feedback,
        "turn_count": state.get("turn_count", 0) + 1
    }


# ========================================
# NODE 3: SUPERVISOR NODE (Part A - State Update)
# ========================================

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    Supervisor Node: Updates the state and prepares for routing decision.
    
    This node's job is to:
    1. Log current state information
    2. Prepare any state updates needed
    3. Return state updates (not routing decisions)
    
    The actual routing decision is made by router_logic() function.
    
    Args:
        state: Current AgentState
    
    Returns:
        Dict: Updates to state (can be empty if no updates needed)
    """
    print("\n" + "="*50)
    print("🎯 NODE: SUPERVISOR (State Update)")
    print("="*50)
    
    # Get state information for logging
    turn_count = state.get("turn_count", 0)
    planner_proposal = state.get("planner_proposal", {})
    reviewer_feedback = state.get("reviewer_feedback", {})
    
    print(f"📊 Current State:")
    print(f"   - Turn Count: {turn_count}")
    print(f"   - Planner Proposal: {'✅ Created' if planner_proposal else '❌ Not created'}")
    print(f"   - Reviewer Feedback: {'✅ Created' if reviewer_feedback else '❌ Not created'}")
    
    if reviewer_feedback:
        approved = reviewer_feedback.get("approved", False)
        print(f"   - Approval Status: {'✅ APPROVED' if approved else '❌ REJECTED'}")
    
    # Supervisor can make state updates if needed
    # (Usually minimal - main logic is in router_logic)
    # Return empty dict if no updates needed
    return {}


# ========================================
# ROUTING FUNCTION (Part B - Routing Decision)
# ========================================

def router_logic(state: AgentState) -> str:
    """
    Routing Function: Decides which node to execute next based on state.
    
    This function is the "decision-making logic":
    1. Analyzes current state
    2. Determines the best next action
    3. Returns the name of the next node to execute
    
    Routing Logic:
    - If max turns reached → END (prevent infinite loops)
    - If no proposal yet → PLANNER (create initial proposal)
    - If proposal exists but no review → REVIEWER (review the proposal)
    - If reviewed and APPROVED → END (success!)
    - If reviewed and REJECTED → PLANNER (revision loop)
    
    Args:
        state: Current AgentState (read-only)
    
    Returns:
        str: Next node name ("planner", "reviewer", or "end")
    """
    print("\n" + "="*50)
    print("🔀 ROUTING DECISION")
    print("="*50)
    
    # Get state information
    turn_count = state.get("turn_count", 0)
    planner_proposal = state.get("planner_proposal", {})
    reviewer_feedback = state.get("reviewer_feedback", {})
    max_turns = 5  # Maximum iterations to prevent infinite loops
    
    print(f"Turn Count: {turn_count}/{max_turns}")
    
    # ========================================
    # ROUTING DECISION TREE
    # ========================================
    
    # DECISION 1: Check if we've exceeded maximum turns
    if turn_count >= max_turns:
        print(f"⚠️ Max turns ({max_turns}) reached.")
        print("→ Routing to: END (prevent infinite loops)")
        return "end"
    
    # DECISION 2: Check if planner hasn't run yet
    if not planner_proposal:
        print("📋 No proposal yet.")
        print("→ Routing to: PLANNER (create initial proposal)")
        return "planner"
    
    # DECISION 3: Check if reviewer hasn't run yet
    if not reviewer_feedback:
        print("👁️ Proposal exists but not reviewed.")
        print("→ Routing to: REVIEWER (review the proposal)")
        return "reviewer"
    
    # DECISION 4: Check if proposal was approved
    approved = reviewer_feedback.get("approved", False)
    confidence = reviewer_feedback.get("confidence_score", 0)
    
    if approved:
        print(f"✅ Proposal APPROVED (confidence: {confidence:.2f})")
        print("→ Routing to: END (success!)")
        return "end"
    else:
        print(f"❌ Proposal REJECTED (confidence: {confidence:.2f})")
        print("→ Routing to: PLANNER (revision loop)")
        # Note: planner_proposal could be cleared here for fresh start,
        # or kept for context. Currently kept for context.
        return "planner"


# ========================================
# EXPLANATION OF SUPERVISOR PATTERN
# ========================================

"""
SUPERVISOR PATTERN - Two-Part Design:

┌─────────────────────────────────────┐
│ Graph Execution Flow                │
└─────────────────────────────────────┘
         ↓
    [Any Node]
    (Planner/Reviewer/etc)
         ↓
┌─────────────────────────────────────┐
│ 1. supervisor_node()                │
│    - Updates state if needed        │
│    - Logs current state             │
│    - Returns: Dict[str, Any]        │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ 2. router_logic()                   │
│    - Reads state (no modifications) │
│    - Decides next action            │
│    - Returns: str (node name)       │
└─────────────────────────────────────┘
         ↓
    [Route to next node]
    or [END]


WHY SPLIT INTO TWO FUNCTIONS?

1. SEPARATION OF CONCERNS:
   - supervisor_node: Handles state management
   - router_logic: Handles decision logic
   
2. LANGGRAPH INTEGRATION:
   - supervisor_node: Added as a regular node in graph
   - router_logic: Used with conditional_edge in graph
   
3. CLARITY:
   - Each function has a single responsibility
   - Easier to test and debug
   - Cleaner code organization


SUPERVISOR_NODE vs ROUTER_LOGIC:

supervisor_node(state) → Dict[str, Any]
- Modifies AgentState
- Updates fields that need changing
- Always adds state updates to graph
- Example: increment counter, log state
- Return: {"field": new_value}

router_logic(state) → str
- Reads AgentState (no modifications)
- Analyzes current state
- Determines next node name
- Does NOT update state
- Example: "planner", "reviewer", "end"
- Return: "node_name"


ROUTING DECISION TREE:

    ┌─ max_turns >= 5? → "end"
    │
    ├─ no planner_proposal? → "planner"
    │
    ├─ no reviewer_feedback? → "reviewer"
    │
    └─ reviewer feedback exists?
       ├─ approved = true? → "end"
       └─ approved = false? → "planner" (loop)
"""
