# Suplestore Táchira

Sistema de gestión de ventas, inventario y clientes para el comercio **Suplestore Táchira** en San Cristóbal, Venezuela.

Aplicación de escritorio construida con Python + Tkinter y MySQL.

## Funcionalidades

- **Login** con control de acceso por usuario y contraseña
- **Panel de control** con acceso por módulos según permisos
- **Inventario** con gestión de productos y lotes (control de stock, precios, fechas de vencimiento)
- **Clientes** (CRUD: registrar, actualizar, eliminar)
- **Ventas** con carrito de compras, descuento de stock por lotes (FIFO), y emisión de notas de entrega
- **Notas de entrega** con historial y detalle de productos
- **Usuarios** con roles (Administrador / Vendedor) y permisos por módulo
- **Alertas automáticas** de lotes próximos a vencer (< 90 días)

## Arquitectura: MVC

```
Prueba app/
├── main.py                     # Punto de entrada
├── AGENTS.md                   # Guía para agentes IA
├── requirements.txt
├── README.md
├── models/
│   └── database_model.py       # Modelo (consultas MySQL)
├── controllers/
│   └── app_controller.py       # Controlador (navegación, estado, permisos)
└── views/
    ├── login_view.py           # Vista de inicio de sesión
    ├── panel_view.py           # Panel de control
    ├── categorias_view.py      # CRUD de categorías
    ├── usuarios_view.py        # CRUD de usuarios
    ├── clientes_view.py        # CRUD de clientes
    ├── ventas_view.py          # Módulo de ventas y carrito
    └── inventario_view.py      # Gestión de inventario y lotes
```

## Requisitos

- Python 3.8+
- MySQL 5.7+ / 8.0
- Conexión de red al servidor MySQL

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración de base de datos

Ejecutar el script SQL de inicialización (no incluido en este repositorio) para crear la base de datos `suplestore_db` con sus tablas, vistas y datos iniciales.

Credenciales por defecto (configurables en `models/database_model.py:10-16`):

| Parámetro | Valor |
|-----------|-------|
| Host      | localhost |
| Usuario   | root |
| Password  | admin |
| Base de datos | suplestore_db |

## Ejecución

```bash
python main.py
```

## Créditos

Desarrollado por José Escalante, Giornaldo Gómez y Brandon Correa.
