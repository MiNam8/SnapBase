from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from src.utils.helpers import safe_int
from src.repositories.chapters import create_chapter
from src.repositories.problems import create_problem, problem_exists_for_chapter
from src.repositories.textbooks import create_textbook, textbook_exists_by_name
from src.repositories.solutions import save_solution_to_db, get_solution_with_problem_by_id
from src.utils.helpers import format_solution_text
from src.keyboards.solutions import solution_detail_keyboard, skip_cancel_keyboard, finish_cancel_keyboard, get_yes_no_keyboard
import json
from src.keyboards.textbooks import get_textbooks_keyboard
from src.states.solutions import AddSolutionStates
from src.repositories.textbooks import get_accepted_textbook_by_id
from src.keyboards.chapters import get_chapters_keyboard
from src.constants.messages import NEW_SOLUTION_PROMPT
from src.utils.helpers import determine_submission_status, generate_success_message, add_solution_text
from src.keyboards.menu import get_back_to_main_keyboard
from src.repositories.chapters import check_chapter_name_for_textbook
import logging

logger = logging.getLogger(__name__)

async def delete_previous_images(callback: CallbackQuery, state: FSMContext):
    """Delete previously sent image messages"""
    data = await state.get_data()
    previous_image_messages = data.get('previous_image_messages', [])
    logger.debug("Deleting previous image messages: %s", previous_image_messages)

    
    for message_id in previous_image_messages:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=message_id
            )
            logger.debug("Deleted message ID %s", message_id)
        except Exception as e:
            logger.warning("Could not delete message %s: %s", message_id, e)
    
    # Clear the stored message IDs
    await state.update_data(previous_image_messages=[])
    logger.debug("Cleared previous_image_messages from state")


