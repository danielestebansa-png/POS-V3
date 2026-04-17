# Clientes Router

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()


class ClienteCreate(BaseModel):
    nombre: str
    identificacion: str = ""
    telefono: str = ""
    email: str = ""
    direccion: str = ""
    estado: str = "activo"


@router.get("/clientes")
async def get_clientes(buscar: str = "", current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    
    query = "SELECT id, nombre, identificacion, telefono, email, direccion, estado FROM clientes WHERE tenant_id = :t"
    params = {"t": tid}
    
    if buscar:
        query += " AND (nombre ILIKE :b OR identificacion ILIKE :b)"
        params["b"] = f"%{buscar}%"
    
    query += " ORDER BY nombre LIMIT 50"
    
    result = await db.execute(text(query), params)
    return [{"id": str(r[0]), "nombre": r[1], "identificacion": r[2], "telefono": r[3], "email": r[4], "direccion": r[5], "estado": r[6]} for r in result.fetchall()]


@router.post("/clientes", status_code=201)
async def create_cliente(cliente: ClienteCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    cid = str(uuid.uuid4())
    
    await db.execute(
        text("INSERT INTO clientes (id, tenant_id, nombre, identificacion, telefono, email, direccion, estado) VALUES (:id, :t, :n, :i, :tel, :e, :d, :est)"),
        {"id": cid, "t": tid, "n": cliente.nombre, "i": cliente.identificacion, "tel": cliente.telefono, "e": cliente.email, "d": cliente.direccion, "est": cliente.estado}
    )
    await db.commit()
    
    return {"id": cid, "message": "Cliente creado"}


@router.put("/clientes/{cliente_id}")
async def update_cliente(cliente_id: str, cliente: ClienteCreate, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    
    await db.execute(
        text("UPDATE clientes SET nombre = :n, identificacion = :i, telefono = :tel, email = :e, direccion = :d, estado = :est WHERE id = :id AND tenant_id = :t"),
        {"id": cliente_id, "t": tid, "n": cliente.nombre, "i": cliente.identificacion, "tel": cliente.telefono, "e": cliente.email, "d": cliente.direccion, "est": cliente.estado}
    )
    await db.commit()
    
    return {"message": "Cliente actualizado"}


@router.delete("/clientes/{cliente_id}")
async def delete_cliente(cliente_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    
    await db.execute(text("DELETE FROM clientes WHERE id = :id AND tenant_id = :t"), {"id": cliente_id, "t": tid})
    await db.commit()
    
    return {"message": "Cliente eliminado"}

print("Clientes router created")
