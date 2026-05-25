import os
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from dotenv import load_dotenv
from src.bot_telegram import start, handle_message, listar_ou_definir_livro

load_dotenv()
TOKEN = os.getenv("TOKEN_TELEGRAM")

def main():
    print("Ligando os motores do Assistente Literário...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("livro", listar_ou_definir_livro))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot online e rodando!")
    app.run_polling()

if __name__ == "__main__":
    main()