async def create_solution_flow(data: dict, username: str, status: str):
    logger.info("Creating solution flow for user %s with status %s", username, status)
    textbook_id = await upsert_textbook(data, status)
    chapter_id = await upsert_chapter(data, status, textbook_id)
    problem_id = await upsert_problem(data, status, chapter_id)

    logger.debug("Resolved IDs: textbook_id=%s, chapter_id=%s, problem_id=%s", textbook_id, chapter_id, problem_id)

    await save_solution_to_db(
        username = username,
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
    logger.debug("Upserting textbook: name=%s, id=%s", textbook_name, textbook_id)

    if textbook_id:
        return textbook_id
    
    textbook = await textbook_exists_by_name(textbook_name)
    if textbook:
        logger.info("Textbook already exists: %s", textbook_name)
        return textbook.id

    if textbook_name:
        textbook = await create_textbook(name=textbook_name, status=status)
        logger.info("Created new textbook: %s (id=%s)", textbook.name, textbook.id)
        return textbook.id
    return textbook_id


async def upsert_chapter(data: dict, status: str, textbook_id: int) -> int | None:
    chapter_name = data.get("chapter_name")
    chapter_id = safe_int(data.get("chapter_id"))
    logger.debug("Upserting chapter: name=%s, id=%s", chapter_name, chapter_id)
    if chapter_id:
        return chapter_id

    chapter = await check_chapter_name_for_textbook(textbook_id, chapter_name)
    if chapter:
        logger.info("Chapter already exists: %s", chapter_name)
        return chapter.id

    if chapter_name:
        chapter = await create_chapter(name=chapter_name, textbook_id=textbook_id, status=status)
        logger.info("Created new chapter: %s (id=%s)", chapter.name, chapter.id)
        return chapter.id
    return chapter_id


async def upsert_problem(data: dict, status: str, chapter_id: int) -> int | None:
    problem_name = data.get("problem_name")
    problem_id = safe_int(data.get("problem_id"))
    logger.debug("Upserting problem: name=%s, id=%s", problem_name, problem_id)

    if problem_id:
        return problem_id

    problem = await problem_exists_for_chapter(chapter_id, problem_name)
    if problem:
        logger.info("Problem already exists: %s", problem_name)
        return problem.id

    if problem_name:
        problem = await create_problem(name=problem_name, chapter_id=chapter_id, status=status)
        logger.info("Created new problem: %s (id=%s)", problem.name, problem.id)
        return problem.id
    return problem_id

async def get_solution_details(solution_id: int):
    logger.info("Fetching solution details for solution_id=%s", solution_id)
    solution = await get_solution_with_problem_by_id(solution_id)

    solution_text = format_solution_text(solution.problem, solution)
    keyboard = solution_detail_keyboard(solution.problem_id)

    file_ids = []
    if solution.image_file_ids:
        try:
            file_ids = json.loads(solution.image_file_ids)
            logger.debug("Parsed file_ids: %s", file_ids)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse image_file_ids JSON: %s", e)

    return solution_text, file_ids, keyboard


async def display_solution_details(callback: CallbackQuery, state: FSMContext):
    logger.info("Displaying solution details for callback: %s", callback.data)
    await delete_previous_images(callback, state)
    
    solution_id = int(callback.data.split("_")[-1])
    text, file_ids, keyboard = await get_solution_details(solution_id)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

    if file_ids:
        await send_and_track_images(callback, state, file_ids)

# Helper function to send images and track message IDs
async def send_and_track_images(callback: CallbackQuery, state: FSMContext, file_ids: list):
    """Send images and store their message IDs for later deletion"""
    logger.info("Sending %d images...", len(file_ids))
    sent_message_ids = []
    
    for file_id in file_ids:
        try:
            sent_message = await callback.message.answer_photo(file_id)
            sent_message_ids.append(sent_message.message_id)
            logger.debug("Sent image file_id: %s", file_id)
        except Exception as e:
            logger.warning("Could not send image %s: %s", file_id, e)

    # Store the message IDs in state for later cleanup
    await state.update_data(previous_image_messages=sent_message_ids)
    logger.debug("Updated previous_image_messages in state: %s", sent_message_ids)


async def prompt_add_solution(callback: CallbackQuery, state: FSMContext):
    logger.info("Prompting user to add solution")
    await delete_previous_images(callback, state)
    
    message_text = NEW_SOLUTION_PROMPT
    keyboard = await get_textbooks_keyboard("add")
    await callback.message.edit_text(message_text, reply_markup=keyboard)
    await state.set_state(AddSolutionStates.waiting_for_textbook)


async def handle_textbook_selection_for_solution(callback: CallbackQuery, state: FSMContext):
    textbook_id = int(callback.data.split("_")[-1])
    logger.info("Textbook selected: %s", textbook_id)
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

async def handle_solution_text_submission(message: Message, state: FSMContext):
    logger.info("Handling solution text submission: %s", message.text)
    if message.text.lower() == 'skip':
        await state.update_data(solution_text=None)
        logger.debug("User chose to skip solution text")
    else:
        await state.update_data(solution_text=message.text)
    
    keyboard = skip_cancel_keyboard()
    
    await message.answer(
        "Step 5: Send images for your solution (if any), or click 'Skip Images' to finish:",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_solution_image)

async def handle_solution_image_submission(message: Message, state: FSMContext):
    logger.info("Handling solution image submission")
    data = await state.get_data()
    image_file_ids = data.get('image_file_ids', [])
    image_file_ids.append(message.photo[-1].file_id)
    await state.update_data(image_file_ids=image_file_ids)
    new_file_id = message.photo[-1].file_id
    logger.debug("Received image file_id: %s", new_file_id)
    
    keyboard = finish_cancel_keyboard()
    
    await message.answer(
        "Image received! Send more images or click 'Finish' to save your solution:",
        reply_markup=keyboard
    )

async def finalize_solution_submission(callback: CallbackQuery, state: FSMContext):
    logger.info("Finalizing solution submission from user: %s", callback.from_user.username)
    full_name = callback.from_user.full_name or "Anonymous"

    if full_name != "Anonymous":
        # Prompt the user about if he wants to stay anonymous.
        keyboard = get_yes_no_keyboard()
        await callback.message.edit_text(
            "Do you want to be anonymous?",
            reply_markup=keyboard
        )
        await state.set_state(AddSolutionStates.waiting_for_anonymity_choice)
        return

    save_to_db_and_clear_state(callback, state, "Anonymous")

async def store_full_name(callback: CallbackQuery, state: FSMContext, anonymity_choice: str):
    if anonymity_choice == "anonymity_yes":
        logger.info("User chose to remain anonymous.")
        await save_to_db_and_clear_state(callback, state, "Anonymous")

    elif anonymity_choice == "anonymity_no":
        logger.info("User chose to show full name.")
        await save_to_db_and_clear_state(callback, state, callback.from_user.username)

async def save_to_db_and_clear_state(callback: CallbackQuery, state: FSMContext, username: str):
    data = await state.get_data()
    status = determine_submission_status(callback.from_user.username)

    result = await create_solution_flow(
        data=data,
        username=username,
        status=status
    )

    logger.info("Solution successfully created: %s", result)

    # Now Telegram-specific part stays in handler
    message_text = generate_success_message(status)
    await callback.message.edit_text(
        message_text,
        reply_markup=get_back_to_main_keyboard()
    )
    await state.clear()
    logger.debug("FSM state cleared")