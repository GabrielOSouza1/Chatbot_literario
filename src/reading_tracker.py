import os
import json
from datetime import datetime
from src.sentiment import analisar_sentimento

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "historico_leitura.json")

def iniciar_sessao_leitura(livro: str, total_paginas: int):
    """Gera o bloco inicial com o total de páginas do livro"""
    return {
        "livro": livro,
        "total_paginas": total_paginas,
        "inicio": datetime.now()
    }

def finalizar_sessao_leitura(sessao: dict, paginas_lidas: int, comentario: str) -> dict:
    inicio = sessao["inicio"]
    fim = datetime.now()
    duracao_minutos = round((fim - inicio).total_seconds() / 60, 1)
    
    # Força 1 minuto para não zerar em testes rápidos
    if duracao_minutos == 0:
        duracao_minutos = 1.0
        
    # Corrige bug das labels do CardiffNLP no sentiment.py
    sentimento = analisar_sentimento(comentario)
    
    # --- MATEMÁTICA DA LEITURA ---
    total_livro = sessao["total_paginas"]
    porcentagem_lida = round((paginas_lidas / total_livro) * 100, 1)
    
    # Ritmo: páginas por minuto
    paginas_por_minuto = paginas_lidas / duracao_minutos
    
    # Estimativa para o resto do livro
    paginas_restantes = total_livro - paginas_lidas
    if paginas_restantes < 0:
        paginas_restantes = 0
        
    if paginas_por_minuto > 0 and paginas_restantes > 0:
        tempo_restante_minutos = round(paginas_restantes / paginas_por_minuto, 1)
    else:
        tempo_restante_minutos = 0.0
        
    registro = {
        "livro": sessao["livro"],
        "total_paginas": total_livro,
        "paginas_lidas_sessao": paginas_lidas,
        "porcentagem_lida": porcentagem_lida,
        "tempo_minutos": duracao_minutos,
        "tempo_restante_estimado_min": tempo_restante_minutos,
        "data": fim.strftime("%d/%m/%Y %H:%M"),
        "comentario": comentario,
        "sentimento": sentimento
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

def obter_historico_texto() -> str:
    path = os.path.abspath(HISTORY_FILE)
    if not os.path.exists(path):
        return "📖 Você ainda não registrou nenhuma leitura."
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            historico = json.load(f)
    except Exception:
        return "📖 Erro ao ler o arquivo de histórico."
        
    if not historico:
        return "📖 Seu histórico de leituras está vazio."
        
    linhas = ["📊 *Seu Histórico de Leituras:*"]
    emojis = {"positivo": "🟢", "neutro": "🟡", "negativo": "🔴"}
    
    for i, r in enumerate(historico[-5:]):
        emo = emojis.get(r["sentimento"], "⚪")
        linhas.append(
            f"\n{i+1}. *{r['livro']}* - {r['data']}\n"
            f"   ⏱️ Leu {r['paginas_lidas_sessao']} pág em {r['tempo_minutos']} min ({r['porcentagem_lida']}% do livro)\n"
            f"   ⏳ Tempo estimado para terminar o livro: {r['tempo_restante_estimado_min']} min\n"
            f"   {emo} Sentimento: {r['sentimento'].capitalize()}\n"
            f"   💬 *Resenha:* _{r['comentario']}_"
        )
    return "\n".join(linhas)