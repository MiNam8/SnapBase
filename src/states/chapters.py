from aiogram.fsm.state import State, StatesGroup

class AddChapterStates(StatesGroup):
    waiting_for_chapter_name = State()