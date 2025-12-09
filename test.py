import asyncio
from core.db import init_db

async def main():
    await init_db()
    print("Tables created successfully!")

asyncio.run(main())