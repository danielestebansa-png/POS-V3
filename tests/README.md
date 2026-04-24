# ============================================
# TESTS - README
# Cómo ejecutar las pruebas
# ============================================

## REQUISITOS

1. PostgreSQL instalado y corriendo
2. Base de datos "pos_test" creada:
   ```sql
   CREATE DATABASE pos_test;
   ```

3. Dependencias instaladas:
   ```bash
   pip install pytest pytest-asyncio sqlalchemy[asyncio] asyncpg
   ```

## ESTRUCTURA DE TESTS

```
tests/
├── conftest.py                    # Fixtures (DB, tenant, user, producto)
├── test_01_stock_concurrencia.py  # Test: Ventas simultáneas
├── test_02_stock_insuficiente.py # Test: Stock insuficiente
├── test_03_aislamiento_tenant.py # Test: Multi-tenant
└── test_04_numeros_factura.py    # Test: Números de factura
```

## EJECUTAR TODOS LOS TESTS

```bash
cd POS_V3/backend
pytest tests/ -v
```

## EJECUTAR UN TEST ESPECÍFICO

```bash
# Test 1: Concurrencia de stock
pytest tests/test_01_stock_concurrencia.py -v

# Test 2: Stock insuficiente
pytest tests/test_02_stock_insuficiente.py -v

# Test 3: Aislamiento tenant
pytest tests/test_03_aislamiento_tenant.py -v

# Test 4: Números de factura
pytest tests/test_04_numeros_factura.py -v
```

## EJECUTAR UN TEST ESPECÍFICO

```bash
pytest tests/test_01_stock_concurrencia.py::test_venta_simultanea_no_rompe_stock -v
```

## RESULTADOS ESPERADOS

### test_01_stock_concurrencia.py
- ✅ test_venta_simultanea_no_rompe_stock: Dos ventas simultáneas, una pasa, otra falla
- ✅ test_venta_simultanea_stock_negativo_prevenido: Stock negativo rechazado
- ✅ test_venta_con_permiso_stock_negativo_pasa: Permite negativo si está habilitado

### test_02_stock_insuficiente.py
- ✅ test_venta_rechazada_por_stock_insuficiente: Venta > stock = rechazo
- ✅ test_venta_exactamente_igual_al_stock_pasa: Venta = stock = éxito
- ✅ test_venta_con_stock_cero_falla: Stock 0 = rechazo
- ✅ test_multiple_items_stock_insuficiente: Un item sin stock = toda la venta fallida

### test_03_aislamiento_tenant.py
- ✅ test_tenant_no_puede_ver_productos_de_otro: Productos aislados
- ✅ test_tenant_no_puede_acceder_por_id: ID isolation
- ✅ test_ventas_aisladas_entre_tenants: Ventas aisladas
- ✅ test_inventario_aislado: Inventario aislado
- ✅ test_clientes_aislados: Clientes aislados
- ✅ test_movimientos_inventario_aislados: Movimientos aislados

### test_04_numeros_factura.py
- ✅ test_contador_factura_se_incrementa: Secuencia correcta
- ✅ test_dos_ventas_concurrentes_numeros_diferentes: Concurrencia OK
- ✅ test_cada_tenant_tiene_su_propio_contador: Contadores separados
- ✅ test_numero_factura_formato_correcto: Formato FAC-00001
- ✅ test_unique_constraint_numero_factura: UNIQUE constraint activo

## NOTAS

- Los tests usan una DB llamada "pos_test"
- Cada test hace rollback de sus cambios
- Los fixtures crean datos limpios para cada test
- Algunos tests requieren PostgreSQL real (no mock)