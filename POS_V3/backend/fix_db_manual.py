"""
Script para ejecutar fixes en la base de datos PostgreSQL
Ejecutar con: python fix_db_manual.py
"""
import asyncio
import sys
import os

# Agregar el path del backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    print("🔧 Ejecutando fixes en base de datos...")
    
    # Conectar a PostgreSQL
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/pos_test",
        echo=False
    )
    
    async with engine.begin() as conn:
        # 1. Crear extensión UUID
        print("1️⃣ Creando extensión uuid-ossp...")
        await conn.exec_driver_sql('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        
        # 2. Fix UUID en contador_facturas
        print("2️⃣ Configurando UUID automático para contador_facturas...")
        await conn.exec_driver_sql('ALTER TABLE contador_facturas ALTER COLUMN id SET DEFAULT uuid_generate_v4()')
        
        # 3. UNIQUE constraint en ventas
        print("3️⃣ Agregando constraint único a ventas...")
        await conn.exec_driver_sql('ALTER TABLE ventas ADD CONSTRAINT unique_numero_por_tenant UNIQUE (tenant_id, numero)')
    
    await engine.dispose()
    
    print("\n✅ ¡Fixes aplicados correctamente!")
    print("\n👉 Ahora ejecuta: python -m pytest tests/ -v")

if __name__ == "__main__":
    asyncio.run(main())
