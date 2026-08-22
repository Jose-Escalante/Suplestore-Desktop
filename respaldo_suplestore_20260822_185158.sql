-- Respaldo Suplestore Tachira - 2026-08-22 18:52:08
-- Generado automaticamente por la aplicacion
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `categorias` (
  `id_categoria` int NOT NULL AUTO_INCREMENT,
  `nombre_categoria` varchar(100) COLLATE utf8mb4_spanish_ci NOT NULL,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nombre_categoria` (`nombre_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
INSERT INTO `categorias` (`id_categoria`, `nombre_categoria`) VALUES (2, 'Creatinas');
INSERT INTO `categorias` (`id_categoria`, `nombre_categoria`) VALUES (3, 'Pre-entrenos');
INSERT INTO `categorias` (`id_categoria`, `nombre_categoria`) VALUES (1, 'Proteínas');
INSERT INTO `categorias` (`id_categoria`, `nombre_categoria`) VALUES (4, 'Vitaminas');

CREATE TABLE `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) COLLATE utf8mb4_spanish_ci NOT NULL,
  `cedula` varchar(20) COLLATE utf8mb4_spanish_ci NOT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_spanish_ci DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `cedula` (`cedula`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
INSERT INTO `clientes` (`id_cliente`, `nombre`, `cedula`, `telefono`) VALUES (1, 'Jose', '32071243', '04147262707');
INSERT INTO `clientes` (`id_cliente`, `nombre`, `cedula`, `telefono`) VALUES (2, 'Maria', '30981941', '04141234678');

CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT,
  `nombre_producto` varchar(150) COLLATE utf8mb4_spanish_ci NOT NULL,
  `id_categoria` int NOT NULL,
  PRIMARY KEY (`id_producto`),
  KEY `id_categoria` (`id_categoria`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
INSERT INTO `productos` (`id_producto`, `nombre_producto`, `id_categoria`) VALUES (1, 'Whein Protein', 1);

CREATE TABLE `lotes` (
  `id_lote` int NOT NULL AUTO_INCREMENT,
  `id_producto` int NOT NULL,
  `stock` int NOT NULL DEFAULT '0',
  `costo` decimal(10,2) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `fecha_vencimiento` date NOT NULL,
  `estado` enum('Activo','Agotado','Inactivo') COLLATE utf8mb4_spanish_ci DEFAULT 'Activo',
  PRIMARY KEY (`id_lote`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `lotes_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
INSERT INTO `lotes` (`id_lote`, `id_producto`, `stock`, `costo`, `precio`, `fecha_vencimiento`, `estado`) VALUES (1, 1, 5, '300.00', '30.00', '2027-08-16', 'Activo');

CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `usuario` varchar(50) COLLATE utf8mb4_spanish_ci NOT NULL,
  `contrasena` varchar(255) COLLATE utf8mb4_spanish_ci NOT NULL,
  `cambio_obligatorio` tinyint(1) NOT NULL DEFAULT '0',
  `intentos_fallidos` int NOT NULL DEFAULT '0',
  `bloqueado_hasta` datetime DEFAULT NULL,
  `rol` enum('Administrador','Vendedor') COLLATE utf8mb4_spanish_ci NOT NULL DEFAULT 'Vendedor',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `usuario` (`usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
INSERT INTO `usuarios` (`id_usuario`, `usuario`, `contrasena`, `cambio_obligatorio`, `intentos_fallidos`, `bloqueado_hasta`, `rol`) VALUES (1, 'admin', '$2b$12$cN.BRaTRqS0xc6gFyV7squ880B5vmTT3RYSOUQuD/Kq.3.raO5LfS', 0, 0, NULL, 'Administrador');
INSERT INTO `usuarios` (`id_usuario`, `usuario`, `contrasena`, `cambio_obligatorio`, `intentos_fallidos`, `bloqueado_hasta`, `rol`) VALUES (2, 'Jose', '$2b$12$aHo0xRb2WTFj94bfthTTvuSHG9o85HkqFw87a7BMUVq3QrsLrdHHG', 0, 0, NULL, 'Administrador');
INSERT INTO `usuarios` (`id_usuario`, `usuario`, `contrasena`, `cambio_obligatorio`, `intentos_fallidos`, `bloqueado_hasta`, `rol`) VALUES (10, 'Maria', '$2b$12$1K5PSUDux0zHb7wcDGxjXeZZjduKSQAwvLiSkztv3vqykXlhNqXQW', 0, 0, NULL, 'Vendedor');
INSERT INTO `usuarios` (`id_usuario`, `usuario`, `contrasena`, `cambio_obligatorio`, `intentos_fallidos`, `bloqueado_hasta`, `rol`) VALUES (11, 'Tony', '$2b$12$JWX6B2UuCmRgwsoMi9e3VeLFyZolJKsa/Dwd/fg/EtNM9usWeMdQi', 0, 0, NULL, 'Vendedor');

CREATE TABLE `notas_entrega` (
  `numero_nota` int NOT NULL AUTO_INCREMENT,
  `id_cliente` int NOT NULL,
  `id_usuario` int NOT NULL,
  `fecha_hora` datetime DEFAULT CURRENT_TIMESTAMP,
  `monto_total` decimal(10,2) NOT NULL,
  `descuento` decimal(10,2) NOT NULL DEFAULT '0.00',
  `metodo_pago` varchar(50) COLLATE utf8mb4_spanish_ci NOT NULL,
  `monto_cancelado` decimal(10,2) NOT NULL,
  `anio` smallint NOT NULL,
  `secuencia` int NOT NULL,
  PRIMARY KEY (`numero_nota`),
  UNIQUE KEY `uk_anio_secuencia` (`anio`,`secuencia`),
  KEY `id_cliente` (`id_cliente`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `notas_entrega_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`) ON UPDATE CASCADE,
  CONSTRAINT `notas_entrega_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
INSERT INTO `notas_entrega` (`numero_nota`, `id_cliente`, `id_usuario`, `fecha_hora`, `monto_total`, `descuento`, `metodo_pago`, `monto_cancelado`, `anio`, `secuencia`) VALUES (1, 1, 1, '2026-08-16 16:05:28', '30.00', '0.00', 'Efectivo ($)', '30.00', 2026, 0);
INSERT INTO `notas_entrega` (`numero_nota`, `id_cliente`, `id_usuario`, `fecha_hora`, `monto_total`, `descuento`, `metodo_pago`, `monto_cancelado`, `anio`, `secuencia`) VALUES (2, 1, 1, '2026-08-16 16:07:10', '30.00', '0.00', 'Efectivo ($)', '30.00', 2026, 2);
INSERT INTO `notas_entrega` (`numero_nota`, `id_cliente`, `id_usuario`, `fecha_hora`, `monto_total`, `descuento`, `metodo_pago`, `monto_cancelado`, `anio`, `secuencia`) VALUES (3, 2, 1, '2026-08-17 17:04:30', '30.00', '0.00', 'Efectivo ($)', '30.00', 2026, 3);
INSERT INTO `notas_entrega` (`numero_nota`, `id_cliente`, `id_usuario`, `fecha_hora`, `monto_total`, `descuento`, `metodo_pago`, `monto_cancelado`, `anio`, `secuencia`) VALUES (6, 1, 10, '2026-08-17 23:53:18', '30.00', '0.00', 'Efectivo ($)', '30.00', 2026, 6);
INSERT INTO `notas_entrega` (`numero_nota`, `id_cliente`, `id_usuario`, `fecha_hora`, `monto_total`, `descuento`, `metodo_pago`, `monto_cancelado`, `anio`, `secuencia`) VALUES (7, 2, 1, '2026-08-22 17:41:18', '30.00', '0.00', 'Efectivo ($)', '30.00', 2026, 7);

CREATE TABLE `detalle_nota` (
  `id_detalle` int NOT NULL AUTO_INCREMENT,
  `numero_nota` int NOT NULL,
  `id_producto` int NOT NULL,
  `id_lote` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `cantidad` int NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `numero_nota` (`numero_nota`),
  KEY `id_producto` (`id_producto`),
  KEY `id_lote` (`id_lote`),
  CONSTRAINT `detalle_nota_ibfk_1` FOREIGN KEY (`numero_nota`) REFERENCES `notas_entrega` (`numero_nota`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `detalle_nota_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON UPDATE CASCADE,
  CONSTRAINT `detalle_nota_ibfk_3` FOREIGN KEY (`id_lote`) REFERENCES `lotes` (`id_lote`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
INSERT INTO `detalle_nota` (`id_detalle`, `numero_nota`, `id_producto`, `id_lote`, `precio_unitario`, `cantidad`, `subtotal`) VALUES (1, 1, 1, 1, '30.00', 1, '30.00');
INSERT INTO `detalle_nota` (`id_detalle`, `numero_nota`, `id_producto`, `id_lote`, `precio_unitario`, `cantidad`, `subtotal`) VALUES (2, 2, 1, 1, '30.00', 1, '30.00');
INSERT INTO `detalle_nota` (`id_detalle`, `numero_nota`, `id_producto`, `id_lote`, `precio_unitario`, `cantidad`, `subtotal`) VALUES (3, 3, 1, 1, '30.00', 1, '30.00');
INSERT INTO `detalle_nota` (`id_detalle`, `numero_nota`, `id_producto`, `id_lote`, `precio_unitario`, `cantidad`, `subtotal`) VALUES (6, 6, 1, 1, '30.00', 1, '30.00');
INSERT INTO `detalle_nota` (`id_detalle`, `numero_nota`, `id_producto`, `id_lote`, `precio_unitario`, `cantidad`, `subtotal`) VALUES (7, 7, 1, 1, '30.00', 1, '30.00');

CREATE TABLE `eventos` (
  `id_evento` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `tipo` varchar(50) COLLATE utf8mb4_spanish_ci NOT NULL,
  `detalle` varchar(255) COLLATE utf8mb4_spanish_ci DEFAULT NULL,
  `fecha_hora` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_evento`),
  KEY `fk_eventos_usuario` (`id_usuario`),
  CONSTRAINT `fk_eventos_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (2, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 18:32:39');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (3, 1, 'reset_contrasena', 'El administrador reseteo la contrasena al usuario (ID 5)', '2026-08-17 18:33:06');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (4, 1, 'logout', 'El usuario admin cerro sesion', '2026-08-17 18:33:17');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (5, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 18:33:41');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (6, 1, 'reset_contrasena', 'El administrador reseteo la contrasena al usuario (ID 5)', '2026-08-17 18:34:14');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (7, 1, 'logout', 'El usuario admin cerro sesion', '2026-08-17 18:34:25');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (8, NULL, 'login', 'El usuario maria1 inicio sesion', '2026-08-17 18:34:30');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (9, NULL, 'cambio_contrasena', 'El usuario Maria1 cambio su contrasena', '2026-08-17 18:34:45');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (10, NULL, 'logout', 'El usuario Maria1 cerro sesion', '2026-08-17 18:35:03');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (11, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 18:35:07');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (12, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 18:38:26');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (13, 1, 'logout', 'El usuario admin cerro sesion', '2026-08-17 18:38:30');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (14, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 18:38:35');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (15, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 18:40:04');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (16, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 18:51:29');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (17, 1, 'reset_contrasena', 'El administrador reseteo la contrasena al usuario (ID 2)', '2026-08-17 18:52:20');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (18, 1, 'logout', 'El usuario admin cerro sesion', '2026-08-17 18:52:30');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (19, 2, 'login', 'El usuario Jose inicio sesion', '2026-08-17 18:52:55');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (20, 2, 'cambio_contrasena', 'El usuario Jose cambio su contrasena', '2026-08-17 18:53:46');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (21, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 18:55:51');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (22, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 19:30:41');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (23, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 19:39:01');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (24, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 19:43:51');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (25, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 19:46:24');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (26, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 20:42:28');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (27, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 20:48:40');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (28, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 20:56:59');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (29, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 21:00:16');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (30, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 21:00:47');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (31, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 21:04:57');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (32, 1, 'login', 'El usuario admin inicio sesion', '2026-08-17 23:49:00');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (33, 1, 'logout', 'El usuario admin cerro sesion', '2026-08-17 23:51:08');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (34, 10, 'login', 'El usuario Maria inicio sesion', '2026-08-17 23:51:22');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (35, 10, 'cambio_contrasena', 'El usuario Maria cambio su contrasena', '2026-08-17 23:52:17');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (36, 10, 'venta', 'Venta registrada: Nota 0006-26 por $30.00', '2026-08-17 23:53:18');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (37, 1, 'login', 'El usuario admin inicio sesion', '2026-08-18 08:17:59');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (38, 1, 'login', 'El usuario admin inicio sesion', '2026-08-22 17:27:55');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (39, 1, 'logout', 'El usuario admin cerro sesion', '2026-08-22 17:28:11');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (40, 1, 'login', 'El usuario admin inicio sesion', '2026-08-22 17:28:18');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (41, 1, 'logout', 'El usuario admin cerro sesion', '2026-08-22 17:29:00');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (42, 11, 'login', 'El usuario Tony inicio sesion', '2026-08-22 17:29:20');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (43, 11, 'cambio_contrasena', 'El usuario Tony cambio su contrasena', '2026-08-22 17:30:19');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (44, 11, 'logout', 'El usuario Tony cerro sesion', '2026-08-22 17:31:19');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (45, 1, 'login', 'El usuario admin inicio sesion', '2026-08-22 17:31:27');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (46, 1, 'venta', 'Venta registrada: Nota 0007-26 por $30.00', '2026-08-22 17:41:18');
INSERT INTO `eventos` (`id_evento`, `id_usuario`, `tipo`, `detalle`, `fecha_hora`) VALUES (47, 1, 'login', 'El usuario admin inicio sesion', '2026-08-22 18:51:54');

CREATE TABLE `permisos_usuario` (
  `id_permiso` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `modulo_inventario` tinyint(1) DEFAULT '0',
  `modulo_clientes` tinyint(1) DEFAULT '0',
  `modulo_ventas` tinyint(1) DEFAULT '0',
  `modulo_categorias` tinyint(1) DEFAULT '0',
  `modulo_usuarios` tinyint(1) DEFAULT '0',
  `modulo_historial` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_permiso`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `permisos_usuario_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
INSERT INTO `permisos_usuario` (`id_permiso`, `id_usuario`, `modulo_inventario`, `modulo_clientes`, `modulo_ventas`, `modulo_categorias`, `modulo_usuarios`, `modulo_historial`) VALUES (1, 1, 1, 1, 1, 1, 1, 1);
INSERT INTO `permisos_usuario` (`id_permiso`, `id_usuario`, `modulo_inventario`, `modulo_clientes`, `modulo_ventas`, `modulo_categorias`, `modulo_usuarios`, `modulo_historial`) VALUES (2, 2, 1, 1, 1, 1, 1, 0);
INSERT INTO `permisos_usuario` (`id_permiso`, `id_usuario`, `modulo_inventario`, `modulo_clientes`, `modulo_ventas`, `modulo_categorias`, `modulo_usuarios`, `modulo_historial`) VALUES (8, 10, 1, 1, 1, 1, 1, 0);
INSERT INTO `permisos_usuario` (`id_permiso`, `id_usuario`, `modulo_inventario`, `modulo_clientes`, `modulo_ventas`, `modulo_categorias`, `modulo_usuarios`, `modulo_historial`) VALUES (9, 11, 1, 1, 1, 1, 1, 0);

CREATE TABLE `secuencia_notas` (
  `anio` smallint NOT NULL,
  `consecutivo` int NOT NULL,
  PRIMARY KEY (`anio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;
INSERT INTO `secuencia_notas` (`anio`, `consecutivo`) VALUES (2026, 7);

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_alertas_vencimiento` AS select `p`.`nombre_producto` AS `Producto`,`l`.`id_lote` AS `Lote_ID`,`l`.`stock` AS `Stock`,`l`.`fecha_vencimiento` AS `Vencimiento`,(to_days(`l`.`fecha_vencimiento`) - to_days(curdate())) AS `Dias_Restantes` from (`lotes` `l` join `productos` `p` on((`l`.`id_producto` = `p`.`id_producto`))) where ((`l`.`estado` = 'Activo') and (`l`.`stock` > 0) and ((to_days(`l`.`fecha_vencimiento`) - to_days(curdate())) between 0 and 90)) order by `l`.`fecha_vencimiento`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_inventario_general` AS select `p`.`id_producto` AS `id`,`p`.`nombre_producto` AS `Producto`,`c`.`nombre_categoria` AS `Categoria`,coalesce(sum(`l`.`stock`),0) AS `Stock` from ((`productos` `p` join `categorias` `c` on((`p`.`id_categoria` = `c`.`id_categoria`))) left join `lotes` `l` on(((`p`.`id_producto` = `l`.`id_producto`) and (`l`.`estado` = 'Activo')))) group by `p`.`id_producto`,`p`.`nombre_producto`,`c`.`nombre_categoria`;

SET FOREIGN_KEY_CHECKS=1;
