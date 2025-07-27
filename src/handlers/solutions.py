from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.states.solutions import AddSolutionStates
from src.services.solutions import solution_details, add_solution, textbook_for_solution, receive_text, receive_image, final_solution_state

router = Router()

@router.callback_query(F.data.startswith("view_solution_"))
async def view_solution_details(callback: CallbackQuery, state: FSMContext):
    await solution_details(callback, state)


@router.callback_query(F.data == "add_solution")
async def start_add_solution(callback: CallbackQuery, state: FSMContext):
    await add_solution(callback, state)

@router.callback_query(F.data.startswith("add_textbook_"))
async def select_textbook_for_solution(callback: CallbackQuery, state: FSMContext):
    await textbook_for_solution(callback, state)


@router.message(AddSolutionStates.waiting_for_solution_text)
async def receive_solution_text(message: Message, state: FSMContext):
    await receive_text(message, state)

@router.message(AddSolutionStates.waiting_for_solution_image, F.photo)
async def receive_solution_image(message: Message, state: FSMContext):
    await receive_image(message, state)

@router.callback_query(F.data.in_(["skip_images", "finish_solution"]))
async def finish_solution(callback: CallbackQuery, state: FSMContext):
    await final_solution_state(callback, state)