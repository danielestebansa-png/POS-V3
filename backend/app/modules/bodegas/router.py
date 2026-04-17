# Bodegas
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()

class BodegaCreate(BaseModel):
    nombre: str
    direccion: str = ""
    estado: str = "activo"

@router.get("/bodegas")
async def get_bodegas(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(text("SELECT id, nombre, direccion, estado FROM bodegas WHERE tenant_id = :t ORDER BY nombre"), {"t": tid})
    return [{"id": str(r[0]), "nombre": r[1], "direccion": r[2], "estado": r[3]} for r in result.fetchall()]

@router.post("/bodegas", status_code=201)
async def create_bodega(b: BodegaCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    bid = str(uuid.uuid4())
    await db.execute(text("INSERT INTO bodegas (id, tenant_id, nombre, direccion, estado) VALUES (:id, :t, :n, :d, :e)"),
                   {"id": bid, "t": tid, "n": b.nombre, "d": b.direccion, "e": b.estado})
    await db.commit()
    return {"id": bid, "message": "Bodega creada"}

@router.put("/bodegas/{bodega_id}")
async def update_bodega(bodega_id: str, b: BodegaCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    await db.execute(text("UPDATE bodegas SET nombre = :n, direccion = :d, estado = :e WHERE id = :id AND tenant_id = :t"),
                   {"id": bodega_id, "t": tid, "n": b.nombre, "d": b.direccion, "e": b.estado})
    await db.commit()
    return {"message": "Bodega actualizada"}

@router.delete("/bodegas/{bodega_id}")
async def delete_bodega(bodega_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    await db.execute(text("DELETE FROM bodegas WHERE id = :id AND tenant_id = :t"), {"id": bodega_id, "t": tid})
    await db.commit()
    return {"message": "Bodega eliminada"}
