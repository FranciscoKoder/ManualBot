import site
import sys
import time
from pathlib import Path
import streamlit as st

user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

SRC_PATH = Path(__file__).resolve().parents[1]
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ingestion.pdf_extract import (
    extrair_frase_de,
    extrair_frase_aleatoria,
    extract_pdf,
    listar_pdfs,
)
from pipeline.rag_pipeline import RAGPipeline

st.set_page_config(page_title="ManualBot - ESP32", layout="wide")

# Identidade visual: paleta ManualBot + tipografia
# Título/headers: Barlow Condensed (peso 900 / Black)
# Corpo de texto: Plus Jakarta Sans (regular)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;900&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

    :root {
        --mb-primary: #0066CC;
        --mb-bg: #FFFFFF;
        --mb-bg-secondary: #F4F6F9;
        --mb-text: #111827;
        --mb-border: #E2E8F0;
        --mb-hover-bg: #E6F0FA;
    }

    /* Fundo da aplicação */
    .stApp {
        background-color: var(--mb-bg) !important;
        color: var(--mb-text) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--mb-bg-secondary) !important;
        border-right: 1px solid var(--mb-border) !important;
    }

    /* Título "ManualBot" na sidebar em azul, cor da marca */
    [data-testid="stSidebar"] h1 {
        color: var(--mb-primary) !important;
    }

    /* Títulos usam Barlow Condensed Black em todo o app */
    h1, h2, h3, h4 {
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 900 !important;
        letter-spacing: 0.01em;
        color: var(--mb-text) !important;
    }

    h1 { font-size: 2.6rem !important; line-height: 1.1 !important; }
    h2 { font-size: 1.9rem !important; }
    h3 { font-size: 1.4rem !important; }

    /* Texto corrido, labels, legendas — exclui explicitamente os ícones do Streamlit,
       que dependem de uma fonte própria (Material Symbols) para renderizar como glifo */
    .stMarkdown, p, span:not([data-testid="stIconMaterial"]), label,
    .stCaption, div[data-testid="stCaptionContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--mb-text) !important;
    }

    /* Garante que os ícones internos do Streamlit continuem usando a fonte de ícones,
       evitando que apareçam como texto cru (ex: "expand_more", "keyboard_double_arrow_left") */
    span[data-testid="stIconMaterial"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapsedControl"] span {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', sans-serif !important;
    }

    /* Espaço no topo do conteúdo principal: reduzido em relação ao padrão do Streamlit,
       mas mantido o suficiente para o título não ficar colado no topo da página */
    .block-container {
        padding-top: 4.5rem !important;
    }

    /* Métricas */
    div[data-testid="stMetricValue"] {
        color: var(--mb-primary) !important;
        font-family: 'Barlow Condensed', sans-serif !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Botões primários na cor da marca, com hover em azul mais escuro */
    .stButton > button[kind="primary"] {
        background-color: var(--mb-primary) !important;
        border: none !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        transition: background-color 0.15s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #004C99 !important;
    }

    /* Botões secundários com hover em azul claro (fundo + texto, sem alterar a borda) */
    .stButton > button {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        border-radius: 8px !important;
        transition: background-color 0.15s ease, color 0.15s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background-color: var(--mb-hover-bg) !important;
        color: var(--mb-primary) !important;
    }
    .stButton > button:not([kind="primary"]):hover p,
    .stButton > button:not([kind="primary"]):hover span {
        color: var(--mb-primary) !important;
    }

    /* Caixas de código, expanders e containers */
    div.stCodeBlock, div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--mb-border) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: var(--mb-hover-bg) !important;
    }
    div[data-testid="stExpander"] summary:hover p,
    div[data-testid="stExpander"] summary:hover span {
        color: var(--mb-primary) !important;
    }

    /* Abas, com hover em azul claro (fundo + texto) */
    button[data-baseweb="tab"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px 8px 0 0 !important;
    }
    button[data-baseweb="tab"]:hover {
        background-color: var(--mb-hover-bg) !important;
    }
    button[data-baseweb="tab"]:hover p {
        color: var(--mb-primary) !important;
    }

    /* Caixas de seleção (selectbox) — inclui os "cards" com nome de PDF e a
       lista de perguntas sugeridas: hover em azul claro, com borda e texto azuis */
    [data-baseweb="select"] > div {
        transition: border-color 0.15s ease, background-color 0.15s ease !important;
    }
    [data-baseweb="select"] > div:hover {
        border-color: var(--mb-primary) !important;
        background-color: var(--mb-hover-bg) !important;
    }
    [data-baseweb="select"] > div:hover * {
        color: var(--mb-primary) !important;
    }

    /* Itens de dropdown (selectbox / multiselect), com fundo e texto azuis no hover */
    li[role="option"]:hover,
    [data-baseweb="menu"] li:hover {
        background-color: var(--mb-hover-bg) !important;
    }
    li[role="option"]:hover *,
    [data-baseweb="menu"] li:hover * {
        color: var(--mb-primary) !important;
    }

    /* Botão de recolher/expandir a sidebar */
    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="baseButton-headerNoPadding"]:hover {
        background-color: var(--mb-hover-bg) !important;
        border-radius: 6px !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover span,
    [data-testid="stSidebarCollapsedControl"]:hover span {
        color: var(--mb-primary) !important;
    }

    /* Checkboxes e radios fora da sidebar (ex: dentro de formulários) */
    div[data-testid="stCheckbox"] label:hover,
    div[data-testid="stRadio"] label:hover {
        background-color: var(--mb-hover-bg) !important;
        border-radius: 6px !important;
    }
    div[data-testid="stCheckbox"] label:hover p,
    div[data-testid="stRadio"] label:hover p {
        color: var(--mb-primary) !important;
    }

    /* Cabeçalho de itens no popover (ex: vetor de embedding completo) */
    [data-baseweb="popover"] button:hover {
        background-color: var(--mb-hover-bg) !important;
        color: var(--mb-primary) !important;
    }

    /* Slider (thumb arrastável) com hover em azul claro */
    [data-testid="stSlider"] [role="slider"]:hover {
        box-shadow: 0 0 0 8px var(--mb-hover-bg) !important;
    }

    /* ---------------------------------------------------------
       Navegação lateral (radio): remove as bolinhas e transforma
       cada opção em um item de menu com hover/seleção em azul claro
       --------------------------------------------------------- */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 8px !important;
        padding: 0.5rem 0.75rem !important;
        width: 100% !important;
        margin-bottom: 2px !important;
        transition: background-color 0.15s ease !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: var(--mb-hover-bg) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover p {
        color: var(--mb-primary) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background-color: var(--mb-hover-bg) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
        color: var(--mb-primary) !important;
        font-weight: 600 !important;
    }
    /* Esconde visualmente apenas o componente de rádio (bolinha), usando o marcador
       específico do BaseWeb, sem depender de posição na árvore — isso evita esconder
       o texto do item por engano */
    [data-testid="stSidebar"] [data-testid="stRadio"] label [data-baseweb="radio"] {
        width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
        border: none !important;
    }

    /* Estilos Customizados para o Chat do ManualBot */
    [data-testid="stChatMessage"] {
        border-radius: 12px !important;
        border: 1px solid var(--mb-border) !important;
        background-color: var(--mb-bg) !important;
        padding: 1rem !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
    }
    
    /* Personaliza o estilo de blockquote (usado nos status/expanders) */
    blockquote {
        border-left-color: var(--mb-primary) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_resource
def get_pipeline():
    projeto_raiz = Path(__file__).resolve().parents[2]
    pipeline = RAGPipeline(projeto_raiz)
    pipeline.carregar_banco_existente()
    return pipeline

pipeline = get_pipeline()

def carregar_pdfs_reais() -> list[Path]:
    projeto_raiz = Path(__file__).resolve().parents[2]
    pasta_pdfs = projeto_raiz / "docs" / "PDFs-Instrucoes"
    return listar_pdfs(pasta_pdfs)

def obter_tamanho_banco(pasta_chroma: Path) -> float:
    """Calcula o tamanho total em Megabytes da pasta do ChromaDB."""
    if not pasta_chroma.exists():
        return 0.0
    total_bytes = sum(f.stat().st_size for f in pasta_chroma.glob("**/*") if f.is_file())
    return total_bytes / (1024 * 1024)

# Estado da sessão
if "historico" not in st.session_state:
    st.session_state.historico = []

if "docs_selecionados" not in st.session_state:
    st.session_state.docs_selecionados = []

# Sidebar - Navegação
st.sidebar.title("ManualBot")
st.sidebar.caption("Assistente RAG para documentação do ESP32 — Semana 3")

banco_status = "Ativo (ChromaDB)" if pipeline.vector_store is not None else "Não construído"
st.sidebar.markdown(f"**Status do Banco Vetorial:** {banco_status}")

st.sidebar.markdown("### Configurações")
modelo_selecionado = st.sidebar.selectbox(
    "Cérebro da IA",
    ["Gemini 3.6 Flash (Nuvem)"]
)
st.session_state.modelo_selecionado = modelo_selecionado

st.sidebar.markdown("### Navegação")
pagina = st.sidebar.radio(
    "Navegação",
    [
        "Chatbot: Consultar Manual",
        "Documentos & Ingestão",
        "Inspeção do Banco Vetorial"
    ],
    label_visibility="collapsed"
)

# ----------------------------------------------------
# Tela: Documentos & Ingestão
# ----------------------------------------------------
if pagina == "Documentos & Ingestão":
    st.title("Gerenciamento de Documentos & Ingestão")
    st.write("Gerencie a base de PDFs, execute o pipeline de Chunking + Embeddings e inspecione os arquivos.")

    pdfs_reais = carregar_pdfs_reais()

    st.subheader("1. Documentos na base de conhecimento")
    if pdfs_reais:
        st.success(f"{len(pdfs_reais)} documento(s) PDF encontrado(s) em `docs/PDFs-Instrucoes`:")
        for pdf in pdfs_reais:
            st.text(f"  • {pdf.name}")
    else:
        st.error("Nenhum PDF encontrado em `docs/PDFs-Instrucoes`.")

    st.divider()

    # Seção de Ingestão (Chunking Estático Fixo)
    st.subheader("Processar Ingestão (Chunking Estático + Embeddings + ChromaDB)")
    st.markdown(
        "O pipeline utiliza **Chunking Estático Fixo** padronizado especificamente para a "
        "documentação do ESP32 e o modelo `gemini-3.6 Flash`."
    )

    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    col_cfg1.metric("Tamanho do Chunk (Estático)", "900 caracteres")
    col_cfg2.metric("Overlap (Estático)", "150 caracteres")
    col_cfg3.metric("Estratégia", "RecursiveCharacterSplitter")

    chunk_size = 900
    chunk_overlap = 150

    if st.button("Executar Ingestão & Construir Banco Vetorial", type="primary", use_container_width=True):
        with st.spinner("Processando PDFs, gerando embeddings e salvando no ChromaDB... Isso pode levar alguns segundos."):
            inicio = time.time()
            res = pipeline.executar_ingestao(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            tempo_total = time.time() - inicio

        st.balloons()
        st.success(f"Ingestão concluída com sucesso em {tempo_total:.2f} segundos.")

        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Páginas Processadas", res["total_documentos"])
        col_res2.metric("Total de Chunks Gerados", res["total_chunks"])
        col_res3.metric("Local do Banco", "data/chroma_db")

    st.divider()

    st.subheader("Prova de leitura individual e inspeção de PDFs")
    tab1, tab2, tab3 = st.tabs(["Ler PDF Específico", "Sorteio Aleatório", "Relatório de Ingestão"])

    with tab1:
        if pdfs_reais:
            pdf_escolhido = st.selectbox("Selecione o documento", pdfs_reais, format_func=lambda p: p.name, key="pdf_sel")
            if st.button("Ler Frase Real do PDF", key="btn_ler_pdf"):
                with st.spinner("Lendo documento..."):
                    resultado = extrair_frase_de(pdf_escolhido)
                if resultado:
                    st.success(f"Lido de: **{resultado['documento']}** (página {resultado['pagina']} de {resultado['total_paginas']})")
                    st.markdown(f'> "{resultado["frase"]}."')
        else:
            st.warning("Nenhum PDF disponível.")

    with tab2:
        if st.button("Sortear Frase Aleatória", use_container_width=True):
            with st.spinner("Sorteando..."):
                resultado = extrair_frase_aleatoria()
            if resultado:
                st.success(f"Sorteado: **{resultado['documento']}** (página {resultado['pagina']} de {resultado['total_paginas']})")
                st.markdown(f'> "{resultado["frase"]}."')

    with tab3:
        if pdfs_reais:
            pdf_relatorio = st.selectbox("Selecione para análise", pdfs_reais, format_func=lambda p: p.name, key="pdf_rel")
            if st.button("Gerar Relatório de Análise", use_container_width=True):
                rel = extract_pdf(pdf_relatorio)
                st.metric("Total de Páginas", rel["n_pages"])
                st.metric("Páginas com atenção/visuais", len(rel["problem_pages"]))
                with st.expander("Inspeção técnica (JSON)"):
                    st.json(rel)

# ----------------------------------------------------
# Tela 3: Inspeção Visual do Banco Vetorial
# ----------------------------------------------------
elif pagina == "Inspeção do Banco Vetorial":
    st.title("Inspeção Visual do Banco Vetorial (ChromaDB)")
    st.markdown(
        "Esta tela permite que você e seus professores inspecionem visualmente o **banco vetorial físico** "
        "construído para o **ManualBot**, comprovando o chunking, metadados e os vetores de embeddings."
    )

    if pipeline.vector_store is None:
        st.warning("O banco vetorial ainda não foi carregado. Clique no botão abaixo para carregar.")
        if st.button("Carregar Banco Vetorial"):
            with st.spinner("Carregando ChromaDB..."):
                pipeline.carregar_banco_existente()
            st.rerun()
    else:
        try:
            total_chunks = pipeline.vector_store._collection.count()
            tamanho_mb = obter_tamanho_banco(pipeline.pasta_chroma)

            st.markdown("### Visão Geral do Armazenamento")
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Total de Chunks Indexados", f"{total_chunks:,}")
            col_m2.metric("Dimensões por Vetor", "384")
            col_m3.metric("Tamanho do Banco no Disco", f"{tamanho_mb:.1f} MB")
            col_m4.metric("Engine Vetorial", "ChromaDB + SQLite")

            st.info(f"**Caminho Físico do Banco:** `{pipeline.pasta_chroma / 'chroma.sqlite3'}`")

            st.divider()

            st.markdown("### Explorador de Chunks & Vetores")
            st.markdown("Escolha quantos chunks deseja inspecionar para visualizar o texto original, metadados e seus **embeddings numéricos**:")

            limite_inspecao = st.slider("Quantidade de chunks a carregar:", min_value=1, max_value=10, value=3)

            dada_sample = pipeline.vector_store._collection.get(
                limit=limite_inspecao,
                include=["embeddings", "documents", "metadatas"]
            )

            if dada_sample and dada_sample.get("documents"):
                for idx in range(len(dada_sample["documents"])):
                    chunk_text = dada_sample["documents"][idx]
                    metadata = dada_sample["metadatas"][idx] if dada_sample.get("metadatas") else {}
                    embedding_vector = dada_sample["embeddings"][idx] if dada_sample.get("embeddings") is not None else []
                    chunk_id = dada_sample["ids"][idx]

                    fonte_path = metadata.get("source", "Desconhecido")
                    fonte_nome = Path(fonte_path).name
                    pagina_num = metadata.get("page", 0) + 1

                    with st.expander(f"Chunk #{idx+1} — Fonte: {fonte_nome} (Página {pagina_num})", expanded=(idx==0)):
                        st.markdown(f"**ID no ChromaDB:** `{chunk_id}`")
                        st.markdown(f"**Documento de Origem:** `{fonte_nome}`")
                        st.markdown(f"**Página:** `{pagina_num}` | **Tamanho em Caracteres:** `{len(chunk_text)} chars`")

                        st.markdown("**Conteúdo do Texto do Chunk:**")
                        st.code(chunk_text, language="text")

                        if len(embedding_vector) > 0:
                            st.markdown("**Vetor de Embedding (384 dimensões):**")
                            # Formatar vetor para exibição amigável
                            amostra_vetor = [round(float(v), 5) for v in embedding_vector[:10]]
                            st.caption(
                                f"Amostra dos 10 primeiros elementos do vetor: `{amostra_vetor}` ... "
                                f"(Total de {len(embedding_vector)} valores numéricos float32)."
                            )
                            with st.popover("Visualizar vetor completo de 384 números"):
                                st.write(list(embedding_vector))
            else:
                st.warning("Nenhum chunk retornado.")

        except Exception as e:
            st.error(f"Erro ao acessar dados do ChromaDB: {str(e)}")

# ----------------------------------------------------
# Tela Principal: Chatbot Customizado
# ----------------------------------------------------
else:
    st.title("ManualBot - Atendimento Técnico")
    
    if st.session_state.modelo_selecionado == "Llama 3 (Ollama Local)":
        st.info("💡 A integração local do Llama 3 será implementada em breve! Operando via Gemini como fallback de segurança.")
    
    if pipeline.vector_store is None:
        st.warning("⚠️ O banco vetorial não está carregado. Por favor, vá em 'Documentos & Ingestão' e construa a base antes de iniciar o chat.")
    else:
        if "messages" not in st.session_state:
            # Mensagem de boas-vindas do bot
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Olá! Sou o **ManualBot**, seu assistente especialista em ESP32. Como posso ajudar no seu projeto hoje?"
                }
            ]
            
        # Renderizar o histórico de mensagens do chat
        for msg in st.session_state.messages:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
                # Se a mensagem tiver fontes (do assistente), renderiza os expanders
                if "fontes" in msg and msg["fontes"]:
                    with st.expander("📚 Ver Documentação Consultada"):
                        for i, res in enumerate(msg["fontes"], 1):
                            st.markdown(f"**{i}. Documento:** `{res['documento']}` — **Página:** {res['pagina']}")
                            st.caption(f"Relevância (Distância): {res['score_distancia']:.4f}")
                            st.info(res["conteudo"])

        # Input de chat na parte inferior (Fixo)
        if prompt := st.chat_input("Digite sua dúvida técnica sobre o ESP32..."):
            # 1. Adiciona a pergunta e exibe na tela
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
                
            # 2. Exibe o loader interativo e gera a resposta
            with st.chat_message("assistant", avatar="🤖"):
                with st.status("Consultando base de conhecimento...", expanded=True) as status:
                    st.write("🔍 Procurando contextos no banco vetorial (ChromaDB)...")
                    try:
                        resposta = pipeline.responder(prompt, top_k=3)
                        status.update(label="Resposta gerada com sucesso!", state="complete", expanded=False)
                        
                        st.markdown(resposta["resposta"])
                        
                        fontes = resposta["resultados"]
                        if fontes:
                            with st.expander("📚 Ver Documentação Consultada"):
                                for i, res in enumerate(fontes, 1):
                                    st.markdown(f"**{i}. Documento:** `{res['documento']}` — **Página:** {res['pagina']}")
                                    st.caption(f"Relevância (Distância): {res['score_distancia']:.4f}")
                                    st.info(res["conteudo"])
                                    
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": resposta["resposta"],
                            "fontes": fontes
                        })
                    except Exception as e:
                        status.update(label="Erro ao buscar informações", state="error", expanded=False)
                        msg_erro = f"Ocorreu um erro interno: {str(e)}"
                        st.error(msg_erro)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": msg_erro
                        })