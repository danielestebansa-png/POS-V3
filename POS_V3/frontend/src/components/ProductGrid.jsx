import React from 'react'

export default function ProductGrid({ productos, onSelectProduct }) {
  if (!productos || productos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p className="text-lg">No hay productos disponibles</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
      {productos.map((producto) => (
        <button
          key={producto.id}
          onClick={() => onSelectProduct(producto)}
          disabled={!producto.stock || producto.stock <= 0}
          className={`bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-primary-300 hover:bg-primary-50 transition-all duration-200 flex flex-col items-center justify-center text-center group ${
            !producto.stock || producto.stock <= 0 ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mb-2 group-hover:bg-primary-200 transition-colors">
            <span className="text-2xl">📦</span>
          </div>
          <h3 className="font-medium text-gray-800 text-sm line-clamp-2 min-h-[2.5rem]">
            {producto.nombre}
          </h3>
          <p className="text-lg font-bold text-primary-600 mt-1">
            ${Number(producto.precio_venta).toLocaleString('es-CO')}
          </p>
          {producto.stock !== undefined && (
            <p className={`text-xs mt-1 ${producto.stock <= 5 ? 'text-red-500' : 'text-green-500'}`}>
              Stock: {producto.stock}
            </p>
          )}
        </button>
      ))}
    </div>
  )
}
