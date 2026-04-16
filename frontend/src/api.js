import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para agregar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Productos - Endpoints reales del backend
export const getProductos = () => api.get('/productos/productos')
export const getProducto = (id) => api.get(`/productos/productos/${id}`)
export const getProductoByBarcode = (codigo) => api.get(`/productos/productos/barcode/${codigo}`)

// Categorías
export const getCategorias = () => api.get('/productos/categorias')

// Ventas - Endpoints reales del backend
export const createVenta = (data) => api.post('/ventas/ventas/', data)
export const getVentas = () => api.get('/ventas/ventas/')
export const getVentasHoy = () => api.get('/ventas/ventas/hoy')

// Clientes
export const getClientes = () => api.get('/clientes/')
export const createCliente = (data) => api.post('/clientes/', data)

// Auth
export const login = (data) => api.post('/auth/login', data)
export const register = (data) => api.post('/auth/register', data)
export const getMe = () => api.get('/auth/me')

export default api
