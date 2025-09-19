from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import NullPool

from app.core.config import settings

#to specify echo True, will  enable us see generated queries in the console
#echo=settings.DEBUG

engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    #poolclass=NullPool
    )

#expire_on_commit=True, will make sqlalchemy not to issue queries when accessing commited objects
engine.dispose()
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)