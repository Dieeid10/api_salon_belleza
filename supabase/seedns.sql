-- =====================================================================
-- SALON DE BELLEZA - Datos de prueba
-- Ejecutar DESPUES de salon_belleza_supabase.sql, una sola vez.
--
-- Notas:
--   * Todos los datos son ficticios (nombres, telefonos, emails, precios).
--   * Las fechas de turnos y ventas son RELATIVAS al dia en que lo ejecutes.
--   * No crea perfiles: eso requiere usuarios reales de Authentication.
--     Los profesionales quedan sin perfil_id; se vinculan despues (ver final).
--   * La fila "Descuento por chisme" (5%) ya existe por el script principal.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. PROFESIONALES (renombralos con los nombres reales)
-- ---------------------------------------------------------------------
INSERT INTO profesionales (nombre) VALUES
    ('Profesional 1'),
    ('Profesional 2');

-- ---------------------------------------------------------------------
-- 2. SERVICIOS (precios en pesos, ilustrativos)
-- ---------------------------------------------------------------------
INSERT INTO servicios (nombre_servicio, descripcion, precio, duracion_minutos) VALUES
    ('Corte de cabello',        'Corte y peinado final',                 15000,  45),
    ('Corte de cabello hombre', 'Corte clasico o degrade',               10000,  30),
    ('Brushing',                'Lavado y secado con brushing',          12000,  40),
    ('Color raiz',              'Tintura de raiz',                       35000,  90),
    ('Balayage',                'Mechas balayage con tonalizado',        80000, 180),
    ('Manicura semipermanente', 'Esmaltado semipermanente',              18000,  60),
    ('Pedicuria',               'Pedicuria completa',                    20000,  60),
    ('Perfilado de cejas',      'Diseño y perfilado',                     6000,  20),
    ('Limpieza facial',         'Limpieza profunda con hidratacion',     25000,  60),
    ('Keratina',                'Tratamiento de alisado con keratina',   60000, 120);

-- ---------------------------------------------------------------------
-- 3. DESCUENTOS POR SERVICIO
-- ---------------------------------------------------------------------
INSERT INTO descuentos (nombre, tipo, servicio_id, porcentaje, fecha_inicio, fecha_fin)
SELECT 'Promo Brushing', 'servicio', s.id, 10, NULL, NULL
FROM servicios s WHERE s.nombre_servicio = 'Brushing';

INSERT INTO descuentos (nombre, tipo, servicio_id, porcentaje, fecha_inicio, fecha_fin)
SELECT 'Promo Manicura del mes', 'servicio', s.id, 15,
       (now() AT TIME ZONE 'America/Argentina/Buenos_Aires')::date,
       (now() AT TIME ZONE 'America/Argentina/Buenos_Aires')::date + 30
FROM servicios s WHERE s.nombre_servicio = 'Manicura semipermanente';

-- ---------------------------------------------------------------------
-- 4. HORARIOS DE ATENCION (ambos profesionales)
--    Lunes a viernes 09-13 y 15-19 (pausa de mediodia). Sabado 09-13.
-- ---------------------------------------------------------------------
INSERT INTO horarios_atencion (profesional_id, dia_semana, hora_apertura, hora_cierre)
SELECT p.id, d, h.ap, h.ci
FROM profesionales p
CROSS JOIN generate_series(1, 5) AS d
CROSS JOIN (VALUES
    (TIME '09:00', TIME '13:00'),
    (TIME '15:00', TIME '19:00')
) AS h(ap, ci)
WHERE p.nombre IN ('Profesional 1', 'Profesional 2');

INSERT INTO horarios_atencion (profesional_id, dia_semana, hora_apertura, hora_cierre)
SELECT p.id, 6, TIME '09:00', TIME '13:00'
FROM profesionales p
WHERE p.nombre IN ('Profesional 1', 'Profesional 2');

