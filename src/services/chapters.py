from src.db.models import async_session
from src.repositories.chapters import get_accepted_with_textbook
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from src.constants.messages import CHAPTER_NOT_FOUND, EMPTY_CHAPTER_ERROR, CHAPTER_ALREADY_EXISTS
from src.keyboards.problems import get_problems_keyboard
from src.utils.helpers import format_chapter_text, select_problem_text, is_valid_problem_chapter_name
from src.states.solutions import AddSolutionStates
from src.handlers.menu import get_back_to_main_keyboard
from src.states.solutions import AddSolutionStates
from src.services.solutions import delete_previous_images
from src.handlers.solutions import select_textbook_for_solution
from src.services.textbooks import get_textbook_chapters
from src.states.chapters import AddChapterStates
from src.constants.messages import CHAPTER_NAME_PROMPT
from src.repositories.chapters import check_chapter_name_for_textbook
from src.keyboards.menu import get_cancel_keyboard


async def get_accepted_chapter_with_textbook(chapter_id: int):
        async with async_session() as session:
            return await get_accepted_with_textbook(session, chapter_id)
        
async def chapter_problems(callback: CallbackQuery, state: FSMContext):
    await delete_previous_images(callback, state)

    chapter_id = int(callback.data.split("_")[-1])
    chapter = await get_accepted_with_textbook(chapter_id)

    if not chapter:
        await callback.message.answer(CHAPTER_NOT_FOUND)
        return

    message_text = format_chapter_text(chapter)

    keyboard = await get_problems_keyboard(chapter_id, "view")

    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard
    )

async def select_chapter(callback: CallbackQuery, state: FSMContext):
    chapter_id = int(callback.data.split("_")[-1])
    await state.update_data(chapter_id=chapter_id)

    chapter = await get_accepted_with_textbook(chapter_id)
    
    message_text = select_problem_text(chapter.textbook.name, chapter.name)
    keyboard = await get_problems_keyboard(chapter_id, "add")
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard
    )

    await state.set_state(AddSolutionStates.waiting_for_problem)


async def save_chapter(callback: CallbackQuery, state: FSMContext):
    chapter_name = callback.text.strip()
    if not is_valid_problem_chapter_name(chapter_name):
        keyboard = get_back_to_main_keyboard()
        await callback.answer(EMPTY_CHAPTER_ERROR, reply_markup=keyboard)
        return

    data = await state.get_data()
    textbook_id = None 
    if data.get("textbook_id") and data.get("textbook_id") != "None":
        textbook_id = int(data.get("textbook_id"))
    textbook_name = data.get("textbook_name")

    print("Check textbook_id and chapter_name:", textbook_id, chapter_name, type(textbook_id), type(chapter_name))
    if textbook_id and await check_chapter_name_for_textbook(textbook_id, chapter_name):
        keyboard = get_cancel_keyboard()
        await callback.answer(CHAPTER_ALREADY_EXISTS, reply_markup=keyboard)
        return


    # Show success message and continue to problem selection
    await state.update_data(chapter_name=chapter_name)

    message_text = select_problem_text(textbook_name, chapter_name)    
    keyboard = await get_problems_keyboard(None, action_prefix="add")
    await callback.answer(
        message_text,
        reply_markup=keyboard
    )

    # Continue to problem selection step
    await state.set_state(AddSolutionStates.waiting_for_problem)

async def navigate_back_to_chapters(callback: CallbackQuery, state: FSMContext):
    await delete_previous_images(callback, state)
    
    parts = callback.data.split("_")
    action_prefix = parts[3]
    textbook_id = int(parts[4])
    
    if action_prefix == "view":
        await get_chapters(CallbackQuery(
            id=callback.id,
            from_user=callback.from_user,
            chat_instance=callback.chat_instance,
            message=callback.message,
            data=f"view_textbook_{textbook_id}"
        ), state)
    elif action_prefix == "add":
        await select_textbook_for_solution(CallbackQuery(
            id=callback.id,
            from_user=callback.from_user,
            chat_instance=callback.chat_instance,
            message=callback.message,
            data=f"add_textbook_{textbook_id}"
        ), state)


async def get_chapters(callback: CallbackQuery, state: FSMContext):
    await delete_previous_images(callback, state)
    
    textbook_id = int(callback.data.split("_")[-1])

    text, keyboard = await get_textbook_chapters(textbook_id)

    await callback.message.edit_text(text, reply_markup=keyboard)


async def add_chapter(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddChapterStates.waiting_for_chapter_name)
    await callback.message.edit_text(
        CHAPTER_NAME_PROMPT,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
        ])
    )