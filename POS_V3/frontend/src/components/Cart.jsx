import React, { useState } from 'react'
import CartItem from './CartItem'

export default function Cart({ items, onRemove, onUpdateQuantity, onClear, onCobrar }) {
  const [metodoPago, setMetodoPago] = useState('efectivo')
  
  const total = items.reduce((sum, item) => sum + item.subtotal, 0)
  const cantidadItems = items.reduce((sum, item) => sum + item.quantity, 0)

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 flex flex-col h-full">
      {/* Header del carrito */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-800 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            Carrito
          </h2>
          <span className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm font-medium">
            {cantidadItems} items
          </span>
        </div>
      </div>

      {/* Lista deitems */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-40 text-gray-400">
            <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <p>El carrito está vacío</p>
            <p className="text-sm">Agrega productos del grid</p>
          </div>
        ) : (
          items.map((item) => (
            <CartItem
              key={item.product.id}
              item={item}
              onRemove={onRemove}
              onUpdateQuantity={onUpdateQuantity}
            />
          ))
        )}
      </div>

      {/* Total y acciones */}
      {items.length > 0 && (
        <div className="p-4 border-t border-gray-200 space-y-4">
          {/* Método de pago */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Método de pago
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => setMetodoPago('efectivo')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  metodoPago === 'efectivo'
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                💵 Efectivo
              </button>
              <button
                onClick={() => setMetodoPago('tarjeta')}
                className={`p-3 rounded-lg border-2 transition-all ${
                  metodoPago === 'tarjeta'
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                💳 Tarjeta
              </button>
            </div>
          </div>

          {/* Total */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total:</span>
              <span className="text-3xl font-bold text-primary-600">
                ${total.toLocaleString('es-CO')}
              </span>
            </div>
          </div>

          {/* Botones de acción */}
          <div className="space-y-2">
            <button
              onClick={() => onCobrar(metodoPago)}
              className="w-full py-4 bg-green-500 hover:bg-green-600 text-white text-lg font-bold rounded-xl transition-colors shadow-lg shadow-green-200"
            >
              💰 COBRAR
            </button>
            <button
              onClick={onClear}
              className="w-full py-2 text-red-500 hover:text-red-700 text-sm font-medium transition-colors"
            >
              Vaciar carrito
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
