from src.db.models import Problem, Chapter
from src.db.models import async_session
from sqlalchemy import select
from sqlalchemy.orm import selectinload



async def create_problem(name: str, chapter_id: int, status: str) -> Problem:
        async with async_session() as session:
                problem = Problem(name = name, chapter_id = chapter_id, status = status)
                session.add(problem)
                await session.commit()
                await session.refresh(problem)
                return problem


async def get_problem(problem_id: int) -> Problem:
        async with async_session() as session:
                result = await session.execute(
                select(Problem).options(
                        selectinload(Problem.chapter).selectinload(Chapter.textbook)
                ).where(Problem.id == problem_id,
                        Problem.status == "accepted")
                )
                problem = result.scalar_one()
                return problem