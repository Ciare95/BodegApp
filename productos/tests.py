import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from productos.models import Producto


@pytest.mark.django_db
class TestProductoProperties:

    def test_nombre_completo_con_medida_secundaria(
        self, subcategoria, medida_principal, medida_secundaria, codigo_uno, codigo_dos
    ):
        producto = Producto(
            subcategoria=subcategoria,
            medida_principal=medida_principal,
            medida_secundaria=medida_secundaria,
            codigo_uno=codigo_uno,
            codigo_dos=codigo_dos,
            estado='verde',
        )
        assert producto.nombre_completo == 'TORNILLOS TORNILLO GRADO 5 1/4 X 3/4'

    def test_nombre_completo_sin_medida_secundaria(
        self, subcategoria, medida_principal, codigo_uno, codigo_dos
    ):
        producto = Producto(
            subcategoria=subcategoria,
            medida_principal=medida_principal,
            medida_secundaria=None,
            codigo_uno=codigo_uno,
            codigo_dos=codigo_dos,
            estado='verde',
        )
        assert producto.nombre_completo == 'TORNILLOS TORNILLO GRADO 5 1/4'

    def test_codigo_completo(
        self, subcategoria, medida_principal, codigo_uno, codigo_dos
    ):
        producto = Producto(
            subcategoria=subcategoria,
            medida_principal=medida_principal,
            codigo_uno=codigo_uno,
            codigo_dos=codigo_dos,
            estado='verde',
        )
        assert producto.codigo_completo == 'EB-40'


@pytest.mark.django_db
class TestProductoEstado:

    def test_estado_por_defecto_es_verde(
        self, subcategoria, medida_principal, codigo_uno, codigo_dos
    ):
        producto = Producto.objects.create(
            subcategoria=subcategoria,
            medida_principal=medida_principal,
            codigo_uno=codigo_uno,
            codigo_dos=codigo_dos,
        )
        assert producto.estado == 'verde'

    def test_estados_validos(
        self, subcategoria, medida_principal, codigo_uno, codigo_dos
    ):
        for estado in ('verde', 'amarillo', 'rojo'):
            producto = Producto(
                subcategoria=subcategoria,
                medida_principal=medida_principal,
                codigo_uno=codigo_uno,
                codigo_dos=codigo_dos,
                estado=estado,
            )
            producto.full_clean()  # no debe lanzar ValidationError


@pytest.mark.django_db
class TestProductoUniqueTogether:

    def test_duplicado_lanza_integrity_error(
        self, subcategoria, medida_principal, medida_secundaria, codigo_uno, codigo_dos
    ):
        Producto.objects.create(
            subcategoria=subcategoria,
            medida_principal=medida_principal,
            medida_secundaria=medida_secundaria,
            codigo_uno=codigo_uno,
            codigo_dos=codigo_dos,
            estado='verde',
        )
        with pytest.raises(IntegrityError):
            Producto.objects.create(
                subcategoria=subcategoria,
                medida_principal=medida_principal,
                medida_secundaria=medida_secundaria,
                codigo_uno=codigo_uno,
                codigo_dos=codigo_dos,
                estado='rojo',
            )

    def test_diferente_medida_secundaria_no_es_duplicado(
        self, subcategoria, medida_principal, medida_secundaria, codigo_uno, codigo_dos
    ):
        from categorias.models import MedidaSecundaria
        otra_medida = MedidaSecundaria.objects.create(valor='1 1/2')

        Producto.objects.create(
            subcategoria=subcategoria,
            medida_principal=medida_principal,
            medida_secundaria=medida_secundaria,
            codigo_uno=codigo_uno,
            codigo_dos=codigo_dos,
            estado='verde',
        )
        # No debe lanzar error
        producto2 = Producto.objects.create(
            subcategoria=subcategoria,
            medida_principal=medida_principal,
            medida_secundaria=otra_medida,
            codigo_uno=codigo_uno,
            codigo_dos=codigo_dos,
            estado='verde',
        )
        assert producto2.pk is not None
