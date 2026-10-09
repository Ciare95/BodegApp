# Tasks

## 1. Backend — Conteo de productos por prefijo

- [x] 1.1 En `categorias/views.py`, sobreescribir `get_queryset()` en `CodigoUnoViewSet`: cuando el parámetro `?con_conteo=true` está presente, agregar `annotate(producto_count=Count('productos'))` (importar `Count` de `django.db.models`). Verificar con `GET /codigos-uno/?con_conteo=true` que cada objeto incluye el campo `producto_count`.
- [x] 1.2 En `categorias/serializers.py`, agregar `producto_count = serializers.IntegerField(read_only=True, default=0)` al `CodigoUnoSerializer` y añadirlo a `fields`. Verificar que sin `?con_conteo=true` el campo vale `0` y con el parámetro vale el conteo real.

## 2. Backend — Filtro por prefijo en productos

- [x] 2.1 En `productos/views.py`, en `ProductoViewSet.get_queryset()`, leer el parámetro `codigo_uno_id` y aplicar `qs.filter(codigo_uno_id=codigo_uno_id)` cuando está presente. Verificar con `GET /productos/?codigo_uno_id=<id_válido>` que solo devuelve productos de ese prefijo, y que sin el parámetro devuelve todos.

## 3. Frontend — Rutas y navegación

- [x] 3.1 En `frontend/src/router/index.js`, agregar dos rutas hijas bajo `AppLayout`: `{ path: 'revision', name: 'revision', component: () => import('@/views/RevisionView.vue') }` y `{ path: 'revision/:prefijo', name: 'revision-detalle', component: () => import('@/views/RevisionDetalleView.vue') }`. Verificar que navegar a `/revision` no redirige a otra ruta.
- [x] 3.2 En `frontend/src/layouts/AppLayout.vue`, agregar el enlace `<RouterLink to="/revision" class="nav-link">Revisión</RouterLink>` en `.navbar-menu` (después de "Productos", antes de "Catálogos") y el equivalente en `.mobile-menu`. Sin guardia `v-if`. Verificar que el enlace aparece para usuario autenticado con cualquier rol.

## 4. Frontend — RevisionView.vue

- [x] 4.1 Crear `frontend/src/views/RevisionView.vue`. Al montar, llamar `GET /codigos-uno/?con_conteo=true`. Implementar la función de ordenamiento: letras primero (A–Z, `localeCompare`), luego números (ascendente por valor entero). Verificar en consola que el array ordenado tiene letras antes que números.
- [x] 4.2 Renderizar la cuadrícula de cards. Cada card muestra `valor` del prefijo y, si `producto_count === 0`, el texto "Sin productos"; si `producto_count > 0`, el número. Al hacer clic, navegar a `/revision/:prefijo` pasando el `id` y `valor` del prefijo (usar query params o state de router). Verificar que al hacer clic en una card con prefijo "B" la URL cambia a `/revision/B`.

## 5. Frontend — RevisionDetalleView.vue

- [x] 5.1 Crear `frontend/src/views/RevisionDetalleView.vue`. Leer `route.params.prefijo` para obtener el valor del prefijo. Llamar `GET /codigos-uno/?con_conteo=true` para obtener el `id` del prefijo; luego llamar `GET /productos/?codigo_uno_id=<id>`. Aplicar el mismo algoritmo de ordenamiento sobre `codigo_dos_valor` de los resultados. Verificar que la lista carga y está ordenada correctamente.
- [x] 5.2 Renderizar la lista de productos. Cada fila muestra: código completo (`codigo_completo`), nombre completo (`nombre_completo`), y un `<select>` con opciones verde / amarillo / rojo con el valor actual seleccionado y un punto de color que cambia según el estado. Verificar visualmente que cada fila muestra los tres campos y que el color del select coincide con el estado del producto.
- [x] 5.3 Al cambiar el `<select>`, llamar `PATCH /productos/{id}/cambiar-estado/` con `{ estado: nuevoValor }` usando el cliente axios existente. Actualizar el producto en el array reactivo local con el estado devuelto por la API. Verificar que al cambiar el estado en UI, el color cambia de inmediato y que recargando la página el nuevo estado persiste.
- [x] 5.4 Mostrar un breadcrumb o botón "← Revisión" que navegue de vuelta a `/revision`. Si el prefijo no tiene productos, mostrar el mensaje "Sin productos para este prefijo". Verificar que el botón de vuelta funciona y que la vista vacía muestra el mensaje.

## Workflow follow-up

- Ejecutar el backend y el frontend, hacer pruebas manuales completas (navegar entre vistas, cambiar estados, verificar orden) e informar el resultado antes de archivar.
- Archivar el change con `/opsx:archive` y mergear a develop y main.
