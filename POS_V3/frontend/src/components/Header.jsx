import React from 'react'

export default function Header({ titulo = "PUNTO DE VENTA", usuario = "Admin", vista = "pos", onCambiarVista }) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="bg-primary-600 text-white p-2 rounded-lg">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">{titulo}</h1>
        </div>

        {/* Botones de navegación */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onCambiarVista && onCambiarVista('pos')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              vista === 'pos' 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            🛒 POS
          </button>
          <button
            onClick={() => onCambiarVista && onCambiarVista('inventario')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              vista === 'inventario' 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            📦 Inventario
          </button>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm text-gray-500">Usuario</p>
            <p className="font-semibold text-gray-800">{usuario}</p>
          </div>
          <div className="h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-primary-600 font-bold">{usuario.charAt(0)}</span>
          </div>
        </div>
      </div>
    </header>
  )
}