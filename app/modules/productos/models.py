# ============================================
# MODELS - PRODUCTOS, INVENTARIO, CAJA, CLIENTES, VENTAS
# No incluye Tenant (está en tenants/models.py)
# ============================================

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text, Index, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base
from app.modules.tenants.models import Tenant


# ============================================
# ROLES DE USUARIO
# ============================================
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    VENDEDOR = "vendedor"
    CONTADOR = "contador"
    CAJERO = "cajero"


# ============================================
# USER (Usuario)
# ============================================
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=False)
    rol = Column(String(20), default=UserRole.VENDEDOR.value)
    avatar_url = Column(String(500))
    estado = Column(String(20), default="activo")
    ultimo_login = Column(DateTime(timezone=True))
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    ventas = relationship("Venta", back_populates="vendedor", lazy="dynamic")


# ============================================
# CATEGORÍAS
# ============================================
class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    padre_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id", ondelete="SET NULL"))
    estado = Column(String(20), default="activo")
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="categorias")
    productos = relationship("Producto", back_populates="categoria", lazy="dynamic")
    padre = relationship("Categoria", remote_side=[id], backref="subcategorias")


# ============================================
# PRODUCTOS
# ============================================
class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    codigo_barras = Column(String(50), index=True)
    codigo_interno = Column(String(50))
    nombre = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id", ondelete="SET NULL"))
    
    # Precios
    precio_costo = Column(Numeric(15, 2), default=0)
    precio_venta = Column(Numeric(15, 2), nullable=False)
    precio_minimo = Column(Numeric(15, 2))
    iva = Column(Numeric(5, 2), default=19)
    
    imagen_url = Column(String(500))
    permite_stock_negativo = Column(Boolean, default=False)
    producto_servicio = Column(String(20), default="producto")
    estado = Column(String(20), default="activo")
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="productos")
    categoria = relationship("Categoria", back_populates="productos")
    inventario = relationship("Inventario", back_populates="producto", cascade="all, delete-orphan", uselist=False)
    detalles_venta = relationship("VentaDetalle", back_populates="producto", lazy="dynamic")


# ============================================
# INVENTARIO
# ============================================
class Inventario(Base):
    __tablename__ = "inventario"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    
    cantidad = Column(Numeric(15, 3), default=0)
    cantidad_comprometida = Column(Numeric(15, 3), default=0)
    stock_minimo = Column(Numeric(15, 3), default=0)
    stock = Column(Numeric(15, 3), default=0)
    ubicacion = Column(String(100))
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    producto = relationship("Producto", back_populates="inventario")
    
    # Índice compuesto
    __table_args__ = (
        Index('idx_inventario_tenant_producto', 'tenant_id', 'producto_id', unique=True),
    )


# ============================================
# MOVIMIENTOS INVENTARIO
# ============================================
class InventarioMovimiento(Base):
    __tablename__ = "inventario_movimientos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id", ondelete="CASCADE"), nullable=False, index=True)
    
    tipo = Column(String(20), nullable=False)
    cantidad = Column(Numeric(15, 3), nullable=False)
    costo_unitario = Column(Numeric(15, 2))
    documento_ref = Column(String(50))
    observaciones = Column(Text)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# ============================================
# CAJA
# ============================================
class Caja(Base):
    __tablename__ = "cajas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    estado = Column(String(20), default="cerrada")
    
    monto_inicial = Column(Numeric(15, 2), default=0)
    monto_final = Column(Numeric(15, 2))
    diferencia = Column(Numeric(15, 2))
    
    fecha_apertura = Column(DateTime(timezone=True))
    fecha_cierre = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="cajas")
    ventas = relationship("Venta", back_populates="caja", lazy="dynamic")


# ============================================
# CLIENTES
# ============================================
class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    tipo_documento = Column(String(10), nullable=False)
    documento = Column(String(20), nullable=False, index=True)
    nombre = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255))
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(Text)
    limite_credito = Column(Numeric(15, 2), default=0)
    lista_precios = Column(String(50))
    estado = Column(String(20), default="activo")
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="clientes")
    ventas = relationship("Venta", back_populates="cliente", lazy="dynamic")


# ============================================
# VENTAS
# ============================================
class Venta(Base):
    __tablename__ = "ventas"
    __table_args__ = (
        UniqueConstraint("tenant_id", "numero", name="unique_numero_por_tenant"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    numero = Column(String(20), nullable=False)
    prefijo = Column(String(10), default="FAC")
    
    caja_id = Column(UUID(as_uuid=True), ForeignKey("cajas.id", ondelete="SET NULL"))
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id", ondelete="SET NULL"))
    vendedor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    fecha = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    fecha_vencimiento = Column(DateTime(timezone=True))
    
    subtotal = Column(Numeric(15, 2), default=0)
    descuento = Column(Numeric(15, 2), default=0)
    iva = Column(Numeric(15, 2), default=0)
    total = Column(Numeric(15, 2), default=0)
    
    metodo_pago = Column(String(20), default="efectivo")
    estado = Column(String(20), default="completada")
    observaciones = Column(Text)
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="ventas")
    caja = relationship("Caja", back_populates="ventas")
    cliente = relationship("Cliente", back_populates="ventas")
    vendedor = relationship("User", back_populates="ventas")
    detalles = relationship("VentaDetalle", back_populates="venta", cascade="all, delete-orphan", lazy="dynamic")


# ============================================
# DETALLE VENTA
# ============================================
class VentaDetalle(Base):
    __tablename__ = "venta_detalles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venta_id = Column(UUID(as_uuid=True), ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id", ondelete="SET NULL"), nullable=False)
    
    descripcion = Column(String(255), nullable=False)
    cantidad = Column(Numeric(15, 3), nullable=False)
    unidad = Column(String(20), default="und")
    precio_unitario = Column(Numeric(15, 2), nullable=False)
    descuento = Column(Numeric(15, 2), default=0)
    iva = Column(Numeric(5, 2), default=19)
    subtotal = Column(Numeric(15, 2), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_venta")


# ============================================
# CONTADOR DE FACTURAS
# ============================================
class ContadorFactura(Base):
    __tablename__ = "contador_facturas"
    __table_args__ = (
        Index('idx_contador_facturas_tenant', 'tenant_id', unique=True),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True)
    contador = Column(Integer, default=1)  # <-- INTEGER, no String
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())