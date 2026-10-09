from rest_framework import serializers
from productos.models import Producto, Historial


class HistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historial
        fields = ['id', 'producto', 'usuario', 'campo_modificado', 'valor_anterior', 'valor_nuevo', 'fecha']
        read_only_fields = fields


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer de lectura para Producto."""
    nombre_completo = serializers.SerializerMethodField()
    codigo_completo = serializers.SerializerMethodField()
    codigo_uno_valor = serializers.SerializerMethodField()
    codigo_dos_valor = serializers.SerializerMethodField()

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
            'codigo_uno',
            'codigo_dos',
            'estado',
            'orden',
            'creado_en',
            'actualizado_en',
            'nombre_completo',
            'codigo_completo',
            'codigo_uno_valor',
            'codigo_dos_valor',
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

    def get_codigo_uno_valor(self, obj):
        return obj.codigo_uno.valor if obj.codigo_uno_id else None

    def get_codigo_dos_valor(self, obj):
        return obj.codigo_dos.valor if obj.codigo_dos_id else None

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
    class Meta:
        model = Producto
        fields = ['subcategoria', 'medida_principal', 'medida_secundaria', 'codigo_uno', 'codigo_dos', 'estado']

    def validate(self, data):
        tiene_uno = data.get('codigo_uno') is not None
        tiene_dos = data.get('codigo_dos') is not None
        if tiene_uno != tiene_dos:
            raise serializers.ValidationError(
                'El prefijo y el sufijo del código deben completarse juntos o dejarse ambos vacíos.'
            )
        return data
