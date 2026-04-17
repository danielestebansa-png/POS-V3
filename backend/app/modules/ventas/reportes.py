# Reportes Router
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.get("/resumen")
async def get_resumen(fecha: str = None, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tid = current_user["tenant_id"]
    if not fecha:
        from datetime import datetime
        fecha = datetime.now().strftime("%Y-%m-%d")
    
    # Get totals
    r = await db.execute(text("""SELECT COUNT(*), COALESCE(SUM(total), 0),
        COALESCE(SUM(CASE WHEN metodo_pago='efectivo' THEN total ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN metodo_pago='tarjeta' THEN total ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN metodo_pago='transferencia' THEN total ELSE 0 END), 0)
        FROM ventas WHERE tenant_id = :t AND fecha::date = :f"""), {"t": tid, "f": fecha})
    row = r.fetchone()
    
    return {
        "fecha": fecha,
        "num_ventas": row[0],
        "total": float(row[1]),
        "efectivo": float(row[2]),
        "tarjeta": float(row[3]),
        "transferencia": float(row[4])
    }

