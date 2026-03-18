import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import status
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


# ---------------------------------------------------------------------------
# BAPP-48 Tests endpoints Producto
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestProductoEndpoints:

    def _data_producto(
        self, subcategoria, medida_principal, medida_secundaria,
        codigo_uno, codigo_dos
    ):
        return {
            'subcategoria': subcategoria.pk,
            'medida_principal': medida_principal.pk,
            'medida_secundaria': medida_secundaria.pk,
            'codigo_uno': codigo_uno.pk,
            'codigo_dos': codigo_dos.pk,
            'estado': 'verde',
        }

    def test_admin_puede_crear_producto(
        self, cliente_admin, subcategoria, medida_principal,
        medida_secundaria, codigo_uno, codigo_dos
    ):
        data = self._data_producto(
            subcategoria, medida_principal, medida_secundaria,
            codigo_uno, codigo_dos
        )
        response = cliente_admin.post('/api/productos/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'nombre_completo' in response.data
        assert 'codigo_completo' in response.data

    def test_empleado_no_puede_crear_producto(
        self, cliente_empleado, subcategoria, medida_principal,
        medida_secundaria, codigo_uno, codigo_dos
    ):
        data = self._data_producto(
            subcategoria, medida_principal, medida_secundaria,
            codigo_uno, codigo_dos
        )
        response = cliente_empleado.post('/api/productos/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_listar_productos(self, cliente_empleado, producto):
        response = cliente_empleado.get('/api/productos/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_busqueda_por_codigo(self, cliente_admin, producto):
        response = cliente_admin.get('/api/productos/?q=EB')
        assert response.status_code == status.HTTP_200_OK
        assert any('EB' in p['codigo_completo'] for p in response.data)

    def test_busqueda_sin_resultados(self, cliente_admin, producto):
        response = cliente_admin.get('/api/productos/?q=ZZZZZ')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_cambiar_estado_empleado(self, cliente_empleado, producto):
        response = cliente_empleado.patch(
            f'/api/productos/{producto.pk}/cambiar-estado/',
            {'estado': 'rojo'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['estado'] == 'rojo'

    def test_cambiar_estado_invalido(self, cliente_admin, producto):
        response = cliente_admin.patch(
            f'/api/productos/{producto.pk}/cambiar-estado/',
            {'estado': 'azul'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_puede_editar_producto(
        self, cliente_admin, producto, codigo_uno
    ):
        from categorias.models import CodigoUno
        nuevo = CodigoUno.objects.create(valor='GB')
        response = cliente_admin.patch(
            f'/api/productos/{producto.pk}/',
            {'codigo_uno': nuevo.pk},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_admin_puede_eliminar_producto(self, cliente_admin, producto):
        response = cliente_admin.delete(f'/api/productos/{producto.pk}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT


# ---------------------------------------------------------------------------
# BAPP-49 Tests endpoint Historial
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestHistorialEndpoints:

    def test_cambio_de_estado_genera_historial(
        self, cliente_admin, producto
    ):
        cliente_admin.patch(
            f'/api/productos/{producto.pk}/cambiar-estado/',
            {'estado': 'amarillo'},
        )
        response = cliente_admin.get(
            f'/api/historial/?producto_id={producto.pk}'
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        registro = response.data[0]
        assert registro['campo_modificado'] == 'estado'
        assert registro['valor_anterior'] == 'verde'
        assert registro['valor_nuevo'] == 'amarillo'

    def test_empleado_no_puede_ver_historial(
        self, cliente_empleado, producto
    ):
        response = cliente_empleado.get(
            f'/api/historial/?producto_id={producto.pk}'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_historial_filtrado_por_producto(
        self, cliente_admin, producto
    ):
        response = cliente_admin.get(
            f'/api/historial/?producto_id={producto.pk}'
        )
        assert response.status_code == status.HTTP_200_OK
        assert all(
            r['producto'] == producto.pk for r in response.data
        )


# ---------------------------------------------------------------------------
# BAPP-50 Tests endpoint QR
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestQREndpoints:

    def test_qr_retorna_base64(self, cliente_admin, producto):
        response = cliente_admin.get(f'/api/qr/{producto.pk}/')
        assert response.status_code == status.HTTP_200_OK
        assert 'imagen' in response.data
        assert len(response.data['imagen']) > 0

    def test_qr_descarga_retorna_png(self, cliente_admin, producto):
        response = cliente_admin.get(f'/api/qr/{producto.pk}/descargar/')
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'image/png'
        assert 'attachment' in response['Content-Disposition']

    def test_qr_producto_inexistente_retorna_404(self, cliente_admin):
        response = cliente_admin.get('/api/qr/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_empleado_puede_generar_qr(self, cliente_empleado, producto):
        response = cliente_empleado.get(f'/api/qr/{producto.pk}/')
        assert response.status_code == status.HTTP_200_OK
