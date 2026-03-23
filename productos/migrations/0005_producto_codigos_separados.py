from django.db import migrations, models
import django.db.models.deletion


def migrar_codigos(apps, schema_editor):
    """Mueve codigo_uno/codigo_dos de cada Producto al nuevo modelo ProductoCodigo."""
    Producto = apps.get_model('productos', 'Producto')
    ProductoCodigo = apps.get_model('productos', 'ProductoCodigo')
    for p in Producto.objects.all():
        if p.codigo_uno_id and p.codigo_dos_id:
            ProductoCodigo.objects.create(
                producto=p,
                codigo_uno_id=p.codigo_uno_id,
                codigo_dos_id=p.codigo_dos_id,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0004_add_orden_field'),
        ('categorias', '0001_initial'),
    ]

    operations = [
        # 1. Crear el nuevo modelo ProductoCodigo
        migrations.CreateModel(
            name='ProductoCodigo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('producto', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='codigos',
                    to='productos.producto',
                )),
                ('codigo_uno', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='producto_codigos',
                    to='categorias.codigouno',
                )),
                ('codigo_dos', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='producto_codigos',
                    to='categorias.codigodos',
                )),
            ],
            options={
                'unique_together': {('codigo_uno', 'codigo_dos')},
            },
        ),

        # 2. Migrar datos existentes
        migrations.RunPython(migrar_codigos, migrations.RunPython.noop),

        # 3. Eliminar unique_together viejo que incluía codigo_uno/codigo_dos
        migrations.AlterUniqueTogether(
            name='producto',
            unique_together={('subcategoria', 'medida_principal', 'medida_secundaria')},
        ),

        # 4. Eliminar las FKs viejas del modelo Producto
        migrations.RemoveField(model_name='producto', name='codigo_uno'),
        migrations.RemoveField(model_name='producto', name='codigo_dos'),
    ]
