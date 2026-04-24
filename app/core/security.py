# ============================================
# SECURITY - Autenticación simplificada
# ============================================

from fastapi import Header, HTTPException, status
from typing import Optional
from uuid import UUID, uuid4


async def get_current_user(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
) -> dict:
    """Extraer tenant_id del header X-Tenant-ID"""
    
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Tenant-ID header requerido",
        )
    
    try:
        UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID inválido",
        )
    
    # Generar un user_id válido
    system_user_id = str(uuid4())
    
    return {
        "id": system_user_id,
        "tenant_id": x_tenant_id,
        "email": "sistema@local",
        "rol": "vendedor",
        "user_id": system_user_id,
    }


def get_password_hash(password: str) -> str:
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return True


def create_access_token(data: dict, expires_delta=None) -> str:
    return "mock_token"


def decode_token(token: str) -> dict:
    return {"sub": "user", "tenant_id": "default"}