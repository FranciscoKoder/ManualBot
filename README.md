# ManualBot — ESP32

Sistema de perguntas e respostas (RAG) focado na documentação técnica oficial do **ESP32**, desenvolvido para a disciplina *Técnicas Especiais em Computação*.

## O que este repositório contém

O objetivo do ManualBot é permitir consultas em linguagem natural a manuais técnicos do ESP32, fornecendo respostas fundamentadas nos documentos originais, com citação de fonte, página e trecho.

Status atual: **pipeline de RAG completo e orquestrado de ponta a ponta** — extração, chunking, embeddings, banco vetorial, busca semântica, geração de resposta com LLM e orquestração de fluxo já implementados e validados. O sistema responde perguntas em linguagem natural com base exclusivamente na documentação oficial do ESP32, sempre citando a fonte.

Atualmente, o projeto inclui:

- orquestração visual no n8n validada e integrada, consumindo a API local (`POST /perguntar`) para processar a entrada do usuário e estruturar a saída do LLM
- extração e inspeção de PDFs com PyMuPDF, incluindo detecção de páginas escaneadas, esquemáticas ou com tabelas `src/ingestion/pdf_extract.py`
- chunking dos documentos com RecursiveCharacterTextSplitter `src/ingestion/chunker.py`
- geração de embeddings locais com sentence-transformers/all-MiniLM-L6-v2 `src/embeddings/embedding_factory.py`
- banco vetorial persistente com ChromaDB `src/retrieval/vector_store.py`
- geração de resposta com LLM (Google Gemini 3.6 Flash) a partir dos trechos recuperados, com prompt estruturado que exige fidelidade estrita à documentação `src/llm/gemini.py`, `src/llm/prompts.py`
- pipeline que conecta ingestão → embeddings → banco → busca → geração de resposta `src/pipeline/rag_pipeline.py`
- interface em Streamlit conectada ao pipeline real, exibindo a resposta gerada e as fontes consultadas `src/app/app.py`
- API REST (FastAPI) que expõe o pipeline para consumo externo, usada pela automação no n8n `api.py`
- scripts standalone para rodar ingestão e validar busca via linha de comando `ingestao.py`, `validacao_busca.py`
- notebook com os experimentos completos da Semana 2 `notebooks/semana_2_ingestao_e_busca.ipynb`

## Estrutura do projeto

```text
ManualBot/
├── data/
│   ├── raw/                # JSONs de análise extraída de cada PDF
│   └── chroma_db/          # banco vetorial ChromaDB (gerado localmente, fora do Git)
├── docs/
│   ├── Documento_do_Projeto/  # documento de arquitetura e justificativa do domínio
│   └── PDFs-Instrucoes/       # PDFs oficiais do ESP32 usados na base documental
├── notebooks/
│   ├── gerar_notebook.py
│   └── semana_2_ingestao_e_busca.ipynb
├── src/
│   ├── app/
│   │   └── app.py             # interface Streamlit conectada ao pipeline RAG completo
│   ├── embeddings/
│   │   └── embedding_factory.py   # carregamento do modelo de embeddings
│   ├── ingestion/
│   │   ├── pdf_extract.py     # extração e diagnóstico de PDFs
│   │   └── chunker.py         # divisão dos documentos em chunks
│   ├── llm/
│   │   ├── gemini.py          # configuração do modelo Gemini 3.6 Flash
│   │   └── prompts.py         # prompt estruturado do RAG
│   ├── pipeline/
│   │   └── rag_pipeline.py    # orquestração: ingestão + busca + geração de resposta
│   └── retrieval/
│       └── vector_store.py    # criação, carga e consulta do ChromaDB
├── api.py                  # API REST (FastAPI) que expõe o pipeline para o n8n
├── ingestao.py              # script CLI: roda o pipeline completo de ingestão
├── validacao_busca.py       # script CLI: testa a busca semântica com perguntas fixas
├── requirements.txt         # dependências do projeto
├── .env                     # chave de API do Gemini (não versionado)
├── tests/                   # testes automatizados (a implementar)
└── README.md
```

## Como executar

### Clonar o repositório

