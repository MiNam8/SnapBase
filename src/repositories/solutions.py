from src.db.models import Problem, Chapter, Solution
from src.db.models import async_session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import json
import logging

logger = logging.getLogger(__name__)

async def get_solution_with_problem_by_id(solution_id: int) -> Problem:
    logger.debug("Fetching solution with ID: %s and its related problem, chapter, and textbook", solution_id)
    async with async_session() as session:
        result = await session.execute(
            select(Solution).options(
                selectinload(Solution.problem).selectinload(Problem.chapter).selectinload(Chapter.textbook)
            ).where(Solution.id == solution_id,
                    Solution.status == "accepted")
        )
        solution = result.scalar_one()
        logger.info("Fetched accepted solution: %s for problem ID: %s", solution.id, solution.problem_id)
        return solution
    

async def save_solution_to_db(username, full_name, data, problem_id, status):
    logger.info("Saving solution for user: %s to problem ID: %s", username, problem_id)

    async with async_session() as session:
        user_name = f"@{username}" if username else (full_name or "Anonymous")
        logger.info("Saving solution by %s to problem ID %s", user_name, problem_id)
        solution = Solution(
            user_name= user_name,
            text=data.get("solution_text"),
            image_file_ids=json.dumps(data.get("image_file_ids", [])) if data.get("image_file_ids") else None,
            problem_id=problem_id,
            status=status
        )
        session.add(solution)
        await session.flush()
        logger.info("Solution saved: ID=%s, Status=%s", solution.id, status)
        await session.commit()
        logger.info("Solution committed to DB.")


async def get_solution_by_id(solution_id: int):
    logger.debug("Fetching solution by solution_id: %s", solution_id)
    async with async_session() as session:
        result = await session.execute(
            select(Solution).where(Solution.id == solution_id)
        )
        solution = result.scalar_one()
        logger.info("Fetched solution: ID=%s", solution.id)
        return solution

async def get_accepted_solutions_by_problem_id(problem_id: int) -> list[Solution]:
    logger.debug("Fetching accepted solutions for problem_id: %s", problem_id)
    async with async_session() as session:
        result = await session.execute(
            select(Solution).where(
                Solution.problem_id == problem_id,
                Solution.status == "accepted"
            )
        )
        solutions = result.scalars().all()
        logger.info("Fetched %d accepted solutions for problem_id: %s", len(solutions), problem_id)
        return solutions