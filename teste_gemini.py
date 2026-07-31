import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MINHA_CHAVE = os.getenv("GOOGLE_API_KEY")

def testar_conexao():
    if not MINHA_CHAVE:
        print("Erro: Chave GOOGLE_API_KEY não encontrada no arquivo .env")
        return

    print("Iniciando teste de conexão com o Gemini Pro...")

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=MINHA_CHAVE,
            temperature=0.3
        )

        mensagem = "Olá! Confirme que a nossa conexão via variável de ambiente funcionou."
        print("Enviando requisição...\n")

        resposta = llm.invoke(mensagem)
        print("✅ Resposta recebida:\n", resposta.content)

    except Exception as e:
        print("❌ ERRO:", e)

if __name__ == "__main__":
    testar_conexao()
