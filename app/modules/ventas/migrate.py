from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.post("/admin/migrate-inventario")
async def migrate_inventario(db: AsyncSession = Depends(get_db)):
    """Add stock column to inventario table"""
    try:
        await db.execute(text("ALTER TABLE inventario ADD COLUMN IF NOT EXISTS stock NUMERIC(15,3) DEFAULT 0"))
        await db.commit()
        return {"message": "Migration completed"}
    except Exception as e:
        return {"error": str(e)}
