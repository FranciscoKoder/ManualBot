"""
API do ManualBot — ponte entre o pipeline RAG (Python) e o n8n.

Como rodar:
    uvicorn api:app --reload --port 8000

Como testar sem o n8n (no navegador ou com curl):
    http://localhost:8000/docs   -> interface automática de testes (Swagger)

Endpoint principal:
    POST /perguntar
    Body (JSON): {"pergunta": "What is the operating voltage range for the ESP32?", "top_k": 3}
    Resposta (JSON): {
        "pergunta": "...",
        "resposta": "...",
        "fontes": [{"documento": "...", "pagina": 1, "trecho": "...", "distancia": 0.23}]
    }

O n8n deve usar um nó "HTTP Request" apontando para http://localhost:8000/perguntar
(método POST, corpo em JSON com o campo "pergunta").
"""

import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pipeline.rag_pipeline import RAGPipeline

app = FastAPI(
    title="ManualBot API",
    description="API que expõe o pipeline RAG do ManualBot (ESP32) para consumo externo, como o n8n.",
    version="1.0.0"
)

projeto_raiz = Path(__file__).resolve().parent
pipeline = RAGPipeline(projeto_raiz)
pipeline.carregar_banco_existente()


class PerguntaRequest(BaseModel):
    pergunta: str
    top_k: int = 3


class FonteResponse(BaseModel):
    documento: str
    pagina: int
    trecho: str
    distancia: float


class RespostaResponse(BaseModel):
    pergunta: str
    resposta: str
    fontes: list[FonteResponse]


@app.get("/")
def raiz():
    """Endpoint simples para checar se a API está no ar."""
    return {
        "status": "online",
        "banco_vetorial_carregado": pipeline.vector_store is not None
    }


@app.post("/perguntar", response_model=RespostaResponse)
def perguntar(request: PerguntaRequest):
    """
    Recebe uma pergunta em linguagem natural, executa a busca semântica
    e retorna a resposta gerada pelo LLM, junto das fontes utilizadas.
    """
    if not request.pergunta.strip():
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    try:
        resultado = pipeline.responder(request.pergunta, request.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {str(e)}")

    fontes = [
        FonteResponse(
            documento=r["documento"],
            pagina=r["pagina"],
            trecho=r["conteudo"],
            distancia=r["score_distancia"]
        )
        for r in resultado["resultados"]
    ]

    return RespostaResponse(
        pergunta=resultado["pergunta"],
        resposta=resultado["resposta"],
        fontes=fontes
    )
