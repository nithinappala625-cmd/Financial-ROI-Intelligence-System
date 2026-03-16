"""
Standalone Neon PostgreSQL Database Connection Proof.
This script directly queries the live Neon DB to prove our tools work.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(override=True)

from config import settings
from langchain_community.utilities.sql_database import SQLDatabase

# Build sync connection string
sync_db_url = settings.DATABASE_URL.replace(
    "postgresql+asyncpg://", "postgresql://"
)
print(f"Connecting to: {sync_db_url[:40]}...")

try:
    db = SQLDatabase.from_uri(sync_db_url)
    print("✅ Connected to Neon PostgreSQL successfully!\n")

    # 1. List all tables
    tables = db.get_usable_table_names()
    print(f"📋 Tables found in Neon DB: {tables}\n")

    # 2. Query projects table
    print("--- Querying 'projects' table ---")
    result = db.run("SELECT id, name, budget, risk_score FROM projects LIMIT 5;")
    print(f"📊 Projects: {result}\n")

    # 3. Query expenses table
    print("--- Querying 'expenses' table ---")
    result = db.run("SELECT id, project_id, category, amount FROM expenses LIMIT 5;")
    print(f"💰 Expenses: {result}\n")

    # 4. Query employees table
    print("--- Querying 'employees' table ---")
    result = db.run("SELECT id, name, role FROM employees LIMIT 5;")
    print(f"👥 Employees: {result}\n")

    # 5. Query work_logs table
    print("--- Querying 'work_logs' table ---")
    result = db.run("SELECT id, project_id, employee_id, hours FROM work_logs LIMIT 5;")
    print(f"⏱️ Work Logs: {result}\n")

    print("=" * 60)
    print("✅ ALL DATABASE QUERIES SUCCESSFUL - NEON DB IS LIVE!")
    print("=" * 60)

except Exception as e:
    print(f"❌ Database Connection Error: {e}")
