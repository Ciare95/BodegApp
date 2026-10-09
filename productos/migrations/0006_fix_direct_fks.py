from django.db import migrations


class Migration(migrations.Migration):
    """
    Migración de recuperación — vacía intencionalmente.
    En la máquina de desarrollo se aplicó con operaciones SQL que ya fueron
    revertidas por 0007 y rehechas correctamente por 0006_producto_codigo_unico_opcional.
    En máquinas donde 0006_producto_codigo_unico_opcional ya estaba aplicada,
    esta migración no debe hacer nada para evitar conflictos de estado.
    """

    dependencies = [
        ('productos', '0005_producto_codigos_separados'),
        ('categorias', '0001_initial'),
    ]

    operations = []
