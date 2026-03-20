from django.db import models
from django.core.validators import RegexValidator


class Usuario(models.Model):
    ROL_CHOICES = [
        ('admin', 'Admin'),
        ('empleado', 'Empleado'),
    ]

    nombre = models.CharField(max_length=150)
    username = models.CharField(
        max_length=50,
        unique=True,
        validators=[RegexValidator(r'^[a-zA-Z0-9_-]+$')],
    )
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=10, choices=ROL_CHOICES)
    creado_en = models.DateTimeField(auto_now_add=True)

    # Requerido por DRF para request.user.is_authenticated
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return f"{self.nombre} ({self.rol})"
