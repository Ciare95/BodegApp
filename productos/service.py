from django.core.exceptions import ValidationError
from productos.models import Producto


def crear_producto(data: dict, usuario) -> Producto:
    """
    Crea un nuevo producto a partir de un dict con las FK resueltas.

    Args:
        data: Diccionario con los campos del producto
              (subcategoria, medida_principal, medida_secundaria,
               codigo_uno, codigo_dos, estado).
        usuario: Instancia de Usuario que realiza la acción.

    Returns:
        Producto: instancia creada y persistida.

    Raises:
        ValidationError: si ya existe un producto con la misma combinación.
    """
    duplicado = Producto.objects.filter(
        subcategoria=data.get('subcategoria'),
        medida_principal=data.get('medida_principal'),
        medida_secundaria=data.get('medida_secundaria'),
        codigo_uno=data.get('codigo_uno'),
        codigo_dos=data.get('codigo_dos'),
    ).exists()

    if duplicado:
        raise ValidationError(
            'Ya existe un producto con esa combinación de catálogos.'
        )

    producto = Producto.objects.create(
        subcategoria=data['subcategoria'],
        medida_principal=data['medida_principal'],
        medida_secundaria=data.get('medida_secundaria'),
        codigo_uno=data['codigo_uno'],
        codigo_dos=data['codigo_dos'],
        estado=data.get('estado', 'verde'),
        actualizado_por=usuario,
    )

    return producto
