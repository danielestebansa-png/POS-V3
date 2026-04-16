# ============================================
# FASTAPI MAIN APPLICATION
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import async_engine

# Import routers
from app.modules.auth.router import router as auth_router
from app.modules.tenants.router import router as tenants_router
from app.modules.productos.router import router as productos_router
from app.modules.ventas.router import router as ventas_router
from app.modules.clientes.router import router as clientes_router


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


# ============================================
# DATABASE INIT
# ============================================

@app.on_event("startup")
async def init_db():
    """Initialize database tables"""
    from app.core.database import Base
    from app.modules.tenants.models import Tenant
    from app.modules.productos.models import User
    from app.modules.productos.models import Categoria, Producto, Inventario
    from app.modules.ventas.models import Caja, Venta, VentaDetalle
    from app.modules.productos.models import Cliente
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)