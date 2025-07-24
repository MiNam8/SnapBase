from src.db.models import Problem, Chapter, Solution
from src.db.models import async_session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import json


async def get_solution_with_problem_by_id(solution_id: int) -> Problem:
    async with async_session() as session:
        result = await session.execute(
            select(Solution).options(
                selectinload(Solution.problem).selectinload(Problem.chapter).selectinload(Chapter.textbook)
            ).where(Solution.id == solution_id,
                    Solution.status == "accepted")
        )
        solution = result.scalar_one()
        return solution
    

async def save_solution_to_db(username, full_name, data, problem_id, status):

    async with async_session() as session:
        user_name = f"@{username}" if username else (full_name or "Anonymous")
        solution = Solution(
            user_name= user_name,
            text=data.get("solution_text"),
            image_file_ids=json.dumps(data.get("image_file_ids", [])) if data.get("image_file_ids") else None,
            problem_id=problem_id,
            status=status
        )
        session.add(solution)
        await session.commit()


async def get_solution_by_id(solution_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Solution).where(Solution.id == solution_id)
        )
        return result.scalar_one()
