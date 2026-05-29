from telegram import Update
from telegram.ext import ContextTypes
from src.nlp_engine import NLPEngine
from src.reading_tracker import iniciar_sessao_leitura, finalizar_sessao_leitura, obter_historico_texto, obter_livros_salvos

bot_nlp = NLPEngine()

LIVROS_DISPONIVEIS = [
    "O Nome do Vento", "Star Wars", "A Guerra dos Tronos",
    "Mistborn", "O Caminho dos Reis", "Fundação", "O Senhor dos Anéis"
]

def _get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("idioma", "pt")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args and args[0].lower() == "en":
        context.user_data["idioma"] = "en"
    elif args and args[0].lower() == "pt":
        context.user_data["idioma"] = "pt"
        
    lang = _get_lang(context)
    if lang == "pt":
        await update.message.reply_text(
            "📚 *Olá! Eu sou o seu Assistente Literário Bot.*\n\n"
            "📖 `/livro` - Escolhe a obra ativa da IA\n"
            "⏱️ `/ler` - Inicia o cronômetro de leitura\n"
            "🛑 `/parar` - Para o cronômetro e salva progresso\n"
            "📊 `/historico` - Exibe seu diário e estatísticas\n"
            "🌐 Mande `/start en` para mudar para inglês.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "📚 *Hello! I am your Literary Assistant Bot.*\n\n"
            "📖 `/book` - Choose active book for AI\n"
            "⏱️ `/read` - Start reading tracker\n"
            "🛑 `/stop` - Stop tracker and save progress\n"
            "📊 `/history` - View diary and stats\n"
            "🌐 Send `/start pt` to switch to Portuguese.",
            parse_mode="Markdown"
        )

async def listar_ou_definir_livro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = _get_lang(context)
    argument = " ".join(context.args).strip().lower()
    
    if not argument:
        lista_texto = "\n".join([f"• {l}" for l in LIVROS_DISPONIVEIS])
        if lang == "pt":
            await update.message.reply_text(f"📚 *Livros da IA:*\n\n{lista_texto}\n\nUse: `/livro Mistborn`", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"📚 *AI Books:*\n\n{lista_texto}\n\nUse: `/livro Mistborn`", parse_mode="Markdown")
        return

    livro_encontrado = next((l for l in LIVROS_DISPONIVEIS if l.lower() in argument), None)
    if livro_encontrado:
        context.user_data["livro_foco"] = livro_encontrado
        msg = f"📖 *Foco definido para:* '{livro_encontrado}'!" if lang == "pt" else f"📖 *Focus set to:* '{livro_encontrado}'!"
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        msg = "❌ Livro não encontrado." if lang == "pt" else "❌ Book not found."
        await update.message.reply_text(msg)

async def comando_ler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = _get_lang(context)
    livros_salvos = obter_livros_salvos()
    
    if livros_salvos:
        context.user_data["livros_disponiveis_selecao"] = livros_salvos
        context.user_data["estado_registro"] = "escolhendo_livro_historico"
        
        linhas = ["⏱️ *Iniciar Leitura!*" if lang == "pt" else "⏱️ *Start Reading!*"]
        linhas.append("Escolha um número do seu histórico ou digite um novo nome:\n" if lang == "pt" else "Choose a number from your history or type a new name:\n")
        
        for i, (l, dados) in enumerate(livros_salvos.items()):
            linhas.append(f"*{i+1}* - {l} (Progresso: {dados['lidas']}/{dados['total']} pág)")
            
        await update.message.reply_text("\n".join(linhas), parse_mode="Markdown")
    else:
        context.user_data["estado_registro"] = "aguardando_nome_livro"
        msg = "⏱️ *Iniciar Leitura!* Qual o nome do livro?" if lang == "pt" else "⏱️ *Start Reading!* What is the name of the book?"
        await update.message.reply_text(msg, parse_mode="Markdown")

