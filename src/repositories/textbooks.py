from src.db.models import Textbook, async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_accepted_textbook_by_id(textbook_id: int) -> Textbook:
    async with async_session() as session:
            result = await session.execute(
                select(Textbook).where(Textbook.id == textbook_id,
                                    Textbook.status == "accepted")
            )
            textbook = result.scalar_one()
            return textbook


async def exists_by_name(session, name: str) -> bool:
        result = await session.execute(select(Textbook).where(Textbook.name == name))
        return result.scalar_one_or_none() is not None


async def create_textbook(name: str, status: str) -> Textbook:
        async with async_session() as session:
                textbook = Textbook(name=name, status=status)
                session.add(textbook)
                await session.commit()
                await session.refresh(textbook)
                return textbook