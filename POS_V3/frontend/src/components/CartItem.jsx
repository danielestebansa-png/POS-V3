import React from 'react'

export default function CartItem({ item, onRemove, onUpdateQuantity }) {
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-gray-800 truncate">{item.product.nombre}</h4>
        <p className="text-sm text-gray-500">
          ${Number(item.product.precio_venta).toLocaleString('es-CO')} c/u
        </p>
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onUpdateQuantity(item.product.id, item.quantity - 1)}
          className="w-8 h-8 rounded-lg bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-gray-600 transition-colors"
        >
          -
        </button>
        
        <span className="w-10 text-center font-semibold text-gray-800">
          {item.quantity}
        </span>
        
        <button
          onClick={() => onUpdateQuantity(item.product.id, item.quantity + 1)}
          className="w-8 h-8 rounded-lg bg-primary-100 hover:bg-primary-200 flex items-center justify-center text-primary-600 transition-colors"
        >
          +
        </button>
      </div>
      
      <div className="ml-4 text-right min-w-[80px]">
        <p className="font-bold text-gray-800">
          ${item.subtotal.toLocaleString('es-CO')}
        </p>
        <button
          onClick={() => onRemove(item.product.id)}
          className="text-xs text-red-500 hover:text-red-700 transition-colors"
        >
          Eliminar
        </button>
      </div>
    </div>
  )
}
