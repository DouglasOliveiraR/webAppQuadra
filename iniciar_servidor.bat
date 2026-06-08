@echo off
title Pelada FC Manager - Servidor Local (Docker)
echo ========================================
echo   ⚽ Pelada FC Manager - Iniciando...
echo ========================================
echo.

echo 🐍 [Backend] Iniciando o servidor FastAPI...
start "Backend (API)" cmd /k "cd /d e:\APP_FUT_V2\backend && .venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo ⚛️ [Frontend] Iniciando o servidor Vite...
start "Frontend (App)" cmd /k "cd /d e:\APP_FUT_V2\frontend && npm run dev"

echo.
echo ========================================
echo   ✅ Servidores em modo desenvolvimento iniciados!
echo   Frontend (App): http://localhost:5173
echo   Backend (API):  http://localhost:8000/api/
echo   Docs da API:    http://localhost:8000/docs
echo ========================================
echo.
echo Feche esta janela quando quiser. Os servidores continuam rodando nas janelas separadas.
pause
