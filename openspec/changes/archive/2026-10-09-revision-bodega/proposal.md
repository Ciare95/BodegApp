# Proposal

## Why

El equipo necesita una herramienta para recorrer la bodega código por código y saber qué producto ocupa cada posición, sin tener que pasar por la vista de Productos filtrada. La revisión por prefijo (e.g. todos los "B-*") es la unidad natural de trabajo cuando se hace mantenimiento físico de estantes.

## What Changes

- Se agrega un enlace "Revisión" en la barra de navegación, visible para todos los roles (admin y empleado).
- Nueva vista `/revision`: muestra cards de texto con todos los prefijos (`CodigoUno`), ordenados alfabéticamente (letras A–Z primero, luego números 1, 2, 3…), con el conteo de productos asignados. Prefijos sin productos muestran "Sin productos".
- Nueva vista `/revision/:prefijo`: al hacer clic en un prefijo, muestra la lista de productos de ese prefijo, ordenados por sufijo (`CodigoDos`) alfabéticamente y en ascendente. Cada fila muestra el código completo, el nombre del producto y un selector de estado (verde / amarillo / rojo) que guarda de forma inmediata.
- El backend expone el conteo de productos por prefijo y un filtro por `codigo_uno_id` en el endpoint existente de productos.

## Capabilities

### New Capabilities

- `revision-bodega`: Vista de revisión de bodega organizada por prefijos de código, con navegación de dos niveles y edición de estado en línea.

### Modified Capabilities

(ninguna)

## Impact

- **Frontend**: `AppLayout.vue` (navbar), `router/index.js` (2 rutas nuevas), 2 componentes Vue nuevos (`RevisionView.vue`, `RevisionDetalleView.vue`).
- **Backend**: `categorias/views.py` (acción o query param `con_conteo=true` en el viewset de `CodigoUno`); `productos/views.py` (filtro `codigo_uno_id` en `ProductoViewSet`).
- **Sin cambios de modelo ni migraciones**: toda la información necesaria ya existe en el modelo `Producto` y los catálogos `CodigoUno` / `CodigoDos`.
- **Sin cambios de permisos**: la edición de estado usa el endpoint existente `PATCH /productos/{id}/cambiar-estado/` que ya permite `EsAdminOEmpleado`.
