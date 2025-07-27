from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.states.textbooks import AddTextbookStates
from src.services.textbooks import process_textbook_name, get_textbooks, add_textbook_flow, add_textbook, move_to_textbooks
from src.services.chapters import get_chapters

router = Router()

@router.callback_query(F.data == "browse_textbooks")
async def browse_textbooks(callback: CallbackQuery, state: FSMContext):
    await get_textbooks(callback, state)


@router.callback_query(F.data.startswith("view_textbook_"))
async def view_textbook_chapters(callback: CallbackQuery, state: FSMContext):
    await get_chapters(callback, state)


@router.callback_query(F.data == "add_textbook_in_solution_flow")
async def add_textbook_in_solution_flow(callback: CallbackQuery, state: FSMContext):
    await add_textbook_flow(callback, state)

# Add Textbook Flow
@router.callback_query(F.data == "add_textbook")
async def start_add_textbook(callback: CallbackQuery, state: FSMContext):
    await add_textbook(callback, state)


@router.message(AddTextbookStates.waiting_for_textbook_name)
async def receive_textbook_name(message: Message, state: FSMContext):
    await process_textbook_name(message, state)

@router.callback_query(F.data.startswith("back_to_textbooks_"))
async def back_to_textbooks(callback: CallbackQuery, state: FSMContext):
    await move_to_textbooks(callback, state)
