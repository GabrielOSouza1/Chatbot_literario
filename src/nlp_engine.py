import os
import json
import numpy as np
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import nltk

nltk.download("stopwords", quiet=True)
STOPWORDS_PT = set(stopwords.words("portuguese"))

KB_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge_base_pt.json")


class NLPEngine:
    def __init__(self):
        self.nlp_pt = spacy.load("pt_core_news_lg")
        self.kb_pt = self._load_knowledge_base()
        self.all_blocks: list[dict] = []

        # Estrutura correta: {intent: [{topic, source, intent, text}, ...]}
        for intent_blocks in self.kb_pt.values():
            if isinstance(intent_blocks, list):
                self.all_blocks.extend(intent_blocks)

        print(f"✅ [NLPEngine] {len(self.all_blocks)} blocos carregados da base.")

        if not self.all_blocks:
            print("⚠️  [NLPEngine] Base vazia! Rode: python src/build_knowledge_base.py")

    def _load_knowledge_base(self) -> dict:
        path = os.path.abspath(KB_FILE)
        print(f"🔍 [NLPEngine] Carregando base de: {path}")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        print(f"⚠️  [NLPEngine] Arquivo não encontrado: {path}")
        return {}

    def preprocessing(self, sentence: str) -> str:
        doc = self.nlp_pt(sentence.lower())
        entity_texts = {ent.start: ent.text.lower() for ent in doc.ents}
        tokens = []
        for token in doc:
            if token.i in entity_texts:
                tokens.append(entity_texts[token.i])
            elif (
                not token.is_punct
                and not token.is_space
                and not token.like_num
                and len(token.text) > 1
                and not token.is_stop
            ):
                tokens.append(token.lemma_)
        multi = [ent.text.lower() for ent in doc.ents if len(ent.text.split()) > 1]
        return " ".join(list(dict.fromkeys(tokens + multi)))

    def detect_intent(self, text: str) -> str:
        t = text.lower()
        intents = {
            "personagens": ["quem é", "quem foi", "personagem", "protagonista", "vilão", "herói"],
            "habilidades": ["poder", "habilidade", "ataques", "skills", "sistema de magia", "alomancia", "magia", "força"],
            "historia_lore": ["história", "enredo", "trama", "narrativa", "acontece"],
            "mundo_universo": ["mundo", "universo", "reino", "onde se passa", "cenário", "planeta"],
        }
        for intent, keywords in intents.items():
            for kw in keywords:
                if kw in t:
                    return intent
        return "personagens"

    def answer(self, user_text: str, livro_foco: str = None, threshold: float = 0.15, top_k: int = 2) -> str:
        if not self.all_blocks:
            return (
                "⚠️ Base de conhecimento vazia.\n"
                "Rode `python src/build_knowledge_base.py` e reinicie o bot."
            )

        intent = self.detect_intent(user_text)
        entities = [
            w.lower()
            for w in user_text.split()
            if w.lower() not in STOPWORDS_PT and len(w) > 2
        ]

        # 1. Filtra pelo livro em foco
        if livro_foco:
            pool = [b for b in self.all_blocks if b.get("topic", "").lower() == livro_foco.lower()]
            if not pool:
                pool = self.all_blocks
        else:
            pool = self.all_blocks

        # 2. Filtra por entidades ou intent
        filtered = [b for b in pool if any(e in b.get("text", "").lower() for e in entities)]
        if not filtered:
            filtered = [b for b in pool if b.get("intent") == intent]
        if not filtered:
            filtered = pool

        sentences_pool = [b["text"] for b in filtered]
        topics_pool = [b.get("topic", "?") for b in filtered]

        # TF-IDF
        cleaned_pool = [self.preprocessing(s) for s in sentences_pool]
        user_clean = self.preprocessing(user_text)
        vectorizer = TfidfVectorizer()
        all_vectors = vectorizer.fit_transform(cleaned_pool + [user_clean])
        tfidf_scores = cosine_similarity(all_vectors[-1], all_vectors[:-1])[0]

        # Similaridade semântica spaCy
        user_doc = self.nlp_pt(user_text)
        spacy_scores = np.array([
            user_doc.similarity(self.nlp_pt(s)) if user_doc.vector_norm else 0.0
            for s in sentences_pool
        ])

        combined = 0.7 * tfidf_scores + 0.3 * spacy_scores

        for i, s in enumerate(sentences_pool):
            if any(e in s.lower() for e in entities):
                combined[i] *= 2.0

        sorted_idx = combined.argsort()[::-1]

        if combined[sorted_idx[0]] < threshold:
            return "🤔 Não encontrei uma resposta focada sobre isso nos registros das obras."

        respostas = []
        vistos = set()
        for idx in sorted_idx:
            if combined[idx] < threshold:
                break
            texto = sentences_pool[idx]
            chave = texto[:60]
            if chave in vistos:
                continue
            vistos.add(chave)
            respostas.append(f"📌 *[{topics_pool[idx]}]*\n{texto}")
            if len(respostas) >= top_k:
                break

        return "\n\n".join(respostas)