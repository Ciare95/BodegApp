from django.core.exceptions import ValidationError
from django.db import transaction
from productos.models import Producto, Historial


def _validar_codigo_unico(codigo_uno, codigo_dos, excluir_producto_id=None):
    """Valida que el par codigo_uno/codigo_dos no esté en uso por otro producto."""
    if codigo_uno is None or codigo_dos is None:
        return
    qs = Producto.objects.filter(codigo_uno=codigo_uno, codigo_dos=codigo_dos)
    if excluir_producto_id:
        qs = qs.exclude(id=excluir_producto_id)
    if qs.exists():
        raise ValidationError(
            f"El código {codigo_uno.valor}-{codigo_dos.valor} ya está en uso."
        )


@transaction.atomic
def crear_producto(data: dict, usuario) -> Producto:
    duplicado = Producto.objects.filter(
        subcategoria=data.get('subcategoria'),
        medida_principal=data.get('medida_principal'),
        medida_secundaria=data.get('medida_secundaria'),
    ).exists()
    if duplicado:
        raise ValidationError('Ya existe un producto con esa combinación de catálogos.')

    codigo_uno = data.get('codigo_uno')
    codigo_dos = data.get('codigo_dos')
    _validar_codigo_unico(codigo_uno, codigo_dos)

    producto = Producto(
        subcategoria=data['subcategoria'],
        medida_principal=data['medida_principal'],
        medida_secundaria=data.get('medida_secundaria'),
        codigo_uno=codigo_uno,
        codigo_dos=codigo_dos,
        estado=data.get('estado', 'verde'),
        actualizado_por=usuario,
    )
    producto.full_clean()
    producto.save()
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


CAMPOS_PRODUCTO = ['subcategoria', 'medida_principal', 'medida_secundaria', 'codigo_uno', 'codigo_dos', 'estado']


@transaction.atomic
def actualizar_producto(producto, data: dict, usuario) -> Producto:
    campos_modificados = []

    # Validar pareja de códigos si se envía alguno
    nuevo_codigo_uno = data.get('codigo_uno', producto.codigo_uno)
    nuevo_codigo_dos = data.get('codigo_dos', producto.codigo_dos)
    _validar_codigo_unico(nuevo_codigo_uno, nuevo_codigo_dos, excluir_producto_id=producto.id)

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

    if campos_modificados:
        producto.full_clean()
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
