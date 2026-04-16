# POS Frontend - React + Vite + Tailwind

## Estructura

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── index.css
    ├── components/
    │   ├── ProductGrid.jsx
    │   ├── Cart.jsx
    │   ├── CartItem.jsx
    │   └── Header.jsx
    ├── services/
    │   └── api.js
    └── types/
        └── index.js
```

## Instalación

```bash
cd C:\Users\Daniel\Documents\POS_V3\frontend
npm install
npm run dev
```

## Configuración

1. Instalar dependencias:
```bash
npm install
```

2. Configurar API en `src/services/api.js`:
```javascript
const API_URL = "http://localhost:8000/api"
```

3. Ejecutar:
```bash
npm run dev
```
