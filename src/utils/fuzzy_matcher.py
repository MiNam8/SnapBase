from typing import List
from src.schemas import HasNameAndId
from thefuzz import fuzz
import logging

logger = logging.getLogger(__name__)


def get_best_fuzzy_matches(user_input: str, candidates: List[HasNameAndId]) -> List[HasNameAndId]:
    logger.info("Get potential candidates for the user input %s", user_input)

    potential_candidates = []
    for candidate in candidates:
        score = fuzz.ratio(user_input, candidate.name)
        logger.debug("User input: %s; candidate: %s; match-score: %s", user_input, candidate.name, score)
        if score > 90:
            potential_candidates.append(candidate)
            logger.info("Found potential candidate: %s", candidate.name)

    return potential_candidates
