import axios from 'axios'

const API_URL = "https://determined-compassion-production-801a.up.railway.app"
const TENANT_ID = "4a7e815e-f68e-46f4-863d-1d2f786301e8"

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-ID': TENANT_ID,
  },
})

export const getProductos = () => api.get('/api/productos/productos')
export const getCategorias = () => api.get('/api/productos/categorias')
export const createVenta = (data) => api.post('/api/ventas/ventas/', data)
export const getVentas = () => api.get('/api/ventas/ventas/')
