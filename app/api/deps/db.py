from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
#dependency
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session