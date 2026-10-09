# Design

## Context

Ver `proposal.md — Why` para la motivación.

**Estado actual del modelo de datos:**
- `Producto` tiene FKs directas `codigo_uno` / `codigo_dos` (nullable, unique_together) en `models.py`.
- La DB está en estado post-migración `0005` (tabla `productos_productocodigo` existe, columnas `codigo_uno_id`/`codigo_dos_id` no existen en `productos_producto`). La migración `0006_producto_codigo_unico_opcional` fue escrita para re-sincronizar DB y código pero no se ha aplicado.
- Como resultado, el backend y el frontend tienen código roto que asume el modelo intermedio (`ProductoCodigo`) que ya no existe en `models.py`.

**Convenciones del proyecto:**
- App `categorias`: catálogos (CodigoUno, CodigoDos, etc.) con `CatalogoBaseViewSet` (admin para escritura, autenticados para lectura).
- App `productos`: lógica de negocio en `service.py` con `@transaction.atomic`.
- Frontend Vue 3 con Composition API, `client` axios, selects desde catálogos existentes.
- Orden: letras A-Z primero, luego números ascendentes (función `sortKey` ya implementada en `RevisionView.vue`).

## Goals / Non-Goals

**Goals:**
- Aplicar migración pendiente y corregir código inconsistente (prerequisito).
- Nuevo modelo `CodigoLibre` con validación de unicidad contra productos.
- CRUD API siguiendo convenciones de la app `categorias`.
- Auto-limpieza desde `service.py` al asignar código a producto.
- Vista Vue lista + formulario inline con selects de catálogos existentes.

**Non-Goals:**
- Auto-creación de `CodigoUno`/`CodigoDos` desde la vista (solo se usan valores existentes).
- Notificaciones ni historial de cambios en `CodigoLibre`.
- Acceso para empleados (solo admin gestiona).

## Decisions

### 1. Ubicación del modelo `CodigoLibre` → app `categorias`

`CodigoLibre` es un registro de catálogo (pares de códigos), no un producto. Colocarlo en `categorias` mantiene la cohesión y permite reusar `CatalogoBaseViewSet`.

Alternativa descartada: nueva app `codigos` — innecesaria para la cantidad de lógica involucrada.

### 2. Auto-limpieza en `service.py`, no en señales Django

El servicio ya centraliza la creación y actualización de productos con `@transaction.atomic`. Agregar la eliminación de `CodigoLibre` dentro de la misma transacción garantiza consistencia sin introducir señales que son más difíciles de rastrear.

```python
# En crear_producto y actualizar_producto, tras asignar el código:
CodigoLibre.objects.filter(codigo_uno=codigo_uno, codigo_dos=codigo_dos).delete()
```

Alternativa descartada: señal `post_save` en `Producto` — dificulta seguir el flujo y no participa en la transacción atómica de forma explícita.

### 3. Formulario inline con selects (no modal separado)

La vista muestra la lista y, al pulsar "Agregar" o "Editar", expande un formulario inline con dos selects (`CodigoUno`, `CodigoDos`). Coincide con el patrón de otras vistas del proyecto.

### 4. Ordenamiento en el frontend

Reusar la función `sortKey` (letras antes que números) ya definida en `RevisionView.vue`. La API devuelve todos los registros sin paginación (la cantidad de códigos libres es reducida), el ordenamiento se aplica en el cliente.

### 5. Bugfix: aplicar migración 0006 antes de cualquier código nuevo

La migración `0006_producto_codigo_unico_opcional` re-agrega `codigo_uno_id`/`codigo_dos_id` a la DB y migra datos de la tabla intermedia. Debe ser la primera tarea de implementación. Después se corrige el código roto.

## Risks / Trade-offs

- **Migración 0006 con datos existentes** → Si la tabla `productos_productocodigo` tiene datos, el SQL de `0006` los copia a las columnas directas. Si un producto tiene múltiples entradas en la tabla (diseño previo lo permitía), solo se toma la primera por `DISTINCT ON (producto_id)`. Mitigación: verificar datos antes de aplicar con `SELECT producto_id, COUNT(*) FROM productos_productocodigo GROUP BY producto_id HAVING COUNT(*) > 1`.
- **`CodigoUno`/`CodigoDos` con `on_delete=PROTECT` en `CodigoLibre`** → No se puede eliminar un prefijo o sufijo del catálogo si está en uso en un código libre. Es el comportamiento deseado, pero el mensaje de error puede ser confuso. Mitigación: la vista de Catálogos ya maneja este caso con un mensaje legible.

## Migration Plan

1. Crear rama `feature/codigo-libre` desde `develop`.
2. Aplicar `python manage.py migrate` (ejecuta migración `0006`).
3. Corregir código roto (views, seed, frontend).
4. Implementar `CodigoLibre` (modelo, migración, serializer, viewset, urls).
5. Implementar lógica de auto-limpieza en `service.py`.
6. Implementar vista Vue.
7. Verificar manualmente: CRUD, validaciones, auto-limpieza, orden.
8. Commit, push, merge a develop y main.
