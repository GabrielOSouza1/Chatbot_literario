from telegram import Update
from telegram.ext import ContextTypes
from src.nlp_engine import NLPEngine

bot_nlp = NLPEngine()

LIVROS_DISPONIVEIS = [
    "O Nome do Vento",
    "Star Wars",
    "A Guerra dos Tronos",
    "Mistborn",
    "O Caminho dos Reis",
    "Fundação",
    "Devoradores de Estrelas",
    "O Senhor dos Anéis",
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Olá! Eu sou o seu Assistente Literário Bot.*\n\n"
        "📖 Use o comando `/livro` para ver as obras disponíveis na minha base de dados.\n"
        "💬 Depois, basta me perguntar direto sobre os personagens, mundos ou poderes da obra selecionada!",
        parse_mode="Markdown",
    )


async def listar_ou_definir_livro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/livro — lista os livros disponíveis ou seleciona um pelo nome."""
    argumento = " ".join(context.args).strip().lower()

    if not argumento:
        lista_texto = "\n".join([f"• {l}" for l in LIVROS_DISPONIVEIS])
        await update.message.reply_text(
            f"📚 *Livros Disponíveis na Base:*\n\n{lista_texto}\n\n"
            f"Para focar em um, digite por exemplo: `/livro Mistborn`",
            parse_mode="Markdown",
        )
        return

    livro_encontrado = next(
        (l for l in LIVROS_DISPONIVEIS if l.lower() in argumento), None
    )

    if livro_encontrado:
        context.user_data["livro_foco"] = livro_encontrado
        await update.message.reply_text(
            f"📖 *Foco definido para:* '{livro_encontrado}'!\n"
            f"Agora suas perguntas serão respondidas com prioridade para este universo.",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "❌ Esse livro não está cadastrado na minha base.\n"
            "Digite `/livro` para ver a lista de opções disponíveis."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    livro_foco = context.user_data.get("livro_foco")

    # Passa o livro_foco direto para o NLP filtrar na fonte
    resposta = bot_nlp.answer(user_text, livro_foco=livro_foco)
    await update.message.reply_text(resposta, parse_mode="Markdown")