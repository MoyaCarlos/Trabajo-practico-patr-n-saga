# Instrucciones de Uso - Patrón Saga

## 🚀 Iniciar los Servicios

### Linux/Mac
```bash
./start_services.sh
```

### Windows CMD
```cmd
start_services.bat
```

### Windows PowerShell
```powershell
.\start_services.ps1
```

> **Nota:** En PowerShell, si aparece error de permisos, ejecuta primero:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## 🧪 Probar el Sistema

### 1. Health Checks (verificar que todos los servicios estén activos)

```bash
# Orchestrator
curl http://localhost:5000/health

# Catálogo
curl http://localhost:5001/health

# Compras
curl http://localhost:5002/health

# Pagos
curl http://localhost:5003/health

# Inventario
curl http://localhost:5004/health
```

**Respuesta esperada:**
```json
{"status": "ok", "service": "nombre-del-servicio"}
```

---

### 2. Realizar una Compra (Saga Completa)

```bash
curl -X POST http://localhost:5000/compra \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "user123", "producto": "Laptop", "monto": 1500.00}'
```

**Casos posibles:**

#### ✅ Éxito (Saga completa)
```json
{
  "success": true,
  "mensaje": "Saga completada exitosamente",
  "detalles": {
    "producto": "Laptop Gamer",
    "precio": 1200.0,
    "compra_id": "abc-123",
    "pago_id": "xyz-789",
    "reserva_id": "def-456"
  }
}
```

#### ❌ Fallo con Compensación
```json
{
  "success": false,
  "error": "Fallo en el paso de pagos",
  "compensaciones": ["compras"],
  "mensaje": "La transacción ha sido revertida"
}
```

---

### 3. Consultar Estado de los Servicios

#### Ver Inventario Disponible
```bash
curl http://localhost:5004/inventario
```

**Respuesta:**
```json
{
  "LAPTOP": {"nombre": "Laptop Gamer", "precio": 1200.0, "stock": 5, "reservado": 0},
  "MOUSE": {"nombre": "Mouse Inalámbrico", "precio": 25.99, "stock": 10, "reservado": 0},
  "TECLADO": {"nombre": "Teclado Mecánico", "precio": 89.99, "stock": 3, "reservado": 0},
  "AURICULARES": {"nombre": "Auriculares Bluetooth", "precio": 59.99, "stock": 15, "reservado": 0},
  "MONITOR": {"nombre": "Monitor 27 pulgadas", "precio": 350.0, "stock": 8, "reservado": 0}
}
```

#### Ver Compras Activas
```bash
curl http://localhost:5002/compras
```

**Respuesta:**
```json
{
  "compras": [
    {
      "compra_id": "abc-123",
      "usuario_id": "user123",
      "producto": "Laptop Gamer",
      "estado": "confirmada"
    }
  ],
  "total_activas": 1,
  "total_general": 3
}
```

#### Ver Pagos Registrados
```bash
curl http://localhost:5003/pagos
```

**Respuesta:**
```json
{
  "pagos": [
    {
      "pago_id": "xyz-789",
      "usuario_id": "user123",
      "monto": 1200.0,
      "compra_id": "abc-123",
      "estado": "aprobado",
      "fecha": "2025-11-26T10:30:45.123456"
    }
  ],
  "total": 1
}
```

---

### 4. Probar Compensaciones (ejecutar varias veces)

```bash
# Ejecuta este comando múltiples veces para ver tanto éxitos como fallos
curl -X POST http://localhost:5000/compra \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "user456", "producto": "Mouse", "monto": 25.99}'
```

> **Nota:** El sistema tiene una probabilidad del 50% de fallo en compras y pagos. 
> Ejecuta varias veces para observar:
> - ✅ Transacciones exitosas
> - ❌ Fallos con compensaciones automáticas

---

## 📊 Observar los Logs

Los logs se muestran en tiempo real en la consola donde ejecutaste el script de inicio.

**Ejemplo de logs exitosos:**
```
🎬 Iniciando Saga para usuario user123
⏳ Paso 1/4: Consultando catálogo...
✅ Paso 1/4: Producto obtenido - Laptop Gamer ($1200.0)
⏳ Paso 2/4: Creando compra...
✅ Paso 2/4: Compra creada - ID: abc-123
⏳ Paso 3/4: Procesando pago...
✅ Paso 3/4: Pago procesado - ID: xyz-789
⏳ Paso 4/4: Reservando inventario...
✅ Paso 4/4: Inventario reservado - ID: def-456
🎉 Saga completada exitosamente
```

**Ejemplo de logs con compensación:**
```
🎬 Iniciando Saga para usuario user123
⏳ Paso 1/4: Consultando catálogo...
✅ Paso 1/4: Producto obtenido - Mouse Inalámbrico ($25.99)
⏳ Paso 2/4: Creando compra...
✅ Paso 2/4: Compra creada - ID: abc-123
⏳ Paso 3/4: Procesando pago...
❌ Paso 3/4: Fallo al procesar pago
⚠️  Ejecutando compensaciones para: ['compras']
↩️  Compensando compra abc-123...
✅ Compra abc-123 compensada exitosamente
```

---

## 🛑 Detener los Servicios

Presiona **Ctrl+C** en la terminal donde se están ejecutando los servicios.

---

## ⚙️ Configuración de Workers

- **Orchestrator**: 4 workers (maneja más carga)
- **Microservicios**: 2 workers cada uno

Los workers permiten procesar múltiples requests simultáneamente, aprovechando el paralelismo a nivel de proceso.

---

## 🔍 Troubleshooting

### Los servicios no inician
- Verifica que los puertos 5000-5004 no estén ocupados
- Asegúrate de tener las dependencias instaladas: `uv sync` o `pip install -r requirements.txt`

### Error "No module named 'granian'"
```bash
pip install granian>=1.0.0
```

### Los servicios se detienen inmediatamente
- Verifica que el entorno virtual esté activado
- Revisa los logs para identificar errores de importación
