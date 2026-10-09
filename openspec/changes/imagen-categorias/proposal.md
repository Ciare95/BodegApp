# Proposal

## Why

Las cards de categorías y subcategorías en `/productos` muestran solo texto, lo que hace la navegación visualmente plana y difícil de identificar de un vistazo. Añadir imágenes representativas a cada categoría y subcategoría mejora la UX y acelera la orientación visual del usuario en bodega.

## What Changes

- **Backend**: campo `imagen` (opcional) en los modelos `Categoria` y `Subcategoria`.
- **Backend**: configuración de `MEDIA_ROOT` y `MEDIA_URL` en `settings.py` para servir archivos subidos localmente.
- **Backend**: endpoint `PATCH /categorias/{id}/` y `PATCH /subcategorias/{id}/` acepta `multipart/form-data` para actualizar la imagen.
- **Backend**: los serializers exponen la URL absoluta de la imagen (`imagen_url`).
- **Frontend** (`ProductosView.vue`): las cards de categorías y subcategorías muestran la imagen arriba y el nombre abajo; toda la card es clickeable.
- **Frontend** (`TablaCatalogo.vue`): el modal de edición de categorías y subcategorías incluye un campo para subir o reemplazar la imagen desde el sistema de archivos del usuario.

## Capabilities

### New Capabilities

- `imagenes-catalogos`: gestión (upload/reemplazo) y visualización de imágenes asociadas a categorías y subcategorías.

### Modified Capabilities

*(ninguna — no cambian requisitos de specs existentes)*

## Impact

- **Modelos**: `categorias/models.py` — `Categoria`, `Subcategoria`
- **Migraciones**: nueva migración en `categorias/migrations/`
- **Serializers**: `categorias/serializers.py` — `CategoriaSerializer`, `SubcategoriaSerializer`
- **Settings**: `config/settings.py` — `MEDIA_ROOT`, `MEDIA_URL`
- **URLs**: `config/urls.py` — ruta para servir media en desarrollo
- **Frontend**: `frontend/src/views/ProductosView.vue`, `frontend/src/components/TablaCatalogo.vue`
- **Dependencias nuevas**: `Pillow` (requerido por `ImageField` de Django)
