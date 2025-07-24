from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from src.db.models import async_session, Chapter

async def get_chapters_keyboard(textbook_id: int, action_prefix="view"):
    async with async_session() as session:
        result = await session.execute(
            select(Chapter).where(Chapter.textbook_id == textbook_id, 
                                  Chapter.status == "accepted")
        )
        chapters = result.scalars().all()
        
        keyboard_buttons = []
        for chapter in chapters:
            callback_data = f"{action_prefix}_chapter_{chapter.id}"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"📑 {chapter.name}", 
                callback_data=callback_data
            )])
        
        if action_prefix == "add":
            keyboard_buttons.append([
                InlineKeyboardButton(text="➕ Add new chapter", callback_data=f"add_new_chapter_{textbook_id}")
            ])

        keyboard_buttons.append([
                InlineKeyboardButton(text="⬅️ Back to Textbooks", callback_data=f"back_to_textbooks_{action_prefix}"),
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
            ])
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
