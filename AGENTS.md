# BodegApp — Contexto del proyecto

## Qué es BodegApp

Aplicación de escritorio para gestionar y organizar productos físicos de bodega. Su característica principal es el código identificatorio de cada producto (ej. EB-40) para una fácil localización física. Reemplaza un archivo Excel que presentaba problemas de consistencia de datos, pérdida de cambios y falta de control de acceso.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python — Django 6 |
| API | Django REST Framework (DRF) |
| Base de datos | PostgreSQL (producción) / SQLite3 (desarrollo) |
| Frontend | JavaScript — Vue |
| Autenticación | JWT |
| Tests | pytest + pytest-django |

Dependencias actuales en `requirements.txt`:
```
asgiref==3.11.1
Django==6.0.3
djangorestframework==3.16.1
pytest==9.0.2
pytest-django==4.12.0
sqlparse==0.5.5
tzdata==2025.3
```

---

## Estructura del proyecto

```
BODEGAPP/
├── categorias/
├── config/
├── productos/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── service.py
│   ├── tests.py
│   └── views.py
├── qr/
├── usuarios/
├── venv/
├── db.sqlite3
├── manage.py
└── requirements.txt
```

---

## Modelos y relaciones

### Principios de diseño

- **Sin texto libre:** ningún campo crítico del producto acepta texto libre. Todas las partes del nombre y del código provienen de catálogos predefinidos seleccionados por dropdown.
- **Nombre calculado:** el nombre completo del producto no se almacena en la base de datos. Se construye en tiempo de ejecución concatenando los valores de los catálogos referenciados.
- **Trazabilidad completa:** cada cambio en un producto genera un registro inmutable en `Historial`.

### Modelos de catálogo (solo admin puede modificarlos)

Todos tienen `id` (PK autoincremental) y `nombre`/`valor` con restricción `unique=True`.

**Categoria** — clasificación de mayor nivel (equivalente a una hoja del Excel).
```python
id      | nombre (unique)
```

**Subcategoria** — agrupación dentro de una categoría.
```python
id      | categoria (FK → Categoria) | nombre
```

**MedidaPrincipal** — catálogo de medidas primarias. Ejemplos: `1/4`, `5/16`, `3/8`.
```python
id      | valor (unique)
```

**MedidaSecundaria** — catálogo de medidas secundarias. Ejemplos: `3/4`, `1`, `1 1/4`.
```python
id      | valor (unique)
```

**CodigoUno** — prefijo del código, siempre mayúsculas. Ejemplos: `EB`, `GB`, `HB`.
```python
id      | valor (unique)
```

**CodigoDos** — sufijo numérico del código. Ejemplos: `40`, `29`, `10`.
```python
id      | valor (unique)
```

### Modelo Producto

Modelo central. El nombre completo y el código se calculan a partir de las FK. No existe campo `nombre` en la tabla.

```python
id
subcategoria        FK → Subcategoria       (obligatorio)
medida_principal    FK → MedidaPrincipal    (obligatorio)
medida_secundaria   FK → MedidaSecundaria   (nullable)
codigo_uno          FK → CodigoUno          (nullable)
codigo_dos          FK → CodigoDos          (nullable)
estado              CharField: 'verde' | 'amarillo' | 'rojo'
creado_en           DateTimeField auto
actualizado_en      DateTimeField auto
actualizado_por     FK → Usuario (nullable)
```

**Regla de pareja de códigos:** `codigo_uno` y `codigo_dos` siempre deben ir juntos. Si uno tiene valor el otro también debe tenerlo; si uno es nulo el otro también debe serlo. Un producto puede tener exactamente un código completo o ninguno. Esta invariante se valida en `clean()`.

**Nombre completo calculado** (property):
```
subcategoria.nombre + medida_principal.valor + "X" + medida_secundaria.valor
→ "TORNILLO GRADO 5  1/4 X 3/4"
```

**Código completo calculado** (property):
```
codigo_uno.valor + "-" + codigo_dos.valor  →  "EB-40"
(ninguno)                                  →  "—"
```

**Restricciones de unicidad compuestas:**
```python
unique_together = [
    ['subcategoria', 'medida_principal', 'medida_secundaria'],  # nombre único
    ['codigo_uno', 'codigo_dos'],                               # código único global
]
```

### Modelo Historial

Se genera automáticamente con cada cambio en un producto. Nunca se modifica ni elimina.

```python
id
producto            FK → Producto
usuario             FK → Usuario
campo_modificado    CharField  # ej: 'estado', 'codigo_uno'
valor_anterior      CharField
valor_nuevo         CharField
fecha               DateTimeField auto
```

### Modelo Usuario

