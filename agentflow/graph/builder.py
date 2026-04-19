from langgraph.graph import StateGraph, END
from langchain_core.language_models import BaseChatModel
from agentflow.state.workflow_state import WorkflowState, create_initial_state
from agentflow.nodes.supervisor import supervisor_node
from agentflow.nodes.retriever import retriever_node
from agentflow.nodes.analyzer import analyzer_node
from agentflow.nodes.responder import responder_node
from agentflow.routing.router import route_from_supervisor
from agentflow.guardrails.validators import apply_guardrails

def build_agent_graph(llm: BaseChatModel):
    """
    Compiles the Multi-Agent RAG graph.
    """
    workflow = StateGraph(WorkflowState)
    
    # Add Nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("retriever", retriever_node)
    
    # Wrap LLM-dependent nodes
    workflow.add_node("analyzer", lambda state: analyzer_node(state, llm))
    workflow.add_node("guardrails", apply_guardrails)
    workflow.add_node("responder", lambda state: responder_node(state, llm))
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Define edges
    # Supervisor routes to nodes
    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "retriever": "retriever",
            "analyzer": "analyzer",
            "responder": "responder",
            "end": END
        }
    )
    
    # Standard linear path back to supervisor
    workflow.add_edge("retriever", "supervisor")
    
    # Analyzer goes through guardrails first
    workflow.add_edge("analyzer", "guardrails")
    workflow.add_edge("guardrails", "supervisor")
    
    workflow.add_edge("responder", "supervisor")
    
    # Compile graph
    return workflow.compile()
