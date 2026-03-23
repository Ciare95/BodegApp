import pytest
from rest_framework import status


@pytest.mark.django_db
class TestCatalogoPermisos:

    def test_admin_puede_crear_categoria(self, cliente_admin):
        response = cliente_admin.post('/api/categorias/', {'nombre': 'PERNOS'})
        assert response.status_code == status.HTTP_201_CREATED

    def test_empleado_no_puede_crear_categoria(self, cliente_empleado):
        response = cliente_empleado.post('/api/categorias/', {'nombre': 'PERNOS'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_empleado_puede_listar_categorias(self, cliente_empleado, categoria):
        response = cliente_empleado.get('/api/categorias/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_admin_puede_editar_categoria(self, cliente_admin, categoria):
        response = cliente_admin.patch(
            f'/api/categorias/{categoria.pk}/', {'nombre': 'TORNILLOS EDITADO'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['nombre'] == 'TORNILLOS EDITADO'

    def test_admin_puede_eliminar_categoria_sin_referencias(self, cliente_admin, db):
        from categorias.models import Categoria
        cat = Categoria.objects.create(nombre='TEMPORAL')
        response = cliente_admin.delete(f'/api/categorias/{cat.pk}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_no_elimina_categoria_referenciada(self, cliente_admin, subcategoria):
        categoria = subcategoria.categoria
        response = cliente_admin.delete(f'/api/categorias/{categoria.pk}/')
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_subcategorias_filtrables_por_categoria(
        self, cliente_admin, subcategoria
    ):
        categoria_id = subcategoria.categoria.pk
        response = cliente_admin.get(
            f'/api/subcategorias/?categoria_id={categoria_id}'
        )
        assert response.status_code == status.HTTP_200_OK
        assert all(
            s['categoria']['id'] == categoria_id for s in response.data
        )
