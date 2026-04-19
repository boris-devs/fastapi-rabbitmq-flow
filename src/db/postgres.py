from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config.settings import settings

ASYNC_POSTGRES_URL = settings.POSTGRES_DATABASE_URL.replace("postgresql", "postgresql+asyncpg")

async_postgres_engine = create_async_engine(ASYNC_POSTGRES_URL, echo=True)

AsyncSessionLocal = sessionmaker(  # NOQA
    bind=async_postgres_engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession
)


async def get_async_postgres_session():
    async with AsyncSessionLocal() as session:
        yield session
