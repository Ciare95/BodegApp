from rest_framework import serializers
from productos.models import Producto, Historial


class HistorialSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Historial.

    Expone los campos de registro de cambios en productos.
    """

    class Meta:
        model = Historial
        fields = [
            'id',
            'producto',
            'usuario',
            'campo_modificado',
            'valor_anterior',
            'valor_nuevo',
            'fecha',
        ]
        read_only_fields = fields


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Producto.

    Expone nombre_completo y codigo_completo como campos calculados
    de solo lectura. Los campos FK incluyen representaciones anidadas
    de los catálogos para facilitar la visualización.
    """

    nombre_completo = serializers.SerializerMethodField()
    codigo_completo = serializers.SerializerMethodField()
    subcategoria = serializers.StringRelatedField()
    medida_principal = serializers.StringRelatedField()
    medida_secundaria = serializers.StringRelatedField(allow_null=True)
    codigo_uno = serializers.StringRelatedField()
    codigo_dos = serializers.StringRelatedField()
    actualizado_por = serializers.StringRelatedField(allow_null=True)

    class Meta:
        model = Producto
        fields = [
            'id',
            'subcategoria',
            'medida_principal',
            'medida_secundaria',
            'codigo_uno',
            'codigo_dos',
            'estado',
            'creado_en',
            'actualizado_en',
            'actualizado_por',
            'nombre_completo',
            'codigo_completo',
        ]
        read_only_fields = [
            'creado_en',
            'actualizado_en',
            'nombre_completo',
            'codigo_completo',
        ]

    def get_nombre_completo(self, obj):
        """Retorna el nombre completo del producto."""
        return obj.nombre_completo

    def get_codigo_completo(self, obj):
        """Retorna el código completo del producto."""
        return obj.codigo_completo


class ProductoWriteSerializer(serializers.ModelSerializer):
    """
    Serializer de escritura para Producto.
    Acepta FK como IDs para crear/actualizar desde el frontend.
    """
    from categorias.models import Subcategoria, MedidaPrincipal, MedidaSecundaria, CodigoUno, CodigoDos

    class Meta:
        model = Producto
        fields = [
            'subcategoria',
            'medida_principal',
            'medida_secundaria',
            'codigo_uno',
            'codigo_dos',
            'estado',
        ]
