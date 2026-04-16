# ============================================
# TENANTS ROUTER
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID
from app.core.database import get_db, get_sync_db
from app.core.security import get_current_user

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================

class TenantCreate(BaseModel):
    nombre: str
    nit: str
    direccion: str = None
    telefono: str = None
    email: str = None


class TenantResponse(BaseModel):
    id: str
    nombre: str
    nit: str
    plan: str
    
    class Config:
        from_attributes = True


# ============================================
# ENDPOINTS
# ============================================

@router.get("/")
async def get_tenants(current_user: dict = Depends(get_current_user)):
    """Get current tenant info"""
    return {
        "id": current_user["tenant_id"],
        "mensaje": "Este es tu empresa/tenant"
    }


@router.post("/", response_model=TenantResponse)
async def create_tenant(
    tenant: TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear nuevo tenant (empresa) - Público"""
    from app.modules.tenants.models import Tenant
    
    nuevo = Tenant(
        nombre=tenant.nombre,
        nit=tenant.nit,
        direccion=tenant.direccion,
        telefono=tenant.telefono,
        email=tenant.email,
        estado="activo"
    )
    
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    
    return nuevo