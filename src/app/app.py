
import random
import time
import sys
from pathlib import Path

import fitz  # PyMuPDF
import streamlit as st

# Adicionar o diretório src ao path para permitir imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Importar funções do módulo de ingestão
from ingestion.pdf_extract import (
    extrair_frase_de,
    extrair_frase_aleatoria,
    extract_pdf,
    listar_pdfs,
)



st.set_page_config(page_title="ManualBot - ESP32", page_icon="🔧", layout="wide")


# Dados mock (para a tela de consulta)

MOCK_DOCS = [
    "ESP32 Technical Reference Manual",
    "ESP32 Series Datasheet",
    "ESP32-WROOM-32 Datasheet",
    "ESP32 Hardware Design Guidelines",
    "ESP32 SoC Errata",
    "ESP-IDF Programming Guide",
    "Arduino-ESP32 Core",
]

MOCK_ANSWER = (
    "[PLACEHOLDER] Esta é uma resposta simulada. Quando o pipeline RAG "
    "estiver implementado, aqui aparecerá a resposta gerada pelo LLM com "
    "base nos trechos recuperados dos documentos selecionados."
)

MOCK_SOURCE = {
    "documento": "ESP32 Technical Reference Manual",
    "pagina": 42,
    "trecho": (
        "[PLACEHOLDER] Trecho do manual que teria sido usado como contexto "
        "para gerar a resposta acima aparecerá aqui, junto com o número da "
        "página de origem."
    ),
}



# Funções auxiliares

def carregar_pdfs_reais() -> list[Path]:
    """Carrega lista real de PDFs da pasta docs/PDFs-Instrucoes."""
    projeto_raiz = Path(__file__).resolve().parents[2]
    pasta_pdfs = projeto_raiz / "docs" / "PDFs-Instrucoes"
    return listar_pdfs(pasta_pdfs)


# Estado da sessão

if "historico" not in st.session_state:
    st.session_state.historico = []

if "docs_selecionados" not in st.session_state:
    st.session_state.docs_selecionados = []


# Sidebar - Navegação

st.sidebar.title("🔧 ManualBot")
st.sidebar.caption("Assistente de documentação técnica — ESP32")
pagina = st.sidebar.radio("Navegação", ["Início", "Documentos", "Consultar Manual"])


# Tela: Início

