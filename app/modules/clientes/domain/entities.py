from dataclasses import dataclass
from datetime import datetime

from app.shared.error import ValidationError


@dataclass
class Cliente:
    nombre: str
    apellido: str
    telefono: str | None = None
    email: str | None = None
    activo: bool = True
    id: int | None = None
    fecha_creacion: datetime | None = None

    def __post_init__(self) -> None:
        self.nombre = self.nombre.strip()
        self.apellido = self.apellido.strip()
        self.telefono = self.telefono.strip() if self.telefono else None
        self.email = self.email.strip().lower() if self.email else None

        if not self.nombre:
            raise ValidationError("El nombre de la clienta es obligatorio")
        if len(self.nombre) > 100:
            raise ValidationError("El nombre no puede superar 100 caracteres")
        if not self.apellido:
            raise ValidationError("El apellido de la clienta es obligatorio")
        if len(self.apellido) > 100:
            raise ValidationError("El apellido no puede superar 100 caracteres")
        if self.telefono is not None and len(self.telefono) > 50:
            raise ValidationError("El teléfono no puede superar 50 caracteres")
        if self.email is not None and len(self.email) > 100:
            raise ValidationError("El email no puede superar 100 caracteres")
        if self.telefono is None and self.email is None:
            raise ValidationError("La clienta debe tener teléfono o email de contacto")

    def actualizar_datos(
        self,
        nombre: str,
        apellido: str,
        telefono: str | None,
        email: str | None,
    ) -> None:
        actualizado = Cliente(
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            email=email,
            activo=self.activo,
            id=self.id,
            fecha_creacion=self.fecha_creacion,
        )
        self.nombre = actualizado.nombre
        self.apellido = actualizado.apellido
        self.telefono = actualizado.telefono
        self.email = actualizado.email

    def desactivar(self) -> None:
        self.activo = False