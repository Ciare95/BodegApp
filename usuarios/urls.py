from django.urls import path
from usuarios.views import RegistroUsuarioView, PerfilUsuarioView

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='usuario_registro'),
    path('me/', PerfilUsuarioView.as_view(), name='usuario_perfil'),
]
