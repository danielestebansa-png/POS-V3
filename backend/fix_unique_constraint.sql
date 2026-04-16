-- Agregar UNIQUE constraint a ventas.numero si no existe
-- Esto evita números de factura duplicados dentro de un tenant

ALTER TABLE ventas 
ADD CONSTRAINT unique_numero_por_tenant 
UNIQUE (tenant_id, numero);
