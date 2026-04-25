# Listas de Precios
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()

class ListaPrecioCreate(BaseModel):
    nombre: str
    tipo: str = "porcentaje"  # porcentaje, fijo
    valor: float = 0

@router.get("/listas")
async def get_listas(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(text("SELECT id, nombre, tipo, valor FROM lista_precios WHERE tenant_id = :t ORDER BY nombre"), {"t": tid})
    return [{"id": str(r[0]), "nombre": r[1], "tipo": r[2], "valor": float(r[3])} for r in result.fetchall()]

@router.post("/listas", status_code=201)
async def create_lista(lista: ListaPrecioCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    lid = str(uuid.uuid4())
    await db.execute(text("INSERT INTO lista_precios (id, tenant_id, nombre, tipo, valor) VALUES (:id, :t, :n, :tipo, :val)"),
                   {"id": lid, "t": tid, "n": lista.nombre, "tipo": lista.tipo, "val": lista.valor})
    await db.commit()
    return {"id": lid, "message": "Lista creada"}

@router.get("/listas/{lista_id}/productos")
async def get_productos_lista(lista_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(
        text("""SELECT p.id, p.nombre, p.precio_venta, lp.valor as descuento
               FROM productos p
               JOIN lista_precios_productos lpp ON lpp.producto_id = p.id AND lpp.lista_id = :lid
               JOIN lista_precios lp ON lp.id = lpp.lista_id AND lp.tenant_id = :t
               WHERE p.tenant_id = :t"""),
        {"lid": lista_id, "t": tid}
    )
    return [{"id": str(r[0]), "nombre": r[1], "precio_base": float(r[2]), "descuento": float(r[3])} for r in result.fetchall()]

@router.post("/listas/{lista_id}/productos")
async def add_producto_lista(lista_id: str, producto_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    await db.execute(text("INSERT INTO lista_precios_productos (id, tenant_id, lista_id, producto_id) VALUES (:id, :t, :lid, :pid)"),
                   {"id": str(uuid.uuid4()), "t": tid, "lid": lista_id, "pid": producto_id})
    await db.commit()
    return {"message": "Producto agregado a lista"}

