import React from 'react'

export default function FacturaModal({ venta, onClose }) {
  if (!venta) return null

  // Función para formatear precio
  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP'
    }).format(price)
  }

  // Función para formatear fecha
  const formatDate = () => {
    return new Date().toLocaleString('es-CO', {
      dateStyle: 'medium',
      timeStyle: 'short'
    })
  }

  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-green-600 text-white p-4 rounded-t-lg text-center">
          <h2 className="text-xl font-bold">✅ Venta Exitosa</h2>
          <p className="text-sm">Gracias por su compra</p>
        </div>

        {/* Contenido del ticket */}
        <div className="p-4" id="factura-content">
          {/* Info de la venta */}
          <div className="text-center border-b pb-4 mb-4">
            <p className="text-2xl font-bold text-gray-800">{venta.numero}</p>
            <p className="text-gray-500 text-sm">{formatDate()}</p>
            <p className="text-gray-500 text-sm capitalize">Método: {venta.metodo_pago}</p>
          </div>

          {/* Productos */}
          <div className="border-b pb-4 mb-4">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-500 border-b">
                  <th className="text-left py-1">Producto</th>
                  <th className="text-center py-1">Cant</th>
                  <th className="text-right py-1">Precio</th>
                </tr>
              </thead>
              <tbody>
                {venta.detalles && venta.detalles.map((item, index) => (
                  <tr key={index} className="border-b border-gray-100">
                    <td className="py-1">{item.nombre_producto || 'Producto'}</td>
                    <td className="text-center py-1">{item.cantidad}</td>
                    <td className="text-right py-1">{formatPrice(item.precio_unitario)}</td>
                  </tr>
                ))}
                {/* Mostrar desde el carrito si no hay detalles en la respuesta */}
                {(!venta.detalles || venta.detalles.length === 0) && venta.detalles_carrito && (
                  <>
                    {venta.detalles_carrito.map((item, index) => (
                      <tr key={index} className="border-b border-gray-100">
                        <td className="py-1">{item.product?.nombre || 'Producto'}</td>
                        <td className="text-center py-1">{item.quantity}</td>
                        <td className="text-right py-1">{formatPrice(item.product?.precio_venta || item.precio_unitario)}</td>
                      </tr>
                    ))}
                  </>
                )}
              </tbody>
            </table>
          </div>

          {/* Totales */}
          <div className="space-y-2">
            <div className="flex justify-between text-gray-600">
              <span>Subtotal:</span>
              <span>{formatPrice(venta.subtotal)}</span>
            </div>
            {venta.descuento > 0 && (
              <div className="flex justify-between text-red-500">
                <span>Descuento:</span>
                <span>-{formatPrice(venta.descuento)}</span>
              </div>
            )}
            {venta.iva > 0 && (
              <div className="flex justify-between text-gray-600">
                <span>IVA:</span>
                <span>{formatPrice(venta.iva)}</span>
              </div>
            )}
            <div className="flex justify-between text-xl font-bold text-gray-800 pt-2 border-t">
              <span>TOTAL:</span>
              <span>{formatPrice(venta.total)}</span>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-6 pt-4 border-t text-gray-500 text-xs">
            <p>Sistema POS - Punto de Venta</p>
            <p>Gracias por preferirnos</p>
          </div>
        </div>

        {/* Botones */}
        <div className="p-4 border-t flex gap-2">
          <button
            onClick={onClose}
            className="flex-1 bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600 transition-colors"
          >
            Cerrar
          </button>
          <button
            onClick={handlePrint}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Imprimir
          </button>
        </div>
      </div>
    </div>
  )
}