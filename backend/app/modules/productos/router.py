# ============================================
# PRODUCTOS ROUTER
# ============================================

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()


class ProductoResponse(BaseModel):
    id: str
    nombre: str
    precio_venta: float


@router.get("/productos")
async def get_productos(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    tid = current_user["tenant_id"]
    
    # Debug: log the tenant_id
    print(f"DEBUG: tenant_id = {tid}")
    
    # First check if tenant exists
    tenant_check = await db.execute(
        text("SELECT COUNT(*) FROM tenants WHERE id = :t"),
        {"t": tid}
    )
    tenant_count = tenant_check.scalar()
    print(f"DEBUG: Tenant exists: {tenant_count}")
    
    # Check products table
    prod_check = await db.execute(
        text("SELECT COUNT(*) FROM productos WHERE tenant_id = :t"),
        {"t": tid}
    )
    prod_count = prod_check.scalar()
    print(f"DEBUG: Products count: {prod_count}")
    
    result = await db.execute(
        text("""
            SELECT p.id, p.nombre, p.precio_venta, COALESCE(i.cantidad, 0) as stock 
            FROM productos p 
            LEFT JOIN inventario i ON i.producto_id = p.id 
            WHERE p.tenant_id = :t AND p.estado = 'activo'
            ORDER BY p.nombre
        """),
        {"t": tid}
    )
    rows = result.fetchall()
    products = [
        {"id": str(r[0]), "nombre": r[1], "precio_venta": float(r[2] or 0), "stock": int(r[3] or 0)}
        for r in rows
    ]
    print(f"DEBUG: Found {len(products)} products")
    return products


@router.get("/categorias")
async def get_categorias(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(
        text("SELECT id, nombre FROM categorias WHERE tenant_id = :t AND estado = 'activo'"),
        {"t": tid}
    )
    return [{"id": str(r[0]), "nombre": r[1]} for r in result.fetchall()]