import os
from dotenv import load_dotenv
from crewai import Agent
from app.ai_agents.tools import (
    fetch_project_timeline,
    fetch_project_expenses,
    fetch_team_work_logs,
)
from app.ai_agents.dl_tools import (
    fetch_deep_learning_forecast,
    fetch_revenue_prediction,
    fetch_cashflow_forecast,
    scan_project_anomalies,
)

# Load .env so GROQ_API_KEY is available in os.environ for LiteLLM
load_dotenv()

# Groq model — blazing fast, generous limits
GROQ_MODEL = "groq/llama-3.3-70b-versatile"


# 1. Project Agent
project_agent = Agent(
    role="Project Knowledge Architect",
    goal=("Retrieve, analyze, and structure complex "
          "project timelines, tasks, and resource allocation."),
    backstory=("You are a seasoned Project Manager capable "
               "of understanding project phases. You collaborate openly with "
               "the Finance Intelligence Analyst to ensure they have the "
               "full scope."),
    verbose=True,
    allow_delegation=True,
    tools=[fetch_project_timeline, fetch_team_work_logs],
    llm=GROQ_MODEL
)

# 2. Finance Agent
finance_agent = Agent(
    role="Finance Intelligence Analyst",
    goal=("Calculate and track budgets, expenses, "
          "burn rate, and ROI for projects."),
    backstory=("You are an expert financial analyst who looks "
               "closely at the numbers. You regularly ask the Project "
               "Manager for clarifications on timeline implications."),
    verbose=True,
    allow_delegation=True,
    tools=[fetch_project_expenses, scan_project_anomalies],
    llm=GROQ_MODEL
)

# 3. Forecast Agent (The Deep Learning Bridge)
forecast_agent = Agent(
    role="Predictive Forecasting Agent",
    goal=("Analyze historical spending and deep learning "
          "predictive models to forecast budget overruns."),
    backstory=("You combine financial data with advanced neural "
               "network patterns to predict future expenses. You "
               "critically review inputs from both the Project and "
               "Finance agents."),
    verbose=True,
    allow_delegation=True,
    tools=[
        fetch_deep_learning_forecast,
        fetch_revenue_prediction,
        fetch_cashflow_forecast,
    ],
    llm=GROQ_MODEL
)

# 4. Summary Executive Agent
summary_agent = Agent(
    role="Executive Summary Communicator",
    goal=("Synthesize project structure, financial metrics, "
          "and predictive forecasts into a clear, concise "
          "executive report."),
    backstory=("You are an Executive Assistant to the CTO. "
               "You take highly technical financial outputs and "
               "translate them into actionable insights for "
               "C-level executives."),
    verbose=True,
    allow_delegation=False,
    llm=GROQ_MODEL
)
