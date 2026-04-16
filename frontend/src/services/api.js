import axios from 'axios'

const API_URL = 'https://determined-compassion-production-801a.up.railway.app'

// Tenant ID del seed (Tienda Demo)
const TENANT_ID = "4a7e815e-f68e-46f4-863d-1d2f786301e8"

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-ID': TENANT_ID,
  },
})

// Debug: log todas las respuestas
api.interceptors.response.use(
  (response) => {
    console.log(`${response.config.method?.toUpperCase()} ${response.config.url}:`, response.data)
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const getProductos = () => api.get('/api/productos/productos')
export const getCategorias = () => api.get('/api/productos/categorias')
export const createVenta = (data) => api.post('/api/ventas/ventas/', data)
export const getVentas = () => api.get('/api/ventas/ventas/')
