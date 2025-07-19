# from aiogram import Router, F
# from aiogram.filters import CommandStart
# from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from sqlalchemy import select
# from sqlalchemy.orm import selectinload
# from src.db.models import async_session, Textbook, Chapter, Problem, Solution
# import json

# router = Router()

# # FSM States for adding solutions
# class AddSolutionStates(StatesGroup):
#     waiting_for_textbook = State()
#     waiting_for_chapter = State()
#     waiting_for_problem = State()
#     waiting_for_solution_text = State()
#     waiting_for_solution_image = State()

# # FSM States for adding textbooks
# class AddTextbookStates(StatesGroup):
#     waiting_for_textbook_name = State()
#     waiting_for_textbook_description = State()

# class AddChapterStates(StatesGroup):
#     waiting_for_chapter_name = State()

# class AddProblemStates(StatesGroup):
#     waiting_for_problem_name = State()

# # Main menu keyboard
# def get_main_menu_keyboard():
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="📚 Browse Textbooks", callback_data="browse_textbooks")],
#         [InlineKeyboardButton(text="➕ Add Solution", callback_data="add_solution")],
#         [InlineKeyboardButton(text="📖 Add Textbook", callback_data="add_textbook")],
#         [InlineKeyboardButton(text="❓ Help", callback_data="help")]
#     ])
#     return keyboard

# # Back to main menu keyboard
# def get_back_to_main_keyboard():
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="🏠 Back to Main Menu", callback_data="main_menu")]
#     ])
#     return keyboard

# # Textbooks keyboard
# async def get_textbooks_keyboard(action_prefix="view"):
#     async with async_session() as session:
#         result = await session.execute(select(Textbook))
#         textbooks = result.scalars().all()
#         keyboard_buttons = []
#         for textbook in textbooks:
#             callback_data = f"{action_prefix}_textbook_{textbook.id}"
#             keyboard_buttons.append([InlineKeyboardButton(
#                 text=f"📖 {textbook.name}", 
#                 callback_data=callback_data
#             )])

#         keyboard_buttons.append([InlineKeyboardButton(text="🏠 Back to Main Menu", callback_data="main_menu")])
#         return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

# # Chapters keyboard
# async def get_chapters_keyboard(textbook_id: int, action_prefix="view"):
#     async with async_session() as session:
#         result = await session.execute(
#             select(Chapter).where(Chapter.textbook_id == textbook_id)
#         )
#         chapters = result.scalars().all()
        
#         keyboard_buttons = []
#         for chapter in chapters:
#             callback_data = f"{action_prefix}_chapter_{chapter.id}"
#             keyboard_buttons.append([InlineKeyboardButton(
#                 text=f"📑 {chapter.name}", 
#                 callback_data=callback_data
#             )])
        
#         if action_prefix == "add":
#             keyboard_buttons.append([
#                 InlineKeyboardButton(text="➕ Add new chapter", callback_data=f"add_new_chapter_{textbook_id}")
#             ])

#         keyboard_buttons.append([
#                 InlineKeyboardButton(text="⬅️ Back to Textbooks", callback_data=f"back_to_textbooks_{action_prefix}"),
#                 InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
#             ])
#         return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

# # Problems keyboard
# async def get_problems_keyboard(chapter_id: int, action_prefix="view"):
#     async with async_session() as session:
#         result = await session.execute(
#             select(Problem).where(Problem.chapter_id == chapter_id)
#         )
#         problems = result.scalars().all()
        
#         keyboard_buttons = []
#         for problem in problems:
#             callback_data = f"{action_prefix}_problem_{problem.id}"
#             keyboard_buttons.append([InlineKeyboardButton(
#                 text=f"🧮 {problem.name}", 
#                 callback_data=callback_data
#             )])
        
#         # Get textbook_id for back navigation
#         chapter_result = await session.execute(
#             select(Chapter).where(Chapter.id == chapter_id)
#         )
#         chapter = chapter_result.scalar_one()
        
#         if action_prefix == "add":
#             keyboard_buttons.append([
#                 InlineKeyboardButton(text="➕ Add new problem", callback_data=f"add_new_problem_{chapter_id}")
#             ])

#         keyboard_buttons.append([
#             InlineKeyboardButton(text="⬅️ Back to Chapters", callback_data=f"back_to_chapters_{action_prefix}_{chapter.textbook_id}"),
#             InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
#         ])
#         return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

# # Solutions keyboard
# async def get_solutions_keyboard(problem_id: int):
#     async with async_session() as session:
#         result = await session.execute(
#             select(Solution).where(Solution.problem_id == problem_id)
#         )
#         solutions = result.scalars().all()
        
#         keyboard_buttons = []
#         for i, solution in enumerate(solutions, 1):
#             callback_data = f"view_solution_{solution.id}"
#             keyboard_buttons.append([InlineKeyboardButton(
#                 text=f"📝 Solution {i} by {solution.user_name}", 
#                 callback_data=callback_data
#             )])
        
#         # Get chapter_id for back navigation
#         problem_result = await session.execute(
#             select(Problem).where(Problem.id == problem_id)
#         )
#         problem = problem_result.scalar_one()
        
#         keyboard_buttons.append([
#             InlineKeyboardButton(text="⬅️ Back to Problems", callback_data=f"back_to_problems_view_{problem.chapter_id}"),
#             InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
#         ])
#         return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

# @router.message(CommandStart())
# async def cmd_start(message: Message):
#     await message.answer(
#         "🎓 Welcome to the Textbook Solutions Bot!\n\n"
#         "Choose an option below to get started:",
#         reply_markup=get_main_menu_keyboard()
#     )

# @router.callback_query(F.data == "main_menu")
# async def show_main_menu(callback: CallbackQuery, state: FSMContext):
#     print("STATE JUST BEFORE CLEARING IT:", state, callback)
#     await state.clear()
#     await callback.message.edit_text(
#         "🎓 Welcome to the Textbook Solutions Bot!\n\n"
#         "Choose an option below to get started:",
#         reply_markup=get_main_menu_keyboard()
#     )

