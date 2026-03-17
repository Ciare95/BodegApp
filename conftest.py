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
