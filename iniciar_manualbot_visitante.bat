@echo off
color 0D
echo ===================================================
echo     INICIANDO O MANUALBOT (MODO VISITANTE/PROFESSOR)
echo ===================================================
echo.
echo Este script vai abrir 3 janelinhas pretas. 
echo Ele usa uma conta pre-configurada do Ngrok.
echo Nao feche as telas enquanto estiver usando!
echo.

IF NOT EXIST ".venv\" (
    echo ===================================================
    echo [!] PRIMEIRA EXECUCAO DETECTADA!
    echo [!] Preparando o sistema automaticamente...
    echo [!] Instalando as dependencias em background.
    echo [!] Aguarde, isso pode levar 1 ou 2 minutos...
    echo ===================================================
    python -m venv .venv
    call .venv\Scripts\activate
    pip install -r requirements.txt > nul 2>&1
    echo [!] Tudo instalado com sucesso! Iniciando os modulos...
    echo.
) ELSE (
    echo [!] Sistema ja configurado. Iniciando os modulos...
    echo.
)

echo [1/3] Iniciando a API (Servidor Uvicorn)...
start "API do ManualBot (Uvicorn)" cmd /k "call .venv\Scripts\activate && uvicorn api:app --port 8000"
timeout /t 3 /nobreak > nul

echo [2/3] Iniciando a Interface Grafica (Streamlit)...
start "Interface do ManualBot (Streamlit)" cmd /k "call .venv\Scripts\activate && streamlit run src\app\app.py"
timeout /t 3 /nobreak > nul

echo [3/3] Iniciando a Ponte com o n8n (Ngrok) com Autenticacao...
start "Ponte Ngrok" cmd /k "ngrok http 127.0.0.1:8000 --authtoken 3HWqcbpsaRfCEVb6zicugBn3EHJ_75z1B5xP5deF7ekj2ps3x"

echo.
echo ===================================================
echo TUDO PRONTO! O sistema esta rodando.
echo ===================================================
pause
