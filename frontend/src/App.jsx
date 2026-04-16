import React, { useState, useEffect } from 'react'
import Header from './components/Header'
import ProductGrid from './components/ProductGrid'
import Cart from './components/Cart'
import FacturaModal from './components/FacturaModal'
import Inventario from './components/Inventario'
import { getProductos, createVenta } from './services/api'

export default function App() {
  const [vista, setVista] = useState('pos') // 'pos' | 'inventario'
  const [productos, setProductos] = useState([])
  const [cart, setCart] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [ventaActual, setVentaActual] = useState(null)
  const [mostrarFactura, setMostrarFactura] = useState(false)

  // Cargar productos del backend real
  useEffect(() => {
    cargarProductos()
  }, [])

  const cargarProductos = async () => {
    try {
      setLoading(true)
      const response = await getProductos()
      
      if (response.data && Array.isArray(response.data)) {
        setProductos(response.data)
      }
    } catch (err) {
      console.error('Error cargando productos:', err)
      setError('No se pudieron cargar los productos')
    } finally {
      setLoading(false)
    }
  }

  // Agregar producto al carrito
  const handleSelectProduct = (producto) => {
    setCart((prevCart) => {
      const existente = prevCart.find((item) => item.product.id === producto.id)
      
      if (existente) {
        return prevCart.map((item) =>
          item.product.id === producto.id
            ? {
                ...item,
                quantity: item.quantity + 1,
                subtotal: (item.quantity + 1) * Number(producto.precio_venta),
              }
            : item
        )
      }
      
      return [
        ...prevCart,
        {
          product: producto,
          quantity: 1,
          subtotal: Number(producto.precio_venta),
        },
      ]
    })
  }

  // Eliminar producto del carrito
  const handleRemoveFromCart = (productId) => {
    setCart((prevCart) => prevCart.filter((item) => item.product.id !== productId))
  }

  // Actualizar cantidad
  const handleUpdateQuantity = (productId, nuevaCantidad) => {
    if (nuevaCantidad <= 0) {
      handleRemoveFromCart(productId)
      return
    }

    setCart((prevCart) =>
      prevCart.map((item) =>
        item.product.id === productId
          ? {
              ...item,
              quantity: nuevaCantidad,
              subtotal: nuevaCantidad * Number(item.product.precio_venta),
            }
          : item
      )
    )
  }

  // Vaciar carrito
  const handleClearCart = () => {
    setCart([])
  }

  // Cobrar - crear venta en backend real
  const handleCobrar = async (metodoPago) => {
    if (cart.length === 0) return

    try {
      setLoading(true)
      
      // Construir detalles según formato requerido
      const detalles = cart.map((item) => ({
        producto_id: item.product.id,
        cantidad: item.quantity,
        precio_unitario: Number(item.product.precio_venta),
        descuento: 0,
        iva: item.product.iva || 0,
      }))

      const ventaData = {
        detalles,
        metodo_pago: metodoPago,
      }

      const response = await createVenta(ventaData)
      
      // Guardar datos para la factura (incluir detalles del carrito)
      const ventaGuardada = {
        ...response.data,
        detalles_carrito: cart
      }
      
      setVentaActual(ventaGuardada)
      setMostrarFactura(true)
      setCart([])
      
      // Recargar productos para ver stock actualizado
      cargarProductos()
      
    } catch (err) {
      console.error('Error al crear venta:', err)
      const mensaje = err.response?.data?.detail || 'Error al procesar la venta'
      alert(mensaje)
    } finally {
      setLoading(false)
    }
  }

  // Cerrar modal de factura
  const handleCerrarFactura = () => {
    setMostrarFactura(false)
    setVentaActual(null)
  }

  // Cambiar vista
  const handleCambiarVista = (nuevaVista) => {
    setVista(nuevaVista)
  }

  // Renderizar según la vista actual
  if (vista === 'inventario') {
    return (
      <div className="min-h-screen bg-gray-100 flex flex-col">
        <Header vista={vista} onCambiarVista={handleCambiarVista} />
        <Inventario onVolver={() => setVista('pos')} />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Header vista={vista} onCambiarVista={handleCambiarVista} />
      
      <main className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Grid de productos - izquierda */}
        <div className="flex-1 p-4 lg:p-6 overflow-y-auto">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-800">Productos</h2>
            <span className="text-sm text-gray-500">
              {loading ? 'Cargando...' : `${productos.length} productos`}
            </span>
          </div>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
              {error}
            </div>
          )}
          
          <ProductGrid productos={productos} onSelectProduct={handleSelectProduct} />
        </div>

        {/* Carrito - derecha */}
        <div className="w-full lg:w-96 p-4 lg:p-6 bg-white lg:bg-gray-50 border-t lg:border-t-0 lg:border-l border-gray-200">
          <Cart
            items={cart}
            onRemove={handleRemoveFromCart}
            onUpdateQuantity={handleUpdateQuantity}
            onClear={handleClearCart}
            onCobrar={handleCobrar}
          />
        </div>
      </main>

      {/* Modal de Factura */}
      {mostrarFactura && ventaActual && (
        <FacturaModal 
          venta={ventaActual} 
          onClose={handleCerrarFactura} 
        />
      )}
    </div>
  )
}