# @router.callback_query(F.data == "browse_textbooks")
# async def browse_textbooks(callback: CallbackQuery):
#     keyboard = await get_textbooks_keyboard("view")
#     await callback.message.edit_text(
#         "📚 Available Textbooks:\n\n"
#         "Select a textbook to browse its chapters:",
#         reply_markup=keyboard
#     )

# @router.callback_query(F.data.startswith("view_textbook_"))
# async def view_textbook_chapters(callback: CallbackQuery, state: FSMContext):
#     textbook_id = int(callback.data.split("_")[-1])
    
#     async with async_session() as session:
#         result = await session.execute(
#             select(Textbook).where(Textbook.id == textbook_id)
#         )
#         textbook = result.scalar_one()

#     state.update_data(textbook_id=textbook_id)
#     data = await state.get_data()

#     keyboard = await get_chapters_keyboard(textbook_id, "view")
#     await callback.message.edit_text(
#         f"📖 Textbook: {textbook.name}\n\n"
#         "Select a chapter to view its problems:",
#         reply_markup=keyboard
#     )

# @router.callback_query(F.data.startswith("view_chapter_"))
# async def view_chapter_problems(callback: CallbackQuery):
#     chapter_id = int(callback.data.split("_")[-1])
    
#     async with async_session() as session:
#         result = await session.execute(
#             select(Chapter).options(selectinload(Chapter.textbook)).where(Chapter.id == chapter_id)
#         )
#         chapter = result.scalar_one()
    
#     keyboard = await get_problems_keyboard(chapter_id, "view")
#     await callback.message.edit_text(
#         f"📖 Textbook: {chapter.textbook.name}\n"
#         f"📑 Chapter: {chapter.name}\n\n"
#         "Select a problem to view its solutions:",
#         reply_markup=keyboard
#     )

# @router.callback_query(F.data.startswith("view_problem_"))
# async def view_problem_solutions(callback: CallbackQuery):
#     problem_id = int(callback.data.split("_")[-1])
    
#     async with async_session() as session:
#         result = await session.execute(
#             select(Problem).options(
#                 selectinload(Problem.chapter).selectinload(Chapter.textbook)
#             ).where(Problem.id == problem_id)
#         )
#         problem = result.scalar_one()
    
#     keyboard = await get_solutions_keyboard(problem_id)
#     await callback.message.edit_text(
#         f"📖 Textbook: {problem.chapter.textbook.name}\n"
#         f"📑 Chapter: {problem.chapter.name}\n"
#         f"🧮 Problem: {problem.name}\n\n"
#         "Select a solution to view:",
#         reply_markup=keyboard
#     )

# @router.callback_query(F.data.startswith("view_solution_"))
# async def view_solution_details(callback: CallbackQuery):
#     solution_id = int(callback.data.split("_")[-1])
    
#     async with async_session() as session:
#         result = await session.execute(
#             select(Solution).options(
#                 selectinload(Solution.problem).selectinload(Problem.chapter).selectinload(Chapter.textbook)
#             ).where(Solution.id == solution_id)
#         )
#         solution = result.scalar_one()
    
#     solution_text = f"📖 Textbook: {solution.problem.chapter.textbook.name}\n"
#     solution_text += f"📑 Chapter: {solution.problem.chapter.name}\n"
#     solution_text += f"🧮 Problem: {solution.problem.name}\n"
#     solution_text += f"👤 Solved by: {solution.user_name}\n"
#     solution_text += f"📅 Created: {solution.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    
#     if solution.text:
#         solution_text += f"📝 Solution:\n{solution.text}\n\n"
    
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="⬅️ Back to Solutions", callback_data=f"view_problem_{solution.problem_id}")],
#         [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
#     ])
    
#     await callback.message.edit_text(solution_text, reply_markup=keyboard)
    
#     # Send images if any
#     if solution.image_file_ids:
#         try:
#             file_ids = json.loads(solution.image_file_ids)
#             for file_id in file_ids:
#                 await callback.message.answer_photo(file_id)
#         except json.JSONDecodeError:
#             pass

# # Add Textbook Flow
# @router.callback_query(F.data == "add_textbook")
# async def start_add_textbook(callback: CallbackQuery, state: FSMContext):
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
#     ])
    
#     await callback.message.edit_text(
#         "📖 Add a New Textbook\n\n"
#         "Step 1: Please enter the textbook name:",
#         reply_markup=keyboard
#     )
#     await state.set_state(AddTextbookStates.waiting_for_textbook_name)

# @router.message(AddTextbookStates.waiting_for_textbook_name)
# async def receive_textbook_name(message: Message, state: FSMContext):
#     textbook_name = message.text.strip()
    
#     if len(textbook_name) < 4:
#         await message.answer(
#             "❌ Textbook name must be at least 4 characters long. Please try again:"
#         )
#         return
    
#     await state.update_data(textbook_name=textbook_name)
    
#     # keyboard = InlineKeyboardMarkup(inline_keyboard=[
#     #     [InlineKeyboardButton(text="✅ Skip Description", callback_data="skip_description")],
#     #     [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
#     # ])
    
#     # await message.answer(
#     #     f"📖 Textbook Name: {textbook_name}\n\n"
#     #     "Step 2: Please enter a description for the textbook (or click 'Skip Description'):",
#     #     reply_markup=keyboard
#     # )
#     await finish_textbook_creation(message, state)
#     # await state.set_state(AddTextbookStates.waiting_for_textbook_chapters)

# # @router.message(AddTextbookStates.waiting_for_textbook_chapters)
# # async def receive_textbook_description(message: Message, state: FSMContext):
# #     number_of_chapters = message.text.strip()
# #     await state.update_data(number_of_chapters=number_of_chapters)
# #     await finish_textbook_creation(message, state)

