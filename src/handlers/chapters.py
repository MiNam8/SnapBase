from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.states.chapters import AddChapterStates
from src.constants.messages import CHAPTER_NAME_PROMPT
from src.services.chapters import display_chapter_problems, handle_chapter_selection, handle_chapter_name, handle_back_to_chapters, prompt_add_chapter, handle_chapter_choice
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data.startswith("view_chapter_"))
async def view_chapter_problems(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s, triggered 'view_chapter_' with data: %s", callback.from_user.id, callback.data)
    await display_chapter_problems(callback, state)

@router.callback_query(F.data.startswith("add_chapter_"))
async def select_chapter_for_solution(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s triggered 'add_chapter_' with data: %s", callback.from_user.id, callback.data)
    await handle_chapter_selection(callback, state)

@router.callback_query(F.data.startswith("add_new_chapter"))
async def add_new_chapter(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s is adding a new chapter.", callback.from_user.id)
    await prompt_add_chapter(callback, state)

@router.message(AddChapterStates.waiting_for_chapter_name)
async def save_new_chapter(message: Message, state: FSMContext):
    logger.info("User %s sent new chapter name: %s", message.from_user.id, message.text)
    await handle_chapter_name(message, state)

@router.callback_query(F.data.startswith("back_to_chapters_"))
async def back_to_chapters(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s triggered 'back_to_chapters_' with data: %s", callback.from_user.id, callback.data)
    await handle_back_to_chapters(callback, state)

@router.callback_query(F.data.startswith("chapter_suggestions:"))
async def chapter_choice(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s triggered 'chapter_choice' with choice: %s", callback.from_user.id, callback.data.split(":")[1])
    await handle_chapter_choice(callback, state)