from src.repositories.textbooks import get_accepted_textbook_by_id
from src.db.models import Textbook, async_session
from src.constants.messages import ERROR_TEXTBOOK_EXISTS, SUCCESS_TEXTBOOK_CREATED
from src.repositories.textbooks import exists_by_name, create_textbook
from src.constants.messages import STEP2_SELECT_CHAPTER
from typing import Tuple

async def fetch_textbook_for_viewing(textbook_id: int) -> Textbook:
    textbook = await get_accepted_textbook_by_id(textbook_id)
    return textbook

async def create_textbook_if_not_exists(name: str) -> tuple[bool, str]:
        async with async_session() as session:
            exists = await exists_by_name(session, name)
            if exists:
                return False, ERROR_TEXTBOOK_EXISTS.format(name=name)

            # Optionally: await TextbookRepository.create(session, name)
            return True, SUCCESS_TEXTBOOK_CREATED.format(name=name)
        
async def create_textbook_and_return_id(name: str) -> Tuple[bool, str, int]:
        async with async_session() as session:
            if await exists_by_name(session, name):
                return False, ERROR_TEXTBOOK_EXISTS.format(name=name), None
            
            new_textbook = await create(session, name)
            return True, STEP2_SELECT_CHAPTER.format(name=name), new_textbook.id