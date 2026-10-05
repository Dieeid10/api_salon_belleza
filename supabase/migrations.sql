-- =====================================================================
-- SALON DE BELLEZA - Esquema v2 PostgreSQL para Supabase
-- Ejecutar completo en: Supabase > SQL Editor (en un proyecto vacio)
--
-- Novedades v2:
--   * 2 profesionales trabajando en paralelo (tabla profesionales)
--   * Reservas hibridas: invitada (via servidor) o clienta con Google
--   * Descuentos por servicio (tabla descuentos)
--   * Descuento por chisme (5%, configurable)
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. EXTENSIONES Y TIPOS
-- ---------------------------------------------------------------------
-- btree_gist permite combinar "= profesional" con "solapamiento de rangos"
CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA extensions;

CREATE TYPE rol_usuario    AS ENUM ('dueno', 'vendedor');
CREATE TYPE estado_turno   AS ENUM ('Pendiente', 'Confirmado', 'Realizado', 'Cancelado', 'Ausente');
CREATE TYPE origen_turno   AS ENUM ('interno', 'online');
CREATE TYPE tipo_descuento AS ENUM ('servicio', 'chisme');

-- ---------------------------------------------------------------------
-- 1. PERSONAL
-- ---------------------------------------------------------------------

-- Perfiles: reemplaza a "usuarios". El login lo maneja Supabase Auth (auth.users).
-- El rol vive aca y solo lo modifica la duena.
CREATE TABLE perfiles (
    id             uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nombre         varchar(50) NOT NULL,
    rol            rol_usuario NOT NULL,
    fecha_creacion timestamptz NOT NULL DEFAULT now()
);

-- Profesionales: quienes atienden turnos (la duena y la empleada).
-- perfil_id los vincula con su login (opcional).
CREATE TABLE profesionales (
    id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre    varchar(100) NOT NULL,
    perfil_id uuid UNIQUE REFERENCES perfiles(id) ON DELETE SET NULL,
    activo    boolean NOT NULL DEFAULT true
);

-- ---------------------------------------------------------------------
-- 2. CLIENTES Y SERVICIOS
-- ---------------------------------------------------------------------

-- Clientes: user_id es NULL para invitadas, y se completa si luego entran con Google.
CREATE TABLE clientes (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id        uuid UNIQUE REFERENCES auth.users(id) ON DELETE SET NULL,
    nombre         varchar(100) NOT NULL,
    apellido       varchar(100) NOT NULL,
    telefono       varchar(50),
    email          varchar(100),
    activo         boolean NOT NULL DEFAULT true,
    fecha_creacion timestamptz NOT NULL DEFAULT now(),
    -- Para poder contactarla hace falta al menos un medio
    CONSTRAINT cliente_con_contacto CHECK (telefono IS NOT NULL OR email IS NOT NULL)
);
CREATE UNIQUE INDEX uq_clientes_email ON clientes (lower(email));
CREATE INDEX idx_clientes_telefono ON clientes (telefono);

CREATE TABLE servicios (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_servicio  varchar(100) NOT NULL,
    descripcion      varchar(255),
    precio           numeric(10,2) NOT NULL CHECK (precio >= 0),
    duracion_minutos integer NOT NULL DEFAULT 60 CHECK (duracion_minutos > 0),
    visible_online   boolean NOT NULL DEFAULT true,
    activo           boolean NOT NULL DEFAULT true
);

-- ---------------------------------------------------------------------
-- 3. DESCUENTOS
-- ---------------------------------------------------------------------
-- tipo 'servicio': promo sobre un servicio puntual (con vigencia opcional)
-- tipo 'chisme'  : descuento global que se aplica a la venta (solo 1 fila)
CREATE TABLE descuentos (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre       varchar(100) NOT NULL,
    tipo         tipo_descuento NOT NULL,
    servicio_id  bigint REFERENCES servicios(id) ON DELETE CASCADE,
    porcentaje   numeric(5,2) NOT NULL CHECK (porcentaje > 0 AND porcentaje <= 100),
    fecha_inicio date,
    fecha_fin    date,
    activo       boolean NOT NULL DEFAULT true,
    CONSTRAINT descuento_vigencia_valida CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio),
    CONSTRAINT descuento_tipo_servicio CHECK (
        (tipo = 'servicio' AND servicio_id IS NOT NULL) OR
        (tipo = 'chisme'   AND servicio_id IS NULL)
    )
);
CREATE INDEX idx_descuentos_servicio ON descuentos (servicio_id);
-- Solo puede existir una configuracion de descuento por chisme
CREATE UNIQUE INDEX uq_descuento_chisme ON descuentos (tipo) WHERE tipo = 'chisme';

