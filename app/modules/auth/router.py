# ============================================
# AUTH ROUTER - Login & Registration
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.modules.productos.models import User, UserRole

router = APIRouter()


# ============================================
# SCHEMAS / DTOs
# ============================================

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    rol: UserRole = UserRole.VENDEDOR


class UserResponse(BaseModel):
    id: str
    email: str
    nombre: str
    rol: str
    estado: str
    
    class Config:
        from_attributes = True


# ============================================
# ENDPOINTS
# ============================================

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Buscar usuario
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Verificar password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Verificar estado
    if user.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear token
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id)}
    )
    
    return LoginResponse(
        access_token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "nombre": user.nombre,
            "rol": user.rol.value
        }
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserCreate, db: AsyncSession = Depends(get_db)):
    # Verificar si email existe
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )
    
    # Crear usuario
    # NOTA: En producción, primero crear el tenant, luego el usuario
    # Por ahora usamos un tenant temporal para demo
    from app.modules.tenants.models import Tenant
    
    # Buscar o crear tenant demo
    result = await db.execute(select(Tenant).limit(1))
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        tenant = Tenant(
            nombre="Demo Empresa",
            nit="123456789",
            estado="activo"
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
    
    user = User(
        tenant_id=tenant.id,
        email=request.email,
        password_hash=get_password_hash(request.password),
        nombre=request.nombre,
        rol=request.rol,
        estado="activo"
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        nombre=user.nombre,
        rol=user.rol.value,
        estado=user.estado
    )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.id == current_user["user_id"])
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id": str(user.id),
        "email": user.email,
        "nombre": user.nombre,
        "rol": user.rol.value,
        "tenant_id": str(user.tenant_id)
    }