# 📚 LittleLeiturasbot - Assistente Literário Inteligente

O **LittleLeiturasbot** é um chatbot híbrido avançado para o Telegram, desenvolvido como projeto prático para a disciplina de **Processamento de Linguagem Natural (NLP)** na **Fatec**. 

O objetivo do sistema é atuar como um companheiro de leitura definitivo. Ele gerencia o tempo de leitura do usuário, gera métricas estatísticas de desempenho, distribui medalhas por conquistas (gamificação) e utiliza algoritmos de NLP para responder a perguntas e tirar dúvidas sobre **qualquer livro** em tempo real, utilizando a Wikipédia como base de conhecimento dinâmica.

---

## 🚀 Funcionalidades Principais

### 🧠 1. Cérebro de NLP & Q&A Dinâmico
Diferente de chatbots tradicionais com respostas estáticas, o bot cria sua própria base de conhecimento sob demanda:
* **Busca Dinâmica (Web Scraping):** Ao informar o livro, o bot consome a API da Wikipédia em tempo real (suporte bilíngue: PT/EN).
* **Processamento de Texto:** Aplica técnicas de *Tokenização* e *Stemming* (redução ao radical via algoritmo Porter Stemmer) para normalizar as entradas.
* **Vetorização TF-IDF:** Transforma o texto em matrizes numéricas ponderadas estatisticamente.
* **Similaridade de Cossenos:** Calcula matematicamente a frase mais relevante da base para responder à dúvida do usuário com base no contexto.

### ⏱️ 2. Monitoramento e Métricas de Leitura
Ferramenta completa de gerenciamento de tempo para leitores:
* **Cronômetro Ativo:** Comandos para iniciar (`/ler`) e pausar (`/parar`) sessões de leitura.
* **Cálculo de Ritmo:** Analisa a velocidade de leitura do usuário (minutos gastos por página).
* **Estimativa de Término:** Lógica matemática que projeta quantas horas faltam para o usuário concluir o livro baseado no ritmo atual e nas páginas restantes.

### 🏆 3. Gamificação (Sistema de Conquistas)
Para incentivar o hábito da leitura, o bot conta com um sistema de recompensas psicológicas:
* **Conquistas Gerais:** Medalhas por tempo de foco (ex: *Foco de Titã*) ou consistência de leitura.
* **Conquistas Lendárias (Por Livro):** Se o usuário terminar um livro mapeado pelo sistema, ganha uma conquista exclusiva do universo literário (ex: ao terminar *Mistborn*, desbloqueia a conquista `"🪙 Nascido das Brumas"`; ao terminar *Stormlight*, ganha `"🛡️ Cavaleiro Radiante"`).
* **Mecanismo de Fallback:** Caso o livro lido não possua uma conquista exclusiva, o bot gera uma conquista automática baseada no volume de páginas lidas (ex: *Historiador Lendário* para calhamaços).

### 🎨 4. Conversational UX (Experiência do Usuário)
* **Interface Conversacional (GUI):** Implementado diretamente no ecossistema do Telegram, substituindo interfaces gráficas desktop obsoletas.
* **Menu Fixo de Comandos:** Navegação intuitiva através do botão nativo de Menu do Telegram.
* **Teclados Inline:** Uso de botões dinâmicos para evitar digitação excessive e mitigar erros do usuário.
* **Hierarquia Visual:** Relatórios de leitura elegantes formatados em Markdown, incluindo **barra de progresso textual** (`[████░░░░░░]`).

---

## 📦 Tecnologias & Stack Técnica

O ecossistema do projeto foi construído utilizando o ecossistema robusto do **Python 3.x** e as principais bibliotecas de Ciência de Dados e Processamento de Linguagem Natural (NLP) do mercado:

| Tecnologia / Lib | Badge | Função no Projeto |
| :--- | :---: | :--- |
| **Python 3.x** | ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) | Linguagem base de todo o ecossistema do assistente. |
| **python-telegram-bot** | ![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white) | Conexão, roteamento de comandos e interface conversacional. |
| **scikit-learn** | ![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white) | Criação de vetores numéricos via **TF-IDF** e **Similaridade de Cossenos**. |
| **NLTK** | ![NLTK](https://img.shields.io/badge/NLTK-Green?style=for-the-badge&logo=python&logoColor=white) | Processamento de NLP: *Tokenização* de sentenças e aplicação do *Stemmer*. |
| **Wikipedia-API** | ![Wikipedia](https://img.shields.io/badge/Wikipedia-%23000000.svg?style=for-the-badge&logo=wikipedia&logoColor=white) | Mecanismo de *Web Scraping* dinâmico para extração de dados dos livros. |
| **python-dotenv** | ![Dotenv](https://img.shields.io/badge/.ENV-Black?style=for-the-badge) | Gerenciamento seguro de variáveis de ambiente e proteção do Token. |
| **TextBlob & LangDetect** | ![IA](https://img.shields.io/badge/AI--Sentiment-8A2BE2?style=for-the-badge) | Detecção de idioma e classificação do sentimento (Humor do usuário). |

## 🛠️ Arquitetura do Projeto

O projeto segue boas práticas de engenharia de software e os princípios do **SOLID**, sendo totalmente modularizado para facilitar a manutenção e escalabilidade:

```text
Chatbot_literario/
│
├── src/
│   ├── __init__.py        # Inicializador do módulo Python
│   ├── bot_telegram.py    # Interface conversacional e handlers do Telegram
│   ├── nlp_engine.py      # Mecanismo de Scraping, TF-IDF e Similaridade de Cossenos
│   ├── sentiment.py       # Análise de sentimento e adequação ao humor do cliente
│   └── tracker.py         # Regras de negócio, cálculos de ritmo e gamificação
│
├── .env                   # Chaves e Tokens protegidos (Variáveis de Ambiente)
├── .gitignore             # Filtro para não expor a venv e chaves no GitHub
├── main.py                # Ponto de entrada (Bootstrapper da aplicação)
└── requirements.txt       # Gerenciador de dependências do projeto
