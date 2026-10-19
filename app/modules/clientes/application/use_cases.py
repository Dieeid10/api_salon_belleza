from app.modules.clientes.application.dto import (
    ClientResult,
    CreateClientCommand,
    UpdateClientCommand,
)
from app.modules.clientes.application.ports import ClientRepository
from app.modules.clientes.domain.entities import Client
from app.modules.clientes.domain.errors import ClientNotFound


def _to_result(client: Client) -> ClientResult:
    assert client.id is not None
    assert client.created_at is not None
    return ClientResult(
        id=client.id,
        first_name=client.first_name,
        last_name=client.last_name,
        phone=client.phone,
        email=client.email,
        is_active=client.is_active,
        created_at=client.created_at,
    )


class ClientUseCases:
    def __init__(self, repository: ClientRepository) -> None:
        self._repository = repository

    def create(self, command: CreateClientCommand) -> ClientResult:
        client = Client(
            first_name=command.first_name,
            last_name=command.last_name,
            phone=command.phone,
            email=command.email,
        )
        return _to_result(self._repository.create(client))

    def get(self, client_id: int) -> ClientResult:
        return _to_result(self._get_or_raise(client_id))

    def list_all(self, active_only: bool = True) -> list[ClientResult]:
        return [
            _to_result(client)
            for client in self._repository.list_all(active_only)
        ]

    def update(self, command: UpdateClientCommand) -> ClientResult:
        client = self._get_or_raise(command.client_id)
        client.update_details(
            command.first_name,
            command.last_name,
            command.phone,
            command.email,
        )
        return _to_result(self._repository.update(client))

    def deactivate(self, client_id: int) -> None:
        client = self._get_or_raise(client_id)
        client.deactivate()
        self._repository.update(client)

    def activate(self, client_id: int) -> None:
        client = self._get_or_raise(client_id)
        client.activate()
        self._repository.update(client)

    def _get_or_raise(self, client_id: int) -> Client:
        client = self._repository.get(client_id)
        if client is None:
            raise ClientNotFound()
        return client