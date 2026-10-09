from django.db import migrations


class Migration(migrations.Migration):
    """
    Migración de recuperación — vacía intencionalmente.
    En la máquina de desarrollo revertía los cambios de 0006_fix_direct_fks.
    Vacía aquí para evitar conflictos en máquinas donde el estado del DB
    ya es el correcto gracias a 0006_producto_codigo_unico_opcional.
    """

    dependencies = [
        ('productos', '0006_fix_direct_fks'),
        ('categorias', '0001_initial'),
    ]

    operations = []
