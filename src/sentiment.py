import os
from transformers import pipeline

_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
            top_k=None
        )
    return _classifier

def analisar_sentimento(texto: str) -> str:
    try:
        classifier = get_classifier()
        resultados = classifier(texto[:512])

        if resultados and isinstance(resultados[0], list):
            resultados = resultados[0]

        scores = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        
        for r in resultados:
            label = r.get("label", "").lower()
            score_val = r.get("score", 0.0)
            
            if "label_0" in label or "neg" in label:
                scores["negative"] = score_val
            elif "label_1" in label or "neu" in label:
                scores["neutral"] = score_val
            elif "label_2" in label or "pos" in label:
                scores["positive"] = score_val

        pos = scores["positive"]
        neg = scores["negative"]
        neu = scores["neutral"]

        print(f"\n[IA SENTIMENTO] Frase: '{texto[:40]}'")
        print(f"📊 Scores -> POS: {pos:.2f} | NEG: {neg:.2f} | NEU: {neu:.2f}")

        if pos > 0.45 and pos > neg and pos > neu:
            return "positivo"
        elif neg > 0.45 and neg > pos and neg > neu:
            return "negativo"
        else:
            return "neutro"

    except Exception as e:
        print(f"[Sentimento] Erro: {e}")
        return "neutro"