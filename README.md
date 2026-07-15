# ManualBot — ESP32

Sistema de perguntas e respostas (RAG) sobre a documentação técnica oficial do **ESP32**, desenvolvido para a disciplina *Técnicas Especiais em Computação*.

## Sobre o projeto

O ManualBot permite que o usuário faça perguntas em linguagem natural sobre o ESP32 (GPIO, periféricos, modos de energia, etc.) e receba respostas fundamentadas diretamente na documentação oficial da Espressif, com indicação do documento, página e trecho utilizados.

## Domínio escolhido

**ESP32** (Espressif Systems) — justificativa detalhada em `docs/entrega_semana1.docx`.

## Estrutura de pastas

```
manualbot-esp32/
├── data/
│   ├── raw/              # PDFs originais baixados (não versionar binários grandes)
│   └── manifest.json     # nome, versão, data de acesso de cada documento
├── src/
│   ├── ingestion/         # extração de texto e chunking (PyMuPDF)
│   ├── embeddings/        # geração de embeddings (Sentence Transformers)
│   ├── retrieval/         # busca semântica no ChromaDB
│   └── pipeline/          # orquestração RAG (LangChain)
├── app/
│   └── streamlit_app.py   # interface do usuário
├── notebooks/              # exploração e testes pontuais
├── docs/                   # entregas e documentação do projeto
├── tests/
├── requirements.txt
└── README.md
```

## Equipe

| Integrante | Responsabilidade (Semana 1) |
|---|---|
| Vitor | Escolha do domínio e manuais |
| Nidlan | Preparação dos PDFs |
| Rafael | Estudo do domínio e questões de teste |
| Thales | Definição da arquitetura |

## Tecnologias (Semana 1)

Python, Streamlit, PyMuPDF, Sentence Transformers, LangChain, ChromaDB, n8n. Ver análise crítica em `docs/entrega_semana1.docx`, seção 5.

## Status

🚧 Semana 1 — domínio definido, arquitetura detalhada, protótipo de interface (mock).
