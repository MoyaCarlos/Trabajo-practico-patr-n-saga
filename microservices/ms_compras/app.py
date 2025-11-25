# Compras Flask application
from flask import Flask, jsonify, request  # ← request para recibir JSON
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

compras_db = {} 
#GET  /health              → Health check
#POST /transaccion         → Registra compra (200 o 409 aleatorio)
#POST /compensacion        → Cancela compra (200 siempre)

#metodo get para health check. Codigo 200
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "ms-compras"}), 200

@app.route("/transaccion", methods=["POST"])
def crear_transaccion():
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    producto = data.get("producto")
    
    logger.info(f'Registrando compra para usuario_id: {usuario_id} con producto: {producto}')
    
    # Simular latencia usando helper
    simular_latencia()

    # Simular éxito o fallo aleatorio usando helper
    if not tiene_exito():
        logger.warning(f'Fallo al registrar compra para usuario_id: {usuario_id}')
        # FALLO - No se pudo registrar
        return jsonify({
            "success": False,
            "error": "No se pudo registrar la compra"
        }), 409
    
    # ÉXITO - Registrar compra usando helper para generar ID
    compra_id = generar_id()
    compras_db[compra_id] = {
        "compra_id": compra_id,
        "usuario_id": usuario_id,
        "producto": producto,
        "estado": "confirmada"
    }
    logger.info(f'Compra registrada exitosamente: {compras_db[compra_id]}')
    return jsonify({
        "success": True,
        "compra_id": compra_id,
        "mensaje": "Compra registrada exitosamente"
    }), 200
    
@app.route('/compensacion', methods=['POST'])
def compensar_compra():
    data = request.get_json()
    compra_id = data.get('compra_id')
    
    if not compra_id:
        logger.warning("Compensación llamada sin compra_id")
        return jsonify({
            "success": True,
            "mensaje": "No hay compra para compensar"
        }), 200
    
    # Buscar y cancelar la compra
    if compra_id in compras_db:
        compras_db[compra_id]['estado'] = 'cancelada'
        logger.info(f"Compra {compra_id} cancelada exitosamente")
    else:
        logger.warning(f"Compra {compra_id} no encontrada (quizás ya fue cancelada)")
 
    
    return jsonify({
        "success": True,
        "mensaje": "Compra cancelada"
    }), 200

#configurar un metodo get para ver las compras registradas
@app.route("/compras", methods=["GET"])
def ver_compras(): 
    logger.info(f'Listado de compras solicitadas - Total de compras: {len(compras_db)}')
    return jsonify({"compras": list(compras_db.values()), "total": len(compras_db)}), 200



if __name__ == '__main__':
    logger.info("🚀 Iniciando ms-compras en puerto 5002...")
    logger.info("✅ Servicio listo - Health check: http://localhost:5002/health")
    app.run(host='0.0.0.0', port=5002, debug=True)