# ============================================
# TENANT QUERY HELPER - P3
# Aislamiento automático de tenant para TODAS las queries
# ============================================

from uuid import UUID
from typing import Optional, TypeVar, Type
from sqlalchemy import and_, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

# Tipo genérico para modelos
T = TypeVar('T')


class TenantQueryMixin:
    """
    Mixin que proporciona métodos de query con aislamiento automático de tenant.
    
    Uso en modelos:
        class Producto(Base, TenantQueryMixin):
            ...
        
        # Query automático con tenant:
        productos = await Producto.get_by_tenant(session, tenant_id)
    """
    
    __tenant_id__: str = "tenant_id"  # Nombre del campo de tenant
    
    @classmethod
    async def get_by_tenant(
        cls,
        db: AsyncSession,
        tenant_id: UUID,
        filters: Optional[list] = None
    ):
        """
        Obtiene todos los registros para un tenant específico.
        
        Args:
            db: Sesión de base de datos
            tenant_id: ID del tenant
            filters: Filtros adicionales (opcional)
            
        Returns:
            Lista de registros
        """
        from sqlalchemy import select
        
        tenant_field = getattr(cls, cls.__tenant_id__, None)
        if not tenant_field:
            raise ValueError(f"Modelo {cls.__name__} no tiene campo tenant_id")
        
        query = select(cls).where(tenant_field == tenant_id)
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @classmethod
    async def get_by_id_tenant(
        cls,
        db: AsyncSession,
        tenant_id: UUID,
        record_id: UUID
    ):
        """
        Obtiene un registro específico verificando tenant_id.
        
        Args:
            db: Sesión de base de datos
            tenant_id: ID del tenant
            record_id: ID del registro
            
        Returns:
            Registro o None
        """
        from sqlalchemy import select
        
        tenant_field = getattr(cls, cls.__tenant_id__, None)
        id_field = getattr(cls, "id", None)
        
        query = select(cls).where(
            and_(
                tenant_field == tenant_id,
                id_field == record_id
            )
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()


def tenant_filter(model_class, tenant_id: UUID, extra_filters: Optional[list] = None):
    """
    Función auxiliar para crear filtros de tenant.
    
    Uso directo en queries:
        query = select(Producto).where(
            tenant_filter(Producto, tenant_id)
        )
    
    Args:
        model_class: Clase del modelo SQLAlchemy
        tenant_id: ID del tenant
        extra_filters: Filtros adicionales (opcional)
        
    Returns:
        Condición WHERE para filtrar por tenant
    """
    from sqlalchemy import and_
    
    tenant_field = getattr(model_class, "tenant_id", None)
    if not tenant_field:
        raise ValueError(f"Modelo {model_class.__name__} no tiene campo tenant_id")
    
    filters = [tenant_field == tenant_id]
    
    if extra_filters:
        filters.extend(extra_filters)
    
    return and_(*filters)


# ============================================
# EJEMPLO DE USO EN MODELO
# ============================================
"""
# En modelos.py, añadir el mixin:

from app.core.tenant_query import TenantQueryMixin

class Producto(Base, TenantQueryMixin):
    __tablename__ = "productos"
    __tenant_id__ = "tenant_id"  # Campo que define el tenant
    ...

# Luego en router:
async def get_productos(...):
    # En lugar de:
    result = await db.execute(
        select(Producto).where(Producto.tenant_id == tenant_id)
    )
    
    # Puedes usar:
    productos = await Producto.get_by_tenant(db, tenant_id)
    
    # O con filtros:
    productos = await Producto.get_by_tenant(
        db, tenant_id,
        filters=[Producto.categoria_id == categoria_id]
    )
"""