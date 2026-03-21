from django.core.exceptions import ValidationError
from django.db import transaction
from productos.models import Producto, ProductoCodigo, Historial


def _validar_codigos(codigos_data, excluir_producto_id=None):
    """Valida que ningún par codigo_uno/codigo_dos ya esté en uso."""
    for c in codigos_data:
        qs = ProductoCodigo.objects.filter(
            codigo_uno=c['codigo_uno'],
            codigo_dos=c['codigo_dos'],
        )
        if excluir_producto_id:
            qs = qs.exclude(producto_id=excluir_producto_id)
        if qs.exists():
            raise ValidationError(
                f"El código {c['codigo_uno'].valor}-{c['codigo_dos'].valor} ya está en uso."
            )


@transaction.atomic
def crear_producto(data: dict, usuario) -> Producto:
    codigos_data = data.pop('codigos', [])

    duplicado = Producto.objects.filter(
        subcategoria=data.get('subcategoria'),
        medida_principal=data.get('medida_principal'),
        medida_secundaria=data.get('medida_secundaria'),
    ).exists()
    if duplicado:
        raise ValidationError('Ya existe un producto con esa combinación de catálogos.')

    if not codigos_data:
        raise ValidationError('El producto debe tener al menos un código.')

    _validar_codigos(codigos_data)

    producto = Producto.objects.create(
        subcategoria=data['subcategoria'],
        medida_principal=data['medida_principal'],
        medida_secundaria=data.get('medida_secundaria'),
        estado=data.get('estado', 'verde'),
        actualizado_por=usuario,
    )

    for c in codigos_data:
        ProductoCodigo.objects.create(
            producto=producto,
            codigo_uno=c['codigo_uno'],
            codigo_dos=c['codigo_dos'],
        )

    return producto


def _valor_legible(campo: str, instancia) -> str:
    valor = getattr(instancia, campo)
    if valor is None:
        return ''
    if hasattr(valor, 'valor'):
        return valor.valor
    if hasattr(valor, 'nombre'):
        return valor.nombre
    return str(valor)


CAMPOS_PRODUCTO = ['subcategoria', 'medida_principal', 'medida_secundaria', 'estado']


@transaction.atomic
def actualizar_producto(producto, data: dict, usuario) -> Producto:
    codigos_data = data.pop('codigos', None)
    campos_modificados = []

    for campo in CAMPOS_PRODUCTO:
        if campo not in data:
            continue
        valor_anterior = _valor_legible(campo, producto)
        nuevo_valor_obj = data[campo]
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

    # Sincronizar códigos si se enviaron
    if codigos_data is not None:
        if not codigos_data:
            raise ValidationError('El producto debe tener al menos un código.')

        # Validar unicidad de los nuevos códigos (excluyendo los del propio producto)
        _validar_codigos(codigos_data, excluir_producto_id=producto.id)

        # Determinar qué códigos agregar y cuáles eliminar
        nuevos_pares = {(c['codigo_uno'].id, c['codigo_dos'].id) for c in codigos_data}
        existentes = {(c.codigo_uno_id, c.codigo_dos_id): c for c in producto.codigos.all()}
        existentes_pares = set(existentes.keys())

        agregar = nuevos_pares - existentes_pares
        eliminar = existentes_pares - nuevos_pares

        for par in eliminar:
            pc = existentes[par]
            valor = f"{pc.codigo_uno.valor}-{pc.codigo_dos.valor}"
            pc.delete()
            campos_modificados.append(('codigo_eliminado', valor, ''))

        for c in codigos_data:
            par = (c['codigo_uno'].id, c['codigo_dos'].id)
            if par in agregar:
                ProductoCodigo.objects.create(
                    producto=producto,
                    codigo_uno=c['codigo_uno'],
                    codigo_dos=c['codigo_dos'],
                )
                valor = f"{c['codigo_uno'].valor}-{c['codigo_dos'].valor}"
                campos_modificados.append(('codigo_agregado', '', valor))

    if campos_modificados:
        producto.actualizado_por = usuario
        producto.save()
        Historial.objects.bulk_create([
            Historial(
                producto=producto,
                usuario=usuario,
                campo_modificado=campo,
                valor_anterior=v_ant,
                valor_nuevo=v_nuevo,
            )
            for campo, v_ant, v_nuevo in campos_modificados
        ])

    return producto


@transaction.atomic
def agregar_codigo(producto, codigo_uno, codigo_dos, usuario) -> ProductoCodigo:
    """Agrega un nuevo código a un producto existente."""
    if ProductoCodigo.objects.filter(codigo_uno=codigo_uno, codigo_dos=codigo_dos).exists():
        raise ValidationError(
            f"El código {codigo_uno.valor}-{codigo_dos.valor} ya está en uso."
        )
    pc = ProductoCodigo.objects.create(
        producto=producto,
        codigo_uno=codigo_uno,
        codigo_dos=codigo_dos,
    )
    Historial.objects.create(
        producto=producto,
        usuario=usuario,
        campo_modificado='codigo_agregado',
        valor_anterior='',
        valor_nuevo=f"{codigo_uno.valor}-{codigo_dos.valor}",
    )
    return pc


@transaction.atomic
def eliminar_codigo(producto, codigo_id, usuario) -> None:
    """Elimina un código de un producto. Debe quedar al menos uno."""
    if producto.codigos.count() <= 1:
        raise ValidationError('El producto debe tener al menos un código.')
    try:
        pc = producto.codigos.get(id=codigo_id)
    except ProductoCodigo.DoesNotExist:
        raise ValidationError('Código no encontrado en este producto.')
    valor = f"{pc.codigo_uno.valor}-{pc.codigo_dos.valor}"
    pc.delete()
    Historial.objects.create(
        producto=producto,
        usuario=usuario,
        campo_modificado='codigo_eliminado',
        valor_anterior=valor,
        valor_nuevo='',
    )


def cambiar_estado(producto, nuevo_estado: str, usuario) -> Producto:
    estados_validos = {'verde', 'amarillo', 'rojo'}
    if nuevo_estado not in estados_validos:
        raise ValidationError(f"Estado inválido '{nuevo_estado}'.")
    if producto.estado == nuevo_estado:
        raise ValidationError(f"El producto ya tiene el estado '{nuevo_estado}'.")

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
