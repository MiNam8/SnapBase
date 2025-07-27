from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from src.utils.helpers import safe_int
from src.repositories.chapters import create_chapter
from src.repositories.problems import create_problem
from src.repositories.textbooks import create_textbook
from src.repositories.solutions import save_solution_to_db, get_solution_with_problem_by_id
from src.utils.helpers import format_solution_text
from src.keyboards.solutions import solution_detail_keyboard, skip_cancel_keyboard, finish_cancel_keyboard
import json
from src.keyboards.textbooks import get_textbooks_keyboard
from src.states.solutions import AddSolutionStates
from src.repositories.textbooks import get_accepted_textbook_by_id
from src.keyboards.chapters import get_chapters_keyboard
from src.constants.messages import NEW_SOLUTION_PROMPT
from src.utils.helpers import determine_submission_status, generate_success_message, add_solution_text
from src.keyboards.menu import get_back_to_main_keyboard



async def delete_previous_images(callback: CallbackQuery, state: FSMContext):
    """Delete previously sent image messages"""
    data = await state.get_data()
    previous_image_messages = data.get('previous_image_messages', [])
    
    for message_id in previous_image_messages:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=message_id
            )
        except Exception as e:
            # Message might already be deleted or not exist
            print(f"Could not delete message {message_id}: {e}")
    
    # Clear the stored message IDs
    await state.update_data(previous_image_messages=[])


async def create_solution_flow(data: dict, username: str, full_name: str, status: str):
    textbook_id = await upsert_textbook(data, status)
    chapter_id = await upsert_chapter(data, status, textbook_id)
    problem_id = await upsert_problem(data, status, chapter_id)

    await save_solution_to_db(
        username = username,
        full_name = full_name,
        data=data,
        problem_id=problem_id,
        status=status
    )

    return {
        "status": status,
        "textbook_id": textbook_id,
        "chapter_id": chapter_id,
        "problem_id": problem_id,
    }

async def upsert_textbook(data: dict, status: str) -> int | None:
    textbook_name = data.get("textbook_name")
    textbook_id = safe_int(data.get("textbook_id"))
    if textbook_id:
        return textbook_id
    
    if textbook_name:
        textbook = await create_textbook(name=textbook_name, status=status)
        return textbook.id
    return textbook_id


async def upsert_chapter(data: dict, status: str, textbook_id: int) -> int | None:
    chapter_name = data.get("chapter_name")
    chapter_id = safe_int(data.get("chapter_id"))
    if chapter_id:
        return chapter_id

    if chapter_name:
        chapter = await create_chapter(name=chapter_name, textbook_id=textbook_id, status=status)
        return chapter.id
    return chapter_id


async def upsert_problem(data: dict, status: str, chapter_id: int) -> int | None:
    problem_name = data.get("problem_name")
    problem_id = safe_int(data.get("problem_id"))
    if problem_id:
        return problem_id

    if problem_name:
        problem = await create_problem(name=problem_name, chapter_id=chapter_id, status=status)
        return problem.id
    return problem_id

async def get_solution_details(solution_id: int):
    solution = await get_solution_with_problem_by_id(solution_id)

    solution_text = format_solution_text(solution.problem, solution)
    keyboard = solution_detail_keyboard(solution.problem_id)

    file_ids = []
    if solution.image_file_ids:
        try:
            file_ids = json.loads(solution.image_file_ids)
        except json.JSONDecodeError:
            pass

    return solution_text, file_ids, keyboard


async def solution_details(callback: CallbackQuery, state: FSMContext):
    await delete_previous_images(callback, state)
    
    solution_id = int(callback.data.split("_")[-1])
    text, file_ids, keyboard = await get_solution_details(solution_id)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

    if file_ids:
        await send_and_track_images(callback, state, file_ids)

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


async def add_solution(callback: CallbackQuery, state: FSMContext):
    await delete_previous_images(callback, state)
    
    message_text = NEW_SOLUTION_PROMPT
    keyboard = await get_textbooks_keyboard("add")
    await callback.message.edit_text(message_text, reply_markup=keyboard)
    await state.set_state(AddSolutionStates.waiting_for_textbook)


async def textbook_for_solution(callback: CallbackQuery, state: FSMContext):
    textbook_id = int(callback.data.split("_")[-1])
    await state.update_data(textbook_id=textbook_id)
    
    textbook = await get_accepted_textbook_by_id(textbook_id)
    await state.update_data(textbook_name = textbook.name)
    
    message_text = add_solution_text(textbook.name)
    keyboard = await get_chapters_keyboard(textbook_id, "add")
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_chapter)

async def receive_text(message: Message, state: FSMContext):
    if message.text.lower() == 'skip':
        await state.update_data(solution_text=None)
    else:
        await state.update_data(solution_text=message.text)
    
    keyboard = skip_cancel_keyboard()
    
    await message.answer(
        "Step 5: Send images for your solution (if any), or click 'Skip Images' to finish:",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_solution_image)

async def receive_image(message: Message, state: FSMContext):
    data = await state.get_data()
    image_file_ids = data.get('image_file_ids', [])
    image_file_ids.append(message.photo[-1].file_id)
    await state.update_data(image_file_ids=image_file_ids)
    
    keyboard = finish_cancel_keyboard()
    
    await message.answer(
        "Image received! Send more images or click 'Finish' to save your solution:",
        reply_markup=keyboard
    )

async def final_solution_state(callback: CallbackQuery, state: FSMContext):
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