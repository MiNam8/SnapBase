from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.services.textbooks import finish_textbook_creation, finish_textbook_creation_in_solution_flow
from src.services.solutions import delete_previous_images
from src.keyboards.solutions import get_solutions_keyboard
from src.repositories.problems import fetch_problem_with_chapter_and_textbook
from src.utils.helpers import format_select_solution, format_add_solution, is_valid_problem_chapter_name
from src.states.solutions import AddSolutionStates
from src.states.problems import AddProblemStates
from src.keyboards.menu import get_cancel_keyboard
from src.constants.messages import NEW_PROBLEM_PROMPT, INVALID_PROBLEM_NAME, PROBLEM_ALREADY_EXISTS
from src.handlers.chapters import view_chapter_problems
from src.repositories.problems import problem_exists_for_chapter
import logging

logger = logging.getLogger(__name__)

async def handle_textbook_flow(message: Message, state: FSMContext):
    data = await state.get_data()
    logger.info("Handling textbook flow. in_solution_flow: %s", data.get('in_solution_flow'))

    if data.get('in_solution_flow'):
        await finish_textbook_creation_in_solution_flow(message, state)
    else:
        await finish_textbook_creation(message, state)

async def display_problem_solutions(callback: Message, state: FSMContext):
    logger.info("Displaying solutions for problem. Callback data: %s", callback.data)
    await delete_previous_images(callback, state)
    
    problem_id = int(callback.data.split("_")[-1])
    logger.debug("Parsed problem_id: %d", problem_id)
    
    problem = await fetch_problem_with_chapter_and_textbook(problem_id)
    
    keyboard = await get_solutions_keyboard(problem_id)
    msg = format_select_solution(problem.chapter.textbook.name, problem.chapter.name, problem.name)
    await callback.message.edit_text(msg, reply_markup=keyboard)

async def handle_problem_selection(callback: Message, state: FSMContext):
    logger.info("Handling problem selection. Callback data: %s", callback.data)
    problem_id = int(callback.data.split("_")[-1])
    await state.update_data(problem_id=problem_id)
    
    problem = await fetch_problem_with_chapter_and_textbook(problem_id)
    
    keyboard = get_cancel_keyboard()
    
    msg = format_add_solution(problem.chapter.textbook.name, problem.chapter.name, problem.name)

    await callback.message.edit_text(msg, reply_markup=keyboard)
    await state.set_state(AddSolutionStates.waiting_for_solution_text)

async def prompt_add_problem(callback: Message, state: FSMContext):
    chapter_id = callback.data.split("_")[-1]
    logger.info("Prompting to add problem to chapter_id: %s", chapter_id)

    await state.update_data(chapter_id=chapter_id)
    await state.set_state(AddProblemStates.waiting_for_problem_name)

    keyboard = get_cancel_keyboard()
    message_text = NEW_PROBLEM_PROMPT

    await callback.message.edit_text(message_text, reply_markup=keyboard)

async def save_problem(message: Message, state: FSMContext):
    problem_name = message.text.strip()
    logger.info("Saving problem. Name: %s", problem_name)
    
    if not is_valid_problem_chapter_name(problem_name):
        logger.warning("Invalid problem name received: %s", problem_name)
        await message.answer(INVALID_PROBLEM_NAME)
        return

    data = await state.get_data()
    chapter_id = None
    logger.debug("Extracted chapter_id: %s", chapter_id)
    if data.get("chapter_id") != "None":
        chapter_id = int(data.get("chapter_id"))

    if chapter_id and await problem_exists_for_chapter(chapter_id, problem_name):
        logger.info("Problem already exists for chapter_id %d: %s", chapter_id, problem_name)
        keyboard = get_cancel_keyboard()
        await message.answer(PROBLEM_ALREADY_EXISTS, reply_markup=keyboard)
        return

    textbook_name = data.get("textbook_name")
    chapter_name = data.get("chapter_name")
    await state.update_data(problem_name=problem_name)

    keyboard = get_cancel_keyboard()
    msg = format_add_solution(textbook_name, chapter_name, problem_name)

    await message.answer(msg, reply_markup=keyboard)

    # Continue to solution text input step
    await state.set_state(AddSolutionStates.waiting_for_solution_text)

async def handle_back_to_problems(callback: CallbackQuery, state: FSMContext):
    logger.info("Handling back to problems. Callback data: %s", callback.data)
    await delete_previous_images(callback, state)
    
    parts = callback.data.split("_")
    if len(parts) < 5:
        logger.warning("Unexpected callback data format: %s", callback.data)
        return
    
    action_prefix = parts[3]
    chapter_id = int(parts[4])
    logger.debug("Parsed action_prefix: %s, chapter_id: %d", action_prefix, chapter_id)
    
    if action_prefix == "view":
        logger.info("Redirecting to view_chapter_problems for chapter_id: %d", chapter_id)
        await view_chapter_problems(CallbackQuery(
            id=callback.id,
            from_user=callback.from_user,
            chat_instance=callback.chat_instance,
            message=callback.message,
            data=f"view_chapter_{chapter_id}"
        ), state)
