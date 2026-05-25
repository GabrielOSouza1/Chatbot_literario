import re
from nltk.corpus import stopwords
import nltk

nltk.download("stopwords", quiet=True)
STOPWORDS_PT = set(stopwords.words("portuguese"))

SECTION_TO_INTENT = {
    "história": "historia_lore",
    "enredo": "historia_lore",
    "trama": "historia_lore",
    "sinopse": "historia_lore",
    "habilidades": "habilidades",
    "poderes": "habilidades",
    "alomancia": "habilidades",
    "sistema de magia": "habilidades",
    "personalidade": "personagens",
    "biografia": "personagens",
    "personagens": "personagens",
    "mundo": "mundo_universo",
    "universo": "mundo_universo",
    "ambientação": "mundo_universo",
    "cenário": "mundo_universo",
}


def clean_sentence(sentence: str) -> str:
    sentence = re.sub(r"\[\d+\]", "", sentence)
    sentence = re.sub(r"\{\{[^}]+\}\}", "", sentence)
    sentence = sentence.replace("\n", " ").strip()
    sentence = re.sub(r"\s+", " ", sentence)
    return sentence


def is_valid_sentence(sentence: str) -> bool:
    if len(sentence.split()) < 6:
        return False
    if sentence.startswith("[") or sentence.startswith("("):
        return False
    return True


def remove_stopwords(sentence: str) -> str:
    words = sentence.lower().split()
    filtered = [w for w in words if w not in STOPWORDS_PT]
    return " ".join(filtered)


def heading_to_intent(heading_text: str) -> str | None:
    h = heading_text.lower().strip()
    for key, intent in SECTION_TO_INTENT.items():
        if key in h:
            return intent
    return None


def classify_sentence_fallback(sentence: str) -> str:
    s = sentence.lower()
    if any(x in s for x in [
        "personagem", "protagonista", "vilão", "líder",
        "nascido das brumas", "nascida das brumas", "kvothe", "jon snow", "daenerys",
    ]):
        return "personagens"
    if any(x in s for x in [
        "habilidade", "poder", "queimar metal", "metais",
        "alomancia", "magia", "força",
    ]):
        return "habilidades"
    if any(x in s for x in [
        "história", "enredo", "trama", "narrativa",
        "império final", "tronos",
    ]):
        return "historia_lore"
    if any(x in s for x in [
        "mundo", "universo", "reino", "cidade", "cenário", "westeros", "galáxia",
    ]):
        return "mundo_universo"
    return "curiosidades"