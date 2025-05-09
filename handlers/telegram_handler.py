from telegram import Update
from telegram.ext import ContextTypes
from services.arbitrage_service import ArbitrageService
from services.wallet_service import WalletService
from services.update_service import UpdateService
from utils.config import load_config, save_config

arbitrage_service = ArbitrageService()
update_service = UpdateService()
auto_trading = False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Bienvenido al Bot de Arbitraje de Criptomonedas!\n"
        "Usa /help para ver los comandos disponibles."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📘 *Comandos del Bot de Arbitraje de Criptomonedas*

⛽ /check_fees <red>  
Verifica las tarifas de red (eth / bsc / polygon)

🧪 /check_token <red> <token_address>  
Consulta información de un token en una red

▶️ /start  
Inicia el bot

ℹ️ /help  
Muestra este menú de ayuda

🏦 /register_exchange <exchange> <api_key> <secret>  
Registra un exchange con tus credenciales API

📋 /list_exchanges  
Lista todos los exchanges registrados

⚙️ /enable_auto  
Activa el trading automático

⛔ /disable_auto  
Desactiva el trading automático

🔐 /add_dex_wallet <nombre_wallet> <clave_privada> <estado_kyc>  
Agrega una wallet descentralizada (DEX)

🏛️ /add_cex_wallet <exchange> <nombre_wallet> <api_key> <secret> <contraseña>  
Agrega una wallet de un exchange centralizado (CEX)

💰 /balance <wallet_id>  
Consulta el balance de una wallet

🔍 /scan <par>  
Escanea oportunidades de arbitraje (ej: /scan BTC/USDT)

🔄 /check_updates  
Revisa si hay actualizaciones disponibles

🚀 /update_bot  
Actualiza el bot a la última versión
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


async def check_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update_service.check_updates()
    await update.message.reply_text(result['message'])

async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update_service.update_bot()
    await update.message.reply_text(result['message'])

async def add_dex_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, wallet_name, private_key, kyc_status = update.message.text.split()
        wallet_service = WalletService()
        result = wallet_service.add_dex_wallet(private_key, wallet_name, kyc_status)
        if result['success']:
            await update.message.reply_text(f"Wallet agregada exitosamente: {result['address']}")
        else:
            await update.message.reply_text(f"Error: {result['error']}")
    except ValueError:
        await update.message.reply_text("Uso: /add_dex_wallet <private_key>")

async def add_cex_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, exchange, wallet_name, api_key, secret, password = update.message.text.split()
        wallet_service = WalletService()
        result = wallet_service.add_cex_wallet(exchange, api_key, secret, wallet_name, password)
        if result['success']:
            await update.message.reply_text(f"Wallet de {exchange} agregada exitosamente")
        else:
            await update.message.reply_text(f"Error: {result['error']}")
    except ValueError:
        await update.message.reply_text("Uso: /add_cex_wallet <exchange> <api_key> <secret>")

async def get_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, wallet_id = update.message.text.split()
        wallet_service = WalletService()
        if wallet_id.startswith('0x'):
            result = wallet_service.get_dex_balance(wallet_id)
        else:
            result = wallet_service.get_cex_balance(wallet_id)
        
        if result['success']:
            await update.message.reply_text(f"Balance: {result['balance']}")
        else:
            await update.message.reply_text(f"Error: {result['error']}")
    except ValueError:
        await update.message.reply_text("Uso: /balance <wallet_id>")