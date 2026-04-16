// Tipos para el POS

export interface Product {
  id: string
  nombre: string
  precio_venta: number
  precio_costo?: number
  codigo_barras?: string
  iva: number
  permite_stock_negativo: boolean
  estado: string
  categoria_id?: string
}

export interface CartItem {
  product: Product
  quantity: number
  subtotal: number
}

export interface Venta {
  id: string
  tenant_id: string
  numero: string
  subtotal: number
  descuento: number
  iva: number
  total: number
  metodo_pago: string
  estado: string
  created_at: string
}

export interface Cliente {
  id: string
  nombre: string
  documento: string
  email?: string
  telefono?: string
}
