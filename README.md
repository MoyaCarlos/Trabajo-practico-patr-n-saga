# uv
## Instalación
1. Abrir **consola de PowerShell como administrador**.  
2. Instalar `uv`:
```
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
3. Reiniciar la PC.
## Crear Proyecto
```
uv init nombre-proyecto
uv init # si el proyecto ya existe
```

## Instalación de Envtorno Virtual venv
```
uv venv
```

## Agregar dependencias 
```
uv add flask==3.1.2
```
## Sincronizar dependencias 
```
uv sync
```
## Documentación
[Referencia: https://docs.astral.sh/uv/getting-started/first-steps/]

# Patrón Saga - Microservicios

Implementación del patrón Saga con orquestación centralizada para gestión de transacciones distribuidas.

## 🏗️ Arquitectura

El proyecto consta de 5 servicios:
- **Orchestrator** (puerto 5000): Coordina la saga y maneja compensaciones
- **Catálogo** (puerto 5001): Gestión de productos
- **Compras** (puerto 5002): Registro de órdenes de compra
- **Pagos** (puerto 5003): Procesamiento de pagos
- **Inventario** (puerto 5004): Gestión de stock y reservas

## 🚀 Instalación

### 1. Instalar dependencias

Con `uv` (recomendado):
```bash
uv sync
```

O con `pip`:
```bash
pip install -r requirements.txt
```

## 🎯 Ejecución

### Modo Producción (Recomendado - con Granian)

Granian es un servidor WSGI de alto rendimiento escrito en Rust que permite ejecutar múltiples workers para manejar concurrencia.

**Opción 1: Script automático**
```bash
./start_services.sh
```

**Opción 2: Servicios individuales**
```bash
# Orchestrator (4 workers)
granian --interface wsgi --host 0.0.0.0 --port 5000 --workers 4 orchestrator.app:app

# Catálogo (2 workers)
granian --interface wsgi --host 0.0.0.0 --port 5001 --workers 2 ms_catalogo.app:app

# Compras (2 workers)
granian --interface wsgi --host 0.0.0.0 --port 5002 --workers 2 ms_compras.app:app

# Pagos (2 workers)
granian --interface wsgi --host 0.0.0.0 --port 5003 --workers 2 ms_pagos.app:app

# Inventario (2 workers)
granian --interface wsgi --host 0.0.0.0 --port 5004 --workers 2 ms_inventario.app:app
```

### Modo Desarrollo (sin Granian)

Para desarrollo y debugging, puedes ejecutar cada servicio directamente con Python:

```bash
# En terminales separadas
python ms_catalogo/app.py
python ms_compras/app.py
python ms_pagos/app.py
python ms_inventario/app.py
python orchestrator/app.py
```

## 📊 Configuración de Workers

- **Orchestrator**: 4 workers (maneja más carga al coordinar todas las transacciones)
- **Microservicios**: 2 workers cada uno (suficiente para operaciones individuales)

Los servicios utilizan `threading.Lock()` para garantizar seguridad en operaciones concurrentes cuando se ejecutan con múltiples workers.

## 🧪 Probar el Sistema

```bash
# Health check de todos los servicios
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5004/health

# Realizar una compra (Saga completa)
curl -X POST http://localhost:5000/compra \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "user123", "producto": "Laptop", "monto": 1500.00}'
```

## 🗄️ Base de Datos (Opcional)

El proyecto incluye soporte para PostgreSQL con Docker:

```bash
# Iniciar PostgreSQL
docker-compose up -d

# Verificar logs
docker logs saga-postgres
```

La base de datos se inicializa automáticamente con el esquema en `init-db.sql`.

## 📚 Documentación Adicional

### Granian
Servidor HTTP de **alto rendimiento escrito en Rust** para **aplicaciones Python**. Soporta los estándares **ASGI, RSGI y WSGI**.

**Documentación**: https://github.com/emmett-framework/granian


