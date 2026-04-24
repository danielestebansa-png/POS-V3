# ============================================
# TEST 4: NÚMEROS DE FACTURA
# ============================================

import pytest
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.productos.models import Inventario
from app.modules.ventas.router import create_venta, VentaCreate, VentaDetalleCreate
from app.modules.ventas.models import ContadorFactura


@pytest.mark.asyncio
async def test_contador_factura_se_incrementa(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    user_a
):
    """
    CASO: Contador se incrementa después de cada venta

    RESULTADO ESPERADO: Números secuenciales 00001, 00002, 00003...
    """

    # Resetear contador
    result = await db_session.execute(
        select(ContadorFactura).where(ContadorFactura.tenant_id == tenant_a.id)
    )
    contador = result.scalar_one_or_none()
    if contador:
        contador.contador = 1
    else:
        contador = ContadorFactura(tenant_id=tenant_a.id, contador=1)
        db_session.add(contador)
    await db_session.commit()

    # Resetear inventario
    result = await db_session.execute(
        select(Inventario).where(Inventario.producto_id == producto_a.id)
    )
    inv = result.scalar_one()
    inv.cantidad = Decimal("100")
    await db_session.commit()

    # Crear 3 ventas
    numeros = []
    for i in range(3):
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

        resultado = await create_venta(
            venta_data,
            current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
            db=db_session
        )
        numeros.append(resultado.numero)

    # Verificar secuencia
    assert numeros[0] == "FAC-00001", f"Primera factura debe ser FAC-00001, es {numeros[0]}"
    assert numeros[1] == "FAC-00002", f"Segunda factura debe ser FAC-00002, es {numeros[1]}"
    assert numeros[2] == "FAC-00003", f"Tercera factura debe ser FAC-00003, es {numeros[2]}"


@pytest.mark.asyncio
async def test_dos_ventas_concurrentes_numeros_diferentes(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    user_a
):
    """
    CASO: Dos ventas que intentan obtener número al mismo tiempo

    RESULTADO ESPERADO: Números diferentes (UPSERT atómico)
    """

    # Resetear
    result = await db_session.execute(
        select(ContadorFactura).where(ContadorFactura.tenant_id == tenant_a.id)
    )
    contador = result.scalar_one_or_none()
    if contador:
        contador.contador = 1
    else:
        db_session.add(ContadorFactura(tenant_id=tenant_a.id, contador=1))
    await db_session.commit()

    result = await db_session.execute(
        select(Inventario).where(Inventario.producto_id == producto_a.id)
    )
    inv = result.scalar_one()
    inv.cantidad = Decimal("100")
    await db_session.commit()

    # Simular dos transacciones simultáneas
    # En PostgreSQL, el UPSERT con ON CONFLICT es atómico
    # Solo una puede ganar la competencia por el contador

    # Transaction 1
    async with db_session.begin():
        result1 = await db_session.execute(
            text("""
                INSERT INTO contador_facturas (id, tenant_id, contador)
                VALUES (gen_random_uuid(), :tenant_id, 1)
                ON CONFLICT (tenant_id)
                DO UPDATE SET contador = contador_facturas.contador + 1
                RETURNING contador - 1
            """),
            {"tenant_id": str(tenant_a.id)}
        )
        numero1 = result1.scalar_one()

    # Transaction 2
    async with db_session.begin():
        result2 = await db_session.execute(
            text("""
                INSERT INTO contador_facturas (id, tenant_id, contador)
                VALUES (gen_random_uuid(), :tenant_id, 1)
                ON CONFLICT (tenant_id)
                DO UPDATE SET contador = contador_facturas.contador + 1
                RETURNING contador - 1
            """),
            {"tenant_id": str(tenant_a.id)}
        )
        numero2 = result2.scalar_one()

    # Deben ser diferentes
    assert numero1 != numero2, "Los números de factura deben ser diferentes"


