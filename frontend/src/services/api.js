import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'https://determined-compassion-production-801a.up.railway.app'

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

// Interceptor para agregar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // Siempre incluir tenant ID
  config.headers['X-Tenant-ID'] = TENANT_ID
  return config
})

// Productos - Endpoints reales del backend
export const getProductos = () => api.get('/api/productos/productos')
export const getProducto = (id) => api.get(`/api/productos/productos/${id}`)
export const getProductoByBarcode = (codigo) => api.get(`/api/productos/productos/barcode/${codigo}`)

// Categorías
export const getCategorias = () => api.get('/api/productos/categorias')

// Ventas - Endpoints reales del backend
export const createVenta = (data) => api.post('/api/ventas/ventas/', data)
export const getVentas = () => api.get('/api/ventas/ventas/')
export const getVentasHoy = () => api.get('/api/ventas/ventas/hoy')

// Clientes
export const getClientes = () => api.get('/api/clientes/')
export const createCliente = (data) => api.post('/api/clientes/', data)

// Auth
export const login = (data) => api.post('/api/auth/login', data)
export const register = (data) => api.post('/api/auth/register', data)
export const getMe = () => api.get('/api/auth/me')

export default api
