@echo off
title Pelada FC Manager - Servidor Local (Docker)
echo ========================================
echo   ⚽ Pelada FC Manager - Iniciando...
echo ========================================
echo.

echo 🐳 [Docker] Iniciando os containers (Frontend NGINX + Backend FastAPI)...
start "Docker Compose" cmd /k "cd /d e:\APP_FUT_V2 && docker-compose up --build"

echo.
echo ========================================
echo   ✅ Servidores iniciados via Docker!
echo   Frontend (App): http://localhost
echo   Backend (API):  http://localhost:8000/api/
echo   Docs da API:    http://localhost:8000/docs
echo ========================================
echo.
echo Feche esta janela quando quiser. Os servidores continuam rodando na janela do Docker Compose.
pause
