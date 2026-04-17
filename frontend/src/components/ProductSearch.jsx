import React, { useState, useEffect } from 'react'
import { getProductos, getCategorias } from '../services/api'

// Componente mejorado de búsqueda y productos
export default function ProductSearch({ onAddToCart }) {
  const [productos, setProductos] = useState([])
  const [categorias, setCategorias] = useState([])
  const [loading, setLoading] = useState(true)
  const [busqueda, setBusqueda] = useState('')
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState(null)
  const [pagina, setPagina] = useState(1)
  const [favoritos, setFavoritos] = useState([])
  const productosPorPagina = 20

  useEffect(() => {
    cargarDatos()
    // Cargar favoritos del localStorage
    const saved = localStorage.getItem('favoritos')
    if (saved) setFavoritos(JSON.parse(saved))
  }, [])

  useEffect(() => {
    cargarProductos()
  }, [busqueda, categoriaSeleccionada, pagina])

  const cargarDatos = async () => {
    try {
      setLoading(true)
      const [prods, cats] = await Promise.all([
        getProductos(),
        getCategorias()
      ])
      setProductos(prods.data || [])
      setCategorias(cats.data || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const cargarProductos = async () => {
    try {
      setLoading(true)
      const res = await getProductos()
      let productosFiltrados = res.data || []
      
      // Filtrar por búsqueda (nombre o código)
      if (busqueda.trim()) {
        const buscar = busqueda.toLowerCase()
        productosFiltrados = productosFiltrados.filter(p => 
          p.nombre?.toLowerCase().includes(buscar) || 
          p.codigo?.toLowerCase().includes(buscar)
        )
      }
      
      // Filtrar por categoría
      if (categoriaSeleccionada) {
        productosFiltrados = productosFiltrados.filter(p => 
          p.categoria_id === categoriaSeleccionada
        )
      }
      
      setProductos(productosFiltrados)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  // Pagination
  const totalPaginas = Math.ceil(productos.length / productosPorPagina)
  const productosPagina = productos.slice(
    (pagina - 1) * productosPorPagina, 
    pagina * productosPorPagina
  )

  // Toggle favorito
  const toggleFavorito = (productoId) => {
    let nuevosFavoritos
    if (favoritos.includes(productoId)) {
      nuevosFavoritos = favoritos.filter(id => id !== productoId)
    } else {
      nuevosFavoritos = [...favoritos, productoId]
    }
    setFavoritos(nuevosFavoritos)
    localStorage.setItem('favoritos', JSON.stringify(nuevosFavoritos))
  }

  const esFavorito = (productoId) => favoritos.includes(productoId)

  return (
    <div className="space-y-4">
      {/* 🔍 BUSCADOR */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <input
            type="text"
            placeholder="🔍 Buscar por nombre o código..."
            value={busqueda}
            onChange={(e) => {
              setBusqueda(e.target.value)
              setPagina(1)
            }}
            className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500"
          />
          {busqueda && (
            <button 
              onClick={() => setBusqueda('')}
              className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* 📂 CATEGORÍAS */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        <button
          onClick={() => {setCategoriaSeleccionada(null); setPagina(1)}}
          className={`px-4 py-2 rounded-full whitespace-nowrap ${
            !categoriaSeleccionada 
              ? 'bg-emerald-600 text-white' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Todas
        </button>
        {categorias.map(cat => (
          <button
            key={cat.id}
            onClick={() => {setCategoriaSeleccionada(cat.id); setPagina(1)}}
            className={`px-4 py-2 rounded-full whitespace-nowrap ${
              categoriaSeleccionada === cat.id
                ? 'bg-emerald-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {cat.nombre}
          </button>
        ))}
      </div>

      {/* CONTADOR */}
      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>{productos.length} productos encontrados</span>
        {busqueda && (
          <span className="text-emerald-600">Buscando: "{busqueda}"</span>
        )}
      </div>

      {/* GRID PRODUCTOS */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">Cargando...</div>
      ) : productosPagina.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No se encontraron productos
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {productosPagina.map(p => (
              <div key={p.id} className="relative bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:shadow-md hover:border-emerald-300 transition">
                {/* Botón favorito */}
                <button
                  onClick={() => toggleFavorito(p.id)}
                  className={`absolute top-2 right-2 text-xl ${esFavorito(p.id) ? 'text-yellow-500' : 'text-gray-300 hover:text-yellow-500'}`}
                >
                  ⭐
                </button>
                
                <button 
                  onClick={() => onAddToCart(p)}
                  className="w-full text-left"
                >
                  <div className="text-2xl mb-1">📦</div>
                  <p className="font-medium text-sm text-gray-800 line-clamp-2">{p.nombre}</p>
                  {p.codigo && (
                    <p className="text-xs text-gray-400">📋 {p.codigo}</p>
                  )}
                  <p className="text-emerald-600 font-bold text-lg mt-1">
                    ${Number(p.precio_venta).toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500">Stock: {p.stock}</p>
                </button>
              </div>
            ))}
          </div>

          {/* PAGINATION */}
          {totalPaginas > 1 && (
            <div className="flex justify-center gap-2 mt-4">
              <button
                onClick={() => setPagina(p => Math.max(1, p - 1))}
                disabled={pagina === 1}
                className="px-4 py-2 rounded bg-gray-100 hover:bg-gray-200 disabled:opacity-50"
              >
                ← Anterior
              </button>
              
              <span className="px-4 py-2 text-gray-600">
                {pagina} / {totalPaginas}
              </span>
              
              <button
                onClick={() => setPagina(p => Math.min(totalPaginas, p + 1))}
                disabled={pagina === totalPaginas}
                className="px-4 py-2 rounded bg-gray-100 hover:bg-gray-200 disabled:opacity-50"
              >
                Siguiente →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
