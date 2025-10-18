# chassis/db.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
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

# ----------------------------
# Generic DB helper functions
# ----------------------------
async def get_list(db: AsyncSession, model):
    """Retrieve a list of elements from database."""
    result = await db.execute(select(model))
    return result.unique().scalars().all()

async def get_list_statement_result(db: AsyncSession, stmt):
    """Execute given statement and return list of items."""
    result = await db.execute(stmt)
    return result.unique().scalars().all()

async def get_element_statement_result(db: AsyncSession, stmt):
    """Execute statement and return a single item."""
    result = await db.execute(stmt)
    return result.scalar()

async def get_element_by_id(db: AsyncSession, model, element_id):
    """Retrieve any DB element by id."""
    if element_id is None:
        return None
    return await db.get(model, element_id)

async def delete_element_by_id(db: AsyncSession, model, element_id):
    """Delete any DB element by id."""
    element = await get_element_by_id(db, model, element_id)
    if element is not None:
        await db.delete(element)
        await db.commit()
    return element