# # @router.callback_query(F.data == "skip_description")
# # async def skip_textbook_description(callback: CallbackQuery, state: FSMContext):
# #     await state.update_data(textbook_description=None)
# #     await finish_textbook_creation(callback.message, state, is_callback=True)

# async def finish_textbook_creation(message, state: FSMContext, is_callback=False):
#     data = await state.get_data()
#     textbook_name = data['textbook_name']
#     # textbook_chapters = data.get('number_of_chapters')
    
#     # Check if textbook with same name already exists
#     async with async_session() as session:
#         existing_textbook = await session.execute(
#             select(Textbook).where(Textbook.name == textbook_name)
#         )
#         if existing_textbook.scalar_one_or_none():
#             error_text = f"❌ A textbook with the name '{textbook_name}' already exists. Please choose a different name."
#             if is_callback:
#                 await message.edit_text(error_text, reply_markup=get_back_to_main_keyboard())
#             else:
#                 await message.answer(error_text, reply_markup=get_back_to_main_keyboard())
#             await state.clear()
#             return
        
#         # Create new textbook
#         new_textbook = Textbook(
#             name=textbook_name,
#         )
#         session.add(new_textbook)
#         await session.commit()
#         await session.refresh(new_textbook)
    
#     success_text = f"✅ Textbook '{textbook_name}' has been added successfully!\n\n"
#     # if textbook_description:
#     #     success_text += f"📝 Description: {textbook_description}\n\n"
#     success_text += "You can now add chapters and problems to this textbook."
    
#     if is_callback:
#         await message.edit_text(success_text, reply_markup=get_back_to_main_keyboard())
#     else:
#         await message.answer(success_text, reply_markup=get_back_to_main_keyboard())
    
#     await state.clear()

# # Add Solution Flow
# @router.callback_query(F.data == "add_solution")
# async def start_add_solution(callback: CallbackQuery, state: FSMContext):
#     keyboard = await get_textbooks_keyboard("add")
#     await callback.message.edit_text(
#         "➕ Add a New Solution\n\n"
#         "Step 1: Select the textbook:",
#         reply_markup=keyboard
#     )
#     await state.set_state(AddSolutionStates.waiting_for_textbook)

# @router.callback_query(F.data.startswith("add_textbook_"))
# async def select_textbook_for_solution(callback: CallbackQuery, state: FSMContext):
#     textbook_id = int(callback.data.split("_")[-1])
#     await state.update_data(textbook_id=textbook_id)
    
#     async with async_session() as session:
#         result = await session.execute(
#             select(Textbook).where(Textbook.id == textbook_id)
#         )
#         textbook = result.scalar_one()
    
#     keyboard = await get_chapters_keyboard(textbook_id, "add")
#     await callback.message.edit_text(
#         f"➕ Add Solution to: {textbook.name}\n\n"
#         "Step 2: Select the chapter:",
#         reply_markup=keyboard
#     )
#     await state.set_state(AddSolutionStates.waiting_for_chapter)

# @router.callback_query(F.data.startswith("add_chapter_"))
# async def select_chapter_for_solution(callback: CallbackQuery, state: FSMContext):
#     chapter_id = int(callback.data.split("_")[-1])
#     await state.update_data(chapter_id=chapter_id)
    
#     async with async_session() as session:
#         result = await session.execute(
#             select(Chapter).options(selectinload(Chapter.textbook)).where(Chapter.id == chapter_id)
#         )
#         chapter = result.scalar_one()
    
#     keyboard = await get_problems_keyboard(chapter_id, "add")
#     await callback.message.edit_text(
#         f"➕ Add Solution to: {chapter.textbook.name}\n"
#         f"📑 Chapter: {chapter.name}\n\n"
#         "Step 3: Select the problem:",
#         reply_markup=keyboard
#     )
#     await state.set_state(AddSolutionStates.waiting_for_problem)

# @router.callback_query(F.data.startswith("add_problem_"))
# async def select_problem_for_solution(callback: CallbackQuery, state: FSMContext):
#     problem_id = int(callback.data.split("_")[-1])
#     await state.update_data(problem_id=problem_id)
    
#     async with async_session() as session:
#         result = await session.execute(
#             select(Problem).options(
#                 selectinload(Problem.chapter).selectinload(Chapter.textbook)
#             ).where(Problem.id == problem_id)
#         )
#         problem = result.scalar_one()
    
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
#     ])
    
#     await callback.message.edit_text(
#         f"➕ Adding Solution to:\n"
#         f"📖 Textbook: {problem.chapter.textbook.name}\n"
#         f"📑 Chapter: {problem.chapter.name}\n"
#         f"🧮 Problem: {problem.name}\n\n"
#         "Step 4: Please send your solution text (or skip by sending 'skip'):",
#         reply_markup=keyboard
#     )
#     await state.set_state(AddSolutionStates.waiting_for_solution_text)

# @router.message(AddSolutionStates.waiting_for_solution_text)
# async def receive_solution_text(message: Message, state: FSMContext):
#     if message.text.lower() == 'skip':
#         await state.update_data(solution_text=None)
#     else:
#         await state.update_data(solution_text=message.text)
    
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="✅ Skip Images", callback_data="skip_images")],
#         [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
#     ])
    
#     await message.answer(
#         "Step 5: Send images for your solution (if any), or click 'Skip Images' to finish:",
#         reply_markup=keyboard
#     )
#     await state.set_state(AddSolutionStates.waiting_for_solution_image)

# @router.message(AddSolutionStates.waiting_for_solution_image, F.photo)
# async def receive_solution_image(message: Message, state: FSMContext):
#     data = await state.get_data()
#     image_file_ids = data.get('image_file_ids', [])
#     image_file_ids.append(message.photo[-1].file_id)
#     await state.update_data(image_file_ids=image_file_ids)
    
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="✅ Finish", callback_data="finish_solution")],
#         [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
#     ])
    
