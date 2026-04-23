import React from 'react'

export default function CategoriaModal({ show, onClose, nombre, setNombre, descripcion, setDescripcion, onCrear }) {
  if (!show) return null;
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <h2 className="text-xl font-bold mb-4">New Category</h2>
        <div className="space-y-3">
          <input placeholder="Name *" value={nombre} onChange={e => setNombre(e.target.value)} className="w-full border rounded px-3 py-2" />
          <textarea placeholder="Description" value={descripcion} onChange={e => setDescripcion(e.target.value)} className="w-full border rounded px-3 py-2" rows={3} />
        </div>
        <div className="flex gap-2 mt-4">
          <button onClick={onClose} className="flex-1 border py-2 rounded text-gray-600">Cancel</button>
          <button onClick={onCrear} className="flex-1 bg-emerald-600 text-white py-2 rounded">Create</button>
        </div>
      </div>
    </div>
  )
}
