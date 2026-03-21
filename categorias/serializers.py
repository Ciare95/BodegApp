from rest_framework import serializers
from categorias.models import (
    Categoria,
    Subcategoria,
    MedidaPrincipal,
    MedidaSecundaria,
    CodigoUno,
    CodigoDos,
)


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class SubcategoriaSerializer(serializers.ModelSerializer):
    # Lectura: muestra el objeto categoria anidado
    categoria = CategoriaSerializer(read_only=True)
    # Campo plano para mostrar en tablas
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    # Escritura: acepta el id de la categoria
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True,
    )

    class Meta:
        model = Subcategoria
        fields = ['id', 'categoria', 'categoria_nombre', 'categoria_id', 'nombre']


class MedidaPrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedidaPrincipal
        fields = ['id', 'valor']


class MedidaSecundariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedidaSecundaria
        fields = ['id', 'valor']


class CodigoUnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoUno
        fields = ['id', 'valor']


class CodigoDosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoDos
        fields = ['id', 'valor']
