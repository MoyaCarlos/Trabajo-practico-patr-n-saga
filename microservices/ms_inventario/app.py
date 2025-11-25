# Inventario Flask application
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

inventario = {
    "LAPTOP": {"stock": 5, "reservado": 0},
    "MOUSE": {"stock": 10, "reservado": 0},
    "TECLADO": {"stock": 3, "reservado": 0}
}

reservas_db = {}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "ms-inventario"}), 200

@app.route("/inventario", methods=["GET"])
def obtener_inventario():
    logger.info("Inventario solicitado")
    return jsonify(inventario), 200

@app.route("/transaccion", methods=["POST"])
def reservar():
    data = request.get_json()
    producto = data.get("producto").upper()
    cantidad = data.get("cantidad", 1)

    logger.info(f"Intentando reservar {cantidad}x{producto}")

    simular_latencia()
# verifica si el producto existe
    if producto not in inventario:
        logger.warning(f"producto {producto} no encontrado")
        return jsonify({
            'Exito': False,
            'error': 'Producto no encontrado'
        }), 409

#verifica si hay stock suficiente
    stock_disponible = inventario[producto]['stock']

    if stock_disponible < cantidad:
        logger.warning(f'Stock insuficiente para {producto}. Disponible: {stock_disponible}, Requerido: {cantidad}')
        return jsonify({
            'Exito': False,
            'error': 'Stock insuficiente'
        }), 409
    
    #Caso de exito:
    reserva_id = generar_id()

    #actualizar inventario
    inventario[producto]['stock'] -= cantidad
    inventario[producto]['reservado'] += cantidad

    reservas_db[reserva_id] = {
        "reserva_id": reserva_id,
        "producto": producto,
        "cantidad": cantidad,
        "estado": "reservado"
    }

    logger.info(f'Stock reservado: {reservas_db[reserva_id]}')
    logger.info(f'Inventario actualizado - {producto}: stock={inventario[producto]["stock"]}, reservado={inventario[producto]["reservado"]}')
    
    return jsonify({
        "success": True,
        "reserva_id": reserva_id,
        "mensaje": "Stock reservado exitosamente"
    }), 200

@app.route('/compensacion', methods=['POST'])
def compensar_reserva():
    data = request.get_json()
    reserva_id = data.get('reserva_id')
    
    if not reserva_id:
        logger.warning("Compensación llamada sin reserva_id")
        return jsonify({
            "success": True,
            "mensaje": "No hay reserva para compensar"
        }), 200
    
    # Buscar y liberar la reserva
    if reserva_id in reservas_db:
        reserva = reservas_db[reserva_id]
        producto = reserva['producto']
        cantidad = reserva['cantidad']
        
        # Actualizar inventario
        inventario[producto]['stock'] += cantidad
        inventario[producto]['reservado'] -= cantidad
        
        reserva['estado'] = 'cancelada'
        logger.info(f"Reserva {reserva_id} cancelada exitosamente. Inventario actualizado - {producto}: stock={inventario[producto]['stock']}, reservado={inventario[producto]['reservado']}")
    else:
        logger.warning(f"Reserva {reserva_id} no encontrada (quizás ya fue cancelada)")
    
    return jsonify({
        "success": True,
        "mensaje": "Reserva compensada exitosamente"
    }), 200


if __name__ == '__main__':
    logger.info("🚀 Iniciando ms-inventario en puerto 5004...")
    logger.info("✅ Servicio listo - Health check: http://localhost:5004/health")
    app.run(host='0.0.0.0', port=5004, debug=True)