from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from usuarios.models import Usuario
from usuarios.serializers import UsuarioRegistroSerializer, UsuarioPerfilSerializer
from usuarios.permissions import EsSoloAdmin, EsAdminOEmpleado


class RegistroUsuarioView(APIView):
    """
    POST /api/usuarios/registro/
    Solo accesible por admin. Crea un nuevo usuario con rol asignado.
    """
    permission_classes = [EsSoloAdmin]

    def post(self, request):
        serializer = UsuarioRegistroSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            return Response(
                UsuarioPerfilSerializer(usuario).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PerfilUsuarioView(APIView):
    """
    GET /api/usuarios/me/
    Devuelve los datos del usuario autenticado.
    """
    permission_classes = [EsAdminOEmpleado]

    def get(self, request):
        serializer = UsuarioPerfilSerializer(request.user)
        return Response(serializer.data)


from rest_framework import viewsets
from rest_framework.exceptions import ValidationError


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios. Solo accesible por admin.
    - list / retrieve: listar y ver detalle
    - create: delega a RegistroUsuarioView (hashea password)
    - update / partial_update: editar nombre, email, rol
    - destroy: eliminar usuario
    """
    permission_classes = [EsSoloAdmin]
    queryset = Usuario.objects.all().order_by('nombre')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return UsuarioRegistroSerializer
        return UsuarioPerfilSerializer

    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()
        if usuario == request.user:
            raise ValidationError('No puedes eliminar tu propio usuario.')
        return super().destroy(request, *args, **kwargs)
