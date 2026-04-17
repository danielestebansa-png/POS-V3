import React, { useState, useEffect } from 'react'
import { getVentas } from '../services/api'

export default function HistorialVentas() {
  const [ventas, setVentas] = useState([])
  const [loading, setLoading] = useState(true)
  const [filtro, setFiltro] = useState('todas')
  const [busqueda, setBusqueda] = useState('')

  useEffect(() => {
    loadVentas()
  }, [])

  const loadVentas = async () => {
    setLoading(true)
    try {
      const res = await getVentas()
      setVentas(res.data || [])
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  // Filtrar ventas
  const ventasFiltradas = ventas.filter(v => {
    // Filtro por método de pago
    if (filtro !== 'todas' && v.metodo_pago !== filtro) return false
    // Búsqueda por número
    if (busqueda && !v.numero.toLowerCase().includes(busqueda.toLowerCase())) return false
    return true
  })

  // Calcular totales
  const totalVentas = ventasFiltradas.reduce((s, v) => s + v.total, 0)
  const conteoPorMetodo = ventasFiltradas.reduce((acc, v) => {
    acc[v.metodo_pago] = (acc[v.metodo_pago] || 0) + 1
    return acc
  }, {})

  const getMetodoIcon = (metodo) => {
    const icons = { efectivo: '💵', transferencia: '🏦', tarjeta: '💳' }
    return icons[metodo] || '❓'
  }

  const getMetodoLabel = (metodo) => {
    const labels = { efectivo: 'Efectivo', transferencia: 'Transferencia', tarjeta: 'Tarjeta' }
    return labels[metodo] || metodo
  }

  return (
    <div className="space-y-4">
      {/* Header con stats */}
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">📊 Historial de Ventas</h2>
          <span className="text-sm text-gray-500">{ventasFiltradas.length} transacciones</span>
        </div>
        
        {/* Filtros */}
        <div className="flex flex-wrap gap-3 mb-4">
          <input
            type="text"
            placeholder="Buscar por número..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="border rounded px-3 py-2 text-sm flex-1 min-w-[200px]"
          />
          <select 
            value={filtro} 
            onChange={(e) => setFiltro(e.target.value)}
            className="border rounded px-3 py-2 text-sm"
          >
            <option value="todas">Todos los métodos</option>
            <option value="efectivo">Efectivo</option>
            <option value="transferencia">Transferencia</option>
            <option value="tarjeta">Tarjeta</option>
          </select>
        </div>

        {/* Stats rápidas */}
        <div className="grid grid-cols-4 gap-3 mb-4">
          <div className="bg-emerald-50 p-3 rounded text-center">
            <p className="text-xl font-bold text-emerald-700">${totalVentas.toLocaleString()}</p>
            <p className="text-xs text-emerald-600">Total</p>
          </div>
          <div className="bg-gray-50 p-3 rounded text-center">
            <p className="text-xl font-bold text-gray-700">{conteoPorMetodo.efectivo || 0}</p>
            <p className="text-xs text-gray-600">Efectivo</p>
          </div>
          <div className="bg-gray-50 p-3 rounded text-center">
            <p className="text-xl font-bold text-gray-700">{conteoPorMetodo.transferencia || 0}</p>
            <p className="text-xs text-gray-600">Transferencia</p>
          </div>
          <div className="bg-gray-50 p-3 rounded text-center">
            <p className="text-xl font-bold text-gray-700">{conteoPorMetodo.tarjeta || 0}</p>
            <p className="text-xs text-gray-600">Tarjeta</p>
          </div>
        </div>
      </div>

      {/* Tabla de ventas */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Cargando...</div>
        ) : ventasFiltradas.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No hay ventas</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3">Factura</th>
                <th className="text-left p-3">Método</th>
                <th className="text-right p-3">Subtotal</th>
                <th className="text-right p-3">Descuento</th>
                <th className="text-right p-3">IVA</th>
                <th className="text-right p-3">Total</th>
                <th className="text-center p-3">Estado</th>
              </tr>
            </thead>
            <tbody>
              {ventasFiltradas.map((v, idx) => (
                <tr key={v.id} className={`border-b ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                  <td className="p-3 font-medium">{v.numero}</td>
                  <td className="p-3">
                    <span className="flex items-center gap-1">
                      {getMetodoIcon(v.metodo_pago)}
                      {getMetodoLabel(v.metodo_pago)}
                    </span>
                  </td>
                  <td className="text-right p-3">${v.subtotal?.toLocaleString() || 0}</td>
                  <td className="text-right p-3 text-gray-500">${v.descuento?.toLocaleString() || 0}</td>
                  <td className="text-right p-3 text-gray-500">${v.iva?.toLocaleString() || 0}</td>
                  <td className="text-right p-3 font-bold text-emerald-600">${v.total?.toLocaleString() || 0}</td>
                  <td className="text-center p-3">
                    <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs">
                      {v.estado || 'completada'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
