# Gestion de Efectivo
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()

class MovimientoEfectivo(BaseModel):
    tipo: str  # ingreso, retiro
    cantidad: float
    observaciones: str = ""
    cliente_id: str = None

@router.post("/movimientos", status_code=201)
async def create_movimiento(mov: MovimientoEfectivo, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    mid = str(uuid.uuid4())
    await db.execute(
        text("INSERT INTO caja_movimientos (id, tenant_id, tipo, cantidad, observaciones, cliente_id, creado_en) VALUES (:id, :t, :tipo, :cant, :obs, :cli, NOW())"),
        {"id": mid, "t": tid, "tipo": mov.tipo, "cant": mov.cantidad, "obs": mov.observaciones, "cli": mov.cliente_id}
    )
    await db.commit()
    return {"id": mid, "message": f"{mov.tipo.capitalize()} registrado"}

@router.get("/movimientos")
async def get_movimientos(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(
        text("SELECT id, tipo, cantidad, observaciones, cliente_id, creado_en FROM caja_movimientos WHERE tenant_id = :t ORDER BY creado_en DESC LIMIT 30"),
        {"t": tid}
    )
    return [{"id": str(r[0]), "tipo": r[1], "cantidad": float(r[2]), "obs": r[3], "cliente_id": str(r[4]) if r[4] else None, "fecha": str(r[5])} for r in result.fetchall()]

@router.get("/arqueo")
async def get_arqueo(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    # Get totals
    result = await db.execute(
        text("""SELECT 
            COALESCE(SUM(CASE WHEN tipo = 'ingreso' THEN cantidad ELSE 0 END), 0) as ingresos,
            COALESCE(SUM(CASE WHEN tipo = 'retiro' THEN cantidad ELSE 0 END), 0) as retiros
            FROM caja_movimientos WHERE tenant_id = :t"""),
        {"t": tid}
    )
    row = result.fetchone()
    return {"ingresos": float(row[0]), "retiros": float(row[1]), "neto": float(row[0]) - float(row[1])}

