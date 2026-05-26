import os
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
from dotenv import load_dotenv
from src.bot_telegram import start, handle_message, listar_ou_definir_livro, comando_ler, comando_parar, comando_historico

load_dotenv()
TOKEN = os.getenv("TOKEN_TELEGRAM")

def main():
    print("Ligando os motores do Assistente Literário...")
    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos de Configuração e Menu
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("livro", listar_ou_definir_livro))
    
    # Comandos do Monitor de Leitura
    app.add_handler(CommandHandler("ler", comando_ler))
    app.add_handler(CommandHandler("parar", comando_parar))
    app.add_handler(CommandHandler("historico", comando_historico))
    
    # Tratamento de textos de mensagens
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot online e rodando!")
    app.run_polling()

if __name__ == "__main__":
    main()