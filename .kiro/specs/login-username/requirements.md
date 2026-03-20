# Requirements Document

## Introduction

BodegApp actualmente usa el campo `email` como identificador de login. Esta feature reemplaza ese campo por un `username` (nombre de usuario único) para mejorar la UX: los empleados de bodega prefieren recordar un alias corto en lugar de su dirección de correo completa.

El cambio implica agregar el campo `username` al modelo `Usuario`, actualizar la lógica de autenticación JWT para validar por `username`, actualizar los serializers y vistas del backend, y actualizar el formulario de login en el frontend Vue.

## Glossary

- **Sistema**: BodegApp en su conjunto (backend Django + frontend Vue).
- **Backend**: Servidor Django con DRF que expone la API REST.
- **Frontend**: Aplicación Vue.js que consume la API.
- **Usuario**: Instancia del modelo `Usuario` con rol `admin` o `empleado`.
- **Username**: Identificador único de texto corto (solo letras, números, guiones bajos y guiones) que el usuario elige al momento de ser registrado. No es el nombre completo (`nombre`).
- **Autenticador**: Componente `AutenticacionJWTUsuario` en `usuarios/authentication.py`.
- **Servicio_Auth**: Lógica de negocio de autenticación en `usuarios/services.py`.
- **Serializer_Registro**: `UsuarioRegistroSerializer` en `usuarios/serializers.py`.
- **Serializer_Perfil**: `UsuarioPerfilSerializer` en `usuarios/serializers.py`.
- **LoginView**: Vista Vue en `frontend/` que muestra el formulario de inicio de sesión.
- **Token_JWT**: Par de tokens (access + refresh) generados por `obtener_tokens_para_usuario`.

---

## Requirements

### Requirement 1: Campo username en el modelo Usuario

**User Story:** Como admin, quiero que cada usuario tenga un `username` único, para que los empleados puedan identificarse con un alias corto en lugar de su email.

#### Acceptance Criteria

1. THE Backend SHALL agregar el campo `username` al modelo `Usuario` con restricción `unique=True` y longitud máxima de 50 caracteres.
2. THE Backend SHALL aceptar únicamente valores de `username` que contengan letras, números, guiones bajos (`_`) y guiones (`-`).
3. IF se intenta guardar un `Usuario` con un `username` ya existente, THEN THE Backend SHALL retornar un error de validación con código HTTP 400.
4. THE Backend SHALL mantener el campo `email` en el modelo `Usuario` para preservar datos históricos y permitir comunicaciones futuras.

---

### Requirement 2: Autenticación por username

**User Story:** Como empleado, quiero iniciar sesión con mi `username` y contraseña, para no tener que recordar mi dirección de email.

#### Acceptance Criteria

1. WHEN el Frontend envía `username` y `password` al endpoint de login, THE Servicio_Auth SHALL buscar al `Usuario` por el campo `username`.
2. WHEN el `username` no existe en la base de datos, THE Servicio_Auth SHALL retornar un error con código HTTP 401 y el mensaje `"Credenciales inválidas"`.
3. WHEN el `username` existe pero la `password` no coincide con `password_hash`, THE Servicio_Auth SHALL retornar un error con código HTTP 401 y el mensaje `"Credenciales inválidas"`.
4. WHEN las credenciales son válidas, THE Servicio_Auth SHALL retornar un `Token_JWT` que incluya `user_id`, `username` y `rol` en el payload.
5. THE Autenticador SHALL resolver el `user_id` del `Token_JWT` contra el modelo `Usuario` sin depender del campo `email`.

---

### Requirement 3: Serializers actualizados

**User Story:** Como admin, quiero registrar usuarios con `username`, para que el campo sea obligatorio desde la creación.

#### Acceptance Criteria

1. THE Serializer_Registro SHALL incluir `username` como campo obligatorio al crear un `Usuario`.
2. THE Serializer_Registro SHALL validar que el `username` cumpla el patrón `^[a-zA-Z0-9_-]+$` antes de persistir.
3. THE Serializer_Perfil SHALL exponer el campo `username` en la respuesta del perfil del usuario autenticado.
4. THE Serializer_Perfil SHALL excluir `password_hash` de toda respuesta de la API.

---

### Requirement 4: Formulario de login en el frontend

**User Story:** Como empleado, quiero ver un campo `username` en el formulario de login, para saber exactamente qué dato debo ingresar.

#### Acceptance Criteria

1. THE LoginView SHALL mostrar un campo de texto con etiqueta `"Usuario"` en lugar del campo `"Email"`.
2. WHEN el usuario envía el formulario con el campo `username` vacío, THE LoginView SHALL mostrar el mensaje de validación `"El usuario es requerido"` sin realizar la petición al Backend.
3. WHEN el Backend retorna HTTP 401, THE LoginView SHALL mostrar el mensaje `"Usuario o contraseña incorrectos"`.
4. WHEN el login es exitoso, THE LoginView SHALL almacenar el `Token_JWT` y redirigir al usuario a la vista principal según su `rol`.

---

### Requirement 5: Migración de datos existentes

**User Story:** Como admin, quiero que los usuarios existentes reciban un `username` generado automáticamente durante la migración, para que no pierdan acceso al sistema.

#### Acceptance Criteria

1. WHEN se ejecuta la migración de base de datos, THE Backend SHALL generar un `username` inicial para cada `Usuario` existente derivado de la parte local de su `email` (texto antes del `@`).
2. IF el `username` derivado del `email` ya existe para otro `Usuario`, THEN THE Backend SHALL agregar un sufijo numérico incremental para garantizar unicidad (ej. `juan`, `juan_1`, `juan_2`).
3. THE Backend SHALL ejecutar la migración sin pérdida de datos en los campos existentes del modelo `Usuario`.
