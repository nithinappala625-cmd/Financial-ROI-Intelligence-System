import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from config import settings
from sqlalchemy import text

async def clear_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        print("Dropping all schemas...")
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        print("Database totally cleared.")

if __name__ == "__main__":
    asyncio.run(clear_db())
