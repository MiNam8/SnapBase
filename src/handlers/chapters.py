from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.states.chapters import AddChapterStates
from src.constants.messages import CHAPTER_NAME_PROMPT
from src.services.chapters import display_chapter_problems, handle_chapter_selection, handle_chapter_name, handle_back_to_chapters, prompt_add_chapter

router = Router()

@router.callback_query(F.data.startswith("view_chapter_"))
async def view_chapter_problems(callback: CallbackQuery, state: FSMContext):
    await display_chapter_problems(callback, state)


@router.callback_query(F.data.startswith("add_chapter_"))
async def select_chapter_for_solution(callback: CallbackQuery, state: FSMContext):
    await handle_chapter_selection(callback, state)

@router.callback_query(F.data.startswith("add_new_chapter"))
async def add_new_chapter(callback: CallbackQuery, state: FSMContext):
    await prompt_add_chapter(callback, state)

@router.message(AddChapterStates.waiting_for_chapter_name)
async def save_new_chapter(message: Message, state: FSMContext):
    await handle_chapter_name(message, state)


@router.callback_query(F.data.startswith("back_to_chapters_"))
async def back_to_chapters(callback: CallbackQuery, state: FSMContext):
    await handle_back_to_chapters(callback, state)
