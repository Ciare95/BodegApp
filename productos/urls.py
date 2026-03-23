from rest_framework.routers import DefaultRouter
from productos.views import ProductoViewSet, HistorialViewSet

router = DefaultRouter()
router.register('productos', ProductoViewSet, basename='producto')
router.register('historial', HistorialViewSet, basename='historial')

urlpatterns = router.urls
