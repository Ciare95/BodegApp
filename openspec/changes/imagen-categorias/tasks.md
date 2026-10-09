# Tasks

## 1. Rama y dependencias

- [x] 1.1 Crear rama `feature/imagen` desde `develop` con `git checkout develop && git checkout -b feature/imagen` y verificar que la rama activa es `feature/imagen`
- [x] 1.2 Instalar Pillow con `venv\Scripts\pip install Pillow` y agregarlo a `requirements.txt`; verificar con `pip show Pillow`

## 2. Backend — configuración de media

- [x] 2.1 Agregar `MEDIA_ROOT = BASE_DIR / 'media'` y `MEDIA_URL = '/media/'` en `config/settings.py`; verificar que la variable existe imprimiendo `python manage.py shell -c "from django.conf import settings; print(settings.MEDIA_ROOT)"`
- [x] 2.2 Agregar ruta para servir media en desarrollo en `config/urls.py`: `path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT})` (importar `serve` de `django.views.static`); verificar que el servidor arranca sin error

## 3. Backend — modelos y migración

- [x] 3.1 Agregar `imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)` a `Categoria` en `categorias/models.py`; verificar que el campo existe inspeccionando `Categoria._meta.get_field('imagen')`
- [x] 3.2 Agregar `imagen = models.ImageField(upload_to='subcategorias/', blank=True, null=True)` a `Subcategoria` en `categorias/models.py`
- [x] 3.3 Generar migración con `python manage.py makemigrations categorias` y verificar que crea un archivo en `categorias/migrations/`
- [x] 3.4 Aplicar migración con `python manage.py migrate` y verificar que termina sin errores

## 4. Backend — serializers y parsers

- [x] 4.1 Agregar `imagen_url = serializers.SerializerMethodField()` y su método `get_imagen_url` a `CategoriaSerializer`; el método devuelve `request.build_absolute_uri(obj.imagen.url)` si hay imagen, `None` si no; verificar con `GET /categorias/` que el campo aparece en la respuesta
- [x] 4.2 Hacer lo mismo para `SubcategoriaSerializer` y verificar con `GET /subcategorias/`
- [x] 4.3 Agregar `parser_classes = [MultiPartParser, FormParser, JSONParser]` a `CatalogoBaseViewSet` en `categorias/views.py`; verificar que `PATCH /categorias/{id}/` con `multipart/form-data` e imagen devuelve 200 y `imagen_url` no nula (probar con curl o Postman)

## 5. Frontend — cards de navegación en ProductosView

- [x] 5.1 Modificar el bloque de cards de categorías en `ProductosView.vue`: el `.cat-card` pasa a mostrar imagen (o placeholder) arriba y nombre abajo; eliminar el ícono de flecha; el área completa (imagen + texto) permanece clickeable llamando a `seleccionarCategoria(cat)`; verificar visualmente en `/productos`
- [x] 5.2 Hacer lo mismo para el bloque de subcategorías (`seleccionarSubcategoria(sub)`); verificar visualmente
- [x] 5.3 Asegurar que las cards sin imagen muestran un placeholder (fondo neutro + ícono de imagen); verificar con una categoría sin imagen

## 6. Frontend — modo imagen en TablaCatalogo

- [x] 6.1 Agregar prop `conImagen: { type: Boolean, default: false }` y `campoImagen: { type: String, default: 'imagen_url' }` a `TablaCatalogo.vue`; verificar que el componente acepta las props sin romper los catálogos existentes
- [x] 6.2 Cuando `conImagen` es `true`, reemplazar la tabla por un grid de cards con imagen arriba y nombre abajo; la tabla sigue mostrándose cuando `conImagen` es `false`; verificar abriendo la tab de Categorías en `/catalogos`
- [x] 6.3 En modo `conImagen`, el botón Editar abre un modal con: previsualización de imagen actual (o placeholder), `<input type="file" accept="image/*">` con previsualización local (`URL.createObjectURL`), campo de texto para el nombre; verificar abriendo el modal de edición de una categoría
- [x] 6.4 Al guardar con imagen nueva, `guardarEdicion` envía `PATCH` con `FormData` (incluyendo el archivo y el nombre); verificar que la imagen aparece actualizada en el grid tras guardar
- [x] 6.5 Al guardar sin cambiar imagen (solo nombre), `guardarEdicion` envía solo el campo `nombre` (sin archivo vacío en el FormData) para no sobrescribir la imagen existente; verificar que la imagen no se pierde al editar solo el nombre

## 7. Frontend — CatalogosView

- [x] 7.1 Pasar `:con-imagen="true"` y `campo-imagen="imagen_url"` a `TablaCatalogo` en las tabs de Categorías y Subcategorías en `CatalogosView.vue`; verificar que las otras tabs (medidas, códigos) siguen mostrando tabla normal

## 8. Verificación de integración

- [x] 8.1 Flujo completo admin: ir a `/catalogos` → tab Categorías → Editar → subir imagen → Guardar → navegar a `/productos` y confirmar que la card de esa categoría muestra la imagen subida
- [x] 8.2 Flujo completo subcategorías: mismo flujo en tab Subcategorías y verificar que la imagen aparece al hacer click en la categoría padre

## Workflow follow-up

- Ejecutar `git add` + `git commit` con los cambios de la rama `feature/imagen`.
- Revisar los cambios en PowerShell con:
  ```powershell
  git diff develop...feature/imagen --stat
  git diff develop...feature/imagen
  ```
- Hacer merge a `develop` cuando la revisión sea satisfactoria.
