from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_session() -> AsyncSession:
    """Dependency for FastAPI: get async DB session."""
    async with AsyncSessionLocal() as session:
        yield session

class BaseModel(Base):
    """Base model class for ORM models."""
    __abstract__ = True

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
