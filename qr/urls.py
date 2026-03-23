from django.urls import path
from qr.views import QRView, QRDescargarView

urlpatterns = [
    path('<int:producto_id>/', QRView.as_view(), name='qr_ver'),
    path('<int:producto_id>/descargar/', QRDescargarView.as_view(), name='qr_descargar'),
]
