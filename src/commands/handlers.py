from telegram.ext import CommandHandler

from src.commands.callbacks import profile

profile_command = CommandHandler(["start", "profile"], profile)
