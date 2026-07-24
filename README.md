# ManualBot — ESP32

Sistema de perguntas e respostas (RAG) focado na documentação técnica oficial do **ESP32**, desenvolvido para a disciplina *Técnicas Especiais em Computação*.

## O que este repositório contém

O objetivo do ManualBot é permitir consultas em linguagem natural a manuais técnicos do ESP32, fornecendo respostas fundamentadas nos documentos originais, com citação de fonte, página e trecho.

Status atual: pipeline de RAG (recuperação) funcional de ponta a ponta — extração, chunking, embeddings, banco vetorial e busca semântica já implementados e testados. A geração de resposta por LLM ainda está em desenvolvimento (próxima etapa).

Atualmente, o projeto inclui:

- extração e inspeção de PDFs com PyMuPDF, incluindo detecção de páginas escaneadas, esquemáticas ou com tabelas `src/ingestion/pdf_extract.py`
- chunking dos documentos com RecursiveCharacterTextSplitter `src/ingestion/chunker.py`
- geração de embeddings locais com sentence-transformers/all-MiniLM-L6-v2 `src/embeddings/embedding_factory.py`
- banco vetorial persistente com ChromaDB `src/retrieval/vector_store.py`
- pipeline orquestrado que conecta ingestão → embeddings → banco → busca `src/pipeline/rag_pipeline.py`
- interface em Streamlit conectada ao pipeline real, com busca semântica ao vivo e inspeção visual do banco vetorial `src/app/app.py`
- scripts standalone para rodar ingestão e validar busca via linha de comando `ingestao.py, validacao_busca.py`
- notebook com os experimentos completos da Semana 2 `notebooks/semana_2_ingestao_e_busca.ipynb`

> Observação: a busca semântica retorna os trechos mais relevantes dos manuais, mas ainda não há um LLM gerando a resposta final em linguagem natural a partir desses trechos, essa integração está planejada para a próxima etapa do projeto.

## Estrutura do projeto

```
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
│   │   └── app.py             # interface Streamlit conectada ao pipeline RAG
│   ├── embeddings/
│   │   └── embedding_factory.py   # carregamento do modelo de embeddings
│   ├── ingestion/
│   │   ├── pdf_extract.py     # extração e diagnóstico de PDFs
│   │   └── chunker.py         # divisão dos documentos em chunks
│   ├── pipeline/
│   │   └── rag_pipeline.py    # orquestração: ingestão + busca
│   └── retrieval/
│       └── vector_store.py    # criação, carga e consulta do ChromaDB
├── ingestao.py             # script CLI: roda o pipeline completo de ingestão
├── validacao_busca.py      # script CLI: testa a busca semântica com perguntas fixas
├── tests/                  # testes automatizados (a implementar)
└── README.md
```

## Como executar

### Clonar o repositório

```bash
git clone https://github.com/FranciscoKoder/ManualBot.git
cd ManualBot
```

### Configuração inicial (ambiente virtual)

Em versões recentes do Linux (Ubuntu 23.04+, Debian 12+), o `pip` bloqueia instalações globais de pacotes para evitar conflitos com o sistema. A solução é usar um **Ambiente Virtual (Virtual Environment)**.

**1. Instale o `venv` (se necessário):**

```bash
sudo apt update
sudo apt install python3-venv
```

**2. Crie o ambiente virtual:**

Na raiz do projeto (`~/Documentos/Github Repositorios/ManualBot`), execute:

```bash
python3 -m venv .venv
```

**3. Ative o ambiente virtual:**

```bash
source .venv/bin/activate
```

Você verá `(.venv)` no início da linha do terminal, indicando que o ambiente está ativo.

> **Dica importante:** Sempre que fechar o terminal e retornar ao projeto, lembre-se de rodar `source .venv/bin/activate` antes de trabalhar no código.

### Instalação e execução

1. Com o ambiente virtual ativado, instale as dependências:

```bash
pip install streamlit pymupdf langchain langchain-community langchain-text-splitters langchain-huggingface langchain-chroma sentence-transformers
```

2. Rodar a ingestão (chunking + embeddings + banco vetorial)

