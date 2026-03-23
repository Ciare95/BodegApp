import hashlib
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import authentication, exceptions
from usuarios.models import Usuario


def obtener_tokens_para_usuario(usuario):
    """Genera par de tokens JWT para un Usuario personalizado."""
    refresh = RefreshToken()
    refresh['user_id'] = usuario.id
    refresh['username'] = usuario.username
    refresh['rol'] = usuario.rol
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class AutenticacionJWTUsuario(authentication.BaseAuthentication):
    """
    Backend de autenticación JWT que resuelve el user_id del token
    contra el modelo Usuario personalizado (no auth.User).
    """

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).split()

        if not header or header[0].lower() != b'bearer':
            return None

        if len(header) != 2:
            raise exceptions.AuthenticationFailed('Token JWT malformado.')

        try:
            token = AccessToken(header[1].decode('utf-8'))
        except (InvalidToken, TokenError):
            raise exceptions.AuthenticationFailed('Token inválido o expirado.')

        user_id = token.get('user_id')
        if not user_id:
            raise exceptions.AuthenticationFailed('Token sin user_id.')

        try:
            usuario = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            raise exceptions.AuthenticationFailed('Usuario no encontrado.')

        return (usuario, token)
