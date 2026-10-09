# Spec Delta

## Purpose

Permite asociar una imagen representativa a cada categoría y subcategoría, visualizarla como card con imagen y nombre en la vista de navegación de productos, y gestionarla (subir o reemplazar) desde el panel de catálogos del admin.

## ADDED Requirements

### Requirement: Campo imagen en Categoria y Subcategoria
El sistema SHALL almacenar una imagen opcional para cada `Categoria` y cada `Subcategoria`. La imagen puede estar ausente; en ese caso el sistema SHALL mostrar un placeholder visual.

#### Scenario: Categoria sin imagen devuelta por la API
- **WHEN** se consulta `GET /categorias/` o `GET /categorias/{id}/`
- **THEN** la respuesta SHALL incluir `imagen_url: null` cuando no hay imagen asociada

#### Scenario: Categoria con imagen devuelta por la API
- **WHEN** se consulta `GET /categorias/` o `GET /categorias/{id}/`
- **THEN** la respuesta SHALL incluir `imagen_url` con la URL absoluta accesible desde el navegador

#### Scenario: Subcategoria sin imagen
- **WHEN** se consulta `GET /subcategorias/`
- **THEN** la respuesta SHALL incluir `imagen_url: null` cuando no hay imagen

#### Scenario: Subcategoria con imagen
- **WHEN** se consulta `GET /subcategorias/`
- **THEN** la respuesta SHALL incluir `imagen_url` con la URL absoluta de la imagen

---

### Requirement: Upload y reemplazo de imagen vía API
El sistema SHALL aceptar la subida y el reemplazo de la imagen de una categoría o subcategoría mediante `PATCH` al endpoint correspondiente con `Content-Type: multipart/form-data`.

#### Scenario: Subir imagen a una categoria existente
- **WHEN** el admin envía `PATCH /categorias/{id}/` con `Content-Type: multipart/form-data` y un campo `imagen` con un archivo de imagen válido
- **THEN** el sistema SHALL almacenar el archivo y devolver la nueva `imagen_url` en la respuesta

#### Scenario: Reemplazar imagen existente
- **WHEN** el admin envía `PATCH /categorias/{id}/` con una nueva imagen sobre una que ya tenía imagen
- **THEN** el sistema SHALL reemplazar el archivo y actualizar `imagen_url`

#### Scenario: Archivo inválido rechazado
- **WHEN** el admin envía un archivo que no es una imagen (por tipo MIME)
- **THEN** el sistema SHALL retornar HTTP 400 con un mensaje de error de validación

#### Scenario: Solo admin puede subir imágenes
- **WHEN** un usuario con rol `empleado` intenta `PATCH` con imagen
- **THEN** el sistema SHALL retornar HTTP 403

---

### Requirement: Visualización de imagen en cards de navegación
El sistema SHALL mostrar la imagen de la categoría o subcategoría en la card de navegación de `/productos`. La card SHALL ser completamente clickeable (tanto la imagen como el texto).

#### Scenario: Card de categoria con imagen
- **WHEN** el usuario navega a `/productos` y la categoría tiene imagen
- **THEN** la card SHALL mostrar la imagen en la parte superior y el nombre debajo

#### Scenario: Card de categoria sin imagen
- **WHEN** el usuario navega a `/productos` y la categoría no tiene imagen
- **THEN** la card SHALL mostrar un área de placeholder y el nombre debajo

#### Scenario: Click en cualquier parte de la card navega al nivel siguiente
- **WHEN** el usuario hace click sobre la imagen o sobre el nombre de la card
- **THEN** el sistema SHALL navegar al nivel de subcategorías de esa categoría (o a los productos si es subcategoría)

---

### Requirement: Gestión de imagen desde el panel de catálogos
El admin SHALL poder subir o reemplazar la imagen de una categoría o subcategoría desde el modal de edición en `/catalogos`, usando un selector de archivo del sistema operativo.

#### Scenario: Modal de edición muestra imagen actual
- **WHEN** el admin abre el modal de edición de una categoria que tiene imagen
- **THEN** el modal SHALL mostrar una previsualización de la imagen actual

#### Scenario: Modal de edición sin imagen previa
- **WHEN** el admin abre el modal de edición de una categoria sin imagen
- **THEN** el modal SHALL mostrar un área de drop/selección de archivo

#### Scenario: El admin selecciona una imagen nueva
- **WHEN** el admin selecciona un archivo de imagen desde el selector del sistema operativo
- **THEN** el modal SHALL mostrar una previsualización del archivo seleccionado antes de guardar

#### Scenario: Guardar con imagen nueva
- **WHEN** el admin hace click en "Guardar" con una imagen seleccionada
- **THEN** el sistema SHALL enviar `PATCH` con `multipart/form-data` y persistir la imagen
