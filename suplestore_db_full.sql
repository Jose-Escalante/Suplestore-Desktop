-- ============================================================================
-- SCRIPT DE INICIALIZACION: Base de Datos Suplestore Tachira
-- Descripcion: Creacion de la BD `suplestore_db` con su esquema completo
--              (tablas y vistas) y datos iniciales minimos.
--              Refleja EXACTAMENTE el esquema en produccion del sistema.
-- Compatibilidad: MySQL 8.0+ (probado en 9.x)
-- Uso:
--   > mysql -u root -p < suplestore_db_full.sql
--   o importarlo desde MySQL Workbench / phpMyAdmin.
--
-- NOTAS IMPORTANTES:
--   - La aplicacion usa consultas SQL directas desde Python y no requiere
--     procedimientos almacenados ni funciones.
--   - Las credenciales de conexion de la app se configuran en un archivo
--     `.env` local (no incluido en el repositorio).
--   - NO ejecutar este script sobre una base de datos existente con datos:
--     las tablas usan IF NOT EXISTS y no borran nada, pero una BD ya creada
--     con diferencias quedaria desactualizada.
-- ============================================================================

-- ============================================================================
-- 1. CREACION DE LA BASE DE DATOS
-- ============================================================================
CREATE DATABASE IF NOT EXISTS `suplestore_db`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_spanish_ci;

USE `suplestore_db`;

-- ============================================================================
-- 2. TABLAS (esquema identico al de produccion)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 2.1. usuarios: credenciales, rol y seguridad de cada usuario del sistema.
--      cambio_obligatorio fuerza el cambio de clave en el proximo login.
--      intentos_fallidos / bloqueado_hasta implementan el bloqueo temporal
--      tras 5 intentos fallidos (5 minutos).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario`         INT          NOT NULL AUTO_INCREMENT,
  `usuario`            VARCHAR(50)  COLLATE utf8mb4_spanish_ci NOT NULL,
  `contrasena`         VARCHAR(255) COLLATE utf8mb4_spanish_ci NOT NULL,
  `cambio_obligatorio` TINYINT(1)   NOT NULL DEFAULT '0',
  `intentos_fallidos`  INT          NOT NULL DEFAULT '0',
  `bloqueado_hasta`    DATETIME     DEFAULT NULL,
  `rol`                ENUM('Administrador','Vendedor') COLLATE utf8mb4_spanish_ci NOT NULL DEFAULT 'Vendedor',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `usuario` (`usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.2. permisos_usuario: permisos por modulo para cada usuario (1=acceso).