```python
id
nombre              CharField
email               EmailField (unique)  # usado como login
password_hash       CharField            # nunca texto plano
rol                 CharField: 'admin' | 'empleado'
creado_en           DateTimeField auto
```

**Roles:**
- `admin`: gestiona catálogos, usuarios, productos y consulta historial.
- `empleado`: consulta y actualiza estado de productos. No puede modificar catálogos.

### Mapa de relaciones

```
Categoria      ──< Subcategoria   (una categoría tiene muchas subcategorías)
Subcategoria   ──< Producto       (una subcategoría agrupa muchos productos)
MedidaPrincipal──< Producto
MedidaSecundaria─< Producto       (nullable)
CodigoUno      ──< Producto
CodigoDos      ──< Producto
Usuario        ──< Producto       (actualizado_por)
Producto       ──< Historial
Usuario        ──< Historial
```

---

## Historias de usuario

| ID | Actor | Historia |
|---|---|---|
| HU-01 | Admin | Gestionar productos de bodega para mantener el inventario actualizado y organizado. |
| HU-02 | Admin, Empleado | Cambiar el estado del producto para reflejar la disponibilidad física real en bodega. |
| HU-03 | Empleado | Acceder a la aplicación para ver los productos disponibles en bodega. |
| HU-04 | Admin | Gestionar los catálogos (categorías, subcategorías, medidas, códigos) para garantizar consistencia en los datos. |
| HU-05 | Admin, Empleado | Buscar productos por nombre o código para encontrarlos rápido sin navegar por todas las categorías. |
| HU-06 | Admin | Consultar el historial de cambios de un producto para auditar quién modificó qué y cuándo. |
| HU-07 | Admin, Empleado | Generar y escanear el código QR de un producto para identificarlo desde un dispositivo móvil. |

---

## Casos de uso

**CU-01 — Iniciar sesión**
Actores: Admin, Empleado. El usuario ingresa correo y contraseña. El sistema valida credenciales, identifica el rol y redirige a la vista correspondiente.

**CU-02 — Gestionar producto**
Actor: Admin. Requiere catálogos con datos. El admin crea, edita o elimina un producto seleccionando valores de los dropdowns. El sistema muestra preview del nombre y código antes de confirmar. Al guardar registra `actualizado_por` y `actualizado_en`.

**CU-03 — Cambiar estado del producto**
Actores: Admin, Empleado. El usuario localiza el producto y selecciona el nuevo estado (verde / amarillo / rojo). El sistema actualiza el estado y genera un registro en `Historial` con valor anterior y nuevo.

**CU-04 — Gestionar catálogos**
Actor: Admin. Puede agregar, editar o eliminar valores en cualquier catálogo. No puede eliminar un valor referenciado por un producto activo. Valida unicidad antes de guardar.

**CU-05 — Buscar producto**
Actores: Admin, Empleado. El usuario escribe en el buscador. El sistema filtra en tiempo real por nombre (subcategoría + medidas) y por código completo.

**CU-06 — Consultar historial**
Actor: Admin. Desde el detalle del producto accede al historial ordenado del más reciente al más antiguo, con campo modificado, valores anterior/nuevo, usuario y fecha.

**CU-07 — Generar código QR**
Actores: Admin, Empleado. Desde el detalle del producto genera el QR con el ID del producto. Puede visualizarse en pantalla o descargarse. Al escanearlo abre el detalle del producto en el móvil.

**CU-08 — Cerrar sesión**
Actores: Admin, Empleado. El sistema invalida la sesión JWT activa y redirige al login.

---

## Convenciones de código

- Los modelos de catálogo siguen el patrón: `id` + un único campo `valor` o `nombre` con `unique=True`.
- Los serializers exponen el `nombre_completo` y `codigo_completo` como campos de solo lectura calculados (SerializerMethodField).
- La lógica de negocio (generación de historial, validaciones) vive en `service.py`, no en views ni serializers.
- Los tests van en `tests.py` de cada app usando pytest. Fixtures en `conftest.py`.
- Las vistas siguen el patrón ViewSet de DRF.
- El estado del producto se valida con `choices` en el modelo: `VERDE`, `AMARILLO`, `ROJO`.

---

## Comportamientos automáticos esperados

- Al guardar o actualizar cualquier `Producto`, se debe registrar automáticamente en `Historial` el campo que cambió, el valor anterior y el nuevo, junto con el usuario autenticado.
- `actualizado_en` y `actualizado_por` se actualizan en cada `save()`.
- El nombre completo y el código completo nunca se persisten; siempre se calculan.
- Los valores de catálogo que estén referenciados por al menos un producto deben estar protegidos contra eliminación (`on_delete=PROTECT`).