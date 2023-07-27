from telegram.ext import CallbackQueryHandler, ConversationHandler

from src.commands import handlers
from src.conversations.profile import callbacks, constants

profile_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callbacks.program, constants.PROGRAM),
        CallbackQueryHandler(callbacks.semester, constants.SEMESTER),
    ],
    states={1: [CallbackQueryHandler(handlers.profile, constants.PROFILE)]},
    fallbacks=[],
    name=constants.NAME,
    per_message=True,
    # allow_reentry must be set to true for the conversation
    # to work after pressing Back button
    allow_reentry=True,
)
