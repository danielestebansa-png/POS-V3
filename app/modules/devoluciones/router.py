# Devoluciones Router
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()

class DevolucionCreate(BaseModel):
    venta_id: str
    tipo: str  # dinero, credito, combinado
    cantidad: float
    observaciones: str = ""

@router.post("/devoluciones", status_code=201)
async def create_devolucion(dev: DevolucionCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    did = str(uuid.uuid4())
    estado = "pendiente"
    
    await db.execute(
        text("INSERT INTO devoluciones (id, tenant_id, venta_id, tipo, cantidad, estado, observaciones, creado_en) VALUES (:id, :t, :v, :tipo, :cant, :est, :obs, NOW())"),
        {"id": did, "t": tid, "v": dev.venta_id, "tipo": dev.tipo, "cant": dev.cantidad, "est": estado, "obs": dev.observaciones}
    )
    await db.commit()
    return {"id": did, "message": "Devolución solicitada", "estado": estado}

@router.get("/devoluciones")
async def get_devoluciones(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(
        text("SELECT d.id, d.venta_id, d.tipo, d.cantidad, d.estado, d.observaciones, d.creado_en FROM devoluciones d WHERE d.tenant_id = :t ORDER BY d.creado_en DESC LIMIT 30"),
        {"t": tid}
    )
    return [{"id": str(r[0]), "venta_id": str(r[1]), "tipo": r[2], "cantidad": float(r[3]), "estado": r[4], "obs": r[5], "fecha": str(r[6])} for r in result.fetchall()]

@router.put("/devoluciones/{devolucion_id}/aprobar")
async def aprobar_devolucion(devolucion_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    await db.execute(text("UPDATE devoluciones SET estado = 'aprobada', actualizado_en = NOW() WHERE id = :id AND tenant_id = :t"), {"id": devolucion_id, "t": tid})
    await db.commit()
    return {"message": "Devolución aprobada"}
