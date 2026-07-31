import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI

# Subindo 2 níveis até a raiz 'ManualBot'
projeto_raiz = Path(__file__).resolve().parents[2]
load_dotenv(projeto_raiz / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

LLM = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    api_key=GOOGLE_API_KEY  # Parâmetro recomendado: api_key
)