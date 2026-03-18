from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from categorias.models import (
    Categoria,
    Subcategoria,
    MedidaPrincipal,
    MedidaSecundaria,
    CodigoUno,
    CodigoDos,
)
from categorias.serializers import (
    CategoriaSerializer,
    SubcategoriaSerializer,
    MedidaPrincipalSerializer,
    MedidaSecundariaSerializer,
    CodigoUnoSerializer,
    CodigoDosSerializer,
)
from categorias.service import eliminar_valor_catalogo
from usuarios.permissions import EsSoloAdmin, EsAdminOEmpleado


class CatalogoBaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet base para todos los catálogos.
    - list / retrieve: admin y empleado
    - create / update / destroy: solo admin
    """

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [EsAdminOEmpleado()]
        return [EsSoloAdmin()]

    def destroy(self, request, *args, **kwargs):
        instancia = self.get_object()
        try:
            eliminar_valor_catalogo(instancia)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response(
                {'detail': e.message},
                status=status.HTTP_409_CONFLICT,
            )


class CategoriaViewSet(CatalogoBaseViewSet):
    queryset = Categoria.objects.all().order_by('nombre')
    serializer_class = CategoriaSerializer


class SubcategoriaViewSet(CatalogoBaseViewSet):
    serializer_class = SubcategoriaSerializer

    def get_queryset(self):
        qs = Subcategoria.objects.select_related('categoria').order_by('nombre')
        categoria_id = self.request.query_params.get('categoria_id')
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
        return qs


class MedidaPrincipalViewSet(CatalogoBaseViewSet):
    queryset = MedidaPrincipal.objects.all().order_by('valor')
    serializer_class = MedidaPrincipalSerializer


class MedidaSecundariaViewSet(CatalogoBaseViewSet):
    queryset = MedidaSecundaria.objects.all().order_by('valor')
    serializer_class = MedidaSecundariaSerializer


class CodigoUnoViewSet(CatalogoBaseViewSet):
    queryset = CodigoUno.objects.all().order_by('valor')
    serializer_class = CodigoUnoSerializer


class CodigoDosViewSet(CatalogoBaseViewSet):
    queryset = CodigoDos.objects.all().order_by('valor')
    serializer_class = CodigoDosSerializer
