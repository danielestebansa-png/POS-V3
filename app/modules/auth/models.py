# ============================================
# MODELS - AUTH (User roles)
# ============================================

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    VENDEDOR = "vendedor"
    CONTADOR = "contador"
    CAJERO = "cajero"


# El modelo User está definido en productos/models.py
# para evitar duplicación con Tenant