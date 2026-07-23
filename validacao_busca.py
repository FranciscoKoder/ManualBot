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

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PASTA_CHROMA = PROJETO_RAIZ / "data" / "chroma_db"
MODELO_EMBEDDING = "sentence-transformers/all-MiniLM-L6-v2"

def validar_busca():
    print("==================================================")
    print("     MANUALBOT - VALIDAÇÃO DA BUSCA SEMÂNTICA     ")
    print("==================================================")

    if not PASTA_CHROMA.exists() or not any(PASTA_CHROMA.iterdir()):
        print(f"Erro: O banco vetorial em '{PASTA_CHROMA}' não existe ou está vazio.")
        print("Por favor, execute o script 'python ingestao.py' primeiro!")
        return

    print("\nCarregando modelo de embeddings e banco vetorial ChromaDB...")
    embeddings = HuggingFaceEmbeddings(
        model_name=MODELO_EMBEDDING,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    vector_store = Chroma(
        persist_directory=str(PASTA_CHROMA),
        embedding_function=embeddings
    )
    
    # Questões de teste sobre ESP32
    perguntas_teste = [
        "What is the operating voltage range for the ESP32?",
        "How many GPIO pins does the ESP32 have?",
        "What are the Wi-Fi protocols supported by the ESP32?",
        "How does deep sleep mode work on ESP32?"
    ]
    
    print("\n--- INICIANDO VALIDAÇÃO DA BUSCA SEMÂNTICA ---")
    for idx, pergunta in enumerate(perguntas_teste, 1):
        print(f"\n[Pergunta {idx}]: {pergunta}")
        print("=" * 60)
        
        resultados = vector_store.similarity_search_with_score(pergunta, k=3)
        
        for i, (doc, score) in enumerate(resultados):
            fonte_path = doc.metadata.get('source', 'Desconhecida')
            fonte_nome = Path(fonte_path).name
            pagina = doc.metadata.get('page', 0) + 1 # 1-indexed
            
            print(f"  Resultado {i+1} (Distância: {score:.4f}):")
            print(f"  Fonte: {fonte_nome} | Página: {pagina}")
            preview = doc.page_content.replace('\n', ' ').strip()[:200]
            print(f"  Trecho: \"{preview}...\"")
            print("  " + "-" * 50)

if __name__ == "__main__":
    validar_busca()
