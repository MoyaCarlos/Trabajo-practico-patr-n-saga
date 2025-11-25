# Pagos Flask application
from flask import Flask, jsonify, request
import logging
import sys
import os
from datetime import datetime

# Agregar el directorio padre al path para importar common
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.transaction_helper import simular_latencia, tiene_exito, generar_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")

app = Flask(__name__)

pagos_exitosos={}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "ms-pagos"}), 200

@app.route("/transaccion", methods=["POST"])
def procesar_pago():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    monto = data.get("monto")
    compra_id = data.get('compra_id')  # ID de la compra asociada

    logger.info(f'Procesando pago para usuario_id: {usuario_id} por monto: ${monto}')
    
    # Simular latencia
    simular_latencia()

    # Simular éxito o fallo aleatorio usando helper
    if not tiene_exito():
        logger.warning(f'Fallo al procesar pago para usuario {usuario_id}')
        return jsonify({
            "success": False,
            "error": "No se pudo procesar el pago"
        }), 409
    
    # ÉXITO - Registrar pago usando helper para generar ID
    pago_id = generar_id()
    pagos_exitosos[pago_id] = {
        "pago_id": pago_id,
        "usuario_id": usuario_id,
        "monto": monto,
        "compra_id": compra_id,
        "estado": "aprobado",
        "fecha": datetime.now().isoformat()
    }
    logger.info(f'✅ Pago procesado exitosamente: {pagos_exitosos[pago_id]}')
    return jsonify({
        "success": True,
        "pago_id": pago_id,
        "mensaje": "Pago procesado exitosamente"
    }), 200

@app.route('/compensacion', methods=['POST'])
def compensar_pago():
    data = request.get_json()
    pago_id = data.get('pago_id')
    
    if not pago_id:
        logger.warning("⚠️  Compensación llamada sin pago_id")
        return jsonify({
            "success": True,
            "mensaje": "No hay pago para compensar"
        }), 200
    
    # Buscar y reembolsar el pago
    if pago_id in pagos_exitosos:
        pagos_exitosos[pago_id]['estado'] = 'reembolsado'
        logger.info(f"↩️  Pago {pago_id} reembolsado exitosamente")
    else:
        logger.warning(f"⚠️  Pago {pago_id} no encontrado (quizás ya fue reembolsado)")
    
    return jsonify({
        "success": True,
        "mensaje": "Pago reembolsado"
    }), 200

@app.route("/pagos", methods=["GET"])
def ver_pagos():
    logger.info(f'📋 Listado de pagos solicitados - Total de pagos: {len(pagos_exitosos)}')
    return jsonify({"pagos": list(pagos_exitosos.values()), "total": len(pagos_exitosos)}), 200

if __name__ == '__main__':
    logger.info("🚀 Iniciando ms-pagos en puerto 5003...")
    logger.info("✅ Servicio listo - Health check: http://localhost:5003/health")
    app.run(host='0.0.0.0', port=5003, debug=True)