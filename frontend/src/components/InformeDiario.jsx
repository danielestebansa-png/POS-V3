import React, { useState, useEffect, useMemo } from 'react'
import { getVentas, getProductos, getCategorias } from '../services/api'

const NOMBRE_TIENDA = "Mi Papelería"

export default function InformeDiario() {
  const [ventas, setVentas] = useState([])
  const [productos, setProductos] = useState([])
  const [categorias, setCategorias] = useState([])
  const [loading, setLoading] = useState(true)
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState(null)
  const [mostrarTodosProductos, setMostrarTodosProductos] = useState(false)
  const LIMIT_PRODUCTOS = 10
  
  const [filtroFecha, setFiltroFecha] = useState('dia')
  const [fechaInicio, setFechaInicio] = useState(new Date().toISOString().split('T')[0])
  const [fechaFin, setFechaFin] = useState(new Date().toISOString().split('T')[0])
  const [metodoPago, setMetodoPago] = useState('todas')

  useEffect(() => { loadData() }, [])

  useEffect(() => {
    const today = new Date()
    if (filtroFecha === 'dia') {
      setFechaInicio(today.toISOString().split('T')[0])
      setFechaFin(today.toISOString().split('T')[0])
    } else if (filtroFecha === 'semana') {
      const start = new Date(today)
      start.setDate(today.getDate() - today.getDay())
      setFechaInicio(start.toISOString().split('T')[0])
      setFechaFin(today.toISOString().split('T')[0])
    } else if (filtroFecha === 'mes') {
      const start = new Date(today.getFullYear(), today.getMonth(), 1)
      setFechaInicio(start.toISOString().split('T')[0])
      setFechaFin(today.toISOString().split('T')[0])
    }
  }, [filtroFecha])

  const loadData = async () => {
    setLoading(true)
    try {
      const [v, p, c] = await Promise.all([getVentas(), getProductos(), getCategorias()])
      setVentas(v.data || [])
      setProductos(p.data || [])
      setCategorias(c.data || [])
      // Limit initial productos display
      if (p.data?.length > LIMIT_PRODUCTOS) {
        setProductos(p.data.slice(0, LIMIT_PRODUCTOS))
      } else {
        setProductos(p.data || [])
      }
    } catch (e) { 
      console.error('Error loading data:', e)
    }
    setLoading(false)
  }

  const ventasFiltradas = useMemo(() => {
    return ventas.filter(v => {
      const fechaVenta = v.fecha?.split('T')[0] || ''
      const inDateRange = fechaVenta >= fechaInicio && fechaVenta <= fechaFin
      const metodoMatch = metodoPago === 'todas' || v.metodo_pago === metodoPago
      return inDateRange && metodoMatch
    })
  }, [ventas, fechaInicio, fechaFin, metodoPago])

  const stats = useMemo(() => {
    const total = ventasFiltradas.reduce((s, v) => s + v.total, 0)
    const efectivo = ventasFiltradas.filter(v => v.metodo_pago === 'efectivo').reduce((s, v) => s + v.total, 0)
    const transferencia = ventasFiltradas.filter(v => v.metodo_pago === 'transferencia').reduce((s, v) => s + v.total, 0)
    const tarjeta = ventasFiltradas.filter(v => v.metodo_pago === 'tarjeta').reduce((s, v) => s + v.total, 0)
    const count = ventasFiltradas.length
    const promedio = count > 0 ? total / count : 0
    return { total, efectivo, transferencia, tarjeta, count, promedio }
  }, [ventasFiltradas])

  const ventasPorFecha = useMemo(() => {
    const grouped = {}
    ventasFiltradas.forEach(v => {
      const fecha = v.fecha?.split('T')[0] || 'sin fecha'
      if (!grouped[fecha]) grouped[fecha] = { count: 0, total: 0 }
      grouped[fecha].count++
      grouped[fecha].total += v.total
    })
    return Object.entries(grouped).sort((a, b) => b[0].localeCompare(a[0]))
  }, [ventasFiltradas])

  const porMetodo = [
    { metodo: 'Efectivo', icono: '💵', total: stats.efectivo, count: ventasFiltradas.filter(v => v.metodo_pago === 'efectivo').length },
    { metodo: 'Transferencia', icono: '🏦', total: stats.transferencia, count: ventasFiltradas.filter(v => v.metodo_pago === 'transferencia').length },
    { metodo: 'Tarjeta', icono: '💳', total: stats.tarjeta, count: ventasFiltradas.filter(v => v.metodo_pago === 'tarjeta').length },
  ]

  const formatFecha = (f) => {
    const d = new Date(f)
    return d.toLocaleDateString('es-CO', { weekday: 'short', day: 'numeric', month: 'short' })
  }

  const productosPorCategoria = useMemo(() => {
    const grouped = {}
    productos.forEach(p => {
      const catId = p.categoria_id || 'sin_cat'
      if (!grouped[catId]) {
        grouped[catId] = { 
          nombre: p.categoria?.nombre || 'Sin categoría', 
          productos: [],
          totalStock: 0,
          valorTotal: 0
        }
      }
      grouped[catId].productos.push(p)
      grouped[catId].totalStock += p.stock || 0
      grouped[catId].valorTotal += (Number(p.precio_venta) * (p.stock || 0))
    })
    return Object.values(grouped)
  }, [productos])

  if (loading) return <div className="p-8 text-center">Cargando informe...</div>

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">📊 Comprobante de Informe Diario</h2>
          <button onClick={() => window.print()} className="bg-emerald-600 text-white px-4 py-2 rounded text-sm hover:bg-emerald-700">
            🖨️ Imprimir
          </button>
        </div>

        <div className="flex flex-wrap gap-3 mb-4">
          <select value={filtroFecha} onChange={(e) => setFiltroFecha(e.target.value)} className="border rounded px-3 py-2 text-sm">
            <option value="dia">Hoy</option>
            <option value="semana">Esta Semana</option>
            <option value="mes">Este Mes</option>
            <option value="personalizado">Personalizado</option>
          </select>
          
          <input type="date" value={fechaInicio} onChange={(e) => setFechaInicio(e.target.value)} className="border rounded px-3 py-2 text-sm" />
          <span className="self-center">hasta</span>
          <input type="date" value={fechaFin} onChange={(e) => setFechaFin(e.target.value)} className="border rounded px-3 py-2 text-sm" />
          
          <select value={metodoPago} onChange={(e) => setMetodoPago(e.target.value)} className="border rounded px-3 py-2 text-sm">
            <option value="todas">Todos los métodos</option>
            <option value="efectivo">Efectivo</option>
            <option value="transferencia">Transferencia</option>
            <option value="tarjeta">Tarjeta</option>
          </select>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-emerald-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-emerald-700">${stats.total.toLocaleString()}</p>
            <p className="text-sm text-emerald-600">Total Ingresos</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-blue-700">{stats.count}</p>
            <p className="text-sm text-blue-600">Transacciones</p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-purple-700">${stats.promedio.toLocaleString()}</p>
            <p className="text-sm text-purple-600">Promedio/Venta</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <p className="text-2xl font-bold text-gray-700">{ventasFiltradas.length}</p>
            <p className="text-sm text-gray-600">Documentos</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-4">
        <h3 className="font-bold mb-3">💰 Ingresos por Método de Pago</h3>
        <div className="grid grid-cols-3 gap-3">
          {porMetodo.map(m => (
            <div key={m.metodo} className="bg-gray-50 p-3 rounded-lg text-center">
              <p className="text-2xl mb-1">{m.icono}</p>
              <p className="text-lg font-bold">${m.total.toLocaleString()}</p>
              <p className="text-sm text-gray-500">{m.metodo} ({m.count})</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-4">
        <h3 className="font-bold mb-3">📅 Resumen por Fecha</h3>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left p-2">Fecha</th>
              <th className="text-right p-2">Transacciones</th>
              <th className="text-right p-2">Total</th>
            </tr>
          </thead>
          <tbody>
            {ventasPorFecha.map(([fecha, data]) => (
              <tr key={fecha} className="border-b">
                <td className="p-2">{formatFecha(fecha)}</td>
                <td className="text-right p-2">{data.count}</td>
                <td className="text-right p-2 font-bold text-emerald-600">${data.total.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-4">
        <h3 className="font-bold mb-3">🏷️ Categorías - Click para ver detalle</h3>
        {/* Botón ver todos los productos */}
        {productos.length >= LIMIT_PRODUCTOS && (
          <button
            onClick={async () => {
              if (mostrarTodosProductos) {
                const all = await getProductos()
                setProductos(all.data?.slice(0, LIMIT_PRODUCTOS) || [])
              } else {
                const all = await getProductos()
                setProductos(all.data || [])
              }
              setMostrarTodosProductos(!mostrarTodosProductos)
            }}
            className="mb-3 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
          >
            {mostrarTodosProductos ? '▲ Ver menos' : `📋 Ver todos los productos`}
          </button>
        )}
        {productosPorCategoria.length > 0 ? (
          <div className="space-y-2">
            {productosPorCategoria.map((cat, idx) => {
              return (
                <div key={idx} className="border rounded-lg overflow-hidden">
                  <button 
                    onClick={() => setCategoriaSeleccionada(categoriaSeleccionada === idx ? null : idx)}
                    className="w-full p-3 flex justify-between items-center hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-3">
                      <span className="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-full text-sm font-medium">
                        {cat.nombre}
                      </span>
                    </div>
                    <div className="flex items-center gap-6 text-sm">
                      <span className="text-gray-500">{cat.productos.length} productos</span>
                      <span className="text-gray-500">Stock: {cat.totalStock}</span>
                      <span className="font-bold text-emerald-600">${cat.valorTotal.toLocaleString()}</span>
                      <span>{categoriaSeleccionada === idx ? '▲' : '▼'}</span>
                    </div>
                  </button>
                  
                  {categoriaSeleccionada === idx && (
                    <div className="bg-gray-50 p-4 border-t">
                      <h4 className="font-medium mb-3">📦 Productos en {cat.nombre}</h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                        {cat.productos.map(p => (
                          <div key={p.id} className="bg-white p-3 rounded border text-sm">
                            <p className="font-medium truncate">{p.nombre}</p>
                            <p className="text-emerald-600 font-bold">${Number(p.precio_venta).toLocaleString()}</p>
                            <p className="text-gray-500 text-xs">Stock: {p.stock || 0}</p>
                            <p className="text-gray-500 text-xs">Código: {p.codigo || 'N/A'}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">Sin categorías</p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-4">
        <h3 className="font-bold mb-3">📦 Todos los Productos ({productos.length})</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {productos.map(p => (
            <div key={p.id} className="bg-gray-50 p-3 rounded text-center">
              <p className="font-medium text-sm truncate">{p.nombre}</p>
              <p className="text-lg font-bold text-emerald-600">${Number(p.precio_venta).toLocaleString()}</p>
              <p className="text-xs text-gray-500">Stock: {p.stock}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-4">
        <h3 className="font-bold mb-3">⏰ Turnos</h3>
        <div className="bg-gray-50 p-4 rounded text-center">
          <p className="text-gray-500">Configura turnos para ver el detalle aquí</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border p-4">
        <h3 className="font-bold mb-3">📉 Egresos</h3>
        <div className="bg-gray-50 p-4 rounded text-center">
          <p className="text-gray-500">Registra gastos para ver el detalle aquí</p>
        </div>
      </div>

      <div className="bg-emerald-600 text-white rounded-lg shadow-sm p-4 text-center">
        <p className="font-bold">{NOMBRE_TIENDA}</p>
        <p className="text-sm">Informe del {formatFecha(fechaInicio)} al {formatFecha(fechaFin)}</p>
        <p className="text-xs mt-2 opacity-75">Generado automáticamente por el sistema POS</p>
      </div>
    </div>
  )
}
