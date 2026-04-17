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


@router.get("/productos/seed")
async def force_seed():
    """Force seed products with correct tenant ID"""
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import text
    from uuid import uuid4
    
    correct_tenant = "4a7e815e-f68e-46f4-863d-1d2f786301e8"
    
    async with AsyncSessionLocal() as db:
        # Delete all products
        await db.execute(text("DELETE FROM inventario"))
        await db.execute(text("DELETE FROM productos"))
        await db.execute(text("DELETE FROM categorias"))
        await db.execute(text("DELETE FROM tenants"))
        
        # Create tenant
        await db.execute(text(f"""
            INSERT INTO tenants (id, nombre, nit, direccion, telefono, email, plan, estado)
            VALUES ('{correct_tenant}', 'Tienda Demo', '12345678901', 'Calle 123', '3001234567', 'demo@tienda.com', 'basic', 'activo')
        """))
        
        # Create category
        cat_id = str(uuid4())
        await db.execute(text(f"""
            INSERT INTO categorias (id, tenant_id, nombre, estado)
            VALUES ('{cat_id}', '{correct_tenant}', 'Bebidas y Comidas', 'activo')
        """))
        
        # Create products
        productos = [
            ("Café Americano", 2500, 50),
            ("Café Latte", 3500, 30),
            ("Te Verde", 2500, 40),
            ("Jugo Natural", 4500, 20),
            ("Sandwich", 6500, 15),
            ("Croissant", 2500, 25),
            ("Galletas", 1500, 60),
            ("Agua Mineral", 1500, 100),
            ("Gaseosa", 2000, 80),
            ("Cerveza", 4000, 48),
        ]
        
        for nombre, precio, stock in productos:
            prod_id = str(uuid4())
            await db.execute(text(f"""
                INSERT INTO productos (id, tenant_id, nombre, precio_venta, estado)
                VALUES ('{prod_id}', '{correct_tenant}', '{nombre}', {precio}, 'activo')
            """))
            await db.execute(text(f"""
                INSERT INTO inventario (id, tenant_id, producto_id, cantidad)
                VALUES ('{str(uuid4())}', '{correct_tenant}', '{prod_id}', {stock})
            """))
        
        await db.commit()
        return {"message": "Seed completed! Products created."}


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

# Create Producto
class ProductoCreate(BaseModel):
    nombre: str
    precio_venta: float
    precio_costo: float = 0.0
    stock: int = 0
    categoria_id: str = ""
    codigo: str = ""
    estado: str = "activo"


@router.post("/productos", status_code=201)
async def create_producto(producto: ProductoCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    pid = str(uuid.uuid4())
    
    await db.execute(
        text("""INSERT INTO productos (id, tenant_id, nombre, precio_venta, precio_costo, categoria_id, codigo, estado) 
              VALUES (:id, :tid, :nombre, :pv, :pc, :cat, :cod, :est)"""),
        {"id": pid, "tid": tid, "nombre": producto.nombre, "pv": producto.precio_venta, 
         "pc": producto.precio_costo, "cat": producto.categoria_id, "cod": producto.codigo, "est": producto.estado}
    )
    await db.commit()
    
    # Also add to inventario
    await db.execute(
        text("INSERT INTO inventario (id, tenant_id, producto_id, cantidad) VALUES (:id, :tid, :pid, :cant)"),
        {"id": str(uuid.uuid4()), "tid": tid, "pid": pid, "cant": producto.stock or 0}
    )
    await db.commit()
    
    return {"id": pid, "message": "Producto creado"}


# Update Producto
@router.put("/productos/{producto_id}")
async def update_producto(producto_id: str, producto: ProductoCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    
    await db.execute(
        text("""UPDATE productos SET nombre = :nombre, precio_venta = :pv, precio_costo = :pc, 
              categoria_id = :cat, codigo = :cod, estado = :est WHERE id = :id AND tenant_id = :tid"""),
        {"id": producto_id, "tid": tid, "nombre": producto.nombre, "pv": producto.precio_venta,
         "pc": producto.precio_costo, "cat": producto.categoria_id, "cod": producto.codigo, "est": producto.estado}
    )
    await db.commit()
    
    return {"message": "Producto actualizado"}


# Delete Producto
@router.delete("/productos/{producto_id}")
async def delete_producto(producto_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    
    await db.execute(text("DELETE FROM inventario WHERE producto_id = :pid AND tenant_id = :tid"), {"pid": producto_id, "tid": tid})
    await db.execute(text("DELETE FROM productos WHERE id = :id AND tenant_id = :tid"), {"id": producto_id, "tid": tid})
    await db.commit()
    
    return {"message": "Producto eliminado"}


# Create Categoria
class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    padre_id: Optional[str] = None


@router.post("/categorias", status_code=201)
async def create_categoria(categoria: CategoriaCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    cid = str(uuid.uuid4())
    
    await db.execute(
        text("INSERT INTO categorias (id, tenant_id, nombre, descripcion, padre_id, estado) VALUES (:id, :tid, :nom, :desc, :padre, 'activo')"),
        {"id": cid, "tid": tid, "nom": categoria.nombre, "desc": categoria.descripcion, "padre": categoria.padre_id}
    )
    await db.commit()
    
    return {"id": cid, "message": "Categoría creada"}


# Cleanup duplicate categories
@router.post("/categorias/cleanup")
async def cleanup_categorias(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    
    # Delete all categories and recreate clean
    await db.execute(text("DELETE FROM categorias WHERE tenant_id = :t"), {"t": tid})
    
    # Create clean categories
    cats = [
        ("Bebidas y Comidas", "b7bee82b-312f-408b-bb1e-8e5d84e491b2"),
        ("Útiles Escolares", "c7bee82b-312f-408b-bb1e-8e5d84e491b3"),
        ("Papelería", "d7bee82b-312f-408b-bb1e-8e5d84e491b4"),
        ("Artes y Manualidades", "e7bee82b-312f-408b-bb1e-8e5d84e491b5"),
        ("Tecnología", "f7bee82b-312f-408b-bb1e-8e5d84e491b6"),
    ]
    for nom, cid in cats:
        await db.execute(
            text("INSERT INTO categorias (id, tenant_id, nombre, estado) VALUES (:id, :t, :nom, 'activo')"),
            {"id": cid, "t": tid, "nom": nom}
        )
    await db.commit()
    
    return {"message": "Categorías limpiadas"}
