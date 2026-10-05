# Base de datos Supabase

Este directorio contiene el esquema PostgreSQL del salon, los datos ficticios
para desarrollo y una migracion puntual para bases que ya existian.

| Archivo | Uso |
| --- | --- |
| `migrations.sql` | Esquema completo para inicializar una base vacia. |
| `seedns.sql` | Datos de prueba. Ejecutar despues del esquema y solo una vez por base de desarrollo. |
| `add_estado_ausente.sql` | Agrega el estado `Ausente` a una base que ya tenia creado `estado_turno`. |

La API se conecta a PostgreSQL usando `DATABASE_URL`; Supabase Auth administra
las cuentas y emite los JWT. El cliente desktop no se conecta directamente a la
base.

## Inicializar

Para un proyecto/base vacia, ejecutar `migrations.sql` completo desde el SQL
Editor de Supabase. El script crea la extension `btree_gist`, los tipos, tablas,
indices, vistas, funciones, politicas RLS y una fila inicial de descuento por
chisme.

Despues:

1. Crear las cuentas del personal en Supabase Authentication.
2. Copiar los UUID de las cuentas y crear sus filas en `perfiles` con el rol
   `dueno` o `vendedor`.
3. Crear o vincular sus filas en `profesionales` y cargar sus horarios en
   `horarios_atencion`.
4. En desarrollo, ejecutar `seedns.sql` una sola vez para insertar datos
   ficticios. El seed no crea cuentas de Auth ni perfiles reales.

No vuelvas a ejecutar el esquema completo sobre una base ya inicializada: usa
migraciones puntuales para cambios. Para una base existente, `add_estado_ausente.sql`
debe ejecutarse una vez en el SQL Editor para que PostgreSQL acepte ese estado.

## Tipos

| Tipo | Valores |
| --- | --- |
| `rol_usuario` | `dueno`, `vendedor` |
| `estado_turno` | `Pendiente`, `Confirmado`, `Realizado`, `Cancelado`, `Ausente` |
| `origen_turno` | `interno`, `online` |
| `tipo_descuento` | `servicio`, `chisme` |

Los enums de PostgreSQL distinguen mayusculas y minusculas. El dominio Python
usa valores como `pendiente` y `completado`; el adaptador de persistencia los
traduce a `Pendiente` y `Realizado`. Para ver los valores instalados en una base:

```sql
SELECT unnest(enum_range(NULL::estado_turno));
```

## Tablas

### Personal y catalogos

- `perfiles`: `id` (PK y FK a `auth.users`, cascada al borrar), `nombre`, `rol`
  y `fecha_creacion`. El rol que autoriza la API se consulta aqui.
- `profesionales`: `id` (PK), `nombre`, `perfil_id` (FK unico y opcional a
  `perfiles`, se vuelve NULL al borrar el perfil) y `activo`. Varios turnos
  pueden pertenecer a una profesional.
- `clientes`: `id` (PK), `user_id` (FK unico y opcional a `auth.users`),
  `nombre`, `apellido`, `telefono`, `email`, `activo` y `fecha_creacion`.
  Requiere telefono o email; un indice unico sobre `lower(email)` evita emails
  repetidos sin distinguir mayusculas. `user_id` se vuelve NULL al borrar Auth.
- `servicios`: `id` (PK), `nombre_servicio`, `descripcion`, `precio`,
  `duracion_minutos`, `visible_online` y `activo`. Precio no negativo y
  duracion positiva.
- `descuentos`: `id` (PK), `nombre`, `tipo`, `servicio_id` (FK opcional),
  `porcentaje`, `fecha_inicio`, `fecha_fin` y `activo`. El porcentaje debe ser
  mayor que cero y hasta 100; el tipo servicio exige `servicio_id`, mientras
  que chisme no lo permite. La vigencia final no puede preceder a la inicial.
  Un indice parcial permite una sola fila de tipo `chisme`.

### Turnos y agenda

- `turnos`: `id` (PK), `cliente_id` (FK, no permite borrar el cliente),
  `profesional_id` (FK, no permite borrar la profesional), `fecha_hora`,
  `fecha_hora_fin`, `estado`, `observaciones`, `origen`, `token_cancelacion`
  (unico) y `fecha_creacion`. Exige fin posterior al inicio. No guarda un
  total: se calcula sumando sus detalles. Tiene indices por cliente, profesional
  y fecha.
- `detalle_turnos`: `id` (PK), `turno_id` (FK, cascada al borrar turno),
  `servicio_id` (FK, no permite borrar servicio), `descuento_id` (FK opcional,
  se vuelve NULL al borrar descuento), `precio_lista`, `descuento_pct` y
  `precio_reservado`. Guarda el snapshot economico de cada servicio reservado.
- `horarios_atencion`: `id` (PK), `profesional_id` (FK, cascada al borrar
  profesional), `dia_semana`, `hora_apertura`, `hora_cierre` y `activo`. Dia de
  0 (domingo) a 6 (sabado); fin debe ser posterior al inicio. Varias filas del
  mismo dia representan pausas, por ejemplo manana y tarde.
- `bloqueos`: `id` (PK), `profesional_id` (FK opcional, cascada al borrar la
  profesional), `fecha_inicio`, `fecha_fin` y `motivo`. Si no hay profesional,
  el bloqueo corresponde a todo el salon; fin debe ser posterior al inicio.

