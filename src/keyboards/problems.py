from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.repositories.problems import get_accepted_with_chapter_id
from src.repositories.chapters import get_chapter_by_id

async def get_problems_keyboard(chapter_id: int, action_prefix="view"):
    problems = await get_accepted_with_chapter_id(chapter_id)
    
    keyboard_buttons = []
    for problem in problems:
        callback_data = f"{action_prefix}_problem_{problem.id}"
        keyboard_buttons.append([InlineKeyboardButton(
            text=f"🧮 {problem.name}", 
            callback_data=callback_data
        )])
    
    # Get textbook_id for back navigation
    # chapter = None
    # if action_prefix == "view":
    chapter = await get_chapter_by_id(chapter_id)
    
    if action_prefix == "add":
        keyboard_buttons.append([
            InlineKeyboardButton(text="➕ Add new problem", callback_data=f"add_new_problem_{chapter_id}")
        ])

    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Chapters", callback_data=f"back_to_chapters_{action_prefix}_{chapter.textbook_id if chapter else ""}"),
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
