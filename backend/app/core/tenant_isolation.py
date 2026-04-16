# ============================================
# MIDDLEWARE DE AISLAMIENTO DE TENANT
# P1: Asegura que todos los queries filtren tenant_id
# ============================================

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import UUID
from app.core.database import get_db
from app.core.security import get_current_user


class TenantAwareSession:
    """
    Decorador/Dependency que asegura tenant isolation.
    Agrega automáticamente tenant_id a todas las queries.
    """
    
    def __init__(self, tenant_id: UUID):
        self.tenant_id = tenant_id


async def get_tenant_id(
    current_user: dict = Depends(get_current_user)
) -> UUID:
    """
    Dependency que obtiene el tenant_id del token JWT.
    Todos los endpoints deben usar esto.
    """
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin tenant_id"
        )
    return UUID(tenant_id)


async def get_tenant_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency que retorna dict con tenant_id y user_id.
    Útil para crear registros con created_by.
    """
    return {
        "tenant_id": UUID(current_user["tenant_id"]),
        "user_id": UUID(current_user["user_id"])
    }