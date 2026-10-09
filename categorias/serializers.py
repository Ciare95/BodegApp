from rest_framework import serializers
from categorias.models import (
    Categoria,
    Subcategoria,
    MedidaPrincipal,
    MedidaSecundaria,
    CodigoUno,
    CodigoDos,
    CodigoLibre,
)


class CategoriaSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    imagen = serializers.ImageField(write_only=True, required=False)

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'imagen_url', 'imagen']


class SubcategoriaSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True,
    )
    imagen_url = serializers.SerializerMethodField()
    imagen = serializers.ImageField(write_only=True, required=False)

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url

    class Meta:
        model = Subcategoria
        fields = ['id', 'categoria', 'categoria_nombre', 'categoria_id', 'nombre', 'imagen_url', 'imagen']


class MedidaPrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedidaPrincipal
        fields = ['id', 'valor']


class MedidaSecundariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedidaSecundaria
        fields = ['id', 'valor']


class CodigoUnoSerializer(serializers.ModelSerializer):
    producto_count = serializers.SerializerMethodField()

    def get_producto_count(self, obj):
        return getattr(obj, 'producto_count', 0)

    class Meta:
        model = CodigoUno
        fields = ['id', 'valor', 'producto_count']


class CodigoDosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoDos
        fields = ['id', 'valor']


class CodigoLibreSerializer(serializers.ModelSerializer):
    codigo_uno_valor = serializers.CharField(source='codigo_uno.valor', read_only=True)
    codigo_dos_valor = serializers.CharField(source='codigo_dos.valor', read_only=True)
    codigo_uno = serializers.PrimaryKeyRelatedField(queryset=CodigoUno.objects.all())
    codigo_dos = serializers.PrimaryKeyRelatedField(queryset=CodigoDos.objects.all())

    class Meta:
        model = CodigoLibre
        fields = ['id', 'codigo_uno', 'codigo_dos', 'codigo_uno_valor', 'codigo_dos_valor']
