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
    """Initialize database tables and seed data if empty"""
    from app.core.database import Base, AsyncSessionLocal
    from app.modules.tenants.models import Tenant
    from app.modules.productos.models import User, Categoria, Producto, Inventario
    from app.modules.ventas.models import Caja, Venta, VentaDetalle
    from app.modules.productos.models import Cliente
    from sqlalchemy import select
    from uuid import uuid4

    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed data if empty
    async with AsyncSessionLocal() as session:
        # Check if tenant exists by ID OR by NIT
        result = await session.execute(
            select(Tenant).where(
                (Tenant.id == "4a7e815e-f68e-46f4-863d-1d2f786301e8") | 
                (Tenant.nit == "12345678901")
            )
        )
        existing_tenant = result.scalar_one_or_none()
        
        if not existing_tenant:
            print("🔄 Seed data...")
            # Create tenant with fixed ID
            tenant = Tenant(
                id="4a7e815e-f68e-46f4-863d-1d2f786301e8",
                nombre="Tienda Demo",
                nit="12345678901",
                direccion="Calle 123",
                telefono="3001234567",
                email="demo@tienda.com",
                plan="basic",
                estado="activo"
            )
            session.add(tenant)
            await session.flush()
        else:
            # Use existing tenant
            tenant = existing_tenant
            print("✅ Tenant already exists")

            # Force create category if not exists
            result_cat = await session.execute(
                select(Categoria).where(Categoria.tenant_id == tenant.id)
            )
            existing_cat = result_cat.scalar_one_or_none()
            
            if not existing_cat:
                categoria = Categoria(
                    id="d7bee82b-312f-408b-bb1e-8e5d84e491b2",
                    tenant_id=tenant.id,
                    nombre="Bebidas y Comidas"
                )
                session.add(categoria)
                await session.flush()
                print("✅ Category created")
            else:
                print("✅ Category already exists")

            # Force create products if not exist
            result_prod = await session.execute(
                select(Producto).where(Producto.tenant_id == tenant.id)
            )
            existing_products = result_prod.scalars().all()
            
            if len(existing_products) == 0:
                print("🔄 Creating products...")
                productos = [
                    {"nombre": "Café Americano", "precio_venta": 2500, "precio_costo": 1200, "stock": 50},
                    {"nombre": "Café Latte", "precio_venta": 3500, "precio_costo": 1800, "stock": 30},
                    {"nombre": "Te Verde", "precio_venta": 2500, "precio_costo": 1000, "stock": 40},
                    {"nombre": "Jugo Natural", "precio_venta": 4500, "precio_costo": 2000, "stock": 20},
                    {"nombre": "Sandwich", "precio_venta": 6500, "precio_costo": 3000, "stock": 15},
                    {"nombre": "Croissant", "precio_venta": 2500, "precio_costo": 1000, "stock": 25},
                    {"nombre": "Galletas", "precio_venta": 1500, "precio_costo": 500, "stock": 60},
                    {"nombre": "Agua Mineral", "precio_venta": 1500, "precio_costo": 500, "stock": 100},
                    {"nombre": "Gaseosa", "precio_venta": 2000, "precio_costo": 800, "stock": 80},
                    {"nombre": "Cerveza", "precio_venta": 4000, "precio_costo": 1800, "stock": 48},
                ]

                for p in productos:
                    prod = Producto(
                        id=uuid4(),
                        tenant_id=tenant.id,
                        nombre=p["nombre"],
                        precio_venta=p["precio_venta"],
                        precio_costo=p["precio_costo"],
                        estado="activo"
                    )
                    session.add(prod)
                    await session.flush()

                    inv = Inventario(
                        id=uuid4(),
                        tenant_id=tenant.id,
                        producto_id=prod.id,
                        cantidad=p["stock"]
                    )
                    session.add(inv)

                await session.commit()
                print("✅ Seed complete!")
            else:
                print(f"✅ Products already exist: {len(existing_products)}")


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)