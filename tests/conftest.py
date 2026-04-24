# ============================================
# CONFTIG - PYTEST FIXTURES (POSTGRESQL)
# Aislamiento real: transacción por test, rollback SIEMPRE
# ============================================

import pytest
import pytest_asyncio
from uuid import uuid4
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

# Modelos
from app.core.database import Base
from app.modules.tenants.models import Tenant
from app.modules.productos.models import User, Categoria, Producto, Inventario, InventarioMovimiento
from app.modules.productos.models import Venta, VentaDetalle, Caja, ContadorFactura
from app.core.security import get_password_hash, create_access_token

# Configurar TESTING antes de importar anything más
from app.core.config import get_settings
settings = get_settings()
settings.TESTING = True


# ============================================
# CONFIGURACIÓN - POSTGRESQL
# ============================================
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/pos_test"


# ============================================
# EVENT LOOP
# ============================================
@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ============================================
# ENGINE - POSTGRESQL, function scoped
# ============================================
@pytest_asyncio.fixture(scope="function")
async def engine():
    """Crea engine PostgreSQL para cada test"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )
    
    # Crear schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


# ============================================
# SESIÓN POR TEST - AISLAMIENTOS REAL CON ROLLBACK
# ============================================
@pytest_asyncio.fixture
async def db_session(engine):
    """
    Sesión con AISLAMIENTOS REAL y GARANTIZADO.
    
    PATRÓN:
    1. Obtener conexión cruda del pool
    2. Iniciar transacción (sin commit)
    3. Crear sesión atada a esa conexión
    4. Entregar al test
    5. HACER ROLLBACK al final (SIEMPRE, aunque test pase)
    
    Esto garantiza que NADA se persista entre tests.
    """
    # 1. Obtener conexión del pool
    connection = await engine.connect()
    
    # 2. Iniciar transacción (sin commit automático)
    await connection.begin()
    
    # 3. Crear sesión atada a esta conexión
    async_session = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # 4. Crear sesión y entregar al test
    session = async_session()
    
    try:
        yield session
    finally:
        # 5. FORZAR ROLLBACK - SIEMPRE, sin importar si test pasa o falla
        try:
            await connection.rollback()
        except Exception:
            pass  # Ignorar errores en rollback
        
        # Cerrar sesión
        await session.close()
        
        # Cerrar conexión y devolver al pool
        await connection.close()


# ============================================
# FIXTURES DE DATOS
# ============================================

@pytest_asyncio.fixture
async def tenant_a(db_session):
    tenant = Tenant(
        id=uuid4(),
        nombre="Empresa A",
        nit="900123456-1",
        estado="activo"
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


@pytest_asyncio.fixture
async def tenant_b(db_session):
    tenant = Tenant(
        id=uuid4(),
        nombre="Empresa B",
        nit="900654321-1",
        estado="activo"
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


@pytest_asyncio.fixture
async def user_a(db_session, tenant_a):
    user = User(
        id=uuid4(),
        tenant_id=tenant_a.id,
        email="user_a@test.com",
        password_hash=get_password_hash("test"),
        nombre="Usuario A",
        rol="admin",
        estado="activo"
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def user_b(db_session, tenant_b):
    user = User(
        id=uuid4(),
        tenant_id=tenant_b.id,
        email="user_b@test.com",
        password_hash=get_password_hash("test"),
        nombre="Usuario B",
        rol="admin",
        estado="activo"
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def producto_a(db_session, tenant_a):
    producto = Producto(
        id=uuid4(),
        tenant_id=tenant_a.id,
        nombre="Producto Test A",
        codigo_barras="123456789",
        precio_costo=Decimal("1000"),
        precio_venta=Decimal("2000"),
        iva=Decimal("19"),
        permite_stock_negativo=False,
        estado="activo"
    )
    db_session.add(producto)
    await db_session.flush()
    
    inventario = Inventario(
        id=uuid4(),
        tenant_id=tenant_a.id,
        producto_id=producto.id,
        cantidad=Decimal("10"),
        stock_minimo=Decimal("5")
    )
    db_session.add(inventario)
    await db_session.flush()
    
    return producto


@pytest_asyncio.fixture
async def producto_b(db_session, tenant_b):
    producto = Producto(
        id=uuid4(),
        tenant_id=tenant_b.id,
        nombre="Producto Test B",
        codigo_barras="987654321",
        precio_costo=Decimal("500"),
        precio_venta=Decimal("1000"),
        iva=Decimal("19"),
        permite_stock_negativo=False,
        estado="activo"
    )
    db_session.add(producto)
    await db_session.flush()
    
    inventario = Inventario(
        id=uuid4(),
        tenant_id=tenant_b.id,
        producto_id=producto.id,
        cantidad=Decimal("5"),
        stock_minimo=Decimal("2")
    )
    db_session.add(inventario)
    await db_session.flush()
    
    return producto


@pytest.fixture
def token_a(tenant_a, user_a):
    return create_access_token({
        "sub": str(user_a.id),
        "tenant_id": str(tenant_a.id)
    })


@pytest.fixture
def token_b(tenant_b, user_b):
    return create_access_token({
        "sub": str(user_b.id),
        "tenant_id": str(tenant_b.id)
    })


@pytest_asyncio.fixture
async def contador_factura_a(db_session, tenant_a):
    contador = ContadorFactura(
        tenant_id=tenant_a.id,
        contador=1
    )
    db_session.add(contador)
    await db_session.flush()
    return contador


@pytest_asyncio.fixture
async def contador_factura_b(db_session, tenant_b):
    contador = ContadorFactura(
        tenant_id=tenant_b.id,
        contador=1
    )
    db_session.add(contador)
    await db_session.flush()
    return contador