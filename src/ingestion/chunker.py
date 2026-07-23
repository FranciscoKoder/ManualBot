import logging
from pathlib import Path
from typing import List, Tuple
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

def carregar_e_dividir_documentos(
    pasta_docs: Path,
    chunk_size: int = 800,
    chunk_overlap: int = 100
) -> Tuple[List[Document], List[Document]]:
    """
    Carrega todos os PDFs presentes na pasta especificada e aplica
    o chunking utilizando RecursiveCharacterTextSplitter.
    
    Retorna uma tupla: (documentos_originais, lista_de_chunks).
    """
    pasta_docs = Path(pasta_docs)
    if not pasta_docs.exists():
        raise FileNotFoundError(f"A pasta '{pasta_docs}' não existe.")

    logger.info(f"Carregando PDFs de: {pasta_docs}")
    loader = PyPDFDirectoryLoader(str(pasta_docs))
    documentos = loader.load()

    logger.info(f"Aplicando chunking (size={chunk_size}, overlap={chunk_overlap})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documentos)
    logger.info(f"Carregados {len(documentos)} páginas. Gerados {len(chunks)} chunks.")
    
    return documentos, chunks
