from django.db import migrations, models
import django.core.validators


def rellenar_username_desde_email(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    for usuario in Usuario.objects.filter(username__isnull=True):
        base = usuario.email.split('@')[0]
        candidato = base
        sufijo = 1
        while Usuario.objects.filter(username=candidato).exists():
            candidato = f"{base}_{sufijo}"
            sufijo += 1
        usuario.username = candidato
        usuario.save(update_fields=['username'])


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_usuario_username_nullable'),
    ]

    operations = [
        migrations.RunPython(rellenar_username_desde_email, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='usuario',
            name='username',
            field=models.CharField(
                max_length=50,
                unique=True,
                validators=[django.core.validators.RegexValidator(r'^[a-zA-Z0-9_-]+$')],
            ),
        ),
    ]
