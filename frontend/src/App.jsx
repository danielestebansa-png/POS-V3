import React, { useState, useEffect } from 'react'
import ProductManager from './components/ProductManager'
import PaymentModal from './components/PaymentModal'
import ReceiptModal from './components/ReceiptModal'
import ProductSearch from './components/ProductSearch'
import HistorialVentas from './components/HistorialVentas'
import InformeDiario from './components/InformeDiario'
import HistorialVentas from './components/HistorialVentas'

const NOMBRE_TIENDA = "Mi Papelería"

export default function App() {
  const [portal, setPortal] = useState('inicio')
  
  useEffect(() => {
    const path = window.location.pathname
    if (path.startsWith('/pos')) setPortal('pos')
    else if (path.startsWith('/portal')) setPortal('portal')
    else setPortal('inicio')
  }, [])

  if (portal === 'pos') return <POSPortal />
  if (portal === 'portal') return <PortalClientes />
  return <InicioPortal />
}

import Layout from './components/layout/Layout'

function InicioPortal() {
  const [currentPage, setCurrentPage] = useState('inicio')
  const navigateTo = (page) => {
    if (page === 'pos' || page === 'pos_full') window.location.href = '/pos'
    else if (page === 'portal') window.location.href = '/portal'
    else setCurrentPage(page)
  }
  return <Layout currentPage={currentPage} onNavigate={navigateTo}><Dashboard onNavigate={navigateTo} /></Layout>
}

function Dashboard({ onNavigate }) {
  return (
    <div className="space-y-6">
      <button onClick={() => onNavigate('pos')} className="w-full bg-emerald-600 text-white p-8 rounded-xl hover:bg-emerald-700 transition">
        <div className="flex items-center justify-between">
          <div><h2 className="text-3xl font-bold">🛒 {NOMBRE_TIENDA}</h2><p className="text-emerald-200">Sistema</p></div>
          <div className="text-4xl">→</div>
        </div>
      </button>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded shadow-sm border text-center"><div className="text-3xl mb-2 text-emerald-600">💰</div><p className="text-2xl font-bold">$125,000</p><p className="text-gray-500 text-sm">Ventas Hoy</p></div>
        <div className="bg-white p-6 rounded shadow-sm border text-center"><div className="text-3xl mb-2 text-gray-600">📦</div><p className="text-2xl font-bold">10</p><p className="text-gray-500 text-sm">Productos</p></div>
        <div className="bg-white p-6 rounded shadow-sm border text-center"><div className="text-3xl mb-2 text-gray-600">👥</div><p className="text-2xl font-bold">5</p><p className="text-gray-500 text-sm">Clientes</p></div>
      </div>
    </div>
  )
}

