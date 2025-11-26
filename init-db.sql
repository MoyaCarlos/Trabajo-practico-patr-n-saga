-- Tabla de compras
CREATE TABLE IF NOT EXISTS compras (
    compra_id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(100) NOT NULL,
    producto VARCHAR(200) NOT NULL,
    estado VARCHAR(20) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de pagos
CREATE TABLE IF NOT EXISTS pagos (
    pago_id VARCHAR(36) PRIMARY KEY,
    usuario_id VARCHAR(100) NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    compra_id VARCHAR(36) NOT NULL,
    estado VARCHAR(20) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (compra_id) REFERENCES compras(compra_id)
);

-- Tabla de inventario
CREATE TABLE IF NOT EXISTS inventario (
    producto VARCHAR(50) PRIMARY KEY,
    stock INTEGER NOT NULL DEFAULT 0,
    reservado INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar inventario inicial
INSERT INTO inventario (producto, stock, reservado) VALUES
    ('LAPTOP', 5, 0),
    ('MOUSE', 10, 0),
    ('TECLADO', 3, 0),
    ('AURICULARES', 15, 0),
    ('MONITOR', 8, 0)
ON CONFLICT (producto) DO NOTHING;

-- Tabla de reservas
CREATE TABLE IF NOT EXISTS reservas (
    reserva_id VARCHAR(36) PRIMARY KEY,
    producto VARCHAR(50) NOT NULL,
    cantidad INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto) REFERENCES inventario(producto)
);

-- Índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_compras_usuario ON compras(usuario_id);
CREATE INDEX IF NOT EXISTS idx_compras_estado ON compras(estado);
CREATE INDEX IF NOT EXISTS idx_pagos_compra ON pagos(compra_id);
CREATE INDEX IF NOT EXISTS idx_pagos_estado ON pagos(estado);
CREATE INDEX IF NOT EXISTS idx_reservas_producto ON reservas(producto);
CREATE INDEX IF NOT EXISTS idx_reservas_estado ON reservas(estado);
