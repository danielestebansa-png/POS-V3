import React, { useState, useEffect } from 'react'
import { getProductos, getCategorias } from '../services/api'

export default function Inventario({ onVolver }) {
  const [productos, setProductos] = useState([])
  const [categorias, setCategorias] = useState([])
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [categoriaFilter, setCategoriaFilter] = useState('')
  const [editando, setEditando] = useState(null)
  const [nuevoStock, setNuevoStock] = useState('')
  const [mensaje, setMensaje] = useState(null)

  // Cargar datos
  useEffect(() => {
    cargarDatos()
  }, [])

  const cargarDatos = async () => {
    try {
      setLoading(true)
      const [prodRes, catRes] = await Promise.all([
        getProductos(),
        getCategorias()
      ])
      if (prodRes.data) setProductos(prodRes.data)
      if (catRes.data) setCategorias(catRes.data)
    } catch (err) {
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Filtrar productos
  const productosFiltrados = productos.filter(p => {
    const texto = search.toLowerCase()
    const coincideTexto = p.nombre?.toLowerCase().includes(texto) ||
                          p.codigo_barras?.toLowerCase().includes(texto)
    const coincideCategoria = !categoriaFilter || p.categoria_id === categoriaFilter
    return coincideTexto && coincideCategoria
  })

  // Estadísticas
  const totalProductos = productosFiltrados.length
  const stockBajo = productosFiltrados.filter(p => p.stock !== undefined && p.stock < 10).length
  const stockAgotado = productosFiltrados.filter(p => p.stock === 0).length
  const valorInventario = productosFiltrados.reduce((acc, p) => acc + (p.precio_venta * (p.stock || 0)), 0)

  // Iniciar edición de stock
  const handleEditarStock = (producto) => {
    setEditando(producto.id)
    setNuevoStock(producto.stock?.toString() || '0')
  }

  // Guardar stock (simulado)
  const handleGuardarStock = (producto) => {
    const stockNum = parseFloat(nuevoStock)
    if (isNaN(stockNum) || stockNum < 0) {
      setMensaje({ tipo: 'error', texto: 'Stock inválido' })
      return
    }

    setProductos(productos.map(p => 
      p.id === producto.id ? { ...p, stock: stockNum } : p
    ))
    setMensaje({ tipo: 'success', texto: 'Stock actualizado correctamente' })
    setEditando(null)
    setNuevoStock('')
    setTimeout(() => setMensaje(null), 3000)
  }

  // Cancelar edición
  // Importar desde Excel
  const handleImportExcel = (e) => {
    const archivo = e.target.files[0]
    if (!archivo) return
    
    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        const texto = event.target.result
        const lineas = texto.split("\n")
        let importados = 0
        
        lineas.forEach((linea, i) => {
          if (i === 0) return // skip header
          const cols = linea.split(",")
          if (cols.length < 2) return
          
          const nombre = cols[0].trim()
          const precio = parseFloat(cols[1].trim())
          const stock = parseFloat(cols[2]?.trim() || 0)
          
          if (nombre && !isNaN(precio)) {
            const existe = productos.find(p => p.nombre.toLowerCase() === nombre.toLowerCase())
            if (existe) {
              setProductos(productos.map(p =>
                p.nombre.toLowerCase() === nombre.toLowerCase()
                  ? { ...p, precio_venta: precio, stock: stock || p.stock } : p
              ))
            } else {
              setProductos([...productos, {
                id: crypto.randomUUID(),
                nombre,
                precio_venta: precio,
                stock: stock || 0,
                estado: "activo"
              }])
            }
            importados++
          }
        })
        setMensaje({ tipo: "success", texto: `${importados} productos importados` })
      } catch (err) {
        setMensaje({ tipo: "error", texto: "Error al importar" })
      }
    }
    reader.readAsText(archivo)
  }

  const handleCancelar = () => {
    setEditando(null)
    setNuevoStock('')
  }

  // Formatear precio
  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(price)
  }

  // Obtener color de stock
  const getStockColor = (stock) => {
    if (stock === 0) return 'bg-red-100 text-red-700 border border-red-300'
    if (stock < 10) return 'bg-orange-100 text-orange-700 border border-orange-300'
    return 'bg-green-100 text-green-700 border border-green-300'
  }

  const getStockBadge = (stock) => {
    if (stock === 0) return 'AGOTADO'
    if (stock < 10) return 'BAJO'
    return null
  }

  return (
    <div className="min-h-screen bg-gray-100 p-4 lg:p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div className="flex items-center gap-4">
          <button
            onClick={onVolver}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Volver
          </button>
          <h1 className="text-2xl font-bold text-gray-800">📦 Gestión de Inventario</h1>
        </div>
        
        {/* Filtros */}
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Buscador */}
          <div className="relative">
            <input
              type="text"
              placeholder="Buscar producto..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full sm:w-64 px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <svg className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            {search && (
              <button onClick={() => setSearch('')} className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600">
                ✕
              </button>
            )}
          </div>

          {/* Filtro categoría */}
          <select
            value={categoriaFilter}
            onChange={(e) => setCategoriaFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas las categorías</option>
            {categorias.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Tarjetas de resumen */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <p className="text-sm text-gray-500">Total Productos</p>
          <p className="text-2xl font-bold text-gray-800">{totalProductos}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500">
          <p className="text-sm text-gray-500">Stock Bajo (&lt;10)</p>
          <p className="text-2xl font-bold text-orange-600">{stockBajo}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
          <p className="text-sm text-gray-500">Agotados</p>
          <p className="text-2xl font-bold text-red-600">{stockAgotado}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <p className="text-sm text-gray-500">Valor Inventario</p>
          <p className="text-xl font-bold text-gray-800">{formatPrice(valorInventario)}</p>
        </div>
      </div>

      {/* Mensaje */}
      {mensaje && (
        <div className={`mb-4 p-3 rounded-lg flex items-center gap-2 ${
          mensaje.tipo === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          <span>{mensaje.tipo === 'success' ? '✓' : '✕'}</span>
          {mensaje.texto}
        </div>
      )}

      {/* Tabla */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Producto</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600">Categoría</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">Precio Venta</th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-600">Stock</th>
                <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600">Valor</th>
                <th className="px-4 py-3 text-center text-sm font-semibold text-gray-600">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                    <div className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Cargando...
                    </div>
                  </td>
                </tr>
              ) : productosFiltrados.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                    No se encontraron productos
                  </td>
                </tr>
              ) : (
                productosFiltrados.map((producto) => {
                  const badge = getStockBadge(producto.stock)
                  const valorTotal = (producto.precio_venta || 0) * (producto.stock || 0)
                  
                  return (
                    <tr key={producto.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3">
                        <div className="flex flex-col">
                          <span className="font-medium text-gray-800">{producto.nombre}</span>
                          <span className="text-xs text-gray-400">
                            {producto.codigo_barras || 'Sin código'}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-gray-600 text-sm">-</span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="font-semibold text-gray-800">
                          {formatPrice(producto.precio_venta)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        {editando === producto.id ? (
                          <input
                            type="number"
                            value={nuevoStock}
                            onChange={(e) => setNuevoStock(e.target.value)}
                            className="w-20 px-2 py-1 border-2 border-blue-500 rounded text-center font-bold focus:outline-none"
                            min="0"
                            step="1"
                            autoFocus
                          />
                        ) : (
                          <div className="flex items-center justify-center gap-2">
                            <span className={`px-2 py-1 rounded font-bold ${getStockColor(producto.stock)}`}>
                              {producto.stock ?? 0}
                            </span>
                            {badge && (
                              <span className={`text-xs px-1 py-0.5 rounded font-bold ${
                                badge === 'AGOTADO' ? 'bg-red-600 text-white' : 'bg-orange-500 text-white'
                              }`}>
                                {badge}
                              </span>
                            )}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-gray-600 text-sm">
                          {formatPrice(valorTotal)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        {editando === producto.id ? (
                          <div className="flex justify-center gap-2">
                            <button
                              onClick={() => handleGuardarStock(producto)}
                              className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition-colors"
                            >
                              ✓ Guardar
                            </button>
                            <button
                              onClick={handleCancelar}
                              className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600 transition-colors"
                            >
                              ✕
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => handleEditarStock(producto)}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 transition-colors"
                          >
                            Editar
                          </button>
                        )}
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer con totales */}
      <div className="mt-4 flex flex-wrap justify-between items-center text-sm text-gray-600 bg-white p-3 rounded-lg shadow">
        <span>Mostrando {productosFiltrados.length} de {productos.length} productos</span>
        <div className="flex gap-4">
          <span className="text-orange-600">● Stock bajo: {stockBajo}</span>
          <span className="text-red-600">● Agotados: {stockAgotado}</span>
        </div>
      </div>
    </div>
  )
}