#     await message.answer(
#         "Image received! Send more images or click 'Finish' to save your solution:",
#         reply_markup=keyboard
#     )

# @router.callback_query(F.data.in_(["skip_images", "finish_solution"]))
# async def finish_solution(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
    
#     # Create solution in database
#     async with async_session() as session:
#         solution = Solution(
#             user_name=callback.from_user.full_name or callback.from_user.username or "Anonymous",
#             text=data.get('solution_text'),
#             image_file_ids=json.dumps(data.get('image_file_ids', [])) if data.get('image_file_ids') else None,
#             problem_id=data['problem_id']
#         )
#         session.add(solution)
#         await session.commit()
    
#     await callback.message.edit_text(
#         "✅ Solution added successfully!\n\n"
#         "Thank you for contributing to the textbook solutions!",
#         reply_markup=get_back_to_main_keyboard()
#     )
#     await state.clear()

# # Add new chapter flow
# @router.callback_query(F.data.startswith("add_new_chapter"))
# async def add_new_chapter(callback: CallbackQuery, state: FSMContext):
#     textbook_id = callback.data.split("_")[-1]
#     await state.update_data(textbook_id=textbook_id)

#     if not textbook_id:
#         await callback.message.edit_text("❌ Could not determine which textbook to add a chapter to.", reply_markup=get_back_to_main_keyboard())
#         return

#     await state.set_state(AddChapterStates.waiting_for_chapter_name)
#     await callback.message.edit_text(
#         "📝 Please enter the name of the new chapter:",
#         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
#         ])
#     )

# @router.message(AddChapterStates.waiting_for_chapter_name)
# async def save_new_chapter(message: Message, state: FSMContext):
#     chapter_name = message.text.strip()
#     if len(chapter_name) < 1:
#         await message.answer("❌ Chapter name must be at least 1 character. Please enter a valid name:")
#         return

#     data = await state.get_data()
#     textbook_id = int(data.get("textbook_id"))

#     async with async_session() as session:
#         # Check if chapter with the same name already exists under the same textbook
#         result = await session.execute(
#             select(Chapter).where(Chapter.textbook_id == textbook_id, Chapter.name == chapter_name)
#         )
#         existing = result.scalar_one_or_none()
#         if existing:
#             await message.answer("❌ A chapter with this name already exists in the selected textbook.")
#             return

#         # Create new chapter
#         new_chapter = Chapter(name=chapter_name, textbook_id=textbook_id)
#         session.add(new_chapter)
#         await session.commit()

#     await message.answer(
#         f"✅ Chapter '{chapter_name}' added successfully!",
#         reply_markup=await get_chapters_keyboard(textbook_id, action_prefix="add")
#     )

#     # Go back to chapter selection in add flow
#     await state.set_state(AddSolutionStates.waiting_for_chapter)


# # Add new problem flow
# @router.callback_query(F.data.startswith("add_new_problem"))
# async def add_new_problem(callback: CallbackQuery, state: FSMContext):
#     chapter_id = callback.data.split("_")[-1]
#     await state.update_data(chapter_id=chapter_id)

#     if not chapter_id:
#         await callback.message.edit_text("❌ Could not determine which chapter to add a problem to.", reply_markup=get_back_to_main_keyboard())
#         return

#     await state.set_state(AddProblemStates.waiting_for_problem_name)
#     await callback.message.edit_text(
#         "📝 Please enter the name of the new problem:",
#         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
#         ])
#     )

# @router.message(AddProblemStates.waiting_for_problem_name)
# async def save_new_chapter(message: Message, state: FSMContext):
#     problem_name = message.text.strip()
#     if len(problem_name) < 1:
#         await message.answer("❌ Problem name must be at least 1 character. Please enter a valid name:")
#         return

#     data = await state.get_data()
#     chapter_id = int(data.get("chapter_id"))

#     async with async_session() as session:
#         # Check if chapter with the same name already exists under the same textbook
#         result = await session.execute(
#             select(Problem).where(Problem.chapter_id == chapter_id, Problem.name == problem_name)
#         )
#         existing = result.scalar_one_or_none()
#         if existing:
#             await message.answer("❌ A problem with this name already exists in the selected textbook.")
#             return

#         # Create new chapter
#         new_chapter = Problem(name=problem_name, chapter_id=chapter_id)
#         session.add(new_chapter)
#         await session.commit()

#     await message.answer(
#         f"✅ Problem '{problem_name}' added successfully!",
#         reply_markup=await get_chapters_keyboard(chapter_id, action_prefix="add")
#     )

#     # Go back to chapter selection in add flow
#     await state.set_state(AddSolutionStates.waiting_for_chapter)


# # Back navigation handlers
# @router.callback_query(F.data.startswith("back_to_textbooks_"))
# async def back_to_textbooks(callback: CallbackQuery):
#     action_prefix = callback.data.split("_")[-1]
#     if action_prefix == "view":
#         await browse_textbooks(callback)
#     elif action_prefix == "add":
#         await start_add_solution(callback, None)

# @router.callback_query(F.data.startswith("back_to_chapters_"))
# async def back_to_chapters(callback: CallbackQuery):
#     parts = callback.data.split("_")
#     action_prefix = parts[3]
#     textbook_id = int(parts[4])
    
#     if action_prefix == "view":
#         await view_textbook_chapters(CallbackQuery(
#             id=callback.id,
#             from_user=callback.from_user,
#             chat_instance=callback.chat_instance,
#             message=callback.message,
#             data=f"view_textbook_{textbook_id}"
#         ))
#     elif action_prefix == "add":
#         await select_textbook_for_solution(CallbackQuery(
#             id=callback.id,
#             from_user=callback.from_user,
#             chat_instance=callback.chat_instance,
#             message=callback.message,
#             data=f"add_textbook_{textbook_id}"
#         ))

