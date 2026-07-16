
import random
import time
from pathlib import Path

import fitz  # PyMuPDF
import streamlit as st

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



# Função de leitura real (não-mock) - prova de conceito de extração

def extrair_frase_aleatoria():
    """Sorteia um PDF real da pasta docs/PDFs-Instrucoes, sorteia uma página,
    e extrai uma frase de verdade usando PyMuPDF. Usado só para demonstrar
    que a leitura dos documentos funciona - não faz parte do pipeline RAG."""
    projeto_raiz = Path(__file__).resolve().parents[2]
    pasta_pdfs = projeto_raiz / "docs" / "PDFs-Instrucoes"
    pdfs = list(pasta_pdfs.glob("*.pdf"))

    if not pdfs:
        return None

    pdf_escolhido = random.choice(pdfs)
    doc = fitz.open(pdf_escolhido)
    pagina_num = random.randint(0, doc.page_count - 1)
    texto = doc[pagina_num].get_text().strip()
    total_paginas = doc.page_count
    doc.close()

    frases = [f.strip() for f in texto.split(".") if len(f.strip()) > 30]
    frase = random.choice(frases) if frases else "(página sem frase longa, tente de novo)"

    return {
        "documento": pdf_escolhido.name,
        "pagina": pagina_num + 1,
        "total_paginas": total_paginas,
        "frase": frase,
    }



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
        "Sorteia um PDF e uma página reais de docs/PDFs-Instrucoes/ e extrai uma frase "
        "com PyMuPDF — mostra que a leitura funciona de verdade, sem mock."
    )

    if st.button("Provar que estou lendo os PDFs"):
        with st.spinner("Abrindo PDF e extraindo texto..."):
            resultado = extrair_frase_aleatoria()

        if resultado is None:
            st.error("Nenhum PDF encontrado em docs/PDFs-Instrucoes/.")
        else:
            st.success(
                f"Lido agora: **{resultado['documento']}** "
                f"(página {resultado['pagina']} de {resultado['total_paginas']})"
            )
            st.markdown(f"> \"{resultado['frase']}.\"")


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