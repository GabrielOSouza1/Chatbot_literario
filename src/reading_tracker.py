import os
import json
from datetime import datetime
from src.sentiment import analisar_sentimento

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "historico_leitura.json")

def obter_livros_salvos():
    path = os.path.abspath(HISTORY_FILE)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            historico = json.load(f)
        livros = {}
        for r in historico:
            livro_nome = r["livro"].strip()
            total = r.get("total_paginas", 0)
            lidas_ate_agora = r.get("pagina_atual_acumulada", 0)
            
            chave_busca = livro_nome.lower()
            if chave_busca not in livros or lidas_ate_agora > livros[chave_busca]["lidas"]:
                livros[chave_busca] = {"nome_original": livro_nome, "total": total, "lidas": lidas_ate_agora}
        
        resultado_final = {}
        for item in livros.values():
            resultado_final[item["nome_original"]] = {"total": item["total"], "lidas": item["lidas"]}
        return resultado_final
    except Exception:
        return {}

def iniciar_sessao_leitura(livro: str, total_paginas: int, pagina_atual_acumulada: int = 0):
    return {
        "livro": livro.strip(),
        "total_paginas": total_paginas,
        "pagina_anterior_acumulada": pagina_atual_acumulada,
        "inicio": datetime.now()
    }

def finalizar_sessao_leitura(sessao: dict, paginas_lidas_sessao: int, comentario: str) -> dict:
    inicio = sessao["inicio"]
    fim = datetime.now()
    duracao_minutos = round((fim - inicio).total_seconds() / 60, 1)
    
    if duracao_minutos == 0:
        duracao_minutos = 1.0
        
    sentimento = analisar_sentimento(comentario)
    total_livro = sessao["total_paginas"]
    
    nova_pagina_atual = sessao["pagina_anterior_acumulada"] + paginas_lidas_sessao
    concluido = False
    if nova_pagina_atual >= total_livro:
        nova_pagina_atual = total_livro
        concluido = True
        
    porcentagem_lida = round((nova_pagina_atual / total_livro) * 100, 1)
    
    paginas_por_minuto = paginas_lidas_sessao / duracao_minutos
    paginas_restantes = total_livro - nova_pagina_atual
    
    if paginas_por_minuto > 0 and paginas_restantes > 0:
        tempo_restante_minutos = round(paginas_restantes / paginas_por_minuto, 1)
    else:
        tempo_restante_minutos = 0.0
        
    registro = {
        "livro": sessao["livro"],
        "total_paginas": total_livro,
        "paginas_lidas_sessao": paginas_lidas_sessao,
        "pagina_atual_acumulada": nova_pagina_atual,
        "porcentagem_lida": porcentagem_lida,
        "tempo_minutos": duracao_minutos,
        "tempo_restante_estimado_min": tempo_restante_minutos,
        "data": fim.strftime("%d/%m/%Y %H:%M"),
        "comentario": comentario,
        "sentimento": sentimento,
        "concluido": concluido
    }
    
    _salvar_no_historico(registro)
    return registro

def _salvar_no_historico(registro: dict):
    path = os.path.abspath(HISTORY_FILE)
    historico = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                historico = json.load(f)
        except Exception:
            historico = []
            
    historico.append(registro)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

def obter_historico_texto(lang: str = "pt") -> str:
    path = os.path.abspath(HISTORY_FILE)
    if not os.path.exists(path):
        return "📖 Você ainda não registrou nenhuma leitura." if lang == "pt" else "📖 You haven't recorded any reading yet."
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            historico = json.load(f)
    except Exception:
        return "📖 Erro ao ler o histórico." if lang == "pt" else "📖 Error reading history."
        
    if not historico:
        return "📖 Seu histórico está vazio." if lang == "pt" else "📖 Your history is empty."
        
    linhas = ["📊 *Seu Histórico de Leituras:*" if lang == "pt" else "📊 *Your Reading History:*"]
    emojis = {"positivo": "🟢", "neutro": "🟡", "negativo": "🔴"}
    
    for i, r in enumerate(historico[-5:]):
        emo = emojis.get(r["sentimento"], "⚪")
        sent_label = r["sentimento"].capitalize()
        if lang == "en":
            sent_label = "Positive" if r["sentimento"] == "positivo" else "Negative" if r["sentimento"] == "negativo" else "Neutral"
            
        pag_atual = r.get("pagina_atual_acumulada", r["paginas_lidas_sessao"])
        status_concluido = " 🎉 *[CONCLUÍDO]*" if r.get("concluido", False) else ""
        
        if lang == "pt":
            linhas.append(
                f"\n{i+1}. *{r['livro']}*{status_concluido} - {r['data']}\n"
                f"   ⏱️ Leu {r['paginas_lidas_sessao']} pág em {r['tempo_minutos']} min (Progresso: {pag_atual}/{r['total_paginas']} pág - {r['porcentagem_lida']}%)\n"
                f"   ⏳ Tempo estimado para terminar: {r['tempo_restante_estimado_min']} min\n"
                f"   {emo} Sentimento: {sent_label}\n"
                f"   💬 *Resenha:* _{r['comentario']}_"
            )
        else:
            status_concluido_en = " 🎉 *[COMPLETED]*" if r.get("concluido", False) else ""
            linhas.append(
                f"\n{i+1}. *{r['livro']}*{status_concluido_en} - {r['data']}\n"
                f"   ⏱️ Read {r['paginas_lidas_sessao']} pages in {r['tempo_minutos']} min (Progress: {pag_atual}/{r['total_paginas']} pages - {r['porcentagem_lida']}%)\n"
                f"   ⏳ Estimated time left: {r['tempo_restante_estimado_min']} min\n"
                f"   {emo} Sentiment: {sent_label}\n"
                f"   💬 *Review:* _{r['comentario']}_"
            )
    return "\n".join(linhas)