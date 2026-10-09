# Proposal

## Why

La bodega acumula pares de códigos (prefijo + sufijo) que están disponibles para asignar a productos pero aún no tienen producto vinculado. Sin un registro explícito, el equipo no puede distinguir qué códigos están "reservados" de los que simplemente no se han usado. Además, el cambio de modelo de datos de la sesión anterior dejó el backend y el frontend con código inconsistente que rompe Productos y Revisión de Bodega, situación que debe resolverse antes de agregar cualquier nueva funcionalidad.

## What Changes

- **Bugfix (prerequisito):** Aplicar migración `0006_producto_codigo_unico_opcional` para sincronizar DB con `models.py`. Corregir código roto en `categorias/views.py` (anotación `Count`), `productos/views.py` (filtro `codigo_uno_id`), `seed.py` (import `ProductoCodigo`), y `RevisionDetalleView.vue` (acceso a `prod.codigos`).
- **Nuevo modelo `CodigoLibre`** en la app `categorias`: par `(codigo_uno, codigo_dos)` con unique_together, validación de que el código no esté asignado a ningún producto.
- **API CRUD** `GET/POST /codigos-libres/`, `PATCH/DELETE /codigos-libres/{id}/`: admin para escritura, todos los autenticados para lectura. Lectura devuelve lista ordenada (letras A–Z primero, luego números ascendentes).
- **Auto-limpieza**: cuando un producto es creado o actualizado con un código, el servicio de productos elimina el `CodigoLibre` correspondiente si existe.
- **Vista Vue `/codigo-libre`**: lista de códigos libres, formulario inline de creación (selección de prefijo/sufijo existentes en catálogo), acciones de edición y eliminación por fila.
- **Enlace de navegación** "Código libre" en `AppLayout.vue`, visible solo para administradores (operación de mantenimiento).

## Capabilities

### New Capabilities

- `codigo-libre`: Registro y gestión de pares de códigos disponibles (no asignados a ningún producto). Permite crear, editar y eliminar entradas manualmente, con validación de unicidad contra productos existentes.

### Modified Capabilities

(ninguna — el bugfix restaura el comportamiento ya especificado en `revision-bodega` sin cambiar sus requisitos)

## Impact

- `categorias/models.py`: nuevo modelo `CodigoLibre`, nueva migración
- `categorias/serializers.py`: nuevo `CodigoLibreSerializer`
- `categorias/views.py`: nuevo `CodigoLibreViewSet`, corrección anotación `Count`
- `categorias/urls.py`: registro de ruta `codigos-libres`
- `productos/views.py`: corrección filtro `codigo_uno_id`
- `productos/service.py`: auto-eliminación de `CodigoLibre` al asignar código a producto
- `productos/management/commands/seed.py`: eliminar import/uso de `ProductoCodigo`
- `frontend/src/views/RevisionDetalleView.vue`: corrección acceso a código del producto
- `frontend/src/views/CodigoLibreView.vue`: nueva vista
- `frontend/src/router/index.js`: nueva ruta `/codigo-libre`
- `frontend/src/layouts/AppLayout.vue`: nuevo enlace de navegación
