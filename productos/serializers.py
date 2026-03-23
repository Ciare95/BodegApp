from rest_framework import serializers
from productos.models import Producto, ProductoCodigo, Historial


class ProductoCodigoSerializer(serializers.ModelSerializer):
    codigo_uno_valor = serializers.CharField(source='codigo_uno.valor', read_only=True)
    codigo_dos_valor = serializers.CharField(source='codigo_dos.valor', read_only=True)
    codigo_completo = serializers.SerializerMethodField()

    class Meta:
        model = ProductoCodigo
        fields = ['id', 'codigo_uno', 'codigo_dos', 'codigo_uno_valor', 'codigo_dos_valor', 'codigo_completo']

    def get_codigo_completo(self, obj):
        return f"{obj.codigo_uno.valor}-{obj.codigo_dos.valor}"


class ProductoCodigoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductoCodigo
        fields = ['codigo_uno', 'codigo_dos']
        # La validación de unicidad la maneja el service (excluye los del propio producto)
        validators = []


class HistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historial
        fields = ['id', 'producto', 'usuario', 'campo_modificado', 'valor_anterior', 'valor_nuevo', 'fecha']
        read_only_fields = fields


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer de lectura para Producto."""
    nombre_completo = serializers.SerializerMethodField()
    codigo_completo = serializers.SerializerMethodField()
    codigos = ProductoCodigoSerializer(many=True, read_only=True)

    subcategoria_detalle = serializers.SerializerMethodField()
    medida_principal_detalle = serializers.SerializerMethodField()
    medida_secundaria_detalle = serializers.SerializerMethodField()
    actualizado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id',
            'subcategoria',
            'medida_principal',
            'medida_secundaria',
            'estado',
            'orden',
            'creado_en',
            'actualizado_en',
            'nombre_completo',
            'codigo_completo',
            'codigos',
            'subcategoria_detalle',
            'medida_principal_detalle',
            'medida_secundaria_detalle',
            'actualizado_por_nombre',
        ]
        read_only_fields = fields

    def get_nombre_completo(self, obj):
        return obj.nombre_completo

    def get_codigo_completo(self, obj):
        return obj.codigo_completo

    def get_subcategoria_detalle(self, obj):
        return {
            'id': obj.subcategoria.id,
            'nombre': obj.subcategoria.nombre,
            'categoria_id': obj.subcategoria.categoria.id,
            'categoria_nombre': obj.subcategoria.categoria.nombre,
        }

    def get_medida_principal_detalle(self, obj):
        return {'id': obj.medida_principal.id, 'valor': obj.medida_principal.valor}

    def get_medida_secundaria_detalle(self, obj):
        if obj.medida_secundaria:
            return {'id': obj.medida_secundaria.id, 'valor': obj.medida_secundaria.valor}
        return None

    def get_actualizado_por_nombre(self, obj):
        return obj.actualizado_por.nombre if obj.actualizado_por else None


class ProductoWriteSerializer(serializers.ModelSerializer):
    """Serializer de escritura. Los códigos se manejan por separado."""
    codigos = ProductoCodigoWriteSerializer(many=True, required=False)

    class Meta:
        model = Producto
        fields = ['subcategoria', 'medida_principal', 'medida_secundaria', 'estado', 'codigos']
