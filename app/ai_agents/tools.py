import os
from langchain_community.utilities.sql_database import SQLDatabase
from crewai.tools import tool
from config import settings

# Langchain SQLDatabase requires a sync connection string.
# Since our DATABASE_URL is an asyncpg string, we modify it to standard postgresql.
sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
db = SQLDatabase.from_uri(sync_db_url)

@tool
def fetch_project_timeline(project_name: str) -> str:
    """
    Fetch the overall project details, timeline, risk score, and total budget for a given project name.
    Useful for understanding the scope of a project before calculating complex financials.
    If project_name is missing or 'all', it returns a summary of all active projects.
    """
    try:
        if project_name.lower() in ["all", "any", "none", ""]:
            query = "SELECT id, name, budget, risk_score FROM projects LIMIT 10;"
        else:
            query = f"SELECT id, name, budget, expenditure, risk_score FROM projects WHERE name ILIKE '%{project_name}%';"
        
        result = db.run(query)
        if not result or result == "[]":
             return f"No projects found matching '{project_name}'. Please verify the name in the database."
        return f"Project Master Record: {result}"
    except Exception as e:
        return f"Database Error encountered fetching project details: {str(e)}"

@tool
def fetch_project_expenses(project_id: int) -> str:
    """
    Fetch all detailed hard expenses (category, amount, anomalies) linked to a specific project.
    Always use fetch_project_timeline first to find the correct project_id!
    """
    try:
        query = f"SELECT category, amount, flagged_anomaly FROM expenses WHERE project_id = {project_id};"
        result = db.run(query)
        if not result or result == "[]":
             return f"No expenses found for project ID {project_id}."
        return f"Expense Ledger Records: {result}"
    except Exception as e:
        return f"Database Error tracking expenses: {str(e)}"
        
@tool
def fetch_team_work_logs(project_id: int) -> str:
    """
    Fetch employee time logs and calculated contribution value for a project.
    Determines how much labor cost is burning the budget.
    Always use fetch_project_timeline first to find the correct project_id!
    """
    try:
        query = f"SELECT e.name, e.role, w.hours, w.contribution_value FROM work_logs w JOIN employees e ON w.employee_id = e.id WHERE w.project_id = {project_id};"
        result = db.run(query)
        if not result or result == "[]":
             return f"No employee work logs found for project ID {project_id}."
        return f"Labor and Contribution Ledger: {result}"
    except Exception as e:
        return f"Database Error checking work logs: {str(e)}"
