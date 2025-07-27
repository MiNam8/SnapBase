from sqlalchemy import select
from src.db.models import Chapter
from sqlalchemy.orm import selectinload
from src.db.models import Textbook, async_session

async def get_accepted_with_textbook(chapter_id: int):
        async with async_session() as session:
                result = await session.execute(
                select(Chapter)
                .options(selectinload(Chapter.textbook))
                .where(Chapter.id == chapter_id, Chapter.status == "accepted")
                )
                return result.scalar_one_or_none()

async def get_accepted_with_name_and_id(session, textbook_id: int, chapter_name: str):
        result = await session.execute(
            select(Chapter).where(Chapter.textbook_id == textbook_id, Chapter.name == chapter_name, Chapter.status == "accepted")
        )
        return result.scalar_one_or_none()

# async def chapter_exists_by_name(chapter_name: str) -> Chapter:
#         async with async_session() as session:
#                 result = await session.execute(select(Chapter).where(Chapter.name == chapter_name))
#                 return result.scalar_one_or_none()


async def create_chapter(name: str, textbook_id: int, status: str) -> Chapter:
        async with async_session() as session:
                chapter = Chapter(name = name, textbook_id = textbook_id, status = status)
                session.add(chapter)
                await session.commit()
                await session.refresh(chapter)
                return chapter
        
async def check_chapter_name_for_textbook(textbook_id: int, chapter_name: str) -> Chapter:
        async with async_session() as session:
                result = await session.execute(
                        select(Chapter)
                        .where(Chapter.textbook_id == textbook_id, Chapter.name == chapter_name)
                )
                return result.scalar_one_or_none()