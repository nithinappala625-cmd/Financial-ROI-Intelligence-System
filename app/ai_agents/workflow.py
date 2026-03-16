from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from crewai import Crew, Process
from app.ai_agents.agents import project_agent, finance_agent, forecast_agent, summary_agent
from app.ai_agents.tasks import create_tasks

# Define the Graph State
class AgentState(TypedDict):
    query: str
    intermediate_result: Optional[str]
    final_response: Optional[str]

def crewai_node(state: AgentState):
    """
    This node triggers the multi-agent CrewAI process.
    It takes the query from the state, runs it through the agents, and stores the result.
    """
    query = state["query"]
    tasks = create_tasks(query)
    
    # Initialize the crew
    financial_crew = Crew(
        agents=[project_agent, finance_agent, forecast_agent, summary_agent],
        tasks=tasks,
        process=Process.sequential, # Execute tasks sequentially
        verbose=True
    )
    
    # Run the crew
    result = financial_crew.kickoff()
    state["final_response"] = result.raw if hasattr(result, "raw") else str(result)
    return state

# Build the LangGraph
workflow = StateGraph(AgentState)

# Add node
workflow.add_node("crewai_execution", crewai_node)

# Add edges - straightforward execution
workflow.set_entry_point("crewai_execution")
workflow.add_edge("crewai_execution", END)

# Compile the graph
agent_app = workflow.compile()

def process_query_agentic(query: str):
    """Entry point to process a query using the agentic system."""
    initial_state = {"query": query, "intermediate_result": None, "final_response": None}
    
    # Run the subgraph
    result_state = agent_app.invoke(initial_state)
    return result_state["final_response"]
