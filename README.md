# 🤖 ManualBot — Assistente RAG para Manuais Técnicos

**ManualBot** é um sistema completo de perguntas e respostas RAG (Retrieval-Augmented Generation) focado na análise de documentações técnicas oficiais, permitindo que usuários façam perguntas em linguagem natural e recebam respostas precisas com citação direta de documento e página.

Este projeto foi desenvolvido como entrega para a disciplina de **Técnicas Especiais em Computação**.

---

## 🚀 Como Executar o Projeto

Preparamos scripts automatizados para facilitar a avaliação e o uso do sistema, sem a necessidade de abrir múltiplos terminais manualmente.

### Opção 1: Inicialização Completa (Recomendado)
Se você for o desenvolvedor ou tiver o seu token do Ngrok configurado localmente:
1. Abra a pasta do projeto no Windows.
2. Dê um duplo clique no arquivo **`iniciar_manualbot.bat`**.
3. O sistema abrirá automaticamente:
   - A API backend (FastAPI/Uvicorn)
   - A Interface Gráfica (Streamlit) no navegador
   - O túnel Ngrok para expor a API para o n8n/Telegram

### Opção 2: Modo Visitante / Professor
Se você está avaliando o trabalho em outra máquina:
1. Edite o arquivo **`iniciar_manualbot_visitante.bat`**.
2. Substitua o texto `COLE_SEU_TOKEN_AQUI_E_APAGUE_ESTE_TEXTO` pelo seu authtoken do Ngrok.
3. Salve e execute o arquivo com duplo clique. 
*(Isso garantirá que o webhook do Telegram/n8n funcione perfeitamente sem configurações extras).*

---

## 📅 Cronograma de Entregas e Evolução do Projeto

O projeto foi construído e validado em 4 semanas, cumprindo integralmente (e excedendo) os requisitos do edital da disciplina.

### Semana 1: Estruturação e Domínio
- [x] **Escolher os manuais:** Seleção de documentações técnicas complexas.
- [x] **Preparar os PDFs:** Organização na pasta `docs/PDFs-Instrucoes`.
- [x] **Estudar o domínio:** Análise da densidade do material para garantir que um RAG seria aplicável.
- [x] **Definir a arquitetura:** Modelagem do fluxo (Ingestão -> Embedding -> Vector Store -> LLM -> Interface/n8n).

### Semana 2: Ingestão e Vetorização
- [x] **Implementar Chunking:** Processamento automático dos PDFs usando `RecursiveCharacterTextSplitter` (tamanho: 900, overlap: 150).
- [x] **Gerar Embeddings:** Adoção inicial e evolução para o modelo poliglota `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` rodando 100% local (CPU), garantindo o cruzamento de perguntas em português com PDFs em inglês.
- [x] **Construir o Banco Vetorial:** Persistência dos vetores e metadados (documento/página) utilizando **ChromaDB** e SQLite.
- [x] **Validar a busca semântica:** Scripts e aba de inspeção na interface gráfica criados para exibir chunks e vetores puros de 384 dimensões.

### Semana 3: Integração e Automação
- [x] **Integrar o RAG ao LLM:** Conexão estabelecida com o Google Gemini 3.6 Flash via LangChain.
- [x] **Desenvolver os prompts:** Criação da Regra de Restrição Absoluta (RF11), garantindo que o bot recuse educadamente responder caso a informação não esteja no PDF, eliminando alucinações.
- [x] **Implementar o workflow no n8n:** Criação de um bot no **Telegram** integrado via Webhooks, com o Ngrok expondo nossa API local (FastAPI).
- [x] **Validar as respostas:** Testes de estresse com saudações e perguntas fora de contexto para validar o comportamento da persona.

### Semana 4: Interface e Entrega Final
- [x] **Desenvolver a interface:** Substituição dos scripts básicos por uma interface gráfica rica e dinâmica em **Streamlit**, imitando um layout de chat moderno com identidade visual própria e seletor de Modelos de IA.
- [x] **Realizar testes finais:** Validação do fluxo de interface, tratamento de erros e exibição correta das fontes consultadas dentro de componentes colapsáveis (*expanders*).
- [x] **Documentação:** Criação deste README completo e organização dos arquivos.
- [x] **Apresentação & Gravação de Vídeo:** Concluídos.

---

## 🌟 Desafios Extras Implementados (Bônus)

Além da base exigida, implementamos **5 desafios extras** para enriquecer o sistema:

1. 🏆 **Atendimento via Telegram utilizando o n8n:** Fluxo totalmente automatizado conversando diretamente pelo celular do usuário.
2. 🏆 **Geração de respostas citando documento e página:** O LLM aponta de onde tirou cada informação na resposta gerada.
3. 🏆 **Destaque automático do trecho utilizado:** A interface (abaixo do chat) possui o botão expansível "Ver Documentação Consultada", exibindo os trechos matematicamente mais próximos.
4. 🏆 **Painel com métricas de recuperação:** Exibição clara do "Score de Distância Coseno", quantidade de chunks criados e peso do banco vetorial.
5. 🏆 **Arquitetura preparada para comparação de Modelos (LLM):** O front-end já possui seletor funcional para uso futuro do Llama 3 (Ollama Local) em contraste com o Gemini.

---

## 🛠️ Stack Tecnológica

- **Backend / Orquestração RAG:** Python 3, LangChain, FastAPI, Uvicorn
- **Extração de Dados:** PyMuPDF (`fitz`)
- **Embeddings:** HuggingFace (`sentence-transformers`)
- **Vector Database:** ChromaDB
- **LLM:** Google Gemini 3.6 Flash
- **Interface Visual:** Streamlit
- **Automação Externa:** n8n, Telegram Bot API, Ngrok

---

*Desenvolvido com excelência para a disciplina de Técnicas Especiais em Computação.* 🎓
