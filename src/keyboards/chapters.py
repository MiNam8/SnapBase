from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.repositories.chapters import get_accepted_with_textbook_id
import logging

logger = logging.getLogger(__name__)

async def get_chapters_keyboard(textbook_id: int, action_prefix="view"):
    logger.info("Generating chapters keyboard for textbook_id=%s with action_prefix=%s", textbook_id, action_prefix)

    chapters = await get_accepted_with_textbook_id(textbook_id)
    logger.info("Fetched %s chapters for textbook_id=%s", len(chapters), textbook_id)
    
    keyboard_buttons = []
    for chapter in chapters:
        callback_data = f"{action_prefix}_chapter_{chapter.id}"
        logger.debug("Adding chapter button: id=%s, name=%s", chapter.id, chapter.name)
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
