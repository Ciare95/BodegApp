# Design

## Context

Ver `proposal.md — Why` para la motivación. El estado actual relevante:

- `Categoria` y `Subcategoria` en `categorias/models.py` solo tienen campos `nombre` (y FK en Subcategoria). Sin campo de imagen.
- `settings.py` no tiene `MEDIA_ROOT` ni `MEDIA_URL` configurados. Usa `whitenoise` para estáticos.
- Los ViewSets heredan de `CatalogoBaseViewSet` con permisos ya definidos (`EsSoloAdmin` para escritura).
- `ProductosView.vue` muestra `.cat-card` como `<button>` con solo texto + ícono flecha.
- `TablaCatalogo.vue` es un componente genérico (6 catálogos) con edición inline en fila. El modal de creación acepta `camposCreacion` vía props, pero no soporta uploads.

---

## Goals / Non-Goals

**Goals:**
- Campo `imagen` opcional en `Categoria` y `Subcategoria` con almacenamiento local en `media/`.
- API acepta `multipart/form-data` en `PATCH` para ambos modelos.
- Cards en `ProductosView` muestran imagen + nombre; toda la card es clickeable.
- Modal de edición en `TablaCatalogo` (solo para catálogos con imagen) permite subir/reemplazar imagen con previsualización.

**Non-Goals:**
- Redimensionado o compresión de imágenes en el servidor.
- CDN o almacenamiento en la nube.
- Imágenes en otros modelos de catálogo (MedidaPrincipal, MedidaSecundaria, CodigoUno, CodigoDos).
- Eliminar la imagen de forma independiente (sin reemplazarla); la imagen se puede dejar en blanco al actualizar si se requiere en el futuro.

---

## Decisions

### 1. `ImageField` de Django (con Pillow) vs `CharField` con ruta manual

**Decisión**: `ImageField`.

`ImageField` valida que el archivo sea una imagen real (requiere Pillow), genera rutas relativas en la BD y se integra nativamente con `FileResponse` de DRF. `CharField` obligaría a validar manualmente el tipo MIME y gestionar el path.

**Alternativa descartada**: `CharField` — más código de validación, sin garantía de integridad del tipo.

---

### 2. Directorio de almacenamiento

**Decisión**:
```
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL  = '/media/'
upload_to  = 'categorias/'   (Categoria)
upload_to  = 'subcategorias/'  (Subcategoria)
```

Archivos quedan en `BodegApp/media/categorias/<nombre_archivo>`. En desarrollo, Django sirve `/media/` directamente vía `django.views.static.serve` montado en `config/urls.py`.

---

### 3. Serializer — exposición de la URL de imagen

**Decisión**: campo `SerializerMethodField` llamado `imagen_url` que devuelve la URL absoluta usando `request.build_absolute_uri(instance.imagen.url)` cuando hay imagen, o `None`.

No se expone el path relativo (`imagen`) directamente al frontend para evitar acoplamiento al sistema de archivos.

---

### 4. Estrategia de upload en el ViewSet

**Decisión**: `parser_classes = [MultiPartParser, FormParser, JSONParser]` en `CatalogoBaseViewSet`. DRF ya enruta `PATCH` al serializer correcto; al incluir `MultiPartParser`, `request.FILES` estará disponible.

No se requiere override de `update()`: el serializer con `ImageField` toma el archivo de `request.FILES` automáticamente.

---

### 5. Frontend — componente de cards

**Decisión**: Modificar `TablaCatalogo.vue` para aceptar dos nuevas props opcionales:
- `conImagen: Boolean` — activa el modo card con imagen en lugar de tabla.
- `campoImagen: String` — nombre del campo en el objeto que contiene la `imagen_url`.

Cuando `conImagen` es `true`, el componente renderiza un grid de cards en lugar de la tabla, y el modal de edición incluye un `<input type="file" accept="image/*">` con previsualización local (`URL.createObjectURL`).

**Alternativa descartada**: nuevo componente `TarjetasCatalogo.vue` separado. Mantener la lógica de CRUD (cargar, crear, editar, eliminar, confirmación) en un solo componente es preferible a duplicar esa lógica. La prop `conImagen` actúa como switch de presentación sin romper los catálogos existentes.

---

### 6. Rama de desarrollo

**Decisión**: rama `feature/imagen` creada desde `develop`.

---

## Risks / Trade-offs

- **Archivos huérfanos** → Si se reemplaza una imagen, el archivo anterior queda en disco. En un entorno local esto es aceptable; se puede limpiar manualmente o con un comando de gestión en el futuro.
- **Sin redimensionado** → Una imagen muy grande (ej. 10 MB) se sirve tal cual. Riesgo: lentitud en la carga de `/productos`. Mitigación: documentar en la UI que se recomienda subir imágenes ligeras. Fuera de scope para esta iteración.
- **`TablaCatalogo` más complejo** → Añadir la prop `conImagen` rompe el modelo "componente puramente tabular". Trade-off aceptado: evita duplicar ~150 líneas de lógica CRUD.

## Migration Plan

1. Crear rama `feature/imagen` desde `develop`.
2. Instalar `Pillow` y agregarlo a `requirements.txt`.
3. Agregar `MEDIA_ROOT` / `MEDIA_URL` a `settings.py` y ruta media a `config/urls.py`.
4. Agregar campo `imagen` a `Categoria` y `Subcategoria`; generar y aplicar migración.
5. Actualizar serializers para exponer `imagen_url`.
6. Actualizar `CatalogoBaseViewSet` con los parsers multipart.
7. Modificar `TablaCatalogo.vue` con prop `conImagen` y lógica de upload/preview.
8. Modificar `CatalogosView.vue` para pasar `con-imagen` a las tabs de Categorías y Subcategorías.
9. Modificar `ProductosView.vue` para renderizar cards con imagen.

**Rollback**: revertir la rama. Las migraciones pueden deshacerse con `migrate categorias 0001_initial` (o el número anterior).
