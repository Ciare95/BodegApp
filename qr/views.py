from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from productos.models import Producto
from qr.service import generar_qr, generar_qr_bytes
from usuarios.permissions import EsAdminOEmpleado


class QRView(APIView):
    """
    GET /api/qr/{producto_id}/
    Devuelve el QR del producto como imagen base64.
    """
    permission_classes = [EsAdminOEmpleado]

    def get(self, request, producto_id):
        get_object_or_404(Producto, pk=producto_id)
        imagen_b64 = generar_qr(producto_id)
        return Response({
            'producto_id': producto_id,
            'imagen': imagen_b64,
            'formato': 'png',
        })


class QRDescargarView(APIView):
    """
    GET /api/qr/{producto_id}/descargar/
    Devuelve el QR como archivo PNG descargable.
    """
    permission_classes = [EsAdminOEmpleado]

    def get(self, request, producto_id):
        get_object_or_404(Producto, pk=producto_id)
        imagen_bytes = generar_qr_bytes(producto_id)
        response = HttpResponse(imagen_bytes, content_type='image/png')
        response['Content-Disposition'] = (
            f'attachment; filename="qr-producto-{producto_id}.png"'
        )
        return response
