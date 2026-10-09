# Tasks

## 1. Rama y migración (prerequisito)

- [x] 1.1 Crear rama `feature/codigo-libre` desde `develop` y verificar que está activa con `git branch`
- [x] 1.2 Ejecutar `python manage.py migrate` para aplicar `0006_producto_codigo_unico_opcional` y verificar que `productos_producto` tiene columnas `codigo_uno_id` y `codigo_dos_id` (consultar `information_schema.columns`)

## 2. Corrección de código roto (bugfix)

- [x] 2.1 En `categorias/views.py`, cambiar la anotación de `CodigoUnoViewSet.get_queryset()` de `Count('producto_codigos__producto', distinct=True)` a `Count('productos', distinct=True)` y verificar que `GET /codigos-uno/?con_conteo=true` devuelve conteos correctos sin error
- [x] 2.2 En `productos/views.py`, cambiar el filtro de `qs.filter(codigos__codigo_uno_id=codigo_uno_id)` a `qs.filter(codigo_uno_id=codigo_uno_id)` y verificar que `GET /productos/?codigo_uno_id=<id>` devuelve productos correctos
- [x] 2.3 En `productos/management/commands/seed.py`, eliminar import de `ProductoCodigo`, reescribir el bloque de creación de productos para asignar `codigo_uno` y `codigo_dos` directamente en `Producto.objects.get_or_create` (campo `defaults`), y verificar que `python manage.py seed` ejecuta sin errores
- [x] 2.4 En `frontend/src/views/RevisionDetalleView.vue`, reemplazar las funciones `codigoDosValor(prod)` y `codigoPrincipal(prod)` para usar `prod.codigo_dos_valor` y `prod.codigo_completo` directamente (sin acceder a `prod.codigos`) y verificar que la vista de detalle de revisión muestra códigos y ordena correctamente

## 3. Modelo y migración de CodigoLibre

- [x] 3.1 Agregar clase `CodigoLibre` a `categorias/models.py` con FKs `codigo_uno` (PROTECT, `related_name='codigos_libres'`) y `codigo_dos` (PROTECT, `related_name='codigos_libres'`), `unique_together = [('codigo_uno', 'codigo_dos')]`, y método `__str__` que devuelve `"<prefijo>-<sufijo>"`. Verificar con `python manage.py check` sin errores
- [x] 3.2 Crear y aplicar la migración: `python manage.py makemigrations categorias -n add_codigo_libre && python manage.py migrate` y verificar que la tabla `categorias_codigolibre` existe en la DB
- [x] 3.3 Agregar `CodigoLibreSerializer` a `categorias/serializers.py` con campos `id`, `codigo_uno` (PK write-only), `codigo_dos` (PK write-only), `codigo_uno_valor` (read-only, `source='codigo_uno.valor'`), `codigo_dos_valor` (read-only, `source='codigo_dos.valor'`). Verificar que el serializer acepta `{codigo_uno: id, codigo_dos: id}` y devuelve los valores en lectura
- [x] 3.4 Agregar `CodigoLibreViewSet` a `categorias/views.py` extendiendo `CatalogoBaseViewSet`. `get_queryset()` devuelve todos los registros con `select_related('codigo_uno', 'codigo_dos')`. Sobreescribir `create` y `update` para validar que la combinación no está asignada a un `Producto` (si lo está, devolver 400 con mensaje "Ese código ya está asignado a un producto"). Verificar permiso: POST/PATCH/DELETE requieren admin; GET requiere autenticado
- [x] 3.5 Registrar la ruta `codigos-libres` en `categorias/urls.py` y verificar que `GET /codigos-libres/` responde 200

## 4. Auto-limpieza en service.py

- [x] 4.1 En `productos/service.py`, importar `CodigoLibre` de `categorias.models`. En `crear_producto`, después de asignar código al producto, agregar `CodigoLibre.objects.filter(codigo_uno=codigo_uno, codigo_dos=codigo_dos).delete()`. Aplicar el mismo patrón en `actualizar_producto` (usando los valores final de `nuevo_codigo_uno` y `nuevo_codigo_dos`). Verificar: registrar código "B-1" como libre, crear producto con ese código, confirmar que ya no aparece en `GET /codigos-libres/`

## 5. Vista Vue — CodigoLibreView

- [x] 5.1 Crear `frontend/src/views/CodigoLibreView.vue` con: lista de códigos libres ordenada (letras antes que números, misma función `sortKey` que `RevisionView.vue`); formulario inline de agregar (dos selects: prefijo de `/codigos-uno/`, sufijo de `/codigos-dos/`); botones "Editar" y "Eliminar" por fila; modo edición inline con los mismos selects pre-cargados. Verificar que la lista carga, se puede agregar un código libre válido, el error "Ese código ya está asignado" se muestra al intentar uno ocupado, y se puede editar y eliminar
- [x] 5.2 Agregar ruta `{ path: 'codigo-libre', name: 'codigo-libre', component: () => import('@/views/CodigoLibreView.vue'), meta: { soloAdmin: true } }` en `frontend/src/router/index.js` y verificar que navegar a `/codigo-libre` carga la vista (admin) y redirige a `/productos` (empleado)
- [x] 5.3 Agregar enlace "Código libre" en `frontend/src/layouts/AppLayout.vue` con `v-if="auth.esAdmin"`, junto a los demás enlaces de la barra de navegación (escritorio y menú móvil). Verificar que aparece en sesión admin y no aparece en sesión empleado

## Workflow follow-up

- Probar manualmente el flujo completo: CRUD de código libre, auto-limpieza al asignar producto, orden correcto, y Revisión de Bodega funcionando con el bugfix.
- Hacer commit, push a `feature/codigo-libre`, merge a `develop`, merge a `main`, push ambos.
- Archivar el change con `/opsx:archive`.
