from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    La migración 0005 fue registrada como aplicada pero la DB quedó en el estado
    original: codigo_uno_id y codigo_dos_id siguen en productos_producto y la tabla
    productos_productoCodigo nunca fue creada.

    Esta migración sincroniza el estado de Django con la realidad de la DB:
    - Las columnas ya existen → se declaran con SeparateDatabaseAndState (no-op en DB)
    - ProductoCodigo nunca existió → se elimina solo del estado de Django
    - Se ajusta unique_together al nuevo diseño
    """

    dependencies = [
        ('productos', '0005_producto_codigos_separados'),
        ('categorias', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Las columnas ya existen en la DB → no ejecutar nada
            database_operations=[],
            # Actualizar el estado de Django para que refleje la realidad
            state_operations=[
                # 1. Agregar codigo_uno y codigo_dos al estado del modelo Producto
                migrations.AddField(
                    model_name='producto',
                    name='codigo_uno',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='productos',
                        to='categorias.codigouno',
                    ),
                ),
                migrations.AddField(
                    model_name='producto',
                    name='codigo_dos',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='productos',
                        to='categorias.codigodos',
                    ),
                ),
                # 2. Eliminar ProductoCodigo del estado (nunca existió en la DB)
                migrations.DeleteModel(name='ProductoCodigo'),
            ],
        ),

        # 3. Actualizar unique_together (sí ejecuta en DB)
        migrations.AlterUniqueTogether(
            name='producto',
            unique_together={
                ('subcategoria', 'medida_principal', 'medida_secundaria'),
                ('codigo_uno', 'codigo_dos'),
            },
        ),
    ]
