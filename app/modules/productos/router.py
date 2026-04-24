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
    result = await db.execute(
        text("SELECT id, nombre, precio_venta, categoria_id FROM productos WHERE tenant_id = :t AND estado = 'activo'"),
        {"t": tid}
    )
    rows = result.fetchall()
    return [
        {"id": str(r[0]), "nombre": r[1], "precio_venta": float(r[2] or 0)}
        for r in rows
    ]


@router.get("/categorias")
async def get_categorias(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(
        text("SELECT id, nombre FROM categorias WHERE tenant_id = :t AND estado = 'activo'"),
        {"t": tid}
    )
    return [{"id": str(r[0]), "nombre": r[1]} for r in result.fetchall()]

# ============================================
# ADMIN SEED ENDPOINT - Temporary
# ============================================
@router.post("/seed-categorias-productos")
async def seed_categories_and_products(db: AsyncSession = Depends(get_db)):
    """Seed categories and products for testing"""
    from uuid import uuid4
    from sqlalchemy import text
    
    tenant_id = "4a7e815e-f68e-46f4-863d-1d2f786301e8"
    
    # Create categories with subcategories
    categorias_data = [
        {"nombre": "Útiles Escolares", "padre_id": None},
        {"nombre": "Papelería", "padre_id": None},
        {"nombre": "Artes y Manualidades", "padre_id": None},
        {"nombre": "Tecnología", "padre_id": None},
    ]
    
    created_cats = {}
    for cat in categorias_data:
        cat_id = str(uuid4())
        await db.execute(
            text("INSERT INTO categorias (id, tenant_id, nombre, padre_id, estado, created_at, updated_at) VALUES (:id, :tenant, :nombre, :padre, 'activo', NOW(), NOW())"),
            {"id": cat_id, "tenant": tenant_id, "nombre": cat["nombre"], "padre": cat["padre_id"]}
        )
        created_cats[cat["nombre"]] = cat_id
    
    # Create subcategories
    subcategorias = [
        {"nombre": "Cuadernos", "padre": "Útiles Escolares"},
        {"nombre": "Lápices y Colores", "padre": "Útiles Escolares"},
        {"nombre": "Carpetas", "padre": "Papelería"},
        {"nombre": "Papel Bond", "padre": "Papelería"},
        {"nombre": "Pinturas", "padre": "Artes y Manualidades"},
        {"nombre": "Pinceles", "padre": "Artes y Manualidades"},
        {"nombre": "Cables USB", "padre": "Tecnología"},
        {"nombre": "Mouse", "padre": "Tecnología"},
    ]
    
    for sub in subcategorias:
        sub_id = str(uuid4())
        await db.execute(
            text("INSERT INTO categorias (id, tenant_id, nombre, padre_id, estado, created_at, updated_at) VALUES (:id, :tenant, :nombre, :padre, 'activo', NOW(), NOW())"),
            {"id": sub_id, "tenant": tenant_id, "nombre": sub["nombre"], "padre": created_cats[sub["padre"]]}
        )
    
    # Create 20 new products
    productos_data = [
        # Útiles Escolares (5)
        {"nombre": "Cuaderno College 100 hojas", "precio_venta": 8500, "stock": 45, "cat": "Útiles Escolares"},
        {"nombre": "Lápices colores x12", "precio_venta": 12000, "stock": 30, "cat": "Útiles Escolares"},
        {"nombre": "Borrador blanco", "precio_venta": 1500, "stock": 100, "cat": "Útiles Escolares"},
        {"nombre": "Sacapuntas metálico", "precio_venta": 3500, "stock": 25, "cat": "Útiles Escolares"},
        {"nombre": "Regla 30cm", "precio_vela": 2500, "stock": 40, "cat": "Útiles Escolares"},
        # Papelería (5)
        {"nombre": "Carpeta plastificada", "precio_venta": 5500, "stock": 35, "cat": "Papelería"},
        {"nombre": "Papel Bond A4 x500", "precio_venta": 18000, "stock": 20, "cat": "Papelería"},
        {"nombre": "Clips x50", "precio_venta": 2500, "stock": 50, "cat": "Papelería"},
        {"nombre": "Grapadora", "precio_venta": 12000, "stock": 15, "cat": "Papelería"},
        {"nombre": "Tijeras escolares", "precio_venta": 4500, "stock": 25, "cat": "Papelería"},
        # Artes y Manualidades (5)
        {"nombre": "Pintura acrílica x6", "precio_venta": 15000, "stock": 18, "cat": "Artes y Manualidades"},
        {"nombre": "Pinceles pelo fino x5", "precio_venta": 8000, "stock": 22, "cat": "Artes y Manualidades"},
        {"nombre": "Cartulina colores x10", "precio_venta": 6000, "stock": 40, "cat": "Artes y Manualidades"},
        {"nombre": "Pegamento escolar", "precio_venta": 3500, "stock": 60, "cat": "Artes y Manualidades"},
        {"nombre": "Fomi colores", "precio_venta": 4000, "stock": 35, "cat": "Artes y Manualidades"},
        # Tecnología (5)
        {"nombre": "Cable USB tipo C", "precio_venta": 15000, "stock": 28, "cat": "Tecnología"},
        {"nombre": "Mouse inalámbrico", "precio_venta": 25000, "stock": 12, "cat": "Tecnología"},
        {"nombre": "Teclado USB", "precio_venta": 35000, "stock": 8, "cat": "Tecnología"},
        {"nombre": "Audífonos basic", "precio_venta": 18000, "stock": 15, "cat": "Tecnología"},
        {"nombre": "Pendrive 32GB", "precio_venta": 22000, "stock": 20, "cat": "Tecnología"},
    ]
    
    for prod in productos_data:
        prod_id = str(uuid4())
        cat_id = created_cats.get(prod["cat"])
        await db.execute(
            text("INSERT INTO productos (id, tenant_id, nombre, precio_venta, precio_costo, stock, categoria_id, estado, created_at, updated_at) VALUES (:id, :tenant, :nombre, :precio, :costo, :stock, :cat, 'activo', NOW(), NOW())"),
            {"id": prod_id, "tenant": tenant_id, "nombre": prod["nombre"], "precio": prod["precio_venta"], "costo": prod["precio_venta"]*0.5, "stock": prod["stock"], "cat": cat_id}
        )
    
    await db.commit()
    
    return {"message": f"Created {len(categorias_data)} categories, {len(subcategorias)} subcategories, and {len(productos_data)} products"}
