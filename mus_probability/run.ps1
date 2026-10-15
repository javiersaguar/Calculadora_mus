# Inicia backend (FastAPI) y frontend (Vite) en ventanas separadas.
# Backend: http://localhost:8001  Docs: http://localhost:8001/docs
# Frontend: http://localhost:5173

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$root\backend'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"
)

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$root\frontend'; npm run dev"
)

Write-Host ""
Write-Host "Calculadora de Mus iniciada:" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8001" -ForegroundColor Cyan
Write-Host "  API docs: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cierra las dos ventanas de PowerShell para detener los servidores."
