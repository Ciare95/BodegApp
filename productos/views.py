from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from productos.models import Producto, Historial
from productos.serializers import (
    ProductoSerializer,
    ProductoWriteSerializer,
    HistorialSerializer,
)
from productos.service import crear_producto, actualizar_producto, cambiar_estado
from usuarios.permissions import EsSoloAdmin, EsAdminOEmpleado


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Producto.
    - list / retrieve / buscar: admin y empleado
    - create / update / destroy: solo admin
    - cambiar_estado: admin y empleado
    """

    def get_queryset(self):
        qs = Producto.objects.select_related(
            'subcategoria__categoria',
            'medida_principal',
            'medida_secundaria',
            'codigo_uno',
            'codigo_dos',
            'actualizado_por',
        ).order_by('subcategoria__nombre')

        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(
                subcategoria__nombre__icontains=q
            ) | qs.filter(
                subcategoria__categoria__nombre__icontains=q
            ) | qs.filter(
                medida_principal__valor__icontains=q
            ) | qs.filter(
                medida_secundaria__valor__icontains=q
            ) | qs.filter(
                codigo_uno__valor__icontains=q
            ) | qs.filter(
                codigo_dos__valor__icontains=q
            )
        return qs.distinct()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ProductoWriteSerializer
        return ProductoSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'cambiar_estado'):
            return [EsAdminOEmpleado()]
        return [EsSoloAdmin()]

    def create(self, request, *args, **kwargs):
        serializer = ProductoWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            producto = crear_producto(serializer.validated_data, request.user)
            return Response(
                ProductoSerializer(producto).data,
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        producto = self.get_object()
        serializer = ProductoWriteSerializer(
            producto, data=request.data, partial=kwargs.get('partial', False)
        )
        serializer.is_valid(raise_exception=True)
        try:
            producto = actualizar_producto(
                producto, serializer.validated_data, request.user
            )
            return Response(ProductoSerializer(producto).data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        """
        PATCH /api/productos/{id}/cambiar-estado/
        Body: { "estado": "amarillo" }
        """
        producto = self.get_object()
        nuevo_estado = request.data.get('estado')
        if not nuevo_estado:
            return Response(
                {'detail': 'El campo estado es requerido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            producto = cambiar_estado(producto, nuevo_estado, request.user)
            return Response(ProductoSerializer(producto).data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)


class HistorialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para Historial.
    Filtrable por producto_id: GET /api/historial/?producto_id=1
    Solo admin puede consultar.
    """
    serializer_class = HistorialSerializer
    permission_classes = [EsSoloAdmin]

    def get_queryset(self):
        qs = Historial.objects.select_related('producto', 'usuario')
        producto_id = self.request.query_params.get('producto_id')
        if producto_id:
            qs = qs.filter(producto_id=producto_id)
        return qs
