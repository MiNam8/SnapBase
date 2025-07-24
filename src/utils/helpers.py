import re

# -------------------- Validation helpers --------------------
def is_valid_textbook_name_length(name: str) -> bool:
    return len(name) >= 4

def is_valid_textbook_name_format(name: str) -> bool:
    pattern = r"^.+\s*-\s*.+\s*-\s*((\d+(st|nd|rd|th)? Edition,\s*\d{4})|\d{4})$"
    return re.match(pattern, name) is not None

def is_valid_chapter_name(name: str) -> bool:
    return len(name) > 0



# -------------------- Message formatting --------------------
def format_add_solution(textbook, chapter, problem):
    return (
        f"➕ Adding Solution to:\n"
        f"📖 Textbook: {textbook}\n"
        f"📑 Chapter: {chapter}\n"
        f"🧮 Problem: {problem}\n\n"
        "Step 4: Please send your solution text (or skip by sending 'skip'):"
    )

def format_select_solution(textbook, chapter, problem):
    return (
        f"➕ Adding Solution to:\n"
        f"📖 Textbook: {textbook}\n"
        f"📑 Chapter: {chapter}\n"
        f"🧮 Problem: {problem}\n\n"
        "Step 4: Please send your solution text (or skip by sending 'skip'):"
    )

def determine_submission_status(username: str) -> str:
    return "accepted" if username == "Iamer8" else "awaiting"

def generate_success_message(status: str) -> str:
    if status == "accepted":
        return "✅ Solution added and approved automatically!\n\nThank you for contributing to the textbook solutions!"
    return "✅ Your solution proposal is accepted, the admins will review it.\n\nThank you for contributing to the textbook solutions!"

def safe_int(value: str | None) -> int | None:
    return int(value) if value and value != "None" else None

def format_solution_text(problem, solution) -> str:
    text = f"📖 Textbook: {problem.chapter.textbook.name}\n"
    text += f"📑 Chapter: {problem.chapter.name}\n"
    text += f"🧮 Problem: {problem.name}\n"
    text += f"👤 Solved by: {solution.user_name}\n"
    text += f"📅 Created: {solution.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"

    if solution.text:
        text += f"📝 Solution:\n{solution.text}\n\n"
    
    return text
