from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

def get_main_menu_keyboard():
    logger.info("Generating main menu keyboard.")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Browse Solutions", callback_data="browse_textbooks")],
        [InlineKeyboardButton(text="➕ Add Solution", callback_data="add_solution")],
        [InlineKeyboardButton(text="❓ Help", callback_data="help")]
    ])
    return keyboard

# Back to main menu keyboard
def get_back_to_main_keyboard():
    logger.info("Generating back to main menu keyboard.")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Back to Main Menu", callback_data="main_menu")]
    ])
    return keyboard

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    logger.info("Generating cancel keyboard.")

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])
