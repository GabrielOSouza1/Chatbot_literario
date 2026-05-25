import requests
import nltk
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from text_processing import heading_to_intent, clean_sentence, is_valid_sentence


def traduzir_texto(texto: str) -> str:
    try:
        if len(texto.strip()) > 5:
            return GoogleTranslator(source="en", target="pt").translate(texto)
    except Exception:
        pass
    return texto


def _extrair_blocos_fandom(api_url: str, titulo: str, topic: str, url: str, headers: dict) -> list[dict]:
    blocks = []
    params = {
        "action": "parse",
        "page": titulo,
        "prop": "text",
        "format": "json",
        "origin": "*",
    }
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return blocks
        data = response.json()
        html = data.get("parse", {}).get("text", {}).get("*", "")
        if not html:
            return blocks
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["script", "style", "table"]):
            tag.decompose()
        paragrafos = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 30]
        for p in paragrafos[:15]:
            frases = nltk.tokenize.sent_tokenize(p, language="english")
            for i in range(0, len(frases), 2):
                en_text = " ".join(frases[i : i + 2])
                pt_text = clean_sentence(traduzir_texto(en_text))
                if is_valid_sentence(pt_text):
                    blocks.append({
                        "topic": topic,
                        "source": url,
                        "intent": "personagens",
                        "text": pt_text,
                    })
    except Exception as e:
        print(f"     [ERRO FANDOM] {api_url}: {e}")
    return blocks


def _extrair_blocos_html(url: str, topic: str, headers: dict) -> list[dict]:
    """Scraping HTML genérico — funciona para Coppermind, awoiaf e similares."""
    blocks = []
    current_intent = "curiosidades"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all(["script", "style"]):
            tag.decompose()
        content = (
            soup.select_one("#mw-content-text")
            or soup.select_one(".mw-parser-output")
            or soup
        )
        for tag in content.find_all(["h2", "h3", "p"]):
            if tag.name in ["h2", "h3"]:
                detected = heading_to_intent(tag.get_text())
                if detected:
                    current_intent = detected
            elif tag.name == "p":
                raw = tag.get_text().strip()
                if not raw:
                    continue
                sentences = nltk.sent_tokenize(raw, language="english")
                for i in range(0, len(sentences), 2):
                    en_text = " ".join(sentences[i : i + 2])
                    pt_text = clean_sentence(traduzir_texto(en_text))
                    if not is_valid_sentence(pt_text):
                        continue
                    blocks.append({
                        "topic": topic,
                        "source": url,
                        "intent": current_intent,
                        "text": pt_text,
                    })
    except Exception as e:
        print(f"     [ERRO HTML] {url}: {e}")
    return blocks


def scrape_page(url: str, topic: str) -> list[dict]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    if "fandom.com" in url:
        subdominio = url.split("//")[1].split(".fandom.com")[0]
        titulo = url.split("/wiki/")[-1]
        api_url = f"https://{subdominio}.fandom.com/api.php"
        return _extrair_blocos_fandom(api_url, titulo, topic, url, headers)
    else:
        # Coppermind, awoiaf e qualquer outro — scraping HTML direto
        return _extrair_blocos_html(url, topic, headers)