if pagina == "Início":
    st.title("Bem-vindo ao ManualBot")
    st.write(
        "Este protótipo demonstra a organização das telas do ManualBot, "
        "um sistema RAG para responder perguntas sobre a documentação técnica do ESP32."
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Domínio", "ESP32")
    col2.metric("Documentos na base", len(MOCK_DOCS))
    col3.metric("Status do pipeline", "Em construção")

    st.info(
        "Use o menu à esquerda: em **Documentos** você seleciona os manuais e pode provar "
        "que a leitura funciona de verdade, e em **Consultar Manual** você faz sua pergunta."
    )


# Tela: Documentos (seleção / upload / prova de leitura)

elif pagina == "Documentos":
    st.title("Documentos da Base")
    st.write("Selecione quais documentos o ManualBot deve considerar ao responder.")

    docs_selecionados = st.multiselect(
        "Documentos disponíveis",
        MOCK_DOCS,
        default=st.session_state.docs_selecionados or MOCK_DOCS[:2],
    )
    st.session_state.docs_selecionados = docs_selecionados

    st.divider()

    st.subheader("Upload de novo documento")
    st.caption("Placeholder — ainda não conectado ao pipeline de ingestão.")
    st.file_uploader("Adicionar PDF", type=["pdf"], accept_multiple_files=True)

    if docs_selecionados:
        st.success(f"{len(docs_selecionados)} documento(s) selecionado(s) para consulta.")
    else:
        st.warning("Nenhum documento selecionado ainda.")

    st.divider()
    st.subheader("Prova de leitura (dado real, ao vivo)")
    st.caption(
        "Funções do backend `pdf_extract.py` sendo chamadas pela interface Streamlit — "
        "sem mock, extração real de PDFs."
    )

    # Carregar PDFs reais
    pdfs_reais = carregar_pdfs_reais()

    if not pdfs_reais:
        st.error("⚠️ Nenhum PDF encontrado em docs/PDFs-Instrucoes/.")
    else:
        st.write(f"**{len(pdfs_reais)} PDF(s) encontrado(s)** na pasta de documentos.")

        # Abas para os diferentes modos de leitura
        tab1, tab2, tab3 = st.tabs(
            ["📖 Ler PDF Específico", "🎲 Sorteio Aleatório", "📋 Relatório Completo"]
        )

        # TAB 1: Ler PDF Específico
        with tab1:
            st.markdown("**Escolha um PDF e extraia uma frase real dele:**")
            pdf_escolhido = st.selectbox(
                "Selecione o documento",
                pdfs_reais,
                format_func=lambda p: p.name,
                key="pdf_selector",
            )

            col1, col2 = st.columns(2)
            with col1:
                btn_ler = st.button(
                    "📖 Ler PDF", key="btn_ler_pdf", use_container_width=True
                )

            if btn_ler:
                with st.spinner("Extraindo frase do PDF..."):
                    resultado = extrair_frase_de(pdf_escolhido)

                if resultado:
                    st.success(
                        f"Lido de: **{resultado['documento']}** "
                        f"(página {resultado['pagina']} de {resultado['total_paginas']})"
                    )
                    st.markdown(f'> "{resultado["frase"]}."')
                else:
                    st.error("Erro ao ler o PDF.")

        # TAB 2: Sorteio Aleatório
        with tab2:
            st.markdown("**Sorteia um PDF aleatório e extrai uma frase dele:**")

            if st.button("🎲 Sortear PDF e Frase", use_container_width=True):
                with st.spinner("Sorteando e extraindo..."):
                    resultado = extrair_frase_aleatoria()

                if resultado is None:
                    st.error("Nenhum PDF encontrado em docs/PDFs-Instrucoes/.")
                else:
                    st.success(
                        f"Sorteado: **{resultado['documento']}** "
                        f"(página {resultado['pagina']} de {resultado['total_paginas']})"
                    )
                    st.markdown(f'> "{resultado["frase"]}."')

        # TAB 3: Relatório Completo
        with tab3:
            st.markdown(
                "**Gere um relatório completo de um PDF** "
                "(páginas, problemas detectados, conteúdo visual, etc):"
            )

            pdf_relatorio = st.selectbox(
                "Selecione o documento para análise",
                pdfs_reais,
                format_func=lambda p: p.name,
                key="pdf_selector_relatorio",
            )

            if st.button("📋 Gerar Relatório", use_container_width=True):
                with st.spinner("Analisando PDF..."):
                    relatorio = extract_pdf(pdf_relatorio)

                st.subheader(f"Relatório: {relatorio['file']}")
                st.metric("Total de páginas", relatorio["n_pages"])
                st.metric("Páginas com problema", len(relatorio["problem_pages"]))

                if relatorio["problem_pages"]:
                    st.warning("**Páginas com possível problema:**")
                    for pp in relatorio["problem_pages"]:
                        st.write(f"- Página {pp['page']}: {pp['reason']}")

                with st.expander("📊 Visualizar JSON completo"):
                    st.json(relatorio)

# Tela: Consultar Manual

else:
    st.title("Consultar Manual do ESP32")

    if st.session_state.docs_selecionados:
        st.caption("Consultando em: " + ", ".join(st.session_state.docs_selecionados))
    else:
        st.warning("Nenhum documento selecionado. Vá até a tela **Documentos** primeiro.")

    pergunta = st.text_input(
        "Pergunta", placeholder="Ex: Como configurar o modo deep sleep no ESP32?"
    )

    consultar = st.button("Consultar", type="primary")

    if consultar:
        if not pergunta.strip():
            st.warning("Digite uma pergunta antes de consultar.")
        elif not st.session_state.docs_selecionados:
            st.warning("Selecione ao menos um documento na tela Documentos.")
        else:
            with st.spinner("Consultando documentação..."):
                time.sleep(1)
            st.session_state.historico.append(pergunta)

            st.subheader("Resposta")
            st.success(MOCK_ANSWER)

            st.subheader("Fonte utilizada")
            with st.container(border=True):
                st.markdown(f"**Documento:** {MOCK_SOURCE['documento']}")
                st.markdown(f"**Página:** {MOCK_SOURCE['pagina']}")
                st.markdown("**Trecho:**")
                st.markdown(f"> {MOCK_SOURCE['trecho']}")

    if st.session_state.historico:
        with st.expander("Histórico de perguntas desta sessão"):
            for h in reversed(st.session_state.historico):
                st.write(f"- {h}")