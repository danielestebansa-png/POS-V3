import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = "https://determined-compassion-production-801a.up.railway.app"
const TENANT_ID = "4a7e815e-f68e-46f4-863d-1d2f786301e8"

const api = axios.create({
  baseURL: API_URL,
  headers: { 'X-Tenant-ID': TENANT_ID }
})

export default function Clientes() {
  const [clientes, setClientes] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ nombre: '', identificacion: '', telefono: '', email: '', direccion: '' })
  const [editando, setEditando] = useState(null)

  useEffect(() => { cargarClientes() }, [])

  const cargarClientes = async () => {
    try {
      const res = await api.get('/api/clientes/clientes')
      setClientes(res.data)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const guardar = async () => {
    if (editando) {
      await api.put(`/api/clientes/clientes/${editando}`, form)
    } else {
      await api.post('/api/clientes/clientes', form)
    }
    setForm({ nombre: '', identificacion: '', telefono: '', email: '', direccion: '' })
    setEditando(null)
    cargarClientes()
  }

  const editar = (c) => { setForm(c); setEditando(c.id) }
  const eliminar = async (id) => { if(confirm('Eliminar?')) { await api.delete(`/api/clientes/clientes/${id}`); cargarClientes() } }

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">👥 Clientes</h2>
      
      <div className="bg-white p-4 rounded-lg shadow mb-4">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          <input className="border p-2 rounded" placeholder="Nombre" value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} />
          <input className="border p-2 rounded" placeholder="Identificación" value={form.identificacion} onChange={e => setForm({...form, identificacion: e.target.value})} />
          <input className="border p-2 rounded" placeholder="Teléfono" value={form.telefono} onChange={e => setForm({...form, telefono: e.target.value})} />
          <input className="border p-2 rounded" placeholder="Email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
          <button onClick={guardar} className="bg-green-600 text-white p-2 rounded hover:bg-green-700">{editando ? 'Actualizar' : 'Agregar'}</button>
        </div>
      </div>

      {loading ? <p>Cargando...</p> : (
        <div className="grid gap-2">
          {clientes.map(c => (
            <div key={c.id} className="bg-white p-3 rounded shadow flex justify-between items-center">
              <div>
                <p className="font-bold">{c.nombre}</p>
                <p className="text-sm text-gray">{c.telefono} | {c.email}</p>
              </div>
              <div>
                <button onClick={() => editar(c)} className="text-blue-600 mr-2">✏️</button>
                <button onClick={() => eliminar(c.id)} className="text-red-600">🗑️</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
