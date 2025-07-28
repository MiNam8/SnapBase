from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from src.db.models import Problem, Solution
from src.repositories.solutions import get_accepted_solutions_by_problem_id
from src.repositories.problems import get_accepted_by_problem_id

async def get_solutions_keyboard(problem_id: int):
    solutions = await get_accepted_solutions_by_problem_id(problem_id)
    
    keyboard_buttons = []
    for i, solution in enumerate(solutions, 1):
        callback_data = f"view_solution_{solution.id}"
        keyboard_buttons.append([InlineKeyboardButton(
            text=f"📝 Solution {i} by {solution.user_name}", 
            callback_data=callback_data
        )])
    
    # Get chapter_id for back navigation
    problem = await get_accepted_by_problem_id(problem_id)
    
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