INSERT INTO descuentos (nombre, tipo, porcentaje)
VALUES ('Descuento por chisme', 'chisme', 5);

-- ---------------------------------------------------------------------
-- 4. TURNOS
-- ---------------------------------------------------------------------
CREATE TABLE turnos (
    id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id        bigint NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
    profesional_id    bigint NOT NULL REFERENCES profesionales(id) ON DELETE RESTRICT,
    fecha_hora        timestamptz NOT NULL,
    fecha_hora_fin    timestamptz NOT NULL,
    estado            estado_turno NOT NULL DEFAULT 'Pendiente',
    observaciones     varchar(250),
    origen            origen_turno NOT NULL DEFAULT 'interno',
    token_cancelacion uuid NOT NULL DEFAULT gen_random_uuid() UNIQUE,
    fecha_creacion    timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT turnos_fin_mayor_inicio CHECK (fecha_hora_fin > fecha_hora),
    -- Una misma profesional no puede tener dos turnos activos solapados.
    -- Dos profesionales distintas si pueden atender en el mismo horario.
    CONSTRAINT turnos_sin_solapamiento
        EXCLUDE USING gist (
            profesional_id WITH =,
            tstzrange(fecha_hora, fecha_hora_fin) WITH &&
        ) WHERE (estado IN ('Pendiente', 'Confirmado'))
);
CREATE INDEX idx_turnos_cliente     ON turnos (cliente_id);
CREATE INDEX idx_turnos_profesional ON turnos (profesional_id, fecha_hora);
CREATE INDEX idx_turnos_fecha       ON turnos (fecha_hora, fecha_hora_fin, estado);

-- precio_lista = precio del servicio al reservar
-- descuento_pct = % de la promo aplicada (0 si no hubo)
-- precio_reservado = precio final con descuento
CREATE TABLE detalle_turnos (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    turno_id         bigint NOT NULL REFERENCES turnos(id) ON DELETE CASCADE,
    servicio_id      bigint NOT NULL REFERENCES servicios(id) ON DELETE RESTRICT,
    descuento_id     bigint REFERENCES descuentos(id) ON DELETE SET NULL,
    precio_lista     numeric(10,2) NOT NULL CHECK (precio_lista >= 0),
    descuento_pct    numeric(5,2)  NOT NULL DEFAULT 0 CHECK (descuento_pct >= 0 AND descuento_pct <= 100),
    precio_reservado numeric(10,2) NOT NULL CHECK (precio_reservado >= 0)
);
CREATE INDEX idx_detalle_turnos_turno ON detalle_turnos (turno_id);

-- ---------------------------------------------------------------------
-- 5. VENTAS
-- ---------------------------------------------------------------------
-- El descuento por chisme se guarda en la venta como snapshot:
--   chisme_pct     = % aplicado (0 si no hubo chisme)
--   chisme_detalle = de que se trataba el chisme (uso interno, opcional)
CREATE TABLE ventas (
    id                   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha_hora           timestamptz NOT NULL DEFAULT now(),
    cliente_id           bigint REFERENCES clientes(id) ON DELETE SET NULL,
    empleado_id          uuid REFERENCES perfiles(id) ON DELETE SET NULL,
    turno_id             bigint REFERENCES turnos(id) ON DELETE SET NULL,
    descuento_chisme_id  bigint REFERENCES descuentos(id) ON DELETE SET NULL,
    chisme_pct           numeric(5,2) NOT NULL DEFAULT 0 CHECK (chisme_pct >= 0 AND chisme_pct <= 100),
    chisme_detalle       varchar(250)
);
CREATE INDEX idx_ventas_cliente ON ventas (cliente_id);
CREATE INDEX idx_ventas_fecha   ON ventas (fecha_hora);

CREATE TABLE detalle_ventas (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venta_id       bigint NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    servicio_id    bigint REFERENCES servicios(id) ON DELETE SET NULL,
    descuento_id   bigint REFERENCES descuentos(id) ON DELETE SET NULL,
    precio_lista   numeric(10,2) CHECK (precio_lista >= 0),
    descuento_pct  numeric(5,2) NOT NULL DEFAULT 0 CHECK (descuento_pct >= 0 AND descuento_pct <= 100),
    precio_cobrado numeric(10,2) NOT NULL CHECK (precio_cobrado >= 0)
);
CREATE INDEX idx_detalle_ventas_venta ON detalle_ventas (venta_id);

