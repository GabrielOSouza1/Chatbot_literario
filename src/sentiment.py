from transformers import pipeline

_classifier = None


def get_classifier():
    global _classifier
    if _classifier is None:
        print("[Sentimento] Carregando modelo HuggingFace...")
        _classifier = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
            top_k=None,  # retorna todos os scores
        )
        print("[Sentimento] Modelo carregado!")
    return _classifier


def analisar_sentimento(texto: str) -> str:
    try:
        classifier = get_classifier()
        # O pipeline com top_k=None joga o resultado direto na lista
        resultados = classifier(texto[:512])

        # Se vier encapsulado em outra lista por preciosismo do pipeline, a gente desfaz
        if resultados and isinstance(resultados[0], list):
            resultados = resultados[0]

        # Mapeamento definitivo do CardiffNLP:
        # label_0 -> negative | label_1 -> neutral | label_2 -> positive
        scores = {}
        for r in resultados:
            label = r["label"].lower()
            if label == "label_0":
                scores["negative"] = r["score"]
            elif label == "label_1":
                scores["neutral"] = r["score"]
            elif label == "label_2":
                scores["positive"] = r["score"]
            else:
                scores[label] = r["score"]

        pos = scores.get("positive", 0)
        neg = scores.get("negative", 0)
        neu = scores.get("neutral", 0)

        # Print de debug no terminal do VS Code para você acompanhar a decisão matemática da IA
        print(f"[Sentimento Debug] TEXTO: '{texto[:30]}' | POS: {pos:.4f} | NEG: {neg:.4f} | NEU: {neu:.4f}")

        # Mantém sua regra de segurança (threshold > 0.5)
        if pos > 0.5 and pos > neg and pos > neu:
            return "positivo"
        elif neg > 0.5 and neg > pos and neg > neu:
            return "negativo"
        else:
            return "neutro"

    except Exception as e:
        print(f"[Sentimento] Erro crítico na análise: {e}")
        return "neutro"