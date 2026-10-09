from django.db import migrations


class Migration(migrations.Migration):
    """
    Merge de las dos ramas que salieron de 0005:

    Rama A: 0005 -> 0006_producto_codigo_unico_opcional (no aplicada aún)
    Rama B: 0005 -> 0006_fix_direct_fks -> 0007_restaurar_producto_codigo (aplicadas)

    Al aplicar este merge, Django aplicará primero 0006_producto_codigo_unico_opcional
    sobre el estado dejado por 0007. El SQL de esa migración usa IF NOT EXISTS / IF EXISTS
    para detectar el estado real del DB y actuar en consecuencia:
    - Agrega las columnas codigo_uno_id / codigo_dos_id (no existen después de 0007)
    - Migra los datos desde productos_productocodigo (que sí existe después de 0007)
    - Elimina la tabla intermedia

    El resultado: DB y models.py quedan sincronizados con FKs directas en Producto.
    """

    dependencies = [
        ('productos', '0006_producto_codigo_unico_opcional'),
        ('productos', '0007_restaurar_producto_codigo'),
    ]

    operations = []
