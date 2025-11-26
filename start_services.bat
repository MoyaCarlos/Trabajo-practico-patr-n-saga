@echo off
REM Script para iniciar todos los microservicios con Granian en Windows
echo.
echo Iniciando microservicios con Granian...
echo.

REM Iniciar Catalogo (2 workers)
echo Iniciando ms_catalogo en puerto 5001...
start /B granian --interface wsgi --host 0.0.0.0 --port 5001 --workers 2 --threads 4 --backpressure 100 ms_catalogo.app:app

REM Iniciar Compras (2 workers)
echo Iniciando ms_compras en puerto 5002...
start /B granian --interface wsgi --host 0.0.0.0 --port 5002 --workers 2 --threads 4 --backpressure 100 ms_compras.app:app

REM Iniciar Pagos (2 workers)
echo Iniciando ms_pagos en puerto 5003...
start /B granian --interface wsgi --host 0.0.0.0 --port 5003 --workers 2 --threads 4 --backpressure 100 ms_pagos.app:app

REM Iniciar Inventario (2 workers)
echo Iniciando ms_inventario en puerto 5004...
start /B granian --interface wsgi --host 0.0.0.0 --port 5004 --workers 2 --threads 4 --backpressure 100 ms_inventario.app:app

REM Esperar un poco para que los microservicios inicien
timeout /t 2 /nobreak >nul

REM Iniciar Orchestrator (4 workers - maneja mas carga)
echo Iniciando orchestrator en puerto 5000...
start /B granian --interface wsgi --host 0.0.0.0 --port 5000 --workers 4 --threads 8 --backpressure 200 orchestrator.app:app

echo.
echo Todos los servicios iniciados
echo.
echo Endpoints disponibles:
echo    - Orchestrator: http://localhost:5000/compra
echo    - Catalogo:     http://localhost:5001/health
echo    - Compras:      http://localhost:5002/health
echo    - Pagos:        http://localhost:5003/health
echo    - Inventario:   http://localhost:5004/health
echo.
echo Configuracion de workers:
echo    - Orchestrator: 4 workers (alta carga)
echo    - Microservicios: 2 workers cada uno
echo.
echo Para detener todos los servicios: Ctrl+C
echo.
pause
