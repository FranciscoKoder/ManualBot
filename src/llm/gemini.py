from langchain_google_genai import ChatGoogleGenerativeAI
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

LLM = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key= GOOGLE_API_KEY
)