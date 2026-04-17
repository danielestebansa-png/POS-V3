import React, { useState, useEffect } from 'react'
import { getProductos, getCategorias, crearProducto, actualizarProducto, eliminarProducto, getInventario } from '../services/api'

export default function ProductManager() {
  const [productos, setProductos] = useState([])
  const [categorias, setCategorias] = useState([])
  const [loading, setLoading] = useState(true)
  const [editando, setEditando] = useState(null)
  const [form, setForm] = useState({
    nombre: '', precio_venta: '', precio_costo: '', stock: '', categoria_id: '', codigo: '', estado: 'activo'
  })

  const loadData = async () => {
    setLoading(true)
    const [p, c] = await Promise.all([getProductos(), getCategorias()])
    setProductos(p.data || [])
    setCategorias(c.data || [])
    setLoading(false)
  }

  useEffect(() => { loadData() }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const data = {
      ...form,
      precio_venta: Number(form.precio_venta),
      precio_costo: Number(form.precio_costo),
      stock: Number(form.stock)
    }
    
    if (editando) {
      await actualizarProducto(editando, data)
    } else {
      await crearProducto(data)
    }
    setForm({ nombre: '', precio_venta: '', precio_costo: '', stock: '', categoria_id: '', codigo: '', estado: 'activo' })
    setEditando(null)
    loadData()
  }

  const handleEdit = (p) => {
    setEditando(p.id)
    setForm({
      nombre: p.nombre,
      precio_venta: p.precio_venta,
      precio_costo: p.precio_costo || '',
      stock: p.stock || '',
      categoria_id: p.categoria_id || '',
      codigo: p.codigo || '',
      estado: p.estado
    })
  }

  const handleDelete = async (id) => {
    if (confirm('¿Eliminar producto?')) {
      await eliminarProducto(id)
      loadData()
    }
  }

  if (loading) return <div className="p-4">Cargando...</div>

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">📦 Gestión de Productos</h2>
      
      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow mb-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <input
          type="text"
          placeholder="Nombre del producto"
          value={form.nombre}
          onChange={e => setForm({...form, nombre: e.target.value})}
          className="border p-2 rounded"
          required
        />
        <input
          type="number"
          placeholder="Precio venta"
          value={form.precio_venta}
          onChange={e => setForm({...form, precio_venta: e.target.value})}
          className="border p-2 rounded"
          required
        />
        <input
          type="number"
          placeholder="Precio costo"
          value={form.precio_costo}
          onChange={e => setForm({...form, precio_costo: e.target.value})}
          className="border p-2 rounded"
        />
        <input
          type="number"
          placeholder="Stock"
          value={form.stock}
          onChange={e => setForm({...form, stock: e.target.value})}
          className="border p-2 rounded"
        />
        <select
          value={form.categoria_id}
          onChange={e => setForm({...form, categoria_id: e.target.value})}
          className="border p-2 rounded"
        >
          <option value="">Seleccionar categoría</option>
          {categorias.map(c => (
            <option key={c.id} value={c.id}>{c.nombre}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Código"
          value={form.codigo}
          onChange={e => setForm({...form, codigo: e.target.value})}
          className="border p-2 rounded"
        />
        <select
          value={form.estado}
          onChange={e => setForm({...form, estado: e.target.value})}
          className="border p-2 rounded"
        >
          <option value="activo">Activo</option>
          <option value="inactivo">Inactivo</option>
        </select>
        <button type="submit" className="bg-emerald-600 text-white p-2 rounded hover:bg-emerald-700">
          {editando ? 'Actualizar' : 'Agregar'}
        </button>
      </form>

      {/* List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3 text-left">Producto</th>
              <th className="p-3 text-left">Categoría</th>
              <th className="p-3 text-right">Venta</th>
              <th className="p-3 text-right">Costo</th>
              <th className="p-3 text-right">Stock</th>
              <th className="p-3 text-center">Estado</th>
              <th className="p-3 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {productos.map(p => {
              const cat = categorias.find(c => c.id === p.categoria_id)
              return (
                <tr key={p.id} className="border-t">
                  <td className="p-3">{p.nombre}</td>
                  <td className="p-3 text-gray-600">{cat?.nombre || 'Sin categoría'}</td>
                  <td className="p-3 text-right font-bold">${Number(p.precio_venta).toLocaleString()}</td>
                  <td className="p-3 text-right text-gray-600">${Number(p.precio_costo || 0).toLocaleString()}</td>
                  <td className="p-3 text-right">{p.stock || 0}</td>
                  <td className="p-3 text-center">
                    <span className={`px-2 py-1 rounded text-sm ${p.estado === 'activo' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {p.estado}
                    </span>
                  </td>
                  <td className="p-3 text-center">
                    <button onClick={() => handleEdit(p)} className="text-blue-600 hover:underline mr-2">Editar</button>
                    <button onClick={() => handleDelete(p.id)} className="text-red-600 hover:underline">Eliminar</button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
