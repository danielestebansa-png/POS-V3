# ============================================
# MODELS - VENTAS
# Los modelos ya están definidos en productos/models.py
# Este archivo mantiene compatibilidad con imports existentes
# ============================================

# Re-exportar desde productos/models para compatibilidad
from app.modules.productos.models import (
    Venta,
    VentaDetalle,
    Caja,
    ContadorFactura
)

__all__ = ['Venta', 'VentaDetalle', 'Caja', 'ContadorFactura']