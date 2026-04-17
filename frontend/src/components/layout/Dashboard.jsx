import React from 'react'

const kpis = [
  { label: 'Ventas Hoy', value: '$125,000', icon: '💰', color: 'bg-green-100 text-green-600' },
  { label: 'Productos', value: '10', icon: '📦', color: 'bg-blue-100 text-blue-600' },
  { label: 'Clientes', value: '5', icon: '👥', color: 'bg-purple-100 text-purple-600' },
  { label: 'Tickets', value: '8', icon: '🧾', color: 'bg-orange-100 text-orange-600' },
]

export default function Dashboard({ onNavigate }) {
  return (
    <div className="space-y-6">
      {/* Sistema POS - BIG BUTTON */}
      <button 
        onClick={() => onNavigate('pos')}
        className="w-full bg-blue-600 text-white p-8 rounded-xl hover:bg-blue-700 transition-all shadow-lg"
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold">🛒 SISTEMA POS</h2>
            <p className="text-blue-200 mt-2">点击 para entrar al sistema de facturación</p>
          </div>
          <div className="text-6xl">→</div>
        </div>
      </button>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="bg-white p-6 rounded-lg shadow">
            <div className={`w-12 h-12 rounded-full ${kpi.color} flex items-center justify-center text-2xl mb-3`}>
              {kpi.icon}
            </div>
            <p className="text-2xl font-bold text-gray-800">{kpi.value}</p>
            <p className="text-sm text-gray-500">{kpi.label}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-bold text-gray-800 mb-4">Acciones Rápidas</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button onClick={() => onNavigate('pos')} className="bg-blue-600 text-white p-4 rounded-lg hover:bg-blue-700">
            <span className="text-2xl block">🛒</span>
            <span className="font-medium">POS</span>
          </button>
          <button onClick={() => onNavigate('facturar')} className="bg-green-600 text-white p-4 rounded-lg hover:bg-green-700">
            <span className="text-2xl block">📄</span>
            <span className="font-medium">Facturar</span>
          </button>
          <button onClick={() => onNavigate('inventario')} className="bg-purple-600 text-white p-4 rounded-lg hover:bg-purple-700">
            <span className="text-2xl block">📦</span>
            <span className="font-medium">Inventario</span>
          </button>
          <button onClick={() => onNavigate('reportes')} className="bg-gray-600 text-white p-4 rounded-lg hover:bg-gray-700">
            <span className="text-2xl block">📊</span>
            <span className="font-medium">Reportes</span>
          </button>
        </div>
      </div>

      {/* Ventas Recientes */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-bold text-gray-800 mb-4">Ventas Recientes</h2>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 text-gray-600">Factura</th>
              <th className="text-left py-3 text-gray-600">Cliente</th>
              <th className="text-right py-3 text-gray-600">Total</th>
              <th className="text-right py-3 text-gray-600">Fecha</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-gray-100">
              <td className="py-3">FAC-001</td>
              <td className="py-3">Juan Pérez</td>
              <td className="py-3 text-right">$25,000</td>
              <td className="py-3 text-right">16/04/2026</td>
            </tr>
            <tr className="border-b border-gray-100">
              <td className="py-3">FAC-002</td>
              <td className="py-3">María García</td>
              <td className="py-3 text-right">$15,000</td>
              <td className="py-3 text-right">16/04/2026</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
