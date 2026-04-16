# ============================================
# CLIENTES ROUTER
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.productos.models import Cliente

router = APIRouter()


# ============================================
# SCHEMAS
# ============================================

class ClienteCreate(BaseModel):
    tipo_documento: str  # CC, NIT, CE
    documento: str
    nombre: str
    nombre_comercial: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    limite_credito: float = 0


class ClienteResponse(BaseModel):
    id: str
    tipo_documento: str
    documento: str
    nombre: str
    telefono: Optional[str]
    email: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================
# ENDPOINTS
# ============================================

@router.get("/", response_model=List[ClienteResponse])
async def get_clientes(
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Cliente).where(
        and_(Cliente.tenant_id == current_user["tenant_id"], Cliente.estado == "activo")
    )
    
    if search:
        search = f"%{search}%"
        query = query.where(
            (Cliente.nombre.ilike(search)) |
            (Cliente.documento.ilike(search)) |
            (Cliente.telefono.ilike(search))
        )
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def get_cliente(
    cliente_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Cliente).where(
            and_(
                Cliente.id == cliente_id,
                Cliente.tenant_id == current_user["tenant_id"]
            )
        )
    )
    cliente = result.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return cliente


@router.post("/", response_model=ClienteResponse, status_code=201)
async def create_cliente(
    cliente: ClienteCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verificar documento único
    result = await db.execute(
        select(Cliente).where(
            and_(
                Cliente.tenant_id == current_user["tenant_id"],
                Cliente.documento == cliente.documento
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Cliente con este documento ya existe")
    
    nuevo_cliente = Cliente(
        tenant_id=current_user["tenant_id"],
        tipo_documento=cliente.tipo_documento,
        documento=cliente.documento,
        nombre=cliente.nombre,
        nombre_comercial=cliente.nombre_comercial,
        telefono=cliente.telefono,
        email=cliente.email,
        direccion=cliente.direccion,
        limite_credito=cliente.limite_credito,
        estado="activo"
    )
    
    db.add(nuevo_cliente)
    await db.commit()
    await db.refresh(nuevo_cliente)
    
    return nuevo_cliente