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

# Get tenant settings
@router.get("/configuracion")
async def get_config(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    
    result = await db.execute(
        text("SELECT id, nombre, nit, direccion, telefono, email, timezone, plan, estado FROM tenants WHERE id = :tid"),
        {"tid": tid}
    )
    row = result.fetchone()
    
    if not row:
        return {"error": "Tenant no encontrado"}
    
    return {
        "id": str(row[0]),
        "nombre": row[1],
        "nit": row[2],
        "direccion": row[3],
        "telefono": row[4],
        "email": row[5],
        "timezone": row[6],
        "plan": row[7],
        "estado": row[8]
    }


# Update tenant settings
class TenantUpdate(BaseModel):
    nombre: str = ""
    nit: str = ""
    direccion: str = ""
    telefono: str = ""
    email: str = ""
    timezone: str = "America/Bogota"


@router.put("/configuracion")
async def update_config(config: TenantUpdate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    
    # Only update non-empty fields
    await db.execute(
        text("""UPDATE tenants SET 
              nombre = COALESCE(NULLIF(:nombre, ''), nombre),
              nit = COALESCE(NULLIF(:nit, ''), nit),
              direccion = COALESCE(NULLIF(:direccion, ''), direccion),
              telefono = COALESCE(NULLIF(:telefono, ''), telefono),
              email = COALESCE(NULLIF(:email, ''), email),
              updated_at = NOW()
              WHERE id = :tid"""),
        {"tid": tid, "nombre": config.nombre, "nit": config.nit, "direccion": config.direccion, 
         "telefono": config.telefono, "email": config.email}
    )
    await db.commit()
    
    return {"message": "Configuración actualizada"}


