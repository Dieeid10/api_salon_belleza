from app.modules.auth.application.dto import SessionResult
from app.modules.auth.application.ports import AuthProvider


class AuthUseCases:
    def __init__(self, provider: AuthProvider) -> None:
        self._provider = provider

    def login(self, email: str, password: str) -> SessionResult:
        return self._provider.login(email, password)

    def refresh(self, refresh_token: str) -> SessionResult:
        return self._provider.refresh(refresh_token)