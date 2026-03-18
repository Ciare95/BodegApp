import pytest
from rest_framework import status


@pytest.mark.django_db
class TestEndpointsPublicos:

    def test_token_requiere_credenciales(self, api_client):
        response = api_client.post('/api/token/', {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_acceso_sin_token_retorna_401(self, api_client):
        response = api_client.get('/api/productos/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_invalido_retorna_401(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION='Bearer token.invalido.aqui')
        response = api_client.get('/api/productos/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPermisosAdmin:

    def test_admin_puede_listar_usuarios(self, cliente_admin):
        response = cliente_admin.get('/api/usuarios/')
        assert response.status_code == status.HTTP_200_OK

    def test_admin_puede_crear_usuario(self, cliente_admin):
        data = {
            'nombre': 'Nuevo Empleado',
            'email': 'nuevo@bodegapp.com',
            'password': 'segura1234',
            'rol': 'empleado',
        }
        response = cliente_admin.post('/api/usuarios/registro/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'nuevo@bodegapp.com'

    def test_admin_puede_acceder_a_su_perfil(self, cliente_admin):
        response = cliente_admin.get('/api/usuarios/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['rol'] == 'admin'


@pytest.mark.django_db
class TestPermisosEmpleado:

    def test_empleado_no_puede_listar_usuarios(self, cliente_empleado):
        response = cliente_empleado.get('/api/usuarios/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_empleado_no_puede_crear_usuario(self, cliente_empleado):
        data = {
            'nombre': 'Intruso',
            'email': 'intruso@bodegapp.com',
            'password': 'pass1234',
            'rol': 'admin',
        }
        response = cliente_empleado.post('/api/usuarios/registro/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_empleado_puede_ver_su_perfil(self, cliente_empleado):
        response = cliente_empleado.get('/api/usuarios/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['rol'] == 'empleado'

    def test_empleado_no_puede_crear_categoria(self, cliente_empleado):
        response = cliente_empleado.post('/api/categorias/', {'nombre': 'NUEVA'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_empleado_puede_listar_categorias(self, cliente_empleado, categoria):
        response = cliente_empleado.get('/api/categorias/')
        assert response.status_code == status.HTTP_200_OK
