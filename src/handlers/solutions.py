from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.states.solutions import AddSolutionStates
from src.services.solutions import display_solution_details, prompt_add_solution, handle_textbook_selection_for_solution, handle_solution_text_submission, handle_solution_image_submission, finalize_solution_submission

router = Router()

@router.callback_query(F.data.startswith("view_solution_"))
async def view_solution_details(callback: CallbackQuery, state: FSMContext):
    await display_solution_details(callback, state)


@router.callback_query(F.data == "add_solution")
async def start_add_solution(callback: CallbackQuery, state: FSMContext):
    await prompt_add_solution(callback, state)

@router.callback_query(F.data.startswith("add_textbook_"))
async def select_textbook_for_solution(callback: CallbackQuery, state: FSMContext):
    await handle_textbook_selection_for_solution(callback, state)


@router.message(AddSolutionStates.waiting_for_solution_text)
async def receive_solution_text(message: Message, state: FSMContext):
    await handle_solution_text_submission(message, state)

@router.message(AddSolutionStates.waiting_for_solution_image, F.photo)
async def receive_solution_image(message: Message, state: FSMContext):
    await handle_solution_image_submission(message, state)

@router.callback_query(F.data.in_(["skip_images", "finish_solution"]))
async def finish_solution(callback: CallbackQuery, state: FSMContext):
    await finalize_solution_submission(callback, state)