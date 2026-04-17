import React, { useState } from 'react'

export default function SalesTabs({ carts, activeCart, onSwitchCart, onNewCart, onCloseCart }) {
  const [hoveredTab, setHoveredTab] = useState(null)

  return (
    <div className="flex items-center gap-0 overflow-x-auto pb-0">
      {/* Tabs estilo Excel simples */}
      {carts.map((cart, index) => (
        <div
          key={index}
          onMouseEnter={() => setHoveredTab(index)}
          onMouseLeave={() => setHoveredTab(null)}
          className="relative"
        >
          <button
            onClick={() => onSwitchCart(index)}
            className={`
              relative px-4 py-2 text-sm font-medium transition-colors
              ${activeCart === index 
                ? 'bg-white text-gray-800 border-t border-l border-r border-gray-200 rounded-t' 
                : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
              }
            `}
          >
            {cart.nombre || `Venta ${index + 1}`}
            {cart.items.length > 0 && (
              <span className={`ml-1.5 text-xs px-1.5 py-0.5 rounded ${activeCart === index ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-200 text-gray-600'}`}>
                {cart.items.length}
              </span>
            )}
          </button>
          
          {/* Botón X para cerrar al hover */}
          {(hoveredTab === index) && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onCloseCart(index)
              }}
              className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white rounded-full text-[10px] flex items-center justify-center hover:bg-red-600 z-10"
            >
              ✕
            </button>
          )}
          
          {/* Línea separadora */}
          {index < carts.length - 1 && (
            <span className="absolute right-0 top-2 bottom-2 w-px bg-gray-300" />
          )}
        </div>
      ))}
      
      {/* Botón + nueva venta */}
      <button
        onClick={onNewCart}
        className="px-4 py-2 text-sm text-emerald-600 hover:bg-emerald-50 font-medium transition rounded-t"
      >
        + Nueva
      </button>
    </div>
  )
}
