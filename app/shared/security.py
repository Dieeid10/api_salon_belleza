import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.shared.infrastructure.db.database import db
from app.shared.infrastructure.config import settings

_bearer = HTTPBearer(auto_error=False)
_SUPABASE_ISSUER = f"{settings.supabase_url.rstrip('/')}/auth/v1"
_JWKS_CLIENT = jwt.PyJWKClient(f"{_SUPABASE_ISSUER}/.well-known/jwks.json")


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Falta el token")
    try:
        if settings.jwt_algorithm == "ES256":
            signing_key = _JWKS_CLIENT.get_signing_key_from_jwt(
                creds.credentials
            ).key
        else:
            if not settings.supabase_jwt_secret:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Falta SUPABASE_JWT_SECRET para HS256",
                )
            signing_key = settings.supabase_jwt_secret

        claims = jwt.decode(
            creds.credentials,
            signing_key,
            algorithms=[settings.jwt_algorithm],
            audience="authenticated",
            issuer=_SUPABASE_ISSUER,
        )
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")

    issued_at = claims.get("iat")
    expires_at = claims.get("exp")
    max_lifetime = settings.jwt_expiration_hours * 60 * 60
    if (
        not isinstance(issued_at, (int, float))
        or not isinstance(expires_at, (int, float))
        or expires_at <= issued_at
        or expires_at - issued_at > max_lifetime
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Duración del token inválida")
    return claims


def current_staff(user: dict = Depends(current_user)) -> dict:
    """El JWT prueba quién es; que sea personal lo decide la tabla perfiles."""
    with db.transaction() as conn:
        row = conn.execute(
            "SELECT rol FROM perfiles WHERE id = %s", (user["sub"],)
        ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No tenés permiso")
    return {**user, "rol": row["rol"]}


def require_role(*roles: str):
    def checker(staff: dict = Depends(current_staff)) -> dict:
        if staff["rol"] not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tenés permiso")
        return staff

    return checker

