-- Fix UUID for contador_facturas
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
ALTER TABLE contador_facturas ALTER COLUMN id SET DEFAULT uuid_generate_v4();

-- Fix UNIQUE constraint for ventas
ALTER TABLE ventas ADD CONSTRAINT unique_numero_por_tenant UNIQUE (tenant_id, numero);
