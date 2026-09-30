from dataclasses import dataclass

from app.shared.error import ValidationError


@dataclass
class Profesional:
    nombre: str
    perfil_id: str | None = None
    activo: bool = True
    id: int | None = None

    def __post_init__(self) -> None:
        self.nombre = self.nombre.strip()
        if not self.nombre:
            raise ValidationError("El nombre del profesional es obligatorio")
        if len(self.nombre) > 100:
            raise ValidationError("El nombre no puede superar 100 caracteres")

    def actualizar_datos(self, nombre: str, perfil_id: str | None) -> None:
        actualizado = Profesional(
            nombre=nombre,
            perfil_id=perfil_id,
            activo=self.activo,
            id=self.id,
        )
        self.nombre = actualizado.nombre
        self.perfil_id = actualizado.perfil_id

    def desactivar(self) -> None:
        self.activo = False