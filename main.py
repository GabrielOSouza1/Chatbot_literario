import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from src.bot_telegram import (
    start,
    listar_ou_definir_livro,
    comando_ler,
    comando_parar,
    comando_historico,
    handle_message
)

load_dotenv()

def main():
    token = os.getenv("TOKEN_TELEGRAM")
    if not token:
        print("Erro: TOKEN_TELEGRAM não encontrado no arquivo .env")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("livro", listar_ou_definir_livro))
    app.add_handler(CommandHandler("book", listar_ou_definir_livro))
    app.add_handler(CommandHandler("ler", comando_ler))
    app.add_handler(CommandHandler("read", comando_ler))
    app.add_handler(CommandHandler("parar", comando_parar))
    app.add_handler(CommandHandler("stop", comando_parar))
    app.add_handler(CommandHandler("historico", comando_historico))
    app.add_handler(CommandHandler("history", comando_historico))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot online e operando em modo híbrido bilíngue...")
    app.run_polling()

if __name__ == "__main__":
    main()