# ============================================
# MODELS - TENANT (Empresa)
# ============================================

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    nit = Column(String(20), unique=True, nullable=False)
    direccion = Column(Text)
    telefono = Column(String(20))
    email = Column(String(100))
    logo_url = Column(String(500))
    timezone = Column(String(50), default="America/Bogota")
    plan = Column(String(50), default="basic")
    estado = Column(String(20), default="activo")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    productos = relationship("Producto", back_populates="tenant", cascade="all, delete-orphan")
    categorias = relationship("Categoria", back_populates="tenant", cascade="all, delete-orphan")
    clientes = relationship("Cliente", back_populates="tenant", cascade="all, delete-orphan")
    ventas = relationship("Venta", back_populates="tenant", cascade="all, delete-orphan")
    cajas = relationship("Caja", back_populates="tenant", cascade="all, delete-orphan")