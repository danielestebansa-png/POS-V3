# ============================================
# DATABASE CONNECTION - SQLAlchemy
# ============================================

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Auto-detectar driver desde la URL
db_url = settings.DATABASE_URL
if "+asyncpg" in db_url:
    async_driver = "postgresql+asyncpg"
elif "+psycopg2" in db_url:
    async_driver = "postgresql+psycopg2"
else:
    async_driver = "postgresql+asyncpg"

# Async engine (for FastAPI)
async_engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    future=True
)

# Sync engine (for scripts/migrations)
sync_url = settings.DATABASE_URL_SYNC.replace("postgresql://", "postgresql+psycopg2://")
sync_engine = create_engine(
    sync_url,
    echo=settings.DEBUG
)

# Session factories - SQLAlchemy 2.x
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# Base para modelos
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
