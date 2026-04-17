import React, { useState, useEffect } from 'react'

export default function App() {
  const [portal, setPortal] = useState('inicio')
  
  useEffect(() => {
    const h = window.location.hash.replace('#', '') || '/'
    if (h.startsWith('/pos')) setPortal('pos')
    else if (h.startsWith('/portal')) setPortal('portal')
    else setPortal('inicio')
  }, [])

  if (portal === 'pos') return <POSPortal />
  return <div style={{padding:20}}><h1>Mi Papelería</h1><button onClick={() => window.location.hash='#/pos/facturar'}>Entrar POS</button></div>
}

function POSPortal() {
  const [page, setPage] = useState('facturar')
  const [menuOpen, setMenuOpen] = useState(false)
  
  useEffect(() => {
    const h = window.location.hash.replace('#/pos/','')||'facturar'
    if (h) setPage(h)
  },[])

  const navigate = p => { setPage(p); window.location.hash = '#/pos/'+p }
  
  const menu = [
    {id:'inicio',label:'🏠 Inicio'},
    {id:'facturar',label:'📄 Facturar'},
    {id:'productos_servicios',label:'📦 Productos'},
    {id:'clientes',label:'👥 Clientes'},
  ]

  return (
    <div style={{minHeight:'100vh',background:'#f9f9f9'}}>
      <header style={{background:'white',padding:'12px',borderBottom:'1px solid #ddd',display:'flex',justifyContent:'space-between'}}>
        <button onClick={()=>setMenuOpen(!menuOpen)} style={{fontSize:24,background:'none',border:'none',cursor:'pointer'}}>☰</button>
        <span style={{fontWeight:'bold'}}>Mi Papelería POS</span>
        <div style={{width:40}}></div>
      </header>
      
      {menuOpen && (
        <div style={{position:'fixed',top:0,left:0,right:0,bottom:0,background:'rgba(0,0,0,0.5)'}} onClick={()=>setMenuOpen(false)}>
          <div style={{width:250,background:'white',height:'100%',padding:16}}>
            {menu.map(m => <button key={m.id} onClick={()=>{navigate(m.id);setMenuOpen(false)}} style={{display:'block',width:'100%',padding:'12px',textAlign:'left',border:'none',background:page===m.id?'#e0ffe0':'transparent',cursor:'pointer'}}>{m.label}</button>)}
          </div>
        </div>
      )}
      
      <main style={{padding:16}}>
        <h2>{menu.find(m=>m.id===page)?.label}</h2>
        <p>Página: {page}</p>
        <div style={{marginTop:20,padding:20,background:'white',borderRadius:8}}>
          <em>Contenido de {page} en construcción...</em>
        </div>
      </main>
    </div>
  )
}
