from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.handlers.solutions import delete_previous_images
from src.handlers.menu import get_back_to_main_keyboard
from src.states.solutions import AddSolutionStates
from src.keyboards.problems import get_problems_keyboard
from src.states.chapters import AddChapterStates
from src.handlers.textbooks import view_textbook_chapters
from src.handlers.solutions import select_textbook_for_solution
from src.repositories.chapters import get_accepted_with_textbook, get_accepted_with_name_and_id
from src.constants.messages import CHAPTER_NOT_FOUND, CHAPTER_NAME_PROMPT, EMPTY_CHAPTER_ERROR
from src.utils.helpers import is_valid_chapter_name

router = Router()

@router.callback_query(F.data.startswith("view_chapter_"))
async def view_chapter_problems(callback: CallbackQuery, state: FSMContext):
    await delete_previous_images(callback, state)
    
    chapter_id = int(callback.data.split("_")[-1])
    
    chapter = await get_accepted_with_textbook(chapter_id)
    if not chapter:
        await callback.message.answer(CHAPTER_NOT_FOUND)
        return

    keyboard = await get_problems_keyboard(chapter_id, "view")
    await callback.message.edit_text(
        f"📖 Textbook: {chapter.textbook.name}\n"
        f"📑 Chapter: {chapter.name}\n\n"
        "Select a problem to view its solutions:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("add_chapter_"))
async def select_chapter_for_solution(callback: CallbackQuery, state: FSMContext):
    chapter_id = int(callback.data.split("_")[-1])
    await state.update_data(chapter_id=chapter_id)
    
    chapter = await get_accepted_with_textbook(chapter_id)
    
    keyboard = await get_problems_keyboard(chapter_id, "add")
    await callback.message.edit_text(
        f"➕ Add Solution to: {chapter.textbook.name}\n"
        f"📑 Chapter: {chapter.name}\n\n"
        "Step 3: Select the problem:",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_problem)

@router.callback_query(F.data.startswith("add_new_chapter"))
async def add_new_chapter(callback: CallbackQuery, state: FSMContext):

    await state.set_state(AddChapterStates.waiting_for_chapter_name)
    await callback.message.edit_text(
        CHAPTER_NAME_PROMPT,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
        ])
    )

@router.message(AddChapterStates.waiting_for_chapter_name)
async def save_new_chapter(message: Message, state: FSMContext):
    chapter_name = message.text.strip()
    if not is_valid_chapter_name(chapter_name):
        keyboard = get_back_to_main_keyboard()
        await message.answer(EMPTY_CHAPTER_ERROR, reply_markup=keyboard)
        return

    data = await state.get_data()
    textbook_id = None 
    if data.get("textbook_id") and data.get("textbook_id") != "None":
        textbook_id = int(data.get("textbook_id"))
    textbook_name = data.get("textbook_name")

    # Show success message and continue to problem selection
    await state.update_data(chapter_name=chapter_name)
    keyboard = await get_problems_keyboard(None, action_prefix="add")
    
    await message.answer(
        f"➕ Add Solution to: {textbook_name}\n"
        f"📑 Chapter: {chapter_name}\n\n"
        "Step 3: Select the problem:",
        reply_markup=keyboard
    )

    # Continue to problem selection step
    await state.set_state(AddSolutionStates.waiting_for_problem)


@router.callback_query(F.data.startswith("back_to_chapters_"))
async def back_to_chapters(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating back
    await delete_previous_images(callback, state)
    
    parts = callback.data.split("_")
    action_prefix = parts[3]
    textbook_id = int(parts[4])
    
    if action_prefix == "view":
        await view_textbook_chapters(CallbackQuery(
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


