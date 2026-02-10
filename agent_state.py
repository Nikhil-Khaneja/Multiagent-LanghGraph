# ========================================
# PART 3: STATEFUL AGENT GRAPH
# LangGraph Supervisor Pattern Implementation
# ========================================

from typing import TypedDict, Dict, Any

# ========================================
# STEP 2: DEFINE AGENT STATE
# ========================================

class AgentState(TypedDict):
    """
    Shared state dictionary that acts as the "memory" for all agents.
    Every agent can read from and write to this central state.
    
    This TypedDict defines the structure of data flowing through the graph.
    """
    
    # Initial Inputs
    title: str                          # Book title input
    content: str                        # Book content/description input
    email: str                          # User email input
    strict: bool                        # Whether to use strict mode
    task: str                           # Current task being executed
    
    # LLM Reference
    llm: Any                            # Language model instance
    
    # Agent Outputs
    planner_proposal: Dict[str, Any]   # Output from Planner agent
                                        # Contains: title, content, suggestions
    
    reviewer_feedback: Dict[str, Any]  # Output from Reviewer agent
                                        # Contains: issues, suggestions, approved
    
    # Control Flow
    turn_count: int                     # Counter to prevent infinite loops
                                        # Increments with each turn
                                        # Helps implement max iteration limit


# ========================================
# EXPLANATION OF AGENTSTATE FIELDS
# ========================================

"""
INPUT FIELDS (set at the beginning):
- title: The book title provided by user
- content: The book content/description provided by user
- email: User's email address for feedback
- strict: Boolean flag to determine strictness of review
- task: Description of what needs to be done

LLM FIELD:
- llm: Language model instance used by agents for processing
       (e.g., GPT-4, Claude, etc.)

AGENT OUTPUT FIELDS:
- planner_proposal: Contains the planner's proposal
  Structure: {
    "title": str,
    "content": str,
    "suggestions": List[str]
  }

- reviewer_feedback: Contains the reviewer's analysis
  Structure: {
    "issues": List[str],
    "suggestions": List[str],
    "approved": bool
  }

CONTROL FLOW FIELD:
- turn_count: Prevents infinite loops
  - Starts at 0
  - Increments after each agent turn
  - Used to set max iterations (e.g., max_turns=5)
  - If turn_count >= max_turns, graph ends
"""


# ========================================
# STATE INITIALIZATION HELPER
# ========================================

def create_initial_state(
    title: str,
    content: str,
    email: str,
    strict: bool,
    task: str,
    llm: Any
) -> AgentState:
    """
    Create an initial AgentState for a new workflow.
    
    Args:
        title: Book title
        content: Book content
        email: User email
        strict: Strict mode flag
        task: Task description
        llm: Language model instance
    
    Returns:
        AgentState: Initial state ready for graph execution
    """
    return AgentState(
        title=title,
        content=content,
        email=email,
        strict=strict,
        task=task,
        llm=llm,
        planner_proposal={},           # Empty initially
        reviewer_feedback={},          # Empty initially
        turn_count=0                   # Start at 0
    )


# ========================================
# EXAMPLE USAGE
# ========================================

"""
# When you have your LLM model:
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")

# Create initial state
state = create_initial_state(
    title="The Great Gatsby",
    content="A novel about the American Dream...",
    email="user@example.com",
    strict=True,
    task="Review and enhance the book description",
    llm=llm
)

# Now this state can be passed through the graph:
# - Supervisor reads it
# - Routes to Planner or Reviewer
# - Agent updates state with their output
# - Next agent receives updated state
# - Process continues until completion
"""
