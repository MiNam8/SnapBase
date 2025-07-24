from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.handlers.textbooks import finish_textbook_creation, finish_textbook_creation_in_solution_flow

async def handle_textbook_flow(message: Message, state: FSMContext):
    data = await state.get_data()

    if data.get('in_solution_flow'):
        await finish_textbook_creation_in_solution_flow(message, state)
    else:
        await finish_textbook_creation(message, state)
