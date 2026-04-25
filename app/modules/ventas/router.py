from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.productos.models import User, Producto
from app.modules.ventas.models import Venta, VentaDetalle
from decimal import Decimal
from uuid import uuid4
from datetime import datetime
import json

router = APIRouter()

@router.get("/ventas/hoy")
async def get_ventas_hoy(current_user: User = Depends(get_current_user)):
    """Get today's sales"""
    db = await get_db().__anext__()
    try:
        from datetime import datetime, timedelta
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        result = await db.execute(
            select(Venta).where(
                and_(
                    Venta.tenant_id == current_user.tenant_id,
                    Venta.created_at >= today_start
                )
            ).order_by(Venta.created_at.desc())
        )
        ventas = result.scalars().all()
        
        return [{"id": str(v.id), "numero": v.numero, "total": float(v.total or 0), "created_at": v.created_at.isoformat() if v.created_at else None} for v in ventas]
    finally:
        await db.close()

@router.get("/ventas/{venta_id}")
async def get_venta(venta_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific sale"""
    db = await get_db().__anext__()
    try:
        result = await db.execute(
            select(Venta).where(
                and_(
                    Venta.id == venta_id,
                    Venta.tenant_id == current_user.tenant_id
                )
            )
        )
        venta = result.scalar_one_or_none()
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        
        return {
            "id": str(venta.id),
            "numero": venta.numero,
            "total": float(venta.total or 0),
            "created_at": venta.created_at.isoformat() if venta.created_at else None
        }
    finally:
        await db.close()

@router.post("/ventas/")
async def crear_venta(request_data: dict, current_user: User = Depends(get_current_user)):
    """Create a new sale"""
    db = await get_db().__anext__()
    tenant_id = current_user.tenant_id
    
    try:
        detalles = request_data.get("detalles", [])
        metodo_pago = request_data.get("metodo_pago", "efectivo")
        cliente_id = request_data.get("cliente_id")
        
        if not detalles:
            raise HTTPException(status_code=400, detail="La venta debe tener detalles")
        
        # Get next invoice number
        from sqlalchemy import text
        result = await db.execute(text("""
            INSERT INTO contador_facturas (id, tenant_id, contador) 
            VALUES (gen_random_uuid(), :tenant, 1) 
            ON CONFLICT (tenant_id) 
            DO UPDATE SET contador = contador_facturas.contador + 1 
            RETURNING contador - 1
        """), {"tenant": tenant_id})
        numero = result.scalar() or 1
        
        venta_id = str(uuid4())
        subtotal = Decimal("0")
        total_iva = Decimal("0")
        total_descuento = Decimal("0")
        
        # Process each item
        for item in detalles:
            producto_id = item.get("producto_id")
            cantidad = Decimal(str(item.get("cantidad", 1)))
            precio_unitario = Decimal(str(item.get("precio_unitario", 0)))
            descuento = Decimal(str(item.get("descuento", 0)))
            iva = Decimal(str(item.get("iva", 0)))
            
            # Get product
            result = await db.execute(
                select(Producto).where(
                    and_(
                        Producto.id == producto_id,
                        Producto.tenant_id == tenant_id
                    )
                ).with_for_update()
            )
            producto = result.scalar_one_or_none()
            
            if not producto:
                raise HTTPException(status_code=400, detail=f"Producto no encontrado: {producto_id}")
            
            # Check stock (simple validation)
            if not getattr(producto, 'permite_stock_negativo', False):
                stock_actual = getattr(producto, 'stock', None) or Decimal("0")
                if stock_actual < cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente: {producto.nombre}. Disp: {stock_actual}, Sol: {cantidad}"
                    )
            
            # Calculate totals
            precio = Decimal(str(precio_unitario))
            subtotal_item = precio * cantidad
            descuento_item = subtotal_item * (descuento / Decimal("100"))
            iva_item = (subtotal_item - descuento_item) * (iva / Decimal("100"))
            
            subtotal += subtotal_item - descuento_item
            total_iva += iva_item
            total_descuento += descuento_item
            
            # Create sale detail
            detalle_id = str(uuid4())
            await db.execute(text("""
                INSERT INTO venta_detalles (id, tenant_id, venta_id, producto_id, cantidad, precio_unitario, descuento, iva, created_at)
                VALUES (:id, :tenant, :venta, :producto, :cantidad, :precio, :descuento, :iva, NOW())
            """), {
                "id": detalle_id,
                "tenant": tenant_id,
                "venta": venta_id,
                "producto": producto_id,
                "cantidad": float(cantidad),
                "precio": float(precio_unitario),
                "descuento": float(descuento),
                "iva": float(iva)
            })
            
            # Update product stock
            if hasattr(producto, 'stock') and producto.stock is not None:
                new_stock = int((producto.stock or 0) - cantidad)
                await db.execute(text("""
                    UPDATE productos SET stock = :new_stock, updated_at = NOW()
                    WHERE id = :producto_id AND tenant_id = :tenant
                """), {"new_stock": new_stock, "producto_id": producto_id, "tenant": tenant_id})
        
        # Create sale
        total = subtotal + total_iva
        
        await db.execute(text("""
            INSERT INTO ventas (id, tenant_id, numero, cliente_id, metodo_pago, subtotal, impuesto, descuento, total, user_id, created_at, updated_at)
            VALUES (:id, :tenant, :numero, :cliente, :metodo, :subtotal, :impuesto, :descuento, :total, :user, NOW(), NOW())
        """), {
            "id": venta_id,
            "tenant": tenant_id,
            "numero": f"FVC-{numero:06d}",
            "cliente": cliente_id,
            "metodo": metodo_pago,
            "subtotal": float(subtotal),
            "impuesto": float(total_iva),
            "descuento": float(total_descuento),
            "total": float(total),
            "user": current_user.id
        })
        
        await db.commit()
        
        return {
            "id": venta_id,
            "numero": f"FVC-{numero:06d}",
            "total": float(total),
            "message": "Venta creada exitosamente"
        }
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar venta: {str(e)}")
    finally:
        await db.close()
