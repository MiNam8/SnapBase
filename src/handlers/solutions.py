from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.states.solutions import AddSolutionStates
from src.services.solutions import display_solution_details, prompt_add_solution, handle_textbook_selection_for_solution, handle_solution_text_submission, handle_solution_image_submission, finalize_solution_submission, store_full_name
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data.startswith("view_solution_"))
async def view_solution_details(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s, triggered 'view_solution_details' with data: %s", callback.from_user.id, callback.data)
    await display_solution_details(callback, state)


@router.callback_query(F.data == "add_solution")
async def start_add_solution(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s, triggered 'start_add_solution' with data: %s", callback.from_user.id, callback.data)
    await prompt_add_solution(callback, state)

@router.callback_query(F.data.startswith("add_textbook_"))
async def select_textbook_for_solution(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s, triggered 'select_textbook_for_solution' with data: %s", callback.from_user.id, callback.data)
    await handle_textbook_selection_for_solution(callback, state)


@router.message(AddSolutionStates.waiting_for_solution_text)
async def receive_solution_text(message: Message, state: FSMContext):
    logger.info("User %s sent solution text: %s", message.from_user.id, message.text)
    await handle_solution_text_submission(message, state)

@router.message(AddSolutionStates.waiting_for_solution_image, F.photo)
async def receive_solution_image(message: Message, state: FSMContext):
    logger.info("User %s sent solution image(s): %s", message.from_user.id, message.photo)
    await handle_solution_image_submission(message, state)

@router.callback_query(F.data.in_(["skip_images", "finish_solution"]))
async def finish_solution(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s, triggered 'finish_solution' with data: %s", callback.from_user.id, callback.data)
    await finalize_solution_submission(callback, state)

@router.callback_query(F.data.in_(["anonymity_yes", "anonymity_no"]))
async def anonymity_check(callback: CallbackQuery, state: FSMContext):
    logger.info("User %s, triggered 'store_full_name' with data: %s", callback.from_user.id, callback.data)
    await store_full_name(callback, state, anonymity_choice=callback.data)
