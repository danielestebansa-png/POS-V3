# ============================================
# TEST 3: AISLAMIENTOS MULTI-TENANT
# ============================================

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.productos.models import Producto, Inventario, Categoria
from app.modules.ventas.models import Venta, VentaDetalle, Caja
from app.modules.productos.models import Cliente
from app.modules.tenants.models import Tenant


@pytest.mark.asyncio
async def test_tenant_no_puede_ver_productos_de_otro(
    db_session: AsyncSession,
    tenant_a,
    tenant_b,
    producto_a,
    producto_b,
    user_a
):
    """
    CASO: Tenant A intenta ver productos de Tenant B
    
    RESULTADO ESPERADO: No encuentra nada (aislamiento completo)
    """
    
    # Tenant A hace query de productos (debe ver solo los suyos)
    result_a = await db_session.execute(
        select(Producto).where(Producto.tenant_id == tenant_a.id)
    )
    productos_a = result_a.scalars().all()
    
    # Tenant A debe ver producto_a, NO producto_b
    ids_productos_a = [p.id for p in productos_a]
    
    assert producto_a.id in ids_productos_a, "Tenant A debe ver su producto"
    assert producto_b.id not in ids_productos_a, "Tenant A NO debe ver producto de B"
    
    # Lo inverso para Tenant B
    result_b = await db_session.execute(
        select(Producto).where(Producto.tenant_id == tenant_b.id)
    )
    productos_b = result_b.scalars().all()
    
    ids_productos_b = [p.id for p in productos_b]
    
    assert producto_b.id in ids_productos_b, "Tenant B debe ver su producto"
    assert producto_a.id not in ids_productos_b, "Tenant B NO debe ver producto de A"
    
    print("✅ TEST 3A PASÓ: Productos aislados por tenant")


@pytest.mark.asyncio
async def test_tenant_no_puede_acceder_por_id(
    db_session: AsyncSession,
    tenant_a,
    tenant_b,
    producto_a,
    producto_b,
    user_a
):
    """
    CASO: Tenant A conoce el ID de producto de Tenant B e intenta acceder
    
    RESULTADO ESPERADO: Devuelve None o falla (no puede ver)
    """
    
    # Tenant A intenta acceder al producto de B usando su ID
    # La query debe incluir both: id AND tenant_id
    result = await db_session.execute(
        select(Producto).where(
            Producto.id == producto_b.id,
            Producto.tenant_id == tenant_a.id  # Filtro de aislamiento
        )
    )
    producto_encontrado = result.scalar_one_or_none()
    
    assert producto_encontrado is None, \
        "Tenant A no puede acceder a producto de B aunque conozca el ID"
    
    print("✅ TEST 3B PASÓ: Aislamiento por ID no puede ser bypaseado")


@pytest.mark.asyncio
async def test_ventas_aisladas_entre_tenants(
    db_session: AsyncSession,
    tenant_a,
    tenant_b,
    producto_a,
    producto_b,
    user_a,
    user_b
):
    """
    CASO: Ventas de un tenant no aparecen en otro
    
    RESULTADO ESPERADO: Total aislamiento
    """
    
    # Crear caja para cada tenant
    caja_a = Caja(tenant_id=tenant_a.id, nombre="Caja A", estado="cerrada")
    caja_b = Caja(tenant_id=tenant_b.id, nombre="Caja B", estado="cerrada")
    db_session.add(caja_a)
    db_session.add(caja_b)
    await db_session.flush()
    
    # Crear venta para Tenant A
    venta_a = Venta(
        tenant_id=tenant_a.id,
        numero="FAC-00001",
        caja_id=caja_a.id,
        vendedor_id=user_a.id,
        subtotal=2000,
        total=2380,
        iva=380,
        metodo_pago="efectivo",
        estado="completada"
    )
    db_session.add(venta_a)
    
    # Crear venta para Tenant B
    venta_b = Venta(
        tenant_id=tenant_b.id,
        numero="FAC-00001",
        caja_id=caja_b.id,
        vendedor_id=user_b.id,
        subtotal=1000,
        total=1190,
        iva=190,
        metodo_pago="efectivo",
        estado="completada"
    )
    db_session.add(venta_b)
    await db_session.commit()
    
    # Query desde Tenant A
    result_a = await db_session.execute(
        select(Venta).where(Venta.tenant_id == tenant_a.id)
    )
    ventas_a = result_a.scalars().all()
    
    assert len(ventas_a) == 1, "Tenant A debe ver 1 venta"
    assert ventas_a[0].numero == "FAC-00001"
    
    # Query desde Tenant B
    result_b = await db_session.execute(
        select(Venta).where(Venta.tenant_id == tenant_b.id)
    )
    ventas_b = result_b.scalars().all()
    
    assert len(ventas_b) == 1, "Tenant B debe ver 1 venta"
    assert ventas_b[0].numero == "FAC-00001"
    
    # Verificar que son objetos diferentes
    assert ventas_a[0].id != ventas_b[0].id, "Las ventas deben ser diferentes"
    
    print("✅ TEST 3C PASÓ: Ventas completamente aisladas")


