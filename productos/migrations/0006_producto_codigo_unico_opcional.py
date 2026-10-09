from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Migración robusta que maneja dos estados posibles de la DB:

    Caso A (dev): La 0005 fue marcada como aplicada pero no ejecutó —
    las columnas codigo_uno_id/codigo_dos_id ya existen en productos_producto
    y la tabla productos_producto_codigo nunca fue creada.

    Caso B (producción): La 0005 se ejecutó correctamente — las columnas
    fueron eliminadas de productos_producto y existe productos_producto_codigo.

    El SQL usa DO $$ ... $$ para detectar el estado real y actuar en consecuencia.
    """

    dependencies = [
        ('productos', '0005_producto_codigos_separados'),
        ('categorias', '0001_initial'),
    ]

    operations = [
        # 1. Sincronizar estado interno de Django (sin tocar la DB)
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

        # 2. Agregar columnas en DB solo si no existen (Caso B: 0005 se ejecutó bien)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'productos_producto'
                          AND column_name = 'codigo_uno_id'
                    ) THEN
                        ALTER TABLE productos_producto
                            ADD COLUMN codigo_uno_id integer
                                REFERENCES categorias_codigouno(id)
                                DEFERRABLE INITIALLY DEFERRED,
                            ADD COLUMN codigo_dos_id integer
                                REFERENCES categorias_codigodos(id)
                                DEFERRABLE INITIALLY DEFERRED;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 3. Migrar datos y eliminar tabla intermedia si existe (Caso B)
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'productos_producto_codigo'
                    ) THEN
                        UPDATE productos_producto p
                        SET codigo_uno_id = pc.codigo_uno_id,
                            codigo_dos_id = pc.codigo_dos_id
                        FROM (
                            SELECT DISTINCT ON (producto_id)
                                producto_id, codigo_uno_id, codigo_dos_id
                            FROM productos_producto_codigo
                            ORDER BY producto_id, id
                        ) pc
                        WHERE p.id = pc.producto_id;

                        DROP TABLE productos_producto_codigo;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # 4. Crear unique_together (las columnas ya existen en ambos casos)
        migrations.AlterUniqueTogether(
            name='producto',
            unique_together={
                ('subcategoria', 'medida_principal', 'medida_secundaria'),
                ('codigo_uno', 'codigo_dos'),
            },
        ),
    ]
