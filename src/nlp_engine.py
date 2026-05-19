import re
import wikipediaapi

def dividir_sentencas(texto):
    
  
    texto = re.sub(r'\[.*?\]', '', texto)
    frases = re.split(r'\.\s+', texto)
    return [f.strip() for f in frases if len(f.strip()) > 20]


def buscar_livro_wikipedia(nome_livro):
  
    
    USER_AGENT = "AssistenteLiterarioBot/1.0 (contato@fatec.edu)"
    
    
    wiki_pt = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="pt")
    page_pt = wiki_pt.page(nome_livro)
    
    if page_pt.exists():
        print(f"📚 [NLP ENGINE] Livro encontrado em PT: {page_pt.title}")
        return dividir_sentencas(page_pt.text)
        
    
    print(f"🔍 [NLP ENGINE] '{nome_livro}' não achado em PT. Tentando em EN...")
    wiki_en = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="en")
    page_en = wiki_en.page(nome_livro)
    
    if page_en.exists():
        print(f"📚 [NLP ENGINE] Livro encontrado em EN: {page_en.title}")
        return dividir_sentencas(page_en.text)
        
    
    print(f"❌ [NLP ENGINE] Livro '{nome_livro}' não foi encontrado na Wikipédia.")
    return []

   