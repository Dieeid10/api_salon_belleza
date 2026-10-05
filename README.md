# Salon API

API REST del sistema de gestion de un salon de belleza. Expone operaciones para
clientes, servicios, profesionales, descuentos, turnos y ventas. La identidad se
deleg a Supabase Auth; la API valida los JWT y aplica permisos antes de ejecutar
operaciones sobre PostgreSQL.

## Stack

- Python 3.12 o superior.
- FastAPI y Pydantic para HTTP, validacion y esquemas.
- Psycopg 3 y `psycopg_pool` para PostgreSQL.
- Supabase Auth como proveedor de identidad y emisor de tokens.
- PyJWT para verificar access tokens.
- `uv` para dependencias y ejecucion del proyecto.

## Arquitectura

La API es un monolito modular organizado alrededor de los dominios del salon.
Cada modulo separa la logica de negocio de los mecanismos HTTP y de persistencia:

```text
app/
	main.py
	modules/
		<modulo>/
			domain/             # entidades, reglas y errores del dominio
			application/        # casos de uso, DTOs y puertos
			infrastructure/
				api/              # routers, esquemas y dependencias HTTP
				persistence/      # adaptadores concretos para PostgreSQL
	shared/
		config.py             # acceso a configuracion tipada
		error.py              # errores de dominio compartidos
		security.py           # validacion JWT, personal y roles
		infrastructure/
			config.py           # variables de entorno
			db/                 # pool y utilidades compartidas de base de datos
```

El flujo habitual de una peticion es:

1. FastAPI recibe la peticion y valida el cuerpo y los parametros con un esquema
	 Pydantic.
2. El router obtiene el caso de uso mediante dependencias y convierte el
	 esquema HTTP en un comando o consulta de aplicacion.
3. El caso de uso ejecuta las reglas del dominio a traves de puertos, sin
	 depender de FastAPI ni de Psycopg.
4. Un adaptador de persistencia implementa el puerto con PostgreSQL y devuelve
	 entidades o resultados.
5. El router transforma el resultado en la respuesta HTTP.

Patrones usados en el codigo:

- **Arquitectura hexagonal / limpia:** dominio y aplicacion separados de los
	adaptadores de entrada (API) y salida (persistencia y Supabase Auth).
- **Repository y puertos:** los casos de uso dependen de contratos; los
	repositorios Psycopg implementan esos contratos.
- **Use cases:** cada operacion importante tiene una accion de aplicacion
	explicita; turnos separa, por ejemplo, reserva, disponibilidad y cambio de
	estado.
- **DTOs y Commands/Queries:** transportan datos entre capas sin exponer las
	entidades de dominio como contratos de entrada.
- **Unit of Work:** el flujo de turnos agrupa lecturas y escrituras relacionadas
	en una transaccion; un fallo revierte el trabajo asociado.
- **Dependency Injection:** FastAPI construye casos de uso y adaptadores a
	traves de `Depends`.
- **Errores de dominio:** `main.py` traduce errores comunes a respuestas HTTP
	coherentes (404, 409, 403 y 422, entre otras).

## Modulos y endpoints

Las rutas siguientes son relativas a la raiz de la API. Los endpoints que
requieren personal aceptan `Authorization: Bearer <access_token>`.

