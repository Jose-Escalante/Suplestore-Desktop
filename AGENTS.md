# Suplestore Táchira - Guía para Agentes IA

## Arquitectura: MVC (Modelo-Vista-Controlador)

```
Prueba app/
├── main.py                           # Punto de entrada
├── AGENTS.md                         # Esta guía
├── opencode.json                     # Configuración del agente
├── requirements.txt                  # Dependencias del proyecto
├── README.md                         # Documentación general
├── models/                           # CAPA MODELO (SRP)
│   ├── __init__.py                   # Exporta todos los modelos
│   ├── connection.py                 # DatabaseConnection (conexión MySQL)
│   ├── database_model.py             # FACADE: unifica los sub-modelos
│   ├── user_model.py                 # UserModel: usuarios y permisos
│   ├── client_model.py               # ClientModel: clientes CRUD
│   ├── category_model.py             # CategoryModel: categorías CRUD
│   ├── product_model.py              # ProductModel: productos y lotes
│   └── sale_model.py                 # SaleModel: ventas y notas
├── controllers/
│   └── app_controller.py             # CAPA CONTROLADOR: estado, navegación, permisos
└── views/
    ├── login_view.py                 # CAPA VISTA: login
    ├── panel_view.py                 # CAPA VISTA: panel de control
    ├── categorias_view.py            # CAPA VISTA: CRUD categorías
    ├── usuarios_view.py              # CAPA VISTA: CRUD usuarios
    ├── clientes_view.py              # CAPA VISTA: CRUD clientes
    ├── ventas_view.py                # CAPA VISTA: módulo de ventas + carrito
    └── inventario_view.py            # CAPA VISTA: inventario y lotes
```

## Principios SOLID aplicados

### Single Responsibility (SRP) — Modelos
Cada modelo tiene **una única responsabilidad**:

| Clase | Archivo | Responsabilidad |
|-------|---------|----------------|
| `DatabaseConnection` | `connection.py` | Conexión a MySQL (commit/rollback) |
| `UserModel` | `user_model.py` | Usuarios y permisos |
| `ClientModel` | `client_model.py` | Clientes (CRUD) |
| `CategoryModel` | `category_model.py` | Categorías (CRUD) |
| `ProductModel` | `product_model.py` | Productos, lotes e inventario |
| `SaleModel` | `sale_model.py` | Notas de entrega y ventas |
| `DatabaseModel` | `database_model.py` | Fachada (delega a los modelos SRP) |

**Regla:** Si necesitas modificar la lógica de clientes, solo tocas `client_model.py`. Nunca mezcles responsabilidades.

### Dependency Injection
Cada modelo SRP recibe `DatabaseConnection` por inyección:
```python
db = DatabaseConnection()
user_model = UserModel(db)
client_model = ClientModel(db)
```
Esto permite probar cada modelo de forma aislada.

### Facade Pattern
`DatabaseModel` expone el mismo `self.controller.model.*()` que antes, pero delega internamente al modelo SRP correcto. Las vistas no se enteran del cambio.

## Reglas del proyecto

### 1. Sin comentarios en el código
- No agregues comentarios a archivos `.py` salvo este `AGENTS.md`
- La documentación va en `README.md` o `AGENTS.md`

### 2. No importar tkinter desde el modelo
- `models/` NO debe importar `tkinter` excepto `messagebox` en `connection.py` para errores críticos de conexión
- Los sub-modelos (`user_model.py`, etc.) usan `messagebox` para errores de BD
- Para errores de negocio, lanza excepción y que el controlador la maneje

### 3. Flujo de datos
```
Vista (View) --→ Controlador (Controller) --→ DatabaseModel (facade)
                                                      │
                                            ┌─────────┼─────────┐
                                            │         │         │
                                       UserModel  ClientModel  ...
```
- Las Vistas **nunca** llaman a los modelos SRP directamente, solo al facade
- Las Vistas **nunca** modifican el estado del controller directamente
- El Controlador es el único que escribe en `usuario_actual` y decide navegación

### 4. Cada Vista recibe el controller en `__init__`
```python
class MiVista:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root
```
- Usa `self.root` como ventana padre
- Usa `self.controller.model.metodo()` para acceder a datos
- Usa `self.controller.show_*()` para navegar

### 5. Navegación entre pantallas
Siempre usa los métodos del controller:
```python
controller.show_panel()
controller.show_login()
controller.show_categorias()
controller.show_usuarios()
controller.show_clientes()
controller.show_ventas()
controller.show_inventario()
```

### 6. Convenciones de código
- **Sin comentarios** en el código
- Nombres de métodos/variables en `snake_case`
- Nombres de clases en `PascalCase`
- Botones sin emojis en el texto
- Layout: `top_bar` verde con título, `container` gris oscuro, `sidebar` a la derecha con botones, tabla a la izquierda
- Imports ordenados: estándar → terceros → locales

### 7. Base de datos
- Motor: MySQL (`mysql.connector`)
- Host: `localhost`, User: `root`, Password: `admin`, DB: `suplestore_db`
- La conexión se hace en `DatabaseConnection.__init__()` (`models/connection.py`)
- Todas las consultas usan `cursor(dictionary=True)` para devolver dicts
- `commit()` y `rollback()` van por `self.db.commit()` / `self.db.rollback()`

### 8. Permisos
- Cada módulo tiene permiso booleano en `permisos_usuario`
- El controller expone `verificar_permiso(modulo)` y `verificar_permiso_o_rechazar(modulo)`
- Las vistas de módulos verifican permiso antes de construirse (el controller lo hace automáticamente en `show_*`)

### 9. Cómo agregar un nuevo módulo

#### Si el módulo necesita nuevos datos en BD:
1. Crear `models/mi_modulo_model.py` con una clase que reciba `db: DatabaseConnection`
2. Agregar métodos de consulta en esa clase
3. En `models/database_model.py`:
   - Importar la clase
   - Instanciarla en `__init__`
   - Agregar métodos de delegación

#### Vista y controlador:
1. Crear `views/mi_modulo_view.py` con clase `MiModuloView(controller)`
2. En `controllers/app_controller.py`:
   - Importar la vista
   - Agregar método `show_mi_modulo()` con verificación de permiso

### 10. Ejecución
```bash
pip install -r requirements.txt
python main.py
```
Requiere Python 3.8+ con `mysql-connector-python` instalado.
