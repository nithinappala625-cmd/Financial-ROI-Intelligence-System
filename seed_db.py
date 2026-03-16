import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings
from app.models.project import Project
from app.models.expense import Expense
from app.models.employee import Employee
from app.models.work_log import WorkLog

async def seed_data():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        print("Seeding database...")
        # Check if project Alpha exists
        from sqlalchemy import select
        result = await session.execute(select(Project).filter_by(name="Project Alpha"))
        project = result.scalars().first()
        
        if not project:
            print("Adding Project Alpha...")
            project = Project(
                name="Project Alpha",
                budget=500000.0,
                expenditure=200000.0,
                risk_score=0.25
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)
            
            print(f"Added Project Alpha with ID: {project.id}")
            
            # Add some expenses
            expense1 = Expense(project_id=project.id, category="Software", amount=50000.0)
            expense2 = Expense(project_id=project.id, category="Hardware", amount=150000.0)
            session.add_all([expense1, expense2])
            
            # Add employees
            emp1 = Employee(name="Alice Smith", role="Lead Developer")
            emp2 = Employee(name="Bob Jones", role="Data Scientist")
            session.add_all([emp1, emp2])
            await session.commit()
            
            print("Database seeded with sample data!")
        else:
            print("Project Alpha already exists in the database.")

if __name__ == "__main__":
    asyncio.run(seed_data())
