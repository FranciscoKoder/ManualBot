@echo off
color 0B
echo ===================================================
echo           INICIANDO O MANUALBOT (ESP32)
echo ===================================================
echo.
echo Este script vai abrir 3 janelinhas pretas. 
echo Nao feche elas enquanto estiver usando o projeto!
echo.

echo [1/3] Iniciando a API (Servidor Uvicorn)...
start "API do ManualBot (Uvicorn)" cmd /k "call .venv\Scripts\activate && uvicorn api:app --port 8000"
timeout /t 3 /nobreak > nul

echo [2/3] Iniciando a Interface Grafica (Streamlit)...
start "Interface do ManualBot (Streamlit)" cmd /k "call .venv\Scripts\activate && streamlit run src\app\app.py"
timeout /t 3 /nobreak > nul

echo [3/3] Iniciando a Ponte com o n8n (Ngrok)...
start "Ponte Ngrok" cmd /k "ngrok http 127.0.0.1:8000"

echo.
echo ===================================================
echo TUDO PRONTO! O sistema esta rodando.
echo - A interface do Streamlit vai abrir no seu navegador.
echo - Pegue o link novo na janelinha do Ngrok e atualize no n8n.
echo ===================================================
pause