La tabla `turnos` tiene una restriccion de exclusion: impide que una misma
profesional tenga reservas `Pendiente` o `Confirmado` que se solapen. Turnos de
profesionales distintas pueden coincidir.

### Ventas

- `ventas`: `id` (PK), `fecha_hora`, `cliente_id` (FK opcional, se vuelve NULL
  al borrar cliente), `empleado_id` (FK opcional a `perfiles`), `turno_id` (FK
  opcional), `descuento_chisme_id` (FK opcional), `chisme_pct` y
  `chisme_detalle`. El porcentaje va de 0 a 100.
- `detalle_ventas`: `id` (PK), `venta_id` (FK, cascada al borrar venta),
  `servicio_id` y `descuento_id` (FK opcionales que se vuelven NULL al borrar
  el catalogo correspondiente), `precio_lista`, `descuento_pct` y
  `precio_cobrado`. Conserva el snapshot de los importes cobrados.

La vista `ventas_resumen` calcula subtotal, descuento por chisme y total a
partir de `detalle_ventas`. La aplicacion evita registrar dos ventas para el
mismo turno; la base no define un indice unico sobre `ventas.turno_id`.

### Columnas de `ventas_resumen`

La vista expone `id`, `fecha_hora`, `cliente_id`, `empleado_id`, `turno_id`,
`subtotal`, `chisme_pct`, `descuento_chisme` y `total`. Se define con
`security_invoker`, por lo que respeta los permisos/RLS del usuario que consulta.

## De donde salen los horarios

La disponibilidad no se almacena como una lista de horas. Se calcula a partir
de las franjas de `horarios_atencion`, la duracion de los servicios activos en
`servicios` y los intervalos ocupados en `turnos`. Se ofrecen inicios cada 15
minutos que entren completos en una franja, sean futuros y no se solapen con
reservas activas.

Este query muestra los dias y franjas activos de cada profesional; una pausa
aparece como varias filas:

```sql
SELECT
    p.id AS profesional_id,
    p.nombre AS profesional,
    CASE h.dia_semana
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miercoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sabado'
    END AS dia,
    h.hora_apertura,
    h.hora_cierre
FROM horarios_atencion AS h
JOIN profesionales AS p ON p.id = h.profesional_id
WHERE h.activo = TRUE
ORDER BY p.id, h.dia_semana, h.hora_apertura;
```

La funcion SQL `franjas_ocupadas(desde, hasta)` combina turnos activos y filas
de `bloqueos`. Sin embargo, el caso de uso actual de disponibilidad de la API
consulta directamente `turnos` y no invoca esa funcion; por eso los bloqueos
guardados no se descuentan actualmente al ofrecer horarios desde la API.

## Vistas y funciones

- `ventas_resumen`: entrega ventas con subtotal, importe del descuento por
  chisme y total.
- `es_personal()`: indica si el usuario autenticado tiene perfil del salon.
- `es_dueno()`: comprueba si el perfil autenticado tiene rol `dueno`.
- `franjas_ocupadas(desde, hasta)`: devuelve intervalos de turnos activos y
  bloqueos, sin datos de clientes; se concede a `anon` y `authenticated`.
- `vincular_cliente_actual()`: vincula la ficha de cliente cuyo email coincide
  con el email verificado del usuario autenticado.

## Seguridad y RLS

RLS esta habilitado en las tablas del esquema. Las politicas principales son:

- `dueno` y `vendedor` pueden gestionar clientes, servicios, horarios, bloqueos
  y turnos. La administracion de profesionales y descuentos requiere `dueno`.
  Las fichas de clientes invitadas no se exponen directamente al rol anonimo.
- Una clienta autenticada puede leer su perfil de cliente y sus turnos/detalles.
- Usuarios anonimos pueden leer profesionales activos (solo id/nombre),
  servicios activos y visibles, descuentos de servicio vigentes y horarios
  activos.
- El descuento por chisme es interno. La gestion de descuentos y de perfiles
  requiere rol `dueno`.
- Ventas y detalles son visibles para el personal; solo la dueña puede
  eliminarlos.

La API tambien verifica los JWT de Supabase y consulta el rol en `perfiles`.
Las politicas de RLS y las autorizaciones de la API son capas distintas; no
confiar solamente en que la interfaz desktop oculte controles.

## Consultas utiles

Ver franjas activas de un profesional para un dia. En el ejemplo, el ID es 1 y
el dia 6 corresponde al sabado; reemplazalos por los valores que quieras:

```sql
SELECT hora_apertura, hora_cierre
FROM horarios_atencion
WHERE profesional_id = 1
  AND dia_semana = 6
  AND activo = TRUE
ORDER BY hora_apertura;
```

Ver ventas calculadas:

```sql
SELECT * FROM ventas_resumen ORDER BY fecha_hora DESC;
```

Ver bloqueos:

```sql
SELECT profesional_id, fecha_inicio, fecha_fin, motivo
FROM bloqueos
ORDER BY fecha_inicio;
```

## Archivos relacionados

- Esquema: [migrations.sql](migrations.sql)
- Datos de prueba: [seedns.sql](seedns.sql)
- Migracion para bases existentes: [add_estado_ausente.sql](add_estado_ausente.sql)
- Conexion PostgreSQL de la API: `api/app/shared/infrastructure/db/database.py`
- Disponibilidad de turnos: `api/app/modules/turnos/application/use_cases/consultar_disponibilidad.py`