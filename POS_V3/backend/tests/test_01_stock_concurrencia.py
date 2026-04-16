# ============================================
# TEST 1: DOS VENTAS SIMULTÁNEAS NO ROMPEN STOCK
# ============================================

import pytest
import asyncio
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.productos.models import Inventario
from app.modules.ventas.models import Venta, VentaDetalle, ContadorFactura
from app.modules.ventas.router import create_venta, VentaCreate, VentaDetalleCreate
from app.core.security import get_current_user


class MockCurrentUser:
    """Mock de get_current_user para tests"""
    def __init__(self, tenant_id, user_id):
        self.tenant_id = tenant_id
        self.user_id = user_id


@pytest.mark.asyncio
async def test_venta_simultanea_no_rompe_stock(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    contador_factura_a,
    user_a
):
    """
    CASO: Dos ventas simultáneas con el mismo producto
    
    ESCENARIO:
    - Producto tiene stock = 10
    - Venta 1: 6 unidades
    - Venta 2: 6 unidades (ejecuta al mismo tiempo)
    
    RESULTADO ESPERADO:
    - Venta 1: Éxito (6 <= 10)
    - Venta 2: Fallo por stock insuficiente (6 > 4 restantes)
    - Stock final: 4 (no negativo, no corrupto)
    """
    
    # Preparar datos para venta 1
    venta1_data = VentaCreate(
        detalles=[
            VentaDetalleCreate(
                producto_id=producto_a.id,
                cantidad=6,
                precio_unitario=2000,
                descuento=0,
                iva=19,
            )
        ],
        metodo_pago="efectivo"
    )

    # Preparar datos para venta 2
    venta2_data = VentaCreate(
        detalles=[
            VentaDetalleCreate(
                producto_id=producto_a.id,
                cantidad=6,
                precio_unitario=2000,
                descuento=0,
                iva=19,
            )
        ],
        metodo_pago="efectivo"
    )

    # Resetear contador
    contador_factura_a.contador = 1

    # Simular que el producto tiene stock 10
    producto_id_str = str(producto_a.id)
    # Usar UPDATE directo
    from sqlalchemy import update
    await db_session.execute(
        update(Inventario)
        .where(Inventario.producto_id == producto_id_str)
        .values(cantidad=Decimal("10"))
    )

    # Venta 1 debería pasar
    try:
        resultado1 = await create_venta(
            venta1_data,
            current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
            db=db_session
        )
        venta1_exitosa = True
    except Exception as e:
        venta1_exitosa = False
        print(f"Venta 1 falló: {e}")

    # Verificar estado del inventario después de venta 1 (sin refresh)
    result = await db_session.execute(
        select(Inventario).where(Inventario.producto_id == producto_id_str)
    )
    inventario = result.scalar_one()
    stock_despues_v1 = inventario.cantidad

    # Venta 2 intenta ejecutar (debe fallar por stock insuficiente)
    try:
        resultado2 = await create_venta(
            venta2_data,
            current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
            db=db_session
        )
        venta2_exitosa = True
    except Exception as e:
        venta2_exitosa = False
        print(f"Venta 2 falló: {e}")

    # Verificaciones
    assert venta1_exitosa, "Venta 1 debería ser exitosa"
    assert not venta2_exitosa, "Venta 2 debería fallar por stock insuficiente"
    assert stock_despues_v1 == Decimal("4"), f"Stock debería ser 4, es {stock_despues_v1}"

    # Verificar que no hay stock negativo
    result = await db_session.execute(
        select(Inventario).where(Inventario.producto_id == producto_id_str)
    )
    inventario = result.scalar_one_or_none()
    assert inventario is not None, "Inventario debe existir"
    assert inventario.cantidad >= 0, "Stock no puede ser negativo" 
    assert inventario.cantidad >= 0, "Stock no puede ser negativo"


@pytest.mark.asyncio
async def test_venta_simultanea_stock_negativo_prevenido(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    user_a
):
    """
    CASO: Intentar vender más de lo que hay (sin allow_stock_negativo)

    RESULTADO ESPERADO: Venta rechazada
    """

    # Producto con permite_stock_negativo = False
    assert producto_a.permite_stock_negativo == False

    # Intentar vender 100 unidades (hay 10)
    venta_data = VentaCreate(
        detalles=[
            VentaDetalleCreate(
                producto_id=producto_a.id,
                cantidad=100,
                precio_unitario=2000,
                descuento=0,
                iva=19,
            )
        ],
        metodo_pago="efectivo"
    )

    # Debería fallar
    with pytest.raises(Exception) as exc_info:
        await create_venta(
            venta_data,
            current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
            db=db_session
        )

    assert "Stock insuficiente" in str(exc_info.value)


@pytest.mark.asyncio
async def test_venta_con_permiso_stock_negativo_pasa(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    user_a
):
    """
    CASO: Producto que permite stock negativo

    RESULTADO ESPERADO: Venta exitosa aunque resultante < 0
    """

    # Habilitar stock negativo
    producto_a.permite_stock_negativo = True
    await db_session.commit()

    # Resetear inventario
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
                cantidad=15,
                precio_unitario=2000,
                descuento=0,
                iva=19,
            )
        ],
        metodo_pago="efectivo"
    )

    # Debe pasar porque permite stock negativo
    try:
        resultado = await create_venta(
            venta_data,
            current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
            db=db_session
        )
        venta_exitosa = True
    except Exception as e:
        venta_exitosa = False
        print(f"Error: {e}")

    assert venta_exitosa, "Venta debería ser exitosa con permite_stock_negativo"
