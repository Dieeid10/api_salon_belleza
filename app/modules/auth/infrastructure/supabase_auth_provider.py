import httpx

from app.modules.auth.application.dto import SessionResult
from app.modules.auth.domain.errors import InvalidCredentials
from app.shared.infrastructure.config import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseAuthProvider:
    def _request_token(self, grant_type: str, body: dict) -> SessionResult:
        resp = httpx.post(
            f"{settings.supabase_url}/auth/v1/token",
            params={"grant_type": grant_type},
            headers={"apikey": settings.supabase_anon_key},
            json=body,
            timeout=10,
        )
        if resp.status_code in (400, 401):
            logger.warning("Supabase auth %s: %s", resp.status_code, resp.text)
            raise InvalidCredentials()
        resp.raise_for_status()
        data = resp.json()
        return SessionResult(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_in=data["expires_in"],
        )

    def login(self, email: str, password: str) -> SessionResult:
        return self._request_token("password", {"email": email, "password": password})

    def refresh(self, refresh_token: str) -> SessionResult:
        return self._request_token("refresh_token", {"refresh_token": refresh_token})