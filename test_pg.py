import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import settings

async def check_data():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT id, name, budget FROM public.projects"))
        rows = res.fetchall()
        print("ROWS IN PROJECTS:", rows)

if __name__ == "__main__":
    asyncio.run(check_data())