Isso processa todos os PDFs e constrói o banco vetorial local em data/chroma_db/:

```bash
python ingestao.py
```

Esse passo pode demorar alguns minutos, especialmente na primeira execução (baixa o modelo de embeddings).

3. Inicie a interface Streamlit:

```bash
cd src/app
streamlit run app.py
```

Abre automaticamente em http://localhost:8501. Use o menu lateral para navegar:

Início — visão geral do status do pipeline (nº de PDFs, configuração de chunking, modelo de embeddings, tamanho do banco)
Documentos & Ingestão — lista os PDFs disponíveis, permite rodar a ingestão pela própria interface e inspecionar cada PDF individualmente
Inspeção do Banco Vetorial — mostra os chunks indexados no ChromaDB, incluindo o texto original e o vetor de embedding de 384 dimensões
Consultar Manual (Busca Semântica) — campo de pergunta com busca semântica real no banco vetorial, retornando os trechos mais relevantes com documento, página e trecho de origem

## Componentes principais

- `src/app/app.py`
  - interface de usuário Streamlit, conectada ao pipeline RAG real
  - telas de Início, Documentos & Ingestão, Inspeção do Banco Vetorial e Consultar Manual
  - executa ingestão e busca semântica ao vivo, sem dados simulados
  - inspeção visual dos chunks indexados e de seus vetores de embedding (384 dimensões)

- `src/ingestion/pdf_extract.py`
  - extrai texto e metadados de PDFs com PyMuPDF
  - gera análises de páginas, detecção de páginas com possível OCR/diagramas e amostras de texto
  - salva resultados JSON em `data/raw/`
 
- `src/ingestion/chunker.py`
  - carrega todos os PDFs de `docs/PDFs-Instrucoes/` com `PyPDFDirectoryLoader`
  - divide o texto em chunks de 800 caracteres com overlap de 100, via `RecursiveCharacterTextSplitter`

- `src/embeddings/embedding_factory.py`
  - carrega o modelo de embeddings `sentence-transformers/all-MiniLM-L6-v2`
  - roda localmente em CPU, com padrão singleton para evitar recarregar o modelo a cada chamada
 
 - `src/retrieval/vector_store.py`
  - cria e persiste o banco vetorial ChromaDB em `data/chroma_db/`
  - carrega o banco existente e executa buscas por similaridade semântica
  - mantém metadados de documento e página junto de cada chunk

- `src/pipeline/rag_pipeline.py`
  - classe `RAGPipeline` que orquestra o fluxo completo: ingestão (chunking + embeddings + banco) e consulta (busca semântica formatada)
  - ponto único de entrada usado tanto pela interface Streamlit quanto pelos scripts CLI
 
- `ingestao.py`
  - script de linha de comando que roda o pipeline completo de ingestão sem abrir a interface
  - útil para (re)construir o banco vetorial do zero

- `validacao_busca.py`
  - script de linha de comando que carrega o banco vetorial já existente
  - testa um conjunto de perguntas fixas sobre o ESP32 e imprime os trechos mais relevantes com fonte, página e distância

## Tecnologias usadas

- Python 3.x
- Streamlit
- PyMuPDF
- LangChain (langchain-community, langchain-text-splitters, langchain-huggingface, langchain-chroma) — chunking e integração com o banco vetorial
- sentence-transformers (all-MiniLM-L6-v2) — geração de embeddings, rodando localmente em CPU
- ChromaDB — banco vetorial persistente

## Próximos passos

- Integrar um LLM para gerar respostas em linguagem natural a partir dos trechos recuperados (RF08/RF09)
- Processar as fontes "rolling" (ESP-IDF Programming Guide, Arduino-ESP32 Core)
- Diferenciar a estratégia de chunking para documentos ricos em tabelas (datasheets)
- Criar requirements.txt com versões fixadas das dependências
- Implementar testes automatizados em tests/
- Adicionar upload de novos PDFs diretamente pela interface

## Nota sobre o domínio

Domínio: ESP32 (Espressif Systems). A justificativa técnica completa e os detalhes de arquitetura estão na pasta docs/Documento_do_Projeto/.
