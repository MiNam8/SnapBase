from aiogram.fsm.state import State, StatesGroup

class AddTextbookStates(StatesGroup):
    waiting_for_textbook_name = State()
    waiting_for_textbook_description = State()