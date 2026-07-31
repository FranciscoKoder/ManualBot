# ManualBot: Arquitetura do Sistema RAG (ESP32)

## Visão Geral das Camadas (Os Blocos de Construção)
O sistema foi dividido em quatro camadas principais, garantindo que o código fique organizado e modular (um excelente ponto de Engenharia de Software para destacar na defesa do trabalho):

* **Camada de Apresentação (Frontend):** É a "vitrine" do sistema, construída com Streamlit. A responsabilidade exclusiva desta camada é interagir com o usuário: receber o texto da pergunta, exibir a resposta final e fornecer o menu lateral para selecionar qual LLM será usado. Ela não processa a inteligência do RAG.
* **Camada de Orquestração e Backend:** É o "cérebro" ou o "maestro" do projeto. Aqui roda o seu script Python principal (utilizando o framework LangChain). A responsabilidade deste bloco é coordenar todo o tráfego: ele decide quando converter texto em vetor, quando buscar no banco e para qual IA enviar o prompt final (Model Switcher).
* **Camada de Dados e Embeddings (Vetorial):** É a biblioteca de conhecimento especializada no domínio ESP32. É composta pelo modelo Sentence Transformers (que funciona como um tradutor, transformando palavras em números/vetores) e pelo ChromaDB (um banco de dados persistente que armazena essas matrizes numéricas e as cruza rapidamente por similaridade).
* **Camada de Geração e Modelos (IA):** São os "motores de raciocínio". Em vez de ter apenas um, o projeto tem um roteamento duplo. Pode usar o Google Gemini Pro (conectando via internet por requisição HTTP/REST) ou o Llama 3 (rodando isolado na sua própria máquina através do Ollama).

## O Fluxo de Comunicação (O Caminho do Dado)
A comunicação acontece em dois grandes momentos independentes: a preparação do sistema (Offline) e a consulta do usuário (Online).

### Fase 1: Fluxo de Ingestão (A Preparação)
Antes de o usuário fazer qualquer pergunta, o sistema precisa ler os manuais do ESP32.

* **Passos 3a e 3b:** Os arquivos em PDF originais passam pelo script Python, que extrai o texto bruto e o recorta em blocos menores de palavras (Chunks).
* **Passos 4 e 5:** Cada um desses blocos de texto é enviado ao Modelo de Embedding para ser transformado em um vetor (uma coordenada matemática). Esses vetores, junto com a indicação da página e do documento de origem, são salvos de forma definitiva no ChromaDB.

### Fase 2: Fluxo RAG de Consulta (Tempo Real)
É aqui que a mágica acontece durante a sua demonstração.

* **Passo 1 e 2:** O usuário digita uma dúvida sobre o ESP32 e seleciona a IA no Streamlit. O Streamlit envia esses parâmetros para a Camada de Orquestração (Backend).
* **Passo 6:** O Backend precisa entender a pergunta matematicamente. Ele envia a dúvida de texto para o Modelo de Embedding, que devolve um vetor correspondente àquela exata pergunta.
* **Passos 7 e 8 (A Busca Semântica):** O Backend pega esse vetor da pergunta e bate na porta do ChromaDB. O banco de dados calcula a distância matemática (Similaridade L2) entre a pergunta e todos os parágrafos do manual salvos anteriormente. Ele devolve para o Backend apenas os 3 ou 5 parágrafos mais relevantes.
* **Passo 9a ou 9b (O Roteamento):** O Backend monta um pacote final chamado "Prompt". Esse pacote contém a pergunta original do usuário + os trechos do manual recuperados do banco. Dependendo do que foi escolhido na interface, esse pacote viaja pela internet até a API do Gemini (9a) ou bate na porta local 11434 do seu Llama 3 (9b).
* **Passo 10a ou 10b:** A Inteligência Artificial lê o pacote, formula a resposta baseada exclusivamente naqueles trechos fornecidos e devolve o texto limpo para o Backend.
* **Passo 11:** O Backend passa essa resposta final de volta para o Streamlit, que renderiza na tela de forma amigável, listando a fonte e a página exata de onde a informação saiu.
