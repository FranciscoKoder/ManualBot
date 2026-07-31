import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
chave = os.getenv("GOOGLE_API_KEY")

if not chave:
    print("❌ Erro: Chave GOOGLE_API_KEY não encontrada no .env")
    exit()

genai.configure(api_key=chave)

print("==================================================")
print(" MODELOS LIBERADOS PARA GERAÇÃO DE TEXTO")
print("==================================================\n")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Nome exato: {m.name}")
except Exception as e:
    print(f"Erro ao consultar a API: {e}")
