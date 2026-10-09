import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Revierte los cambios de DB de la migración 0006.
    Restaura la tabla productos_productocodigo y elimina las columnas
    codigo_uno_id/codigo_dos_id de productos_producto.
    Los datos se migran de vuelta a la tabla intermedia.
    """

    dependencies = [
        ('productos', '0006_fix_direct_fks'),
        ('categorias', '0001_initial'),
    ]

    operations = [
        # 1. Sync state: tell Django that ProductoCodigo is back
        #    and Producto no longer has codigo_uno/codigo_dos
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
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
                    options={'unique_together': {('codigo_uno', 'codigo_dos')}},
                ),
                migrations.RemoveField(model_name='producto', name='codigo_uno'),
                migrations.RemoveField(model_name='producto', name='codigo_dos'),
                migrations.AlterUniqueTogether(
                    name='producto',
                    unique_together={('subcategoria', 'medida_principal', 'medida_secundaria')},
                ),
            ],
        ),

        # 2. Restore table and migrate data via SQL
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS productos_productocodigo (
                    id SERIAL PRIMARY KEY,
                    producto_id integer NOT NULL
                        REFERENCES productos_producto(id) ON DELETE CASCADE,
                    codigo_uno_id integer NOT NULL
                        REFERENCES categorias_codigouno(id) ON DELETE RESTRICT,
                    codigo_dos_id integer NOT NULL
                        REFERENCES categorias_codigodos(id) ON DELETE RESTRICT,
                    CONSTRAINT productos_productocodigo_codigo_uno_id_codigo_dos_id_key
                        UNIQUE (codigo_uno_id, codigo_dos_id)
                );

                INSERT INTO productos_productocodigo (producto_id, codigo_uno_id, codigo_dos_id)
                SELECT id, codigo_uno_id, codigo_dos_id
                FROM productos_producto
                WHERE codigo_uno_id IS NOT NULL AND codigo_dos_id IS NOT NULL;

                ALTER TABLE productos_producto
                    DROP CONSTRAINT IF EXISTS productos_producto_codigo_one_codigo_dos_key,
                    DROP CONSTRAINT IF EXISTS productos_producto_codigo_uno_id_codigo_dos_id_key,
                    DROP CONSTRAINT IF EXISTS productos_producto_codigo_uno_id_fkey,
                    DROP CONSTRAINT IF EXISTS productos_producto_codigo_dos_id_fkey;

                ALTER TABLE productos_producto
                    DROP COLUMN IF EXISTS codigo_uno_id,
                    DROP COLUMN IF EXISTS codigo_dos_id;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
