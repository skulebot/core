from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.conversations.profile import constants

# Fake data
programs = [
    "BSc Information Technology",
    "BSc Computer Science",
    "BSc Statistics",
    "BSc Mathematics",
    "BSc Statistics & Computer Science",
    "BSc Mathematics & Computer Science",
]
semesters = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


async def program(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    query = update.callback_query
    await query.answer()

    keyboard = []
    for program in programs:
        keyboard.append(
            [
                InlineKeyboardButton(program, callback_data=program),
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton("Back", callback_data=constants.PROFILE),
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "Select your program"
    await query.edit_message_text(message, reply_markup=reply_markup)

    return 1


async def semester(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    query = update.callback_query
    await query.answer()

    keyboard = []
    for semester in semesters:
        text = f"Semester {semester}"
        keyboard.append(
            [
                InlineKeyboardButton(text, callback_data=semester),
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton("Back", callback_data=constants.PROFILE),
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "Select semester"
    await query.edit_message_text(message, reply_markup=reply_markup)

    return 1