async def comando_parar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = _get_lang(context)
    sessao = context.user_data.get("sessao_leitura")
    if not sessao:
        msg = "⚠️ Nenhum cronômetro rodando. Digite `/ler`!" if lang == "pt" else "⚠️ No timer running. Type `/ler`!"
        await update.message.reply_text(msg)
        return
        
    context.user_data["aguardando_paginas_lidas"] = sessao
    del context.user_data["sessao_leitura"]
    
    msg = "🛑 *Cronômetro parado!* Quantas páginas leu nessa sessão?" if lang == "pt" else "🛑 *Timer stopped!* How many pages did you read in this session?"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def comando_historico(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = _get_lang(context)
    await update.message.reply_text(obter_historico_texto(lang), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    estado = context.user_data.get("estado_registro")
    lang = _get_lang(context)

    if estado == "escolhendo_livro_historico":
        livros_salvos = context.user_data.get("livros_disponiveis_selecao", {})
        lista_nomes = list(livros_salvos.keys())
        
        try:
            indice = int(user_text) - 1
            if 0 <= indice < len(lista_nomes):
                livro_escolhido = lista_nomes[indice]
                total_p = livros_salvos[livro_escolhido]["total"]
                lidas_p = livros_salvos[livro_escolhido]["lidas"]
                
                del context.user_data["estado_registro"]
                del context.user_data["livros_disponiveis_selecao"]
                
                context.user_data["sessao_leitura"] = iniciar_sessao_leitura(livro_escolhido, total_p, lidas_p)
                
                if lang == "pt":
                    msg = f"⏱️ *Cronômetro rodando!*\nLivro: *{livro_escolhido}*\nVocê já leu {lidas_p} páginas dele anteriormente."
                else:
                    msg = f"⏱️ *Timer running!*\nBook: *{livro_escolhido}*\nYou have already read {lidas_p} pages of it."
                    
                await update.message.reply_text(msg, parse_mode="Markdown")
                return
        except ValueError:
            pass
            
        livro_digitado_norm = user_text.lower()
        match_livro = next((orig for orig, d in livros_salvos.items() if orig.lower() == livro_digitado_norm), None)
        
        if match_livro:
            total_p = livros_salvos[match_livro]["total"]
            lidas_p = livros_salvos[match_livro]["lidas"]
            del context.user_data["estado_registro"]
            del context.user_data["livros_disponiveis_selecao"]
            context.user_data["sessao_leitura"] = iniciar_sessao_leitura(match_livro, total_p, lidas_p)
            msg = f"⏱️ *Cronômetro rodando!*\nLivro: *{match_livro}* (Resgatado do histórico)" if lang == "pt" else f"⏱️ *Timer running!*\nBook: *{match_livro}* (Loaded from history)"
            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        context.user_data["temp_livro"] = user_text
        context.user_data["estado_registro"] = "aguardando_total_paginas"
        del context.user_data["livros_disponiveis_selecao"]
        msg = f"E qual o total de páginas de *{user_text}*?" if lang == "pt" else f"And what is the total pages of *{user_text}*?"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    if estado == "aguardando_nome_livro":
        livros_salvos = obter_livros_salvos()
        livro_digitado_norm = user_text.lower()
        match_livro = next((orig for orig, d in livros_salvos.items() if orig.lower() == livro_digitado_norm), None)
        
        if match_livro:
            total_p = livros_salvos[match_livro]["total"]
            lidas_p = livros_salvos[match_livro]["lidas"]
            del context.user_data["estado_registro"]
            context.user_data["sessao_leitura"] = iniciar_sessao_leitura(match_livro, total_p, lidas_p)
            msg = f"⏱️ *Cronômetro rodando!*\nLivro: *{match_livro}* (Resgatado do histórico)" if lang == "pt" else f"⏱️ *Timer running!*\nBook: *{match_livro}* (Loaded from history)"
            await update.message.reply_text(msg, parse_mode="Markdown")
            return

        context.user_data["temp_livro"] = user_text
        context.user_data["estado_registro"] = "aguardando_total_paginas"
        msg = f"E qual o total de páginas de *{user_text}*?" if lang == "pt" else f"And what is the total pages of *{user_text}*?"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    if estado == "aguardando_total_paginas":
        try:
            total_p = int(user_text)
        except ValueError:
            await update.message.reply_text("❌ Digite apenas números:" if lang == "pt" else "❌ Enter numbers only:")
            return
            
        livro = context.user_data["temp_livro"]
        del context.user_data["estado_registro"]
        del context.user_data["temp_livro"]
        
        context.user_data["sessao_leitura"] = iniciar_sessao_leitura(livro, total_p, 0)
        msg = f"⏱️ *Cronômetro rodando!*\nLivro: *{livro}*" if lang == "pt" else f"⏱️ *Timer running!*\nBook: *{livro}*"
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    sessao_paginas = context.user_data.get("aguardando_paginas_lidas")
    if sessao_paginas:
        try:
            p_lidas = int(user_text)
        except ValueError:
            await update.message.reply_text("❌ Digite apenas números:" if lang == "pt" else "❌ Enter numbers only:")
            return
            
        context.user_data["temp_p_lidas"] = p_lidas
        context.user_data["aguardando_resenha"] = sessao_paginas
        del context.user_data["aguardando_paginas_lidas"]
        
        msg = "Perfeito! O que achou dessa sessão?" if lang == "pt" else "Perfect! What did you think of this session?"
        await update.message.reply_text(msg)
        return

    sessao_fim = context.user_data.get("aguardando_resenha")
    if sessao_fim:
        p_lidas = context.user_data["temp_p_lidas"]
        del context.user_data["aguardando_resenha"]
        del context.user_data["temp_p_lidas"]
        
        await update.message.reply_text("🤖 ...")
        registro = finalizar_sessao_leitura(sessao_fim, p_lidas, user_text)
        
        emojis_pt = {"positivo": "🟢 Positivo", "neutro": "🟡 Neutro", "negativo": "🔴 Negativo"}
        emojis_en = {"positivo": "🟢 Positive", "neutro": "🟡 Neutral", "negativo": "🔴 Negative"}
        emo = emojis_pt.get(registro['sentimento']) if lang == "pt" else emojis_en.get(registro['sentimento'])
        
        status_concluido = "\n🏆 *LIVRO TOTALMENTE CONCLUÍDO!*" if registro.get("concluido", False) else ""
        status_concluido_en = "\n🏆 *BOOK FULLY COMPLETED!*" if registro.get("concluido", False) else ""

        if lang == "pt":
            await update.message.reply_text(
                f"✅ *Sessão Registrada!*\n\n"
                f"📖 *Livro:* {registro['livro']}\n"
                f"⏱️ *Tempo da Sessão:* {registro['tempo_minutos']} min\n"
                f"📊 *Progresso Geral:* {registro['pagina_atual_acumulada']}/{registro['total_paginas']} pág ({registro['porcentagem_lida']}%)\n"
                f"⏳ *Projeção:* Restam *{registro['tempo_restante_estimado_min']} minutos* de leitura para terminar o livro.\n"
                f"🧠 *Sentimento:* {emo}{status_concluido}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"✅ *Session Recorded!*\n\n"
                f"📖 *Book:* {registro['livro']}\n"
                f"⏱️ *Session Time:* {registro['tempo_minutos']} min\n"
                f"📊 *Overall Progress:* {registro['pagina_atual_acumulada']}/{registro['total_paginas']} pages ({registro['porcentagem_lida']}%)\n"
                f"⏳ *Projection:* *{registro['tempo_restante_estimado_min']} minutes* left to finish the book.\n"
                f"🧠 *Sentiment:* {emo}{status_concluido_en}",
                parse_mode="Markdown"
            )
        return

    livro_foco = context.user_data.get("livro_foco")
    resposta = bot_nlp.answer(user_text, livro_foco=livro_foco)
    await update.message.reply_text(resposta, parse_mode="Markdown")