-- Resumen con totales: subtotal (ya con promos por servicio),
-- descuento por chisme aplicado sobre el subtotal, y total final.
-- security_invoker hace que respete las politicas RLS de quien consulta.
CREATE VIEW ventas_resumen WITH (security_invoker = true) AS
SELECT
    v.id,
    v.fecha_hora,
    v.cliente_id,
    v.empleado_id,
    v.turno_id,
    COALESCE(SUM(d.precio_cobrado), 0)                                        AS subtotal,
    v.chisme_pct,
    ROUND(COALESCE(SUM(d.precio_cobrado), 0) * v.chisme_pct / 100, 2)         AS descuento_chisme,
    ROUND(COALESCE(SUM(d.precio_cobrado), 0) * (1 - v.chisme_pct / 100), 2)   AS total
FROM ventas v
LEFT JOIN detalle_ventas d ON d.venta_id = v.id
GROUP BY v.id;

-- ---------------------------------------------------------------------
-- 6. AGENDA
-- ---------------------------------------------------------------------

-- Horarios de atencion por profesional: 0 = domingo ... 6 = sabado.
-- Varias filas por dia permiten pausa de mediodia.
CREATE TABLE horarios_atencion (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    profesional_id bigint NOT NULL REFERENCES profesionales(id) ON DELETE CASCADE,
    dia_semana     smallint NOT NULL CHECK (dia_semana BETWEEN 0 AND 6),
    hora_apertura  time NOT NULL,
    hora_cierre    time NOT NULL,
    activo         boolean NOT NULL DEFAULT true,
    CONSTRAINT horario_valido CHECK (hora_cierre > hora_apertura)
);
CREATE INDEX idx_horarios_profesional ON horarios_atencion (profesional_id, dia_semana);

-- Feriados, vacaciones, bloqueos. profesional_id NULL = bloquea a todo el salon.
CREATE TABLE bloqueos (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    profesional_id bigint REFERENCES profesionales(id) ON DELETE CASCADE,
    fecha_inicio   timestamptz NOT NULL,
    fecha_fin      timestamptz NOT NULL,
    motivo         varchar(150),
    CONSTRAINT bloqueo_valido CHECK (fecha_fin > fecha_inicio)
);

-- ---------------------------------------------------------------------
-- 7. FUNCIONES
-- ---------------------------------------------------------------------

-- Es personal del salon (duena o vendedor)?
CREATE OR REPLACE FUNCTION es_personal()
RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = ''
AS $$
    SELECT EXISTS (SELECT 1 FROM public.perfiles WHERE id = (SELECT auth.uid()));
$$;

-- Es la duena?
CREATE OR REPLACE FUNCTION es_dueno()
RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = ''
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.perfiles
        WHERE id = (SELECT auth.uid()) AND rol = 'dueno'
    );
$$;

-- Franjas ocupadas por profesional (turnos activos + bloqueos), para calcular
-- disponibilidad. Devuelve SOLO rangos, nunca datos de clientes. Es publica.
-- profesional_id NULL en el resultado = bloqueo que afecta a todo el salon.
CREATE OR REPLACE FUNCTION franjas_ocupadas(desde timestamptz, hasta timestamptz)
RETURNS TABLE (profesional_id bigint, inicio timestamptz, fin timestamptz)
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = ''
AS $$
    SELECT t.profesional_id, t.fecha_hora, t.fecha_hora_fin
    FROM public.turnos t
    WHERE t.estado IN ('Pendiente', 'Confirmado')
      AND t.fecha_hora < hasta AND t.fecha_hora_fin > desde
    UNION ALL
    SELECT b.profesional_id, b.fecha_inicio, b.fecha_fin
    FROM public.bloqueos b
    WHERE b.fecha_inicio < hasta AND b.fecha_fin > desde;
$$;

-- Vincula la ficha de cliente (creada como invitada) con la cuenta de Google
-- de la persona que acaba de entrar, si el email coincide y esta verificado.
-- Llamarla desde Next tras el login: supabase.rpc('vincular_cliente_actual')
CREATE OR REPLACE FUNCTION vincular_cliente_actual()
RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    v_uid   uuid := (SELECT auth.uid());
    v_email text;
    v_id    bigint;
