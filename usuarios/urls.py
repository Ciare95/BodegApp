from django.urls import path
from rest_framework.routers import DefaultRouter
from usuarios.views import RegistroUsuarioView, PerfilUsuarioView, UsuarioViewSet

router = DefaultRouter()
router.register('', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='usuario_registro'),
    path('me/', PerfilUsuarioView.as_view(), name='usuario_perfil'),
] + router.urls