# @router.callback_query(F.data.startswith("back_to_problems_"))
# async def back_to_problems(callback: CallbackQuery):
#     parts = callback.data.split("_")
#     action_prefix = parts[3]
#     chapter_id = int(parts[4])
    
#     if action_prefix == "view":
#         await view_chapter_problems(CallbackQuery(
#             id=callback.id,
#             from_user=callback.from_user,
#             chat_instance=callback.chat_instance,
#             message=callback.message,
#             data=f"view_chapter_{chapter_id}"
#         ))

# @router.callback_query(F.data == "help")
# async def show_help(callback: CallbackQuery):
#     help_text = """
# ❓ **Help - How to Use This Bot**

# 🔹 **Browse Textbooks**: Navigate through available textbooks, chapters, and problems to view existing solutions.

# 🔹 **Add Solution**: Contribute your own solutions to problems:
#    • Select textbook → chapter → problem
#    • Add solution text (optional)
#    • Upload images (optional)
#    • Submit your solution

# 🔹 **Add Textbook**: Add new textbooks to the database:
#    • Enter textbook name (required)
#    • Add description (optional)
#    • Textbook will be available for adding chapters and problems

# 🔹 **Navigation**: Use the inline buttons to navigate. You can always go back or return to the main menu.

# 🔹 **Solution Format**: 
#    • Text solutions support plain text
#    • You can upload multiple images
#    • Both text and images are optional, but at least one is recommended

# 🔹 **Textbook Requirements**:
#    • Textbook name must be at least 3 characters
#    • Each textbook name must be unique
#    • Description is optional but recommended

# Need more help? Contact the bot administrator.
#     """
    
#     await callback.message.edit_text(
#         help_text,
#         reply_markup=get_back_to_main_keyboard()
#     )












from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.db.models import async_session, Textbook, Chapter, Problem, Solution
import json

router = Router()

# FSM States for adding solutions
class AddSolutionStates(StatesGroup):
    waiting_for_textbook = State()
    waiting_for_chapter = State()
    waiting_for_problem = State()
    waiting_for_solution_text = State()
    waiting_for_solution_image = State()

# FSM States for adding textbooks
class AddTextbookStates(StatesGroup):
    waiting_for_textbook_name = State()
    waiting_for_textbook_description = State()

class AddChapterStates(StatesGroup):
    waiting_for_chapter_name = State()

class AddProblemStates(StatesGroup):
    waiting_for_problem_name = State()

# State for tracking image messages
class ImageTrackingState(StatesGroup):
    has_images = State()

# Helper function to delete previous images
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

# Helper function to send images and track message IDs
async def send_and_track_images(callback: CallbackQuery, state: FSMContext, file_ids: list):
    """Send images and store their message IDs for later deletion"""
    sent_message_ids = []
    
    for file_id in file_ids:
        try:
            sent_message = await callback.message.answer_photo(file_id)
            sent_message_ids.append(sent_message.message_id)
        except Exception as e:
            print(f"Could not send image {file_id}: {e}")
    
    # Store the message IDs in state for later cleanup
    await state.update_data(previous_image_messages=sent_message_ids)

# Main menu keyboard
def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Browse Textbooks", callback_data="browse_textbooks")],
        [InlineKeyboardButton(text="➕ Add Solution", callback_data="add_solution")],
        [InlineKeyboardButton(text="📖 Add Textbook", callback_data="add_textbook")],
        [InlineKeyboardButton(text="❓ Help", callback_data="help")]
    ])
    return keyboard

# Back to main menu keyboard
def get_back_to_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Back to Main Menu", callback_data="main_menu")]
    ])
    return keyboard

# Textbooks keyboard
async def get_textbooks_keyboard(action_prefix="view"):
    async with async_session() as session:
        result = await session.execute(select(Textbook))
        textbooks = result.scalars().all()
        keyboard_buttons = []
        for textbook in textbooks:
            callback_data = f"{action_prefix}_textbook_{textbook.id}"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"📖 {textbook.name}", 
                callback_data=callback_data
            )])

        keyboard_buttons.append([InlineKeyboardButton(text="🏠 Back to Main Menu", callback_data="main_menu")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

# Chapters keyboard
async def get_chapters_keyboard(textbook_id: int, action_prefix="view"):
    async with async_session() as session:
        result = await session.execute(
            select(Chapter).where(Chapter.textbook_id == textbook_id)
        )
        chapters = result.scalars().all()
        
        keyboard_buttons = []
        for chapter in chapters:
            callback_data = f"{action_prefix}_chapter_{chapter.id}"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"📑 {chapter.name}", 
                callback_data=callback_data
            )])
        
        if action_prefix == "add":
            keyboard_buttons.append([
                InlineKeyboardButton(text="➕ Add new chapter", callback_data=f"add_new_chapter_{textbook_id}")
            ])

        keyboard_buttons.append([
                InlineKeyboardButton(text="⬅️ Back to Textbooks", callback_data=f"back_to_textbooks_{action_prefix}"),
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
            ])
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

# Problems keyboard
async def get_problems_keyboard(chapter_id: int, action_prefix="view"):
    async with async_session() as session:
        result = await session.execute(
            select(Problem).where(Problem.chapter_id == chapter_id)
        )
        problems = result.scalars().all()
        
        keyboard_buttons = []
        for problem in problems:
            callback_data = f"{action_prefix}_problem_{problem.id}"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"🧮 {problem.name}", 
                callback_data=callback_data
            )])
        
        # Get textbook_id for back navigation
        chapter_result = await session.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        chapter = chapter_result.scalar_one()
        
        if action_prefix == "add":
            keyboard_buttons.append([
                InlineKeyboardButton(text="➕ Add new problem", callback_data=f"add_new_problem_{chapter_id}")
            ])

        keyboard_buttons.append([
            InlineKeyboardButton(text="⬅️ Back to Chapters", callback_data=f"back_to_chapters_{action_prefix}_{chapter.textbook_id}"),
            InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
        ])
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

