import React from 'react'

export default function Header({ title, currentPage, onNavigate }) {
  return (
    <header className="bg-white shadow p-4 flex justify-between items-center">
      <h1 className="text-xl font-bold text-gray-800">
        {title}
      </h1>
      <div className="flex items-center gap-4">
        <button 
          onClick={() => onNavigate('inicio')}
          className="text-gray-600 hover:text-gray-800"
        >
          🏠 Inicio
        </button>
        <button 
          onClick={() => onNavigate('pos')}
          className="text-gray-600 hover:text-gray-800"
        >
          🛒 POS
        </button>
        <span className="text-sm text-gray-600">Admin</span>
        <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm">
          👤
        </button>
      </div>
    </header>
  )
}
