from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from productos.models import Producto, Historial
from productos.serializers import (
    ProductoSerializer,
    ProductoWriteSerializer,
    ProductoCodigoSerializer,
    ProductoCodigoWriteSerializer,
    HistorialSerializer,
)
from productos.service import (
    crear_producto,
    actualizar_producto,
    cambiar_estado,
    agregar_codigo,
    eliminar_codigo,
)
from usuarios.permissions import EsSoloAdmin, EsAdminOEmpleado


class ProductoViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        qs = Producto.objects.select_related(
            'subcategoria__categoria',
            'medida_principal',
            'medida_secundaria',
            'actualizado_por',
        ).prefetch_related(
            'codigos__codigo_uno',
            'codigos__codigo_dos',
        ).order_by('orden', 'id')

        q = self.request.query_params.get('q')
        if q:
            from django.db.models import Q
            tokens = q.strip().split()
            for token in tokens:
                # Si el token tiene formato "XX-YY", buscar prefijo y sufijo juntos
                if '-' in token:
                    partes = token.split('-', 1)
                    prefijo, sufijo = partes[0], partes[1]
                    qs = qs.filter(
                        Q(subcategoria__nombre__icontains=token)
                        | Q(subcategoria__categoria__nombre__icontains=token)
                        | Q(medida_principal__valor__icontains=token)
                        | Q(medida_secundaria__valor__icontains=token)
                        | Q(
                            codigos__codigo_uno__valor__icontains=prefijo,
                            codigos__codigo_dos__valor__icontains=sufijo,
                        )
                    )
                else:
                    qs = qs.filter(
                        Q(subcategoria__nombre__icontains=token)
                        | Q(subcategoria__categoria__nombre__icontains=token)
                        | Q(medida_principal__valor__icontains=token)
                        | Q(medida_secundaria__valor__icontains=token)
                        | Q(codigos__codigo_uno__valor__icontains=token)
                        | Q(codigos__codigo_dos__valor__icontains=token)
                    )

        categoria_id = self.request.query_params.get('categoria_id')
        if categoria_id:
            qs = qs.filter(subcategoria__categoria_id=categoria_id)

        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

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
            return Response(ProductoSerializer(producto).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        producto = self.get_object()
        serializer = ProductoWriteSerializer(
            producto, data=request.data, partial=kwargs.get('partial', False)
        )
        serializer.is_valid(raise_exception=True)
        try:
            producto = actualizar_producto(producto, serializer.validated_data, request.user)
            return Response(ProductoSerializer(producto).data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='codigos', permission_classes=[EsSoloAdmin])
    def agregar_codigo(self, request, pk=None):
        """POST /api/productos/{id}/codigos/ — agrega un código al producto."""
        producto = self.get_object()
        serializer = ProductoCodigoWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            pc = agregar_codigo(
                producto,
                serializer.validated_data['codigo_uno'],
                serializer.validated_data['codigo_dos'],
                request.user,
            )
            return Response(ProductoCodigoSerializer(pc).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='codigos/(?P<codigo_id>[0-9]+)', permission_classes=[EsSoloAdmin])
    def eliminar_codigo(self, request, pk=None, codigo_id=None):
        """DELETE /api/productos/{id}/codigos/{codigo_id}/ — elimina un código."""
        producto = self.get_object()
        try:
            eliminar_codigo(producto, int(codigo_id), request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='reordenar', permission_classes=[EsSoloAdmin])
    def reordenar(self, request):
        ids = request.data.get('orden', [])
        if not ids:
            return Response({'detail': 'Se requiere la lista orden.'}, status=status.HTTP_400_BAD_REQUEST)
        from django.db import transaction
        with transaction.atomic():
            for posicion, producto_id in enumerate(ids):
                Producto.objects.filter(id=producto_id).update(orden=posicion)
        return Response({'detail': 'Orden actualizado.'})

    @action(detail=True, methods=['patch'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        producto = self.get_object()
        nuevo_estado = request.data.get('estado')
        if not nuevo_estado:
            return Response({'detail': 'El campo estado es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            producto = cambiar_estado(producto, nuevo_estado, request.user)
            return Response(ProductoSerializer(producto).data)
        except ValidationError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)


class HistorialViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HistorialSerializer
    permission_classes = [EsSoloAdmin]

    def get_queryset(self):
        qs = Historial.objects.select_related('producto', 'usuario')
        producto_id = self.request.query_params.get('producto_id')
        if producto_id:
            qs = qs.filter(producto_id=producto_id)
        return qs
