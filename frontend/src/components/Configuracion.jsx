import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = "https://determined-compassion-production-801a.up.railway.app"
const TENANT_ID = "4a7e815e-f68e-46f4-863d-1d2f786301e8"

const api = axios.create({ baseURL: API_URL, headers: { 'X-Tenant-ID': TENANT_ID } })

export default function Configuracion() {
  const [config, setConfig] = useState({ nombre: '', nit: '', telefono: '', email: '', direccion: '' })
  const [loading, setLoading] = useState(true)

  useEffect(() => { cargar() }, [])

  const cargar = async () => {
    try {
      const res = await api.get('/api/tenants/configuracion')
      setConfig(res.data)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const guardar = async () => {
    await api.put('/api/tenants/configuracion', config)
    alert('Configuración guardada')
  }

  if (loading) return <div className="p-4">Cargando...</div>

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">⚙️ Configuración</h2>
      
      <div className="bg-white p-4 rounded-lg shadow max-w-lg">
        <label className="block mb-2">Nombre del Negocio</label>
        <input className="w-full border p-2 rounded mb-3" value={config.nombre || ''} onChange={e => setConfig({...config, nombre: e.target.value})} />
        
        <label className="block mb-2">NIT</label>
        <input className="w-full border p-2 rounded mb-3" value={config.nit || ''} onChange={e => setConfig({...config, nit: e.target.value})} />
        
        <label className="block mb-2">Teléfono</label>
        <input className="w-full border p-2 rounded mb-3" value={config.telefono || ''} onChange={e => setConfig({...config, telefono: e.target.value})} />
        
        <label className="block mb-2">Email</label>
        <input className="w-full border p-2 rounded mb-3" value={config.email || ''} onChange={e => setConfig({...config, email: e.target.value})} />
        
        <label className="block mb-2">Dirección</label>
        <input className="w-full border p-2 rounded mb-3" value={config.direccion || ''} onChange={e => setConfig({...config, direccion: e.target.value})} />
        
        <button onClick={guardar} className="bg-blue-600 text-white px-4 py-2 rounded w-full">Guardar</button>
      </div>
    </div>
  )
}
