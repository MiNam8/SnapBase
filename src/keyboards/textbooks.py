from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from src.db.models import async_session, Textbook

async def get_textbooks_keyboard(action_prefix="view"):
    async with async_session() as session:
        result = await session.execute(select(Textbook).where(Textbook.status == "accepted"))
        textbooks = result.scalars().all()
        keyboard_buttons = []
        for textbook in textbooks:
            callback_data = f"{action_prefix}_textbook_{textbook.id}"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"📖 {textbook.name}", 
                callback_data=callback_data
            )])

        if action_prefix == "add":
            keyboard_buttons.append(
                [InlineKeyboardButton(text="➕ Add Textbook", callback_data="add_textbook_in_solution_flow")],
            )

        keyboard_buttons.append([InlineKeyboardButton(text="🏠 Back to Main Menu", callback_data="main_menu")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
