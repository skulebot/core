"""Contains wrapper functions for creating, running and register handlers
for an application."""
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

import src.commands as commands
from src.errors import MissingVariableError


def create() -> Application:
    """Creates an instance of `telegram.ext.Application` and configures it."""
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise MissingVariableError("BOT_TOKEN")
    application = Application.builder().token(BOT_TOKEN).build()
    return application


def register_handlers(application: Application):
    """Registers `CommandHandler`s, `ConversationHandler`s ...etc."""

    application.add_handler(CommandHandler(["start", "profile"], commands.profile))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, commands.echo)
    )


def run(application: Application):
    """Runs the application.
    Will use `run_polling` in development environments, and `run_webhook`
    in production"""
    if os.getenv("ENV") == "production":
        PORT = int(os.getenv("PORT", "8443"))
        WEBHOOK_SERCRET_TOKEN = int(os.getenv("WEBHOOK_SECRET_TOKEN"))
        WEBHOOK_URL = int(os.getenv("WEBHOOK_URL"))
        if not WEBHOOK_URL:
            raise MissingVariableError("WEBHOOK_URL")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            secret_token=WEBHOOK_SERCRET_TOKEN,
            webhook_url=WEBHOOK_URL,
        )
    else:
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
