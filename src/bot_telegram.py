from telegram import Update
from telegram.ext import ContextTypes
from src.nlp_engine import NLPEngine
from src.reading_tracker import iniciar_sessao_leitura, finalizar_sessao_leitura, obter_historico_texto

bot_nlp = NLPEngine()

LIVROS_DISPONIVEIS = [
    "O Nome do Vento", "Star Wars", "A Guerra dos Tronos",
    "Mistborn", "O Caminho dos Reis", "Fundação", "O Senhor dos Anéis"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Olá! Eu sou o seu Assistente Literário Bot.*\n\n"
        "📖 `/livro` - Escolhe a obra ativa para as perguntas de IA\n"
        "⏱️ `/ler` - Inicia o passo a passo e o cronômetro de leitura\n"
        "🛑 `/parar` - Para o cronômetro, pede as páginas e grava sua opinião\n"
        "📊 `/historico` - Exibe seu diário de leituras, progresso e sentimentos\n\n"
        "💬 Mande qualquer pergunta sobre os livros cadastrados!",
        parse_mode="Markdown",
    )

async def listar_ou_definir_livro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/livro — lista os livros disponíveis ou seleciona um pelo nome para a IA de busca."""
    argument = " ".join(context.args).strip().lower()
    
    if not argument:
        lista_texto = "\n".join([f"• {l}" for l in LIVROS_DISPONIVEIS])
        await update.message.reply_text(
            f"📚 *Livros de Perguntas da IA:*\n\n{lista_texto}\n\n"
            f"Para focar, digite: `/livro Mistborn`",
            parse_mode="Markdown",
        )
        return

    livro_encontrado = next((l for l in LIVROS_DISPONIVEIS if l.lower() in argument), None)
    if livro_encontrado:
        context.user_data["livro_foco"] = livro_encontrado
        await update.message.reply_text(
            f"📖 *Foco de perguntas definido para:* '{livro_encontrado}'!\n"
            f"Agora suas dúvidas de lore terão prioridade neste universo.", 
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ Esse livro não está na base de perguntas. Mande `/livro` para ver a lista de opções."
        )

# === SISTEMA DO MONITOR DE LEITURA (LIVRE) ===

async def comando_ler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["estado_registro"] = "aguardando_nome_livro"
    await update.message.reply_text("⏱️ *Iniciar Leitura!* Qual o nome do livro?")

async def comando_parar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sessao = context.user_data.get("sessao_leitura")
    if not sessao:
        await update.message.reply_text("⚠️ Nenhum cronômetro rodando. Digite `/ler` para começar!")
        return
        
    context.user_data["aguardando_paginas_lidas"] = sessao
    del context.user_data["sessao_leitura"]
    
    await update.message.reply_text("🛑 *Cronômetro parado!* Quantas páginas você leu nessa sessão?")

async def comando_historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(obter_historico_texto(), parse_mode="Markdown")

# === GERENCIADOR DE ESTADOS INTELIGENTE ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    estado = context.user_data.get("estado_registro")

    # Passo 1: Recebe o nome do livro
    if estado == "aguardando_nome_livro":
        context.user_data["temp_livro"] = user_text
        context.user_data["estado_registro"] = "aguardando_total_paginas"
        await update.message.reply_text(f"E qual o total de páginas que o livro *{user_text}* tem no total?")
        return

    # Passo 2: Recebe o total de páginas e inicia o cronômetro
    if estado == "aguardando_total_paginas":
        try:
            total_p = int(user_text)
        except ValueError:
            await update.message.reply_text("❌ Digite apenas números para o total de páginas:")
            return
            
        livro = context.user_data["temp_livro"]
        del context.user_data["estado_registro"]
        del context.user_data["temp_livro"]
        
        context.user_data["sessao_leitura"] = iniciar_sessao_leitura(livro, total_p)
        await update.message.reply_text(
            f"⏱️ *Cronômetro rodando!*\nLivro: *{livro}* ({total_p} páginas)\n\nMande `/parar` quando terminar.",
            parse_mode="Markdown"
        )
        return

    # Passo 3: Recebe as páginas lidas na sessão (Após dar /parar)
    sessao_paginas = context.user_data.get("aguardando_paginas_lidas")
    if sessao_paginas:
        try:
            p_lidas = int(user_text)
        except ValueError:
            await update.message.reply_text("❌ Digite apenas o número de páginas lidas:")
            return
            
        context.user_data["temp_p_lidas"] = p_lidas
        context.user_data["aguardando_resenha"] = sessao_paginas
        del context.user_data["aguardando_paginas_lidas"]
        
        await update.message.reply_text("Perfeito! Agora me conte em uma frase: o que achou dessa sessão?")
        return

    # Passo 4: Recebe a opinião e calcula tudo com IA
    sessao_fim = context.user_data.get("aguardando_resenha")
    if sessao_fim:
        p_lidas = context.user_data["temp_p_lidas"]
        del context.user_data["aguardando_resenha"]
        del context.user_data["temp_p_lidas"]
        
        await update.message.reply_text("🤖 _Processando sua opinião e calculando projeções..._")
        registro = finalizar_sessao_leitura(sessao_fim, p_lidas, user_text)
        
        emojis = {"positivo": "🟢 Positivo", "neutro": "🟡 Neutro", "negativo": "🔴 Negativo"}
        
        await update.message.reply_text(
            f"✅ *Sessão Registrada!*\n\n"
            f"📖 *Livro:* {registro['livro']}\n"
            f"⏱️ *Tempo da Sessão:* {registro['tempo_minutos']} min\n"
            f"📊 *Progresso:* Você leu {registro['porcentagem_lida']}% do livro nesta sessão.\n"
            f"⏳ *Projeção:* No ritmo atual, restam *{registro['tempo_restante_estimado_min']} minutos* para você fechar o livro!\n"
            f"🧠 *Sentimento:* {emojis.get(registro['sentimento'], registro['sentimento'])}\n\n"
            f"Consulte seu progresso em `/historico`.",
            parse_mode="Markdown"
        )
        return

    # Fallback para as perguntas normais da lore
    livro_foco = context.user_data.get("livro_foco")
    resposta = bot_nlp.answer(user_text, livro_foco=livro_foco, sentimento="neutro")
    await update.message.reply_text(resposta, parse_mode="Markdown")