-- ---------------------------------------------------------------------
-- 5. BLOQUEO DE EJEMPLO (Profesional 2 no esta 3 dias adelante, 13 a 15 hs)
-- ---------------------------------------------------------------------
INSERT INTO bloqueos (profesional_id, fecha_inicio, fecha_fin, motivo)
SELECT p.id,
       (((now() AT TIME ZONE 'America/Argentina/Buenos_Aires')::date + 3) + TIME '13:00')
            AT TIME ZONE 'America/Argentina/Buenos_Aires',
       (((now() AT TIME ZONE 'America/Argentina/Buenos_Aires')::date + 3) + TIME '15:00')
            AT TIME ZONE 'America/Argentina/Buenos_Aires',
       'Tramite personal (bloqueo de prueba)'
FROM profesionales p WHERE p.nombre = 'Profesional 2';

-- ---------------------------------------------------------------------
-- 6. CLIENTES (ficticios)
-- ---------------------------------------------------------------------
INSERT INTO clientes (nombre, apellido, telefono, email) VALUES
    ('Maria',   'Gonzalez', '11-5555-0101', 'maria.gonzalez@example.com'),
    ('Sofia',   'Rodriguez','11-5555-0102', 'sofia.rodriguez@example.com'),
    ('Carolina','Fernandez','11-5555-0103', NULL),
    ('Valeria', 'Lopez',    '11-5555-0104', 'valeria.lopez@example.com'),
    ('Julieta', 'Martinez', '11-5555-0105', 'julieta.martinez@example.com');

-- ---------------------------------------------------------------------
-- 7. TURNOS Y VENTAS DE EJEMPLO
-- ---------------------------------------------------------------------
DO $$
DECLARE
    tz      constant text := 'America/Argentina/Buenos_Aires';
    hoy     date := (now() AT TIME ZONE tz)::date;
    p1 bigint; p2 bigint;
    c1 bigint; c2 bigint; c3 bigint; c4 bigint;
    s_corte bigint; s_color bigint; s_brush bigint; s_mani bigint; s_cejas bigint;
    d_brush bigint; d_mani bigint; d_chisme bigint;
    t bigint; v bigint;
