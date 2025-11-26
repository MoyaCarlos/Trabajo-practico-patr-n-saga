#!/bin/bash

# Script para iniciar todos los microservicios con Granian
# Granian es un servidor WSGI de alto rendimiento escrito en Rust

echo "🚀 Iniciando microservicios con Granian..."
echo ""

# Función para matar procesos al recibir SIGINT (Ctrl+C)
trap 'kill $(jobs -p) 2>/dev/null; echo ""; echo "🛑 Servicios detenidos"; exit 0' SIGINT

# Iniciar Catálogo (2 workers)
echo "📦 Iniciando ms_catalogo en puerto 5001..."
granian --interface wsgi --host 0.0.0.0 --port 5001 --workers 2 ms_catalogo.app:app &

# Iniciar Compras (2 workers)
echo "🛒 Iniciando ms_compras en puerto 5002..."
granian --interface wsgi --host 0.0.0.0 --port 5002 --workers 2 ms_compras.app:app &

# Iniciar Pagos (2 workers)
echo "💳 Iniciando ms_pagos en puerto 5003..."
granian --interface wsgi --host 0.0.0.0 --port 5003 --workers 2 ms_pagos.app:app &

# Iniciar Inventario (2 workers)
echo "📦 Iniciando ms_inventario en puerto 5004..."
granian --interface wsgi --host 0.0.0.0 --port 5004 --workers 2 ms_inventario.app:app &

# Esperar un poco para que los microservicios inicien
sleep 2

# Iniciar Orchestrator (4 workers - maneja más carga)
echo "🎯 Iniciando orchestrator en puerto 5000..."
granian --interface wsgi --host 0.0.0.0 --port 5000 --workers 4 orchestrator.app:app &

echo ""
echo "✅ Todos los servicios iniciados"
echo ""
echo "📋 Endpoints disponibles:"
echo "   - Orchestrator: http://localhost:5000/compra"
echo "   - Catálogo:     http://localhost:5001/health"
echo "   - Compras:      http://localhost:5002/health"
echo "   - Pagos:        http://localhost:5003/health"
echo "   - Inventario:   http://localhost:5004/health"
echo ""
echo "⚙️  Configuración de workers:"
echo "   - Orchestrator: 4 workers (alta carga)"
echo "   - Microservicios: 2 workers cada uno"
echo ""
echo "📊 Para ver logs en tiempo real, revisa la salida de la consola"
echo "🛑 Para detener todos los servicios: Ctrl+C"
echo ""

# Mantener el script corriendo
wait
