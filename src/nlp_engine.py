import os
import json
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class NLPEngine:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.vectorizer = TfidfVectorizer()
        
        # Pega a pasta de onde o terminal está rodando (raiz do projeto)
        self.base_path = os.path.join(os.getcwd(), "knowledge_base_pt.json")
        self.kb_data = self._load_kb()

    def _load_kb(self):
        path = os.path.abspath(self.base_path)
        print(f"\n🔍 [IA BIBLIOTECA] Tentando carregar a base de dados de: {path}")
        
        if not os.path.exists(path):
            # Segunda tentativa: tenta buscar um nível acima caso o terminal esteja na pasta src
            path = os.path.join(os.path.dirname(__file__), "..", "knowledge_base_pt.json")
            path = os.path.abspath(path)
            print(f"🔄 [IA BIBLIOTECA] Segunda tentativa (caminho relativo): {path}")

        if not os.path.exists(path):
            print(f"⚠️ [Aviso] Arquivo JSON não foi encontrado em nenhum dos caminhos!")
            return {}
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                dados = json.load(f)
                print(f"✅ [IA BIBLIOTECA] Sucesso! Carregados {len(dados)} livros da base de conhecimento.")
                return dados
        except Exception as e:
            print(f"❌ [Erro] Falha crítica ao ler o arquivo JSON: {e}")
            return {}

    def answer(self, question: str, livro_foco: str = None) -> str:
        if not self.kb_data:
            return "🤖 Desculpe, minha base de dados de livros está vazia ou não foi encontrada no momento."

        documentos = []
        metadados = []

        for livro, capitulos in self.kb_data.items():
            if livro_foco and livro.lower() != livro_foco.lower():
                continue
            for cap, textos in capitulos.items():
                for t in textos:
                    documentos.append(t)
                    metadados.append({"livro": livro, "capitulo": cap})

        if not documentos:
            if livro_foco:
                return f"🤖 Não encontrei nenhuma informação específica sobre o livro *{livro_foco}* na minha base."
            return "🤖 Não encontrei informações sobre livros na minha base de dados."

        textos_limpos = [" ".join([token.lemma_ for token in self.nlp(doc.lower()) if not token.is_stop]) for doc in documentos]
        pergunta_limpa = " ".join([token.lemma_ for token in self.nlp(question.lower()) if not token.is_stop])

        if not pergunta_limpa.strip():
            pergunta_limpa = question.lower()

        try:
            tfidf_matrix = self.vectorizer.fit_transform(textos_limpos)
            query_vector = self.vectorizer.transform([pergunta_limpa])
            
            similaridades = cosine_similarity(query_vector, tfidf_matrix).flatten()
            melhor_idx = similaridades.argsort()[-1]
            
            if similaridades[melhor_idx] < 0.15:
                return "🤖 Hum, eu conheço os livros, mas não encontrei nenhum trecho específico na minha base que responda exatamente a isso."

            resposta_bruta = documentos[melhor_idx]
            meta = metadados[melhor_idx]
            
            return f"📖 *Fonte: {meta['livro']} ({meta['capitulo']})*\n\n{resposta_bruta}"
        except Exception:
            return "🤖 Tive um problema ao processar a busca matemática no texto, mas minha base está carregada!"