# Solutions keyboard
async def get_solutions_keyboard(problem_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Solution).where(Solution.problem_id == problem_id)
        )
        solutions = result.scalars().all()
        
        keyboard_buttons = []
        for i, solution in enumerate(solutions, 1):
            callback_data = f"view_solution_{solution.id}"
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"📝 Solution {i} by {solution.user_name}", 
                callback_data=callback_data
            )])
        
        # Get chapter_id for back navigation
        problem_result = await session.execute(
            select(Problem).where(Problem.id == problem_id)
        )
        problem = problem_result.scalar_one()
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="⬅️ Back to Problems", callback_data=f"back_to_problems_view_{problem.chapter_id}"),
            InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
        ])
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # Clear any existing state and image tracking
    await state.clear()
    await message.answer(
        "🎓 Welcome to the Textbook Solutions Bot!\n\n"
        "Choose an option below to get started:",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    print("STATE JUST BEFORE CLEARING IT:", state, callback)
    # Delete any previous images before clearing state
    await delete_previous_images(callback, state)
    await state.clear()
    
    await callback.message.edit_text(
        "🎓 Welcome to the Textbook Solutions Bot!\n\n"
        "Choose an option below to get started:",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "browse_textbooks")
async def browse_textbooks(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when starting browse flow
    await delete_previous_images(callback, state)
    
    keyboard = await get_textbooks_keyboard("view")
    await callback.message.edit_text(
        "📚 Available Textbooks:\n\n"
        "Select a textbook to browse its chapters:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("view_textbook_"))
async def view_textbook_chapters(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating
    await delete_previous_images(callback, state)
    
    textbook_id = int(callback.data.split("_")[-1])
    
    async with async_session() as session:
        result = await session.execute(
            select(Textbook).where(Textbook.id == textbook_id)
        )
        textbook = result.scalar_one()

    keyboard = await get_chapters_keyboard(textbook_id, "view")
    await callback.message.edit_text(
        f"📖 Textbook: {textbook.name}\n\n"
        "Select a chapter to view its problems:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("view_chapter_"))
async def view_chapter_problems(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating
    await delete_previous_images(callback, state)
    
    chapter_id = int(callback.data.split("_")[-1])
    
    async with async_session() as session:
        result = await session.execute(
            select(Chapter).options(selectinload(Chapter.textbook)).where(Chapter.id == chapter_id)
        )
        chapter = result.scalar_one()
    
    keyboard = await get_problems_keyboard(chapter_id, "view")
    await callback.message.edit_text(
        f"📖 Textbook: {chapter.textbook.name}\n"
        f"📑 Chapter: {chapter.name}\n\n"
        "Select a problem to view its solutions:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("view_problem_"))
async def view_problem_solutions(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating
    await delete_previous_images(callback, state)
    
    problem_id = int(callback.data.split("_")[-1])
    
    async with async_session() as session:
        result = await session.execute(
            select(Problem).options(
                selectinload(Problem.chapter).selectinload(Chapter.textbook)
            ).where(Problem.id == problem_id)
        )
        problem = result.scalar_one()
    
    keyboard = await get_solutions_keyboard(problem_id)
    await callback.message.edit_text(
        f"📖 Textbook: {problem.chapter.textbook.name}\n"
        f"📑 Chapter: {problem.chapter.name}\n"
        f"🧮 Problem: {problem.name}\n\n"
        "Select a solution to view:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("view_solution_"))
async def view_solution_details(callback: CallbackQuery, state: FSMContext):
    # Delete previous images before showing new solution
    await delete_previous_images(callback, state)
    
    solution_id = int(callback.data.split("_")[-1])
    
    async with async_session() as session:
        result = await session.execute(
            select(Solution).options(
                selectinload(Solution.problem).selectinload(Problem.chapter).selectinload(Chapter.textbook)
            ).where(Solution.id == solution_id)
        )
        solution = result.scalar_one()
    
    solution_text = f"📖 Textbook: {solution.problem.chapter.textbook.name}\n"
    solution_text += f"📑 Chapter: {solution.problem.chapter.name}\n"
    solution_text += f"🧮 Problem: {solution.problem.name}\n"
    solution_text += f"👤 Solved by: {solution.user_name}\n"
    solution_text += f"📅 Created: {solution.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    if solution.text:
        solution_text += f"📝 Solution:\n{solution.text}\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Solutions", callback_data=f"view_problem_{solution.problem_id}")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
    ])
    
    # Edit the main text message
    await callback.message.edit_text(solution_text, reply_markup=keyboard)
    
    # Send images if any and track their message IDs
    if solution.image_file_ids:
        try:
            file_ids = json.loads(solution.image_file_ids)
            if file_ids:  # Only send if there are actually file IDs
                await send_and_track_images(callback, state, file_ids)
        except json.JSONDecodeError:
            pass

# Add Textbook Flow
@router.callback_query(F.data == "add_textbook")
async def start_add_textbook(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when starting add textbook flow
    await delete_previous_images(callback, state)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        "📖 Add a New Textbook\n\n"
        "Step 1: Please enter the textbook name:",
        reply_markup=keyboard
    )
    await state.set_state(AddTextbookStates.waiting_for_textbook_name)

@router.message(AddTextbookStates.waiting_for_textbook_name)
async def receive_textbook_name(message: Message, state: FSMContext):
    textbook_name = message.text.strip()
    
    if len(textbook_name) < 4:
        await message.answer(
            "❌ Textbook name must be at least 4 characters long. Please try again:"
        )
        return
    
    await state.update_data(textbook_name=textbook_name)
    await finish_textbook_creation(message, state)

async def finish_textbook_creation(message, state: FSMContext, is_callback=False):
    data = await state.get_data()
    textbook_name = data['textbook_name']
    
    # Check if textbook with same name already exists
    async with async_session() as session:
        existing_textbook = await session.execute(
            select(Textbook).where(Textbook.name == textbook_name)
        )
        if existing_textbook.scalar_one_or_none():
            error_text = f"❌ A textbook with the name '{textbook_name}' already exists. Please choose a different name."
            if is_callback:
                await message.edit_text(error_text, reply_markup=get_back_to_main_keyboard())
            else:
                await message.answer(error_text, reply_markup=get_back_to_main_keyboard())
            await state.clear()
            return
        
        # Create new textbook
        new_textbook = Textbook(
            name=textbook_name,
        )
        session.add(new_textbook)
        await session.commit()
        await session.refresh(new_textbook)
    
    success_text = f"✅ Textbook '{textbook_name}' has been added successfully!\n\n"
    success_text += "You can now add chapters and problems to this textbook."
    
    if is_callback:
        await message.edit_text(success_text, reply_markup=get_back_to_main_keyboard())
    else:
        await message.answer(success_text, reply_markup=get_back_to_main_keyboard())
    
    await state.clear()

# Add Solution Flow
@router.callback_query(F.data == "add_solution")
async def start_add_solution(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when starting add solution flow
    await delete_previous_images(callback, state)
    
    keyboard = await get_textbooks_keyboard("add")
    await callback.message.edit_text(
        "➕ Add a New Solution\n\n"
        "Step 1: Select the textbook:",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_textbook)

@router.callback_query(F.data.startswith("add_textbook_"))
async def select_textbook_for_solution(callback: CallbackQuery, state: FSMContext):
    textbook_id = int(callback.data.split("_")[-1])
    await state.update_data(textbook_id=textbook_id)
    
    async with async_session() as session:
        result = await session.execute(
            select(Textbook).where(Textbook.id == textbook_id)
        )
        textbook = result.scalar_one()
    
    keyboard = await get_chapters_keyboard(textbook_id, "add")
    await callback.message.edit_text(
        f"➕ Add Solution to: {textbook.name}\n\n"
        "Step 2: Select the chapter:",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_chapter)

@router.callback_query(F.data.startswith("add_chapter_"))
async def select_chapter_for_solution(callback: CallbackQuery, state: FSMContext):
    chapter_id = int(callback.data.split("_")[-1])
    await state.update_data(chapter_id=chapter_id)
    
    async with async_session() as session:
        result = await session.execute(
            select(Chapter).options(selectinload(Chapter.textbook)).where(Chapter.id == chapter_id)
        )
        chapter = result.scalar_one()
    
    keyboard = await get_problems_keyboard(chapter_id, "add")
    await callback.message.edit_text(
        f"➕ Add Solution to: {chapter.textbook.name}\n"
        f"📑 Chapter: {chapter.name}\n\n"
        "Step 3: Select the problem:",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_problem)

@router.callback_query(F.data.startswith("add_problem_"))
async def select_problem_for_solution(callback: CallbackQuery, state: FSMContext):
    problem_id = int(callback.data.split("_")[-1])
    await state.update_data(problem_id=problem_id)
    
    async with async_session() as session:
        result = await session.execute(
            select(Problem).options(
                selectinload(Problem.chapter).selectinload(Chapter.textbook)
            ).where(Problem.id == problem_id)
        )
        problem = result.scalar_one()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        f"➕ Adding Solution to:\n"
        f"📖 Textbook: {problem.chapter.textbook.name}\n"
        f"📑 Chapter: {problem.chapter.name}\n"
        f"🧮 Problem: {problem.name}\n\n"
        "Step 4: Please send your solution text (or skip by sending 'skip'):",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_solution_text)

@router.message(AddSolutionStates.waiting_for_solution_text)
async def receive_solution_text(message: Message, state: FSMContext):
    if message.text.lower() == 'skip':
        await state.update_data(solution_text=None)
    else:
        await state.update_data(solution_text=message.text)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Skip Images", callback_data="skip_images")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])
    
    await message.answer(
        "Step 5: Send images for your solution (if any), or click 'Skip Images' to finish:",
        reply_markup=keyboard
    )
    await state.set_state(AddSolutionStates.waiting_for_solution_image)

@router.message(AddSolutionStates.waiting_for_solution_image, F.photo)
async def receive_solution_image(message: Message, state: FSMContext):
    data = await state.get_data()
    image_file_ids = data.get('image_file_ids', [])
    image_file_ids.append(message.photo[-1].file_id)
    await state.update_data(image_file_ids=image_file_ids)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Finish", callback_data="finish_solution")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
    ])
    
    await message.answer(
        "Image received! Send more images or click 'Finish' to save your solution:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.in_(["skip_images", "finish_solution"]))
async def finish_solution(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Create solution in database
    async with async_session() as session:
        solution = Solution(
            user_name=callback.from_user.full_name or callback.from_user.username or "Anonymous",
            text=data.get('solution_text'),
            image_file_ids=json.dumps(data.get('image_file_ids', [])) if data.get('image_file_ids') else None,
            problem_id=data['problem_id']
        )
        session.add(solution)
        await session.commit()
    
    await callback.message.edit_text(
        "✅ Solution added successfully!\n\n"
        "Thank you for contributing to the textbook solutions!",
        reply_markup=get_back_to_main_keyboard()
    )
    await state.clear()

# Add new chapter flow
@router.callback_query(F.data.startswith("add_new_chapter"))
async def add_new_chapter(callback: CallbackQuery, state: FSMContext):
    textbook_id = callback.data.split("_")[-1]
    await state.update_data(textbook_id=textbook_id)

    if not textbook_id:
        await callback.message.edit_text("❌ Could not determine which textbook to add a chapter to.", reply_markup=get_back_to_main_keyboard())
        return

    await state.set_state(AddChapterStates.waiting_for_chapter_name)
    await callback.message.edit_text(
        "📝 Please enter the name of the new chapter:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
        ])
    )

@router.message(AddChapterStates.waiting_for_chapter_name)
async def save_new_chapter(message: Message, state: FSMContext):
    chapter_name = message.text.strip()
    if len(chapter_name) < 1:
        await message.answer("❌ Chapter name must be at least 1 character. Please enter a valid name:")
        return

    data = await state.get_data()
    textbook_id = int(data.get("textbook_id"))

    async with async_session() as session:
        # Check if chapter with the same name already exists under the same textbook
        result = await session.execute(
            select(Chapter).where(Chapter.textbook_id == textbook_id, Chapter.name == chapter_name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            await message.answer("❌ A chapter with this name already exists in the selected textbook.")
            return

        # Create new chapter
        new_chapter = Chapter(name=chapter_name, textbook_id=textbook_id)
        session.add(new_chapter)
        await session.commit()

    await message.answer(
        f"✅ Chapter '{chapter_name}' added successfully!",
        reply_markup=await get_chapters_keyboard(textbook_id, action_prefix="add")
    )

    # Go back to chapter selection in add flow
    await state.set_state(AddSolutionStates.waiting_for_chapter)

# Add new problem flow
@router.callback_query(F.data.startswith("add_new_problem"))
async def add_new_problem(callback: CallbackQuery, state: FSMContext):
    chapter_id = callback.data.split("_")[-1]
    await state.update_data(chapter_id=chapter_id)

    if not chapter_id:
        await callback.message.edit_text("❌ Could not determine which chapter to add a problem to.", reply_markup=get_back_to_main_keyboard())
        return

    await state.set_state(AddProblemStates.waiting_for_problem_name)
    await callback.message.edit_text(
        "📝 Please enter the name of the new problem:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="main_menu")]
        ])
    )

@router.message(AddProblemStates.waiting_for_problem_name)
async def save_new_problem(message: Message, state: FSMContext):
    problem_name = message.text.strip()
    if len(problem_name) < 1:
        await message.answer("❌ Problem name must be at least 1 character. Please enter a valid name:")
        return

    data = await state.get_data()
    chapter_id = int(data.get("chapter_id"))

    async with async_session() as session:
        # Check if problem with the same name already exists under the same chapter
        result = await session.execute(
            select(Problem).where(Problem.chapter_id == chapter_id, Problem.name == problem_name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            await message.answer("❌ A problem with this name already exists in the selected chapter.")
            return

        # Create new problem
        new_problem = Problem(name=problem_name, chapter_id=chapter_id)
        session.add(new_problem)
        await session.commit()

    await message.answer(
        f"✅ Problem '{problem_name}' added successfully!",
        reply_markup=await get_problems_keyboard(chapter_id, action_prefix="add")
    )

    # Go back to problem selection in add flow
    await state.set_state(AddSolutionStates.waiting_for_problem)

# Back navigation handlers
@router.callback_query(F.data.startswith("back_to_textbooks_"))
async def back_to_textbooks(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating back
    await delete_previous_images(callback, state)
    
    action_prefix = callback.data.split("_")[-1]
    if action_prefix == "view":
        await browse_textbooks(callback, state)
    elif action_prefix == "add":
        await start_add_solution(callback, state)

@router.callback_query(F.data.startswith("back_to_chapters_"))
async def back_to_chapters(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating back
    await delete_previous_images(callback, state)
    
    parts = callback.data.split("_")
    action_prefix = parts[3]
    textbook_id = int(parts[4])
    
    if action_prefix == "view":
        await view_textbook_chapters(CallbackQuery(
            id=callback.id,
            from_user=callback.from_user,
            chat_instance=callback.chat_instance,
            message=callback.message,
            data=f"view_textbook_{textbook_id}"
        ), state)
    elif action_prefix == "add":
        await select_textbook_for_solution(CallbackQuery(
            id=callback.id,
            from_user=callback.from_user,
            chat_instance=callback.chat_instance,
            message=callback.message,
            data=f"add_textbook_{textbook_id}"
        ), state)

@router.callback_query(F.data.startswith("back_to_problems_"))
async def back_to_problems(callback: CallbackQuery, state: FSMContext):
    # Delete any previous images when navigating back
    await delete_previous_images(callback, state)
    
    parts = callback.data.split("_")
    action_prefix = parts[3]
    chapter_id = int(parts[4])
    
    if action_prefix == "view":
        await view_chapter_problems(CallbackQuery(
            id=callback.id,
            from_user=callback.from_user,
            chat_instance=callback.chat_instance,
            message=callback.message,
            data=f"view_chapter_{chapter_id}"
        ), state)

@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    help_text = """
❓ **Help - How to Use This Bot**

🔹 **Browse Textbooks**: Navigate through available textbooks, chapters, and problems to view existing solutions.

🔹 **Add Solution**: Contribute your own solutions to problems:
   • Select textbook → chapter → problem
   • Add solution text (optional)
   • Upload images (optional)
   • Submit your solution

🔹 **Add Textbook**: Add new textbooks to the database:
   • Enter textbook name (required)
   • Add description (optional)
   • Textbook will be available for adding chapters and problems

🔹 **Navigation**: Use the inline buttons to navigate. You can always go back or return to the main menu.

🔹 **Solution Format**: 
   • Text solutions support plain text
   • You can upload multiple images
   • Both text and images are optional, but at least one is recommended

🔹 **Textbook Requirements**:
   • Textbook name must be at least 3 characters
   • Each textbook name must be unique
   • Description is optional but recommended

Need more help? Contact the bot administrator.
    """
    
    await callback.message.edit_text(
        help_text,
        reply_markup=get_back_to_main_keyboard()
    )


    