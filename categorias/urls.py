from rest_framework.routers import DefaultRouter
from categorias.views import (
    CategoriaViewSet,
    SubcategoriaViewSet,
    MedidaPrincipalViewSet,
    MedidaSecundariaViewSet,
    CodigoUnoViewSet,
    CodigoDosViewSet,
)

router = DefaultRouter()
router.register('categorias', CategoriaViewSet, basename='categoria')
router.register('subcategorias', SubcategoriaViewSet, basename='subcategoria')
router.register('medidas-principales', MedidaPrincipalViewSet, basename='medida-principal')
router.register('medidas-secundarias', MedidaSecundariaViewSet, basename='medida-secundaria')
router.register('codigos-uno', CodigoUnoViewSet, basename='codigo-uno')
router.register('codigos-dos', CodigoDosViewSet, basename='codigo-dos')

urlpatterns = router.urls
