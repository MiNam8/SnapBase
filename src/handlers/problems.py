from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.states.problems import AddProblemStates
from src.services.problems import display_problem_solutions, handle_problem_selection, prompt_add_problem, save_problem, handle_back_to_problems

router = Router()

@router.callback_query(F.data.startswith("view_problem_"))
async def view_problem_solutions(callback: CallbackQuery, state: FSMContext):
    await display_problem_solutions(callback, state)    

@router.callback_query(F.data.startswith("add_problem_"))
async def select_problem_for_solution(callback: CallbackQuery, state: FSMContext):
    await handle_problem_selection(callback, state)


@router.callback_query(F.data.startswith("add_new_problem"))
async def add_new_problem(callback: CallbackQuery, state: FSMContext):
    await prompt_add_problem(callback, state)


@router.message(AddProblemStates.waiting_for_problem_name)
async def save_new_problem(message: Message, state: FSMContext):
    await save_problem(message, state)


@router.callback_query(F.data.startswith("back_to_problems_"))
async def back_to_problems(callback: CallbackQuery, state: FSMContext):
    await handle_back_to_problems(callback, state)