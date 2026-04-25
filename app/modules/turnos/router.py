# Turnos Router

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.post("/abrir", status_code=201)
async def abrir_turno(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    import uuid
    tid_turno = str(uuid.uuid4())
    
    # Check existing open turn
    result = await db.execute(text("SELECT id FROM turnos WHERE tenant_id = :t AND estado = 'abierto'"), {"t": tid})
    if result.fetchone():
        return {"error": "Ya hay un turno abierto"}
    
    await db.execute(text("INSERT INTO turnos (id, tenant_id, usuario_id, estado, base_inicial, creado_en) VALUES (:id, :t, :u, 'abierto', 0, NOW())"),
                 {"id": tid_turno, "t": tid, "u": current_user.get("user_id")})
    await db.commit()
    
    return {"id": tid_turno, "message": "Turno abierto"}


@router.post("/cerrar")
async def cerrar_turno(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(text("SELECT id FROM turnos WHERE tenant_id = :t AND estado = 'abierto'"), {"t": tid})
    row = result.fetchone()
    if not row:
        return {"error": "No hay turno abierto"}
    
    await db.execute(text("UPDATE turnos SET estado = 'cerrado', cerrado_en = NOW() WHERE id = :id"), {"id": str(row[0])})
    await db.commit()
    return {"message": "Turno cerrado"}


@router.get("/actual")
async def get_turno_actual(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(text("SELECT id, base_inicial, estado, creado_en FROM turnos WHERE tenant_id = :t ORDER BY creado_en DESC LIMIT 1"), {"t": tid})
    row = result.fetchone()
    if not row:
        return {"status": "sin_turno"}
    return {"id": str(row[0]), "base": float(row[1]), "estado": row[2], "fecha": str(row[3])}


@router.get("/historial")
async def get_historial(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    result = await db.execute(text("SELECT id, estado, base_inicial, creado_en, cerrado_en, total_ventas FROM turnos WHERE tenant_id = :t ORDER BY creado_en DESC LIMIT 20"), {"t": tid})
    return [{"id": str(r[0]), "estado": r[1], "base": float(r[2]), "inicio": str(r[3]), "cierre": str(r[4]) if r[4] else None, "total": float(r[5])} for r in result.fetchall()]

print("Turnos router created")
