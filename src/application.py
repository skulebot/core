"""Contains wrapper functions for creating, running and register handlers
for an application."""
import os

from telegram import Update
from telegram.ext import Application

from src import commands, conversations
from src.errors import MissingVariableError


def create() -> Application:
    """Creates an instance of `telegram.ext.Application` and configures it.
    Raise MissingVariableError if no bot token present in .env"""
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise MissingVariableError("BOT_TOKEN")
    application = Application.builder().token(BOT_TOKEN).build()
    return application


def register_handlers(application: Application):
    """Registers `CommandHandler`s, `ConversationHandler`s ...etc."""

    application.add_handler(commands.profile_command)
    application.add_handler(conversations.profile_conv)


def run(application: Application):
    """Runs the application.
    Will use `run_polling` in development environments, and `run_webhook`
    in production"""
    if os.getenv("ENV") == "production":
        PORT = int(os.getenv("PORT", "8443"))
        WEBHOOK_SERCRET_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN")
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
