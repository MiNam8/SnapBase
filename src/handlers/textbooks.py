from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.states.textbooks import AddTextbookStates
from src.services.textbooks import process_textbook_name, get_textbooks, add_textbook_flow, prompt_add_textbook, handle_back_to_textbooks
from src.services.chapters import display_chapter_list
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data == "browse_textbooks")
async def browse_textbooks(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s triggered 'browse_textbooks'", callback.from_user.id)
    await get_textbooks(callback, state)


@router.callback_query(F.data.startswith("view_textbook_"))
async def view_textbook_chapters(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s triggered 'view_textbook_chapters'", callback.from_user.id)
    await display_chapter_list(callback, state)


@router.callback_query(F.data == "add_textbook_in_solution_flow")
async def add_textbook_in_solution_flow(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s triggered 'add_textbook_in_solution_flow'", callback.from_user.id)
    await add_textbook_flow(callback, state)

# Add Textbook Flow
@router.callback_query(F.data == "add_textbook")
async def start_add_textbook(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s triggered 'start_add_textbook'", callback.from_user.id)
    await prompt_add_textbook(callback, state)


@router.message(AddTextbookStates.waiting_for_textbook_name)
async def receive_textbook_name(message: Message, state: FSMContext):
    logger.info("User %s triggered 'receive_textbook_name' with message: %s", message.from_user.id, message.text)
    await process_textbook_name(message, state)

@router.callback_query(F.data.startswith("back_to_textbooks_"))
async def back_to_textbooks(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s triggered 'back_to_textbooks'", callback.from_user.id)
    await handle_back_to_textbooks(callback, state)
