from django.core.exceptions import ValidationError
from django.db import transaction
from productos.models import Producto, Historial
from categorias.models import CodigoLibre


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
def crear_producto(data: dict, usuario) -> Producto:
    codigo_uno = data.get('codigo_uno')
    codigo_dos = data.get('codigo_dos')

    producto = Producto.objects.create(
        subcategoria=data['subcategoria'],
        medida_principal=data['medida_principal'],
        medida_secundaria=data.get('medida_secundaria'),
        codigo_uno=codigo_uno,
        codigo_dos=codigo_dos,
        estado=data.get('estado', 'verde'),
        actualizado_por=usuario,
    )

    if codigo_uno and codigo_dos:
        CodigoLibre.objects.filter(codigo_uno=codigo_uno, codigo_dos=codigo_dos).delete()

    return producto


@transaction.atomic
def actualizar_producto(producto, data: dict, usuario) -> Producto:
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

        codigo_uno = producto.codigo_uno
        codigo_dos = producto.codigo_dos
        if codigo_uno and codigo_dos:
            CodigoLibre.objects.filter(codigo_uno=codigo_uno, codigo_dos=codigo_dos).delete()

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
