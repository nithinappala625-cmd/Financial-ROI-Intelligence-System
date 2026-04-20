import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings
from sqlalchemy import text

async def seed_data():
    engine = create_async_engine(settings.DATABASE_URL, echo=True, connect_args={"server_settings": {"search_path": "public"}})
    
    async with engine.begin() as conn:
        print("Seeding database...")
        # Check if project Alpha exists
        result = await conn.execute(text("SELECT id FROM public.projects WHERE name='Project Alpha'"))
        project_id = result.scalar()
        
        if not project_id:
            print("Adding Project Alpha...")
            res = await conn.execute(text("""
                INSERT INTO public.projects (name, budget, expenditure, revenue, risk_score) 
                VALUES ('Project Alpha', 500000.0, 200000.0, 0, 0.25)
                RETURNING id
            """))
            project_id = res.scalar()
            print(f"Added Project Alpha with ID: {project_id}")
            
            # Add some expenses
            await conn.execute(text(f"""
                INSERT INTO public.expenses (project_id, category, amount, flagged_anomaly) 
                VALUES ({project_id}, 'Software', 50000.0, false)
            """))
            await conn.execute(text(f"""
                INSERT INTO public.expenses (project_id, category, amount, flagged_anomaly) 
                VALUES ({project_id}, 'Hardware', 150000.0, false)
            """))
            
            # Add employees
            await conn.execute(text("""
                INSERT INTO public.employees (name, role, salary) 
                VALUES ('Alice Smith', 'Lead Developer', 0)
            """))
            await conn.execute(text("""
                INSERT INTO public.employees (name, role, salary) 
                VALUES ('Bob Jones', 'Data Scientist', 0)
            """))
            
            print("Database seeded with sample data!")
        else:
            print("Project Alpha already exists in the database.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_data())