BEGIN
    SELECT id INTO p1 FROM profesionales WHERE nombre = 'Profesional 1';
    SELECT id INTO p2 FROM profesionales WHERE nombre = 'Profesional 2';

    SELECT id INTO c1 FROM clientes WHERE apellido = 'Gonzalez';
    SELECT id INTO c2 FROM clientes WHERE apellido = 'Rodriguez';
    SELECT id INTO c3 FROM clientes WHERE apellido = 'Fernandez';
    SELECT id INTO c4 FROM clientes WHERE apellido = 'Lopez';

    SELECT id INTO s_corte FROM servicios WHERE nombre_servicio = 'Corte de cabello';
    SELECT id INTO s_color FROM servicios WHERE nombre_servicio = 'Color raiz';
    SELECT id INTO s_brush FROM servicios WHERE nombre_servicio = 'Brushing';
    SELECT id INTO s_mani  FROM servicios WHERE nombre_servicio = 'Manicura semipermanente';
    SELECT id INTO s_cejas FROM servicios WHERE nombre_servicio = 'Perfilado de cejas';

    SELECT id INTO d_brush  FROM descuentos WHERE nombre = 'Promo Brushing';
    SELECT id INTO d_mani   FROM descuentos WHERE nombre = 'Promo Manicura del mes';
    SELECT id INTO d_chisme FROM descuentos WHERE tipo = 'chisme';

    -- ===== TURNOS =====

    -- Turno pasado, ya realizado (origen de la venta 1)
    INSERT INTO turnos (cliente_id, profesional_id, fecha_hora, fecha_hora_fin, estado, origen)
    VALUES (c1, p1,
            ((hoy - 2) + TIME '11:00') AT TIME ZONE tz,
            ((hoy - 2) + TIME '11:45') AT TIME ZONE tz,
            'Realizado', 'interno')
    RETURNING id INTO t;
    INSERT INTO detalle_turnos (turno_id, servicio_id, precio_lista, descuento_pct, precio_reservado)
    SELECT t, s.id, s.precio, 0, s.precio FROM servicios s WHERE s.id = s_corte;

    -- Venta 1: nace del turno realizado, sin chisme
    INSERT INTO ventas (fecha_hora, cliente_id, turno_id)
    VALUES (((hoy - 2) + TIME '12:00') AT TIME ZONE tz, c1, t)
    RETURNING id INTO v;
    INSERT INTO detalle_ventas (venta_id, servicio_id, precio_lista, descuento_pct, precio_cobrado)
    SELECT v, s.id, s.precio, 0, s.precio FROM servicios s WHERE s.id = s_corte;

    -- Manana 10:00 - Profesional 1 (corte). Confirmado.
    INSERT INTO turnos (cliente_id, profesional_id, fecha_hora, fecha_hora_fin, estado, origen)
    VALUES (c1, p1,
            ((hoy + 1) + TIME '10:00') AT TIME ZONE tz,
            ((hoy + 1) + TIME '10:45') AT TIME ZONE tz,
            'Confirmado', 'interno')
    RETURNING id INTO t;
    INSERT INTO detalle_turnos (turno_id, servicio_id, precio_lista, descuento_pct, precio_reservado)
    SELECT t, s.id, s.precio, 0, s.precio FROM servicios s WHERE s.id = s_corte;

    -- Manana 10:00 - Profesional 2 (color): mismo horario, otra profesional. Permitido.
    INSERT INTO turnos (cliente_id, profesional_id, fecha_hora, fecha_hora_fin, estado, origen)
    VALUES (c2, p2,
            ((hoy + 1) + TIME '10:00') AT TIME ZONE tz,
            ((hoy + 1) + TIME '11:30') AT TIME ZONE tz,
            'Confirmado', 'interno')
    RETURNING id INTO t;
    INSERT INTO detalle_turnos (turno_id, servicio_id, precio_lista, descuento_pct, precio_reservado)
    SELECT t, s.id, s.precio, 0, s.precio FROM servicios s WHERE s.id = s_color;

    -- Turno CANCELADO en el mismo horario que el de Profesional 1 (no bloquea: solo
    -- cuentan Pendiente y Confirmado en la restriccion anti solapamiento)
    INSERT INTO turnos (cliente_id, profesional_id, fecha_hora, fecha_hora_fin, estado, origen)
    VALUES (c4, p1,
            ((hoy + 1) + TIME '10:00') AT TIME ZONE tz,
            ((hoy + 1) + TIME '10:45') AT TIME ZONE tz,
            'Cancelado', 'online')
    RETURNING id INTO t;
    INSERT INTO detalle_turnos (turno_id, servicio_id, precio_lista, descuento_pct, precio_reservado)
    SELECT t, s.id, s.precio, 0, s.precio FROM servicios s WHERE s.id = s_corte;

    -- Manana 16:00 - Profesional 1, manicura con promo del mes (15%). Reserva online.
    INSERT INTO turnos (cliente_id, profesional_id, fecha_hora, fecha_hora_fin, estado, origen)
    VALUES (c3, p1,
            ((hoy + 1) + TIME '16:00') AT TIME ZONE tz,
            ((hoy + 1) + TIME '17:00') AT TIME ZONE tz,
            'Pendiente', 'online')
    RETURNING id INTO t;
    INSERT INTO detalle_turnos (turno_id, servicio_id, descuento_id, precio_lista, descuento_pct, precio_reservado)
    SELECT t, s.id, d_mani, s.precio, 15, ROUND(s.precio * 0.85, 2)
    FROM servicios s WHERE s.id = s_mani;

    -- Pasado manana 11:00 - Profesional 2, cejas + corte (65 min). Reserva online de invitada.
    INSERT INTO turnos (cliente_id, profesional_id, fecha_hora, fecha_hora_fin, estado, origen, observaciones)
    VALUES (c4, p2,
            ((hoy + 2) + TIME '11:00') AT TIME ZONE tz,
            ((hoy + 2) + TIME '12:05') AT TIME ZONE tz,
            'Pendiente', 'online', 'Reserva de prueba desde la web')
    RETURNING id INTO t;
    INSERT INTO detalle_turnos (turno_id, servicio_id, precio_lista, descuento_pct, precio_reservado)
    SELECT t, s.id, s.precio, 0, s.precio FROM servicios s WHERE s.id IN (s_cejas, s_corte);

    -- ===== VENTAS =====

    -- Venta 2: color + brushing (con promo 10%) y descuento por chisme del 5%.
    -- Subtotal 45.800 -> descuento chisme 2.290 -> total 43.510
    INSERT INTO ventas (fecha_hora, cliente_id, descuento_chisme_id, chisme_pct, chisme_detalle)
    VALUES (((hoy - 1) + TIME '17:30') AT TIME ZONE tz,
            c2, d_chisme, 5, 'Chisme de prueba')
    RETURNING id INTO v;
    INSERT INTO detalle_ventas (venta_id, servicio_id, precio_lista, descuento_pct, precio_cobrado)
    SELECT v, s.id, s.precio, 0, s.precio FROM servicios s WHERE s.id = s_color;
    INSERT INTO detalle_ventas (venta_id, servicio_id, descuento_id, precio_lista, descuento_pct, precio_cobrado)
    SELECT v, s.id, d_brush, s.precio, 10, ROUND(s.precio * 0.90, 2)
    FROM servicios s WHERE s.id = s_brush;

    -- Venta 3: manicura con promo del mes (15%), sin chisme
    INSERT INTO ventas (fecha_hora, cliente_id)
    VALUES (((hoy - 1) + TIME '18:15') AT TIME ZONE tz, c3)
    RETURNING id INTO v;
    INSERT INTO detalle_ventas (venta_id, servicio_id, descuento_id, precio_lista, descuento_pct, precio_cobrado)
    SELECT v, s.id, d_mani, s.precio, 15, ROUND(s.precio * 0.85, 2)
    FROM servicios s WHERE s.id = s_mani;
