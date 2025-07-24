from aiogram.fsm.state import State, StatesGroup

class AddSolutionStates(StatesGroup):
    waiting_for_textbook = State()
    waiting_for_chapter = State()
    waiting_for_problem = State()
    waiting_for_solution_text = State()
    waiting_for_solution_image = State()

class ImageTrackingState(StatesGroup):
    has_images = State()