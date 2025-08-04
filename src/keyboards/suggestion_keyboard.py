from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from src.schemas import HasNameAndId

logger = logging.getLogger(__name__)

def get_suggestions_keyboard(options: list[HasNameAndId], entity: str) -> InlineKeyboardMarkup:
    
    for option in options:
        callback_data = f"{entity}_suggestions:{option.id}"
        logger.debug("the callback_data: %s", callback_data)
    
    buttons = [
        [InlineKeyboardButton(text=option.name, callback_data=f"{entity}_suggestions:{option.id}")]
        for option in options
    ]

    buttons.append([InlineKeyboardButton(text="❌ None of these", callback_data=f"{entity}_suggestions:none")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)