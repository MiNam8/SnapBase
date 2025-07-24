from aiogram.fsm.state import State, StatesGroup

class AddProblemStates(StatesGroup):
    waiting_for_problem_name = State()