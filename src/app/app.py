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

# ------------------------------------------------------------------
# Identidade visual: paleta ManualBot + tipografia
# Título/headers: Barlow Condensed (peso 900 / Black)
# Corpo de texto: Plus Jakarta Sans (regular)
# ------------------------------------------------------------------
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

    /* Botões secundários com hover em azul claro */
    .stButton > button {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        border-radius: 8px !important;
        transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background-color: #E6F0FA !important;
        border-color: var(--mb-primary) !important;
        color: var(--mb-primary) !important;
    }

    /* Caixas de código, expanders e containers */
    div.stCodeBlock, div[data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--mb-border) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: #E6F0FA !important;
    }

    /* Abas, com hover em azul claro */
    button[data-baseweb="tab"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px 8px 0 0 !important;
    }
    button[data-baseweb="tab"]:hover {
        background-color: #E6F0FA !important;
    }

    /* Itens de dropdown (selectbox / multiselect) */
    li[role="option"]:hover,
    [data-baseweb="menu"] li:hover {
        background-color: #E6F0FA !important;
    }

    /* Botão de recolher/expandir a sidebar */
    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="baseButton-headerNoPadding"]:hover {
        background-color: #E6F0FA !important;
        border-radius: 6px !important;
    }

    /* Checkboxes e radios fora da sidebar (ex: dentro de formulários) */
    div[data-testid="stCheckbox"] label:hover,
    div[data-testid="stRadio"] label:hover {
        background-color: #E6F0FA !important;
        border-radius: 6px !important;
    }

    /* Cabeçalho de itens no popover (ex: vetor de embedding completo) */
    [data-baseweb="popover"] button:hover {
        background-color: #E6F0FA !important;
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
        background-color: #E6F0FA !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background-color: #E6F0FA !important;
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
st.sidebar.caption("Assistente RAG para documentação do ESP32 — Semana 2")

banco_status = "Ativo (ChromaDB)" if pipeline.vector_store is not None else "Não construído"
st.sidebar.markdown(f"**Status do Banco Vetorial:** {banco_status}")

pagina = st.sidebar.radio(
    "Navegação",
    [
        "Início",
        "Documentos & Ingestão",
        "Inspeção do Banco Vetorial",
        "Consultar Manual (Busca Semântica)"
    ],
    label_visibility="collapsed"
)

# ----------------------------------------------------
# Tela 1: Início
# ----------------------------------------------------
if pagina == "Início":
    st.title("Bem-vindo ao ManualBot — ESP32")
    st.markdown(
        """
        O **ManualBot** é um sistema RAG (Retrieval-Augmented Generation) projetado para
        responder perguntas técnicas sobre o **ESP32** com base na sua documentação oficial.
        """
    )

    st.markdown("### Status da Entrega - Semana 2")
    col1, col2, col3, col4 = st.columns(4)

    pdfs_reais = carregar_pdfs_reais()
    col1.metric("PDFs na Base", len(pdfs_reais))
    col2.metric("Chunk Size / Overlap", "800 / 100")
    col3.metric("Modelo de Embeddings", "all-MiniLM-L6-v2")

    tamanho_mb = obter_tamanho_banco(pipeline.pasta_chroma)
    col4.metric("Tamanho ChromaDB", f"{tamanho_mb:.1f} MB")

    st.divider()

    st.markdown("### Funcionalidades da Semana 2")
    col_a, col_b = st.columns(2)

    with col_a:
        st.info(
            "**Ingestão & Chunking**\n\n"
            "Processamento automático dos PDFs usando `RecursiveCharacterTextSplitter` "
            "com tamanho de 800 caracteres e sobreposição de 100 caracteres."
        )
        st.info(
            "**Embeddings & Banco Vetorial**\n\n"
            "Vetorização com HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`) "
            "e persistência no ChromaDB local (`data/chroma_db`)."
        )

    with col_b:
        st.success(
            "**Inspeção Visual do Banco Vetorial**\n\n"
            "Na aba **Inspeção do Banco Vetorial**, visualize a quantidade exata de chunks "
            "indexados, amostras de texto e os vetores numéricos de 384 dimensões em tempo real."
        )
        st.warning(
            "**Busca Semântica em Tempo Real**\n\n"
            "Na aba **Consultar Manual**, realize consultas semânticas sobre a documentação "
            "com ranking por similaridade/distância."
        )

# ----------------------------------------------------
# Tela 2: Documentos & Ingestão
# ----------------------------------------------------
elif pagina == "Documentos & Ingestão":
    st.title("Gerenciamento de Documentos & Ingestão (Semana 2)")
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

    # Seção de Ingestão (Semana 2 - Parâmetros Estáticos Fixo)
    st.subheader("Processar Ingestão (Chunking Estático + Embeddings + ChromaDB)")
    st.markdown(
        "O pipeline da Semana 2 utiliza **Chunking Estático Fixo** padronizado especificamente para a "
        "documentação do ESP32 e o modelo `all-MiniLM-L6-v2`."
    )

    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    col_cfg1.metric("Tamanho do Chunk (Estático)", "800 caracteres")
    col_cfg2.metric("Overlap (Estático)", "100 caracteres")
    col_cfg3.metric("Estratégia", "RecursiveCharacterSplitter")

    chunk_size = 800
    chunk_overlap = 100

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
# Tela 4: Consultar Manual (Busca Semântica Real)
# ----------------------------------------------------
else:
    st.title("Consultar Manual — Busca Semântica Real (Semana 2)")
    st.markdown(
        "Faça uma pergunta sobre o ESP32. O sistema utilizará os **embeddings** "
        "e o **ChromaDB** para recuperar os trechos mais relevantes da documentação."
    )

    if pipeline.vector_store is None:
        st.warning(
            "O banco vetorial ainda não foi inicializado nesta sessão. "
            "Você pode clicar no botão abaixo para carregar/gerar o banco vetorial."
        )
        if st.button("Carregar/Construir Banco Vetorial Agora"):
            with st.spinner("Inicializando modelo de embeddings e ChromaDB..."):
                if not pipeline.carregar_banco_existente():
                    pipeline.executar_ingestao()
            st.rerun()

    pergunta_sugerida = st.selectbox(
        "Sugestões de perguntas de teste (Semana 1 / 2):",
        [
            "Selecione ou digite uma pergunta abaixo...",
            "What is the operating voltage range for the ESP32?",
            "How many GPIO pins does the ESP32 have?",
            "What are the Wi-Fi protocols supported by the ESP32?",
            "How does deep sleep mode work on ESP32?",
            "What is the maximum CPU frequency of the ESP32?"
        ]
    )

    valor_inicial = pergunta_sugerida if pergunta_sugerida != "Selecione ou digite uma pergunta abaixo..." else ""

    pergunta = st.text_input("Sua pergunta:", value=valor_inicial, placeholder="Ex: What is the operating voltage of ESP32?")
    top_k = st.slider("Quantidade de trechos a recuperar (Top K):", min_value=1, max_value=6, value=3)

    consultar = st.button("Executar Busca Semântica", type="primary", use_container_width=True)

    if consultar:
        if not pergunta.strip():
            st.warning("Por favor, digite uma pergunta válida.")
        else:
            with st.spinner("Buscando vetores mais similares no ChromaDB..."):
                try:
                    resultados = pipeline.consultar(pergunta, top_k=top_k)
                    st.session_state.historico.append(pergunta)

                    st.subheader(f"Trechos mais relevantes encontrados (Top {len(resultados)})")

                    for i, res in enumerate(resultados, 1):
                        with st.container(border=True):
                            col_head1, col_head2 = st.columns([3, 1])
                            with col_head1:
                                st.markdown(f"**{i}. Documento:** `{res['documento']}` — **Página:** {res['pagina']}")
                            with col_head2:
                                st.caption(f"Distância Coseno: `{res['score_distancia']:.4f}`")

                            st.markdown("**Trecho recuperado:**")
                            st.info(res["conteudo"])

                except Exception as e:
                    st.error(f"Erro durante a busca semântica: {str(e)}")

    if st.session_state.historico:
        with st.expander("Histórico de perguntas da sessão"):
            for h in reversed(st.session_state.historico):
                st.write(f"• {h}")