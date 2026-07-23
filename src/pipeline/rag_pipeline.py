import logging
from pathlib import Path
from typing import Dict, Any, List

from ingestion.chunker import carregar_e_dividir_documentos
from embeddings.embedding_factory import get_embedding_model
from retrieval.vector_store import (
    get_chroma_path,
    carregar_vector_store,
    criar_banco_vetorial,
    realizar_busca_semantica,
)

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, projeto_raiz: Path = None):
        if projeto_raiz is None:
            projeto_raiz = Path(__file__).resolve().parents[2]
        self.projeto_raiz = projeto_raiz
        self.pasta_docs = self.projeto_raiz / "docs" / "PDFs-Instrucoes"
        self.pasta_chroma = get_chroma_path(self.projeto_raiz)
        self.embedding_model = None
        self.vector_store = None

    def inicializar_modelo(self):
        if self.embedding_model is None:
            self.embedding_model = get_embedding_model()
        return self.embedding_model

    def carregar_banco_existente(self):
        self.inicializar_modelo()
        self.vector_store = carregar_vector_store(self.pasta_chroma, self.embedding_model)
        return self.vector_store is not None

    def executar_ingestao(self, chunk_size: int = 800, chunk_overlap: int = 100) -> Dict[str, Any]:
        """
        Executa a esteira da Semana 2:
        1. Carrega PDFs
        2. Aplica Chunking
        3. Gera Embeddings
        4. Cria e persiste o Banco Vetorial
        """
        self.inicializar_modelo()
        documentos, chunks = carregar_e_dividir_documentos(
            self.pasta_docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        self.vector_store = criar_banco_vetorial(
            chunks=chunks,
            persist_directory=self.pasta_chroma,
            embedding_model=self.embedding_model
        )

        return {
            "total_documentos": len(documentos),
            "total_chunks": len(chunks),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "caminho_chroma": str(self.pasta_chroma)
        }

    def consultar(self, pergunta: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Executa a busca semântica no banco vetorial.
        """
        if self.vector_store is None:
            if not self.carregar_banco_existente():
                raise RuntimeError("Banco vetorial não foi construído ainda. Execute a ingestão primeiro.")

        resultados_com_score = realizar_busca_semantica(
            query=pergunta,
            vector_store=self.vector_store,
            k=top_k
        )

        formatados = []
        for doc, score in resultados_com_score:
            fonte_path = doc.metadata.get("source", "Desconhecido")
            fonte_nome = Path(fonte_path).name if fonte_path != "Desconhecido" else "Desconhecido"
            pagina = doc.metadata.get("page", 0) + 1  # 1-indexed

            formatados.append({
                "documento": fonte_nome,
                "pagina": pagina,
                "score_distancia": float(score),
                "conteudo": doc.page_content,
                "metadata": doc.metadata
            })
        return formatados