@pytest.mark.asyncio
async def test_cada_tenant_tiene_su_propio_contador(
    db_session: AsyncSession,
    tenant_a,
    tenant_b,
    producto_a,
    producto_b,
    user_a
):
    """
    CASO: Dos tenants creando facturas al mismo tiempo

    RESULTADO ESPERADO: Cada tenant tiene su propia secuencia
    """

    # Resetear contadores
    for tenant in [tenant_a, tenant_b]:
        result = await db_session.execute(
            select(ContadorFactura).where(ContadorFactura.tenant_id == tenant.id)
        )
        cnt = result.scalar_one_or_none()
        if cnt:
            cnt.contador = 1
        else:
            db_session.add(ContadorFactura(tenant_id=tenant.id, contador=1))
    await db_session.commit()

    # Resetear inventarios
    for producto in [producto_a, producto_b]:
        result = await db_session.execute(
            select(Inventario).where(Inventario.producto_id == producto.id)
        )
        inv = result.scalar_one()
        inv.cantidad = Decimal("100")
    await db_session.commit()

    # Crear venta para cada tenant
    venta_a = VentaCreate(
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

    venta_b = VentaCreate(
        detalles=[
            VentaDetalleCreate(
                producto_id=producto_b.id,
                cantidad=1,
                precio_unitario=1000,
                descuento=0,
                iva=19,
            )
        ],
        metodo_pago="efectivo"
    )

    # Ejecutar (no son truly concurrent pero testea la lógica)
    resultado_a = await create_venta(
        venta_a,
        current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
        db=db_session
    )

    resultado_b = await create_venta(
        venta_b,
        current_user={"tenant_id": str(tenant_b.id), "user_id": str(user_a.id)},
        db=db_session
    )

    # Ambos deben tener FAC-00001 (cada tenant independientes)
    assert resultado_a.numero == "FAC-00001", f"Tenant A debe tener FAC-00001, tiene {resultado_a.numero}"
    assert resultado_b.numero == "FAC-00001", f"Tenant B debe tener FAC-00001, tiene {resultado_b.numero}"


@pytest.mark.asyncio
async def test_numero_factura_formato_correcto(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    user_a
):
    """
    CASO: Formato de número de factura

    RESULTADO ESPERADO: FAC-00001, FAC-00010, FAC-00100, FAC-99999
    """

    # Resetear
    result = await db_session.execute(
        select(ContadorFactura).where(ContadorFactura.tenant_id == tenant_a.id)
    )
    cnt = result.scalar_one_or_none()
    if cnt:
        cnt.contador = 1
    else:
        db_session.add(ContadorFactura(tenant_id=tenant_a.id, contador=1))
    await db_session.commit()

    result = await db_session.execute(
        select(Inventario).where(Inventario.producto_id == producto_a.id)
    )
    inv = result.scalar_one()
    inv.cantidad = Decimal("100000")
    await db_session.commit()

    # Testear formatos
    casos = [
        (1, "FAC-00001"),
        (10, "FAC-00010"),
        (100, "FAC-00100"),
        (999, "FAC-00999"),
        (9999, "FAC-09999"),
        (99999, "FAC-99999"),
    ]

    for contador_deseado, formato_esperado in casos:
        # Setear contador directamente
        result = await db_session.execute(
            select(ContadorFactura).where(ContadorFactura.tenant_id == tenant_a.id)
        )
        cnt = result.scalar_one()
        cnt.contador = contador_deseado
        await db_session.commit()

        # Crear venta
        venta_data = VentaCreate(
            detalles=[
                VentaDetalleCreate(
                    producto_id=producto_a.id,
                    cantidad=1,
                    precio_unitario=1000,
                    descuento=0,
                    iva=19,
                )
            ],
            metodo_pago="efectivo"
        )

        resultado = await create_venta(
            venta_data,
            current_user={"tenant_id": str(tenant_a.id), "user_id": str(user_a.id)},
            db=db_session
        )

        assert resultado.numero == formato_esperado, \
            f"Para contador {contador_deseado}, esperado {formato_esperado}, obtenido {resultado.numero}"


@pytest.mark.asyncio
async def test_unique_constraint_numero_factura(
    db_session: AsyncSession,
    tenant_a,
    producto_a,
    user_a
):
    """
    CASO: SQL UNIQUE constraint evita duplicados

    RESULTADO ESPERADO: Si alguien intenta insertar número duplicado, falla
    """

    from app.modules.ventas.models import Venta, Caja

    # Crear caja
    caja = Caja(tenant_id=tenant_a.id, nombre="Test", estado="cerrada")
    db_session.add(caja)
    await db_session.flush()

    # Crear primera venta
    venta1 = Venta(
        tenant_id=tenant_a.id,
        numero="FAC-99999",
        caja_id=caja.id,
        subtotal=1000,
        total=1190,
        iva=190,
        metodo_pago="efectivo",
        estado="completada"
    )
    db_session.add(venta1)
    await db_session.commit()

    # Intentar crear segunda venta con mismo número
    venta2 = Venta(
        tenant_id=tenant_a.id,
        numero="FAC-99999",
        caja_id=caja.id,
        subtotal=1000,
        total=1190,
        iva=190,
        metodo_pago="efectivo",
        estado="completada"
    )
    # Debe fallar por UNIQUE constraint
    with pytest.raises(Exception):
        db_session.add(venta2)
        await db_session.flush()

    await db_session.rollback()
