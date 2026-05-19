import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configura o log no terminal para ver se há erros
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start básico de boas-vindas"""
    await update.message.reply_text("👋 Olá! O esqueleto do Bot Literário está online e funcionando!")

def main():
    
    app = Application.builder().token(TOKEN_TELEGRAM).build()
    
    
    app.add_handler(CommandHandler("start", start))
    
    print("Bot iniciado! Vá no Telegram e digite /start")
    app.run_polling()

if __name__ == '__main__':
    main()