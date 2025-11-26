"""
Servicio de orquestación usando patrón Saga
"""
import logging
import requests
import time
from typing import Dict, Tuple, List, Optional

from config import (
    MS_CATALOGO_URL,
    MS_COMPRAS_URL,
    MS_PAGOS_URL,
    MS_INVENTARIO_URL,
    MSG_SAGA_EXITOSA,
    MSG_SAGA_FALLIDA,
    DELAY_ENTRE_PASOS
)

logger = logging.getLogger(__name__)


class SagaOrchestrator:
    """Orquestador del patrón Saga para coordinar microservicios"""
    
    def __init__(self):
        # Almacena los IDs de transacciones exitosas para compensar si falla algo
        self.transacciones_exitosas: Dict[str, str] = {}
    
    def ejecutar_saga(self, usuario_id: str) -> Tuple[Dict, int]:
        """
        Ejecuta la saga completa: Catalogo → Compras → Pagos → Inventario
        
        Flujo:
        1. Obtener producto del catálogo
        2. Crear compra
        3. Procesar pago
        4. Reservar inventario
        
        Si algún paso falla (409), ejecuta compensaciones en orden inverso
        
        Args:
            usuario_id: ID del usuario que realiza la compra
            
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """
        logger.info(f"🎬 Iniciando Saga para usuario {usuario_id}")
        self.transacciones_exitosas = {}  # Reset
        
        try:
            # PASO 1: Obtener producto del catálogo
            logger.info("⏳ Paso 1/4: Consultando catálogo...")
            producto = self._llamar_catalogo()
            if not producto:
                return {"success": False, "error": "Catálogo no disponible"}, 500
            
            logger.info(f"✅ Paso 1/4: Producto obtenido - {producto['nombre']} (${producto['precio']})")
            time.sleep(DELAY_ENTRE_PASOS)
            
            # PASO 2: Crear compra
            logger.info("⏳ Paso 2/4: Creando compra...")
            compra_result = self._llamar_compras(usuario_id, producto['nombre'])
            if not compra_result:
                logger.error("❌ Paso 2/4: Fallo al crear compra")
                # No hay compensación (catálogo es read-only)
                return {"success": False, "error": "Fallo al crear compra"}, 409
            
            self.transacciones_exitosas['compra_id'] = compra_result['compra_id']
            logger.info(f"✅ Paso 2/4: Compra creada - ID: {compra_result['compra_id']}")
            time.sleep(DELAY_ENTRE_PASOS)
            
            # PASO 3: Procesar pago
            logger.info("⏳ Paso 3/4: Procesando pago...")
            pago_result = self._llamar_pagos(usuario_id, producto['precio'], compra_result['compra_id'])
            if not pago_result:
                logger.error("❌ Paso 3/4: Fallo al procesar pago")
                # FALLO: Compensar compra
                self._ejecutar_compensaciones(['compras'])
                return {"success": False, "error": MSG_SAGA_FALLIDA}, 409
            
            self.transacciones_exitosas['pago_id'] = pago_result['pago_id']
            logger.info(f"✅ Paso 3/4: Pago procesado - ID: {pago_result['pago_id']}")
            time.sleep(DELAY_ENTRE_PASOS)
            
            # PASO 4: Reservar inventario
            logger.info("⏳ Paso 4/4: Reservando inventario...")
            reserva_result = self._llamar_inventario(producto['nombre'])
            if not reserva_result:
                logger.error("❌ Paso 4/4: Fallo al reservar inventario")
                # FALLO: Compensar pagos y compras (orden inverso)
                self._ejecutar_compensaciones(['pagos', 'compras'])
                return {"success": False, "error": MSG_SAGA_FALLIDA}, 409
            
            self.transacciones_exitosas['reserva_id'] = reserva_result['reserva_id']
            logger.info(f"✅ Paso 4/4: Inventario reservado - ID: {reserva_result['reserva_id']}")
            
            # ✅ SAGA EXITOSA
            logger.info("🎉 Saga completada exitosamente")
            return {
                "success": True,
                "mensaje": MSG_SAGA_EXITOSA,
                "datos": {
                    "producto": producto,
                    "compra_id": compra_result['compra_id'],
                    "pago_id": pago_result['pago_id'],
                    "reserva_id": reserva_result['reserva_id']
                }
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Error inesperado en Saga: {e}")
            self._ejecutar_compensaciones(['pagos', 'compras'])
            return {"success": False, "error": "Error interno del servidor"}, 500
    
    def _llamar_catalogo(self) -> Optional[Dict]:
        """Llama al microservicio de catálogo para obtener un producto"""
        try:
            response = requests.get(f"{MS_CATALOGO_URL}/producto", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error llamando a catálogo: {e}")
        return None
    
    def _llamar_compras(self, usuario_id: str, producto: str) -> Optional[Dict]:
        """Crea una compra"""
        try:
            response = requests.post(
                f"{MS_COMPRAS_URL}/transaccion",
                json={"usuario_id": usuario_id, "producto": producto},
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error llamando a compras: {e}")
        return None
    
    def _llamar_pagos(self, usuario_id: str, monto: float, compra_id: str) -> Optional[Dict]:
        """Procesa un pago"""
        try:
            response = requests.post(
                f"{MS_PAGOS_URL}/transaccion",
                json={"usuario_id": usuario_id, "monto": monto, "compra_id": compra_id},
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error llamando a pagos: {e}")
        return None
    
    def _llamar_inventario(self, producto: str) -> Optional[Dict]:
        """Reserva inventario"""
        try:
            response = requests.post(
                f"{MS_INVENTARIO_URL}/transaccion",
                json={"producto": producto, "cantidad": 1},
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error llamando a inventario: {e}")
        return None
    
    def _ejecutar_compensaciones(self, servicios: List[str]):
        """
        Ejecuta compensaciones en orden inverso
        
        Args:
            servicios: Lista de servicios a compensar en orden ['pagos', 'compras']
        """
        logger.warning(f"⚠️  Ejecutando compensaciones para: {servicios}")
        time.sleep(DELAY_ENTRE_PASOS)
        
        for servicio in servicios:
            if servicio == 'pagos' and 'pago_id' in self.transacciones_exitosas:
                logger.info(f"↩️  Compensando pago {self.transacciones_exitosas['pago_id']}...")
                self._compensar_pago(self.transacciones_exitosas['pago_id'])
                time.sleep(DELAY_ENTRE_PASOS)
            
            elif servicio == 'compras' and 'compra_id' in self.transacciones_exitosas:
                logger.info(f"↩️  Compensando compra {self.transacciones_exitosas['compra_id']}...")
                self._compensar_compra(self.transacciones_exitosas['compra_id'])
                time.sleep(DELAY_ENTRE_PASOS)
    
    def _compensar_pago(self, pago_id: str):
        """Compensa (reembolsa) un pago"""
        try:
            response = requests.post(
                f"{MS_PAGOS_URL}/compensacion",
                json={"pago_id": pago_id},
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"✅ Pago {pago_id} compensado exitosamente")
        except Exception as e:
            logger.error(f"Error compensando pago: {e}")
    
    def _compensar_compra(self, compra_id: str):
        """Compensa (cancela) una compra"""
        try:
            response = requests.post(
                f"{MS_COMPRAS_URL}/compensacion",
                json={"compra_id": compra_id},
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"✅ Compra {compra_id} compensada exitosamente")
        except Exception as e:
            logger.error(f"Error compensando compra: {e}")