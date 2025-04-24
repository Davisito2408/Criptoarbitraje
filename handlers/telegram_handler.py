
from telegram import Update
from telegram.ext import ContextTypes
from services.arbitrage_service import ArbitrageService
from utils.config import load_config, save_config

arbitrage_service = ArbitrageService()
auto_trading = False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Bienvenido al Bot de Arbitraje de Criptomonedas!\n"
        "Usa /help para ver los comandos disponibles."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Comandos disponibles:
/start - Iniciar el bot
/help - Mostrar este mensaje de ayuda
/register_exchange <exchange> <api_key> <secret> - Registrar un nuevo exchange
/list_exchanges - Listar exchanges registrados
/enable_auto - Activar trading automático
/disable_auto - Desactivar trading automático
/scan <symbol> - Buscar oportunidades de arbitraje (ej: /scan BTC/USDT)
"""
    await update.message.reply_text(help_text)

async def register_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, exchange, api_key, secret = update.message.text.split()
        if arbitrage_service.add_exchange(exchange, api_key, secret):
            config = load_config()
            if 'exchanges' not in config:
                config['exchanges'] = {}
            config['exchanges'][exchange] = {
                'api_key': api_key,
                'secret': secret
            }
            save_config(config)
            await update.message.reply_text(f"Exchange {exchange} registrado exitosamente")
        else:
            await update.message.reply_text("Exchange no soportado o datos inválidos")
    except ValueError:
        await update.message.reply_text("Uso: /register_exchange <exchange> <api_key> <secret>")

async def scan_opportunities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, symbol = update.message.text.split()
        opportunities = await arbitrage_service.detect_opportunities(symbol)
        if opportunities:
            response = "Oportunidades encontradas:\n\n"
            for opp in opportunities:
                response += f"💰 {opp['profit_percent']:.2f}% de beneficio\n"
                response += f"Comprar en {opp['buy_exchange']} a {opp['buy_price']}\n"
                response += f"Vender en {opp['sell_exchange']} a {opp['sell_price']}\n\n"
        else:
            response = "No se encontraron oportunidades de arbitraje"
        await update.message.reply_text(response)
    except ValueError:
        await update.message.reply_text("Uso: /scan <symbol> (ej: /scan BTC/USDT)")
