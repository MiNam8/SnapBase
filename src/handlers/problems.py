from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.db.models import async_session, Chapter, Problem
from src.handlers.solutions import delete_previous_images
from src.keyboards.solutions import get_solutions_keyboard
from src.states.solutions import AddSolutionStates
from src.states.problems import AddProblemStates
from src.handlers.chapters import view_chapter_problems
from src.repositories.problems import get_problem
from src.constants.messages import INVALID_PROBLEM_NAME, SOLUTION_STEP_MESSAGE_TEMPLATE
from src.utils.helpers import format_add_solution, format_select_solution

router = Router()

@router.callback_query(F.data.startswith("view_problem_"))
async def view_problem_solutions(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating
    await delete_previous_images(callback, state)
    
    problem_id = int(callback.data.split("_")[-1])
    
    problem = await get_problem(problem_id)
    
    keyboard = await get_solutions_keyboard(problem_id)
    msg = format_select_solution(problem.chapter.textbook.name, problem.chapter.name, problem.name)
    await callback.message.edit_text(msg, reply_markup=keyboard)


@router.callback_query(F.data.startswith("add_problem_"))
async def select_problem_for_solution(callback: CallbackQuery, state: FSMContext):
    problem_id = int(callback.data.split("_")[-1])
    await state.update_data(problem_id=problem_id)
    
    problem = await get_problem(problem_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])
    
    msg = format_add_solution(problem.chapter.textbook.name, problem.chapter.name, problem.name)

    await callback.message.edit_text(msg, reply_markup=keyboard)
    await state.set_state(AddSolutionStates.waiting_for_solution_text)


@router.callback_query(F.data.startswith("add_new_problem"))
async def add_new_problem(callback: CallbackQuery, state: FSMContext):
    chapter_id = callback.data.split("_")[-1]
    await state.update_data(chapter_id=chapter_id)

    await state.set_state(AddProblemStates.waiting_for_problem_name)
    await callback.message.edit_text(
        "📝 Please enter the name of the new problem:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
        ])
    )

@router.message(AddProblemStates.waiting_for_problem_name)
async def save_new_problem(message: Message, state: FSMContext):
    problem_name = message.text.strip()
    
    if len(problem_name) < 1:
        await message.answer(INVALID_PROBLEM_NAME)
        return

    data = await state.get_data()
    if data.get("chapter_id") != "None":
        chapter_id = int(data.get("chapter_id"))
        
    textbook_name = data.get("textbook_name")
    chapter_name = data.get("chapter_name")
    await state.update_data(problem_name=problem_name)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])
    
    msg = format_add_solution(textbook_name, chapter_name, problem_name)

    await message.answer(msg, reply_markup=keyboard)

    # Continue to solution text input step
    await state.set_state(AddSolutionStates.waiting_for_solution_text)


@router.callback_query(F.data.startswith("back_to_problems_"))
async def back_to_problems(callback: CallbackQuery, state: FSMContext):
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
