from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

PROGRAM = "BSc Statistics"
SEMESTER = 4


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # This can not be imported at the top due to circular imports
    from src.conversations.profile import constants

    query: None | CallbackQuery = None
    if update.callback_query:
        query = update.callback_query
        await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("Edit Program", callback_data=constants.PROGRAM),
            InlineKeyboardButton("Edit Semester", callback_data=constants.SEMESTER),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"*Program*: {PROGRAM}\n" f"*Semester*: {SEMESTER}"

    if query:
        await query.edit_message_text(
            message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2
        )
    else:
        await update.message.reply_markdown_v2(message, reply_markup=reply_markup)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)