| Modulo | Rutas | Acceso y comportamiento |
| --- | --- | --- |
| Autenticacion | `POST /auth/login`, `POST /auth/refresh` | Publicas. Login con email/clave y renovacion de tokens de Supabase. |
| Clientes | `GET /clientes/`, `GET /clientes/{id}`, `POST /clientes/`, `PUT /clientes/{id}`, `DELETE /clientes/{id}` | Personal (`dueno` o `vendedor`). El borrado es una desactivacion logica. `solo_activos` es true por defecto. |
| Servicios | `GET /servicios/`, `GET /servicios/{id}` | Publicas; solo catalogo activo y visible online. |
| Servicios | `GET /servicios/gestion`, `GET /servicios/gestion/{id}`, `POST /servicios/`, `PUT /servicios/{id}`, `DELETE /servicios/{id}` | Personal (`dueno` o `vendedor`). Permite gestionar catalogo, incluidos elementos inactivos/no visibles en la lista de gestion. |
| Descuentos | `GET /descuentos/` | Publica; devuelve descuentos publicos vigentes. |
| Descuentos | `GET /descuentos/gestion`, `GET /descuentos/gestion/{id}`, `POST /descuentos/`, `PUT /descuentos/{id}`, `DELETE /descuentos/{id}` | Solo `dueno`. El descuento de tipo `chisme` es de uso interno. |
| Profesionales | `GET /profesionales/`, `GET /profesionales/{id}` | Publicas; el listado solo incluye activos por defecto. |
| Profesionales | `POST /profesionales/`, `PUT /profesionales/{id}`, `DELETE /profesionales/{id}` | Solo `dueno`. El borrado es una desactivacion logica. |
| Turnos publicos | `GET /turnos/disponibilidad`, `POST /turnos/` | Publicas. Consultan horarios disponibles y reservan a nombre de una persona. |
| Turnos de gestion | `GET /admin/turnos/`, `GET /admin/turnos/{id}`, `POST /admin/turnos/`, `POST /admin/turnos/{id}/cancelar`, `PATCH /admin/turnos/{id}/estado` | Personal (`dueno` o `vendedor`). El listado requiere `desde` y `hasta`; admite filtros por profesional y estado. |
| Ventas | `GET /ventas/`, `GET /ventas/{id}`, `POST /ventas/` | Personal del salon. El alta registra una venta asociada a un turno realizado. |

Las rutas son versionadas por el proyecto como `0.1.0`, pero actualmente no
tienen un prefijo `/api/v1`.

### Ejemplos de parametros y cuerpos

Consultar disponibilidad requiere al menos un `servicio_ids`:

```text
GET /turnos/disponibilidad?profesional_id=1&fecha=2026-10-05&servicio_ids=2&servicio_ids=4
```

Reservar un turno exige fecha y hora con zona horaria, profesional, servicios y
datos de contacto:

```json
{
	"nombre": "Sofia",
	"apellido": "Lopez",
	"telefono": "+541155550123",
	"profesional_id": 1,
	"servicio_ids": [2, 4],
	"inicio": "2026-10-05T15:00:00-03:00"
}
```

Para registrar una venta, el turno debe estar realizado y no debe tener ya otra
venta asociada:

```json
{
	"turno_id": 42,
	"chisme_detalle": "Detalle opcional"
}
```

Las respuestas y restricciones completas de cada operacion estan definidas en
los esquemas Pydantic de `app/modules/*/infrastructure/api/schemas.py` y se
publican en OpenAPI durante el desarrollo.

## Autenticacion y autorizacion

1. `POST /auth/login` envia email y clave a Supabase Auth y devuelve
	 `access_token`, `refresh_token` y `expires_in`.
2. Los clientes envian el access token como bearer token a rutas protegidas.
3. `app/shared/security.py` valida firma, emisor, audiencia y vigencia del JWT.
	 Con `ES256` obtiene la clave publica del JWKS de Supabase; con `HS256` usa
	 `SUPABASE_JWT_SECRET`.
4. Los permisos `dueno` y `vendedor` de `require_role` se consultan en la tabla
	 `perfiles`. El rol se valida en el servidor, no se debe confiar en que la
	 interfaz del cliente oculte una accion.

No hay endpoints para crear usuarios ni cambiar contrasenas en esta API. La
creacion inicial de usuarios se realiza desde Supabase Authentication y la
asignacion de roles requiere crear sus filas en `perfiles`.

## Persistencia y reglas del modelo

El esquema de PostgreSQL/Supabase esta definido en
[`../supabase/migrations.sql`](../supabase/migrations.sql). Incluye perfiles,
profesionales, clientes, servicios, descuentos, turnos, detalle de turnos,
ventas, detalle de ventas, horarios y bloqueos.

Reglas relevantes implementadas en la aplicacion y/o el esquema SQL:

- Un cliente debe tener telefono o email de contacto.
- Los servicios guardan precio y duracion; el precio/duracion se copia al
	detalle del turno para conservar lo reservado.
- Los descuentos pueden aplicarse a un servicio o como descuento interno por
	`chisme`, con porcentaje y vigencia opcional.
