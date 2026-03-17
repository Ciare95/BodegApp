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


from productos.models import Historial

# Campos FK del producto y cómo obtener su representación legible
CAMPOS_PRODUCTO = [
    'subcategoria',
    'medida_principal',
    'medida_secundaria',
    'codigo_uno',
    'codigo_dos',
    'estado',
]


def _valor_legible(campo: str, instancia) -> str:
    """Retorna representación string del valor actual de un campo."""
    valor = getattr(instancia, campo)
    if valor is None:
        return ''
    # Para FK retorna el valor/nombre del catálogo referenciado
    if hasattr(valor, 'valor'):
        return valor.valor
    if hasattr(valor, 'nombre'):
        return valor.nombre
    return str(valor)


def actualizar_producto(producto, data: dict, usuario) -> 'Producto':
    """
    Actualiza un producto campo por campo y registra en Historial
    cada campo que haya cambiado.

    Args:
        producto: Instancia de Producto a actualizar.
        data: Diccionario con los campos nuevos (solo los que se quieren cambiar).
        usuario: Instancia de Usuario que realiza la acción.

    Returns:
        Producto: instancia actualizada y persistida.
    """
    campos_modificados = []

    for campo in CAMPOS_PRODUCTO:
        if campo not in data:
            continue

        valor_anterior = _valor_legible(campo, producto)
        nuevo_valor_obj = data[campo]

        # Obtener representación legible del nuevo valor
        if nuevo_valor_obj is None:
            valor_nuevo = ''
        elif hasattr(nuevo_valor_obj, 'valor'):
            valor_nuevo = nuevo_valor_obj.valor
        elif hasattr(nuevo_valor_obj, 'nombre'):
            valor_nuevo = nuevo_valor_obj.nombre
        else:
            valor_nuevo = str(nuevo_valor_obj)

        if valor_anterior != valor_nuevo:
            setattr(producto, campo, nuevo_valor_obj)
            campos_modificados.append((campo, valor_anterior, valor_nuevo))

    if campos_modificados:
        producto.actualizado_por = usuario
        producto.save()

        registros = [
            Historial(
                producto=producto,
                usuario=usuario,
                campo_modificado=campo,
                valor_anterior=v_anterior,
                valor_nuevo=v_nuevo,
            )
            for campo, v_anterior, v_nuevo in campos_modificados
        ]
        Historial.objects.bulk_create(registros)

    return producto


def cambiar_estado(producto, nuevo_estado: str, usuario) -> 'Producto':
    """
    Cambia el estado de un producto y registra el cambio en Historial.

    Args:
        producto: Instancia de Producto a actualizar.
        nuevo_estado: Uno de 'verde', 'amarillo', 'rojo'.
        usuario: Instancia de Usuario que realiza la acción.

    Returns:
        Producto: instancia actualizada.

    Raises:
        ValidationError: si el nuevo estado no es válido o es igual al actual.
    """
    estados_validos = {'verde', 'amarillo', 'rojo'}

    if nuevo_estado not in estados_validos:
        raise ValidationError(
            f"Estado inválido '{nuevo_estado}'. Debe ser: {', '.join(estados_validos)}."
        )

    if producto.estado == nuevo_estado:
        raise ValidationError(
            f"El producto ya tiene el estado '{nuevo_estado}'."
        )

    estado_anterior = producto.estado
    producto.estado = nuevo_estado
    producto.actualizado_por = usuario
    producto.save()

    Historial.objects.create(
        producto=producto,
        usuario=usuario,
        campo_modificado='estado',
        valor_anterior=estado_anterior,
        valor_nuevo=nuevo_estado,
    )

    return producto
