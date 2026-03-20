# Implementation Plan: login-username

## Overview

Reemplazar el campo `email` como identificador de login por `username` en BodegApp. El cambio abarca modelo, autenticación, serializers, migraciones y frontend Vue.

## Tasks

- [ ] 1. Agregar campo `username` al modelo `Usuario`
  - [ ] 1.1 Modificar `usuarios/models.py` para agregar `username = models.CharField(max_length=50, unique=True, validators=[RegexValidator(r'^[a-zA-Z0-9_-]+$')])`
    - Importar `RegexValidator` desde `django.core.validators`
    - El campo `email` se mantiene sin cambios
    - _Requirements: 1.1, 1.2, 1.4_

  - [ ] 1.2 Escribir test de propiedad P1: Username inválido es rechazado
    - **Property 1: Username inválido es rechazado**
    - Usar `st.text()` filtrado para incluir al menos un carácter fuera de `[a-zA-Z0-9_-]`
    - Tag: `# Feature: login-username, Property 1: Username inválido rechazado`
    - **Validates: Requirements 1.2, 3.2**

  - [ ] 1.3 Escribir test de propiedad P2: Username duplicado retorna HTTP 400
    - **Property 2: Username duplicado retorna HTTP 400**
    - Usar `st.from_regex(r'^[a-zA-Z0-9_-]{1,50}$')` para generar usernames válidos
    - Tag: `# Feature: login-username, Property 2: Username duplicado → 400`
    - **Validates: Requirements 1.1, 1.3**

  - [ ] 1.4 Escribir tests unitarios para el modelo
    - `test_email_se_mantiene_en_modelo` — campo `email` sigue existiendo
    - `test_username_max_50_chars` — username de 51 caracteres es rechazado
    - `test_username_solo_guion_valido` — `-` y `_` solos son válidos
    - _Requirements: 1.1, 1.2, 1.4_

- [ ] 2. Crear migraciones de base de datos
  - [ ] 2.1 Crear `usuarios/migrations/0002_usuario_username_nullable.py`
    - Agrega `username` como `null=True, blank=True` para poder aplicar sobre datos existentes
    - _Requirements: 5.3_

  - [ ] 2.2 Crear `usuarios/migrations/0003_populate_username.py`
    - Migración de datos con `RunPython` que ejecuta `generar_username` para cada usuario existente
    - Implementar función `generar_username(email)` en la migración: extrae parte local del email, sanitiza con `re.sub(r'[^a-zA-Z0-9_-]', '_', base)[:50]`, agrega sufijo `_N` incremental si hay colisión
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ] 2.3 Crear `usuarios/migrations/0004_usuario_username_not_null.py`
    - Hace `username` `NOT NULL` y aplica `unique=True`
    - _Requirements: 1.1, 5.3_

  - [ ] 2.4 Escribir test de propiedad P8: Generación de username produce valores únicos
    - **Property 8: Generación de username produce valores únicos derivados del email**
    - Usar `st.lists(st.emails(), min_size=1)` para generar conjuntos de emails
    - Verificar que todos los usernames generados son únicos y derivados de la parte local del email
    - Tag: `# Feature: login-username, Property 8: Generación de username única`
    - **Validates: Requirements 5.1, 5.2**

  - [ ] 2.5 Escribir test de propiedad P9: Migración preserva datos existentes
    - **Property 9: Migración preserva datos existentes**
    - Verificar que `id`, `nombre`, `email`, `password_hash`, `rol`, `creado_en` no cambian tras la migración
    - Tag: `# Feature: login-username, Property 9: Migración preserva datos`
    - **Validates: Requirements 5.3**

- [ ] 3. Checkpoint — Asegurar que las migraciones aplican sin errores
  - Ejecutar `python manage.py migrate` y verificar que no hay errores
  - Asegurar que todos los tests del paso 1 y 2 pasan

