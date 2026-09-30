from typing import Protocol

from app.modules.clientes.domain.entities import Cliente


class ClienteRepository(Protocol):
    def crear(self, cliente: Cliente) -> Cliente: pass
    def obtener(self, cliente_id: int) -> Cliente | None: pass
    def listar(self, solo_activos: bool = True) -> list[Cliente]: pass
    def actualizar(self, cliente: Cliente) -> Cliente: pass
    def obtener_o_crear_para_reserva(
        self, nombre: str, apellido: str, telefono: str
    ) -> int: pass