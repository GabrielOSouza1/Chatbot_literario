import re
import nltk
import wikipediaapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import PorterStemmer 


nltk.download('punkt_tab', quiet=True)
nltk.download('punkt', quiet=True)


stemmer = PorterStemmer()

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

def preprocessamento(frase):
   
    frase = frase.lower().replace('\n', ' ')
    palavras = nltk.word_tokenize(frase)
    return " ".join([stemmer.stem(p) for p in palavras])

def treinar_base_livro(sentencas_originais):
   

    if not sentencas_originais:
        return None, None
        
    tfidf = TfidfVectorizer(ngram_range=(1,2), max_df=0.95, min_df=1)
    sentencas_tratadas = [preprocessamento(s) for s in sentencas_originais]
    matriz_tfidf = tfidf.fit_transform(sentencas_tratadas)
    return tfidf, matriz_tfidf


def calcular_resposta_cosseno(pergunta, sentencas_originais, tfidf, matriz_tfidf, threshold=0.15):

    if not matriz_tfidf:
        return None

   
    pergunta_tratada = preprocessamento(pergunta)
    pergunta_vetor = tfidf.transform([pergunta_tratada])
    
   
    similaridade = cosine_similarity(pergunta_vetor, matriz_tfidf)
    scores = similaridade.flatten()
    
    
    indice_max = scores.argsort()[-1]
    
    
    if scores[indice_max] < threshold:
        return None
        
    resposta = sentencas_originais[indice_max]
    
    if indice_max > 0:
        resposta = sentencas_originais[indice_max - 1] + " " + resposta
    if indice_max < len(sentencas_originais) - 1:
        resposta = resposta + " " + sentencas_originais[indice_max + 1]
        
    return resposta