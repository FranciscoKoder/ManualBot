# ManualBot — ESP32

Sistema de perguntas e respostas (RAG) focado na documentação técnica oficial do **ESP32**, desenvolvido para a disciplina *Técnicas Especiais em Computação*.

## O que este repositório contém

O objetivo do ManualBot é permitir consultas em linguagem natural a manuais técnicos do ESP32, fornecendo respostas fundamentadas nos documentos originais.

Atualmente, o projeto inclui:

- protótipo de interface com **Streamlit** em `src/app/app.py`
- extração e inspeção de PDFs com **PyMuPDF** em `src/ingestion/pdf_extract.py`
- demo de leitura real de documentos na pasta `docs/PDFs-Instrucoes/`
- base de dados de documentos e notebooks para experimentos

> Observação: o pipeline RAG completo ainda está em desenvolvimento. A interface atual mostra respostas mock e uma prova de leitura real de PDFs.

## Estrutura do projeto

```
ManualBot/
├── data/                  # dados gerados e resultados da ingestão
│   └── raw/               # JSONs de análise extraída de PDFs
├── docs/                  # documentação do projeto e PDFs de referência
│   └── PDFs-Instrucoes/   # PDFs usados pelo protótipo de leitura
├── notebooks/             # experimentos e análises exploratórias
├── src/
│   ├── app/               # interface Streamlit do ManualBot
│   │   └── app.py
│   ├── embeddings/        # lugar reservado para geração de embeddings
│   ├── ingestion/         # extração e análise de PDFs
│   │   └── pdf_extract.py
│   ├── pipeline/          # orquestração do fluxo RAG (planejado)
│   └── retrieval/         # busca semântica e recuperação de trechos (planejado)
├── tests/                 # testes do projeto
└── README.md
```

## Como executar

1. Instale as dependências básicas:

```powershell
python -m pip install streamlit pymupdf
```

2. Inicie a interface Streamlit:

```powershell
cd src/app
streamlit run app.py
```

3. Use o menu lateral para navegar entre as telas:

- **Início**: overview do protótipo
- **Documentos**: seleção de PDFs e prova de leitura real
- **Consultar Manual**: formulário de pergunta (resposta atualmente simulada)

## Componentes principais

- `src/app/app.py`
  - interface de usuário Streamlit
  - seleção de documentos
  - prova de leitura real de PDFs a partir de `docs/PDFs-Instrucoes/`
  - mock de resposta RAG para demonstração de fluxo

- `src/ingestion/pdf_extract.py`
  - extrai texto e metadados de PDFs com PyMuPDF
  - gera análises de páginas, detecção de páginas com possível OCR/diagramas e amostras de texto
  - salva resultados JSON em `data/raw/`

## Tecnologias usadas

- Python 3.x
- Streamlit
- PyMuPDF

## Próximos passos

- integrar um modelo de embeddings e vetorstore
- implementar a busca semântica em `src/retrieval/`
- construir o pipeline RAG em `src/pipeline/`
- adicionar controle de upload e ingestão de PDFs na interface
- criar testes automatizados para ingestão e interface

## Nota sobre o domínio

Domínio: **ESP32** (Espressif Systems).
A justificativa técnica e os detalhes do projeto estão na pasta `docs/Documento_do_Projeto/`.
