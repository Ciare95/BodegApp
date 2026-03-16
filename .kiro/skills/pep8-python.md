# PEP 8 — Reglas de estilo para Python

Aplica estas reglas en todo el código Python que escribas o modifiques.

## Indentación
- Usa 4 espacios por nivel de indentación. Nunca tabs.
- Las líneas de continuación deben alinearse con el delimitador de apertura o usar una indentación colgante de 4 espacios.

```python
# Correcto
def funcion(
    arg1,
    arg2,
):
    pass

# Incorrecto
def funcion(arg1,
  arg2):
    pass
```

## Longitud de línea
- Máximo 79 caracteres por línea.
- Docstrings y comentarios: máximo 72 caracteres.
- Usa `\` o paréntesis para romper líneas largas. Prefiere paréntesis.

```python
# Correcto
resultado = (valor_uno + valor_dos
             + valor_tres)
```

## Líneas en blanco
- 2 líneas en blanco antes y después de funciones y clases de nivel superior.
- 1 línea en blanco entre métodos dentro de una clase.
- Usa líneas en blanco con moderación dentro de funciones para separar pasos lógicos.

## Imports
- Un import por línea.
- Orden: 1) stdlib, 2) terceros, 3) locales. Separados por una línea en blanco.
- Evita `from module import *`.

```python
# Correcto
import os
import sys

from django.db import models

from usuarios.models import Usuario
```

## Espacios en blanco en expresiones
- Sin espacios antes de paréntesis, corchetes o llaves.
- Sin espacios alrededor de `=` en argumentos por defecto o keyword arguments.
- Un espacio a cada lado de operadores binarios (`=`, `+=`, `==`, `+`, etc.).

```python
# Correcto
x = 1
lista[1:2]
funcion(arg=valor)
y = x + 1

# Incorrecto
x=1
lista[ 1 : 2 ]
funcion( arg = valor )
```

## Nomenclatura
| Elemento | Estilo | Ejemplo |
|---|---|---|
| Variables y funciones | snake_case | `nombre_completo`, `calcular_total` |
| Clases | PascalCase | `Producto`, `HistorialCambio` |
| Constantes | UPPER_SNAKE_CASE | `MAX_INTENTOS`, `ESTADO_VERDE` |
| Módulos y paquetes | snake_case corto | `usuarios`, `config` |
| Métodos privados | `_nombre` | `_validar_estado` |
| Métodos muy privados | `__nombre` | `__hash_password` |

## Comentarios
- Los comentarios deben ser oraciones completas con mayúscula inicial.
- Comentarios inline: al menos 2 espacios antes del `#`, 1 espacio después.
- Evita comentarios obvios que solo repiten el código.

```python
x = x + 1  # Compensa el offset del borde
```

## Docstrings
- Usa docstrings en todos los módulos, clases y funciones públicas.
- Usa triple comillas dobles `"""`.
- Una línea para funciones simples; multilínea para funciones complejas.

```python
def calcular_codigo(codigo_uno, codigo_dos):
    """Retorna el código completo en formato 'EB-40'."""
    return f"{codigo_uno}-{codigo_dos}"


def nombre_completo(subcategoria, medida_principal, medida_secundaria=None):
    """
    Construye el nombre completo del producto.

    Args:
        subcategoria: Nombre de la subcategoría.
        medida_principal: Valor de la medida principal.
        medida_secundaria: Valor de la medida secundaria (opcional).

    Returns:
        str: Nombre completo calculado.
    """
    partes = [subcategoria, medida_principal]
    if medida_secundaria:
        partes.append(f"X {medida_secundaria}")
    return ' '.join(partes)
```

## Comparaciones
- Usa `is` / `is not` para comparar con `None`, `True`, `False`.
- Usa `==` para comparar valores.
- Evita comparar booleanos con `== True`; usa directamente el valor.

```python
# Correcto
if resultado is None:
if activo:

# Incorrecto
if resultado == None:
if activo == True:
```

## Excepciones
- Captura excepciones específicas, nunca `except Exception` o `except:` a secas sin razón.
- Usa `raise ... from err` para encadenar excepciones.

```python
# Correcto
try:
    valor = int(entrada)
except ValueError as e:
    raise ValueError("Entrada inválida") from e
```

## Type hints (recomendado)
- Anota tipos en funciones públicas cuando aporte claridad.

```python
def obtener_producto(producto_id: int) -> dict:
    ...
```
