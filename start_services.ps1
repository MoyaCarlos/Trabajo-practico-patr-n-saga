# Script para iniciar todos los microservicios con Granian en Windows (PowerShell)

Write-Host ""
Write-Host "🚀 Iniciando microservicios con Granian..." -ForegroundColor Cyan
Write-Host ""

# Función para manejar Ctrl+C
$jobs = @()

# Iniciar Catálogo (2 workers)
Write-Host "📦 Iniciando ms_catalogo en puerto 5001..." -ForegroundColor Green
$jobs += Start-Job -ScriptBlock {
    granian --interface wsgi --host 0.0.0.0 --port 5001 --workers 2 --threads 4 --backpressure 100 ms_catalogo.app:app
}

# Iniciar Compras (2 workers)
Write-Host "🛒 Iniciando ms_compras en puerto 5002..." -ForegroundColor Green
$jobs += Start-Job -ScriptBlock {
    granian --interface wsgi --host 0.0.0.0 --port 5002 --workers 2 --threads 4 --backpressure 100 ms_compras.app:app
}

# Iniciar Pagos (2 workers)
Write-Host "💳 Iniciando ms_pagos en puerto 5003..." -ForegroundColor Green
$jobs += Start-Job -ScriptBlock {
    granian --interface wsgi --host 0.0.0.0 --port 5003 --workers 2 --threads 4 --backpressure 100 ms_pagos.app:app
}

# Iniciar Inventario (2 workers)
Write-Host "📦 Iniciando ms_inventario en puerto 5004..." -ForegroundColor Green
$jobs += Start-Job -ScriptBlock {
    granian --interface wsgi --host 0.0.0.0 --port 5004 --workers 2 --threads 4 --backpressure 100 ms_inventario.app:app
}

# Esperar un poco para que los microservicios inicien
Start-Sleep -Seconds 2

# Iniciar Orchestrator (4 workers - maneja más carga)
Write-Host "🎯 Iniciando orchestrator en puerto 5000..." -ForegroundColor Green
$jobs += Start-Job -ScriptBlock {
    granian --interface wsgi --host 0.0.0.0 --port 5000 --workers 4 --threads 8 --backpressure 200 orchestrator.app:app
}

Write-Host ""
Write-Host "✅ Todos los servicios iniciados" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Endpoints disponibles:" -ForegroundColor Yellow
Write-Host "   - Orchestrator: http://localhost:5000/compra"
Write-Host "   - Catálogo:     http://localhost:5001/health"
Write-Host "   - Compras:      http://localhost:5002/health"
Write-Host "   - Pagos:        http://localhost:5003/health"
Write-Host "   - Inventario:   http://localhost:5004/health"
Write-Host ""
Write-Host "⚙️  Configuración de workers:" -ForegroundColor Yellow
Write-Host "   - Orchestrator: 4 workers (alta carga)"
Write-Host "   - Microservicios: 2 workers cada uno"
Write-Host ""
Write-Host "🛑 Para detener todos los servicios: Ctrl+C" -ForegroundColor Red
Write-Host ""

# Mantener el script corriendo y mostrar logs
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    # Limpiar jobs al salir
    Write-Host ""
    Write-Host "🛑 Deteniendo servicios..." -ForegroundColor Yellow
    $jobs | Stop-Job
    $jobs | Remove-Job
    Write-Host "✅ Servicios detenidos" -ForegroundColor Green
}
