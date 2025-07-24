from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from src.utils.helpers import safe_int
from src.repositories.chapters import create_chapter
from src.repositories.problems import create_problem
from src.repositories.textbooks import create_textbook
from src.repositories.solutions import save_solution_to_db, get_solution_with_problem_by_id
from src.utils.helpers import format_solution_text
from src.keyboards.solutions import solution_detail_keyboard 
import json

async def delete_previous_images(callback: CallbackQuery, state: FSMContext):
    """Delete previously sent image messages"""
    data = await state.get_data()
    previous_image_messages = data.get('previous_image_messages', [])
    
    for message_id in previous_image_messages:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=message_id
            )
        except Exception as e:
            # Message might already be deleted or not exist
            print(f"Could not delete message {message_id}: {e}")
    
    # Clear the stored message IDs
    await state.update_data(previous_image_messages=[])


async def create_solution_flow(data: dict, username: str, full_name: str, status: str):
    textbook_id = await upsert_textbook(data, status)
    chapter_id = await upsert_chapter(data, status, textbook_id)
    problem_id = await upsert_problem(data, status, chapter_id)

    await save_solution_to_db(
        username = username,
        full_name = full_name,
        data=data,
        problem_id=problem_id,
        status=status
    )

    return {
        "status": status,
        "textbook_id": textbook_id,
        "chapter_id": chapter_id,
        "problem_id": problem_id,
    }

async def upsert_textbook(data: dict, status: str) -> int | None:
    textbook_name = data.get("textbook_name")
    textbook_id = safe_int(data.get("textbook_id"))
    if textbook_id:
        return textbook_id
    
    if textbook_name:
        textbook = await create_textbook(name=textbook_name, status=status)
        return textbook.id
    return textbook_id


async def upsert_chapter(data: dict, status: str, textbook_id: int) -> int | None:
    chapter_name = data.get("chapter_name")
    chapter_id = safe_int(data.get("chapter_id"))
    if chapter_id:
        return chapter_id

    if chapter_name:
        chapter = await create_chapter(name=chapter_name, textbook_id=textbook_id, status=status)
        return chapter.id
    return chapter_id


async def upsert_problem(data: dict, status: str, chapter_id: int) -> int | None:
    problem_name = data.get("problem_name")
    problem_id = safe_int(data.get("problem_id"))
    if problem_id:
        return problem_id

    if problem_name:
        problem = await create_problem(name=problem_name, chapter_id=chapter_id, status=status)
        return problem.id
    return problem_id

async def get_solution_details(solution_id: int):
    solution = await get_solution_with_problem_by_id(solution_id)

    solution_text = format_solution_text(solution.problem, solution)
    keyboard = solution_detail_keyboard(solution.problem_id)

    file_ids = []
    if solution.image_file_ids:
        try:
            file_ids = json.loads(solution.image_file_ids)
        except json.JSONDecodeError:
            pass

    return solution_text, file_ids, keyboard
