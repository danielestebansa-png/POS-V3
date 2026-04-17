import React from 'react'

export default function ReceiptModal({ venta, onClose }) {
  if (!venta) return null
  
  const fecha = new Date().toLocaleDateString('es-CO', { 
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })

  const calcularSubtotal = (precio, cantidad, iva) => {
    return precio * cantidad
  }
  
  const calcular_total = () => {
    if (!venta.detalles) return 0
    return venta.detalles.reduce((sum, d) => sum + Number(d.subtotal || 0), 0)
  }

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-60 flex items-center justify-center z-50">
      {/* Factura completa */}
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md mx-4 max-h-[90vh] overflow-auto" id="factura">
        
        {/* Header con X para cerrar */}
        <div className="flex justify-between items-start p-4 border-b border-gray-200 bg-gray-50">
          <div>
            <h2 className="text-lg font-bold text-gray-800">🧾 FACTURA DE VENTA</h2>
            <p className="text-xs text-gray-500">No. {venta.numero_factura}</p>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold w-8 h-8 flex items-center justify-center"
          >
            ✕
          </button>
        </div>
        
        {/* Info negocio */}
        <div className="p-4 border-b border-gray-100 text-center">
          <h3 className="font-bold text-gray-800">Mi Papelería</h3>
          <p className="text-xs text-gray-500">NIT: 123456789-0</p>
          <p className="text-xs text-gray-500">{fecha}</p>
        </div>
        
        {/* Productos comprados */}
        <div className="p-4">
          <table className="w-full text-xs">
            <thead className="border-b-2 border-gray-300">
              <tr>
                <th className="text-left py-2 text-gray-600">Producto</th>
                <th className="text-center py-2 text-gray-600">Cant</th>
                <th className="text-right py-2 text-gray-600">Precio</th>
                <th className="text-right py-2 text-gray-600">Total</th>
              </tr>
            </thead>
            <tbody>
              {venta.detalles?.map((detalle, idx) => (
                <tr key={idx} className="border-b border-gray-100">
                  <td className="py-2 text-gray-800">{detalle.nombre_producto}</td>
                  <td className="text-center py-2 text-gray-800">{detalle.cantidad}</td>
                  <td className="text-right py-2 text-gray-800">${Number(detalle.precio_unitario).toLocaleString()}</td>
                  <td className="text-right py-2 text-gray-800 font-medium">${Number(detalle.subtotal || detalle.cantidad * detalle.precio_unitario).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Totales */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Subtotal:</span>
            <span>${calcular_total().toLocaleString()}</span>
          </div>
          <div className="flex justify-between text-sm text-gray-600">
            <span>IVA (19%):</span>
            <span>$0</span>
          </div>
          <div className="flex justify-between text-lg font-bold text-gray-800 border-t border-gray-200 pt-2 mt-2">
            <span>TOTAL A PAGAR:</span>
            <span className="text-emerald-600">${Number(venta.total).toLocaleString()}</span>
          </div>
          
          {/* Método de pago */}
          <div className="mt-3 text-center text-sm text-gray-500">
            <span className="bg-gray-200 px-3 py-1 rounded">
              Pago: {venta.metodo_pago?.toUpperCase()}
            </span>
          </div>
        </div>
        
        {/* Footer */}
        <div className="p-4 border-t border-gray-200 text-center">
          <p className="text-xs text-gray-400">Gracias por su compra</p>
          <p className="text-xs text-gray-400">Sistema POS - Mi Papelería</p>
        </div>
        
        {/* Botones */}
        <div className="p-4 border-t border-gray-200 flex gap-2">
          {/* Nueva - primero, principal */}
          <button 
            onClick={onClose}
            className="flex-1 bg-emerald-600 text-white py-3 rounded-lg hover:bg-emerald-700 font-medium"
          >
            ➕ Nueva Venta
          </button>
          
          {/* Imprimir - segundo */}
          <button 
            onClick={() => window.print()}
            className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 font-medium"
          >
            🖨️ Imprimir
          </button>
        </div>
      </div>
    </div>
  )
}
