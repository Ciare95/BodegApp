import django.db.models.deletion
from django.db import migrations, models


def migrar_codigos_a_producto(apps, schema_editor):
    """Copia codigo_uno_id/codigo_dos_id de ProductoCodigo a Producto."""
    schema_editor.execute("""
        UPDATE productos_producto p
        SET codigo_uno_id = pc.codigo_uno_id,
            codigo_dos_id = pc.codigo_dos_id
        FROM (
            SELECT DISTINCT ON (producto_id)
                producto_id, codigo_uno_id, codigo_dos_id
            FROM productos_productocodigo
            ORDER BY producto_id, id
        ) pc
        WHERE p.id = pc.producto_id
    """)


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0005_producto_codigos_separados'),
        ('categorias', '0001_initial'),
    ]

    operations = [
        # 1. Sync state: tell Django that Producto now has codigo_uno/codigo_dos
        #    and ProductoCodigo is gone — DB untouched in this step
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='producto',
                    name='codigo_uno',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='productos',
                        to='categorias.codigouno',
                    ),
                ),
                migrations.AddField(
                    model_name='producto',
                    name='codigo_dos',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='productos',
                        to='categorias.codigodos',
                    ),
                ),
                migrations.DeleteModel(name='ProductoCodigo'),
            ],
        ),

        # 2. Add columns and migrate data in raw SQL (outside Django ORM constraints)
        migrations.RunSQL(
            sql="""
                ALTER TABLE productos_producto
                    ADD COLUMN IF NOT EXISTS codigo_uno_id integer,
                    ADD COLUMN IF NOT EXISTS codigo_dos_id integer;

                UPDATE productos_producto p
                SET codigo_uno_id = pc.codigo_uno_id,
                    codigo_dos_id = pc.codigo_dos_id
                FROM (
                    SELECT DISTINCT ON (producto_id)
                        producto_id, codigo_uno_id, codigo_dos_id
                    FROM productos_productocodigo
                    ORDER BY producto_id, id
                ) pc
                WHERE p.id = pc.producto_id;

                DROP TABLE IF EXISTS productos_productocodigo;

                ALTER TABLE productos_producto
                    ADD CONSTRAINT productos_producto_codigo_uno_id_fkey
                        FOREIGN KEY (codigo_uno_id) REFERENCES categorias_codigouno(id)
                        ON DELETE RESTRICT,
                    ADD CONSTRAINT productos_producto_codigo_dos_id_fkey
                        FOREIGN KEY (codigo_dos_id) REFERENCES categorias_codigodos(id)
                        ON DELETE RESTRICT;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 3. Add unique_together constraint via Django ORM state
        migrations.AlterUniqueTogether(
            name='producto',
            unique_together={
                ('subcategoria', 'medida_principal', 'medida_secundaria'),
                ('codigo_uno', 'codigo_dos'),
            },
        ),
    ]
