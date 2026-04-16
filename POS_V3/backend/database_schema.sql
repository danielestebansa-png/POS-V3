-- ============================================
-- SQL DATABASE SCHEMA - POS v3 CORREGIDO
-- Includes: Foreign keys, indices, auditoria, ContadorFacturas
-- ============================================

-- EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TENANT
-- ============================================
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(255) NOT NULL,
    nit VARCHAR(20) UNIQUE NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    logo_url VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'America/Bogota',
    plan VARCHAR(50) DEFAULT 'basic',
    estado VARCHAR(20) DEFAULT 'activo',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- USUARIOS (P1: Indices, ondelete CASCADE)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    rol VARCHAR(20) DEFAULT 'vendedor',
    avatar_url VARCHAR(500),
    estado VARCHAR(20) DEFAULT 'activo',
    ultimo_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID,
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- CATEGORÍAS (P1: ondelete CASCADE/SET NULL)
-- ============================================
CREATE TABLE IF NOT EXISTS categorias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    padre_id UUID REFERENCES categorias(id) ON DELETE SET NULL,
    estado VARCHAR(20) DEFAULT 'activo',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID
);

CREATE INDEX idx_categorias_tenant ON categorias(tenant_id);

-- ============================================
-- PRODUCTOS (P1: Indices, ondelete CASCADE)
-- ============================================
CREATE TABLE IF NOT EXISTS productos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    codigo_barras VARCHAR(50),
    codigo_interno VARCHAR(50),
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    categoria_id UUID REFERENCES categorias(id) ON DELETE SET NULL,
    precio_costo NUMERIC(15,2) DEFAULT 0,
    precio_venta NUMERIC(15,2) NOT NULL,
    precio_minimo NUMERIC(15,2),
    iva NUMERIC(5,2) DEFAULT 19,
    imagen_url VARCHAR(500),
    permite_stock_negativo BOOLEAN DEFAULT FALSE,
    producto_servicio VARCHAR(20) DEFAULT 'producto',
    estado VARCHAR(20) DEFAULT 'activo',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID
);

CREATE INDEX idx_productos_tenant ON productos(tenant_id);
CREATE INDEX idx_productos_codigo_barras ON productos(codigo_barras);
CREATE INDEX idx_productos_nombre ON productos(nombre);
CREATE UNIQUE INDEX idx_productos_tenant_codigo ON productos(tenant_id, codigo_barras) WHERE codigo_barras IS NOT NULL;

-- ============================================
-- INVENTARIO (P1: Índice único compuesto)
-- ============================================
CREATE TABLE IF NOT EXISTS inventario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    cantidad NUMERIC(15,3) DEFAULT 0,
    cantidad_comprometida NUMERIC(15,3) DEFAULT 0,
    stock_minimo NUMERIC(15,3) DEFAULT 0,
    ubicacion VARCHAR(100),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, producto_id)
);

CREATE INDEX idx_inventario_producto ON inventario(producto_id);

-- ============================================
-- MOVIMIENTOS INVENTARIO (P0: Auditoría)
-- ============================================
CREATE TABLE IF NOT EXISTS inventario_movimientos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    producto_id UUID NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    tipo VARCHAR(20) NOT NULL,
    cantidad NUMERIC(15,3) NOT NULL,
    costo_unitario NUMERIC(15,2),
    documento_ref VARCHAR(50),
    observaciones TEXT,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_inv_mov_tenant_fecha ON inventario_movimientos(tenant_id, created_at);
CREATE INDEX idx_inv_mov_producto ON inventario_movimientos(producto_id);

-- ============================================
-- CAJAS
-- ============================================
CREATE TABLE IF NOT EXISTS cajas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    estado VARCHAR(20) DEFAULT 'cerrada',
    monto_inicial NUMERIC(15,2) DEFAULT 0,
    monto_final NUMERIC(15,2),
    diferencia NUMERIC(15,2),
    fecha_apertura TIMESTAMPTZ,
    fecha_cierre TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cajas_tenant ON cajas(tenant_id);

-- ============================================
-- CLIENTES
-- ============================================
CREATE TABLE IF NOT EXISTS clientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    tipo_documento VARCHAR(10) NOT NULL,
    documento VARCHAR(20) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    limite_credito NUMERIC(15,2) DEFAULT 0,
    lista_precios VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'activo',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID,
    UNIQUE(tenant_id, documento)
);

CREATE INDEX idx_clientes_tenant ON clientes(tenant_id);
CREATE INDEX idx_clientes_documento ON clientes(documento);

-- ============================================
-- VENTAS
-- ============================================
CREATE TABLE IF NOT EXISTS ventas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    numero VARCHAR(20) NOT NULL,
    prefijo VARCHAR(10) DEFAULT 'FAC',
    caja_id UUID REFERENCES cajas(id) ON DELETE SET NULL,
    cliente_id UUID REFERENCES clientes(id) ON DELETE SET NULL,
    vendedor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    fecha TIMESTAMPTZ DEFAULT NOW(),
    fecha_vencimiento TIMESTAMPTZ,
    subtotal NUMERIC(15,2) DEFAULT 0,
    descuento NUMERIC(15,2) DEFAULT 0,
    iva NUMERIC(15,2) DEFAULT 0,
    total NUMERIC(15,2) DEFAULT 0,
    metodo_pago VARCHAR(20) DEFAULT 'efectivo',
    estado VARCHAR(20) DEFAULT 'completada',
    observaciones TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, numero)
);

CREATE INDEX idx_ventas_tenant_fecha ON ventas(tenant_id, fecha);
CREATE INDEX idx_ventas_caja ON ventas(caja_id);
CREATE INDEX idx_ventas_cliente ON ventas(cliente_id);

-- ============================================
-- DETALLE VENTA
-- ============================================
CREATE TABLE IF NOT EXISTS venta_detalles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venta_id UUID NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id UUID REFERENCES productos(id) ON DELETE SET NULL,
    descripcion VARCHAR(255) NOT NULL,
    cantidad NUMERIC(15,3) NOT NULL,
    unidad VARCHAR(20) DEFAULT 'und',
    precio_unitario NUMERIC(15,2) NOT NULL,
    descuento NUMERIC(15,2) DEFAULT 0,
    iva NUMERIC(5,2) DEFAULT 19,
    subtotal NUMERIC(15,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_venta_detalles_venta ON venta_detalles(venta_id);

-- ============================================
-- CONTADOR FACTURAS (P0: Evitar duplicados)
-- ============================================
CREATE TABLE IF NOT EXISTS contador_facturas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE UNIQUE,
    contador INTEGER DEFAULT 1,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);