import logging
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_embedding_instance = None

def get_embedding_model(model_name: str = DEFAULT_MODEL_NAME):
    """
    Retorna uma instância singleton ou nova do modelo de embeddings da HuggingFace.
    Usando 'all-MiniLM-L6-v2' que roda localmente de forma eficiente no CPU.
    """
    global _embedding_instance
    if _embedding_instance is None:
        logger.info(f"Carregando modelo de embedding: {model_name}")
        _embedding_instance = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embedding_instance
