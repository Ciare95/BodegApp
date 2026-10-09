# Spec Delta

## Purpose

Herramienta de revisión de bodega organizada por prefijos de código, que permite recorrer todos los productos posición a posición y actualizar su estado desde la misma vista.

## ADDED Requirements

### Requirement: Acceso desde la navegación principal
La sección "Revisión" SHALL estar accesible desde la barra de navegación para todos los usuarios autenticados, sin restricción de rol.

#### Scenario: Usuario autenticado ve el enlace de Revisión
- **WHEN** un usuario autenticado carga cualquier página de la aplicación
- **THEN** el enlace "Revisión" aparece en la barra de navegación

#### Scenario: Acceso directo a la URL
- **WHEN** un usuario autenticado navega a `/revision`
- **THEN** el sistema muestra la vista principal de revisión sin redirigir

### Requirement: Vista principal muestra todos los prefijos ordenados
La vista `/revision` SHALL mostrar una card por cada prefijo (`CodigoUno`) existente, ordenados alfabéticamente (letras A–Z primero) y luego en orden ascendente (números 1, 2, 3…).

#### Scenario: Orden correcto con letras y números mezclados
- **WHEN** existen prefijos "B", "A", "AB", "2", "1", "BB"
- **THEN** se muestran en el orden: A, AB, B, BB, 1, 2

#### Scenario: Prefijo sin productos
- **WHEN** un prefijo no tiene ningún producto asignado
- **THEN** su card muestra el texto "Sin productos"

#### Scenario: Prefijo con productos
- **WHEN** un prefijo tiene uno o más productos asignados
- **THEN** su card muestra el conteo numérico de productos

### Requirement: Vista de detalle por prefijo
La vista `/revision/:prefijo` SHALL mostrar todos los productos cuyo prefijo coincide con el valor del parámetro de ruta, ordenados por sufijo (`CodigoDos`) alfabéticamente y en orden ascendente.

#### Scenario: Navegación al detalle
- **WHEN** el usuario selecciona la card de un prefijo en la vista principal
- **THEN** el sistema navega a `/revision/:prefijo` y muestra la lista de productos de ese prefijo

#### Scenario: Orden de productos por sufijo
- **WHEN** el prefijo "B" tiene productos con sufijos "3", "1", "AB", "2"
- **THEN** se muestran en el orden: AB, B, 1, 2, 3 (letras antes que números, luego ascendente)

#### Scenario: Información mostrada por producto
- **WHEN** el usuario ve la lista de un prefijo
- **THEN** cada fila muestra el código completo (ej. B-1), el nombre completo del producto y su estado (verde / amarillo / rojo)

#### Scenario: Prefijo sin productos en detalle
- **WHEN** el usuario navega a `/revision/:prefijo` y ese prefijo no tiene productos
- **THEN** el sistema muestra un mensaje indicando que no hay productos para ese prefijo

### Requirement: Edición de estado en línea
El usuario SHALL poder cambiar el estado de cualquier producto (verde / amarillo / rojo) directamente desde la vista de detalle, sin salir de la página.

#### Scenario: Cambio de estado exitoso
- **WHEN** el usuario selecciona un estado diferente para un producto
- **THEN** el sistema guarda el nuevo estado de forma inmediata y la vista refleja el cambio sin recargar

#### Scenario: Estado visual diferenciado
- **WHEN** la lista de productos está visible
- **THEN** el estado de cada producto se muestra con su color correspondiente (verde, amarillo, rojo)

#### Scenario: Permiso de edición
- **WHEN** un usuario con rol empleado o admin cambia el estado de un producto
- **THEN** el sistema acepta el cambio y persiste el nuevo estado
