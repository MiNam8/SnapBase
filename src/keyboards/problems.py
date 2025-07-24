from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from src.db.models import async_session, Chapter, Problem

async def get_problems_keyboard(chapter_id: int, action_prefix="view"):
    async with async_session() as session:
        result = await session.execute(
            select(Problem).where(Problem.chapter_id == chapter_id,
                                  Problem.status == "accepted")
        )
        problems = result.scalars().all()
        
        keyboard_buttons = []
        for problem in problems:
            callback_data = f"{action_prefix}_problem_{problem.id}"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"🧮 {problem.name}", 
                callback_data=callback_data
            )])
        
        # Get textbook_id for back navigation
        chapter_result = await session.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        chapter = None
        if action_prefix == "view":
            chapter = chapter_result.scalar_one()
        
        if action_prefix == "add":
            keyboard_buttons.append([
                InlineKeyboardButton(text="➕ Add new problem", callback_data=f"add_new_problem_{chapter_id}")
            ])

        keyboard_buttons.append([
            InlineKeyboardButton(text="⬅️ Back to Chapters", callback_data=f"back_to_chapters_{action_prefix}_{chapter.textbook_id if chapter else ""}"),
            InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
        ])
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