@pytest.mark.asyncio
async def test_inventario_aislado(
    db_session: AsyncSession,
    tenant_a,
    tenant_b,
    producto_a,
    producto_b,
    user_a
):
    """
    CASO: Inventario también está aislado
    
    RESULTADO ESPERADO: Cada tenant ve solo su inventario
    """
    
    # Query inventario desde Tenant A
    result_a = await db_session.execute(
        select(Inventario).where(Inventario.tenant_id == tenant_a.id)
    )
    inv_a = result_a.scalars().all()
    
    assert len(inv_a) == 1, "Tenant A debe ver 1 inventario"
    assert inv_a[0].producto_id == producto_a.id
    
    # Query inventario desde Tenant B
    result_b = await db_session.execute(
        select(Inventario).where(Inventario.tenant_id == tenant_b.id)
    )
    inv_b = result_b.scalars().all()
    
    assert len(inv_b) == 1, "Tenant B debe ver 1 inventario"
    assert inv_b[0].producto_id == producto_b.id
    
    print("✅ TEST 3D PASÓ: Inventario aislado por tenant")


@pytest.mark.asyncio
async def test_clientes_aislados(
    db_session: AsyncSession,
    tenant_a,
    tenant_b,
    user_a
):
    """
    CASO: Clientes también aislados
    """
    
    # Crear cliente A
    cliente_a = Cliente(
        tenant_id=tenant_a.id,
        tipo_documento="CC",
        documento="12345678",
        nombre="Cliente A",
        estado="activo"
    )
    db_session.add(cliente_a)
    
    # Crear cliente B
    cliente_b = Cliente(
        tenant_id=tenant_b.id,
        tipo_documento="CC",
        documento="87654321",
        nombre="Cliente B",
        estado="activo"
    )
    db_session.add(cliente_b)
    await db_session.commit()
    
    # Query desde A
    result_a = await db_session.execute(
        select(Cliente).where(Cliente.tenant_id == tenant_a.id)
    )
    clientes_a = result_a.scalars().all()
    
    assert len(clientes_a) == 1
    assert clientes_a[0].nombre == "Cliente A"
    
    # Query desde B
    result_b = await db_session.execute(
        select(Cliente).where(Cliente.tenant_id == tenant_b.id)
    )
    clientes_b = result_b.scalars().all()
    
    assert len(clientes_b) == 1
    assert clientes_b[0].nombre == "Cliente B"
    
    print("✅ TEST 3E PASÓ: Clientes aislados por tenant")


@pytest.mark.asyncio
async def test_movimientos_inventario_aislados(
    db_session: AsyncSession,
    tenant_a,
    tenant_b,
    producto_a,
    producto_b,
    user_a,
    user_b
):
    """
    CASO: Movimientos de inventario aislados
    """
    from app.modules.productos.models import InventarioMovimiento
    
    # Crear movimiento para A
    mov_a = InventarioMovimiento(
        tenant_id=tenant_a.id,
        producto_id=producto_a.id,
        tipo="entrada",
        cantidad=10,
        documento_ref="TEST-A",
        user_id=user_a.id
    )
    db_session.add(mov_a)
    
    # Crear movimiento para B
    mov_b = InventarioMovimiento(
        tenant_id=tenant_b.id,
        producto_id=producto_b.id,
        tipo="salida",
        cantidad=5,
        documento_ref="TEST-B",
        user_id=user_b.id
    )
    db_session.add(mov_b)
    await db_session.commit()
    
    # Query desde A
    result_a = await db_session.execute(
        select(InventarioMovimiento).where(
            InventarioMovimiento.tenant_id == tenant_a.id
        )
    )
    movimientos_a = result_a.scalars().all()
    
    assert len(movimientos_a) == 1
    assert movimientos_a[0].documento_ref == "TEST-A"
    
    # Query desde B
    result_b = await db_session.execute(
        select(InventarioMovimiento).where(
            InventarioMovimiento.tenant_id == tenant_b.id
        )
    )
    movimientos_b = result_b.scalars().all()
    
    assert len(movimientos_b) == 1
    assert movimientos_b[0].documento_ref == "TEST-B"
    
    print("✅ TEST 3F PASÓ: Movimientos de inventario aislados")