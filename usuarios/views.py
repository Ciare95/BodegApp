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
