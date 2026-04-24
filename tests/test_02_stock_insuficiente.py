# ============================================
# TEST 2: STOCK INSUFICIENTE
# ============================================

import pytest
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.productos.models import Inventario
from app.modules.ventas.router import create_venta, VentaCreate, VentaDetalleCreate


@pytest.mark.asyncio
async def test_venta_rechazada_por_stock_insuficiente(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    user_a
):
    """
    CASO: Venta con cantidad mayor al stock disponible

    ESCENARIO:
    - Producto: stock = 10, permite_stock_negativo = False
    - Venta: cantidad = 15

    RESULTADO ESPERADO:
    - Venta rechazada con error "Stock insuficiente"
    - Stock permanece en 10 (no se modifica)
    """

    # Verificar estado inicial
    result = await db_session.execute(
        select(Inventario).where(Inventario.producto_id == str(producto_a.id))
    )
    inventario = result.scalar_one()
    assert inventario.cantidad == Decimal("10"), "Stock inicial debe ser 10"

    # Intentar vender 15 unidades
    venta_data = VentaCreate(
        detalles=[
            VentaDetalleCreate(
                producto_id=producto_a.id,
                cantidad=15,
                precio_unitario=2000,
                descuento=0,
                iva=19,
            )
        ],
        metodo_pago="efectivo"
    )

    # Debe lanzar HTTPException con "Stock insuficiente"
    with pytest.raises(Exception) as exc_info:
        await create_venta(
            venta_data,
            current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
            db=db_session
        )

    assert "Stock insuficiente" in str(exc_info.value), \
        f"Mensaje debe contener 'Stock insuficiente',got: {exc_info.value}"

    # Verificar que stock NO cambió
    # Verificar que stock NO cambió: usar SELECT (buscar por id guardado)
    producto_id_str = str(producto_a.id)
    result = await db_session.execute(select(Inventario).where(Inventario.producto_id == producto_id_str))
    inventario = result.scalar_one_or_none()
    assert inventario is not None, "Inventario debería existir"
    # El stock debe seguir en 10 porque la venta falló
    assert inventario.cantidad == Decimal("10"), "Stock debe permanecer sin cambios"


@pytest.mark.asyncio
async def test_venta_exactamente_igual_al_stock_pasa(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    user_a
):
    """
    CASO: Venta con cantidad exactamente igual al stock

    RESULTADO ESPERADO: Venta exitosa, stock = 0
    """

    # Resetear stock a 10
    result = await db_session.execute(
        select(Inventario).where(Inventario.producto_id == str(producto_a.id))
    )
    inventario = result.scalar_one()
    inventario.cantidad = Decimal("10")
    await db_session.commit()

    venta_data = VentaCreate(
        detalles=[
            VentaDetalleCreate(
                producto_id=producto_a.id,
                cantidad=10,
                precio_unitario=2000,
                descuento=0,
                iva=19,
            )
        ],
        metodo_pago="efectivo"
    )

    # Debe pasar
    resultado = await create_venta(
        venta_data,
        current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
        db=db_session
    )

    assert resultado is not None, "Venta debe ser exitosa"

    # Verificar stock = 0
    # Verificar que stock NO cambió: usar SELECT (buscar por id guardado)
    producto_id_str = str(producto_a.id)
    result = await db_session.execute(select(Inventario).where(Inventario.producto_id == producto_id_str))
    inventario = result.scalar_one_or_none()
    assert inventario is not None, "Inventario debería existir"
    # El stock debe seguir en 10 porque la venta falló
    assert inventario.cantidad == Decimal("0"), "Stock debe ser 0"


@pytest.mark.asyncio
async def test_venta_con_stock_cero_falla(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    user_a
):
    """
    CASO: Producto con stock 0

    RESULTADO ESPERADO: Venta rechazada
    """

    # Poner stock en 0
    result = await db_session.execute(
        select(Inventario).where(Inventario.producto_id == str(producto_a.id))
    )
    inventario = result.scalar_one()
    inventario.cantidad = Decimal("0")
    await db_session.commit()

    venta_data = VentaCreate(
        detalles=[
            VentaDetalleCreate(
                producto_id=producto_a.id,
                cantidad=1,
                precio_unitario=2000,
                descuento=0,
                iva=19,
            )
        ],
        metodo_pago="efectivo"
    )

    with pytest.raises(Exception) as exc_info:
        await create_venta(
            venta_data,
            current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
            db=db_session
        )

    assert "Stock insuficiente" in str(exc_info.value)


@pytest.mark.asyncio
async def test_multiple_items_stock_insuficiente(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    user_a
):
    """
    CASO: Venta con múltiples items, uno sin stock

    RESULTADO ESPERADO: Toda la venta rechazada (transacción atómica)
    """

    # Resetear stock a 10
    result = await db_session.execute(
        select(Inventario).where(Inventario.producto_id == str(producto_a.id))
    )
    inventario = result.scalar_one()
    inventario.cantidad = Decimal("10")
    await db_session.commit()

    # Crear segundo producto con poco stock
    from app.modules.productos.models import Producto, Categoria
    categoria = Categoria(
        tenant_id=tenant_a.id,
        nombre="Test",
        estado="activo"
    )
    db_session.add(categoria)
    await db_session.flush()

    producto2 = Producto(
        tenant_id=tenant_a.id,
        nombre="Producto 2",
        precio_venta=1000,
        iva=19,
        permite_stock_negativo=False,
        estado="activo",
        categoria_id=categoria.id
    )
    db_session.add(producto2)
    await db_session.flush()

    inventario2 = Inventario(
        tenant_id=tenant_a.id,
        producto_id=producto2.id,
        cantidad=1,
        stock_minimo=1
    )
    db_session.add(inventario2)
    await db_session.commit()

    # Venta con: 5 de producto_a (hay 10) + 5 de producto2 (hay 1)
    venta_data = VentaCreate(
        detalles=[
            VentaDetalleCreate(
                producto_id=producto_a.id,
                cantidad=5,
                precio_unitario=2000,
                descuento=0,
                iva=19,
            ),
            VentaDetalleCreate(
                producto_id=producto2.id,
                cantidad=5,
                precio_unitario=1000,
                descuento=0,
                iva=19,
            )
        ],
        metodo_pago="efectivo"
    )

    # Debe fallar por el segundo producto
    with pytest.raises(Exception) as exc_info:
        await create_venta(
            venta_data,
            current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
            db=db_session
        )

    assert "Stock insuficiente" in str(exc_info.value)
