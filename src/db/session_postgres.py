from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings

postgres_url = settings.postgres_database_url
ASYNC_POSTGRES_URL = postgres_url.replace("postgresql", "postgresql+asyncpg")

async_postgres_engine = create_async_engine(ASYNC_POSTGRES_URL, echo=True)

AsyncSessionLocal = sessionmaker(  # NOQA
    bind=async_postgres_engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession
)

sync_postgres_engine = create_engine(postgres_url, echo=False)

async def get_async_postgres_session():
    async with AsyncSessionLocal() as session:
        yield session
