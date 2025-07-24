from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.keyboards.textbooks import get_textbooks_keyboard
from src.keyboards.chapters import get_chapters_keyboard
from src.states.textbooks import AddTextbookStates
from src.handlers.menu import get_back_to_main_keyboard
from src.handlers.solutions import start_add_solution
from src.states.solutions import AddSolutionStates
from src.services.solutions import delete_previous_images
from src.services.textbooks import fetch_textbook_for_viewing, create_textbook_if_not_exists
from src.constants.messages import ADD_TEXTBOOK_PROMPT, INVALID_TEXTBOOK_NAME, STEP2_SELECT_CHAPTER
from src.keyboards.menu import get_cancel_keyboard
from src.utils.helpers import is_valid_textbook_name_format, is_valid_textbook_name_length
# from src.services.problems import handle_textbook_flow


router = Router()

@router.callback_query(F.data == "browse_textbooks")
async def browse_textbooks(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when starting browse flow
    await delete_previous_images(callback, state)
    
    keyboard = await get_textbooks_keyboard("view")
    await callback.message.edit_text(
        "📚 Available Textbooks:\n\n"
        "Select a textbook to browse its chapters:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("view_textbook_"))
async def view_textbook_chapters(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating
    await delete_previous_images(callback, state)
    
    textbook_id = int(callback.data.split("_")[-1])
    textbook = await fetch_textbook_for_viewing(textbook_id)

    keyboard = await get_chapters_keyboard(textbook_id, "view")
    await callback.message.edit_text(
        f"📖 Textbook: {textbook.name}\n\n"
        "Select a chapter to view its problems:",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "add_textbook_in_solution_flow")
async def add_textbook_in_solution_flow(callback: CallbackQuery, state: FSMContext):
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

# Add Textbook Flow
@router.callback_query(F.data == "add_textbook")
async def start_add_textbook(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when starting add textbook flow
    await delete_previous_images(callback, state)
    
    keyboard = get_cancel_keyboard()
    
    await callback.message.edit_text(
        ADD_TEXTBOOK_PROMPT,
        reply_markup=keyboard
    )

    await state.set_state(AddTextbookStates.waiting_for_textbook_name)


@router.message(AddTextbookStates.waiting_for_textbook_name)
async def receive_textbook_name(message: Message, state: FSMContext):
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


async def finish_textbook_creation(message, state: FSMContext, is_callback=False):
    data = await state.get_data()
    textbook_name = data['textbook_name']
    
    success, msg = await create_textbook_if_not_exists(textbook_name)
    
    if is_callback:
        await message.edit_text(msg, reply_markup=get_back_to_main_keyboard())
    else:
        await message.answer(msg, reply_markup=get_back_to_main_keyboard())
    
    await state.clear()


@router.callback_query(F.data.startswith("back_to_textbooks_"))
async def back_to_textbooks(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating back
    await delete_previous_images(callback, state)
    
    action_prefix = callback.data.split("_")[-1]
    if action_prefix == "view":
        await browse_textbooks(callback, state)
    elif action_prefix == "add":
        await start_add_solution(callback, state)


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