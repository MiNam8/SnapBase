from src.db.models import Textbook, async_session
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

async def get_accepted_textbook_by_id(textbook_id: int) -> Textbook:
    logger.debug("Fetching accepted textbook with ID: %s", {textbook_id})
    async with async_session() as session:
            result = await session.execute(
                select(Textbook).where(Textbook.id == textbook_id,
                                    Textbook.status == "accepted")
            )
            textbook = result.scalar_one()
            logger.info("Accepted textbook found: %s (ID: %s)", textbook.name, textbook.id)
            return textbook


async def textbook_exists_by_name(textbook_name: str) -> Textbook:
        logger.debug("Checking if textbook exists by name: %s", textbook_name)
        async with async_session() as session:
                result = await session.execute(select(Textbook).where(Textbook.name == textbook_name))
                textbook = result.scalar_one_or_none()
                if textbook:
                        logger.info(f"Textbook found: {textbook.name} (ID: {textbook.id})")
                else:
                        logger.info(f"No textbook found with name: {textbook_name}")
                return textbook


async def create_textbook(name: str, status: str) -> Textbook:
        logger.info("Creating textbook with name: %s, status: %s", name, status)
        async with async_session() as session:
                textbook = Textbook(name=name, status=status)
                session.add(textbook)
                await session.commit()
                await session.refresh(textbook)
                logger.info("Textbook created: %s (ID: %s)", textbook.name, textbook.id)
                return textbook