--      Se eliminan en cascada junto con el usuario.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `permisos_usuario` (
  `id_permiso`        INT        NOT NULL AUTO_INCREMENT,
  `id_usuario`        INT        NOT NULL,
  `modulo_inventario` TINYINT(1) DEFAULT '0',
  `modulo_clientes`   TINYINT(1) DEFAULT '0',
  `modulo_ventas`     TINYINT(1) DEFAULT '0',
  `modulo_categorias` TINYINT(1) DEFAULT '0',
  `modulo_usuarios`   TINYINT(1) DEFAULT '0',
  `modulo_historial`  TINYINT(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_permiso`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `permisos_usuario_ibfk_1` FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.3. categorias: clasificacion de productos
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `categorias` (
  `id_categoria`     INT          NOT NULL AUTO_INCREMENT,
  `nombre_categoria` VARCHAR(100) COLLATE utf8mb4_spanish_ci NOT NULL,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nombre_categoria` (`nombre_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.4. clientes: personas que realizan compras (cedula unica)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientes` (
  `id_cliente` INT         NOT NULL AUTO_INCREMENT,
  `nombre`     VARCHAR(150) COLLATE utf8mb4_spanish_ci NOT NULL,
  `cedula`     VARCHAR(20) COLLATE utf8mb4_spanish_ci NOT NULL,
  `telefono`   VARCHAR(20) COLLATE utf8mb4_spanish_ci DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `cedula` (`cedula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.5. productos: items del inventario, pertenecen a una categoria
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `productos` (
  `id_producto`     INT          NOT NULL AUTO_INCREMENT,
  `nombre_producto` VARCHAR(150) COLLATE utf8mb4_spanish_ci NOT NULL,
  `id_categoria`    INT          NOT NULL,
  PRIMARY KEY (`id_producto`),
  KEY `id_categoria` (`id_categoria`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_categoria`)
    REFERENCES `categorias` (`id_categoria`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.6. lotes: unidades de un producto con stock, costo, precio y vencimiento.
--      Se eliminan en cascada junto con el producto.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `lotes` (
  `id_lote`           INT           NOT NULL AUTO_INCREMENT,
  `id_producto`       INT           NOT NULL,
  `stock`             INT           NOT NULL DEFAULT '0',
  `costo`             DECIMAL(10,2) NOT NULL,
  `precio`            DECIMAL(10,2) NOT NULL,
  `fecha_vencimiento` DATE          NOT NULL,
  `estado`            ENUM('Activo','Agotado','Inactivo') COLLATE utf8mb4_spanish_ci DEFAULT 'Activo',
  PRIMARY KEY (`id_lote`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `lotes_ibfk_1` FOREIGN KEY (`id_producto`)
    REFERENCES `productos` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.7. notas_entrega: cabecera de cada venta.
--      anio + secuencia forman el numero de control NNNN-AA (reinicio anual,
--      unicidad por uk_anio_secuencia). descuento guarda el descuento total
--      aplicado a la venta (por items y/o global).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `notas_entrega` (
  `numero_nota`     INT           NOT NULL AUTO_INCREMENT,
  `id_cliente`      INT           NOT NULL,
  `id_usuario`      INT           NOT NULL,
  `fecha_hora`      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  `monto_total`     DECIMAL(10,2) NOT NULL,
  `descuento`       DECIMAL(10,2) NOT NULL DEFAULT '0.00',
  `metodo_pago`     VARCHAR(50)   COLLATE utf8mb4_spanish_ci NOT NULL,
  `monto_cancelado` DECIMAL(10,2) NOT NULL,
  `anio`            SMALLINT      NOT NULL,
  `secuencia`       INT           NOT NULL,
  PRIMARY KEY (`numero_nota`),
  UNIQUE KEY `uk_anio_secuencia` (`anio`,`secuencia`),
  KEY `id_cliente` (`id_cliente`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `notas_entrega_ibfk_1` FOREIGN KEY (`id_cliente`)
    REFERENCES `clientes` (`id_cliente`) ON UPDATE CASCADE,
  CONSTRAINT `notas_entrega_ibfk_2` FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.8. detalle_nota: lineas de producto de cada nota de entrega.
--      Se elimina en cascada junto con la nota.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `detalle_nota` (
  `id_detalle`      INT           NOT NULL AUTO_INCREMENT,
  `numero_nota`     INT           NOT NULL,
  `id_producto`     INT           NOT NULL,
  `id_lote`         INT           NOT NULL,
  `precio_unitario` DECIMAL(10,2) NOT NULL,
  `cantidad`        INT           NOT NULL,
  `subtotal`        DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `numero_nota` (`numero_nota`),
  KEY `id_producto` (`id_producto`),
  KEY `id_lote` (`id_lote`),
  CONSTRAINT `detalle_nota_ibfk_1` FOREIGN KEY (`numero_nota`)
    REFERENCES `notas_entrega` (`numero_nota`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `detalle_nota_ibfk_2` FOREIGN KEY (`id_producto`)
    REFERENCES `productos` (`id_producto`) ON UPDATE CASCADE,
  CONSTRAINT `detalle_nota_ibfk_3` FOREIGN KEY (`id_lote`)
    REFERENCES `lotes` (`id_lote`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.9. secuencia_notas: consecutivo de notas de entrega por anio.
--      La app crea/actualiza la fila del anio actual automaticamente al
--      registrar una venta (INSERT ... ON DUPLICATE KEY UPDATE).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `secuencia_notas` (
  `anio`        SMALLINT NOT NULL,
  `consecutivo` INT      NOT NULL,
  PRIMARY KEY (`anio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.10. eventos: bitacora de actividades del sistema (login, ventas,
--       cambios de contrasena, respaldos). Si se elimina el usuario del
--       evento, el registro se conserva con id_usuario = NULL.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `eventos` (
  `id_evento`  INT          NOT NULL AUTO_INCREMENT,
  `id_usuario` INT          DEFAULT NULL,
  `tipo`       VARCHAR(50)  COLLATE utf8mb4_spanish_ci NOT NULL,
  `detalle`    VARCHAR(255) COLLATE utf8mb4_spanish_ci DEFAULT NULL,
  `fecha_hora` DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_evento`),
  KEY `fk_eventos_usuario` (`id_usuario`),
  CONSTRAINT `fk_eventos_usuario` FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ============================================================================
-- 3. DATOS INICIALES
-- ============================================================================

-- 3.1. Usuario administrador por defecto.
--      Usuario: admin | Contrasena: admin123 (encriptada con bcrypt)
INSERT INTO `usuarios` (`id_usuario`, `usuario`, `contrasena`, `cambio_obligatorio`, `rol`) VALUES
(1, 'admin', '$2b$12$cN.BRaTRqS0xc6gFyV7squ880B5vmTT3RYSOUQuD/Kq.3.raO5LfS', 0, 'Administrador');

-- 3.2. Permisos totales para el administrador
INSERT INTO `permisos_usuario` (`id_usuario`, `modulo_inventario`, `modulo_clientes`, `modulo_ventas`, `modulo_categorias`, `modulo_usuarios`, `modulo_historial`) VALUES
(1, 1, 1, 1, 1, 1, 1);

-- 3.3. Cliente generico para ventas sin cliente definido
INSERT INTO `clientes` (`id_cliente`, `nombre`, `cedula`, `telefono`) VALUES
(1, 'Cliente General', 'V-00000000', '0414-0000000');

-- 3.4. Secuencia de notas de entrega iniciada en cero para el anio actual
INSERT INTO `secuencia_notas` (`anio`, `consecutivo`) VALUES (YEAR(CURDATE()), 0);

-- ============================================================================
-- 4. VISTAS (definiciones identicas a las de produccion)
-- ============================================================================

-- 4.1. Inventario general: columnas id / Producto / Categoria / Stock
CREATE OR REPLACE VIEW `vista_inventario_general` AS
SELECT
  p.`id_producto`      AS `id`,
  p.`nombre_producto`  AS `Producto`,
  c.`nombre_categoria` AS `Categoria`,
  COALESCE(SUM(l.`stock`), 0) AS `Stock`
FROM `productos` p
JOIN `categorias` c ON p.`id_categoria` = c.`id_categoria`
LEFT JOIN `lotes` l
  ON p.`id_producto` = l.`id_producto` AND l.`estado` = 'Activo'
GROUP BY p.`id_producto`, p.`nombre_producto`, c.`nombre_categoria`;

-- 4.2. Alertas de vencimiento: lotes activos con stock que vencen en 0-90 dias
CREATE OR REPLACE VIEW `vista_alertas_vencimiento` AS
SELECT
  p.`nombre_producto`   AS `Producto`,
  l.`id_lote`           AS `Lote_ID`,
  l.`stock`             AS `Stock`,
  l.`fecha_vencimiento` AS `Vencimiento`,
  (TO_DAYS(l.`fecha_vencimiento`) - TO_DAYS(CURDATE())) AS `Dias_Restantes`
FROM `lotes` l
JOIN `productos` p ON l.`id_producto` = p.`id_producto`
WHERE l.`estado` = 'Activo'
  AND l.`stock` > 0
  AND (TO_DAYS(l.`fecha_vencimiento`) - TO_DAYS(CURDATE())) BETWEEN 0 AND 90
ORDER BY l.`fecha_vencimiento`;
