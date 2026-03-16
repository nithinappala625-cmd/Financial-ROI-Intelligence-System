from crewai import Task
from app.ai_agents.agents import project_agent, finance_agent, forecast_agent, summary_agent

def create_tasks(query: str):
    task1 = Task(
        description=f"Extract project requirements or knowledge requested in the user query: '{query}'. Provide detailed project scope.",
        expected_output="A structured summary of project status, timeline, or requested project info.",
        agent=project_agent
    )

    task2 = Task(
        description=f"Using the project context and user query: '{query}', calculate or extract the financial situation (budget, ROI, burn rate).",
        expected_output="A quantitative financial breakdown relating to the project.",
        agent=finance_agent,
        context=[task1] # Force communication with task1 output
    )
    
    task3 = Task(
        description=f"Analyze the financial outputs and user query '{query}'. Apply predictive insights on what will happen next (e.g., budget overrun risk).",
        expected_output="A forward-looking forecast or risk assessment.",
        agent=forecast_agent,
        context=[task1, task2] # Require data from both previous task agents
    )

    task4 = Task(
        description="Take the outputs from the Project, Finance, and Forecast agents, and combine them into a single, cohesive human-readable response that answers the user's original query.",
        expected_output="Final user-facing comprehensive report answering the query.",
        agent=summary_agent,
        context=[task1, task2, task3] # Final synthesis of the conversation
    )
    
    return [task1, task2, task3, task4]
