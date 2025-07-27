from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.services.textbooks import finish_textbook_creation, finish_textbook_creation_in_solution_flow
from src.services.solutions import delete_previous_images
from src.keyboards.solutions import get_solutions_keyboard
from src.repositories.problems import get_problem
from src.utils.helpers import format_select_solution, format_add_solution, is_valid_problem_chapter_name
from src.states.solutions import AddSolutionStates
from src.states.problems import AddProblemStates
from src.keyboards.menu import get_cancel_keyboard
from src.constants.messages import NEW_PROBLEM_PROMPT, INVALID_PROBLEM_NAME, PROBLEM_ALREADY_EXISTS
from src.handlers.chapters import view_chapter_problems
from src.repositories.problems import check_problem_name_for_chapter


async def handle_textbook_flow(message: Message, state: FSMContext):
    data = await state.get_data()

    if data.get('in_solution_flow'):
        await finish_textbook_creation_in_solution_flow(message, state)
    else:
        await finish_textbook_creation(message, state)

async def view_solutions(callback: Message, state: FSMContext):
    await delete_previous_images(callback, state)
    
    problem_id = int(callback.data.split("_")[-1])
    
    problem = await get_problem(problem_id)
    
    keyboard = await get_solutions_keyboard(problem_id)
    msg = format_select_solution(problem.chapter.textbook.name, problem.chapter.name, problem.name)
    await callback.message.edit_text(msg, reply_markup=keyboard)

async def select_problem(callback: Message, state: FSMContext):
    problem_id = int(callback.data.split("_")[-1])
    await state.update_data(problem_id=problem_id)
    
    problem = await get_problem(problem_id)
    
    keyboard = get_cancel_keyboard()
    
    msg = format_add_solution(problem.chapter.textbook.name, problem.chapter.name, problem.name)

    await callback.message.edit_text(msg, reply_markup=keyboard)
    await state.set_state(AddSolutionStates.waiting_for_solution_text)

async def new_problem(callback: Message, state: FSMContext):
    chapter_id = callback.data.split("_")[-1]
    await state.update_data(chapter_id=chapter_id)

    await state.set_state(AddProblemStates.waiting_for_problem_name)

    keyboard = get_cancel_keyboard()
    message_text = NEW_PROBLEM_PROMPT

    await callback.message.edit_text(message_text, reply_markup=keyboard)

async def save_problem(message: Message, state: FSMContext):
    problem_name = message.text.strip()
    
    if not is_valid_problem_chapter_name(problem_name):
        await message.answer(INVALID_PROBLEM_NAME)
        return

    data = await state.get_data()
    chapter_id = None
    if data.get("chapter_id") != "None":
        chapter_id = int(data.get("chapter_id"))

    if chapter_id and await check_problem_name_for_chapter(chapter_id, problem_name):
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

async def back_problems(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating back
    await delete_previous_images(callback, state)
    
    parts = callback.data.split("_")
    action_prefix = parts[3]
    chapter_id = int(parts[4])
    
    if action_prefix == "view":
        await view_chapter_problems(CallbackQuery(
            id=callback.id,
            from_user=callback.from_user,
            chat_instance=callback.chat_instance,
            message=callback.message,
            data=f"view_chapter_{chapter_id}"
        ), state)
