from app.modules.clientes.application.dto import (
    ActualizarClienteCommand,
    ClienteResult,
    CrearClienteCommand,
)
from app.modules.clientes.application.ports import ClienteRepository
from app.modules.clientes.domain.entities import Cliente
from app.modules.clientes.domain.errors import ClienteNoEncontrada


def _to_result(cliente: Cliente) -> ClienteResult:
    assert cliente.id is not None
    assert cliente.fecha_creacion is not None
    return ClienteResult(
        id=cliente.id,
        nombre=cliente.nombre,
        apellido=cliente.apellido,
        telefono=cliente.telefono,
        email=cliente.email,
        activo=cliente.activo,
        fecha_creacion=cliente.fecha_creacion,
    )


class ClientesUseCases:
    def __init__(self, repo: ClienteRepository) -> None:
        self._repo = repo

    def crear(self, cmd: CrearClienteCommand) -> ClienteResult:
        cliente = Cliente(
            nombre=cmd.nombre,
            apellido=cmd.apellido,
            telefono=cmd.telefono,
            email=cmd.email,
        )
        return _to_result(self._repo.crear(cliente))

    def obtener(self, cliente_id: int) -> ClienteResult:
        return _to_result(self._get_or_fail(cliente_id))

    def listar(self, solo_activos: bool = True) -> list[ClienteResult]:
        return [_to_result(cliente) for cliente in self._repo.listar(solo_activos)]

    def actualizar(self, cmd: ActualizarClienteCommand) -> ClienteResult:
        cliente = self._get_or_fail(cmd.cliente_id)
        cliente.actualizar_datos(
            cmd.nombre,
            cmd.apellido,
            cmd.telefono,
            cmd.email,
        )
        return _to_result(self._repo.actualizar(cliente))

    def desactivar(self, cliente_id: int) -> None:
        cliente = self._get_or_fail(cliente_id)
        cliente.desactivar()
        self._repo.actualizar(cliente)

    def _get_or_fail(self, cliente_id: int) -> Cliente:
        cliente = self._repo.obtener(cliente_id)
        if cliente is None:
            raise ClienteNoEncontrada()
        return cliente