BEGIN
    IF v_uid IS NULL THEN
        RETURN NULL;
    END IF;

    SELECT lower(email) INTO v_email
    FROM auth.users
    WHERE id = v_uid AND email_confirmed_at IS NOT NULL;

    IF v_email IS NULL THEN
        RETURN NULL;
    END IF;

    -- Si ya tiene una ficha vinculada, devolverla
    SELECT id INTO v_id FROM public.clientes WHERE user_id = v_uid;
    IF v_id IS NOT NULL THEN
        RETURN v_id;
    END IF;

    UPDATE public.clientes
       SET user_id = v_uid
     WHERE user_id IS NULL AND lower(email) = v_email
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;

-- Permisos de ejecucion
REVOKE EXECUTE ON FUNCTION es_personal()             FROM PUBLIC, anon;
REVOKE EXECUTE ON FUNCTION es_dueno()                FROM PUBLIC, anon;
REVOKE EXECUTE ON FUNCTION vincular_cliente_actual() FROM PUBLIC, anon;
GRANT  EXECUTE ON FUNCTION es_personal()             TO authenticated;
GRANT  EXECUTE ON FUNCTION es_dueno()                TO authenticated;
GRANT  EXECUTE ON FUNCTION vincular_cliente_actual() TO authenticated;
GRANT  EXECUTE ON FUNCTION franjas_ocupadas(timestamptz, timestamptz) TO anon, authenticated;

-- ---------------------------------------------------------------------
-- 8. ROW LEVEL SECURITY
-- ---------------------------------------------------------------------
ALTER TABLE perfiles          ENABLE ROW LEVEL SECURITY;
ALTER TABLE profesionales     ENABLE ROW LEVEL SECURITY;
ALTER TABLE clientes          ENABLE ROW LEVEL SECURITY;
ALTER TABLE servicios         ENABLE ROW LEVEL SECURITY;
ALTER TABLE descuentos        ENABLE ROW LEVEL SECURITY;
ALTER TABLE turnos            ENABLE ROW LEVEL SECURITY;
ALTER TABLE detalle_turnos    ENABLE ROW LEVEL SECURITY;
ALTER TABLE ventas            ENABLE ROW LEVEL SECURITY;
ALTER TABLE detalle_ventas    ENABLE ROW LEVEL SECURITY;
ALTER TABLE horarios_atencion ENABLE ROW LEVEL SECURITY;
ALTER TABLE bloqueos          ENABLE ROW LEVEL SECURITY;

-- perfiles: cada uno ve el suyo, el personal ve todos, solo la duena modifica
CREATE POLICY perfiles_select ON perfiles FOR SELECT TO authenticated
    USING (id = (SELECT auth.uid()) OR es_personal());
CREATE POLICY perfiles_insert ON perfiles FOR INSERT TO authenticated
    WITH CHECK (es_dueno());
CREATE POLICY perfiles_update ON perfiles FOR UPDATE TO authenticated
    USING (es_dueno()) WITH CHECK (es_dueno());
CREATE POLICY perfiles_delete ON perfiles FOR DELETE TO authenticated
    USING (es_dueno());

-- profesionales: el publico ve las activas (solo id y nombre, ver GRANT abajo)
CREATE POLICY profesionales_publico ON profesionales FOR SELECT TO anon, authenticated
    USING (activo);
CREATE POLICY profesionales_personal_select ON profesionales FOR SELECT TO authenticated
    USING (es_personal());
CREATE POLICY profesionales_dueno ON profesionales FOR ALL TO authenticated
    USING (es_dueno()) WITH CHECK (es_dueno());

REVOKE ALL ON profesionales FROM anon;
GRANT SELECT (id, nombre) ON profesionales TO anon;

-- clientes: personal gestiona todo; una clienta logueada ve solo su ficha.
-- Las invitadas NO tienen acceso directo: se crean desde el servidor (service_role).
CREATE POLICY clientes_personal ON clientes FOR ALL TO authenticated
    USING (es_personal()) WITH CHECK (es_personal());
CREATE POLICY clientes_propio ON clientes FOR SELECT TO authenticated
    USING (user_id = (SELECT auth.uid()));

-- servicios: el publico ve los activos y visibles online; personal gestiona todo
CREATE POLICY servicios_publico ON servicios FOR SELECT TO anon, authenticated
    USING (visible_online AND activo);
CREATE POLICY servicios_personal ON servicios FOR ALL TO authenticated
    USING (es_personal()) WITH CHECK (es_personal());

