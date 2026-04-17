import React from 'react'

export default function PaymentModal({ total, onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 overflow-hidden">
        <div className="bg-emerald-600 p-4 text-white text-center">
          <h2 className="text-lg font-semibold">Confirmar Pago</h2>
        </div>
        
        <div className="p-6 text-center">
          <p className="text-gray-500 text-sm">Total a pagar</p>
          <p className="text-3xl font-bold text-emerald-600">${total.toLocaleString('es-CO')}</p>
        </div>
        
        <div className="p-4 space-y-2">
          <button 
            onClick={() => onConfirm('efectivo')}
            className="w-full bg-emerald-600 text-white py-3 rounded-lg hover:bg-emerald-700 flex items-center justify-center gap-2 font-medium"
          >
            <span>💵</span> Efectivo
          </button>
          
          <button 
            onClick={() => onConfirm('transferencia')}
            className="w-full bg-gray-700 text-white py-3 rounded-lg hover:bg-gray-800 flex items-center justify-center gap-2 font-medium"
          >
            <span>📱</span> Transferencia
          </button>
          
          <button 
            onClick={() => onConfirm('tarjeta')}
            className="w-full bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 flex items-center justify-center gap-2 font-medium"
          >
            <span>💳</span> Tarjeta
          </button>
        </div>
        
        <div className="p-4 border-t border-gray-100">
          <button 
            onClick={onCancel}
            className="w-full bg-gray-100 text-gray-600 py-2 rounded-lg hover:bg-gray-200"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  )
}
