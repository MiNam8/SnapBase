from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.repositories.textbooks import get_accepted_textbooks
import logging

logger = logging.getLogger(__name__)

async def get_textbooks_keyboard(action_prefix="view"):
    logger.info("Generating textbooks keyboard with action_prefix: %s", action_prefix)

    textbooks = await get_accepted_textbooks()
    logger.info("Fetched %s accepted textbooks from repo", len(textbooks))

    keyboard_buttons = []
    for textbook in textbooks:
        callback_data = f"{action_prefix}_textbook_{textbook.id}"
        keyboard_buttons.append([InlineKeyboardButton(
            text=f"📖 {textbook.name}", 
            callback_data=callback_data
        )])
        logger.debug("Added button for textbook: id=%s, name=%s", textbook.id, textbook.name)

    if action_prefix == "add":
        keyboard_buttons.append(
            [InlineKeyboardButton(text="➕ Add Textbook", callback_data="add_textbook_in_solution_flow")],
        )
        logger.debug("Added 'Add Textbook' button")

    keyboard_buttons.append([InlineKeyboardButton(text="🏠 Back to Main Menu", callback_data="main_menu")])
    logger.debug("Added 'Back to Main Menu' button")

    logger.info("Finished generating keyboard with %s total rows", len(keyboard_buttons))
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