function POSPortal() {
  const [currentPage, setCurrentPage] = useState('facturar')
  const [menuOpen, setMenuOpen] = useState(false)
  
  const posMenu = [
    { id: 'facturar', label: 'Facturar', icon: '📄' },
    { id: 'documentos', label: 'Documentos electrónicos', icon: '📧' },
    { id: 'ingresos', label: 'Ingresos', icon: '💰', submenu: [
      { id: 'historial_ventas', label: 'Historial de ventas' },
      { id: 'informe_diario', label: 'Comprobante de informe diario' }
    ]},
    { id: 'turnos', label: 'Turnos', icon: '⏰', submenu: [
      { id: 'historial_turnos', label: 'Historial de turnos' },
      { id: 'reporte_turnos', label: 'Reporte de turnos' }
    ]},
    { id: 'efectivo', label: 'Gestión de efectivo', icon: '💵' },
    { id: 'devoluciones', label: 'Devoluciones', icon: '↩️' },
    { id: 'contactos', label: 'Contactos', icon: '👥' },
    { id: 'inventario', label: 'Inventario', icon: '📦', submenu: [
      { id: 'productos_servicios', label: 'Productos y Servicios' },
      { id: 'promociones', label: 'Promociones' },
      { id: 'ajustes_inv', label: 'Ajustes de inventario' },
      { id: 'bodegas', label: 'Bodegas' },
      { id: 'listas_precios', label: 'Listas de Precios' },
      { id: 'gestion_inv', label: 'Gestión de Inventario' }
    ]},
    { id: 'compras', label: 'Compras', icon: '🛒' },
    { id: 'configuraciones', label: 'Configuraciones', icon: '⚙️' },
    { id: 'portal', label: 'Portal Clientes', icon: '🌐' },
  ]

  const renderContent = () => {
    if (currentPage === 'facturar') return <FacturarModule />
    if (currentPage === 'inventario') return <InventarioModule />
    if (currentPage === 'historial_ventas') return <HistorialVentas />
    if (currentPage === 'informe_diario') return <InformeDiario />
    if (currentPage === 'productos_servicios') return <Inventario />
    if (currentPage === 'gestion_productos') return <ProductManager />
    return <Placeholder title={posMenu.find(m => m.id === currentPage)?.label || 'En construcción'} />
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-30">
        <button onClick={() => setMenuOpen(true)} className="text-2xl hover:bg-gray-100 p-1 rounded">☰</button>
        <div className="flex items-center gap-3">
          <span className="font-bold text-lg text-gray-800">{NOMBRE_TIENDA}</span>
          <span className="bg-emerald-600 text-white px-2 py-1 rounded text-xs font-medium">POS</span>
        </div>
        <div className="w-8"></div>
      </header>

      {menuOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => setMenuOpen(false)}>
          <aside className="w-72 bg-white h-full shadow-xl overflow-y-auto" onClick={e => e.stopPropagation()}>
            <div className="p-4 border-b font-bold">{NOMBRE_TIENDA}</div>
            <nav className="py-2">
              {posMenu.map((item, idx) => (
                <div key={item.id}>
                  <button 
                    onClick={() => {
                      if (item.submenu) {
                        const el = document.getElementById(`submenu-${idx}`)
                        el.classList.toggle('hidden')
                      } else {
                        setCurrentPage(item.id)
                        setMenuOpen(false)
                      }
                    }}
                    className={`w-full px-4 py-2.5 text-left flex justify-between items-center hover:bg-gray-50 ${currentPage === item.id ? 'bg-emerald-50 text-emerald-700' : ''}`}
                  >
                    <span className="flex items-center gap-3"><span>{item.icon}</span><span>{item.label}</span></span>
                    {item.submenu && <span className="text-xs">▼</span>}
                  </button>
                  {item.submenu && (
                    <div id={`submenu-${idx}`} className="hidden bg-gray-50 pl-8">
                      {item.submenu.map(sub => (
                        <button 
                          key={sub.id}
                          onClick={() => { setCurrentPage(sub.id); setMenuOpen(false) }}
                          className="w-full px-4 py-2 text-left text-sm text-gray-600 hover:bg-gray-100"
                        >
                          {sub.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </nav>
            <div className="border-t">
              <button onClick={() => window.location.href = '/'} className="w-full px-4 py-2.5 text-left text-gray-500">← Inicio</button>
            </div>
          </aside>
        </div>
      )}
      <main className="flex-1 p-4">{renderContent()}</main>
    </div>
  )
}

function Placeholder({ title }) {
  return <div className="text-center mt-20"><p className="text-6xl mb-4 text-gray-300">🚧</p><h2 className="text-xl font-medium">{title}</h2><p className="text-gray-400 mt-2">En construcción</p></div>
}

function FacturarModule() {
  const [ventas, setVentas] = useState([{ id: 1, nombre: 'Venta 1', items: [] }])
  const [ventaActiva, setVentaActiva] = useState(0)
  const [showPayment, setShowPayment] = useState(false)
  const [showReceipt, setShowReceipt] = useState(false)
  const [metodoSeleccionado, setMetodoSeleccionado] = useState('')
  const [ventaResult, setVentaResult] = useState(null)

  const getCarrito = () => ventas[ventaActiva]?.items || []
  const getTotal = () => getCarrito().reduce((s, i) => s + i.subtotal, 0)

  const agregarAlCarrito = (producto) => {
    setVentas(prev => prev.map((v, idx) => {
      if (idx !== ventaActiva) return v
      const items = v.items
      const existe = items.find(i => i.product.id === producto.id)
      if (existe) {
        return { ...v, items: items.map(i => i.product.id === producto.id ? {...i, quantity: i.quantity + 1, subtotal: (i.quantity + 1) * Number(producto.precio_venta)} : i) }
      }
      return { ...v, items: [...items, { product: producto, quantity: 1, subtotal: Number(producto.precio_venta), precio: producto.precio_venta }] }
    }))
  }

  const cambiarCantidad = (productoId, qty) => {
    if (qty <= 0) {
      setVentas(prev => prev.map((v, idx) => idx !== ventaActiva ? v : { ...v, items: v.items.filter(i => i.product.id !== productoId) }))
    } else {
      setVentas(prev => prev.map((v, idx) => idx !== ventaActiva ? v : { ...v, items: v.items.map(i => i.product.id === productoId ? {...i, quantity: qty, subtotal: qty * Number(i.product.precio_venta)} : i) }))
    }
  }

  const nuevaVenta = () => {
    const nuevoId = ventas.length + 1
    setVentas(prev => [...prev, { id: nuevoId, nombre: `Venta ${nuevoId}`, items: [] }])
    setVentaActiva(ventas.length)
  }

  const cerrarVenta = (index) => {
    if (ventas.length === 1 && index === 0) return
    setVentas(prev => prev.filter((_, idx) => idx !== index))
    if (ventaActiva >= index && ventaActiva > 0) setVentaActiva(ventaActiva - 1)
  }

  const procesarVenta = async (metodo) => {
    if (getCarrito().length === 0) return
    try {
      const data = { detalles: getCarrito().map(i => ({ producto_id: i.product.id, cantidad: i.quantity, precio_unitario: Number(i.precio), descuento: 0 })), metodo_pago: metodo }
      const res = await createVenta(data)
      setVentaResult(res.data)
      setMetodoSeleccionado(metodo)
      setShowPayment(false)
      setShowReceipt(true)
      setVentas(prev => prev.map((v, idx) => idx !== ventaActiva ? v : { ...v, items: [] }))
    } catch (e) { alert('Error: ' + e.message) }
  }

  const cartActual = getCarrito()
  const totalActual = getTotal()

  return (
    <div className="flex gap-4 h-full">
      <div className="flex-1">
        <ProductSearch onAddToCart={agregarAlCarrito} />
      </div>
      
      <div className="w-80 bg-white rounded-lg shadow-sm border p-4 h-fit sticky top-4">
        <div className="flex flex-wrap gap-1 mb-4">
          {ventas.map((v, idx) => (
            <button
              key={idx}
              onClick={() => setVentaActiva(idx)}
              className={`px-2 py-1 text-xs font-medium rounded ${
                ventaActiva === idx ? 'bg-emerald-600 text-white' : 'bg-gray-100 text-gray-600'
              }`}
            >
              {v.nombre}
              {v.items.length > 0 && ` (${v.items.length})`}
            </button>
          ))}
          <button onClick={nuevaVenta} className="px-2 py-1 text-xs text-emerald-600 hover:bg-emerald-50 rounded">
            + Nueva
          </button>
        </div>
        
        <div className="flex justify-between items-center mb-3 border-b pb-2">
          <h2 className="text-base font-medium">{ventas[ventaActiva]?.nombre}</h2>
          <span className="text-xs text-gray-500">{cartActual.length} items</span>
        </div>
        
        {cartActual.length === 0 ? (
          <p className="text-gray-400 text-sm py-8 text-center">Seleccione productos</p>
        ) : (
          <>
            <div className="space-y-2 mb-3 max-h-48 overflow-y-auto">
              {cartActual.map(i => (
                <div key={i.product.id} className="flex justify-between items-center border-b pb-2">
                  <div className="flex-1">
                    <p className="font-medium text-sm truncate">{i.product.nombre}</p>
                    <div className="flex items-center gap-1 mt-1">
                      <button onClick={() => cambiarCantidad(i.product.id, i.quantity-1)} className="bg-gray-100 w-6 h-6 rounded text-sm">-</button>
                      <span className="text-sm px-2">{i.quantity}</span>
                      <button onClick={() => cambiarCantidad(i.product.id, i.quantity+1)} className="bg-gray-100 w-6 h-6 rounded text-sm">+</button>
                    </div>
                  </div>
                  <div className="text-right ml-2">
                    <p className="font-bold text-sm">${i.subtotal.toLocaleString()}</p>
                    <button onClick={() => cambiarCantidad(i.product.id, 0)} className="text-red-500 text-xs">X</button>
                  </div>
                </div>
              ))}
            </div>
            <div className="border-t pt-3 flex justify-between font-bold text-lg">
              <span>Total:</span>
              <span className="text-emerald-600">${totalActual.toLocaleString()}</span>
            </div>
            <button 
              onClick={() => setShowPayment(true)} 
              disabled={!totalActual}
              className="w-full bg-emerald-600 text-white py-3 rounded mt-3 hover:bg-emerald-700 disabled:opacity-50 font-medium"
            >
              💵 COBRAR
            </button>
          </>
        )}
      </div>

      {showPayment && <PaymentModal total={totalActual} onConfirm={procesarVenta} onCancel={() => setShowPayment(false)} />}
      {showReceipt && ventaResult && (
        <ReceiptModal 
          venta={{
            numero_factura: ventaResult?.numero || '001',
            total: totalActual,
            metodo_pago: metodoSeleccionado,
            detalles: cartActual.map(i => ({ nombre_producto: i.product.nombre, cantidad: i.quantity, precio_unitario: Number(i.precio), subtotal: i.subtotal }))
          }} 
          onClose={() => setShowReceipt(false)} 
        />
      )}
    </div>
  )
}

function InventarioModule() {
  const [productos, setProductos] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => { (async () => { setLoading(true); try { const r = await getProductos(); if (r.data) setProductos(r.data) } finally { setLoading(false) } })() }, [])

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-medium">📦 Inventario</h2>
        <button className="bg-emerald-600 text-white px-4 py-2 rounded text-sm">+ Nuevo</button>
      </div>
      {loading && <p>Cargando...</p>}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b"><tr><th className="text-left p-3">Producto</th><th className="text-right p-3">Precio</th><th className="text-right p-3">Stock</th><th className="text-right p-3">Valor</th></tr></thead>
          <tbody>{productos.map(p => <tr key={p.id} className="border-b"><td className="p-3">{p.nombre}</td><td className="text-right p-3">${Number(p.precio_venta).toLocaleString()}</td><td className="text-right p-3">{p.stock}</td><td className="text-right p-3 text-emerald-600">${(Number(p.precio_venta) * p.stock).toLocaleString()}</td></tr>)}</tbody>
        </table>
      </div>
    </div>
  )
}

function PortalClientes() {
  const [page, setPage] = useState('empresa')
  const menu = [
    { id: 'empresa', label: 'Empresa', icon: '🏢' },
    { id: 'soluciones', label: 'Soluciones', icon: '💡' },
    { id: 'perfil', label: 'Perfil', icon: '👤' },
    { id: 'seguridad', label: 'Seguridad', icon: '🔒' },
  ]

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <div className="w-56 bg-white border-r flex flex-col">
        <div className="p-4 border-b font-bold">{NOMBRE_TIENDA}</div>
        <nav className="flex-1 py-2">{menu.map(m => <button key={m.id} onClick={() => setPage(m.id)} className={`w-full px-4 py-2.5 text-left flex gap-2 hover:bg-gray-50 ${page === m.id ? 'bg-emerald-50' : ''}`}><span>{m.icon}</span><span>{m.label}</span></button>)}</nav>
        <button onClick={() => window.location.href = '/'} className="p-3 border-t text-left text-gray-500">← Volver</button>
      </div>
      <main className="flex-1 p-6"><div className="bg-white rounded-lg shadow-sm border p-6"><h2 className="text-lg font-medium">{menu.find(m => m.id === page)?.label}</h2><p className="text-gray-400 mt-2 text-sm">En construcción</p></div></main>
    </div>
  )
}
