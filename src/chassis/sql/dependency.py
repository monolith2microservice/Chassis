from .database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

# Database #########################################################################################
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Generates database sessions and closes them when finished."""
    async with SessionLocal() as db:
        try:
            yield db
            await db.commit()
        except:
            await db.rollback()
            raise
        finally:
            await db.close()