- La reserva comprueba profesional activo, servicios existentes, fecha futura,
	jornada, bloqueos y turnos ocupados. PostgreSQL tambien impide solapamientos
	activos del mismo profesional mediante una restriccion de exclusion.
- Los horarios pueden tener varias franjas por dia, por ejemplo para una pausa.
- La venta usa los importes reservados en el turno, admite el descuento por
	chisme configurado y no permite duplicar la venta del mismo turno.
- Clientes, servicios y profesionales se desactivan en vez de borrarse desde
	sus endpoints de gestion.
- El SQL habilita Row Level Security y define politicas para roles
	`anon`/`authenticated`; la API aplica ademas sus propios controles de acceso.

[`../supabase/seedns.sql`](../supabase/seedns.sql) contiene datos ficticios de
ejemplo: profesionales, servicios, descuentos, horarios, clientes, turnos y
ventas. Ejecutalo solo en una base de desarrollo o prueba, despues del esquema.
No crea usuarios reales de Supabase ni sus perfiles.

La aplicacion abre un pool Psycopg al iniciar y lo cierra al detenerse. El pool
actual se configura con un maximo de tres conexiones. Las transacciones se
obtienen mediante `db.transaction()`; en los casos de uso de turnos, el Unit of
Work define la unidad transaccional del flujo.

## Configuracion

La configuracion se carga desde `api/.env` o variables de entorno, usando
Pydantic Settings. Crea `api/.env` con tus propios valores; no subas secretos al
repositorio:

```dotenv
ENVIRONMENT=development
LOG_LEVEL=INFO
DATABASE_URL=postgresql://usuario:clave@host:5432/postgres
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-clave-publica
JWT_ALGORITHM=ES256
JWT_EXPIRATION_HOURS=1
ZONA_HORARIA=America/Argentina/Buenos_Aires
CORS_ORIGINS=["http://localhost:3000"]
```

`SUPABASE_JWT_SECRET` solo hace falta si el proyecto firma tokens con HS256.
Para ES256, la API busca las claves publicas en el endpoint JWKS derivado de
`SUPABASE_URL`. No compartas claves privadas, contrasenas de base de datos ni
tokens en logs o en el cliente desktop.

Los nombres de variables corresponden a los campos de `app/shared/config.py`;
Pydantic Settings acepta los nombres de campo con formato de entorno en
mayusculas.

## Preparacion y ejecucion con uv

Requisitos: Python 3.12+ y `uv` instalado. Desde esta carpeta (`api/`):

```sh
uv sync
```

Configura `api/.env`, aplica `../supabase/migrations.sql` a una instancia nueva
de Supabase/PostgreSQL y, opcionalmente, carga `../supabase/seedns.sql` en un
entorno de pruebas. Despues inicia el servidor:

```sh
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

En modo desarrollo, OpenAPI se encuentra en
[`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs). `/docs` se desactiva
cuando `ENVIRONMENT=production`; ReDoc esta desactivado. La aplicacion abre el
pool en el startup y lo cierra en el shutdown.

## Pruebas y estado del proyecto

La carpeta `api/testing/` esta vacia y `pyproject.toml` no declara actualmente
un framework de pruebas ni comandos de lint/typecheck. Se puede hacer una
comprobacion de sintaxis con:

```sh
uv run python -m compileall app
```

Eso solo valida compilacion de archivos Python; no reemplaza pruebas unitarias,
de integracion con PostgreSQL/Supabase ni pruebas de contrato HTTP.

Consideraciones para integraciones y siguientes iteraciones:

- La API no expone administracion de usuarios ni cambio de contrasenas.
- El endpoint de disponibilidad/reserva publica es anonimo; en el router hay
	un comentario que deja rate limiting y captcha como trabajo pendiente.
- La reserva publica usa nombre, apellido y telefono para crear o reutilizar
	una ficha de cliente; no requiere autenticacion.
- La autorizacion de ventas consulta `app_metadata.role`, mientras que
	`require_role` en los otros modulos protegidos consulta el rol en `perfiles`.
	Alinear ambos mecanismos antes de depender de un rol unico en todos los
	endpoints.
- Verifica que los valores de estado usados por el dominio de turnos coincidan
	con el enum `estado_turno` instalado en PostgreSQL al desplegar cambios de
	esquema.

