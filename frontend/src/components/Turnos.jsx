import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = "https://determined-compassion-production-801a.up.railway.app"
const TENANT_ID = "4a7e815e-f68e-46f4-863d-1d2f786301e8"

const api = axios.create({ baseURL: API_URL, headers: { 'X-Tenant-ID': TENANT_ID } })

export default function Turnos() {
  const [turno, setTurno] = useState(null)
  const [historial, setHistorial] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { cargar() }, [])

  const cargar = async () => {
    try {
      const t = await api.get('/api/turnos/actual')
      setTurno(t.data)
      const h = await api.get('/api/turnos/historial')
      setHistorial(h.data)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const abrirTurno = async () => {
    await api.post('/api/turnos/abrir')
    cargar()
  }

  const cerrarTurno = async () => {
    await api.post('/api/turnos/cerrar')
    cargar()
  }

  if (loading) return <div className="p-4">Cargando...</div>

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">🕐 Turnos</h2>
      
      <div className="bg-white p-4 rounded-lg shadow mb-4">
        <p className="text-lg mb-2">Estado actual: <span className={`font-bold ${turno?.estado === 'abierto' ? 'text-green-600' : 'text-red-600'}`}>{turno?.estado || 'sin_turno'}</span></p>
        {turno?.estado === 'abierto' ? (
          <button onClick={cerrarTurno} className="bg-red-600 text-white px-4 py-2 rounded">Cerrar Turno</button>
        ) : (
          <button onClick={abrirTurno} className="bg-green-600 text-white px-4 py-2 rounded">Abrir Turno</button>
        )}
      </div>

      <h3 className="text-xl font-bold mb-2">Historial</h3>
      <div className="space-y-2">
        {historial.map(t => (
          <div key={t.id} className="bg-white p-3 rounded shadow">
            <p><strong>Inicio:</strong> {t.inicio?.substring(0,16)} | <strong>Cierre:</strong> {t.cierre?.substring(0,16) || 'Abierto'}</p>
            <p><strong>Total:</strong> ${t.total?.toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
