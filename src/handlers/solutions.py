from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.db.models import async_session, Textbook, Chapter, Problem, Solution
import json
from src.states.solutions import AddSolutionStates
from src.keyboards.textbooks import get_textbooks_keyboard
from src.keyboards.chapters import get_chapters_keyboard
from src.keyboards.menu import get_back_to_main_keyboard 
from src.services.solutions import delete_previous_images, get_solution_details
from src.repositories.textbooks import get_accepted_textbook_by_id
from src.utils.helpers import determine_submission_status, generate_success_message
from src.services.solutions import create_solution_flow

router = Router()

@router.callback_query(F.data.startswith("view_solution_"))
async def view_solution_details(callback: CallbackQuery, state: FSMContext):
    # Delete previous images before showing new solution
    await delete_previous_images(callback, state)
    
    solution_id = int(callback.data.split("_")[-1])
    text, file_ids, keyboard = await get_solution_details(solution_id)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

    if file_ids:
        await send_and_track_images(callback, state, file_ids)


@router.callback_query(F.data == "add_solution")
async def start_add_solution(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when starting add solution flow
    await delete_previous_images(callback, state)
    
    keyboard = await get_textbooks_keyboard("add")
    await callback.message.edit_text(
        "➕ Add a New Solution\n\n"
        "Step 1: Select the textbook:",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_textbook)

@router.callback_query(F.data.startswith("add_textbook_"))
async def select_textbook_for_solution(callback: CallbackQuery, state: FSMContext):
    textbook_id = int(callback.data.split("_")[-1])
    await state.update_data(textbook_id=textbook_id)
    
    textbook = await get_accepted_textbook_by_id(textbook_id)
    await state.update_data(textbook_name = textbook.name)
    
    keyboard = await get_chapters_keyboard(textbook_id, "add")
    await callback.message.edit_text(
        f"➕ Add Solution to: {textbook.name}\n\n"
        "Step 2: Select the chapter:",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_chapter)


@router.message(AddSolutionStates.waiting_for_solution_text)
async def receive_solution_text(message: Message, state: FSMContext):
    if message.text.lower() == 'skip':
        await state.update_data(solution_text=None)
    else:
        await state.update_data(solution_text=message.text)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Skip Images", callback_data="skip_images")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])
    
    await message.answer(
        "Step 5: Send images for your solution (if any), or click 'Skip Images' to finish:",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_solution_image)

@router.message(AddSolutionStates.waiting_for_solution_image, F.photo)
async def receive_solution_image(message: Message, state: FSMContext):
    data = await state.get_data()
    image_file_ids = data.get('image_file_ids', [])
    image_file_ids.append(message.photo[-1].file_id)
    await state.update_data(image_file_ids=image_file_ids)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Finish", callback_data="finish_solution")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])
    
    await message.answer(
        "Image received! Send more images or click 'Finish' to save your solution:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.in_(["skip_images", "finish_solution"]))
async def finish_solution(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    username = callback.from_user.username or ""
    full_name = callback.from_user.full_name or "Anonymous"

    status = determine_submission_status(username)

    # Call service to create and return solution metadata
    result = await create_solution_flow(
        data=data,
        username=username,
        full_name=full_name,
        status=status
    )

    # Now Telegram-specific part stays in handler
    message_text = generate_success_message(status)
    await callback.message.edit_text(
        message_text,
        reply_markup=get_back_to_main_keyboard()
    )
    await state.clear()


# Helper function to send images and track message IDs
async def send_and_track_images(callback: CallbackQuery, state: FSMContext, file_ids: list):
    """Send images and store their message IDs for later deletion"""
    sent_message_ids = []
    
    for file_id in file_ids:
        try:
            sent_message = await callback.message.answer_photo(file_id)
            sent_message_ids.append(sent_message.message_id)
        except Exception as e:
            print(f"Could not send image {file_id}: {e}")
    
    # Store the message IDs in state for later cleanup
    await state.update_data(previous_image_messages=sent_message_ids)