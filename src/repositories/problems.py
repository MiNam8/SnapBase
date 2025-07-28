from src.db.models import Problem, Chapter
from src.db.models import async_session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import logging

logger = logging.getLogger(__name__)

async def create_problem(name: str, chapter_id: int, status: str) -> Problem:
        logger.info("Creating problem: name=%s, chapter_id=%d, status=%s", name, chapter_id, status)
        async with async_session() as session:
                problem = Problem(name = name, chapter_id = chapter_id, status = status)
                session.add(problem)
                await session.commit()
                await session.refresh(problem)
                logger.info("Problem created with id=%d", problem.id)
                return problem


async def fetch_problem_with_chapter_and_textbook(problem_id: int) -> Problem:
        logger.info("Fetching problem with chapter and textbook for problem_id=%d", problem_id)
        async with async_session() as session:
                result = await session.execute(
                select(Problem).options(
                        selectinload(Problem.chapter).selectinload(Chapter.textbook)
                ).where(Problem.id == problem_id,
                        Problem.status == "accepted")
                )
                problem = result.scalar_one()
                logger.debug("Fetched problem: name=%s, chapter_id=%d", problem.name, problem.chapter_id)
                return problem
        
async def problem_exists_for_chapter(chapter_id: int, problem_name: str) -> bool: 
        logger.info("Checking if problem exists for chapter_id=%d with name=%s", chapter_id, problem_name)
        async with async_session() as session:
                result = await session.execute(
                        select(Problem)
                        .where(Problem.chapter_id == chapter_id, Problem.name == problem_name)
                )
                exists = result.scalar_one_or_none() is not None
                logger.debug("Problem exists: %s", exists)
                return exists

async def get_accepted_with_chapter_id(chapter_id: int) -> List[Problem]:
        logger.debug("Fetching accepted problems for chapter_id: %s", chapter_id)

        async with async_session() as session:
                result = await session.execute(
                select(Problem).where(Problem.chapter_id == chapter_id,
                                        Problem.status == "accepted")
                )
                problems = result.scalars().all()
                logger.info("Fetched %d accepted problems for chapter_id: %s", len(problems), chapter_id)
                return problems

async def get_accepted_by_problem_id(problem_id: int) -> Problem:
        logger.debug("Fetching accepted problem by problem_id: %s", problem_id)

        async with async_session() as session:
                result = await session.execute(
                        select(Problem).where(Problem.id == problem_id,
                                                Problem.status == "accepted")
                )
                problem = result.scalar_one()
                if problem:
                        logger.info("Fetched accepted problem with id: %s", problem.id)
                else:
                        logger.warning("No accepted problem found for id: %s", problem_id)
                return problem