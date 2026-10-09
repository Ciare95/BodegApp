# Spec Delta

## Purpose

Registro manual de pares de código (prefijo + sufijo) que están disponibles para asignar a productos. Permite al administrador reservar o documentar códigos libres y garantiza que un código no pueda estar simultáneamente libre y asignado a un producto.

## ADDED Requirements

### Requirement: Acceso desde la navegación principal

La sección "Código libre" SHALL estar accesible desde la barra de navegación únicamente para usuarios con rol administrador.

#### Scenario: Administrador ve el enlace
- **WHEN** un usuario con rol administrador carga cualquier página de la aplicación
- **THEN** el enlace "Código libre" aparece en la barra de navegación

#### Scenario: Empleado no ve el enlace
- **WHEN** un usuario con rol empleado carga cualquier página de la aplicación
- **THEN** el enlace "Código libre" no aparece en la barra de navegación

### Requirement: Lista de códigos libres ordenada

La vista `/codigo-libre` SHALL mostrar todos los registros de código libre ordenados: primero los que comienzan con letras (A–Z alfabéticamente), luego los que comienzan con números (ascendente).

#### Scenario: Orden correcto con letras y números mezclados
- **WHEN** existen códigos libres cuyos prefijos son "B", "A", "2", "1"
- **THEN** se muestran agrupados por prefijo en el orden: A, B, 1, 2 (letras primero, luego números)

#### Scenario: Lista vacía
- **WHEN** no existen registros de código libre
- **THEN** la vista muestra un mensaje indicando que no hay códigos libres registrados

### Requirement: Creación de código libre

El sistema SHALL permitir a un administrador registrar un código libre seleccionando un prefijo y un sufijo existentes en los catálogos (`CodigoUno` y `CodigoDos`).

#### Scenario: Registro exitoso
- **WHEN** el administrador selecciona un prefijo y sufijo que no están asignados a ningún producto ni ya registrados como libres, y confirma
- **THEN** el nuevo código libre aparece en la lista

#### Scenario: Rechazo por código ya asignado a producto
- **WHEN** el administrador intenta registrar un código cuya combinación prefijo-sufijo ya está asignada a un producto
- **THEN** el sistema rechaza la operación con el mensaje "Ese código ya está asignado a un producto"

#### Scenario: Rechazo por código duplicado en lista libre
- **WHEN** el administrador intenta registrar un código cuya combinación prefijo-sufijo ya existe en la lista de códigos libres
- **THEN** el sistema rechaza la operación indicando que el código ya está registrado como libre

### Requirement: Edición de código libre

El sistema SHALL permitir a un administrador cambiar el prefijo y/o sufijo de un código libre existente, seleccionando entre los valores disponibles en los catálogos.

#### Scenario: Edición exitosa
- **WHEN** el administrador edita un código libre y elige una nueva combinación prefijo-sufijo que no está asignada a ningún producto ni registrada como libre
- **THEN** el código libre se actualiza y la lista refleja el nuevo valor

#### Scenario: Rechazo por código ya asignado al editar
- **WHEN** el administrador edita un código libre e intenta asignarle una combinación prefijo-sufijo que ya pertenece a un producto
- **THEN** el sistema rechaza la operación con el mensaje "Ese código ya está asignado a un producto"

### Requirement: Eliminación de código libre

El sistema SHALL permitir a un administrador eliminar un código libre existente.

#### Scenario: Eliminación exitosa
- **WHEN** el administrador confirma la eliminación de un código libre
- **THEN** el código desaparece de la lista

### Requirement: Auto-limpieza al asignar código a producto

Cuando un producto es creado o actualizado con un par de código (prefijo + sufijo), el sistema SHALL eliminar automáticamente el registro de código libre correspondiente, si existía.

#### Scenario: Código libre eliminado al asignar a producto
- **WHEN** un administrador asigna a un producto el código "A-3" y ese par existía en la lista de códigos libres
- **THEN** el código "A-3" desaparece de la lista de códigos libres sin acción manual adicional

#### Scenario: Sin efecto si el código no era libre
- **WHEN** un administrador asigna a un producto un código que no estaba en la lista de códigos libres
- **THEN** la lista de códigos libres no cambia
