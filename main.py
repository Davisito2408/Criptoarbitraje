
import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from handlers.telegram_handler import start_command, help_command, register_exchange, scan_opportunities
from services.arbitrage_service import ArbitrageService
from utils.config import load_config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize bot with token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("register_exchange", register_exchange))
    application.add_handler(CommandHandler("scan", scan_opportunities))
    
    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
