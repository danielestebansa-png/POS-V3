# ============================================
# SEED DATA - Productos e Inventario de prueba
# Ejecutar con: python -m app.scripts.seed
# ============================================

import asyncio
import sys
import os
from decimal import Decimal
from uuid import uuid4

# Agregar el path del backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.database import Base
from app.modules.tenants.models import Tenant
from app.modules.productos.models import (
    User, Categoria, Producto, Inventario
)
from app.modules.productos.models import ContadorFactura


# URL de la base de datos
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/pos_test"


# Productos de ejemplo
PRODUCTOS_EJEMPLO = [
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


async def seed_data():
    """Crear datos de prueba para productos e inventario"""
    
    print("🚀 Iniciando seed de datos...")
    
    # Conectar a la base de datos
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # Crear tablas si no existen
        await conn.run_sync(Base.metadata.create_all)
    
    # Crear sesión
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 1. Verificar si ya existe un tenant
        result = await session.execute(select(Tenant).limit(1))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            # Crear tenant de prueba
            tenant = Tenant(
                id=uuid4(),
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
            print(f"✅ Tenant creado: {tenant.nombre}")
        else:
            print(f"📦 Tenant existente: {tenant.nombre}")
        
        # 2. Verificar si ya existen productos
        result = await session.execute(select(Producto).where(Producto.tenant_id == tenant.id))
        productos_existentes = result.scalars().all()
        
        if len(productos_existentes) > 0:
            print(f"⚠️ Ya existen {len(productos_existentes)} productos. Saltando...")
            await engine.dispose()
            return
        
        # 3. Crear categoría
        categoria = Categoria(
            id=uuid4(),
            tenant_id=tenant.id,
            nombre="Bebidas y Comidas",
            estado="activo"
        )
        session.add(categoria)
        await session.flush()
        print("✅ Categoría creada")
        
        # 4. Crear productos con inventario
        for datos in PRODUCTOS_EJEMPLO:
            # Crear producto
            producto = Producto(
                id=uuid4(),
                tenant_id=tenant.id,
                nombre=datos["nombre"],
                codigo_barras=f"CODE{str(uuid4())[:8]}",
                precio_costo=Decimal(str(datos["precio_costo"])),
                precio_venta=Decimal(str(datos["precio_venta"])),
                iva=Decimal("19"),
                permite_stock_negativo=False,
                estado="activo",
                categoria_id=categoria.id
            )
            session.add(producto)
            await session.flush()
            
            # Crear inventario para el producto
            inventario = Inventario(
                id=uuid4(),
                tenant_id=tenant.id,
                producto_id=producto.id,
                cantidad=Decimal(str(datos["stock"])),
                stock_minimo=Decimal("5")
            )
            session.add(inventario)
            
            print(f"  ✓ {producto.nombre} - Stock: {datos['stock']}")
        
        # 5. Crear contador de facturas
        contador = ContadorFactura(
            id=uuid4(),
            tenant_id=tenant.id,
            contador=1
        )
        session.add(contador)
        
        # Commit final
        await session.commit()
        
        print(f"\n🎉 Seed completado!")
        print(f"   - Productos creados: {len(PRODUCTOS_EJEMPLO)}")
        print(f"   - Tenant ID: {tenant.id}")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
