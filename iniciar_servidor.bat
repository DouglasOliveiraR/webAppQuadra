@echo off
title Pelada FC Manager - Servidor
echo ========================================
echo   ⚽ Pelada FC Manager - Iniciando...
echo ========================================
echo.

:: Inicia o Frontend (Vite) em uma janela separada
echo 🎨 [Frontend] Iniciando React (Vite) na porta 5173...
start "Frontend - Vite" cmd /k "cd /d e:\APP_FUT_V2\frontend && npm run dev"

:: Aguarda 2 segundos para não conflitar
timeout /t 2 /nobreak >nul

:: Inicia o Backend (FastAPI) com venv ativada
echo 🐍 [Backend] Ativando venv e iniciando FastAPI (Uvicorn) na porta 8000...
start "Backend - Uvicorn" cmd /k "cd /d e:\APP_FUT_V2\backend && call .venv\Scripts\activate.bat && set PYTHONPATH=e:\APP_FUT_V2\backend\app && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo ========================================
echo   ✅ Servidores iniciados!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   Docs:     http://localhost:8000/docs
echo ========================================
echo.
echo Feche esta janela quando quiser. Os servidores continuam rodando nas janelas próprias.
pause
