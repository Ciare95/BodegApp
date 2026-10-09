from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.exceptions import ValidationError
from django.db.models import Count

from categorias.models import (
    Categoria,
    Subcategoria,
    MedidaPrincipal,
    MedidaSecundaria,
    CodigoUno,
    CodigoDos,
    CodigoLibre,
)
from categorias.serializers import (
    CategoriaSerializer,
    SubcategoriaSerializer,
    MedidaPrincipalSerializer,
    MedidaSecundariaSerializer,
    CodigoUnoSerializer,
    CodigoDosSerializer,
    CodigoLibreSerializer,
)
from categorias.service import eliminar_valor_catalogo
from usuarios.permissions import EsSoloAdmin, EsAdminOEmpleado


class CatalogoBaseViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

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
    serializer_class = CodigoUnoSerializer

    def get_queryset(self):
        qs = CodigoUno.objects.all().order_by('valor')
        if self.request.query_params.get('con_conteo') == 'true':
            qs = qs.annotate(producto_count=Count('productos', distinct=True))
        return qs


class CodigoDosViewSet(CatalogoBaseViewSet):
    queryset = CodigoDos.objects.all().order_by('valor')
    serializer_class = CodigoDosSerializer


class CodigoLibreViewSet(CatalogoBaseViewSet):
    serializer_class = CodigoLibreSerializer

    def get_queryset(self):
        return CodigoLibre.objects.select_related('codigo_uno', 'codigo_dos').order_by(
            'codigo_uno__valor', 'codigo_dos__valor'
        )

    def _parsear_errores(self, errors):
        if 'non_field_errors' in errors:
            return 'Ese código ya está registrado como libre.'
        partes = []
        for errores in errors.values():
            partes.append(str(errores[0] if isinstance(errores, list) else errores))
        return ' '.join(partes)

    def _validar_no_asignado(self, codigo_uno, codigo_dos):
        from productos.models import Producto
        if Producto.objects.filter(codigo_uno=codigo_uno, codigo_dos=codigo_dos).exists():
            raise ValidationError('Ese código ya está asignado a un producto.')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': self._parsear_errores(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self._validar_no_asignado(
                serializer.validated_data['codigo_uno'],
                serializer.validated_data['codigo_dos'],
            )
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instancia = self.get_object()
        serializer = self.get_serializer(instancia, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return Response({'detail': self._parsear_errores(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self._validar_no_asignado(
                serializer.validated_data.get('codigo_uno', instancia.codigo_uno),
                serializer.validated_data.get('codigo_dos', instancia.codigo_dos),
            )
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_update(serializer)
        except Exception:
            return Response(
                {'detail': 'Ese código ya está registrado como libre.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(serializer.data)
