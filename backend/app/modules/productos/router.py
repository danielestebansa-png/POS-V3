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
            SELECT p.id, p.nombre, p.precio_venta, COALESCE(i.cantidad, 0) as stock, p.categoria_id 
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


@router.get("/subcategorias")
async def get_subcategorias(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtener todas las subcategorías con su jerarquía"""
    tid = current_user["tenant_id"]
    
    result = await db.execute(
        text("""
            SELECT id, nombre, padre_id 
            FROM categorias 
            WHERE tenant_id = :t AND estado = 'activo'
            ORDER BY nombre
        """),
        {"t": tid}
    )
    cats = result.fetchall()
    return [{"id": c[0], "nombre": c[1], "padre_id": c[2]} for c in cats]

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


@router.put("/categorias")
async def update_categoria(
    categoria: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualizar una categoría existente"""
    tid = current_user["tenant_id"]
    cid = categoria.get("id")
    nombre = categoria.get("nombre")
    
    if not cid or not nombre:
        return {"detail": "Se requiere id y nombre"}
    
    try:
        await db.execute(
            text("UPDATE categorias SET nombre = :nom WHERE id = :id AND tenant_id = :tid"),
            {"nom": nombre, "id": cid, "tid": tid}
        )
        await db.commit()
        return {"message": "Categoría actualizada", "nombre": nombre}
    except Exception as e:
        return {"detail": str(e)}

@router.delete("/categorias")
async def delete_categoria(
    categoria: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Eliminar una categoría"""
    tid = current_user["tenant_id"]
    cid = categoria.get("id")
    
    if not cid:
        return {"detail": "Se requiere id"}
    
    try:
        await db.execute(
            text("DELETE FROM categorias WHERE id = :id AND tenant_id = :tid"),
            {"id": cid, "tid": tid}
        )
        await db.commit()
        return {"message": "Categoría eliminada"}
    except Exception as e:
        return {"detail": str(e)}

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


# Inventory Adjustment Model
class InventarioAjuste(BaseModel):
    producto_id: str
    cantidad_anterior: int
    cantidad_nueva: int
    observaciones: str = ""
    tipo: str = "ajuste"  # ajuste, entrada, salida


@router.post("/ajustes", status_code=201)
async def create_ajuste(ajuste: InventarioAjuste, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    aid = str(uuid.uuid4())
    
    diff = ajuste.cantidad_nueva - ajuste.cantidad_anterior
    
    # Update inventory
    await db.execute(
        text("""UPDATE inventario SET cantidad = :nueva WHERE producto_id = :pid AND tenant_id = :tid"""),
        {"pid": ajuste.producto_id, "tid": tid, "nueva": ajuste.cantidad_nueva}
    )
    
    # Record movement
    await db.execute(
        text("""INSERT INTO inventario_movimientos (id, tenant_id, producto_id, tipo, cantidad, observaciones, created_at)
              VALUES (:id, :tid, :pid, :tipo, :cant, :obs, NOW())"""),
        {"id": aid, "tid": tid, "pid": ajuste.producto_id, "tipo": ajuste.tipo, "cant": diff, "obs": ajuste.observaciones}
    )
    await db.commit()
    
    return {"message": "Ajuste registrado", "diferencia": diff}


@router.get("/ajustes")
async def get_ajustes(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    
    result = await db.execute(
        text("""SELECT im.id, im.producto_id, p.nombre, im.tipo, im.cantidad, im.observaciones, im.created_at
              FROM inventario_movimientos im
              JOIN productos p ON p.id = im.producto_id
              WHERE im.tenant_id = :tid
              ORDER BY im.created_at DESC
              LIMIT 50"""),
        {"tid": tid}
    )
    
    return [{
        "id": str(r[0]),
        "producto_id": str(r[1]),
        "producto": r[2],
        "tipo": r[3],
        "cantidad": r[4],
        "observaciones": r[5],
        "fecha": str(r[6])
    } for r in result.fetchall()]


# Get inventory with all details
@router.get("/inventario/detalle")
async def get_inventario_detalle(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    
    result = await db.execute(
        text("""SELECT p.id, p.nombre, p.codigo, p.precio_venta, p.precio_costo, 
                     COALESCE(i.cantidad, 0) as stock, c.nombre as categoria
              FROM productos p
              LEFT JOIN inventario i ON i.producto_id = p.id AND i.tenant_id = p.tenant_id
              LEFT JOIN categorias c ON c.id = p.categoria_id AND c.tenant_id = p.tenant_id
              WHERE p.tenant_id = :tid AND p.estado = 'activo'
              ORDER BY p.nombre"""),
        {"tid": tid}
    )
    
    productos = []
    total_valor = 0
    
    for r in result.fetchall():
        stock = r[5] or 0
        costo = r[4] or 0
        valor = stock * costo
        total_valor += valor
        
        productos.append({
            "id": str(r[0]),
            "nombre": r[1],
            "codigo": r[2],
            "precio_venta": float(r[3] or 0),
            "precio_costo": float(costo),
            "stock": stock,
            "categoria": r[6],
            "valor_total": valor
        })
    
    return {
        "productos": productos,
        "total_items": len(productos),
        "valor_total_inventario": total_valor
    }




# Promociones
class PromocionCreate(BaseModel):
    nombre: str
    tipo_descuento: str = "porcentaje"
    valor: float
    fecha_inicio: str = ""
    fecha_fin: str = ""
    estado: str = "activo"

@router.get("/promociones")
async def get_promociones(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(text("SELECT id, nombre, tipo_descuento, valor, fecha_inicio, fecha_fin, estado FROM promociones WHERE tenant_id = :t AND estado = 'activo'"), {"t": tid})
    return [{"id": str(r[0]), "nombre": r[1], "tipo": r[2], "valor": float(r[3]), "inicio": str(r[4]), "fin": str(r[5]), "estado": r[6]} for r in result.fetchall()]

@router.post("/promociones", status_code=201)
async def create_promocion(p: PromocionCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    pid = str(uuid.uuid4())
    await db.execute(text("INSERT INTO promociones (id, tenant_id, nombre, tipo_descuento, valor, fecha_inicio, fecha_fin, estado) VALUES (:id, :t, :n, :tipo, :val, :ini, :fin, :est)"),
                   {"id": pid, "t": tid, "n": p.nombre, "tipo": p.tipo_descuento, "val": p.valor, "ini": p.fecha_inicio, "fin": p.fecha_fin, "est": p.estado})
    await db.commit()
    return {"id": pid, "message": "Promocion creada"}


# Campos adicionales de productos
class CampoAdicionalCreate(BaseModel):
    nombre: str
    tipo: str = "texto"
    descripcion: str = ""
    obligatorio: bool = False

@router.get("/campos")
async def get_campos(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(text("SELECT id, nombre, tipo, descripcion FROM productos_campos WHERE tenant_id = :t"), {"t": tid})
    return [{"id": str(r[0]), "nombre": r[1], "tipo": r[2], "desc": r[3]} for r in result.fetchall()]

@router.post("/campos", status_code=201)
async def create_campo(c: CampoAdicionalCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    cid = str(uuid.uuid4())
    await db.execute(text("INSERT INTO productos_campos (id, tenant_id, nombre, tipo, descripcion, obligatorio) VALUES (:id, :t, :n, :tipo, :desc, :obl)"),
                   {"id": cid, "t": tid, "n": c.nombre, "tipo": c.tipo, "desc": c.descripcion, "obl": c.obligatorio})
    await db.commit()
    return {"id": cid, "message": "Campo creado"}


# Variantes de productos  
@router.get("/variantes")
async def get_variantes(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    r = await db.execute(text("SELECT id, nombre, opciones FROM productos_variantes WHERE tenant_id = :t"), {"t": tid})
    return [{"id": str(x[0]), "nombre": x[1], "opciones": x[2]} for x in r.fetchall()]

@router.post("/variantes")
async def create_variante(data: dict, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    vid = str(uuid.uuid4())
    await db.execute(text("INSERT INTO productos_variantes (id, tenant_id, nombre, opciones) VALUES (:id, :t, :n, :o)"),
                   {"id": vid, "t": tid, "n": data.get("nombre", ""), "o": data.get("opciones", "")})
    await db.commit()
    return {"id": vid, "message": "Variante creada"}
