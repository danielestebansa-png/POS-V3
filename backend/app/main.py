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
# Deployed with additional categories


# ============================================
# SEED: Add more categories and products
# ============================================
@app.on_event("startup")
async def add_more_categories():
    """Add additional categories and products"""
    import asyncio
    await asyncio.sleep(3)
    
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import text
    from uuid import uuid4
    
    tenant_id = "4a7e815e-f68e-46f4-863d-1d2f786301e8"
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM categorias WHERE tenant_id = :t"), {"t": tenant_id})
            count = result.scalar()
            
            if count <= 1:
                print("Adding more categories...")
                
                cat_ids = {}
                categorias = ["Útiles Escolares", "Papelería", "Artes y Manualidades", "Tecnología"]
                for cat_nombre in categorias:
                    cat_id = str(uuid4())
                    cat_ids[cat_nombre] = cat_id
                    await session.execute(
                        text("INSERT INTO categorias (id, tenant_id, nombre, padre_id, estado, created_at, updated_at) VALUES (:id, :tenant, :nombre, NULL, 'activo', NOW(), NOW())"),
                        {"id": cat_id, "tenant": tenant_id, "nombre": cat_nombre}
                    )
                
                subcategorias = [("Cuadernos", "Útiles Escolares"), ("Lápices y Colores", "Útiles Escolares"), ("Carpetas", "Papelería"), ("Papel Bond", "Papelería"), ("Pinturas", "Artes y Manualidades"), ("Pinceles", "Artes y Manualidades"), ("Cables USB", "Tecnología"), ("Mouse", "Tecnología")]
                for sub_nombre, padre_nombre in subcategorias:
                    sub_id = str(uuid4())
                    await session.execute(
                        text("INSERT INTO categorias (id, tenant_id, nombre, padre_id, estado, created_at, updated_at) VALUES (:id, :tenant, :nombre, :padre, 'activo', NOW(), NOW())"),
                        {"id": sub_id, "tenant": tenant_id, "nombre": sub_nombre, "padre": cat_ids[padre_nombre]}
                    )
                
                productos = [("Cuaderno College", 8500, 45), ("Lápices colores", 12000, 30), ("Borrador", 1500, 100), ("Sacapuntas", 3500, 25), ("Regla 30cm", 2500, 40), ("Carpeta", 5500, 35), ("Papel Bond", 18000, 20), ("Clips", 2500, 50), ("Grapadora", 12000, 15), ("Tijeras", 4500, 25), ("Pintura", 15000, 18), ("Pinceles", 8000, 22), ("Cartulina", 6000, 40), ("Pegamento", 3500, 60), ("Fomi", 4000, 35), ("Cable USB", 15000, 28), ("Mouse", 25000, 12), ("Teclado", 35000, 8), ("Audífonos", 18000, 15), ("Pendrive", 22000, 20)]
                for nombre, precio, stock in productos:
                    prod_id = str(uuid4())
                    cat_idx = productos.index((nombre, precio, stock))
                    cat = list(cat_ids.keys())[cat_idx // 5]
                    await session.execute(
                        text("INSERT INTO productos (id, tenant_id, nombre, precio_venta, precio_costo, stock, categoria_id, estado, created_at, updated_at) VALUES (:id, :tenant, :nombre, :precio, :costo, :stock, :cat, 'activo', NOW(), NOW())"),
                        {"id": prod_id, "tenant": tenant_id, "nombre": nombre, "precio": precio, "costo": precio*0.5, "stock": stock, "cat": cat_ids[cat]}
                    )
                
                await session.commit()
                print(f"Added {len(categorias)} categories and {len(productos)} products")
        except Exception as e:
            print(f"Seed error: {e}")
