"""
Comando de gestión para crear un usuario administrador.
Uso: python manage.py create_admin
"""
import hashlib
from django.core.management.base import BaseCommand
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Crea un usuario administrador inicial'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Nombre de usuario (default: admin)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@bodegapp.com',
            help='Email del administrador (default: admin@bodegapp.com)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password del administrador (default: admin123)',
        )
        parser.add_argument(
            '--nombre',
            type=str,
            default='Administrador',
            help='Nombre completo (default: Administrador)',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        nombre = options['nombre']

        # Verificar si ya existe
        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'El usuario "{username}" ya existe.')
            )
            return

        # Hashear la contraseña con SHA256
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Crear el usuario
        usuario = Usuario.objects.create(
            nombre=nombre,
            username=username,
            email=email,
            password_hash=password_hash,
            rol='admin',
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Usuario administrador creado exitosamente:\n'
                f'  Username: {username}\n'
                f'  Email: {email}\n'
                f'  Password: {password}\n'
                f'  Rol: admin'
            )
        )
