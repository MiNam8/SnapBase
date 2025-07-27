from src.repositories.textbooks import get_accepted_textbook_by_id
from src.db.models import Textbook, async_session
from src.constants.messages import ERROR_TEXTBOOK_EXISTS, SUCCESS_TEXTBOOK_CREATED, INVALID_TEXTBOOK_NAME, AVAILABLE_TEXTBOOKS
from src.repositories.textbooks import textbook_exists_by_name, create_textbook
from src.constants.messages import STEP2_SELECT_CHAPTER
from typing import Tuple
from src.keyboards.chapters import get_chapters_keyboard
from src.utils.helpers import format_textbook_text
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.utils.helpers import is_valid_textbook_name_length, is_valid_textbook_name_format
from src.states.solutions import AddSolutionStates
from src.handlers.menu import get_back_to_main_keyboard
from src.services.solutions import delete_previous_images
from src.keyboards.textbooks import get_textbooks_keyboard
from aiogram.types import Message, CallbackQuery
from src.keyboards.menu import get_cancel_keyboard
from src.constants.messages import ADD_TEXTBOOK_PROMPT
from src.states.textbooks import AddTextbookStates
from src.handlers.solutions import start_add_solution



async def fetch_textbook_for_viewing(textbook_id: int) -> Textbook:
    textbook = await get_accepted_textbook_by_id(textbook_id)
    return textbook

async def create_textbook_if_not_exists(name: str) -> tuple[bool, str]:
        async with async_session() as session:
            exists = await textbook_exists_by_name(name)
            if exists:
                return False, ERROR_TEXTBOOK_EXISTS.format(name=name)

            # Optionally: await TextbookRepository.create(session, name)
            return True, SUCCESS_TEXTBOOK_CREATED.format(name=name)
        
async def create_textbook_and_return_id(name: str) -> Tuple[bool, str, int]:
        async with async_session() as session:
            if await textbook_exists_by_name(name):
                return False, ERROR_TEXTBOOK_EXISTS.format(name=name), None
            
            new_textbook = await create_textbook(session, name)
            return True, STEP2_SELECT_CHAPTER.format(name=name), new_textbook.id
        
async def get_textbook_chapters(textbook_id: int):
        textbook = await fetch_textbook_for_viewing(textbook_id)
        
        keyboard = await get_chapters_keyboard(textbook_id, "view")
        textbook_text = format_textbook_text(textbook.name)
        return textbook_text, keyboard

async def process_textbook_name(message: Message, state: FSMContext):
    textbook_name = message.text.strip()

    if not is_valid_textbook_name_length(textbook_name):
        await message.answer("❌ Textbook name must be at least 4 characters long. Please try again:")
        return

    if not is_valid_textbook_name_format(textbook_name):
        await message.answer(INVALID_TEXTBOOK_NAME)
        return

    await state.update_data(textbook_name=textbook_name)
    data = await state.get_data()

    if data.get('in_solution_flow'):
        await finish_textbook_creation_in_solution_flow(message, state)
    else:
        await finish_textbook_creation(message, state)


async def finish_textbook_creation_in_solution_flow(message: Message, state: FSMContext):
    """Handle textbook creation within solution flow"""
    data = await state.get_data()
    textbook_name = data.get('textbook_name')
    
    # # Continue with chapter selection
    keyboard = await get_chapters_keyboard(None, "add")
    await message.answer(
        STEP2_SELECT_CHAPTER.format(name=textbook_name),
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_chapter)


async def finish_textbook_creation(message, state: FSMContext, is_callback=False):
    data = await state.get_data()
    textbook_name = data['textbook_name']
    
    success, msg = await create_textbook_if_not_exists(textbook_name)
    
    if is_callback:
        await message.edit_text(msg, reply_markup=get_back_to_main_keyboard())
    else:
        await message.answer(msg, reply_markup=get_back_to_main_keyboard())
    
    await state.clear()

async def get_textbooks(callback: CallbackQuery, state: FSMContext):
    await delete_previous_images(callback, state)
    
    keyboard = await get_textbooks_keyboard("view")
    
    await callback.message.edit_text(
        AVAILABLE_TEXTBOOKS,
        reply_markup=keyboard
    )


async def add_textbook_flow(callback: CallbackQuery, state: FSMContext):
    """Handle adding textbook within the solution flow"""
    await delete_previous_images(callback, state)
    
    keyboard = get_cancel_keyboard()
    
    await callback.message.edit_text(
        ADD_TEXTBOOK_PROMPT,
        reply_markup=keyboard
    )

    # Set a flag to know we're in solution flow
    await state.update_data(in_solution_flow=True)
    await state.set_state(AddTextbookStates.waiting_for_textbook_name)


async def add_textbook(callback: CallbackQuery, state: FSMContext):
    await delete_previous_images(callback, state)
    
    keyboard = get_cancel_keyboard()
    
    await callback.message.edit_text(
        ADD_TEXTBOOK_PROMPT,
        reply_markup=keyboard
    )

    await state.set_state(AddTextbookStates.waiting_for_textbook_name)

async def move_to_textbooks(callback: CallbackQuery, state: FSMContext):
     # Delete any previous images when navigating back
    await delete_previous_images(callback, state)
    
    action_prefix = callback.data.split("_")[-1]
    if action_prefix == "view":
        await get_textbooks(callback, state)
    elif action_prefix == "add":
        await start_add_solution(callback, state)
