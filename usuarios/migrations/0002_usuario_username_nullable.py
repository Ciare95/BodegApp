"""
Migración generada como parte de Task 1 para permitir que los tests
de propiedad P1 y P2 puedan ejecutarse contra la BD de test.

Agrega `username` como nullable/blank=True para poder aplicar sobre
datos existentes. Task 2 completará la migración de datos y hará el
campo NOT NULL.
"""
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='username',
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                unique=True,
                validators=[django.core.validators.RegexValidator(r'^[a-zA-Z0-9_-]+$')],
            ),
        ),
    ]