-- descuentos: el publico ve solo promos vigentes por servicio (hora Argentina).
-- El descuento por chisme es interno y solo lo ve el personal.
CREATE POLICY descuentos_publico ON descuentos FOR SELECT TO anon, authenticated
    USING (
        tipo = 'servicio' AND activo
        AND (fecha_inicio IS NULL OR fecha_inicio <= (now() AT TIME ZONE 'America/Argentina/Buenos_Aires')::date)
        AND (fecha_fin    IS NULL OR fecha_fin    >= (now() AT TIME ZONE 'America/Argentina/Buenos_Aires')::date)
    );
CREATE POLICY descuentos_personal_select ON descuentos FOR SELECT TO authenticated
    USING (es_personal());
CREATE POLICY descuentos_dueno ON descuentos FOR ALL TO authenticated
    USING (es_dueno()) WITH CHECK (es_dueno());

-- horarios_atencion: lectura publica, gestion del personal
CREATE POLICY horarios_publico ON horarios_atencion FOR SELECT TO anon, authenticated
    USING (activo);
CREATE POLICY horarios_personal ON horarios_atencion FOR ALL TO authenticated
    USING (es_personal()) WITH CHECK (es_personal());

-- bloqueos: solo personal (el publico los ve como franjas via franjas_ocupadas)
CREATE POLICY bloqueos_personal ON bloqueos FOR ALL TO authenticated
    USING (es_personal()) WITH CHECK (es_personal());

-- turnos: personal gestiona todo; la clienta ve solo los suyos
CREATE POLICY turnos_personal ON turnos FOR ALL TO authenticated
    USING (es_personal()) WITH CHECK (es_personal());
CREATE POLICY turnos_propios ON turnos FOR SELECT TO authenticated
    USING (EXISTS (
        SELECT 1 FROM clientes c
        WHERE c.id = turnos.cliente_id AND c.user_id = (SELECT auth.uid())
    ));

CREATE POLICY detalle_turnos_personal ON detalle_turnos FOR ALL TO authenticated
    USING (es_personal()) WITH CHECK (es_personal());
CREATE POLICY detalle_turnos_propios ON detalle_turnos FOR SELECT TO authenticated
    USING (EXISTS (
        SELECT 1 FROM turnos t
        JOIN clientes c ON c.id = t.cliente_id
        WHERE t.id = detalle_turnos.turno_id AND c.user_id = (SELECT auth.uid())
    ));

-- ventas: solo personal; borrar solo la duena
CREATE POLICY ventas_select ON ventas FOR SELECT TO authenticated USING (es_personal());
CREATE POLICY ventas_insert ON ventas FOR INSERT TO authenticated WITH CHECK (es_personal());
CREATE POLICY ventas_update ON ventas FOR UPDATE TO authenticated
    USING (es_personal()) WITH CHECK (es_personal());
CREATE POLICY ventas_delete ON ventas FOR DELETE TO authenticated USING (es_dueno());

CREATE POLICY detalle_ventas_select ON detalle_ventas FOR SELECT TO authenticated USING (es_personal());
CREATE POLICY detalle_ventas_insert ON detalle_ventas FOR INSERT TO authenticated WITH CHECK (es_personal());
CREATE POLICY detalle_ventas_update ON detalle_ventas FOR UPDATE TO authenticated
    USING (es_personal()) WITH CHECK (es_personal());
CREATE POLICY detalle_ventas_delete ON detalle_ventas FOR DELETE TO authenticated USING (es_dueno());

-- ---------------------------------------------------------------------
-- 9. PUESTA EN MARCHA
-- ---------------------------------------------------------------------
-- 1) Crea a la duena y a la empleada en Authentication > Users
--    (o hacelas entrar una vez con Google).
-- 2) Copia sus UUID y ejecuta (descomentando y completando):
--
-- INSERT INTO perfiles (id, nombre, rol) VALUES
--   ('UUID-DE-LA-DUENA',    'Nombre duena',    'dueno'),
--   ('UUID-DE-LA-EMPLEADA', 'Nombre empleada', 'vendedor');
--
-- INSERT INTO profesionales (nombre, perfil_id) VALUES
--   ('Nombre duena',    'UUID-DE-LA-DUENA'),
--   ('Nombre empleada', 'UUID-DE-LA-EMPLEADA');
--
-- 3) Carga horarios_atencion para cada profesional (obligatorio: sin horarios
--    no hay turnos disponibles online).