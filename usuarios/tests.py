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
            'username': 'nuevo_empleado',
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


# ---------------------------------------------------------------------------
# Feature: login-username — Tests de modelo y propiedades
# ---------------------------------------------------------------------------

from django.core.exceptions import ValidationError as DjangoValidationError
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st
from usuarios.models import Usuario

_VALID_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-')

# ---------------------------------------------------------------------------
# Sub-task 1.2
# Feature: login-username, Property 1: Username inválido rechazado
# Validates: Requirements 1.2, 3.2
# ---------------------------------------------------------------------------

# Estrategia: texto que contiene al menos un carácter fuera de [a-zA-Z0-9_-]
_username_con_invalido = st.text(
    alphabet=st.characters(),
    min_size=1,
).filter(lambda s: any(c not in _VALID_CHARS for c in s))


@pytest.mark.django_db
@given(username=_username_con_invalido)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_username_invalido_rechazado(username):
    """Property 1: cualquier username con carácter inválido debe ser rechazado."""
    usuario = Usuario(
        nombre='Test',
        username=username,
        email='invalido@test.com',
        password_hash='abc',
        rol='empleado',
    )
    with pytest.raises(DjangoValidationError):
        # validate_constraints=False evita la consulta de unicidad a la BD
        # (la columna aún no existe hasta Task 2 — migración)
        usuario.full_clean(validate_constraints=False)


# ---------------------------------------------------------------------------
# Sub-task 1.3
# Feature: login-username, Property 2: Username duplicado → 400
# Validates: Requirements 1.1, 1.3
# ---------------------------------------------------------------------------

from rest_framework.test import APIClient as _APIClient
import uuid as _uuid


@pytest.mark.django_db(transaction=True)
@given(username=st.from_regex(r'^[a-zA-Z0-9_-]{1,50}$', fullmatch=True))
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_username_duplicado_retorna_400(username):
    """Property 2: registrar un segundo usuario con username ya existente retorna HTTP 400."""
    uid = _uuid.uuid4().hex[:8]

    # Crear el primer usuario directamente en la BD
    Usuario.objects.create(
        nombre='Primero',
        username=username,
        email=f'primero_{uid}@test.com',
        password_hash='hash1',
        rol='empleado',
    )

    # Crear un admin para autenticar la petición
    admin = Usuario.objects.create(
        nombre='Admin',
        username=f'admin_{uid}',
        email=f'admin_{uid}@test.com',
        password_hash='hash_admin',
        rol='admin',
    )

    client = _APIClient()
    client.force_authenticate(user=admin)

    data = {
        'nombre': 'Segundo',
        'username': username,
        'email': f'segundo_{uid}@test.com',
        'password': 'segura1234',
        'rol': 'empleado',
    }
    response = client.post('/api/usuarios/registro/', data)
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Sub-task 1.4 — Tests unitarios del modelo
# Validates: Requirements 1.1, 1.2, 1.4
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_email_se_mantiene_en_modelo():
    """El campo email sigue existiendo en el modelo Usuario."""
    assert hasattr(Usuario, 'email')
    usuario = Usuario(
        nombre='Test',
        username='test_user',
        email='test@bodegapp.com',
        password_hash='hash',
        rol='empleado',
    )
    # validate_constraints=False: evita consulta de unicidad (columna aún sin migrar)
    usuario.full_clean(validate_constraints=False)
    assert usuario.email == 'test@bodegapp.com'


@pytest.mark.django_db
def test_username_max_50_chars():
    """Un username de 51 caracteres debe ser rechazado."""
    usuario = Usuario(
        nombre='Test',
        username='a' * 51,
        email='largo@bodegapp.com',
        password_hash='hash',
        rol='empleado',
    )
    with pytest.raises(DjangoValidationError):
        usuario.full_clean(validate_constraints=False)


@pytest.mark.django_db
def test_username_solo_guion_valido():
    """Los caracteres '-' y '_' solos son usernames válidos."""
    for username in ('-', '_'):
        usuario = Usuario(
            nombre='Test',
            username=username,
            email=f'{username}@bodegapp.com',
            password_hash='hash',
            rol='empleado',
        )
        # No debe lanzar excepción
        usuario.full_clean(validate_constraints=False)