END $$;

-- ---------------------------------------------------------------------
-- 8. VERIFICACION (descomentar para probar)
-- ---------------------------------------------------------------------
-- Totales de ventas (la venta 2 debe dar subtotal 45800 y total 43510):
-- SELECT * FROM ventas_resumen ORDER BY id;
--
-- Franjas ocupadas de los proximos 7 dias (lo que veria la web publica):
-- SELECT * FROM franjas_ocupadas(now(), now() + interval '7 days') ORDER BY inicio;
--
-- Probar la restriccion anti doble reserva: debe FALLAR con error de
-- "turnos_sin_solapamiento" (mismo profesional, horario solapado con un turno activo):
-- INSERT INTO turnos (cliente_id, profesional_id, fecha_hora, fecha_hora_fin, estado)
-- SELECT cliente_id, profesional_id, fecha_hora + interval '15 minutes',
--        fecha_hora_fin + interval '15 minutes', 'Pendiente'
-- FROM turnos WHERE estado = 'Confirmado' LIMIT 1;

-- ---------------------------------------------------------------------
-- 9. VINCULAR PROFESIONALES CON SUS LOGINS (cuando crees los usuarios)
-- ---------------------------------------------------------------------
-- INSERT INTO perfiles (id, nombre, rol) VALUES
--   ('UUID-DE-LA-DUENA',    'Nombre duena',    'dueno'),
--   ('UUID-DE-LA-EMPLEADA', 'Nombre empleada', 'vendedor');
--
-- UPDATE profesionales SET nombre = 'Nombre duena',    perfil_id = 'UUID-DE-LA-DUENA'    WHERE nombre = 'Profesional 1';
-- UPDATE profesionales SET nombre = 'Nombre empleada', perfil_id = 'UUID-DE-LA-EMPLEADA' WHERE nombre = 'Profesional 2';

-- ---------------------------------------------------------------------
-- 10. LIMPIAR TODO (descomentar solo si queres borrar los datos de prueba)
--     Ojo: tambien borra la fila del descuento por chisme; se repone abajo.
-- ---------------------------------------------------------------------
-- TRUNCATE detalle_ventas, ventas, detalle_turnos, turnos, bloqueos,
--          horarios_atencion, descuentos, servicios, clientes, profesionales
--          RESTART IDENTITY CASCADE;
-- INSERT INTO descuentos (nombre, tipo, porcentaje) VALUES ('Descuento por chisme', 'chisme', 5);