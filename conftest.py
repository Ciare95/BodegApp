import pytest
from usuarios.models import Usuario
from categorias.models import (
    Categoria,
    Subcategoria,
    MedidaPrincipal,
    MedidaSecundaria,
    CodigoUno,
    CodigoDos,
)


# --- Usuarios ---

@pytest.fixture
def admin(db):
    return Usuario.objects.create(
        nombre='Admin Test',
        email='admin@bodegapp.com',
        password_hash='hashed_admin_pass',
        rol='admin',
    )


@pytest.fixture
def empleado(db):
    return Usuario.objects.create(
        nombre='Empleado Test',
        email='empleado@bodegapp.com',
        password_hash='hashed_empleado_pass',
        rol='empleado',
    )


# --- Catálogos ---

@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre='TORNILLOS')


@pytest.fixture
def subcategoria(db, categoria):
    return Subcategoria.objects.create(
        categoria=categoria,
        nombre='TORNILLO GRADO 5',
    )


@pytest.fixture
def medida_principal(db):
    return MedidaPrincipal.objects.create(valor='1/4')


@pytest.fixture
def medida_secundaria(db):
    return MedidaSecundaria.objects.create(valor='3/4')


@pytest.fixture
def codigo_uno(db):
    return CodigoUno.objects.create(valor='EB')


@pytest.fixture
def codigo_dos(db):
    return CodigoDos.objects.create(valor='40')


# --- Producto base ---

@pytest.fixture
def producto(db, subcategoria, medida_principal, medida_secundaria, codigo_uno, codigo_dos, admin):
    from productos.models import Producto
    return Producto.objects.create(
        subcategoria=subcategoria,
        medida_principal=medida_principal,
        medida_secundaria=medida_secundaria,
        codigo_uno=codigo_uno,
        codigo_dos=codigo_dos,
        estado='verde',
        actualizado_por=admin,
    )


# --- Clientes API autenticados ---

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def cliente_admin(api_client, admin):
    """APIClient autenticado como admin usando force_authenticate."""
    api_client.force_authenticate(user=admin)
    return api_client


@pytest.fixture
def cliente_empleado(api_client, empleado):
    """APIClient autenticado como empleado usando force_authenticate."""
    api_client.force_authenticate(user=empleado)
    return api_client
