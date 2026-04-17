import React, { useState } from 'react'

// Menú del sidebar - CORREGIDO con Mis tareas y POS al final
const menuItems = [
  { id: 'inicio', label: 'Inicio', icon: '🏠', page: 'dashboard' },
  { id: 'pos', label: 'POS', icon: '🛒', page: 'pos_full' }, // VA A PAGINA COMPLETA
  { id: 'facturar', label: 'Facturar', icon: '📄', page: 'facturar' },
  { id: 'ingresos', label: 'Ingresos', icon: '💰', 
    submenu: ['Factura de venta','Facturas recurrentes','Pagos recibidos','Devoluciones','Notas débito','Cotizaciones','Remisiones'] },
  { id: 'gastos', label: 'Gastos', icon: '📤',
    submenu: ['Facturas compra','Documento soporte','Notas ajuste','Pagos','Órdenes compra'] },
  { id: 'contactos', label: 'Contactos', icon: '👥',
    submenu: ['Clientes','Proveedores'] },
  { id: 'inventario', label: 'Inventario', icon: '📦',
    submenu: ['Items venta','Valor inventario','Ajustes','Gestión items','Listas precios','Bodegas','Categorías','Atributos'] },
  { id: 'bancos', label: 'Bancos', icon: '🏦',
    submenu: ['Bancos y cajas','Conciliaciones'] },
  { id: 'contabilidad', label: 'Contabilidad', icon: '📒',
    submenu: ['Sync contable','Catálogo cuentas','Comprobante','Activos','Libro diario','Fiscal'] },
  { id: 'reportes', label: 'Reportes', icon: '📊' },
  { id: 'mis_tareas', label: 'Mis tareas', icon: '✅' },
  { id: 'turnos', label: 'Turnos', icon: '⏰',
    submenu: ['Historial','Reporte'] },
  { id: 'devoluciones', label: 'Devoluciones', icon: '↩️' },
  { id: 'compras', label: 'Compras', icon: '🛍️' },
  { id: 'configuracion', label: 'Configuración', icon: '⚙️' },
  { id: 'nomina', label: 'Nómina', icon: '👤' },
  { id: 'ventas', label: 'Ventas', icon: '💵',
    submenu: ['Historial ventas','Comprobante informe diario'] },
  { id: 'portal_clientes', label: 'Portal Clientes', icon: '🌐' },
]

export default function Layout({ children, currentPage, onNavigate }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [expandedMenu, setExpandedMenu] = useState(null)

  const toggleMenu = (id) => {
    setExpandedMenu(expandedMenu === id ? null : id)
  }

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-gray-900 text-white transition-all duration-300 flex flex-col`}>
        {/* Logo */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          {sidebarOpen && <span className="font-bold text-lg">MI NEGOCIO</span>}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-xl">
            {sidebarOpen ? '◀' : '☰'}
          </button>
        </div>

        {/* Menu */}
        <nav className="flex-1 overflow-y-auto py-2">
          {menuItems.map((item) => (
            <div key={item.id}>
              <button
                onClick={() => {
                  if (item.page) {
                    onNavigate(item.page)
                  } else {
                    toggleMenu(item.id)
                  }
                }}
                className={`w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-800 ${
                  currentPage === item.page || expandedMenu === item.id ? 'bg-gray-800' : ''
                }`}
              >
                <span className="text-lg mr-3">{item.icon}</span>
                {sidebarOpen && (
                  <>
                    <span className="flex-1">{item.label}</span>
                    {item.submenu && (
                      <span>{expandedMenu === item.id ? '▲' : '��'}</span>
                    )}
                  </>
                )}
              </button>
              
              {/* Submenu */}
              {sidebarOpen && item.submenu && expandedMenu === item.id && (
                <div className="bg-gray-800">
                  {item.submenu.map((sub) => (
                    <button
                      key={sub}
                      onClick={() => onNavigate(item.id, sub)}
                      className="w-full px-8 py-2 text-left text-sm hover:bg-gray-700 text-gray-300"
                    >
                      {sub}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow p-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-800">
            {menuItems.find(m => m.page === currentPage)?.label || currentPage}
          </h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Admin</span>
            <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm">
              👤
            </button>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {children}
        </div>
      </main>
    </div>
  )
}
