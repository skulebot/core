"""Build the application, register handlers and run.

Usage:
    ```python
    application.initialize()
    application.register_handlers()
    application.run()
    ```
"""
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

_application: Application | None = None


def _set_application(application: Application):
    global _application
    _application = application


def _get_application():
    global _application
    if _application is None:
        raise RuntimeError("application is not initialized yet.")
    return _application


def initialize():
    """Initialize Application

    Builds the application and sets the bot token
    """

    # Prevent initializing application twice
    global _application
    if _application:
        return

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if BOT_TOKEN is None:
        raise RuntimeError("BOT_TOKEN is not set")
    application = Application.builder().token(BOT_TOKEN).build()
    _set_application(application)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def register_handlers():
    application = _get_application()
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


def run() -> None:
    """Run the bot."""
    application = _get_application()

    if os.getenv("ENV") == "production":
        PORT = int(os.getenv("PORT", "8443"))
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            secret_token=os.getenv("WEBHOOK_SECRET_TOKEN"),
            webhook_url=os.getenv("WEBHOOK_URL"),
        )
    else:
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
