# Design

## Context

Ver `proposal.md — Why` para la motivación. El modelo `Producto` ya tiene `codigo_uno` (FK → `CodigoUno`) y `codigo_dos` (FK → `CodigoDos`), y el endpoint `PATCH /productos/{id}/cambiar-estado/` ya existe con permisos `EsAdminOEmpleado`. No se requieren migraciones ni cambios de modelo. La base de datos está en PostgreSQL (Laragon, puerto 5433).

## Goals / Non-Goals

**Goals:**
- Exponer conteo de productos por prefijo en la API de catálogos.
- Añadir filtro `codigo_uno_id` al endpoint de productos.
- Dos vistas Vue con navegación de dos niveles (`/revision` y `/revision/:prefijo`).
- Ordenamiento letra-antes-número en ambas vistas, calculado en el frontend.

**Non-Goals:**
- Mostrar sufijos sin producto (solo se listan productos existentes).
- Paginación en la vista de detalle (el número de productos por prefijo es manejable).
- Filtros adicionales (estado, categoría) en la vista de Revisión.

## Decisions

### 1. Conteo de productos: query param vs. acción dedicada

**Decisión:** añadir `?con_conteo=true` al viewset existente de `CodigoUno` en `categorias/views.py`. Cuando el parámetro está presente, el serializer agrega `producto_count` a cada objeto usando `annotate(producto_count=Count('productos'))`.

**Alternativa descartada:** endpoint nuevo `/revision/prefijos/`. Innecesario; el viewset de `CodigoUno` ya tiene la ruta y el permiso correcto.

### 2. Filtro de productos por prefijo

**Decisión:** agregar `?codigo_uno_id=<id>` al `get_queryset()` de `ProductoViewSet`. Filtro exacto por ID (más robusto que por valor).

**Alternativa descartada:** reutilizar `?q=B` (búsqueda de texto). Devuelve falsos positivos: coincide en nombre, subcategoría, medida, etc.

### 3. Ordenamiento letra-antes-número

**Decisión:** ordenar en el **frontend** con una función de clave que separa letras de números. Letras: `(0, valor.toUpperCase())`; números: `(1, parseInt(valor))`. Mismo algoritmo para prefijos (vista principal) y sufijos (vista de detalle).

```javascript
function sortKey(valor) {
  return /^\d+$/.test(valor) ? [1, parseInt(valor), ''] : [0, 0, valor.toUpperCase()]
}
items.sort((a, b) => {
  const ka = sortKey(a.valor), kb = sortKey(b.valor)
  if (ka[0] !== kb[0]) return ka[0] - kb[0]
  return ka[0] === 1 ? ka[1] - kb[1] : ka[2].localeCompare(kb[2])
})
```

**Alternativa descartada:** ordenar en PostgreSQL con `CASE WHEN valor ~ '^[0-9]+$'`. Requiere consulta más compleja y la lógica no se reutilizaría fácilmente en el frontend.

### 4. Edición de estado

**Decisión:** selector `<select>` con las tres opciones (verde / amarillo / rojo) en cada fila. Al cambiar el valor llama a `PATCH /productos/{id}/cambiar-estado/` y actualiza el array reactivo en memoria sin recargar la lista.

**Alternativa descartada:** tres botones de color. Menos compacto en listas largas.

### 5. Rutas nuevas

`/revision` y `/revision/:prefijo` se agregan como rutas hijas bajo el layout `AppLayout`. Sin guardia `soloAdmin` (accesible a todos los roles). El enlace "Revisión" se añade en el navbar entre "Productos" y "Catálogos".

## Risks / Trade-offs

- **Prefijos mixtos (letras+números, ej. "B2"):** el algoritmo actual los trataría como letras. Si el catálogo tiene valores de este tipo el orden podría sorprender. Mitigación: documentar la convención; si el catálogo solo tiene valores puros, no aplica.
- **Carga inicial de todos los prefijos:** si `CodigoUno` crece a cientos de entradas, la vista principal puede tardar. Mitigación: la tabla es pequeña en el dominio de una bodega física; no se anticipa problema.
- **Sin paginación en detalle:** un prefijo con muchos productos carga todos de una vez. Mitigación: aceptable para el volumen esperado; se puede añadir paginación en el futuro si es necesario.
