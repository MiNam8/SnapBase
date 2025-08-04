from sqlalchemy import select
from src.db.models import Chapter
from sqlalchemy.orm import selectinload
from src.db.models import async_session
from typing import List
import logging

logger = logging.getLogger(__name__)

async def get_accepted_with_textbook(chapter_id: int):
        logger.debug("Fetching accepted chapter with id=%s including textbook", chapter_id)
        async with async_session() as session:
                result = await session.execute(
                select(Chapter)
                .options(selectinload(Chapter.textbook))
                .where(Chapter.id == chapter_id, Chapter.status == "accepted")
                )
                chapter = result.scalar_one_or_none()
                if chapter:
                        logger.info("Found accepted chapter with id=%s", chapter_id)
                else:
                        logger.warning("No accepted chapter found with id=%s", chapter_id)
                return chapter

async def get_accepted_with_name_and_id(session, textbook_id: int, chapter_name: str):
        logger.debug("Checking for accepted chapter with name='%s' and textbook_id=%s", chapter_name, textbook_id)
        result = await session.execute(
            select(Chapter).where(Chapter.textbook_id == textbook_id, Chapter.name == chapter_name, Chapter.status == "accepted")
        )
        chapter = result.scalar_one_or_none()
        if chapter:
                logger.info("Found accepted chapter '%s' for textbook_id=%s", chapter_name, textbook_id)
        else:
                logger.warning("No accepted chapter '%s' found for textbook_id=%s", chapter_name, textbook_id)
        return chapter

async def create_chapter(name: str, textbook_id: int, status: str) -> Chapter:
        logger.info("Creating chapter '%s' for textbook_id=%s with status='%s'", name, textbook_id, status)
        async with async_session() as session:
                chapter = Chapter(name = name, textbook_id = textbook_id, status = status)
                session.add(chapter)
                await session.commit()
                await session.refresh(chapter)
                logger.info("Created chapter with id=%s", chapter.id)
                return chapter
        
async def check_chapter_name_for_textbook(textbook_id: int, chapter_name: str) -> Chapter:
        logger.debug("Checking if chapter '%s' exists for textbook_id=%s", chapter_name, textbook_id)
        async with async_session() as session:
                result = await session.execute(
                        select(Chapter)
                        .where(Chapter.textbook_id == textbook_id, Chapter.name == chapter_name)
                )
                chapter = result.scalar_one_or_none()
                if chapter:
                        logger.info("Chapter '%s' already exists for textbook_id=%s", chapter_name, textbook_id)
                else:
                        logger.info("Chapter '%s' does not exist yet for textbook_id=%s", chapter_name, textbook_id)
                return chapter

async def get_accepted_with_textbook_id(textbook_id: int) -> List[Chapter]:
        async with async_session() as session:
                result = await session.execute(
                select(Chapter).where(Chapter.textbook_id == textbook_id, 
                                        Chapter.status == "accepted")
                )
                chapters = result.scalars().all()
                return chapters
        
async def get_chapter_by_id(chapter_id: int) -> Chapter:
        async with async_session() as session:
                chapter_result = await session.execute(
                        select(Chapter).where(Chapter.id == chapter_id)
                )
                return chapter_result.scalar_one()

async def get_all_chapters() -> List[Chapter]:
        async with async_session() as session:
                result = await session.execute(select(Chapter))
                chapters = result.scalars().all()
                return chapters