from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
