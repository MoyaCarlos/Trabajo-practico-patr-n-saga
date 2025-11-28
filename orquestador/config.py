"""
Configuración del orquestador
"""

# Puerto del orquestador
PORT = 5000
HOST = '0.0.0.0'
SERVICE_NAME = "orchestrator"
LOG_LEVEL = "INFO"

# URLs de los microservicios
MS_CATALOGO_URL = "http://localhost:5001"
MS_COMPRAS_URL = "http://localhost:5002"
MS_PAGOS_URL = "http://localhost:5003"
MS_INVENTARIO_URL = "http://localhost:5004"

# Mensajes
MSG_SAGA_EXITOSA = "Compra procesada exitosamente"
MSG_SAGA_FALLIDA = "Error al procesar la compra - Compensaciones ejecutadas"

# Delay entre pasos (en segundos)
DELAY_ENTRE_PASOS = 2
