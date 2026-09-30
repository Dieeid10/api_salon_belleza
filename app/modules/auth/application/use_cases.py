from app.modules.auth.application.dto import SesionResult
from app.modules.auth.application.ports import AuthProvider


class AuthUseCases:
    def __init__(self, provider: AuthProvider) -> None:
        self._provider = provider

    def login(self, email: str, password: str) -> SesionResult:
        return self._provider.login(email, password)

    def refrescar(self, refresh_token: str) -> SesionResult:
        return self._provider.refrescar(refresh_token)