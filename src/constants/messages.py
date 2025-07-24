ADD_TEXTBOOK_PROMPT = (
    "📖 Add a New Textbook\n\n"
    "✍️ Please enter the textbook information in the following format:\n\n"
    "👉 [Title] - [Author] - [Edition, Year]\n"
    "📌 Example: Calculus - James Stewart - 8th Edition, 2016\n\n"
    "❗ If there's no edition, you can write:\n"
    "👉 [Title] - [Author] - Year\n"
    "📌 Example: Linear Algebra - Gilbert Strang - 2014\n\n"
    "✅ This helps us keep the database clean and searchable."
)

INVALID_TEXTBOOK_NAME = (
    "❌ Invalid format. Please use:\n\n"
            "👉 Title - Author - Edition, Year\n"
            "📌 Example: Calculus - James Stewart - 8th Edition, 2016\n\n"
            "👉 Or: Title - Author - Year\n"
            "📌 Example: Linear Algebra - Gilbert Strang - 2014"
)

ERROR_TEXTBOOK_EXISTS = "❌ A textbook with the name '{name}' already exists or is currently awaiting admin review."
SUCCESS_TEXTBOOK_CREATED = "✅ Textbook name: {name}\nAdd a chapter to the textbook."



STEP2_SELECT_CHAPTER = (
    "➕ Add Solution to: {name}\n\n"
    "Step 2: Select the chapter:"
)

CHAPTER_NOT_FOUND = "❌ Chapter not found or not accepted."
TEXTBOOK_NOT_FOUND_CHAPTER = "❌ Could not determine which textbook to add a chapter to."
CHAPTER_NAME_PROMPT = "📝 Please enter the name of the new chapter:"
EMPTY_CHAPTER_ERROR = "❌ Chapter name must be at least 1 character. Please enter a valid name:"
CHAPTER_ALREADY_EXISTS = "❌ This chapter already exists in the selected textbook."


INVALID_PROBLEM_NAME = "❌ Problem name must be at least 1 character. Please enter a valid name:"
SOLUTION_STEP_MESSAGE_TEMPLATE = (
    "➕ Adding Solution to:\n"
    "📖 Textbook: {textbook_name}\n"
    "📑 Chapter: {chapter_name}\n"
    "🧮 Problem: {problem_name}\n\n"
    "Step 4: Please send your solution text (or skip by sending 'skip' without braces):"
)
