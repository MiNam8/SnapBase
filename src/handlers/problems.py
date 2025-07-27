from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.services.solutions import delete_previous_images
from src.states.problems import AddProblemStates
from src.handlers.chapters import view_chapter_problems
from src.services.problems import view_solutions, select_problem, new_problem, save_problem, back_problems

router = Router()

@router.callback_query(F.data.startswith("view_problem_"))
async def view_problem_solutions(callback: CallbackQuery, state: FSMContext):
    await view_solutions(callback, state)    

@router.callback_query(F.data.startswith("add_problem_"))
async def select_problem_for_solution(callback: CallbackQuery, state: FSMContext):
    await select_problem(callback, state)


@router.callback_query(F.data.startswith("add_new_problem"))
async def add_new_problem(callback: CallbackQuery, state: FSMContext):
    await new_problem(callback, state)


@router.message(AddProblemStates.waiting_for_problem_name)
async def save_new_problem(message: Message, state: FSMContext):
    await save_problem(message, state)


@router.callback_query(F.data.startswith("back_to_problems_"))
async def back_to_problems(callback: CallbackQuery, state: FSMContext):
    await back_problems(callback, state)