- [ ] 4. Actualizar lógica de autenticación
  - [ ] 4.1 Modificar `usuarios/views.py` — `LoginView`
    - Cambiar lookup de `email` → `username` en la consulta a la base de datos
    - Cambiar el campo esperado en el request de `email` a `username`
    - Mantener mensaje de error unificado `"Credenciales inválidas"` para username inexistente y password incorrecta
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 4.2 Modificar `usuarios/authentication.py` — `obtener_tokens_para_usuario`
    - Reemplazar `refresh['email'] = usuario.email` por `refresh['username'] = usuario.username` en el payload JWT
    - `AutenticacionJWTUsuario.authenticate` no requiere cambios funcionales
    - _Requirements: 2.4, 2.5_

  - [ ] 4.3 Escribir test de propiedad P3: Credenciales inválidas retornan 401
    - **Property 3: Credenciales inválidas retornan 401 con mensaje correcto**
    - Usar `st.text()` para usernames/passwords inexistentes
    - Verificar que la respuesta es siempre 401 con `"Credenciales inválidas"` sin distinguir cuál campo es incorrecto
    - Tag: `# Feature: login-username, Property 3: Credenciales inválidas → 401`
    - **Validates: Requirements 2.2, 2.3**

  - [ ] 4.4 Escribir test de propiedad P4: Login exitoso retorna JWT con campos correctos
    - **Property 4: Login exitoso retorna JWT con campos requeridos**
    - Verificar que el payload contiene exactamente `user_id`, `username` y `rol` con valores correctos
    - Verificar que `AutenticacionJWTUsuario` resuelve el token al usuario correcto usando `user_id`
    - Tag: `# Feature: login-username, Property 4: JWT con campos correctos`
    - **Validates: Requirements 2.1, 2.4, 2.5**

  - [ ] 4.5 Escribir test unitario: login con email falla
    - `test_login_con_email_falla` — enviar `email` en lugar de `username` retorna error
    - _Requirements: 2.1_

- [ ] 5. Actualizar serializers
  - [ ] 5.1 Modificar `UsuarioRegistroSerializer` en `usuarios/serializers.py`
    - Agregar `username` a `fields` como campo obligatorio
    - Agregar validación de patrón `^[a-zA-Z0-9_-]+$` (puede reutilizar el validator del modelo)
    - _Requirements: 3.1, 3.2_

  - [ ] 5.2 Modificar `UsuarioPerfilSerializer` en `usuarios/serializers.py`
    - Agregar `username` a `fields`
    - Verificar que `password_hash` no está en `fields`
    - _Requirements: 3.3, 3.4_

  - [ ] 5.3 Escribir test de propiedad P5: Registro sin username es rechazado
    - **Property 5: Registro sin username es rechazado**
    - Generar payloads de registro con `username` omitido o vacío (`""`)
    - Verificar que el serializer rechaza antes de persistir
    - Tag: `# Feature: login-username, Property 5: Registro sin username rechazado`
    - **Validates: Requirements 3.1**

  - [ ] 5.4 Escribir test de propiedad P6: Perfil expone username y oculta password_hash
    - **Property 6: Perfil expone username y oculta password_hash**
    - Para usuarios con distintos usernames generados, verificar que `/api/usuarios/me/` incluye `username` y no contiene `password_hash`
    - Tag: `# Feature: login-username, Property 6: Perfil expone username, oculta password_hash`
    - **Validates: Requirements 3.3, 3.4**

- [ ] 6. Checkpoint — Asegurar que todos los tests de backend pasan
  - Ejecutar `pytest usuarios/` y verificar que no hay fallos
  - Asegurar que todos los tests de propiedades (P1–P6, P8, P9) pasan con `max_examples=100`

- [ ] 7. Actualizar frontend Vue
  - [ ] 7.1 Modificar `frontend/src/stores/auth.js`
    - Cambiar firma `login(email, password)` → `login(username, password)`
    - Enviar `{ username, password }` en el body del request en lugar de `{ email, password }`
    - _Requirements: 4.4_

  - [ ] 7.2 Modificar `frontend/src/views/LoginView.vue`
    - Reemplazar campo `email` (type="email") por `username` (type="text") con etiqueta `"Usuario"`
    - Agregar validación client-side: campo vacío al enviar → mostrar `"El usuario es requerido"` sin llamar a la API
    - Mapear respuesta HTTP 401 → mostrar `"Usuario o contraseña incorrectos"`
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 7.3 Escribir tests de componente para LoginView.vue
    - `test_campo_usuario_presente` — formulario tiene etiqueta "Usuario" (Req. 4.1)
    - `test_username_vacio_muestra_error` — formulario vacío muestra "El usuario es requerido" sin llamar a la API (Req. 4.2)
    - `test_mensaje_401_correcto` — HTTP 401 muestra "Usuario o contraseña incorrectos" (Req. 4.3)
    - Usar Vitest + @vue/test-utils
    - _Requirements: 4.1, 4.2, 4.3_

- [ ] 8. Checkpoint final — Asegurar que todos los tests pasan
  - Ejecutar `pytest` para el backend completo
  - Ejecutar `vitest --run` para el frontend
  - Verificar que no hay tests rotos ni regresiones en otras features

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada tarea referencia los requisitos específicos para trazabilidad
- Los tests de propiedad usan Hypothesis con `@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])`
- La migración en 3 pasos (nullable → populate → not null) es la estrategia más segura para datos existentes
- El campo `email` se mantiene en el modelo; solo cambia el identificador de login
