import hashlib
from rest_framework import serializers
from usuarios.models import Usuario


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """
    Serializer de escritura para crear un Usuario.
    Recibe password en texto plano y lo hashea antes de guardar.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'email', 'password', 'rol']

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password_hash'] = hashlib.sha256(
            password.encode()
        ).hexdigest()
        return Usuario.objects.create(**validated_data)


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """
    Serializer de solo lectura para exponer datos del usuario autenticado.
    Nunca expone password_hash.
    """
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'email', 'rol', 'creado_en']
        read_only_fields = fields
