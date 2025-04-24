
from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Crypto Arbitrage Bot!\n"
        "Use /help to see available commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/register_exchange - Register a new exchange
/list_exchanges - List registered exchanges
/enable_auto - Enable automatic trading
/disable_auto - Disable automatic trading
"""
    await update.message.reply_text(help_text)

async def register_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Implement exchange registration logic
    await update.message.reply_text("Exchange registration - Coming soon")
