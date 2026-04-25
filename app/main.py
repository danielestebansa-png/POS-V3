# ============================================
# FASTAPI MAIN APPLICATION
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import async_engine, get_db

# Import routers
from app.modules.auth.router import router as auth_router
from app.modules.tenants.router import router as tenants_router
from app.modules.productos.router import router as productos_router
from app.modules.ventas.router import router as ventas_router
from app.modules.clientes.router import router as clientes_router
from app.modules.ventas.migrate import router as migrate_router

# ============================================
# APP INSTANCE
# ============================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema POS multi-tenant para pequeñas empresas"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# ROUTES
# ============================================

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(tenants_router, prefix="/api/tenants", tags=["Tenants"])
app.include_router(productos_router, prefix="/api/productos", tags=["Productos"])
app.include_router(ventas_router, prefix="/api/ventas", tags=["Ventas"])
app.include_router(clientes_router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(migrate_router, tags=["Migrate"])


# ============================================
# DATABASE INIT
# ============================================

@app.on_event("startup")
async def init_db():
    """Initialize database and run migrations"""
    from app.core.database import Base
    from app.modules.tenants.models import Tenant
    from app.modules.productos.models import User
    from app.modules.productos.models import Categoria, Producto, Inventario
    from app.modules.ventas.models import Caja, Venta, VentaDetalle
    from app.modules.productos.models import Cliente
    from uuid import uuid4
    from sqlalchemy import text
    
    async with async_engine.begin() as conn:
        # Run migrations first
        try:
            await conn.execute(text("ALTER TABLE inventario ADD COLUMN IF NOT EXISTS stock NUMERIC(15,3) DEFAULT 0"))
            print("Migration: Added stock column to inventario")
        except Exception as e:
            print(f"Migration skipped: {e}")
        
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed categories and products if none exist
    tenant_id = "4a7e815e-f68e-46f4-863d-1d2f786301e8"
    async with async_engine.connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM categorias WHERE tenant_id = :t"), {"t": tenant_id})
        count = result.scalar()
        
        if count == 0:
            print("Seeding categories and products...")
            cat_ids = {}
            categorias = ["Útiles Escolares", "Papelería", "Artes y Manualidades", "Tecnología"]
            for cat_nombre in categorias:
                cat_id = str(uuid4())
                cat_ids[cat_nombre] = cat_id
                await conn.execute(text("INSERT INTO categorias (id, tenant_id, nombre, padre_id, estado, created_at, updated_at) VALUES (:id, :tenant, :nombre, NULL, 'activo', NOW(), NOW())"), {"id": cat_id, "tenant": tenant_id, "nombre": cat_nombre})
            
            subcategorias = [("Cuadernos", "Útiles Escolares"), ("Lápices y Colores", "Útiles Escolares"), ("Carpetas", "Papelería"), ("Papel Bond", "Papelería"), ("Pinturas", "Artes y Manualidades"), ("Pinceles", "Artes y Manualidades"), ("Cables USB", "Tecnología"), ("Mouse", "Tecnología")]
            for sub_nombre, padre_nombre in subcategorias:
                sub_id = str(uuid4())
                await conn.execute(text("INSERT INTO categorias (id, tenant_id, nombre, padre_id, estado, created_at, updated_at) VALUES (:id, :tenant, :nombre, :padre, 'activo', NOW(), NOW())"), {"id": sub_id, "tenant": tenant_id, "nombre": sub_nombre, "padre": cat_ids[padre_nombre]})
            
            productos = [("Cuaderno College 100 hojas", 8500, 45), ("Lápices colores x12", 12000, 30), ("Borrador blanco", 1500, 100), ("Sacapuntas metálico", 3500, 25), ("Regla 30cm", 2500, 40), ("Carpeta plastificada", 5500, 35), ("Papel Bond A4 x500", 18000, 20), ("Clips x50", 2500, 50), ("Grapadora", 12000, 15), ("Tijeras escolar", 4500, 25), ("Pintura acrílica x6", 15000, 18), ("Pinceles pelo fino x5", 8000, 22), ("Cartulina colores x10", 6000, 40), ("Pegamento escolar", 3500, 60), ("Fomi colores", 4000, 35), ("Cable USB tipo C", 15000, 28), ("Mouse inalámbrico", 25000, 12), ("Teclado USB", 35000, 8), ("Audífonos basic", 18000, 15), ("Pendrive 32GB", 22000, 20)]
            for nombre, precio, stock in productos:
                prod_id = str(uuid4())
                cat_idx = productos.index((nombre, precio, stock))
                cat_keys = list(cat_ids.keys())
                cat = cat_keys[cat_idx // 5]
                await conn.execute(text("INSERT INTO productos (id, tenant_id, nombre, precio_venta, precio_costo, stock, categoria_id, estado, created_at, updated_at) VALUES (:id, :tenant, :nombre, :precio, :costo, :stock, :cat, 'activo', NOW(), NOW())"), {"id": prod_id, "tenant": tenant_id, "nombre": nombre, "precio": precio, "costo": precio*0.5, "stock": stock, "cat": cat_ids[cat]})
            
            await conn.commit()
            print(f"Created {len(categorias)} categories, {len(subcategorias)} subcategories, and {len(productos)} products")


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ============================================
# MIGRATION ENDPOINT
# ============================================
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, async_engine
from sqlalchemy import text

@app.post("/migrate-add-stock")
async def migrate_add_stock(db: AsyncSession = Depends(get_db)):
    """Add stock column to inventario table - run once"""
    try:
        # Add column if not exists
        await db.execute(text("ALTER TABLE inventario ADD COLUMN IF NOT EXISTS stock NUMERIC(15,3) DEFAULT 0"))
        await db.commit()
        return {"success": True, "message": "Column stock added to inventario table"}
    except Exception as e:
        return {"success": False, "error": str(e)}
