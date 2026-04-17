from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user
import uuid

router = APIRouter()

class CompraCreate(BaseModel):
    proveedor_id: str = ""
    numero_factura: str = ""
    fecha: str = ""
    observations: str = ""

@router.get("/compras")
async def get_compras(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    r = await db.execute(text("SELECT id, proveedor_id, numero_factura, fecha, total, estado FROM compras WHERE tenant_id = :t ORDER BY fecha DESC LIMIT 30"), {"t": tid})
    return [{"id": str(x[0]), "proveedor": x[1], "factura": x[2], "fecha": str(x[3]), "total": float(x[4]), "estado": x[5]} for x in r.fetchall()]

@router.post("/compras", status_code=201)
async def create_compra(c: CompraCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    cid = str(uuid.uuid4())
    await db.execute(text("INSERT INTO compras (id, tenant_id, proveedor_id, numero_factura, fecha, estado, creada_en) VALUES (:id, :t, :p, :n, :f, 'pendiente', NOW())"), {"id": cid, "t": tid, "p": c.proveedor_id, "n": c.numero_factura, "f": c.fecha})
    await db.commit()
    return {"id": cid, "message": "Compra registrada"}
