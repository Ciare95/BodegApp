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


def _parsear_error(exc_data):
    """Convierte errores de DRF/Django en un mensaje legible."""
    if isinstance(exc_data, str):
        return exc_data
    if isinstance(exc_data, list):
        return ' '.join(str(e) for e in exc_data)
    if isinstance(exc_data, dict):
        if 'non_field_errors' in exc_data:
            msgs = exc_data['non_field_errors']
            msg = str(msgs[0]) if msgs else ''
            if 'codigo_uno' in msg and 'codigo_dos' in msg:
                return 'Ese código ya está asignado a otro producto.'
            if 'subcategoria' in msg:
                return 'Ya existe un producto con esa combinación de subcategoría y medidas.'
            return msg
        partes = []
        for errores in exc_data.values():
            partes.append(str(errores[0] if isinstance(errores, list) else errores))
        return ' '.join(partes)
    return str(exc_data)


def _traducir_validation_error(exc):
    """Traduce ValidationError de Django a mensaje legible."""
    msg = exc.message if hasattr(exc, 'message') else str(exc)
    msg_dict = exc.message_dict if hasattr(exc, 'message_dict') else {}
    # unique_together dispara message_dict con '__all__'
    if '__all__' in msg_dict:
        raw = str(msg_dict['__all__'][0])
        if 'codigo_uno' in raw and 'codigo_dos' in raw:
            return 'Ese código ya está asignado a otro producto.'
        if 'subcategoria' in raw:
            return 'Ya existe un producto con esa combinación de subcategoría y medidas.'
        return raw
    return msg


class ProductoViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        qs = Producto.objects.select_related(
            'subcategoria__categoria',
            'medida_principal',
            'medida_secundaria',
            'codigo_uno',
            'codigo_dos',
            'actualizado_por',
        ).order_by('orden', 'id')

        q = self.request.query_params.get('q')
        if q:
            from django.db.models import Q
            import re
            raw = q.strip().upper()

            # Si el query contiene un guión, buscar exclusivamente por código
            if '-' in raw:
                partes = raw.split('-', 1)
                prefijo, sufijo = partes[0].strip(), partes[1].strip()
                qs = qs.filter(
                    codigo_uno__valor__icontains=prefijo,
                    codigo_dos__valor__icontains=sufijo,
                )
            else:
                # Reagrupar tokens: "1 1/2" se trata como un solo token
                tokens = re.findall(r'\d+\s+\d+/\d+|\d+/\d+|\d+|[A-Z]+', raw)
                for token in tokens:
                    token = token.strip()
                    if not token:
                        continue
                    qs = qs.filter(
                        Q(subcategoria__nombre__icontains=token)
                        | Q(subcategoria__categoria__nombre__icontains=token)
                        | Q(medida_principal__valor__icontains=token)
                        | Q(medida_secundaria__valor__icontains=token)
                        | Q(codigo_uno__valor__icontains=token)
                        | Q(codigo_dos__valor__icontains=token)
                    )

        categoria_id = self.request.query_params.get('categoria_id')
        if categoria_id:
            qs = qs.filter(subcategoria__categoria_id=categoria_id)

        subcategoria_id = self.request.query_params.get('subcategoria_id')
        if subcategoria_id:
            qs = qs.filter(subcategoria_id=subcategoria_id)

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
        if not serializer.is_valid():
            return Response({'detail': _parsear_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            producto = crear_producto(serializer.validated_data, request.user)
            return Response(ProductoSerializer(producto).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'detail': _traducir_validation_error(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        producto = self.get_object()
        serializer = ProductoWriteSerializer(
            producto, data=request.data, partial=kwargs.get('partial', False)
        )
        if not serializer.is_valid():
            return Response({'detail': _parsear_error(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            producto = actualizar_producto(producto, serializer.validated_data, request.user)
            return Response(ProductoSerializer(producto).data)
        except ValidationError as e:
            return Response({'detail': _traducir_validation_error(e)}, status=status.HTTP_400_BAD_REQUEST)

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
