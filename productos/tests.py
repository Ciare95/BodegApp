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


# ---------------------------------------------------------------------------
# Tests de service.py
# ---------------------------------------------------------------------------

import pytest
from django.core.exceptions import ValidationError
from productos.models import Producto, Historial
from productos.service import crear_producto, actualizar_producto, cambiar_estado
from categorias.service import eliminar_valor_catalogo


@pytest.mark.django_db
class TestCrearProducto:

    def test_crea_producto_correctamente(
        self, subcategoria, medida_principal, medida_secundaria,
        codigo_uno, codigo_dos, admin
    ):
        data = {
            'subcategoria': subcategoria,
            'medida_principal': medida_principal,
            'medida_secundaria': medida_secundaria,
            'codigo_uno': codigo_uno,
            'codigo_dos': codigo_dos,
            'estado': 'verde',
        }
        producto = crear_producto(data, admin)
        assert producto.pk is not None
        assert producto.actualizado_por == admin

    def test_duplicado_lanza_validation_error(
        self, subcategoria, medida_principal, medida_secundaria,
        codigo_uno, codigo_dos, admin
    ):
        data = {
            'subcategoria': subcategoria,
            'medida_principal': medida_principal,
            'medida_secundaria': medida_secundaria,
            'codigo_uno': codigo_uno,
            'codigo_dos': codigo_dos,
        }
        crear_producto(data, admin)
        with pytest.raises(ValidationError):
            crear_producto(data, admin)


@pytest.mark.django_db
class TestActualizarProducto:

    def test_genera_historial_por_campo_cambiado(
        self, producto, admin
    ):
        from categorias.models import CodigoUno
        nuevo_codigo = CodigoUno.objects.create(valor='GB')

        actualizar_producto(producto, {'codigo_uno': nuevo_codigo}, admin)

        registro = Historial.objects.get(
            producto=producto, campo_modificado='codigo_uno'
        )
        assert registro.valor_anterior == 'EB'
        assert registro.valor_nuevo == 'GB'

    def test_no_genera_historial_si_no_hay_cambios(self, producto, admin):
        cantidad_antes = Historial.objects.filter(producto=producto).count()
        actualizar_producto(producto, {'estado': 'verde'}, admin)
        assert Historial.objects.filter(producto=producto).count() == cantidad_antes

    def test_multiples_campos_generan_multiples_registros(
        self, producto, admin
    ):
        from categorias.models import CodigoUno, CodigoDos
        nuevo_c1 = CodigoUno.objects.create(valor='HB')
        nuevo_c2 = CodigoDos.objects.create(valor='99')

        actualizar_producto(
            producto,
            {'codigo_uno': nuevo_c1, 'codigo_dos': nuevo_c2},
            admin,
        )
        assert Historial.objects.filter(producto=producto).count() == 2


@pytest.mark.django_db
class TestCambiarEstado:

    def test_cambia_estado_y_registra_historial(self, producto, empleado):
        cambiar_estado(producto, 'rojo', empleado)
        producto.refresh_from_db()
        assert producto.estado == 'rojo'

        registro = Historial.objects.get(
            producto=producto, campo_modificado='estado'
        )
        assert registro.valor_anterior == 'verde'
        assert registro.valor_nuevo == 'rojo'
        assert registro.usuario == empleado

    def test_estado_invalido_lanza_error(self, producto, admin):
        with pytest.raises(ValidationError):
            cambiar_estado(producto, 'azul', admin)

    def test_mismo_estado_lanza_error(self, producto, admin):
        with pytest.raises(ValidationError):
            cambiar_estado(producto, 'verde', admin)


@pytest.mark.django_db
class TestEliminarCatalogo:

    def test_elimina_catalogo_sin_referencias(self, db):
        from categorias.models import CodigoUno
        codigo = CodigoUno.objects.create(valor='ZZ')
        eliminar_valor_catalogo(codigo)
        assert not CodigoUno.objects.filter(valor='ZZ').exists()

    def test_no_elimina_catalogo_referenciado(self, producto, codigo_uno):
        with pytest.raises(ValidationError):
            eliminar_valor_catalogo(codigo_uno)
