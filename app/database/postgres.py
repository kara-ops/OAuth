from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker,declarative_base
from app.core.config import settings

# Ensure the URL uses the asyncpg driver for async SQLAlchemy.
# Render provides "postgresql://" or "postgres://" but we need "postgresql+asyncpg://".
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, echo=False, pool_size=20, max_overflow=20, pool_timeout=30)
AsyncSessionlocal = sessionmaker(bind=engine, class_=AsyncSession, autoflush = False, autocommit = False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionlocal() as session:
        yield session
