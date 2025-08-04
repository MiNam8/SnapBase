from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.utils.fuzzy_matcher import get_best_fuzzy_matches
from src.keyboards.suggestion_keyboard import get_suggestions_keyboard
import logging

logger = logging.getLogger(__name__)

async def handle_fuzzy_matches_or_continue(message: Message, state: FSMContext, entity: str, entity_name: str, get_all_entities):
    logger.debug("inside handle_fuzzy_matches_or_continue")
    all_entities = await get_all_entities()
    options = get_best_fuzzy_matches(entity_name, all_entities)
    if len(options) == 0:
        return True
    
    keyboard = get_suggestions_keyboard(options, entity)
    logger.debug("After get_suggestions_keyboard")
    await message.answer(
        f"🤔 Did you mean one of these {entity}s?",
        reply_markup=keyboard
    )
    return False