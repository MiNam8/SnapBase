from src.db.models import Textbook, async_session
from src.repositories.chapters import get_accepted_with_textbook

async def get_accepted_chapter_with_textbook(chapter_id: int):
        async with async_session() as session:
            return await get_accepted_with_textbook(session, chapter_id)
        
async def try_add_chapter()