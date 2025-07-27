from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.services.solutions import delete_previous_images
from src.keyboards.menu import get_back_to_main_keyboard
from src.keyboards.menu import get_main_menu_keyboard
from aiogram.filters import CommandStart

router = Router()

@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    help_text = """
❓ *Help \\- How to Use This Bot*

🔹 *Browse Textbooks*: Navigate through available textbooks, chapters, and problems to view existing solutions\\.

🔹 *Add Solution*: Contribute your own solutions to problems:\\n
• Select textbook → chapter → problem\\n
• Add solution text \\(optional\\)\\n
• Upload images \\(optional\\)\\n
• Submit your solution

🔹 *Add Textbook*: Add new textbooks to the database:\\n
• Enter textbook name \\(required\\)\\n
• Add description \\(optional\\)\\n
• Textbook will be available for adding chapters and problems

🔹 *Navigation*: Use the inline buttons to navigate\\. You can always go back or return to the main menu\\.

🔹 *Solution Format*:\\n
• Text solutions support plain text\\n
• You can upload multiple images\\n
• Both text and images are optional, but at least one is recommended

🔹 *Textbook Requirements*:\\n
• Textbook name must be at least 3 characters\\n
• Each textbook name must be unique\\n
• Description is optional but recommended

Need more help\\? Contact the bot administrator\\.
"""

    await callback.message.edit_text(
        help_text,
        reply_markup=get_back_to_main_keyboard(),
        parse_mode="MarkdownV2"
    )

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
    # Delete any previous images before clearing state
    await delete_previous_images(callback, state)
    await state.clear()
    
    await callback.message.edit_text(
        "🎓 Welcome to the Textbook Solutions Bot!\n\n"
        "Choose an option below to get started:",
        reply_markup=get_main_menu_keyboard()
    )
