from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from src.db.models import async_session, Problem, Solution

async def get_solutions_keyboard(problem_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Solution).where(
                                    Solution.problem_id == problem_id,
                                    Solution.status == "accepted"
                                    )
        )
        solutions = result.scalars().all()
        
        keyboard_buttons = []
        for i, solution in enumerate(solutions, 1):
            callback_data = f"view_solution_{solution.id}"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"📝 Solution {i} by {solution.user_name}", 
                callback_data=callback_data
            )])
        
        # Get chapter_id for back navigation
        problem_result = await session.execute(
            select(Problem).where(Problem.id == problem_id,
                                  Problem.status == "accepted")
        )
        problem = problem_result.scalar_one()
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="⬅️ Back to Problems", callback_data=f"back_to_problems_view_{problem.chapter_id}"),
            InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
        ])
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def solution_detail_keyboard(problem_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Solutions", callback_data=f"view_problem_{problem_id}")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
    ])

def skip_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Skip Images", callback_data="skip_images")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])

def finish_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Finish", callback_data="finish_solution")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])