import site
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

PROJETO_RAIZ = Path(__file__).resolve().parent
SRC_DIR = PROJETO_RAIZ / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Configurações baseadas na arquitetura do ManualBot (Semana 2)
PASTA_DOCUMENTOS = PROJETO_RAIZ / "docs" / "PDFs-Instrucoes"
PASTA_CHROMA = PROJETO_RAIZ / "data" / "chroma_db"
MODELO_EMBEDDING = "sentence-transformers/all-MiniLM-L6-v2"

def main():
    print("==================================================")
    print("      MANUALBOT - INGESTÃO E BANCO VETORIAL       ")
    print("==================================================")
    
    print(f"\n1. Carregando documentos PDF da pasta: {PASTA_DOCUMENTOS}")
    loader = PyPDFDirectoryLoader(str(PASTA_DOCUMENTOS))
    documentos = loader.load()
    print(f"   -> Total de páginas/documentos carregados: {len(documentos)}")

    print("\n2. Aplicando estratégia de Chunking...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documentos)
    print(f"   -> Total de chunks gerados: {len(chunks)}")
    print(f"   -> Configuração: chunk_size=800, chunk_overlap=100")

    print(f"\n3. Gerando Embeddings ({MODELO_EMBEDDING}) e construindo o Banco Vetorial...")
    embeddings = HuggingFaceEmbeddings(
        model_name=MODELO_EMBEDDING,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    PASTA_CHROMA.mkdir(parents=True, exist_ok=True)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(PASTA_CHROMA)
    )
    
    print(f"\n[SUCESSO] Banco vetorial construído e salvo com sucesso em: '{PASTA_CHROMA}'!")

if __name__ == "__main__":
    if not PASTA_DOCUMENTOS.exists():
        PASTA_DOCUMENTOS.mkdir(parents=True, exist_ok=True)
        print(f"Pasta '{PASTA_DOCUMENTOS}' criada. Coloque seus PDFs nela e execute novamente.")
    else:
        main()