```bash
git clone https://github.com/FranciscoKoder/ManualBot.git
cd ManualBot
```

### Configuração inicial (ambiente virtual)

Em versões recentes do Linux (Ubuntu 23.04+, Debian 12+), o `pip` bloqueia instalações globais de pacotes para evitar conflitos com o sistema. A solução é usar um **ambiente virtual**.

**1. Instale o `venv` (se necessário, Linux):**

```bash
sudo apt update
sudo apt install python3-venv
```

**2. Crie o ambiente virtual** (na raiz do projeto):

```bash
python -m venv .venv
```

**3. Ative o ambiente virtual:**

```bash
# Linux / Mac
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Você verá `(.venv)` no início da linha do terminal, indicando que o ambiente está ativo.

> **Dica:** sempre ative o ambiente virtual antes de instalar dependências ou rodar qualquer comando do projeto.

### Instalação e execução

**1. Com o ambiente virtual ativado, instale as dependências:**

```bash
pip install -r requirements.txt
```

**2. Configure a chave de API do Gemini:**

Crie um arquivo `.env` na raiz do projeto com o conteúdo:

```
GOOGLE_API_KEY=sua_chave_aqui
```

A chave pode ser gerada em [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

**3. Adicione os PDFs da base documental** em `docs/PDFs-Instrucoes/` (não incluídos no repositório por tamanho — ver seção de fontes abaixo).

**4. Rode a ingestão** (chunking + embeddings + banco vetorial):

```bash
python ingestao.py
```

Esse passo pode demorar alguns minutos, especialmente na primeira execução (baixa o modelo de embeddings). Sempre que os PDFs da base ou a configuração de chunking mudarem, rode a ingestão novamente para reconstruir o banco vetorial.

**5. Inicie a interface Streamlit:**

```bash
cd src/app
streamlit run app.py
```

Abre automaticamente em `http://localhost:8501`. Use o menu lateral para navegar:

- **Início** — visão geral do status do pipeline (nº de PDFs, configuração de chunking, modelo de embeddings, modelo de LLM, tamanho do banco)
- **Documentos & Ingestão** — lista os PDFs disponíveis, permite rodar a ingestão pela própria interface e inspecionar cada PDF individualmente
- **Inspeção do Banco Vetorial** — mostra os chunks indexados no ChromaDB, incluindo o texto original e o vetor de embedding de 384 dimensões
- **Consultar Manual** — campo de pergunta com busca semântica e geração de resposta em tempo real, exibindo a resposta gerada pelo Gemini em destaque, seguida das fontes (documento, página e trecho) que a fundamentaram

**6. (Opcional) Inicie a API para testes ou integração com o n8n:**

Em um terminal separado (com o ambiente virtual ativado), na raiz do projeto:

```bash
uvicorn api:app --reload --port 8000
```

Acesse `http://localhost:8000/docs` para testar o endpoint `POST /perguntar` diretamente pelo navegador, sem precisar do n8n.

## Componentes principais

- `src/app/app.py`
  - interface de usuário Streamlit, conectada ao pipeline RAG completo
  - telas de Início, Documentos & Ingestão, Inspeção do Banco Vetorial e Consultar Manual
  - executa ingestão, busca semântica e geração de resposta ao vivo, sem dados simulados
  - exibe a resposta gerada pelo LLM em destaque, seguida das fontes que a fundamentaram

- `src/ingestion/pdf_extract.py`
  - extrai texto e metadados de PDFs com PyMuPDF
  - gera análises de páginas, detecção de páginas com possível OCR/diagramas e amostras de texto
  - salva resultados JSON em `data/raw/`

- `src/ingestion/chunker.py`
  - carrega todos os PDFs de `docs/PDFs-Instrucoes/` com `PyPDFDirectoryLoader`
  - divide o texto em chunks de 900 caracteres com overlap de 150, via `RecursiveCharacterTextSplitter`

- `src/embeddings/embedding_factory.py`
  - carrega o modelo de embeddings `sentence-transformers/all-MiniLM-L6-v2`
  - roda localmente em CPU, com padrão singleton para evitar recarregar o modelo a cada chamada

