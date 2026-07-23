import logging
from pathlib import Path
from typing import List, Tuple, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from embeddings.embedding_factory import get_embedding_model

logger = logging.getLogger(__name__)

def get_chroma_path(projeto_raiz: Path) -> Path:
    """Retorna o caminho padrão da pasta do banco ChromaDB."""
    return projeto_raiz / "data" / "chroma_db"

def carregar_vector_store(persist_directory: Path, embedding_model=None) -> Optional[Chroma]:
    """Carrega o banco vetorial ChromaDB persistido no disco."""
    if not persist_directory.exists() or not any(persist_directory.iterdir()):
        return None
    
    if embedding_model is None:
        embedding_model = get_embedding_model()

    return Chroma(
        persist_directory=str(persist_directory),
        embedding_function=embedding_model
    )

def criar_banco_vetorial(
    chunks: List[Document],
    persist_directory: Path,
    embedding_model=None
) -> Chroma:
    """Cria e persiste o banco vetorial ChromaDB a partir de uma lista de chunks."""
    if embedding_model is None:
        embedding_model = get_embedding_model()

    persist_directory.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Gerando embeddings e salvando ChromaDB em: {persist_directory}")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=str(persist_directory)
    )
    return vector_store

def realizar_busca_semantica(
    query: str,
    vector_store: Chroma,
    k: int = 3,
    filtro_documentos: Optional[List[str]] = None
) -> List[Tuple[Document, float]]:
    """
    Executa busca por similaridade semântica no banco vetorial.
    """
    resultados = vector_store.similarity_search_with_score(query, k=k)
    return resultados