- `src/retrieval/vector_store.py`
  - cria e persiste o banco vetorial ChromaDB em `data/chroma_db/`
  - carrega o banco existente e executa buscas por similaridade semântica
  - mantém metadados de documento e página junto de cada chunk

- `src/llm/gemini.py`
  - configura o modelo **Gemini 3.6 Flash** via LangChain (`ChatGoogleGenerativeAI`)
  - lê a chave de API da variável de ambiente `GOOGLE_API_KEY`, carregada a partir do arquivo `.env`

- `src/llm/prompts.py`
  - define o prompt estruturado do RAG: exige respostas baseadas exclusivamente no contexto fornecido, resposta sempre em português e recusa explícita quando a informação não está nos manuais

- `src/pipeline/rag_pipeline.py`
  - classe `RAGPipeline` que orquestra o fluxo completo: ingestão (chunking + embeddings + banco), busca semântica (`consultar`) e geração de resposta com LLM (`responder`)
  - ponto único de entrada usado pela interface Streamlit, pela API e pelos scripts CLI

- `api.py`
  - API REST construída com **FastAPI**, expõe o pipeline via `POST /perguntar`
  - recebe uma pergunta em JSON e devolve a resposta gerada junto das fontes utilizadas
  - ponto de integração usado pela automação no **n8n**
  - documentação interativa disponível em `/docs` (Swagger UI)

- `ingestao.py`
  - script de linha de comando que roda o pipeline completo de ingestão sem abrir a interface
  - útil para (re)construir o banco vetorial do zero

- `validacao_busca.py`
  - script de linha de comando que carrega o banco vetorial já existente
  - testa um conjunto de perguntas fixas sobre o ESP32 e imprime os trechos mais relevantes com fonte, página e distância

## Base documental

Domínio: **ESP32** (Espressif Systems). Documentos utilizados:

| Documento | Tipo | Status |
|---|---|---|
| ESP32 Technical Reference Manual | PDF fixo | ✅ processado |
| ESP32 Series Datasheet | PDF fixo | ✅ processado |
| ESP32-WROOM-32 Datasheet (NRND) | PDF fixo | ✅ processado |
| ESP32 Hardware Design Guidelines | PDF fixo | ✅ processado |
| ESP32 SoC Errata | PDF fixo | ✅ processado |
| ESP-IDF Programming Guide | Web / rolling-release | ⏳ pendente |
| Arduino-ESP32 Core (documentação) | Web / rolling-release | ⏳ pendente |

A justificativa técnica completa da escolha do domínio está em `docs/Documento_do_Projeto/`.

## Tecnologias usadas

- **Python 3.x**
- **Streamlit** — interface do usuário
- **PyMuPDF (fitz)** — extração de texto de PDFs
- **LangChain** (`langchain-community`, `langchain-text-splitters`, `langchain-huggingface`, `langchain-chroma`, `langchain-google-genai`) — chunking, integração com o banco vetorial e com o LLM
- **sentence-transformers** (`all-MiniLM-L6-v2`) — geração de embeddings, rodando localmente em CPU
- **ChromaDB** — banco vetorial persistente
- **Google Gemini 3.6 Flash** — geração da resposta final em linguagem natural
- **FastAPI + Uvicorn** — API REST para integração externa (n8n)
- **n8n** — automação/orquestração visual do fluxo (em desenvolvimento)

## Próximos passos

- [ ] Concluir o workflow no n8n, consumindo a API `POST /perguntar`
- [ ] Processar as fontes "rolling" (ESP-IDF Programming Guide, Arduino-ESP32 Core)
- [ ] Diferenciar a estratégia de chunking para documentos ricos em tabelas (datasheets)
- [ ] Validar a qualidade das respostas com um conjunto maior de perguntas de teste
- [ ] Implementar testes automatizados em `tests/`
- [ ] Adicionar upload de novos PDFs diretamente pela interface

## Nota sobre o domínio

Domínio: **ESP32** (Espressif Systems). A justificativa técnica completa e os detalhes de arquitetura estão na pasta `docs/Documento_do_Projeto/`.
